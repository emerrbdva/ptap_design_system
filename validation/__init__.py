"""
Módulo de validación con Pydantic
"""
from .schemas import (
    ParametrosAguaCruda,
    ParametrosProyecto,
    DiseñoMezclaRapida,
    DiseñoFloculacion,
    DiseñoSedimentacion,
    DiseñoFiltracion,
    DiseñoDesinfeccion,
    DiseñoCompleto
)

__all__ = [
    'ParametrosAguaCruda',
    'ParametrosProyecto',
    'DiseñoMezclaRapida',
    'DiseñoFloculacion',
    'DiseñoSedimentacion',
    'DiseñoFiltracion',
    'DiseñoDesinfeccion',
    'DiseñoCompleto'
]
