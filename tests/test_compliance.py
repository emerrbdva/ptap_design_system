"""
Tests para módulos de compliance (RAS 2017, Res. 2115)
Validación de cumplimiento normativo
"""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from compliance.ras_2017 import RAS2017Validator
from compliance.res_2115 import Resolucion2115Validator

class TestRAS2017MezclaRapida:
    """Tests para validación RAS 2017 - Mezcla Rápida"""
    
    def test_gradiente_dentro_rango(self, limites_ras_2017):
        """Verifica validación de gradiente dentro de rango"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'resalto_hidraulico',
            'gradiente_velocidad': 1000,  # s⁻¹
            'tiempo_retencion': 30  # s
        }
        
        resultado = validator.validar_mezcla_rapida(diseño)
        
        assert resultado['conforme'] is True
        assert 'gradiente_velocidad' in resultado['validaciones']
    
    def test_gradiente_fuera_rango(self):
        """Verifica detección de gradiente fuera de rango"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'resalto_hidraulico',
            'gradiente_velocidad': 500,  # Muy bajo
            'tiempo_retencion': 30
        }
        
        resultado = validator.validar_mezcla_rapida(diseño)
        
        assert resultado['conforme'] is False
        assert any('gradiente_velocidad' in v for v in resultado['no_conformidades'])

class TestRAS2017Floculacion:
    """Tests para validación RAS 2017 - Floculación"""
    
    def test_floculacion_conforme(self, limites_ras_2017):
        """Verifica validación de floculación conforme"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'pantallas',
            'gradiente_velocidad': 50,  # s⁻¹
            'tiempo_retencion': 1800,  # s (30 min)
            'numero_camaras': 3
        }
        
        resultado = validator.validar_floculacion(diseño)
        
        assert resultado['conforme'] is True
    
    def test_tiempo_retencion_insuficiente(self):
        """Verifica detección de tiempo de retención insuficiente"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'pantallas',
            'gradiente_velocidad': 50,
            'tiempo_retencion': 600,  # Muy corto
            'numero_camaras': 2
        }
        
        resultado = validator.validar_floculacion(diseño)
        
        assert resultado['conforme'] is False

class TestRAS2017Sedimentacion:
    """Tests para validación RAS 2017 - Sedimentación"""
    
    def test_sedimentacion_alta_tasa_conforme(self, limites_ras_2017):
        """Verifica validación de sedimentador de alta tasa"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'alta_tasa',
            'carga_superficial': 25.0,  # m³/m²/día
            'tiempo_retencion': 10800,  # s (3 h)
            'area_sedimentador': 100.0
        }
        
        resultado = validator.validar_sedimentacion(diseño)
        
        assert resultado['conforme'] is True
    
    def test_carga_superficial_excesiva(self):
        """Verifica detección de carga superficial excesiva"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'convencional',
            'carga_superficial': 50.0,  # Muy alta
            'tiempo_retencion': 7200
        }
        
        resultado = validator.validar_sedimentacion(diseño)
        
        assert resultado['conforme'] is False

