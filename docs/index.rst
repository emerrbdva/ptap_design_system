PTAP Design System - Documentación
====================================

.. image:: https://img.shields.io/badge/version-2.0.0-blue.svg
   :alt: Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :alt: License

.. image:: https://img.shields.io/badge/python-3.12+-blue.svg
   :alt: Python

Sistema profesional de diseño de Plantas de Tratamiento de Agua Potable (PTAP).

**100% Gratuito • Open Source • Sin Costos de Operación**

Características Principales
---------------------------

✅ **Validación Automática** con Pydantic v2
   - Validación estricta de parámetros de entrada
   - Verificación contra normas RAS 2017 y Res. 2115/2007
   - Modelos de datos robustos

💰 **Estimación de Costos**
   - CAPEX (inversión inicial)
   - OPEX (costos operacionales anuales)
   - Análisis financiero VPN a 25 años
   - Base de datos local con 25+ items de costo Colombia 2024

⚡ **Optimización Multi-objetivo**
   - Algoritmo genético (Differential Evolution)
   - Balance entre costo, eficiencia y conformidad
   - Frontera de Pareto
   - Análisis de sensibilidad

🤖 **Machine Learning**
   - Random Forest para predicción de eficiencia
   - Entrenamiento con datos sintéticos o históricos
   - Análisis de importancia de variables

🌐 **API Web REST**
   - FastAPI con documentación interactiva
   - Frontend HTML/CSS/JavaScript puro
   - Sin dependencias de frameworks comerciales

🏗️ **Exportación BIM**
   - Formato IFC 4 (ISO 16739:2018)
   - Compatible con Revit, ArchiCAD, Navisworks
   - Modelos 3D con propiedades técnicas

Instalación
-----------

.. code-block:: bash

   # Clonar repositorio
   git clone https://github.com/tu-usuario/ptap_design_system.git
   cd ptap_design_system

   # Crear entorno virtual
   python -m venv venv
   venv\\Scripts\\activate  # Windows
   source venv/bin/activate  # Linux/Mac

   # Instalar dependencias
   pip install -r requirements.txt

Inicio Rápido
-------------

Diseño Básico
~~~~~~~~~~~~~

.. code-block:: python

   from validation.schemas import ParametrosAguaCruda, ParametrosProyecto
   from economics.cost_estimator import EstimadorCostos

   # Definir parámetros
   agua_cruda = ParametrosAguaCruda(
       caudal=50,
       turbiedad=45,
       ph=7.2,
       temperatura=22
   )

   # Estimar costos
   estimador = EstimadorCostos()
   capex = estimador.estimar_capex({'caudal': 50})
   
   print(f"CAPEX: ${capex['total_capex']:,.0f} COP")

Optimización
~~~~~~~~~~~~

.. code-block:: python

   from optimization.multi_objective import OptimizadorMultiobjetivo

   # Crear optimizador
   opt = OptimizadorMultiobjetivo(
       peso_costo=0.4,
       peso_eficiencia=0.3,
       peso_conformidad=0.3
   )

   # Optimizar
   resultado = opt.optimizar_diseño(
       parametros_fijos={'caudal': 50},
       variables_optimizar=['dosis_coagulante', 'gradiente_mezcla']
   )

   print(f"Eficiencia: {resultado.eficiencia * 100:.1f}%")

Machine Learning
~~~~~~~~~~~~~~~~

.. code-block:: python

   from ml.predictor_eficiencia import PredictorEficiencia, GeneradorDatosSinteticos

   # Generar datos sintéticos
   gen = GeneradorDatosSinteticos()
   datos = gen.generar_dataset(n_samples=1000)

   # Entrenar modelo
   predictor = PredictorEficiencia()
   resultado = predictor.entrenar(datos)
   
   print(f"R² Score: {resultado.r2_test:.3f}")

   # Predecir
   eficiencia = predictor.predecir({
       'turbiedad_entrada': 45,
       'dosis_coagulante': 30,
       # ... más parámetros
   })

API Web
~~~~~~~

.. code-block:: bash

   # Iniciar servidor
   cd web
   python api.py

   # Abrir navegador en http://localhost:8000

Exportación BIM
~~~~~~~~~~~~~~~

.. code-block:: python

   from bim.ifc_exporter import ExportadorBIM

   # Crear exportador
   exporter = ExportadorBIM(
       nombre_proyecto="PTAP San José",
       ubicacion=(4.5, -73.2, 250)
   )

   # Agregar componentes
   exporter.agregar_sedimentador(
       largo=10, ancho=8, alto=4,
       x=0, y=0, z=0
   )

   # Exportar
   exporter.exportar("PTAP_50Ls.ifc")

Índice de Contenidos
--------------------

.. toctree::
   :maxdepth: 2
   :caption: Guía de Usuario

   instalacion
   inicio_rapido
   ejemplos
   guia_completa

.. toctree::
   :maxdepth: 2
   :caption: Referencia API

   api/core
   api/validation
   api/economics
   api/optimization
   api/ml
   api/web
   api/bim

.. toctree::
   :maxdepth: 1
   :caption: Desarrollo

   desarrollo/contribuir
   desarrollo/arquitectura
   desarrollo/testing

Índices y Tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Licencia
========

MIT License - 100% Gratuito y Open Source

Copyright (c) 2025 PTAP Design System Team

Soporte
=======

- **Documentación**: https://ptap-design-system.readthedocs.io
- **Issues**: https://github.com/tu-usuario/ptap_design_system/issues
- **Discusiones**: https://github.com/tu-usuario/ptap_design_system/discussions
