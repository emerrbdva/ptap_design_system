Módulo Optimization
===================

Optimización multi-objetivo con scipy.

Multi-Objective Optimizer
--------------------------

.. automodule:: optimization.multi_objective
   :members:
   :undoc-members:
   :show-inheritance:

Ejemplos
--------

Optimización Básica
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from optimization.multi_objective import OptimizadorMultiobjetivo

   opt = OptimizadorMultiobjetivo(
       peso_costo=0.4,
       peso_eficiencia=0.3,
       peso_conformidad=0.3
   )

   resultado = opt.optimizar_diseño(
       parametros_fijos={
           'caudal': 50,
           'turbiedad': 45,
           'ph': 7.2
       },
       variables_optimizar=[
           'dosis_coagulante',
           'gradiente_mezcla_rapida',
           'tasa_filtracion'
       ]
   )

   if resultado.exito:
       print(f"Eficiencia: {resultado.eficiencia * 100:.1f}%")
       print(f"Costo VPN: ${resultado.costo_total:,.0f} COP")
       print(f"Parámetros: {resultado.parametros_optimos}")

Frontera de Pareto
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   pareto = opt.optimizacion_pareto(
       parametros_fijos={'caudal': 50},
       variables_optimizar=['dosis_coagulante'],
       num_puntos=10
   )

   for i, p in enumerate(pareto):
       print(f"Punto {i}: Costo=${p['costo']:,.0f}, "
             f"Eficiencia={p['eficiencia']*100:.1f}%")

Análisis de Sensibilidad
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   sensibilidad = opt.analisis_sensibilidad(
       parametros_fijos={'caudal': 50},
       variable='dosis_coagulante',
       rango=(10, 80),
       num_puntos=20
   )

   valores = sensibilidad['valores']
   costos = sensibilidad['costos']
   eficiencias = sensibilidad['eficiencias']
