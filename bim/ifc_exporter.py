"""
Exportador de modelos BIM en formato IFC para diseños de PTAP.

Este módulo utiliza ifcopenshell (gratuito) para generar modelos 3D
en formato IFC 4 (ISO 16739:2018), compatible con:
- Autodesk Revit
- ArchiCAD
- Bentley MicroStation
- Navisworks
- Solibri
- Y cualquier software compatible con IFC

El modelo BIM incluye:
- Geometría 3D de componentes
- Propiedades técnicas (caudales, dimensiones, materiales)
- Relaciones espaciales
- Clasificación por sistemas (hidráulico, estructural, etc.)
"""

import ifcopenshell
from ifcopenshell import file as ifc_file
import ifcopenshell.api
import ifcopenshell.guid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
import time


@dataclass
class ComponenteBIM:
    """
    Representa un componente individual de la PTAP en el modelo BIM.
    """
    nombre: str
    tipo: str  # 'sedimentador', 'filtro', 'tanque', 'tuberia', etc.
    largo: float  # metros
    ancho: float  # metros
    alto: float  # metros
    posicion_x: float  # metros
    posicion_y: float  # metros
    posicion_z: float  # metros (elevación)
    propiedades: Dict[str, any]  # Propiedades adicionales
    material: str = 'Concreto'
    color: Optional[Tuple[float, float, float]] = None  # RGB 0-1


