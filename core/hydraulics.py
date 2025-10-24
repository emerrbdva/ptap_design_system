"""
Módulo Core: Simulación Hidráulica

Simulación de perfiles hidráulicos, gradientes de velocidad, tiempos de retención
y pérdidas de carga en sistemas de tratamiento de agua.

Incluye:
- Perfiles de velocidad
- Cálculo de gradientes hidráulicos
- Pérdidas de carga (fricción, localizadas)
- Ecuaciones de Darcy-Weisbach, Hazen-Williams
- Análisis de Reynolds, Froude

Referencias: RAS 2017, Hidráulica de canales abiertos
"""

import sympy as sp
import numpy as np
from scipy import optimize
from pint import UnitRegistry
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

ureg = UnitRegistry()
Q_ = ureg.Quantity

logger = logging.getLogger(__name__)


@dataclass
class HydraulicProfile:
    """Perfil hidráulico de una unidad"""
    velocidades: List[Q_]
    caudales: List[Q_]
    areas: List[Q_]
    reynolds: List[float]
    froude: List[float]
    perdidas_carga: List[Q_]
    

class HydraulicSimulator:
    """
    Simulador hidráulico para unidades de tratamiento.
    
    Calcula:
    - Perfiles de velocidad
    - Números adimensionales (Reynolds, Froude)
    - Pérdidas de carga por fricción y localizadas
    - Gradientes de velocidad
    - Tiempos de retención hidráulicos
    """
    
    def __init__(self, temperatura: float = 15.0):
        """
        Inicializar simulador.
        
        Args:
            temperatura: Temperatura del agua [°C]
        """
        self.temperatura = temperatura
        self.ureg = ureg
        
        # Propiedades del agua a temperatura dada
        self._calcular_propiedades_agua()
        
        logger.info(f"HydraulicSimulator inicializado a {temperatura}°C")
    
    def _calcular_propiedades_agua(self):
        """Calcular propiedades físicas del agua según temperatura"""
        T = self.temperatura
        
        # Densidad: ρ(T) ≈ 1000 - 0.0178*(T-4)² kg/m³
        rho_value = 1000 - 0.0178 * (T - 4)**2
        self.densidad = Q_(rho_value, 'kg/m**3')
        
        # Viscosidad dinámica: μ(T) ≈ 1.787 * e^(-0.0324*T) mPa·s
        mu_value = 1.787 * np.exp(-0.0324 * T) / 1000  # Pa·s
        self.viscosidad_dinamica = Q_(mu_value, 'Pa*s')
        
        # Viscosidad cinemática: ν = μ / ρ
        nu_value = mu_value / rho_value
        self.viscosidad_cinematica = Q_(nu_value, 'm**2/s')
        
        logger.debug(f"Propiedades agua: ρ={self.densidad}, μ={self.viscosidad_dinamica}")
    
    # ========================================================================
    # NÚMEROS ADIMENSIONALES
    # ========================================================================
    
    def calcular_reynolds(
        self,
        velocidad: Q_,
        diametro: Q_
    ) -> float:
        """
        Calcular número de Reynolds.
        
        Re = v·D / ν
        
        Clasificación:
        - Re < 2000: Flujo laminar
        - 2000 < Re < 4000: Flujo transicional
        - Re > 4000: Flujo turbulento
        
        Args:
            velocidad: Velocidad media [m/s]
            diametro: Diámetro característico [m]
            
        Returns:
            Número de Reynolds (adimensional)
        """
        v = velocidad.to('m/s')
        D = diametro.to('m')
        nu = self.viscosidad_cinematica.to('m**2/s')
        
        Re = (v.magnitude * D.magnitude) / nu.magnitude
        
        logger.debug(f"Reynolds: Re={Re:.0f} (v={v}, D={D})")
        return float(Re)
    
    def calcular_froude(
        self,
        velocidad: Q_,
        profundidad: Q_
    ) -> float:
        """
        Calcular número de Froude.
        
        Fr = v / √(g·h)
        
        Clasificación:
        - Fr < 1: Flujo subcrítico (tranquilo)
        - Fr = 1: Flujo crítico
        - Fr > 1: Flujo supercrítico (rápido)
        
        Args:
            velocidad: Velocidad media [m/s]
            profundidad: Profundidad del flujo [m]
            
        Returns:
            Número de Froude (adimensional)
        """
        v = velocidad.to('m/s')
        h = profundidad.to('m')
        g = Q_(9.81, 'm/s**2')
        
        Fr = v.magnitude / np.sqrt(g.magnitude * h.magnitude)
        
        logger.debug(f"Froude: Fr={Fr:.3f} (v={v}, h={h})")
        return float(Fr)
    
    # ========================================================================
    # PÉRDIDAS DE CARGA
    # ========================================================================
    
    def perdida_friccion_darcy(
        self,
        caudal: Q_,
        diametro: Q_,
        longitud: Q_,
        rugosidad: Q_ = Q_(0.0015, 'mm')  # PVC
    ) -> Q_:
        """
        Calcular pérdida de carga por fricción (Darcy-Weisbach).
        
        h_f = f · (L/D) · (v²/2g)
        
        Factor de fricción f calculado con:
        - Ecuación de Haaland (aproximación Colebrook-White)
        - Válida para flujo turbulento
        
        Args:
            caudal: Caudal [m³/s]
            diametro: Diámetro de tubería [m]
            longitud: Longitud de tubería [m]
            rugosidad: Rugosidad absoluta [mm]
            
        Returns:
            Pérdida de carga [m]
        """
        Q = caudal.to('m**3/s')
        D = diametro.to('m')
        L = longitud.to('m')
        k = rugosidad.to('m')
        
        # Velocidad
        A = np.pi * (D.magnitude / 2)**2
        v_value = Q.magnitude / A
        v = Q_(v_value, 'm/s')
        
        # Reynolds
        Re = self.calcular_reynolds(v, D)
        
        # Factor de fricción (Haaland)
        # 1/√f ≈ -1.8·log₁₀[(k/D/3.7)^1.11 + 6.9/Re]
        k_D = k.magnitude / D.magnitude
        term1 = (k_D / 3.7)**1.11
        term2 = 6.9 / Re
        f = 1 / (-1.8 * np.log10(term1 + term2))**2
        
        # Pérdida de carga
        g = 9.81
        hf_value = f * (L.magnitude / D.magnitude) * (v_value**2 / (2 * g))
        hf = Q_(hf_value, 'm')
        
        logger.debug(f"Pérdida fricción: hf={hf}, f={f:.4f}, Re={Re:.0f}")
        return hf
    
    def perdida_hazen_williams(
        self,
        caudal: Q_,
        diametro: Q_,
        longitud: Q_,
        C: float = 140  # Coeficiente Hazen-Williams (PVC = 140-150)
    ) -> Q_:
        """
        Calcular pérdida de carga (Hazen-Williams).
        
        h_f = 10.67 · L · Q^1.852 / (C^1.852 · D^4.87)
        
        Más simple que Darcy, común en sistemas de agua potable.
        
        Args:
            caudal: Caudal [m³/s]
            diametro: Diámetro [m]
            longitud: Longitud [m]
            C: Coeficiente Hazen-Williams
            
        Returns:
            Pérdida de carga [m]
        """
        Q = caudal.to('m**3/s').magnitude
        D = diametro.to('m').magnitude
        L = longitud.to('m').magnitude
        
        hf_value = 10.67 * L * (Q**1.852) / ((C**1.852) * (D**4.87))
        hf = Q_(hf_value, 'm')
        
        logger.debug(f"Hazen-Williams: hf={hf}, C={C}")
        return hf
    
    def perdida_localizada(
        self,
        velocidad: Q_,
        K: float
    ) -> Q_:
        """
        Calcular pérdida de carga localizada.
        
        h_L = K · v²/(2g)
        
        Coeficientes K típicos:
        - Entrada brusca: 0.5
        - Salida brusca: 1.0
        - Codo 90°: 0.9
        - Codo 45°: 0.4
        - Válvula compuerta abierta: 0.2
        - Válvula compuerta 50% cerrada: 2.1
        
        Args:
            velocidad: Velocidad [m/s]
            K: Coeficiente de pérdida
            
        Returns:
            Pérdida de carga [m]
        """
        v = velocidad.to('m/s').magnitude
        g = 9.81
        
        hL_value = K * (v**2) / (2 * g)
        hL = Q_(hL_value, 'm')
        
        logger.debug(f"Pérdida localizada: hL={hL}, K={K}")
        return hL
    
    # ========================================================================
    # GRADIENTES DE VELOCIDAD
    # ========================================================================
    
    def gradiente_velocidad_resalto(
        self,
        caudal: Q_,
        altura_caida: Q_,
        volumen: Q_
    ) -> Q_:
        """
        Calcular gradiente de velocidad en resalto hidráulico.
        
        G = √(γ·Q·h / (μ·V))
        
        Usado en mezcla rápida por resalto.
        
        Args:
            caudal: Caudal [m³/s]
            altura_caida: Altura de caída [m]
            volumen: Volumen de la cámara [m³]
            
        Returns:
            Gradiente de velocidad [s⁻¹]
        """
        Q = caudal.to('m**3/s')
        h = altura_caida.to('m')
        V = volumen.to('m**3')
        
        gamma = (self.densidad * Q_(9.81, 'm/s**2')).to('N/m**3')
        mu = self.viscosidad_dinamica
        
        # P = γ·Q·h (potencia disipada)
        P = gamma * Q * h
        
        # G = √(P / (μ·V))
        G_value = np.sqrt((P / (mu * V)).to_base_units().magnitude)
        G = Q_(G_value, '1/s')
        
        logger.debug(f"Gradiente resalto: G={G}, h={h}")
        return G
    
    def gradiente_velocidad_vertedero(
        self,
        caudal: Q_,
        altura_lamina: Q_,
        volumen: Q_
    ) -> Q_:
        """
        Calcular gradiente en vertedero rectangular.
        
        Args:
            caudal: Caudal [m³/s]
            altura_lamina: Altura de la lámina [m]
            volumen: Volumen [m³]
            
        Returns:
            Gradiente de velocidad [s⁻¹]
        """
        Q = caudal.to('m**3/s')
        h = altura_lamina.to('m')
        V = volumen.to('m**3')
        
        gamma = (self.densidad * Q_(9.81, 'm/s**2')).to('N/m**3')
        mu = self.viscosidad_dinamica
        
        # Potencia: P = γ·Q·h
        P = gamma * Q * h
        
        G_value = np.sqrt((P / (mu * V)).to_base_units().magnitude)
        G = Q_(G_value, '1/s')
        
        return G
    
    # ========================================================================
    # TIEMPOS DE RETENCIÓN
    # ========================================================================
    
    def tiempo_retencion_teorico(
        self,
        volumen: Q_,
        caudal: Q_
    ) -> Q_:
        """
        Tiempo de retención teórico (hidráulico).
        
        t = V / Q
        
        Args:
            volumen: Volumen del reactor [m³]
            caudal: Caudal [m³/s]
            
        Returns:
            Tiempo de retención [s o h]
        """
        V = volumen.to('m**3')
        Q = caudal.to('m**3/s')
        
        t = (V / Q).to('s')
        
        logger.debug(f"Tiempo retención: t={t.to('minute')}, V={V}, Q={Q}")
        return t
    
    def tiempo_retencion_real(
        self,
        tiempo_teorico: Q_,
        factor_cortocircuito: float = 0.8
    ) -> Q_:
        """
        Tiempo de retención real considerando cortocircuito.
        
        t_real = t_teorico · f
        
        Factor típico: 0.7-0.9
        
        Args:
            tiempo_teorico: Tiempo teórico [s]
            factor_cortocircuito: Factor de eficiencia
            
        Returns:
            Tiempo real [s]
        """
        t_real = tiempo_teorico * factor_cortocircuito
        
        logger.debug(f"Tiempo real: t_real={t_real.to('minute')}, f={factor_cortocircuito}")
        return t_real
    
    # ========================================================================
    # PERFILES HIDRÁULICOS COMPLETOS
    # ========================================================================
    
    def perfil_sedimentador(
        self,
        caudal: Q_,
        longitud: Q_,
        ancho: Q_,
        profundidad: Q_,
        num_puntos: int = 20
    ) -> HydraulicProfile:
        """
        Calcular perfil hidráulico de sedimentador rectangular.
        
        Args:
            caudal: Caudal [m³/s]
            longitud: Longitud [m]
            ancho: Ancho [m]
            profundidad: Profundidad [m]
            num_puntos: Puntos de cálculo
            
        Returns:
            Perfil hidráulico completo
        """
        Q = caudal.to('m**3/s')
        L = longitud.to('m')
        B = ancho.to('m')
        h = profundidad.to('m')
        
        # Velocidad horizontal media
        A = B.magnitude * h.magnitude
        v_h = Q.magnitude / A
        
        # Crear perfil a lo largo de L
        x = np.linspace(0, L.magnitude, num_puntos)
        
        velocidades = []
        reynolds_list = []
        froude_list = []
        
        for xi in x:
            v = Q_(v_h, 'm/s')
            velocidades.append(v)
            
            # Diámetro hidráulico
            D_h = 4 * A / (2 * (B.magnitude + h.magnitude))
            
            Re = self.calcular_reynolds(v, Q_(D_h, 'm'))
            Fr = self.calcular_froude(v, h)
            
            reynolds_list.append(Re)
            froude_list.append(Fr)
        
        # Pérdida de carga total (entrada + fricción + salida)
        hf_entrada = self.perdida_localizada(Q_(v_h, 'm/s'), K=0.5)
        hf_friccion = Q_(0.01, 'm')  # Muy pequeña en sedimentador
        hf_salida = self.perdida_localizada(Q_(v_h, 'm/s'), K=1.0)
        
        perdidas = [hf_entrada, hf_friccion, hf_salida]
        
        profile = HydraulicProfile(
            velocidades=velocidades,
            caudales=[Q] * num_puntos,
            areas=[Q_(A, 'm**2')] * num_puntos,
            reynolds=reynolds_list,
            froude=froude_list,
            perdidas_carga=perdidas
        )
        
        logger.info(f"Perfil sedimentador: v_h={v_h:.4f} m/s, Re_prom={np.mean(reynolds_list):.0f}")
        return profile
    
    def perfil_filtro(
        self,
        caudal: Q_,
        area_filtro: Q_,
        profundidad_lecho: Q_,
        diametro_medio_grano: Q_ = Q_(0.5, 'mm'),
        porosidad: float = 0.42
    ) -> Dict[str, Q_]:
        """
        Calcular perfil de filtración y pérdida de carga en lecho.
        
        Usa ecuación de Kozeny-Carman para lecho limpio.
        
        Args:
            caudal: Caudal por filtro [m³/s]
            area_filtro: Área del filtro [m²]
            profundidad_lecho: Profundidad del lecho [m]
            diametro_medio_grano: Diámetro medio [mm]
            porosidad: Porosidad del lecho
            
        Returns:
            Dict con velocidad, pérdida de carga, etc.
        """
        Q = caudal.to('m**3/s')
        A = area_filtro.to('m**2')
        L = profundidad_lecho.to('m')
        d = diametro_medio_grano.to('m')
        e = porosidad
        
        # Velocidad de filtración
        v_f = Q / A
        
        # Pérdida de carga (Kozeny-Carman)
        # h_f = k · (1-e)² / e³ · μ · v · L / (ρ · g · d²)
        # k ≈ 5 (constante Kozeny)
        k = 5.0
        mu = self.viscosidad_dinamica
        rho = self.densidad
        g = Q_(9.81, 'm/s**2')
        
        numerador = k * ((1 - e)**2 / e**3) * mu * v_f * L
        denominador = rho * g * d**2
        
        hf = (numerador / denominador).to('m')
        
        # Tasa de filtración
        tasa = (Q / A).to('m**3/(m**2*day)')
        
        logger.info(f"Perfil filtro: v_f={v_f.to('m/hour')}, hf={hf}, tasa={tasa}")
        
        return {
            "velocidad_filtracion": v_f,
            "tasa_filtracion": tasa,
            "perdida_carga_lecho_limpio": hf,
            "profundidad_lecho": L,
            "diametro_grano": d,
            "porosidad": Q_(e, 'dimensionless')
        }
    
    # ========================================================================
    # CHEQUEOS HIDRÁULICOS
    # ========================================================================
    
    def verificar_regimen_flujo(self, reynolds: float) -> str:
        """Clasificar régimen de flujo según Reynolds"""
        if reynolds < 2000:
            return "laminar"
        elif reynolds < 4000:
            return "transicional"
        else:
            return "turbulento"
    
    def verificar_tipo_flujo_canal(self, froude: float) -> str:
        """Clasificar tipo de flujo según Froude"""
        if froude < 1.0:
            return "subcrítico"
        elif abs(froude - 1.0) < 0.05:
            return "crítico"
        else:
            return "supercrítico"
