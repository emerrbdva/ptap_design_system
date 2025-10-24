"""Módulo Reporting - Generación de Documentos"""

from .pdf_generator import PTAPPDFGenerator, generate_complete_report

__all__ = [
    "PTAPPDFGenerator",
    "generate_complete_report",
]
