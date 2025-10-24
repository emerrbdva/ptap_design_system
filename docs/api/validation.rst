Módulo Validation
=================

El módulo ``validation`` proporciona validación robusta usando Pydantic v2.

Schemas
-------

.. automodule:: validation.schemas
   :members:
   :undoc-members:
   :show-inheritance:

Ejemplos
--------

Validación de Parámetros de Agua Cruda
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from validation.schemas import ParametrosAguaCruda

   # Validación exitosa
   agua = ParametrosAguaCruda(
       caudal=50,
       turbiedad=45,
       ph=7.2,
       temperatura=22
   )

   # Validación con error
   try:
       agua_invalida = ParametrosAguaCruda(
           caudal=-10,  # Error: debe ser > 0
           turbiedad=45,
           ph=7.2
       )
   except ValidationError as e:
       print(e)

Diseño Completo
~~~~~~~~~~~~~~~

.. code-block:: python

   from validation.schemas import DiseñoCompleto

   diseño = DiseñoCompleto(
       parametros_proyecto=...,
       parametros_agua_cruda=...,
       aireacion=...,
       mezcla_rapida=...,
       floculacion=...,
       sedimentacion=...,
       filtracion=...,
       desinfeccion=...
   )

   # Validar contra RAS
   conformidad = diseño.validar_contra_ras()
   print(f"Conformidad: {conformidad['porcentaje_conformidad']:.1f}%")
