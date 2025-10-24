"""
Configuración de Pytest y Fixtures Comunes
Provee fixtures reutilizables para pruebas unitarias
"""
import pytest
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def parametros_agua_cruda_basica():
    """Parámetros típicos de agua cruda para pruebas"""
    return {
        'caudal': 50.0,  # L/s
        'temperatura': 18.0,  # °C
        'turbiedad': 25.0,  # NTU
        'color': 40.0,  # UPC
        'ph': 7.2,
        'alcalinidad': 80.0,  # mg/L CaCO3
        'dureza': 120.0,  # mg/L CaCO3
        'hierro': 0.8,  # mg/L
        'manganeso': 0.15,  # mg/L
        'coliformes_totales': 5000,  # UFC/100mL
    }

@pytest.fixture
def parametros_agua_cruda_critica():
    """Parámetros extremos para pruebas de límites"""
    return {
        'caudal': 200.0,  # L/s
        'temperatura': 30.0,  # °C
        'turbiedad': 500.0,  # NTU
        'color': 200.0,  # UPC
        'ph': 6.5,
        'alcalinidad': 30.0,  # mg/L CaCO3
        'dureza': 250.0,  # mg/L CaCO3
        'hierro': 3.0,  # mg/L
        'manganeso': 0.5,  # mg/L
        'coliformes_totales': 50000,  # UFC/100mL
    }

@pytest.fixture
def parametros_hidraulicos_tipicos():
    """Parámetros hidráulicos estándar"""
    return {
        'viscosidad_cinematica': 1.004e-6,  # m²/s a 20°C
        'densidad': 998.2,  # kg/m³ a 20°C
        'gravedad': 9.81,  # m/s²
        'rugosidad_concreto': 0.0012,  # m
        'rugosidad_pvc': 0.0000015,  # m
    }

@pytest.fixture
def limites_ras_2017():
    """Límites normativos RAS 2017 para validación"""
    return {
        'mezcla_rapida': {
            'gradiente_velocidad_min': 700,  # s⁻¹
            'gradiente_velocidad_max': 1500,  # s⁻¹
            'tiempo_retencion_min': 10,  # s
            'tiempo_retencion_max': 60,  # s
        },
        'floculacion': {
            'gradiente_velocidad_min': 20,  # s⁻¹
            'gradiente_velocidad_max': 80,  # s⁻¹
            'tiempo_retencion_min': 1200,  # s (20 min)
            'tiempo_retencion_max': 2400,  # s (40 min)
        },
        'sedimentacion': {
            'carga_superficial_min': 10,  # m³/m²/día
            'carga_superficial_max': 40,  # m³/m²/día
            'tiempo_retencion_min': 7200,  # s (2 h)
            'tiempo_retencion_max': 14400,  # s (4 h)
        },
        'filtracion': {
            'tasa_filtracion_min': 120,  # m³/m²/día
            'tasa_filtracion_max': 360,  # m³/m²/día
            'lecho_arena_min': 0.6,  # m
            'lecho_arena_max': 0.8,  # m
        }
    }

@pytest.fixture
def limites_res_2115():
    """Límites de calidad agua potable Res. 2115/2007"""
    return {
        'turbiedad_max': 2.0,  # NTU
        'color_max': 15.0,  # UPC
        'ph_min': 6.5,
        'ph_max': 9.0,
        'cloro_residual_min': 0.3,  # mg/L
        'cloro_residual_max': 2.0,  # mg/L
        'coliformes_totales_max': 0,  # UFC/100mL
        'escherichia_coli_max': 0,  # UFC/100mL
    }

@pytest.fixture
def mock_datos_abiertos_response():
    """Respuesta simulada del portal Datos Abiertos"""
    return [
        {
            'id': 'abc123',
            'name': 'Calidad del Agua - IDEAM',
            'description': 'Dataset de prueba para calidad del agua',
            'resource': {
                'columns_name': ['fecha', 'municipio', 'ph', 'turbiedad', 'color']
            }
        },
        {
            'id': 'def456',
            'name': 'IRCA Nacional',
            'description': 'Índice de Riesgo de Calidad del Agua',
            'resource': {
                'columns_name': ['departamento', 'municipio', 'irca', 'nivel_riesgo']
            }
        }
    ]

@pytest.fixture
def mock_diseño_completo():
    """Resultado completo de diseño simulado para pruebas de reportes"""
    return {
        'proyecto': {
            'nombre': 'PTAP Test',
            'ubicacion': 'Municipio Test',
            'caudal_diseno': 50.0
        },
        'procesos': {
            'aireacion': {
                'tipo': 'cascada',
                'numero_bandejas': 4,
                'altura_caida': 0.3,
                'eficiencia_remocion_hierro': 60.0
            },
            'mezcla_rapida': {
                'tipo': 'resalto_hidraulico',
                'gradiente_velocidad': 1000,
                'tiempo_retencion': 30,
                'dosis_coagulante': 25.0
            },
            'floculacion': {
                'tipo': 'pantallas',
                'numero_camaras': 3,
                'gradiente_velocidad': 50,
                'tiempo_retencion': 1800
            },
            'sedimentacion': {
                'tipo': 'alta_tasa',
                'carga_superficial': 25.0,
                'tiempo_retencion': 10800,
                'area_sedimentador': 120.0
            },
            'filtracion': {
                'tipo': 'rapida_gravedad',
                'numero_filtros': 2,
                'tasa_filtracion': 240,
                'area_filtracion': 18.0
            },
            'desinfeccion': {
                'tipo': 'cloro_gas',
                'dosis_cloro': 2.5,
                'tiempo_contacto': 1800,
                'cloro_residual': 0.8
            }
        },
        'conformidad': {
            'ras_2017': True,
            'res_2115': True,
            'validaciones_pasadas': 15,
            'validaciones_totales': 15
        }
    }
