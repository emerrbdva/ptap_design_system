"""
Sistema Integral de Diseño de Plantas de Potabilización de Agua (PTAP)

Este paquete proporciona herramientas completas para el diseño, simulación,
validación normativa y documentación de plantas de potabilización de agua
adaptadas al contexto colombiano.

Módulos principales:
- core: Cálculos y simulación hidráulica
- compliance: Validación normativa (RAS 2017, Res. 2115, Dec. 1575)
- data_connectors: Conexión a portales gubernamentales
- ai: Orquestación de modelos de IA local
- reporting: Generación de documentos técnicos
- cad: Exportación de planos DXF
- utils: Utilidades del sistema

Versión: 1.0.0
Licencia: MIT
"""

__version__ = "1.0.0"
__author__ = "Equipo PTAP"
__license__ = "MIT"

# Importaciones opcionales para facilitar el uso del paquete
try:
    from .core.calculations import TreatmentCalculator
    from .core.hydraulics import HydraulicSimulator
    _has_core = True
except ImportError:
    _has_core = False

try:
    from .compliance.ras_2017 import RAS2017Validator
    from .compliance.res_2115 import Resolucion2115Validator
    _has_compliance = True
except ImportError:
    _has_compliance = False

__all__ = [
    "__version__",
]

if _has_core:
    __all__.extend(["TreatmentCalculator", "HydraulicSimulator"])
if _has_compliance:
    __all__.extend(["RAS2017Validator", "Resolucion2115Validator"])
