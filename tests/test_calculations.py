"""
Tests para el módulo core/calculations.py
Validación de cálculos de procesos unitarios
"""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.calculations import TreatmentCalculator

class TestAireacion:
    """Tests para cálculos de aireación"""
    
    def test_aireacion_cascada_basica(self, parametros_agua_cruda_basica):
        """Verifica cálculo básico de aireación por cascada"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_aireacion(
            tipo='cascada',
            caudal=parametros_agua_cruda_basica['caudal'],
            concentracion_inicial=parametros_agua_cruda_basica['hierro'],
            numero_bandejas=4
        )
        
        assert resultado is not None
        assert 'numero_bandejas' in resultado
        assert resultado['numero_bandejas'] >= 3
        assert resultado['numero_bandejas'] <= 6
        assert 'eficiencia_remocion' in resultado
        assert resultado['eficiencia_remocion'] > 0
    
    def test_aireacion_valores_extremos(self, parametros_agua_cruda_critica):
        """Verifica comportamiento con valores extremos"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_aireacion(
            tipo='cascada',
            caudal=parametros_agua_cruda_critica['caudal'],
            concentracion_inicial=parametros_agua_cruda_critica['hierro'],
            numero_bandejas=6
        )
        
        assert resultado['numero_bandejas'] >= 3
        assert resultado['eficiencia_remocion'] <= 100.0

class TestMezclaRapida:
    """Tests para cálculos de mezcla rápida"""
    
    def test_mezcla_rapida_resalto(self, parametros_agua_cruda_basica, limites_ras_2017):
        """Verifica diseño de mezcla rápida por resalto hidráulico"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_mezcla_rapida(
            tipo='resalto_hidraulico',
            caudal=parametros_agua_cruda_basica['caudal'],
            temperatura=parametros_agua_cruda_basica['temperatura']
        )
        
        assert resultado is not None
        assert 'gradiente_velocidad' in resultado
        
        # Validar contra RAS 2017
        limites = limites_ras_2017['mezcla_rapida']
        assert resultado['gradiente_velocidad'] >= limites['gradiente_velocidad_min']
        assert resultado['gradiente_velocidad'] <= limites['gradiente_velocidad_max']
        
        if 'tiempo_retencion' in resultado:
            assert resultado['tiempo_retencion'] >= limites['tiempo_retencion_min']
            assert resultado['tiempo_retencion'] <= limites['tiempo_retencion_max']
    
    def test_mezcla_rapida_dosis_coagulante(self, parametros_agua_cruda_basica):
        """Verifica cálculo de dosis de coagulante"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_mezcla_rapida(
            tipo='resalto_hidraulico',
            caudal=parametros_agua_cruda_basica['caudal'],
            turbiedad=parametros_agua_cruda_basica['turbiedad'],
            ph=parametros_agua_cruda_basica['ph']
        )
        
        if 'dosis_coagulante' in resultado:
            assert resultado['dosis_coagulante'] > 0
            assert resultado['dosis_coagulante'] < 100  # mg/L razonable

class TestFloculacion:
    """Tests para cálculos de floculación"""
    
    def test_floculacion_pantallas(self, parametros_agua_cruda_basica, limites_ras_2017):
        """Verifica diseño de floculación con pantallas"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_floculacion(
            tipo='pantallas',
            caudal=parametros_agua_cruda_basica['caudal'],
            temperatura=parametros_agua_cruda_basica['temperatura']
        )
        
        assert resultado is not None
        assert 'gradiente_velocidad' in resultado
        
        # Validar contra RAS 2017
        limites = limites_ras_2017['floculacion']
        assert resultado['gradiente_velocidad'] >= limites['gradiente_velocidad_min']
        assert resultado['gradiente_velocidad'] <= limites['gradiente_velocidad_max']
        
        if 'tiempo_retencion' in resultado:
            assert resultado['tiempo_retencion'] >= limites['tiempo_retencion_min']
    
    def test_floculacion_numero_camaras(self, parametros_agua_cruda_basica):
        """Verifica que se diseñen múltiples cámaras"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_floculacion(
            tipo='pantallas',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        if 'numero_camaras' in resultado:
            assert resultado['numero_camaras'] >= 2
            assert resultado['numero_camaras'] <= 4

