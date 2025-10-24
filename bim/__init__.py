"""
Módulo de exportación BIM (Building Information Modeling) en formato IFC.

Este módulo permite exportar diseños de PTAP a formato IFC (Industry Foundation Classes),
compatible con Revit, ArchiCAD, Navisworks y otros software BIM.
"""

from .ifc_exporter import ExportadorBIM, ComponenteBIM

__all__ = ['ExportadorBIM', 'ComponenteBIM']

__version__ = "1.0.0"
