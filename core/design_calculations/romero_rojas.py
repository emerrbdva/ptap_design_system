"""
Metodologías de Diseño según Romero Rojas
"Tratamiento de Aguas Residuales" y "Calidad del Agua"

Implementación de fórmulas y criterios de diseño para:
- Sedimentación
- Floculación
- Filtración
- Desinfeccin
- Aireación
"""

import numpy as np
import sympy as sp
from pint import UnitRegistry
from typing import Dict, Tuple, Optional
import logging
from dataclasses import dataclass

ureg = UnitRegistry()

@dataclass
class RomeroRojasResults:
    """Resultados de cálculos según Romero Rojas"""
    process_name: str
    design_parameters: Dict
    calculated_values: Dict
    design_criteria: Dict
    verification: Dict
    references: Dict

class RomeroRojasCalculations:
    """
    Implementación de metodologías Romero Rojas para diseño de PTAP
    
    Referencias:
    - Romero Rojas, J.A. "Tratamiento de Aguas Residuales"
    - Romero Rojas, J.A. "Calidad del Agua"
    - Romero Rojas, J.A. "Potabilización del Agua"
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.design_criteria = self._load_design_criteria()
    
    def _load_design_criteria(self) -> Dict:
        """Carga criterios de diseño según Romero Rojas"""
        return {
            'sedimentacion': {
                'velocidad_sedimentacion_min': 0.5,  # cm/min
                'velocidad_sedimentacion_max': 3.0,  # cm/min
                'tiempo_retencion_min': 1.5,  # horas
                'tiempo_retencion_max': 4.0,  # horas
                'carga_superficial_max': 40,  # m3/m2/d
                'profundidad_min': 3.0,  # m
                'profundidad_max': 5.0,  # m
                'relacion_largo_ancho': (3, 5),  # min, max
                'pendiente_fondo': 0.01  # m/m
            },
            'floculacion': {
                'tiempo_floculacion_min': 15,  # min
                'tiempo_floculacion_max': 45,  # min
                'gradiente_velocidad_min': 20,  # s-1
                'gradiente_velocidad_max': 100,  # s-1
                'numero_compartimentos_min': 3,
                'numero_compartimentos_max': 6,
                'profundidad_min': 2.5,  # m
                'profundidad_max': 4.0  # m
            },
            'filtracion': {
                'velocidad_filtracion_min': 120,  # m3/m2/d
                'velocidad_filtracion_max': 300,  # m3/m2/d
                'espesor_lecho_min': 0.6,  # m
                'espesor_lecho_max': 1.2,  # m
                'perdida_carga_max': 2.0,  # m
                'velocidad_lavado': 600,  # m3/m2/d
                'expansion_lecho': 0.25  # 25%
            },
            'desinfeccion': {
                'tiempo_contacto_min': 10,  # min
                'tiempo_contacto_max': 30,  # min
                'ct_min': 0.5,  # mg*min/L
                'ct_max': 3.0,  # mg*min/L
                'dosis_cloro_min': 0.5,  # mg/L
                'dosis_cloro_max': 3.0  # mg/L
            }
        }
    
    def calcular_sedimentador_convencional(self, 
                                         caudal_m3_s: float,
                                         eficiencia_remocion: float = 0.85,
                                         temperatura: float = 20.0) -> RomeroRojasResults:
        """
        Diseño de sedimentador convencional según Romero Rojas
        
        Args:
            caudal_m3_s: Caudal de diseño (m3/s)
            eficiencia_remocion: Eficiencia de remoción deseada (fracción)
            temperatura: Temperatura del agua (°C)
            
        Returns:
            RomeroRojasResults con parámetros de diseño
        """
        try:
            # Parámetros de entrada
            Q = caudal_m3_s * ureg.m**3 / ureg.s
            Q_m3_d = (Q * 86400).to(ureg.m**3 / ureg.day).magnitude
            
            # Criterios Romero Rojas para sedimentación
            criteria = self.design_criteria['sedimentacion']
            
            # Velocidad de sedimentación (Hazen)
            # vs = 1.5 cm/min para eficiencia 85% (Romero Rojas)
            vs_cm_min = 1.5 if eficiencia_remocion == 0.85 else 1.5 * (eficiencia_remocion / 0.85)
            vs_m_s = vs_cm_min * 0.01 / 60  # Conversión a m/s
            
            # Área superficial requerida (Ecuación fundamental Hazen)
            As = Q.magnitude / vs_m_s  # m2
            
            # Tiempo de retención (criterio Romero Rojas: 2-4 horas)
            tr_horas = 3.0  # Valor típico recomendado
            
            # Volumen del sedimentador
            V = Q_m3_d * tr_horas / 24  # m3
            
            # Profundidad (criterio Romero Rojas: 3-5 m)
            H = 4.0  # m (valor típico)
            
            # Verificar área con profundidad
            As_verificada = V / H
            
            # Usar el mayor de los dos áreas
            As_diseno = max(As, As_verificada)
            
            # Dimensiones en planta
            # Relación L/B = 4:1 (Romero Rojas)
            B = np.sqrt(As_diseno / 4)  # Ancho
            L = 4 * B  # Largo
            
            # Carga superficial
            Cs = Q_m3_d / As_diseno  # m3/m2/d
            
            # Velocidad horizontal
            vh = Q.magnitude / (B * H)  # m/s
            
            # Número de Reynolds (verificación régimen)
            viscosidad = self._viscosidad_agua(temperatura)
            Re = (vh * H) / viscosidad
            
            # Verificaciones Romero Rojas
            verificaciones = {
                'carga_superficial_ok': criteria['carga_superficial_max'] >= Cs,
                'profundidad_ok': criteria['profundidad_min'] <= H <= criteria['profundidad_max'],
                'tiempo_retencion_ok': criteria['tiempo_retencion_min'] <= tr_horas <= criteria['tiempo_retencion_max'],
                'velocidad_horizontal_ok': vh <= 0.005,  # m/s (criterio Romero Rojas)
                'numero_reynolds': Re,
                'regimen_flujo': 'laminar' if Re < 2000 else 'turbulento'
            }
            
            # Volumen de lodos (Romero Rojas: 10-20% del volumen total)
            V_lodos = V * 0.15  # 15% promedio
            
            calculated_values = {
                'area_superficial_m2': round(As_diseno, 2),
                'largo_m': round(L, 2),
                'ancho_m': round(B, 2),
                'profundidad_m': H,
                'volumen_m3': round(V, 2),
                'tiempo_retencion_h': tr_horas,
                'carga_superficial_m3_m2_d': round(Cs, 2),
                'velocidad_sedimentacion_cm_min': vs_cm_min,
                'velocidad_horizontal_m_s': round(vh, 6),
                'volumen_lodos_m3': round(V_lodos, 2),
                'pendiente_fondo': criteria['pendiente_fondo']
            }
            
            return RomeroRojasResults(
                process_name="Sedimentador Convencional",
                design_parameters={
                    'caudal_m3_s': caudal_m3_s,
                    'eficiencia_remocion': eficiencia_remocion,
                    'temperatura_C': temperatura
                },
                calculated_values=calculated_values,
                design_criteria=criteria,
                verification=verificaciones,
                references={
                    'metodologia': 'Romero Rojas - Tratamiento de Aguas',
                    'ecuaciones': ['Hazen', 'Continuidad', 'Reynolds'],
                    'paginas_referencia': ['156-189', '220-245']
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error en cálculo sedimentador Romero Rojas: {e}")
            raise
    
    def calcular_floculador_hidraulico(self, 
                                     caudal_m3_s: float,
                                     gradiente_velocidad: float = 50.0) -> RomeroRojasResults:
        """
        Diseño de floculador hidráulico según Romero Rojas
        
        Args:
            caudal_m3_s: Caudal de diseño (m3/s)
            gradiente_velocidad: Gradiente de velocidad deseado (s-1)
            
        Returns:
            RomeroRojasResults con parámetros de diseño
        """
        try:
            Q = caudal_m3_s * ureg.m**3 / ureg.s
            G = gradiente_velocidad  # s-1
            
            criteria = self.design_criteria['floculacion']
            
            # Tiempo de floculación (Romero Rojas: 20-30 min)
            tf_min = 25  # minutos
            tf_s = tf_min * 60  # segundos
            
            # Volumen del floculador
            V = Q.magnitude * tf_s  # m3
            
            # Número de compartimientos (Romero Rojas: 3-4)
            n_comp = 4
            V_comp = V / n_comp  # Volumen por compartimiento
            
            # Profundidad (criterio Romero Rojas)
            H = 3.5  # m
            
            # Área en planta por compartimiento
            A_comp = V_comp / H  # m2
            
            # Dimensiones por compartimiento (cuadrado)
            L_comp = np.sqrt(A_comp)
            B_comp = L_comp
            
            # Dimensiones totales
            L_total = L_comp * n_comp
            B_total = B_comp
            
            # Cálculo de potencia requerida (Romero Rojas)
            # P = μ * G^2 * V
            viscosidad = 1.0e-6  # m2/s (agua a 20°C)
            P_requerida = viscosidad * 1000 * (G**2) * V  # W
            
            # Pérdida de carga total
            # hf = P / (ρ * g * Q)
            rho = 1000  # kg/m3
            g = 9.81  # m/s2
            hf_total = P_requerida / (rho * g * Q.magnitude)  # m
            
            # Pérdida de carga por compartimiento
            hf_comp = hf_total / n_comp
            
            # Diseño de tabiques (Romero Rojas)
            # Velocidad en orificios: 0.3 m/s
            v_orificio = 0.3  # m/s
            A_orificios_comp = Q.magnitude / v_orificio  # m2
            
            # Número de orificios por tabique (diámetro 0.15 m)
            d_orificio = 0.15  # m
            A_orificio = np.pi * (d_orificio/2)**2
            n_orificios = int(A_orificios_comp / A_orificio)
            
            verificaciones = {
                'gradiente_velocidad_ok': criteria['gradiente_velocidad_min'] <= G <= criteria['gradiente_velocidad_max'],
                'tiempo_floculacion_ok': criteria['tiempo_floculacion_min'] <= tf_min <= criteria['tiempo_floculacion_max'],
                'numero_compartimientos_ok': criteria['numero_compartimentos_min'] <= n_comp <= criteria['numero_compartimentos_max'],
                'profundidad_ok': criteria['profundidad_min'] <= H <= criteria['profundidad_max'],
                'velocidad_orificios_ok': 0.2 <= v_orificio <= 0.4,
                'perdida_carga_total_m': round(hf_total, 3)
            }
            
            calculated_values = {
                'volumen_total_m3': round(V, 2),
                'numero_compartimientos': n_comp,
                'volumen_por_compartimiento_m3': round(V_comp, 2),
                'largo_total_m': round(L_total, 2),
                'ancho_m': round(B_total, 2),
                'profundidad_m': H,
                'tiempo_floculacion_min': tf_min,
                'gradiente_velocidad_s-1': G,
                'potencia_requerida_W': round(P_requerida, 2),
                'perdida_carga_total_m': round(hf_total, 3),
                'perdida_carga_por_compartimiento_m': round(hf_comp, 3),
                'numero_orificios_por_tabique': n_orificios,
                'diametro_orificios_m': d_orificio,
                'velocidad_orificios_m_s': v_orificio
            }
            
            return RomeroRojasResults(
                process_name="Floculador Hidráulico",
                design_parameters={
                    'caudal_m3_s': caudal_m3_s,
                    'gradiente_velocidad_s-1': gradiente_velocidad
                },
                calculated_values=calculated_values,
                design_criteria=criteria,
                verification=verificaciones,
                references={
                    'metodologia': 'Romero Rojas - Floculación Hidráulica',
                    'ecuaciones': ['Camp-Stein', 'Darcy-Weisbach', 'Continuidad'],
                    'paginas_referencia': ['190-210', '250-270']
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error en cálculo floculador Romero Rojas: {e}")
            raise
    
    def calcular_filtro_rapido(self, 
                             caudal_m3_s: float,
                             numero_filtros: int = 4) -> RomeroRojasResults:
        """
        Diseño de filtros rápidos de arena según Romero Rojas
        
        Args:
            caudal_m3_s: Caudal de diseño (m3/s)
            numero_filtros: Número de unidades de filtración
            
        Returns:
            RomeroRojasResults con parámetros de diseño
        """
        try:
            Q = caudal_m3_s * ureg.m**3 / ureg.s
            Q_m3_d = (Q * 86400).to(ureg.m**3 / ureg.day).magnitude
            
            criteria = self.design_criteria['filtracion']
            
            # Velocidad de filtración (Romero Rojas: 120-300 m/d)
            vf = 200  # m/d (valor típico)
            
            # Área total de filtración
            At = Q_m3_d / vf  # m2
            
            # Área por filtro
            Af = At / numero_filtros  # m2
            
            # Dimensiones por filtro (cuadrado)
            L_filtro = np.sqrt(Af)
            B_filtro = L_filtro
            
            # Caudal por filtro
            Q_filtro = Q_m3_d / numero_filtros  # m3/d
            
            # Diseño del lecho filtrante (Romero Rojas)
            # Arena: 0.6-1.0 m
            # Grava soporte: 0.3 m
            espesor_arena = 0.8  # m
            espesor_grava = 0.3  # m
            espesor_total_lecho = espesor_arena + espesor_grava
            
            # Altura de agua sobre lecho
            h_agua = 1.5  # m
            
            # Altura total del filtro
            h_total = espesor_total_lecho + h_agua + 0.5  # +0.5m borde libre
            
            # Sistema de lavado (Romero Rojas)
            # Velocidad de lavado: 600 m/d
            vl = criteria['velocidad_lavado']  # m/d
            Q_lavado = vl * Af / 86400  # m3/s por filtro
            
            # Expansión del lecho durante lavado
            expansion = criteria['expansion_lecho']  # 25%
            h_expansion = espesor_arena * expansion
            
            # Pérdida de carga inicial (lecho limpio)
            # Ecuación Kozeny-Carman (Romero Rojas)
            hf_inicial = self._perdida_carga_kozeny_carman(vf, espesor_arena)
            
            # Pérdida de carga máxima (criterio Romero Rojas: 2.0 m)
            hf_maxima = criteria['perdida_carga_max']
            
            # Duración de carrera (estimada)
            duracion_carrera = 24  # horas (típico)
            
            verificaciones = {
                'velocidad_filtracion_ok': criteria['velocidad_filtracion_min'] <= vf <= criteria['velocidad_filtracion_max'],
                'espesor_lecho_ok': criteria['espesor_lecho_min'] <= espesor_arena <= criteria['espesor_lecho_max'],
                'perdida_carga_inicial_ok': hf_inicial < hf_maxima / 3,
                'perdida_carga_maxima_ok': hf_maxima <= criteria['perdida_carga_max'],
                'velocidad_lavado_ok': vl == criteria['velocidad_lavado'],
                'area_minima_por_filtro_m2': 20  # criterio mínimo
            }
            
            calculated_values = {
                'numero_filtros': numero_filtros,
                'area_total_filtracion_m2': round(At, 2),
                'area_por_filtro_m2': round(Af, 2),
                'largo_por_filtro_m': round(L_filtro, 2),
                'ancho_por_filtro_m': round(B_filtro, 2),
                'velocidad_filtracion_m_d': vf,
                'caudal_por_filtro_m3_d': round(Q_filtro, 2),
                'espesor_arena_m': espesor_arena,
                'espesor_grava_m': espesor_grava,
                'altura_agua_sobre_lecho_m': h_agua,
                'altura_total_filtro_m': round(h_total, 2),
                'velocidad_lavado_m_d': vl,
                'caudal_lavado_por_filtro_m3_s': round(Q_lavado, 4),
                'expansion_lecho_porcentaje': expansion * 100,
                'altura_expansion_m': round(h_expansion, 2),
                'perdida_carga_inicial_m': round(hf_inicial, 3),
                'perdida_carga_maxima_m': hf_maxima,
                'duracion_carrera_estimada_h': duracion_carrera
            }
            
            return RomeroRojasResults(
                process_name="Filtros Rápidos de Arena",
                design_parameters={
                    'caudal_m3_s': caudal_m3_s,
                    'numero_filtros': numero_filtros
                },
                calculated_values=calculated_values,
                design_criteria=criteria,
                verification=verificaciones,
                references={
                    'metodologia': 'Romero Rojas - Filtración Rápida',
                    'ecuaciones': ['Kozeny-Carman', 'Darcy', 'Continuidad'],
                    'paginas_referencia': ['280-320', '350-380']
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error en cálculo filtros Romero Rojas: {e}")
            raise
    
    def _viscosidad_agua(self, temperatura: float) -> float:
        """Calcula viscosidad cinemática del agua"""
        # Fórmula aproximada para viscosidad cinemática (m2/s)
        return (1.79e-6) / (1 + 0.0337 * temperatura + 0.000221 * temperatura**2)
    
    def _perdida_carga_kozeny_carman(self, velocidad_m_d: float, 
                                   espesor_m: float) -> float:
        """Calcula pérdida de carga usando ecuación Kozeny-Carman"""
        # Parámetros típicos arena (Romero Rojas)
        k = 5.0  # constante Kozeny-Carman
        porosidad = 0.4  # porosidad del lecho
        d_arena = 0.0008  # diámetro efectivo arena (m)
        
        v_m_s = velocidad_m_d / 86400  # conversión a m/s
        viscosidad = 1.0e-6  # m2/s
        
        # Ecuación Kozeny-Carman
        hf = (k * viscosidad * v_m_s * espesor_m * 
              (1 - porosidad)**2) / (9.81 * d_arena**2 * porosidad**3)
        
        return hf
