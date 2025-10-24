"""
Tests para el módulo core/hydraulics.py
Validación de simulación hidráulica
"""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.hydraulics import HydraulicSimulator

class TestCalculosBasicos:
    """Tests para cálculos hidráulicos fundamentales"""
    
    def test_numero_reynolds_flujo_turbulento(self, parametros_hidraulicos_tipicos):
        """Verifica cálculo de número de Reynolds para flujo turbulento"""
        sim = HydraulicSimulator()
        
        reynolds = sim.calcular_reynolds(
            velocidad=1.5,  # m/s
            diametro=0.3,  # m
            viscosidad_cinematica=parametros_hidraulicos_tipicos['viscosidad_cinematica']
        )
        
        assert reynolds > 4000  # Flujo turbulento
    
    def test_numero_reynolds_flujo_laminar(self, parametros_hidraulicos_tipicos):
        """Verifica cálculo de número de Reynolds para flujo laminar"""
        sim = HydraulicSimulator()
        
        reynolds = sim.calcular_reynolds(
            velocidad=0.01,  # m/s
            diametro=0.05,  # m
            viscosidad_cinematica=parametros_hidraulicos_tipicos['viscosidad_cinematica']
        )
        
        assert reynolds < 2000  # Flujo laminar
    
    def test_numero_froude_flujo_subcritico(self):
        """Verifica cálculo de número de Froude para flujo subcrítico"""
        sim = HydraulicSimulator()
        
        froude = sim.calcular_froude(
            velocidad=0.5,  # m/s
            profundidad=0.3,  # m
            gravedad=9.81
        )
        
        assert froude < 1.0  # Flujo subcrítico
    
    def test_numero_froude_flujo_supercritico(self):
        """Verifica cálculo de número de Froude para flujo supercrítico"""
        sim = HydraulicSimulator()
        
        froude = sim.calcular_froude(
            velocidad=3.0,  # m/s
            profundidad=0.2,  # m
            gravedad=9.81
        )
        
        assert froude > 1.0  # Flujo supercrítico

class TestPerdidaCarga:
    """Tests para cálculos de pérdida de carga"""
    
    def test_perdida_carga_darcy_weisbach(self, parametros_hidraulicos_tipicos):
        """Verifica cálculo con ecuación de Darcy-Weisbach"""
        sim = HydraulicSimulator()
        
        perdida = sim.calcular_perdida_carga_darcy(
            longitud=100,  # m
            diametro=0.3,  # m
            velocidad=1.5,  # m/s
            rugosidad=parametros_hidraulicos_tipicos['rugosidad_pvc'],
            viscosidad_cinematica=parametros_hidraulicos_tipicos['viscosidad_cinematica']
        )
        
        assert perdida > 0
        assert perdida < 10  # m, valor razonable
    
    def test_perdida_carga_hazen_williams(self):
        """Verifica cálculo con ecuación de Hazen-Williams"""
        sim = HydraulicSimulator()
        
        perdida = sim.calcular_perdida_carga_hazen_williams(
            longitud=100,  # m
            diametro=0.3,  # m
            caudal=0.05,  # m³/s
            coeficiente_c=140  # PVC
        )
        
        assert perdida > 0
        assert perdida < 10  # m
    
    def test_perdidas_menores_accesorios(self):
        """Verifica cálculo de pérdidas menores"""
        sim = HydraulicSimulator()
        
        # Pérdida en codo 90°
        perdida_codo = sim.calcular_perdida_menor(
            velocidad=1.5,  # m/s
            coeficiente_k=0.9  # Codo 90°
        )
        
        assert perdida_codo > 0
        assert perdida_codo < 1  # m

class TestGradientesVelocidad:
    """Tests para cálculos de gradientes de velocidad"""
    
    def test_gradiente_mezcla_rapida(self, parametros_hidraulicos_tipicos):
        """Verifica cálculo de gradiente para mezcla rápida"""
        sim = HydraulicSimulator()
        
        gradiente = sim.calcular_gradiente_velocidad(
            potencia=500,  # W
            volumen=0.5,  # m³
            viscosidad_dinamica=0.001,  # Pa·s
            temperatura=20  # °C
        )
        
        # Debe estar en rango RAS para mezcla rápida (700-1500 s⁻¹)
        assert gradiente >= 500
        assert gradiente <= 2000
    
    def test_gradiente_floculacion(self, parametros_hidraulicos_tipicos):
        """Verifica cálculo de gradiente para floculación"""
        sim = HydraulicSimulator()
        
        gradiente = sim.calcular_gradiente_velocidad(
            potencia=100,  # W
            volumen=50,  # m³
            viscosidad_dinamica=0.001,  # Pa·s
            temperatura=20  # °C
        )
        
        # Debe estar en rango RAS para floculación (20-80 s⁻¹)
        assert gradiente >= 10
        assert gradiente <= 100

