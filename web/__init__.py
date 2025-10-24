"""
API Web para diseño de PTAP usando FastAPI.

Este módulo proporciona una interfaz REST API y frontend web
para diseñar plantas de tratamiento de agua potable.
"""

from .api import app

__all__ = ['app']

__version__ = "1.0.0"