class TestSedimentacion:
    """Tests para cálculos de sedimentación"""
    
    def test_sedimentacion_alta_tasa(self, parametros_agua_cruda_basica, limites_ras_2017):
        """Verifica diseño de sedimentador de alta tasa"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_sedimentacion(
            tipo='alta_tasa',
            caudal=parametros_agua_cruda_basica['caudal'],
            temperatura=parametros_agua_cruda_basica['temperatura']
        )
        
        assert resultado is not None
        assert 'carga_superficial' in resultado
        
        # Validar contra RAS 2017
        limites = limites_ras_2017['sedimentacion']
        assert resultado['carga_superficial'] >= limites['carga_superficial_min']
        assert resultado['carga_superficial'] <= limites['carga_superficial_max']
    
    def test_sedimentacion_area_minima(self, parametros_agua_cruda_basica):
        """Verifica cálculo de área de sedimentación"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_sedimentacion(
            tipo='convencional',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        if 'area_sedimentador' in resultado:
            # Área debe ser razonable para el caudal
            assert resultado['area_sedimentador'] > 0
            assert resultado['area_sedimentador'] < 1000  # m²

class TestFiltracion:
    """Tests para cálculos de filtración"""
    
    def test_filtracion_rapida_gravedad(self, parametros_agua_cruda_basica, limites_ras_2017):
        """Verifica diseño de filtros rápidos por gravedad"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_filtracion(
            tipo='rapida_gravedad',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        assert resultado is not None
        assert 'tasa_filtracion' in resultado
        
        # Validar contra RAS 2017
        limites = limites_ras_2017['filtracion']
        assert resultado['tasa_filtracion'] >= limites['tasa_filtracion_min']
        assert resultado['tasa_filtracion'] <= limites['tasa_filtracion_max']
    
    def test_filtracion_numero_unidades(self, parametros_agua_cruda_basica):
        """Verifica que se diseñen al menos 2 filtros"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_filtracion(
            tipo='rapida_gravedad',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        if 'numero_filtros' in resultado:
            assert resultado['numero_filtros'] >= 2
    
    def test_filtracion_lecho_arena(self, parametros_agua_cruda_basica, limites_ras_2017):
        """Verifica espesor de lecho filtrante"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_filtracion(
            tipo='rapida_gravedad',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        limites = limites_ras_2017['filtracion']
        if 'espesor_lecho_arena' in resultado:
            assert resultado['espesor_lecho_arena'] >= limites['lecho_arena_min']
            assert resultado['espesor_lecho_arena'] <= limites['lecho_arena_max']

class TestDesinfeccion:
    """Tests para cálculos de desinfección"""
    
    def test_desinfeccion_cloro_gas(self, parametros_agua_cruda_basica):
        """Verifica diseño de cloración"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_desinfeccion(
            tipo='cloro_gas',
            caudal=parametros_agua_cruda_basica['caudal'],
            coliformes_inicial=parametros_agua_cruda_basica['coliformes_totales']
        )
        
        assert resultado is not None
        assert 'dosis_cloro' in resultado
        assert resultado['dosis_cloro'] > 0
        assert resultado['dosis_cloro'] < 10  # mg/L razonable
    
    def test_desinfeccion_cloro_residual(self, parametros_agua_cruda_basica, limites_res_2115):
        """Verifica que se alcance cloro residual adecuado"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_desinfeccion(
            tipo='cloro_gas',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        if 'cloro_residual' in resultado:
            limites = limites_res_2115
            assert resultado['cloro_residual'] >= limites['cloro_residual_min']
            assert resultado['cloro_residual'] <= limites['cloro_residual_max']
    
    def test_desinfeccion_tiempo_contacto(self, parametros_agua_cruda_basica):
        """Verifica tiempo de contacto mínimo"""
        calc = TreatmentCalculator()
        resultado = calc.calcular_desinfeccion(
            tipo='cloro_gas',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        if 'tiempo_contacto' in resultado:
            # Tiempo de contacto mínimo 30 minutos
            assert resultado['tiempo_contacto'] >= 1800

class TestIntegracionCompleta:
    """Tests de integración entre módulos"""
    
    def test_tren_completo_tratamiento(self, parametros_agua_cruda_basica):
        """Verifica que se pueda diseñar un tren completo de tratamiento"""
        calc = TreatmentCalculator()
        
        # Diseñar cada proceso
        aireacion = calc.calcular_aireacion(
            tipo='cascada',
            caudal=parametros_agua_cruda_basica['caudal'],
            concentracion_inicial=parametros_agua_cruda_basica['hierro']
        )
        
        mezcla = calc.calcular_mezcla_rapida(
            tipo='resalto_hidraulico',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        floculacion = calc.calcular_floculacion(
            tipo='pantallas',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        sedimentacion = calc.calcular_sedimentacion(
            tipo='alta_tasa',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        filtracion = calc.calcular_filtracion(
            tipo='rapida_gravedad',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        desinfeccion = calc.calcular_desinfeccion(
            tipo='cloro_gas',
            caudal=parametros_agua_cruda_basica['caudal']
        )
        
        # Verificar que todos los procesos retornen resultados
        assert all([aireacion, mezcla, floculacion, sedimentacion, filtracion, desinfeccion])