class TestRAS2017Filtracion:
    """Tests para validación RAS 2017 - Filtración"""
    
    def test_filtracion_rapida_conforme(self, limites_ras_2017):
        """Verifica validación de filtros rápidos"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'rapida_gravedad',
            'tasa_filtracion': 240,  # m³/m²/día
            'numero_filtros': 2,
            'espesor_lecho_arena': 0.7  # m
        }
        
        resultado = validator.validar_filtracion(diseño)
        
        assert resultado['conforme'] is True
    
    def test_filtros_insuficientes(self):
        """Verifica detección de número insuficiente de filtros"""
        validator = RAS2017Validator()
        
        diseño = {
            'tipo': 'rapida_gravedad',
            'tasa_filtracion': 240,
            'numero_filtros': 1,  # Mínimo 2
            'espesor_lecho_arena': 0.7
        }
        
        resultado = validator.validar_filtracion(diseño)
        
        # RAS requiere mínimo 2 filtros
        assert resultado['conforme'] is False or 'advertencia' in str(resultado).lower()

class TestRAS2017MatrizConformidad:
    """Tests para generación de matriz de conformidad"""
    
    def test_matriz_diseño_completo(self, mock_diseño_completo):
        """Verifica generación de matriz para diseño completo"""
        validator = RAS2017Validator()
        
        matriz = validator.generar_matriz_conformidad(
            mock_diseño_completo['procesos']
        )
        
        assert matriz is not None
        assert 'mezcla_rapida' in matriz
        assert 'floculacion' in matriz
        assert 'sedimentacion' in matriz
        assert 'filtracion' in matriz
    
    def test_porcentaje_conformidad(self, mock_diseño_completo):
        """Verifica cálculo de porcentaje de conformidad"""
        validator = RAS2017Validator()
        
        resultado = validator.calcular_conformidad_total(
            mock_diseño_completo['procesos']
        )
        
        assert 'porcentaje_conformidad' in resultado
        assert resultado['porcentaje_conformidad'] >= 0
        assert resultado['porcentaje_conformidad'] <= 100

class TestRes2115CalidadAgua:
    """Tests para validación Resolución 2115/2007"""
    
    def test_agua_potable_conforme(self, limites_res_2115):
        """Verifica validación de agua potable conforme"""
        validator = Resolucion2115Validator()
        
        parametros_agua_tratada = {
            'turbiedad': 1.5,  # NTU
            'color': 10,  # UPC
            'ph': 7.2,
            'cloro_residual': 0.5,  # mg/L
            'coliformes_totales': 0,
            'escherichia_coli': 0
        }
        
        resultado = validator.validar_calidad_agua(parametros_agua_tratada)
        
        assert resultado['conforme'] is True
    
    def test_turbiedad_excesiva(self, limites_res_2115):
        """Verifica detección de turbiedad excesiva"""
        validator = Resolucion2115Validator()
        
        parametros = {
            'turbiedad': 3.0,  # Excede límite de 2.0 NTU
            'color': 10,
            'ph': 7.2,
            'cloro_residual': 0.5
        }
        
        resultado = validator.validar_calidad_agua(parametros)
        
        assert resultado['conforme'] is False
        assert 'turbiedad' in str(resultado['no_conformidades']).lower()
    
    def test_cloro_residual_bajo(self):
        """Verifica detección de cloro residual insuficiente"""
        validator = Resolucion2115Validator()
        
        parametros = {
            'turbiedad': 1.0,
            'color': 10,
            'ph': 7.2,
            'cloro_residual': 0.2  # Menor que 0.3 mg/L
        }
        
        resultado = validator.validar_calidad_agua(parametros)
        
        assert resultado['conforme'] is False
    
    def test_presencia_coliformes(self):
        """Verifica detección de coliformes"""
        validator = Resolucion2115Validator()
        
        parametros = {
            'turbiedad': 1.0,
            'color': 10,
            'ph': 7.2,
            'cloro_residual': 0.8,
            'coliformes_totales': 5  # No aceptable
        }
        
        resultado = validator.validar_calidad_agua(parametros)
        
        assert resultado['conforme'] is False

class TestRes2115FrecuenciaMuestreo:
    """Tests para determinación de frecuencia de muestreo"""
    
    def test_frecuencia_segun_poblacion(self):
        """Verifica determinación de frecuencia según población"""
        validator = Resolucion2115Validator()
        
        # Población pequeña (< 2,500 habitantes)
        freq_pequeña = validator.determinar_frecuencia_muestreo(poblacion=2000)
        assert freq_pequeña is not None
        
        # Población mediana (2,500 - 12,500)
        freq_mediana = validator.determinar_frecuencia_muestreo(poblacion=8000)
        assert freq_mediana is not None
        
        # Población grande (> 12,500)
        freq_grande = validator.determinar_frecuencia_muestreo(poblacion=50000)
        assert freq_grande is not None
    
    def test_frecuencia_diferentes_parametros(self):
        """Verifica frecuencias para diferentes tipos de parámetros"""
        validator = Resolucion2115Validator()
        
        poblacion = 10000
        
        # Parámetros físico-químicos
        freq_fisicoquimico = validator.determinar_frecuencia_muestreo(
            poblacion=poblacion,
            tipo_parametro='fisicoquimico'
        )
        
        # Parámetros microbiológicos
        freq_microbiologico = validator.determinar_frecuencia_muestreo(
            poblacion=poblacion,
            tipo_parametro='microbiologico'
        )
        
        assert freq_fisicoquimico is not None
        assert freq_microbiologico is not None

class TestIntegracionValidadores:
    """Tests de integración entre validadores"""
    
    def test_validacion_completa_ptap(self, mock_diseño_completo):
        """Verifica validación completa de PTAP"""
        ras_validator = RAS2017Validator()
        res_validator = Resolucion2115Validator()
        
        # Validar diseño según RAS
        conformidad_ras = ras_validator.calcular_conformidad_total(
            mock_diseño_completo['procesos']
        )
        
        # Validar calidad agua según Res. 2115
        parametros_salida = {
            'turbiedad': 1.0,
            'color': 8,
            'ph': 7.5,
            'cloro_residual': 0.6,
            'coliformes_totales': 0
        }
        
        conformidad_res = res_validator.validar_calidad_agua(parametros_salida)
        
        # Ambas validaciones deben pasar
        assert conformidad_ras['porcentaje_conformidad'] > 90
        assert conformidad_res['conforme'] is True