class ExportadorBIM:
    """
    Exportador de diseños PTAP a formato IFC.
    
    Ejemplo de uso:
    ```python
    exporter = ExportadorBIM(
        nombre_proyecto="PTAP San José",
        ubicacion=(4.5, -73.2, 250)  # lat, lon, elevación
    )
    
    # Agregar sedimentador
    exporter.agregar_sedimentador(
        largo=10, ancho=8, alto=4,
        x=0, y=0, z=0,
        carga_superficial=25,
        tiempo_retencion=10800
    )
    
    # Exportar
    exporter.exportar("PTAP_50Ls.ifc")
    ```
    """
    
    def __init__(
        self,
        nombre_proyecto: str = "PTAP",
        ubicacion: Optional[Tuple[float, float, float]] = None,
        autor: str = "PTAP Design System v2.0.0"
    ):
        """
        Args:
            nombre_proyecto: Nombre del proyecto
            ubicacion: Tupla (latitud, longitud, elevación en metros)
            autor: Autor del modelo
        """
        # Crear archivo IFC básico (sin schema específico debido a problemas en Windows)
        self.ifc = ifcopenshell.file()
        
        # Crear elementos básicos del proyecto manualmente
        # Timestamp
        timestamp = int(time.time())
        
        # Crear persona y organización
        org = self.ifc.createIfcOrganization(
            Name="PTAP Design System"
        )
        
        person = self.ifc.createIfcPerson(
            GivenName=autor if autor else "Usuario"
        )
        
        person_org = self.ifc.createIfcPersonAndOrganization(person, org)
        
        # Crear aplicación
        app = self.ifc.createIfcApplication(
            org,
            "2.0.0",
            "PTAP Design System",
            "ptap_design"
        )
        
        # Crear unidades
        dimensions = self.ifc.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
        unit_length = self.ifc.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        unit_area = self.ifc.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE")
        unit_volume = self.ifc.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE")
        units = self.ifc.createIfcUnitAssignment([unit_length, unit_area, unit_volume])
        
        # Crear contexto geométrico 3D
        self.context_3d = self.ifc.createIfcGeometricRepresentationContext(
            None, "Model", 3, 1.0E-5,
            self.ifc.createIfcAxis2Placement3D(
                self.ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))
            ),
            None
        )
        
        # Subcontexto Body
        self.body_context = self.ifc.createIfcGeometricRepresentationSubContext(
            "Body", "Model", None, None, None, None,
            self.context_3d, None, "MODEL_VIEW", None
        )
        
        # Crear proyecto
        self.proyecto = self.ifc.createIfcProject(
            ifcopenshell.guid.new(),
            None,
            nombre_proyecto,
            "Planta de Tratamiento de Agua Potable",
            None, None, None,
            [self.context_3d],
            units
        )
        
        # Crear sitio
        self.sitio = self.ifc.createIfcSite(
            ifcopenshell.guid.new(),
            None,
            "Sitio PTAP",
            None,
            None,
            self.ifc.createIfcLocalPlacement(
                None,
                self.ifc.createIfcAxis2Placement3D(
                    self.ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))
                )
            ),
            None,
            "ELEMENT",
            None, None, None, None, None
        )
        
        # Crear edificio
        self.edificio = self.ifc.createIfcBuilding(
            ifcopenshell.guid.new(),
            None,
            "PTAP",
            None,
            None,
            self.ifc.createIfcLocalPlacement(
                None,
                self.ifc.createIfcAxis2Placement3D(
                    self.ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))
                )
            ),
            None,
            "ELEMENT",
            None, None, None
        )
        
        # Relacionar proyecto -> sitio -> edificio
        self.ifc.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            None, None, None,
            self.proyecto,
            [self.sitio]
        )
        
        self.ifc.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            None, None, None,
            self.sitio,
            [self.edificio]
        )
        
        # Lista para almacenar elementos
        self.elementos = []
        
        # Ubicación (si se proporciona)
        if ubicacion:
            lat, lon, elev = ubicacion
            self.ubicacion = ubicacion
            # Configurar geolocalización en el sitio
            self.sitio.RefLatitude = self._decimal_to_dms(lat)
            self.sitio.RefLongitude = self._decimal_to_dms(lon)
            self.sitio.RefElevation = float(elev)
    
    def _decimal_to_dms(self, decimal: float) -> Tuple[int, int, int, int]:
        """Convierte grados decimales a grados, minutos, segundos"""
        degrees = int(decimal)
        minutes_decimal = abs(decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = int((minutes_decimal - minutes) * 60)
        microseconds = int(((minutes_decimal - minutes) * 60 - seconds) * 1000000)
        
        return (degrees, minutes, seconds, microseconds)
    
    def _crear_caja(
        self,
        largo: float,
        ancho: float,
        alto: float
    ):
        """Crea una geometría de caja (paralelepípedo)"""
        # Crear perfil rectangular
        perfil = self.ifc.createIfcRectangleProfileDef(
            ProfileType="AREA",
            ProfileName="Rectangular",
            XDim=largo,
            YDim=ancho
        )
        
        # Crear dirección de extrusión (eje Z)
        direction = self.ifc.createIfcDirection((0.0, 0.0, 1.0))
        
        # Crear geometría extruida
        geometria = self.ifc.createIfcExtrudedAreaSolid(
            SweptArea=perfil,
            ExtrudedDirection=direction,
            Depth=alto
        )
        
        return geometria
    
    def _crear_representacion(
        self,
        geometria,
        nombre: str = "Body"
    ):
        """Crea representación 3D para un elemento"""
        representacion = self.ifc.createIfcShapeRepresentation(
            ContextOfItems=self.body_context,
            RepresentationIdentifier="Body",
            RepresentationType="SweptSolid",
            Items=[geometria]
        )
        
        return representacion
    
    def _posicionar_elemento(
        self,
        elemento,
        x: float,
        y: float,
        z: float
    ):
        """Posiciona un elemento en coordenadas X, Y, Z"""
        punto = self.ifc.createIfcCartesianPoint((x, y, z))
        placement = self.ifc.createIfcLocalPlacement(
            RelativePlacement=self.ifc.createIfcAxis2Placement3D(
                Location=punto
            )
        )
        
        elemento.ObjectPlacement = placement
        
        return elemento
    
    def _agregar_propiedades(
        self,
        elemento,
        nombre_pset: str,
        propiedades: Dict[str, any]
    ):
        """Agrega property set a un elemento"""
        props = []
        
        for nombre, valor in propiedades.items():
            if isinstance(valor, (int, float)):
                prop = self.ifc.createIfcPropertySingleValue(
                    Name=nombre,
                    NominalValue=self.ifc.createIfcReal(float(valor))
                )
            elif isinstance(valor, str):
                prop = self.ifc.createIfcPropertySingleValue(
                    Name=nombre,
                    NominalValue=self.ifc.createIfcText(valor)
                )
            elif isinstance(valor, bool):
                prop = self.ifc.createIfcPropertySingleValue(
                    Name=nombre,
                    NominalValue=self.ifc.createIfcBoolean(valor)
                )
            else:
                continue
            
            props.append(prop)
        
        pset = self.ifc.createIfcPropertySet(
            GlobalId=ifcopenshell.guid.new(),
            Name=nombre_pset,
            HasProperties=props
        )
        
        rel = self.ifc.createIfcRelDefinesByProperties(
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[elemento],
            RelatingPropertyDefinition=pset
        )
        
        return pset
    
    def agregar_sedimentador(
        self,
        largo: float,
        ancho: float,
        alto: float,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        carga_superficial: float = 25,
        tiempo_retencion: float = 10800,
        tipo: str = "Alta Tasa",
        **kwargs
    ):
        """
        Agrega sedimentador al modelo BIM.
        
        Args:
            largo, ancho, alto: Dimensiones en metros
            x, y, z: Posición en metros
            carga_superficial: m³/m²/día
            tiempo_retencion: segundos
            tipo: "Convencional", "Alta Tasa", "Laminar"
        """
        # Crear elemento
        sedimentador = ifcopenshell.api.run(
            "root.create_entity",
            self.ifc,
            ifc_class="IfcBuildingElementProxy",
            name=f"Sedimentador {tipo}"
        )
        
        # Crear geometría
        geometria = self._crear_caja(largo, ancho, alto)
        representacion = self._crear_representacion(geometria)
        
        # Asignar representación
        sedimentador.Representation = self.ifc.createIfcProductDefinitionShape(
            Representations=[representacion]
        )
        
        # Posicionar
        self._posicionar_elemento(sedimentador, x, y, z)
        
        # Agregar propiedades técnicas
        volumen = largo * ancho * alto
        area_superficial = largo * ancho
        
        self._agregar_propiedades(
            sedimentador,
            "Pset_Sedimentador",
            {
                "Tipo": tipo,
                "Largo_m": largo,
                "Ancho_m": ancho,
                "Alto_m": alto,
                "Volumen_m3": volumen,
                "Area_Superficial_m2": area_superficial,
                "Carga_Superficial_m3_m2_dia": carga_superficial,
                "Tiempo_Retencion_s": tiempo_retencion,
                "Tiempo_Retencion_h": tiempo_retencion / 3600,
                **kwargs
            }
        )
        
        # Relacionar con edificio
        ifcopenshell.api.run(
            "spatial.assign_container",
            self.ifc,
            product=sedimentador,
            relating_structure=self.edificio
        )
        
        self.elementos.append(sedimentador)
        return sedimentador
    
    def agregar_filtro(
        self,
        largo: float,
        ancho: float,
        alto: float,
        x: float,
        y: float,
        z: float = 0,
        tasa_filtracion: float = 240,
        tipo: str = "Rápida Gravedad",
        medio_filtrante: str = "Arena + Antracita",
        **kwargs
    ):
        """Agrega filtro al modelo BIM"""
        filtro = ifcopenshell.api.run(
            "root.create_entity",
            self.ifc,
            ifc_class="IfcBuildingElementProxy",
            name=f"Filtro {tipo}"
        )
        
        geometria = self._crear_caja(largo, ancho, alto)
        representacion = self._crear_representacion(geometria)
        
        filtro.Representation = self.ifc.createIfcProductDefinitionShape(
            Representations=[representacion]
        )
        
        self._posicionar_elemento(filtro, x, y, z)
        
        area = largo * ancho
        volumen = largo * ancho * alto
        
        self._agregar_propiedades(
            filtro,
            "Pset_Filtro",
            {
                "Tipo": tipo,
                "Largo_m": largo,
                "Ancho_m": ancho,
                "Alto_m": alto,
                "Area_m2": area,
                "Volumen_m3": volumen,
                "Tasa_Filtracion_m3_m2_dia": tasa_filtracion,
                "Medio_Filtrante": medio_filtrante,
                **kwargs
            }
        )
        
        ifcopenshell.api.run(
            "spatial.assign_container",
            self.ifc,
            product=filtro,
            relating_structure=self.edificio
        )
        
        self.elementos.append(filtro)
        return filtro
    
    def agregar_tanque(
        self,
        diametro: float,
        altura: float,
        x: float,
        y: float,
        z: float = 0,
        tipo: str = "Almacenamiento",
        capacidad_m3: Optional[float] = None,
        **kwargs
    ):
        """Agrega tanque cilíndrico al modelo BIM"""
        tanque = ifcopenshell.api.run(
            "root.create_entity",
            self.ifc,
            ifc_class="IfcTank",
            name=f"Tanque {tipo}"
        )
        
        # Para tanque cilíndrico usamos aproximación con caja
        # (ifcopenshell tiene limitaciones para cilindros perfectos)
        geometria = self._crear_caja(diametro, diametro, altura)
        representacion = self._crear_representacion(geometria)
        
        tanque.Representation = self.ifc.createIfcProductDefinitionShape(
            Representations=[representacion]
        )
        
        self._posicionar_elemento(tanque, x, y, z)
        
        if capacidad_m3 is None:
            capacidad_m3 = np.pi * (diametro/2)**2 * altura
        
        self._agregar_propiedades(
            tanque,
            "Pset_Tanque",
            {
                "Tipo": tipo,
                "Diametro_m": diametro,
                "Altura_m": altura,
                "Capacidad_m3": capacidad_m3,
                **kwargs
            }
        )
        
        ifcopenshell.api.run(
            "spatial.assign_container",
            self.ifc,
            product=tanque,
            relating_structure=self.edificio
        )
        
        self.elementos.append(tanque)
        return tanque
    
    def agregar_floculador(
        self,
        largo: float,
        ancho: float,
        alto: float,
        x: float,
        y: float,
        z: float = 0,
        tipo: str = "Pantallas",
        numero_camaras: int = 3,
        gradiente: float = 50,
        tiempo_retencion: float = 1800,
        **kwargs
    ):
        """Agrega floculador al modelo BIM"""
        floculador = ifcopenshell.api.run(
            "root.create_entity",
            self.ifc,
            ifc_class="IfcBuildingElementProxy",
            name=f"Floculador {tipo}"
        )
        
        geometria = self._crear_caja(largo, ancho, alto)
        representacion = self._crear_representacion(geometria)
        
        floculador.Representation = self.ifc.createIfcProductDefinitionShape(
            Representations=[representacion]
        )
        
        self._posicionar_elemento(floculador, x, y, z)
        
        volumen = largo * ancho * alto
        
        self._agregar_propiedades(
            floculador,
            "Pset_Floculador",
            {
                "Tipo": tipo,
                "Largo_m": largo,
                "Ancho_m": ancho,
                "Alto_m": alto,
                "Volumen_m3": volumen,
                "Numero_Camaras": numero_camaras,
                "Gradiente_Velocidad_s-1": gradiente,
                "Tiempo_Retencion_s": tiempo_retencion,
                "Tiempo_Retencion_min": tiempo_retencion / 60,
                **kwargs
            }
        )
        
        ifcopenshell.api.run(
            "spatial.assign_container",
            self.ifc,
            product=floculador,
            relating_structure=self.edificio
        )
        
        self.elementos.append(floculador)
        return floculador
    
    def agregar_componente_generico(
        self,
        componente: ComponenteBIM
    ):
        """
        Agrega componente genérico definido por ComponenteBIM.
        
        Args:
            componente: Instancia de ComponenteBIM
        """
        elemento = ifcopenshell.api.run(
            "root.create_entity",
            self.ifc,
            ifc_class="IfcBuildingElementProxy",
            name=componente.nombre
        )
        
        geometria = self._crear_caja(
            componente.largo,
            componente.ancho,
            componente.alto
        )
        representacion = self._crear_representacion(geometria)
        
        elemento.Representation = self.ifc.createIfcProductDefinitionShape(
            Representations=[representacion]
        )
        
        self._posicionar_elemento(
            elemento,
            componente.posicion_x,
            componente.posicion_y,
            componente.posicion_z
        )
        
        # Propiedades
        props = {
            "Tipo": componente.tipo,
            "Material": componente.material,
            "Largo_m": componente.largo,
            "Ancho_m": componente.ancho,
            "Alto_m": componente.alto,
            "Volumen_m3": componente.largo * componente.ancho * componente.alto,
            **componente.propiedades
        }
        
        self._agregar_propiedades(elemento, f"Pset_{componente.tipo}", props)
        
        ifcopenshell.api.run(
            "spatial.assign_container",
            self.ifc,
            product=elemento,
            relating_structure=self.edificio
        )
        
        self.elementos.append(elemento)
        return elemento
    
    def exportar(self, archivo: str = "PTAP.ifc") -> str:
        """
        Exporta modelo BIM a archivo IFC.
        
        Args:
            archivo: Ruta del archivo de salida
            
        Returns:
            Ruta completa del archivo generado
        """
        ruta = Path(archivo)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        
        self.ifc.write(str(ruta))
        
        return str(ruta.absolute())
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del modelo BIM"""
        return {
            "proyecto": self.proyecto.Name,
            "total_elementos": len(self.elementos),
            "archivo_schema": "IFC4",
            "ubicacion": {
                "latitud": self.sitio.RefLatitude if hasattr(self.sitio, 'RefLatitude') else None,
                "longitud": self.sitio.RefLongitude if hasattr(self.sitio, 'RefLongitude') else None,
                "elevacion": self.sitio.RefElevation if hasattr(self.sitio, 'RefElevation') else None
            }
        }
