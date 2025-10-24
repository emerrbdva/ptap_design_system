Módulo Economics
================

Estimación paramétrica de costos CAPEX/OPEX.

Cost Estimator
--------------

.. automodule:: economics.cost_estimator
   :members:
   :undoc-members:
   :show-inheritance:

Ejemplos
--------

CAPEX
~~~~~

.. code-block:: python

   from economics.cost_estimator import EstimadorCostos

   estimador = EstimadorCostos()
   
   capex = estimador.estimar_capex({
       'caudal': 50,
       'tipo_mezcla': 'resalto_hidraulico',
       'tipo_filtracion': 'rapida_gravedad',
       'numero_filtros': 3
   })

   print(f"CAPEX Total: ${capex['total_capex']:,.0f} COP")
   print(f"Obra Civil: ${capex['obra_civil']['subtotal']:,.0f} COP")
   print(f"Equipos: ${capex['equipos']['subtotal']:,.0f} COP")

OPEX
~~~~

.. code-block:: python

   opex = estimador.estimar_opex(
       diseño_dict={'dosis_coagulante': 30, 'dosis_cloro': 2},
       caudal_m3_dia=4320  # 50 L/s × 86.4
   )

   print(f"OPEX Anual: ${opex['total_opex_anual']:,.0f} COP/año")
   print(f"Químicos: ${opex['quimicos']['subtotal']:,.0f} COP/año")
   print(f"Energía: ${opex['energia']['subtotal']:,.0f} COP/año")

Análisis Financiero
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   financiero = estimador.analisis_financiero_completo(
       capex, opex, caudal_m3_dia=4320
   )

   print(f"VPN 25 años: ${financiero['vpn_total']:,.0f} COP")
   print(f"Costo nivelado: ${financiero['costo_nivelado_m3']:.2f} COP/m³")
