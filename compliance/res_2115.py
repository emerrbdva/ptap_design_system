"""
Módulo Compliance: Validación Resolución 2115 de 2007

Validación de calidad del agua para consumo humano según
Resolución 2115 de 2007 del Ministerio de la Protección Social y MinAmbiente.

Incluye:
- Características físicas (color, turbiedad, pH, conductividad)
- Características químicas (nitratos, fluoruros, metales pesados, etc.)
- Características microbiológicas (coliformes, E. coli)
- Límites máximos permisibles (LMP)
- Frecuencias de muestreo según tipo de sistema

Fuente normativa:
https://minvivienda.gov.co/sites/default/files/normativa/2115%20-%202007.pdf
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ParameterCategory(Enum):
    """Categorías de parámetros de calidad"""
    FISICO = "físico"
    QUIMICO = "químico"
    MICROBIOLOGICO = "microbiológico"


@dataclass
class WaterQualityStandard:
    """Estándar de calidad del agua"""
    parameter: str
    category: ParameterCategory
    max_value: Optional[float]
    min_value: Optional[float]
    units: str
    article: str
    description: str
    
    def validate(self, value: float) -> tuple[bool, str]:
        """Validar valor contra estándar"""
        if self.max_value is not None and value > self.max_value:
            return False, f"{self.parameter} = {value} {self.units} excede LMP de {self.max_value} {self.units}"
        
        if self.min_value is not None and value < self.min_value:
            return False, f"{self.parameter} = {value} {self.units} por debajo del mínimo de {self.min_value} {self.units}"
        
        return True, f"{self.parameter} cumple Res. 2115/2007"


class Resolucion2115Validator:
    """
    Validador de calidad del agua según Resolución 2115 de 2007.
    
    Implementa los límites máximos permisibles (LMP) para características
    físicas, químicas y microbiológicas del agua para consumo humano.
    """
    
    def __init__(self):
        """Inicializar validador con estándares Res. 2115/2007"""
        self.standards: Dict[str, WaterQualityStandard] = {}
        self._load_physical_standards()
        self._load_chemical_standards()
        self._load_microbiological_standards()
        
        logger.info("Resolucion2115Validator inicializado")
    
    def _load_physical_standards(self):
        """Cargar estándares físicos - Artículo 2"""
        standards = [
            WaterQualityStandard(
                parameter="color",
                category=ParameterCategory.FISICO,
                max_value=15.0,
                min_value=None,
                units="UPC",
                article="Artículo 2",
                description="Color aparente"
            ),
            WaterQualityStandard(
                parameter="turbiedad",
                category=ParameterCategory.FISICO,
                max_value=2.0,
                min_value=None,
                units="NTU",
                article="Artículo 2",
                description="Turbiedad"
            ),
            WaterQualityStandard(
                parameter="ph",
                category=ParameterCategory.FISICO,
                max_value=9.0,
                min_value=6.5,
                units="unidades",
                article="Artículo 2",
                description="pH"
            ),
            WaterQualityStandard(
                parameter="conductividad",
                category=ParameterCategory.FISICO,
                max_value=1000.0,
                min_value=None,
                units="μS/cm",
                article="Artículo 2",
                description="Conductividad"
            ),
        ]
        
        for std in standards:
            self.standards[std.parameter] = std
    
    def _load_chemical_standards(self):
        """Cargar estándares químicos - Artículos 3, 4, 5"""
        standards = [
            # Elementos/sustancias tóxicas - Artículo 3
            WaterQualityStandard(
                parameter="arsenico",
                category=ParameterCategory.QUIMICO,
                max_value=0.01,
                min_value=None,
                units="mg/L",
                article="Artículo 3",
                description="Arsénico"
            ),
            WaterQualityStandard(
                parameter="cadmio",
                category=ParameterCategory.QUIMICO,
                max_value=0.003,
                min_value=None,
                units="mg/L",
                article="Artículo 3",
                description="Cadmio"
            ),
            WaterQualityStandard(
                parameter="cromo",
                category=ParameterCategory.QUIMICO,
                max_value=0.05,
                min_value=None,
                units="mg/L",
                article="Artículo 3",
                description="Cromo hexavalente"
            ),
            WaterQualityStandard(
                parameter="mercurio",
                category=ParameterCategory.QUIMICO,
                max_value=0.001,
                min_value=None,
                units="mg/L",
                article="Artículo 3",
                description="Mercurio"
            ),
            WaterQualityStandard(
                parameter="plomo",
                category=ParameterCategory.QUIMICO,
                max_value=0.01,
                min_value=None,
                units="mg/L",
                article="Artículo 3",
                description="Plomo"
            ),
            # Elementos/compuestos con efectos - Artículo 4
            WaterQualityStandard(
                parameter="nitratos",
                category=ParameterCategory.QUIMICO,
                max_value=10.0,
                min_value=None,
                units="mg/L NO₃",
                article="Artículo 4",
                description="Nitratos"
            ),
            WaterQualityStandard(
                parameter="nitritos",
                category=ParameterCategory.QUIMICO,
                max_value=0.1,
                min_value=None,
                units="mg/L NO₂",
                article="Artículo 4",
                description="Nitritos"
            ),
            WaterQualityStandard(
                parameter="fluoruros",
                category=ParameterCategory.QUIMICO,
                max_value=1.0,
                min_value=None,
                units="mg/L F⁻",
                article="Artículo 4",
                description="Fluoruros"
            ),
            # Desinfección - Artículo 5
            WaterQualityStandard(
                parameter="cloro_residual_libre",
                category=ParameterCategory.QUIMICO,
                max_value=2.0,
                min_value=0.3,
                units="mg/L Cl₂",
                article="Artículo 5",
                description="Cloro residual libre"
            ),
        ]
        
        for std in standards:
            self.standards[std.parameter] = std
    
    def _load_microbiological_standards(self):
        """Cargar estándares microbiológicos - Artículo 6"""
        standards = [
            WaterQualityStandard(
                parameter="coliformes_totales",
                category=ParameterCategory.MICROBIOLOGICO,
                max_value=0.0,
                min_value=None,
                units="UFC/100mL",
                article="Artículo 6",
                description="Coliformes totales"
            ),
            WaterQualityStandard(
                parameter="escherichia_coli",
                category=ParameterCategory.MICROBIOLOGICO,
                max_value=0.0,
                min_value=None,
                units="UFC/100mL",
                article="Artículo 6",
                description="Escherichia coli"
            ),
        ]
        
        for std in standards:
            self.standards[std.parameter] = std
    
    def validate_parameter(
        self,
        parameter: str,
        value: float
    ) -> Dict[str, any]:
        """
        Validar un parámetro de calidad.
        
        Args:
            parameter: Nombre del parámetro
            value: Valor medido
            
        Returns:
            Dict con resultado de validación
        """
        if parameter not in self.standards:
            logger.warning(f"Parámetro '{parameter}' no definido en Res. 2115/2007")
            return {
                "parameter": parameter,
                "value": value,
                "compliant": None,
                "message": "Parámetro no regulado por Res. 2115/2007"
            }
        
        std = self.standards[parameter]
        compliant, message = std.validate(value)
        
        result = {
            "parameter": parameter,
            "value": value,
            "units": std.units,
            "lmp": std.max_value,
            "compliant": compliant,
            "message": message,
            "category": std.category.value,
            "article": std.article,
            "timestamp": datetime.now().isoformat()
        }
        
        if not compliant:
            logger.error(f"[Calidad Agua] {message}")
        else:
            logger.info(f"[Calidad Agua] {message}")
        
        return result
    
    def validate_water_quality(
        self,
        measurements: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Validar conjunto completo de parámetros.
        
        Args:
            measurements: Dict con parámetros y valores medidos
            
        Returns:
            Dict con resultados y resumen
        """
        results = []
        
        for parameter, value in measurements.items():
            result = self.validate_parameter(parameter, value)
            results.append(result)
        
        # Resumen
        total = len(results)
        compliant = sum(1 for r in results if r["compliant"] is True)
        non_compliant = sum(1 for r in results if r["compliant"] is False)
        
        summary = {
            "results": results,
            "summary": {
                "total_parametros": total,
                "conformes": compliant,
                "no_conformes": non_compliant,
                "apto_consumo": non_compliant == 0
            },
            "normativa": "Resolución 2115 de 2007",
            "fecha_validacion": datetime.now().isoformat()
        }
        
        logger.info(f"Validación calidad: {compliant}/{total} parámetros conformes")
        return summary
    
    def get_sampling_frequency(
        self,
        poblacion: int,
        parameter_category: str
    ) -> str:
        """
        Determinar frecuencia de muestreo según población.
        
        Basado en Artículo 13 - Frecuencias de análisis
        
        Args:
            poblacion: Población servida
            parameter_category: 'fisico', 'quimico', 'microbiologico'
            
        Returns:
            Descripción de frecuencia
        """
        # Simplificación de frecuencias (consultar tabla completa en Res. 2115)
        if parameter_category == "microbiologico":
            if poblacion < 2500:
                return "Mensual"
            elif poblacion < 50000:
                return "Semanal"
            else:
                return "Diaria"
        
        elif parameter_category == "fisico":
            if poblacion < 2500:
                return "Mensual"
            elif poblacion < 50000:
                return "Quincenal"
            else:
                return "Diaria"
        
        elif parameter_category == "quimico":
            if poblacion < 2500:
                return "Semestral"
            elif poblacion < 50000:
                return "Trimestral"
            else:
                return "Mensual"
        
        return "Consultar Artículo 13 Res. 2115/2007"
