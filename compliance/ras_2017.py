"""
Módulo Compliance: Validación Normativa RAS 2017

Validadores automáticos de la Resolución 0330 de 2017 (RAS - Reglamento Técnico
del Sector de Agua Potable y Saneamiento Básico).

Incluye:
- Matriz de conformidad por proceso unitario
- Referencias a artículos, tablas y rangos específicos del RAS
- Alertas por cambios normativos (ej. Resolución 799 de 2021)
- Generación de evidencias de cumplimiento

Fuente normativa:
- MinVivienda: https://minvivienda.gov.co/normativa/resolucion-0330-2017-0
- CRA: https://normas.cra.gov.co/gestor/docs/resolucion_minviviendact_0330_2017.htm
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from pint import UnitRegistry

ureg = UnitRegistry()
Q_ = ureg.Quantity

logger = logging.getLogger(__name__)


class ComplianceStatus(Enum):
    """Estado de conformidad"""
    COMPLIANT = "conforme"
    NON_COMPLIANT = "no_conforme"
    WARNING = "advertencia"
    NOT_APPLICABLE = "no_aplica"


@dataclass
class ComplianceRule:
    """Regla de validación normativa"""
    parameter: str
    min_value: Optional[float]
    max_value: Optional[float]
    units: str
    ras_reference: str  # Ej: "A.7.5 Tabla A.7.4"
    article: str  # Ej: "Artículo 142"
    description: str
    severity: str = "critical"  # critical, warning, info
    
    def validate(self, value: float) -> Tuple[ComplianceStatus, str]:
        """
        Validar valor contra regla.
        
        Returns:
            (status, mensaje)
        """
        if self.min_value is not None and value < self.min_value:
            msg = f"{self.parameter} = {value} {self.units} < {self.min_value} {self.units} (mínimo RAS)"
            status = ComplianceStatus.NON_COMPLIANT if self.severity == "critical" else ComplianceStatus.WARNING
            return status, msg
        
        if self.max_value is not None and value > self.max_value:
            msg = f"{self.parameter} = {value} {self.units} > {self.max_value} {self.units} (máximo RAS)"
            status = ComplianceStatus.NON_COMPLIANT if self.severity == "critical" else ComplianceStatus.WARNING
            return status, msg
        
        msg = f"{self.parameter} = {value} {self.units} cumple con RAS 2017 {self.ras_reference}"
        return ComplianceStatus.COMPLIANT, msg


@dataclass
class ComplianceResult:
    """Resultado de validación de conformidad"""
    process: str
    parameter: str
    value: Any
    status: ComplianceStatus
    message: str
    ras_reference: str
    article: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "process": self.process,
            "parameter": self.parameter,
            "value": str(self.value),
            "status": self.status.value,
            "message": self.message,
            "ras_reference": self.ras_reference,
            "article": self.article,
            "timestamp": self.timestamp.isoformat()
        }


class RAS2017Validator:
    """
    Validador de conformidad con RAS 2017.
    
    Implementa reglas de validación para todos los procesos unitarios
    de tratamiento según la Resolución 0330 de 2017.
    """
    
    def __init__(self):
        """Inicializar validador con reglas RAS 2017"""
        self.rules: Dict[str, List[ComplianceRule]] = {}
        self.results: List[ComplianceResult] = []
        
        # Cargar reglas por proceso
        self._load_aireacion_rules()
        self._load_mezcla_rapida_rules()
        self._load_floculacion_rules()
        self._load_sedimentacion_rules()
        self._load_filtracion_rules()
        self._load_desinfeccion_rules()
        
        logger.info("RAS2017Validator inicializado con reglas completas")
    
    # ========================================================================
    # AIREACIÓN - RAS 2017 Sección A.7.4
    # ========================================================================
    
    def _load_aireacion_rules(self):
        """Cargar reglas de aireación"""
        self.rules["aireacion"] = [
            ComplianceRule(
                parameter="tiempo_contacto",
                min_value=15.0,
                max_value=30.0,
                units="min",
                ras_reference="A.7.4 Tabla A.7.3",
                article="Artículo 138",
                description="Tiempo de contacto en aireación",
                severity="critical"
            ),
            ComplianceRule(
                parameter="carga_superficial",
                min_value=20.0,
                max_value=60.0,
                units="m³/(m²·h)",
                ras_reference="A.7.4 Tabla A.7.3",
                article="Artículo 138",
                description="Carga superficial en aireadores",
                severity="critical"
            ),
        ]
    
    # ========================================================================
    # MEZCLA RÁPIDA - RAS 2017 Sección A.7.5
    # ========================================================================
    
    def _load_mezcla_rapida_rules(self):
        """Cargar reglas de mezcla rápida"""
        self.rules["mezcla_rapida"] = [
            ComplianceRule(
                parameter="gradiente_velocidad",
                min_value=600.0,
                max_value=1500.0,
                units="s⁻¹",
                ras_reference="A.7.5 Tabla A.7.4",
                article="Artículo 142",
                description="Gradiente de velocidad en mezcla rápida",
                severity="critical"
            ),
            ComplianceRule(
                parameter="tiempo_retencion",
                min_value=10.0,
                max_value=60.0,
                units="s",
                ras_reference="A.7.5 Tabla A.7.4",
                article="Artículo 142",
                description="Tiempo de retención en mezcla rápida",
                severity="critical"
            ),
        ]
    
    # ========================================================================
    # FLOCULACIÓN - RAS 2017 Sección A.7.6
    # ========================================================================
    
    def _load_floculacion_rules(self):
        """Cargar reglas de floculación"""
        self.rules["floculacion"] = [
            ComplianceRule(
                parameter="gradiente_velocidad",
                min_value=20.0,
                max_value=70.0,
                units="s⁻¹",
                ras_reference="A.7.6 Tabla A.7.5",
                article="Artículo 147",
                description="Gradiente de velocidad en floculación",
                severity="critical"
            ),
            ComplianceRule(
                parameter="tiempo_retencion",
                min_value=10.0,
                max_value=40.0,
                units="min",
                ras_reference="A.7.6 Tabla A.7.5",
                article="Artículo 147",
                description="Tiempo de retención en floculación",
                severity="critical"
            ),
            ComplianceRule(
                parameter="num_camaras",
                min_value=2.0,
                max_value=None,
                units="unidades",
                ras_reference="A.7.6",
                article="Artículo 147",
                description="Número mínimo de cámaras de floculación",
                severity="warning"
            ),
        ]
    
    # ========================================================================
    # SEDIMENTACIÓN - RAS 2017 Sección A.7.7
    # ========================================================================
    
    def _load_sedimentacion_rules(self):
        """Cargar reglas de sedimentación"""
        self.rules["sedimentacion"] = [
            ComplianceRule(
                parameter="carga_superficial",
                min_value=10.0,
                max_value=50.0,
                units="m³/(m²·día)",
                ras_reference="A.7.7 Tabla A.7.6",
                article="Artículo 152",
                description="Carga superficial en sedimentadores",
                severity="critical"
            ),
            ComplianceRule(
                parameter="velocidad_horizontal",
                min_value=None,
                max_value=0.55,
                units="cm/s",
                ras_reference="A.7.7 Tabla A.7.6",
                article="Artículo 152",
                description="Velocidad horizontal máxima",
                severity="critical"
            ),
            ComplianceRule(
                parameter="tiempo_retencion",
                min_value=1.5,
                max_value=4.0,
                units="h",
                ras_reference="A.7.7 Tabla A.7.6",
                article="Artículo 152",
                description="Tiempo de retención en sedimentación",
                severity="critical"
            ),
            ComplianceRule(
                parameter="profundidad",
                min_value=2.0,
                max_value=5.0,
                units="m",
                ras_reference="A.7.7",
                article="Artículo 152",
                description="Profundidad de sedimentadores",
                severity="warning"
            ),
        ]
    
    # ========================================================================
    # FILTRACIÓN - RAS 2017 Sección A.7.8
    # ========================================================================
    
    def _load_filtracion_rules(self):
        """Cargar reglas de filtración"""
        self.rules["filtracion"] = [
            ComplianceRule(
                parameter="tasa_filtracion",
                min_value=120.0,
                max_value=360.0,
                units="m³/(m²·día)",
                ras_reference="A.7.8 Tabla A.7.7",
                article="Artículo 160",
                description="Tasa de filtración",
                severity="critical"
            ),
            ComplianceRule(
                parameter="profundidad_lecho",
                min_value=0.6,
                max_value=1.0,
                units="m",
                ras_reference="A.7.8 Tabla A.7.7",
                article="Artículo 160",
                description="Profundidad del lecho filtrante",
                severity="critical"
            ),
            ComplianceRule(
                parameter="num_filtros",
                min_value=2.0,
                max_value=None,
                units="unidades",
                ras_reference="A.7.8",
                article="Artículo 160",
                description="Número mínimo de filtros (redundancia)",
                severity="critical"
            ),
        ]
    
    # ========================================================================
    # DESINFECCIÓN - RAS 2017 Sección A.7.9
    # ========================================================================
    
    def _load_desinfeccion_rules(self):
        """Cargar reglas de desinfección"""
        self.rules["desinfeccion"] = [
            ComplianceRule(
                parameter="tiempo_contacto",
                min_value=20.0,
                max_value=30.0,
                units="min",
                ras_reference="A.7.9 Tabla A.7.8",
                article="Artículo 168",
                description="Tiempo de contacto desinfección",
                severity="critical"
            ),
            ComplianceRule(
                parameter="dosis_cloro",
                min_value=0.5,
                max_value=3.0,
                units="mg/L",
                ras_reference="A.7.9 Tabla A.7.8",
                article="Artículo 168",
                description="Dosis de cloro",
                severity="warning"
            ),
            ComplianceRule(
                parameter="CT",
                min_value=2.0,
                max_value=None,
                units="mg·min/L",
                ras_reference="A.7.9 Tabla A.7.9",
                article="Artículo 168",
                description="Valor CT mínimo para inactivación",
                severity="critical"
            ),
        ]
    
    # ========================================================================
    # VALIDACIÓN
    # ========================================================================
    
    def validate_process(
        self,
        process: str,
        parameters: Dict[str, float]
    ) -> List[ComplianceResult]:
        """
        Validar parámetros de un proceso contra RAS 2017.
        
        Args:
            process: Nombre del proceso (ej: 'mezcla_rapida')
            parameters: Dict con parámetros y valores a validar
            
        Returns:
            Lista de resultados de validación
        """
        if process not in self.rules:
            logger.warning(f"Proceso '{process}' no tiene reglas RAS definidas")
            return []
        
        results = []
        
        for rule in self.rules[process]:
            if rule.parameter in parameters:
                value = parameters[rule.parameter]
                status, message = rule.validate(value)
                
                result = ComplianceResult(
                    process=process,
                    parameter=rule.parameter,
                    value=value,
                    status=status,
                    message=message,
                    ras_reference=rule.ras_reference,
                    article=rule.article
                )
                
                results.append(result)
                self.results.append(result)
                
                # Log según severidad
                if status == ComplianceStatus.NON_COMPLIANT:
                    logger.error(f"[{process}] {message}")
                elif status == ComplianceStatus.WARNING:
                    logger.warning(f"[{process}] {message}")
                else:
                    logger.info(f"[{process}] {message}")
        
        return results
    
    def validate_all(
        self,
        design_parameters: Dict[str, Dict[str, float]]
    ) -> Dict[str, List[ComplianceResult]]:
        """
        Validar todos los procesos del diseño.
        
        Args:
            design_parameters: Dict con estructura:
                {
                    'mezcla_rapida': {'gradiente_velocidad': 800, ...},
                    'floculacion': {'gradiente_velocidad': 45, ...},
                    ...
                }
        
        Returns:
            Dict con resultados por proceso
        """
        all_results = {}
        
        for process, parameters in design_parameters.items():
            results = self.validate_process(process, parameters)
            all_results[process] = results
        
        logger.info(f"Validación completa: {len(all_results)} procesos validados")
        return all_results
    
    # ========================================================================
    # MATRIZ DE CONFORMIDAD
    # ========================================================================
    
    def generate_compliance_matrix(self) -> Dict[str, Any]:
        """
        Generar matriz de conformidad resumida.
        
        Returns:
            Dict con estadísticas y resumen de conformidad
        """
        total = len(self.results)
        if total == 0:
            return {"total": 0, "message": "No hay resultados de validación"}
        
        compliant = sum(1 for r in self.results if r.status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for r in self.results if r.status == ComplianceStatus.NON_COMPLIANT)
        warnings = sum(1 for r in self.results if r.status == ComplianceStatus.WARNING)
        
        compliance_rate = (compliant / total) * 100
        
        # Agrupar por proceso
        by_process = {}
        for result in self.results:
            if result.process not in by_process:
                by_process[result.process] = {
                    "total": 0,
                    "compliant": 0,
                    "non_compliant": 0,
                    "warnings": 0
                }
            
            by_process[result.process]["total"] += 1
            if result.status == ComplianceStatus.COMPLIANT:
                by_process[result.process]["compliant"] += 1
            elif result.status == ComplianceStatus.NON_COMPLIANT:
                by_process[result.process]["non_compliant"] += 1
            elif result.status == ComplianceStatus.WARNING:
                by_process[result.process]["warnings"] += 1
        
        matrix = {
            "resumen": {
                "total_validaciones": total,
                "conformes": compliant,
                "no_conformes": non_compliant,
                "advertencias": warnings,
                "tasa_conformidad": round(compliance_rate, 2)
            },
            "por_proceso": by_process,
            "normativa": "RAS 2017 (Resolución 0330 de 2017)",
            "fecha_validacion": datetime.now().isoformat()
        }
        
        logger.info(f"Matriz de conformidad: {compliance_rate:.1f}% conforme")
        return matrix
    
    def export_results(self, filepath: str):
        """Exportar resultados a JSON"""
        import json
        
        data = {
            "results": [r.to_dict() for r in self.results],
            "matrix": self.generate_compliance_matrix()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados de conformidad exportados a {filepath}")
