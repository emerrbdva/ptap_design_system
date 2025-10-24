Módulo BIM
==========

Exportación de modelos 3D en formato IFC.

IFC Exporter
------------

.. automodule:: bim.ifc_exporter
   :members:
   :undoc-members:
   :show-inheritance:

Ejemplos
--------

Modelo Básico
~~~~~~~~~~~~~

.. code-block:: python

   from bim.ifc_exporter import ExportadorBIM

   # Crear exportador
   exporter = ExportadorBIM(
       nombre_proyecto="PTAP San José",
       ubicacion=(4.5, -73.2, 250),  # lat, lon, elevación
       autor="Ingeniero XYZ"
   )

   # Agregar sedimentador
   exporter.agregar_sedimentador(
       largo=10,
       ancho=8,
       alto=4,
       x=0,
       y=0,
       z=0,
       carga_superficial=25,
       tiempo_retencion=10800,
       tipo="Alta Tasa"
   )

   # Agregar filtros
   for i in range(3):
       exporter.agregar_filtro(
           largo=5,
           ancho=4,
           alto=3,
           x=15,
           y=i * 5,
           z=0,
           tasa_filtracion=240,
           tipo="Rápida Gravedad"
       )

   # Exportar
   archivo = exporter.exportar("PTAP_50Ls.ifc")
   print(f"Modelo exportado: {archivo}")

Componente Genérico
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from bim.ifc_exporter import ComponenteBIM

   # Definir componente
   comp = ComponenteBIM(
       nombre="Cámara de Aquietamiento",
       tipo="tanque",
       largo=3,
       ancho=3,
       alto=2,
       posicion_x=20,
       posicion_y=0,
       posicion_z=0,
       propiedades={
           'volumen_util': 18,
           'tiempo_retencion': 300
       },
       material="Concreto 3000 PSI"
   )

   exporter.agregar_componente_generico(comp)

Floculador
~~~~~~~~~~

.. code-block:: python

   exporter.agregar_floculador(
       largo=12,
       ancho=6,
       alto=3.5,
       x=30,
       y=0,
       z=0,
       tipo="Pantallas",
       numero_camaras=3,
       gradiente=50,
       tiempo_retencion=1800
   )

Tanque
~~~~~~

.. code-block:: python

   exporter.agregar_tanque(
       diametro=10,
       altura=5,
       x=50,
       y=10,
       z=0,
       tipo="Almacenamiento",
       capacidad_m3=393
   )

Estadísticas del Modelo
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   stats = exporter.obtener_estadisticas()
   print(f"Proyecto: {stats['proyecto']}")
   print(f"Total elementos: {stats['total_elementos']}")
   print(f"Schema: {stats['archivo_schema']}")

Visualización
-------------

El archivo IFC generado puede abrirse con:

- **Autodesk Revit**: File → Open → Seleccionar .ifc
- **ArchiCAD**: File → Open → IFC
- **Solibri**: Free IFC viewer
- **BIM Vision**: Visor gratuito Windows
- **FreeCAD**: Open source CAD

Propiedades en IFC
------------------

Cada componente incluye property sets con:

- Dimensiones (largo, ancho, alto)
- Volumen
- Parámetros hidráulicos (caudal, tiempo retención, etc.)
- Tipo de proceso
- Material

Estos datos son accesibles desde cualquier software BIM compatible.
