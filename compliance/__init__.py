"""Módulo Compliance - Validadores Normativos"""

from .ras_2017 import RAS2017Validator, ComplianceRule, ComplianceResult, ComplianceStatus
from .res_2115 import Resolucion2115Validator, WaterQualityStandard

__all__ = [
    "RAS2017Validator",
    "Resolucion2115Validator",
    "ComplianceRule",
    "ComplianceResult",
    "ComplianceStatus",
    "WaterQualityStandard",
]
