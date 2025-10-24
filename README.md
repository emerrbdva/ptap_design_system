# Sistema Integral de Diseño de Plantas de Potabilización de Agua (PTAP)

## 🎯 Descripción General

Sistema completo en Python para el diseño de plantas de potabilización de agua (PTAP) adaptable a contextos urbanos y rurales, con módulos de diseño, simulación hidráulica, validación normativa automática, conectividad a fuentes oficiales gubernamentales y generación de documentos técnicos profesionales.

**Características principales:**
- ✅ Operación 100% local con IA sin costos de API externas
- ✅ Validación automática contra normativa colombiana (RAS 2017, Res. 2115/2007, Dec. 1575/2007)
- ✅ Conexión a portales gubernamentales (Datos Abiertos Colombia, IDEAM, SIAC)
- ✅ Cálculos verificados con SymPy/SciPy/Pint (no números directos de LLM)
- ✅ Generación de reportes técnicos profesionales (PDF, Excel, DXF)
- ✅ Trazabilidad completa de cálculos, decisiones y referencias normativas

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
ptap_design_system/
├── app/                    # Interfaz de usuario y aplicación principal
│   ├── web_interface.py   # Interfaz web Flask/FastAPI
│   └── sensor_integration.py  # Integración con sensores IoT
├── core/                   # Núcleo de cálculos y simulación
│   ├── calculations.py    # Procesos unitarios de tratamiento
│   ├── hydraulics.py      # Simulación hidráulica
│   └── units.py          # Gestión de unidades con Pint
├── compliance/            # Validación normativa automática
│   ├── ras_2017.py       # Validadores Resolución 0330/2017
│   ├── res_2115.py       # Validadores Resolución 2115/2007
│   └── dec_1575.py       # Validadores Decreto 1575/2007
├── data_connectors/       # Conectores a portales gubernamentales
│   ├── datos_abiertos.py # Datos Abiertos Colombia (SODA/SoQL)
│   ├── ideam.py          # IDEAM/DHIME series hidrometeorológicas
│   └── siac.py           # SIAC/MinAmbiente recursos hídricos
├── ai/                    # Orquestación de modelos IA locales
│   ├── model_router.py   # Router de intención entre modelos
│   ├── reasoning.py      # DeepSeek-R1 razonamiento técnico
│   ├── math_solver.py    # Qwen2.5-Math resolución matemática
│   └── writer.py         # Mistral-7B redacción técnica
├── reporting/             # Generación de documentos
│   ├── pdf_generator.py  # PDFs profesionales con ReportLab
│   └── excel_exporter.py # Exportación a Excel
├── cad/                   # Exportación CAD
│   └── dxf_generator.py  # Generación DXF con ezdxf
├── utils/                 # Utilidades del sistema
│   ├── traceability.py   # Sistema de trazabilidad
│   └── version_monitor.py # Monitor de cambios normativos
├── tests/                 # Pruebas unitarias e integración
├── docs/                  # Documentación técnica
├── config/                # Archivos de configuración
└── examples/              # Ejemplos de uso
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.9 o superior
- [Ollama](https://ollama.com/) instalado y ejecutándose localmente
- 8GB RAM mínimo (16GB recomendado para modelos grandes)

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### Configuración de Modelos IA Locales

```bash
# Instalar modelos con Ollama
ollama pull deepseek-r1:8b           # o deepseek-r1:14b según hardware
ollama pull qwen2.5-math:7b          # o tamaño mayor según recursos
ollama pull mistral:7b-instruct-v0.3
```

### Configuración Inicial

```bash
# Copiar archivo de configuración ejemplo
cp config/config.example.yaml config/config.yaml

# Editar configuración según necesidades
# Configurar URLs de portales, credenciales, rutas, etc.
```

## 📋 Normativa Implementada

### Resolución 0330 de 2017 (RAS)
- Reglamento técnico del sector de agua potable y saneamiento básico
- Validación automática de parámetros de diseño por proceso unitario
- Referencias directas a artículos, tablas y rangos normativos

### Resolución 2115 de 2007
- Características, instrumentos básicos y frecuencias del sistema de control y vigilancia
- Validación de calidad del agua para consumo humano
- Límites máximos permisibles por parámetro

### Decreto 1575 de 2007
- Sistema para protección y control de la calidad del agua
- Responsabilidades y procedimientos de vigilancia
- Frecuencias de muestreo y análisis

## 🔬 Procesos Unitarios Implementados

1. **Aireación**: Oxidación y remoción de gases
2. **Mezcla Rápida**: Dispersión de coagulante
3. **Coagulación-Floculación**: Desestabilización y aglomeración de partículas
4. **Sedimentación**: Remoción de partículas por gravedad
5. **Filtración**: Remoción física de partículas remanentes
6. **Desinfección**: Inactivación de microorganismos

Cada proceso incluye:
- ✅ Cálculos dimensionales verificados con SymPy/SciPy
- ✅ Control de unidades con Pint
- ✅ Validación de rangos según RAS 2017
- ✅ Trazabilidad completa de fórmulas y referencias

## 🌐 Conectividad a Portales Gubernamentales

### Datos Abiertos Colombia
- Consultas SODA/SoQL con manejo de límites de tasa
- Cache local y snapshots con metadatos
- Reintentos automáticos y tolerancia a fallos

### IDEAM/DHIME
- Descarga de series hidrometeorológicas
- Filtros por estación, variable y período
- Almacenamiento local para reproducibilidad

### SIAC/MinAmbiente
- Consulta de recursos hídricos
- Calidad del agua y contexto ambiental
- Logging de consultas para auditoría

## 🤖 Modelos de IA y Orquestación

### DeepSeek-R1 (Razonamiento Técnico)
- Planificación de trenes de tratamiento
- Auditoría de cadenas de razonamiento
- Decisiones técnicas complejas

### Qwen2.5-Math (Cálculo Matemático)
- Resolución de problemas matemáticos
- Derivación y estructuración de fórmulas
- Verificación cruzada con SymPy

### Mistral-7B-Instruct (Redacción Técnica)
- Memorias de cálculo en español
- Marco normativo y resúmenes ejecutivos
- Ayuda contextual en interfaz

### Política de Exactitud
⚠️ **CRÍTICO**: Ningún resultado numérico proviene directamente de LLMs.
- Todos los cálculos ejecutados con SymPy/SciPy/Pint
- Trazabilidad de expresiones, entradas y resultados
- Unidades consistentes y verificadas

## 📊 Generación de Reportes

### PDF Profesional (ReportLab)
- Portada e índice automático
- Tablas con unidades y figuras
- Anexo de validación normativa por unidad
- Anexos CAD y registro de datasets
- Citas normativas automáticas

### Excel (openpyxl/xlsxwriter)
- Cálculos detallados paso a paso
- Tablas de resultados
- Gráficos de análisis

### DXF (ezdxf)
- Vistas por unidad de tratamiento
- Layout general con capas
- Bloques reutilizables
- Compatible con AutoCAD/CAD estándar

## 🧪 Pruebas y Validación

```bash
# Ejecutar pruebas unitarias
pytest tests/unit/

# Ejecutar pruebas de integración
pytest tests/integration/

# Ejecutar todas las pruebas con cobertura
pytest --cov=. tests/
```

### Casos de Prueba
- ✅ Procesos unitarios con casos límite
- ✅ Validadores RAS/2115/1575
- ✅ Conectores con mocks y tolerancia a fallos
- ✅ Integración end-to-end de flujos completos

## 📖 Uso Básico

```python
from ptap_design_system import PTAPDesigner

# Crear diseñador con parámetros de agua cruda
designer = PTAPDesigner(
    caudal=50,  # L/s
    turbidez=20,  # NTU
    color=30,  # UPC
    ph=7.2
)

# Seleccionar tren de tratamiento
designer.select_treatment_train([
    'aireacion',
    'mezcla_rapida',
    'floculacion',
    'sedimentacion',
    'filtracion',
    'desinfeccion'
])

# Dimensionar procesos
results = designer.design()

# Validar contra normativa
compliance = designer.validate_compliance()

# Generar reportes
designer.export_pdf('diseño_ptap.pdf')
designer.export_excel('calculos_ptap.xlsx')
designer.export_dxf('planos_ptap.dxf')
```

## 🔧 Configuración Avanzada

### Ajuste de Modelos IA

```yaml
# config/config.yaml
ai_models:
  reasoning:
    model: "deepseek-r1:14b"
    temperature: 0.1
  math:
    model: "qwen2.5-math:7b"
    temperature: 0.0
  writing:
    model: "mistral:7b-instruct-v0.3"
    temperature: 0.3
    language: "es"
```

### Configuración de Conectores

```yaml
data_sources:
  datos_abiertos:
    base_url: "https://www.datos.gov.co"
    rate_limit: 1000  # requests/hour
    cache_ttl: 86400  # seconds
  ideam:
    base_url: "http://dhime.ideam.gov.co"
    timeout: 30
```

## 📚 Documentación

- [Manual de Usuario](docs/manual_usuario.md)
- [Guía de Instalación](docs/instalacion.md)
- [Documentación API](docs/api.md)
- [Ejemplos de Uso](examples/)
- [Referencias Normativas](docs/normativa.md)

## 🤝 Contribución

Este proyecto está diseñado para cumplir estrictamente con la normativa colombiana.
Cualquier contribución debe:
- Incluir pruebas unitarias
- Verificar cálculos con SymPy/SciPy
- Referenciar artículos normativos aplicables
- Mantener trazabilidad completa

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- MinVivienda y CRA por normativa técnica (RAS 2017)
- IDEAM por datos hidrometeorológicos
- Datos Abiertos Colombia por infraestructura de datos
- Comunidad open source de Ollama, SymPy, ReportLab y ezdxf

## 📞 Soporte

Para preguntas técnicas o reporte de problemas:
- Abrir un issue en GitHub
- Consultar documentación en `/docs`
- Revisar ejemplos en `/examples`

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Cumplimiento normativo**: RAS 2017, Res. 2115/2007, Dec. 1575/2007