class TestTiemposRetencion:
    """Tests para cálculos de tiempos de retención"""
    
    def test_tiempo_retencion_hidraulico(self):
        """Verifica cálculo de tiempo de retención"""
        sim = HydraulicSimulator()
        
        tiempo = sim.calcular_tiempo_retencion(
            volumen=100,  # m³
            caudal=0.05  # m³/s
        )
        
        # Tiempo en segundos
        assert tiempo > 0
        assert tiempo == pytest.approx(2000, rel=0.01)  # 100/0.05 = 2000 s
    
    def test_tiempo_retencion_diferentes_unidades(self):
        """Verifica conversión de unidades de tiempo"""
        sim = HydraulicSimulator()
        
        tiempo_segundos = sim.calcular_tiempo_retencion(
            volumen=50,  # m³
            caudal=0.05  # m³/s
        )
        
        tiempo_minutos = tiempo_segundos / 60
        tiempo_horas = tiempo_segundos / 3600
        
        assert tiempo_minutos == pytest.approx(16.67, rel=0.01)
        assert tiempo_horas == pytest.approx(0.278, rel=0.01)

class TestVelocidadesCriticas:
    """Tests para verificación de velocidades límite"""
    
    def test_velocidad_minima_autolimpieza(self):
        """Verifica velocidad mínima para autolimpieza"""
        sim = HydraulicSimulator()
        
        velocidad = 0.6  # m/s
        es_adecuada = sim.verificar_velocidad_minima(velocidad, minima=0.5)
        
        assert es_adecuada is True
    
    def test_velocidad_maxima_erosion(self):
        """Verifica velocidad máxima para evitar erosión"""
        sim = HydraulicSimulator()
        
        velocidad = 2.5  # m/s
        es_adecuada = sim.verificar_velocidad_maxima(velocidad, maxima=3.0)
        
        assert es_adecuada is True
    
    def test_velocidad_fuera_rango(self):
        """Verifica detección de velocidades fuera de rango"""
        sim = HydraulicSimulator()
        
        velocidad_muy_baja = 0.2  # m/s
        velocidad_muy_alta = 5.0  # m/s
        
        assert sim.verificar_velocidad_minima(velocidad_muy_baja, minima=0.5) is False
        assert sim.verificar_velocidad_maxima(velocidad_muy_alta, maxima=3.0) is False

class TestResaltoHidraulico:
    """Tests para cálculos de resalto hidráulico"""
    
    def test_profundidad_conjugada(self):
        """Verifica cálculo de profundidades conjugadas"""
        sim = HydraulicSimulator()
        
        y2 = sim.calcular_profundidad_conjugada(
            y1=0.15,  # m
            froude1=3.5
        )
        
        assert y2 > 0.15  # y2 debe ser mayor que y1
        assert y2 < 2.0  # Valor razonable
    
    def test_energia_disipada_resalto(self):
        """Verifica cálculo de energía disipada en resalto"""
        sim = HydraulicSimulator()
        
        energia = sim.calcular_energia_disipada_resalto(
            y1=0.15,  # m
            y2=0.45,  # m
            velocidad1=5.0  # m/s
        )
        
        assert energia > 0
        assert energia < 10  # m

class TestPerfilHidraulico:
    """Tests para cálculo de perfil hidráulico"""
    
    def test_perfil_simple(self, parametros_agua_cruda_basica):
        """Verifica cálculo de perfil hidráulico simple"""
        sim = HydraulicSimulator()
        
        caudal_m3s = parametros_agua_cruda_basica['caudal'] / 1000  # L/s a m³/s
        
        perfil = sim.calcular_perfil_hidraulico(
            caudal=caudal_m3s,
            longitud_total=50,  # m
            rugosidad=0.0012,  # concreto
            diametro=0.4  # m
        )
        
        assert perfil is not None
        assert len(perfil) > 0
    
    def test_perfil_con_cambios_diametro(self, parametros_agua_cruda_basica):
        """Verifica perfil con cambios de sección"""
        sim = HydraulicSimulator()
        
        caudal_m3s = parametros_agua_cruda_basica['caudal'] / 1000
        
        # Simular tramo con cambio de diámetro
        tramos = [
            {'longitud': 20, 'diametro': 0.3},
            {'longitud': 30, 'diametro': 0.4}
        ]
        
        perfil_completo = []
        for tramo in tramos:
            perfil_tramo = sim.calcular_perfil_hidraulico(
                caudal=caudal_m3s,
                longitud_total=tramo['longitud'],
                diametro=tramo['diametro']
            )
            if perfil_tramo:
                perfil_completo.extend(perfil_tramo)
        
        assert len(perfil_completo) > 0
