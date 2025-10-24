Módulo Machine Learning
=======================

Predicción de eficiencia usando Random Forest.

Predictor de Eficiencia
------------------------

.. automodule:: ml.predictor_eficiencia
   :members:
   :undoc-members:
   :show-inheritance:

Ejemplos
--------

Entrenamiento con Datos Sintéticos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from ml.predictor_eficiencia import PredictorEficiencia, GeneradorDatosSinteticos

   # Generar datos
   generador = GeneradorDatosSinteticos(seed=42)
   datos = generador.generar_dataset(n_samples=1000)

   # Entrenar
   predictor = PredictorEficiencia(n_estimators=100)
   resultado = predictor.entrenar(datos, test_size=0.2, cv_folds=5)

   print(f"R² Train: {resultado.r2_train:.3f}")
   print(f"R² Test: {resultado.r2_test:.3f}")
   print(f"MAE: {resultado.mae_test:.4f}")
   print(f"CV Scores: {resultado.cv_scores}")

Predicción
~~~~~~~~~~

.. code-block:: python

   parametros = {
       'turbiedad_entrada': 45,
       'ph_entrada': 7.2,
       'temperatura': 22,
       'dosis_coagulante': 30,
       'gradiente_mezcla': 1000,
       'tiempo_mezcla': 30,
       'gradiente_floculacion': 50,
       'tiempo_floculacion': 1800,
       'carga_superficial': 25,
       'tasa_filtracion': 240
   }

   eficiencia = predictor.predecir(parametros)
   print(f"Eficiencia predicha: {eficiencia * 100:.1f}%")

Importancia de Variables
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   importancia = predictor.analizar_importancia()
   
   for feature, score in importancia.items():
       print(f"{feature}: {score * 100:.1f}%")

Persistencia
~~~~~~~~~~~~

.. code-block:: python

   # Guardar modelo
   predictor.guardar('ml/modelos')

   # Cargar modelo
   predictor_nuevo = PredictorEficiencia()
   predictor_nuevo.cargar('ml/modelos')
