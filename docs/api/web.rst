Módulo Web API
==============

API REST con FastAPI y frontend HTML.

API
---

.. automodule:: web.api
   :members:
   :undoc-members:
   :show-inheritance:

Endpoints Disponibles
---------------------

GET /
~~~~~

Retorna frontend HTML interactivo.

GET /health
~~~~~~~~~~~

Health check del servidor.

**Response:**

.. code-block:: json

   {
     "status": "ok",
     "version": "2.0.0",
     "modules": {
       "validation": true,
       "economics": true,
       "optimization": true,
       "machine_learning": true
     }
   }

POST /api/validar
~~~~~~~~~~~~~~~~~

Valida parámetros de entrada.

**Request:**

.. code-block:: json

   {
     "caudal": 50,
     "turbiedad": 45,
     "ph": 7.2,
     "temperatura": 22
   }

**Response:**

.. code-block:: json

   {
     "valido": true,
     "mensaje": "Parámetros válidos",
     "advertencias": []
   }

POST /api/estimar-costos
~~~~~~~~~~~~~~~~~~~~~~~~

Estima CAPEX y OPEX.

**Request:**

.. code-block:: json

   {
     "caudal": 50,
     "dosis_coagulante": 30,
     "dosis_cloro": 2
   }

**Response:**

.. code-block:: json

   {
     "capex": {
       "total": 306466875,
       "obra_civil": 168750000,
       "equipos": 24000000
     },
     "opex": {
       "total_anual": 226273144,
       "quimicos": 74503800,
       "energia": 51246000
     }
   }

POST /api/optimizar
~~~~~~~~~~~~~~~~~~~

Optimiza diseño multi-objetivo.

**Request:**

.. code-block:: json

   {
     "caudal": 50,
     "turbiedad": 45,
     "ph": 7.2,
     "peso_costo": 0.4,
     "peso_eficiencia": 0.3,
     "peso_conformidad": 0.3
   }

**Response:**

.. code-block:: json

   {
     "exito": true,
     "parametros_optimos": {
       "dosis_coagulante": 83.3,
       "gradiente_mezcla": 749
     },
     "metricas": {
       "eficiencia": 0.814,
       "conformidad_ras": 0.857
     }
   }

POST /api/predecir-eficiencia
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Predice eficiencia con ML.

**Request:**

.. code-block:: json

   {
     "turbiedad_entrada": 45,
     "dosis_coagulante": 30,
     "gradiente_floculacion": 50,
     ...
   }

**Response:**

.. code-block:: json

   {
     "eficiencia_predicha": 0.814,
     "eficiencia_porcentaje": 81.4,
     "variables_mas_importantes": {
       "dosis_coagulante": 0.25,
       "turbiedad_entrada": 0.20
     }
   }

Uso con Python
--------------

.. code-block:: python

   import requests

   # Validar parámetros
   response = requests.post('http://localhost:8000/api/validar', json={
       'caudal': 50,
       'turbiedad': 45,
       'ph': 7.2
   })
   
   print(response.json())

Uso con curl
------------

.. code-block:: bash

   curl -X POST http://localhost:8000/api/estimar-costos \\
        -H "Content-Type: application/json" \\
        -d '{"caudal": 50, "dosis_coagulante": 30}'

Ejecutar Servidor
-----------------

.. code-block:: bash

   # Modo desarrollo
   cd web
   python api.py

   # Modo producción
   uvicorn web.api:app --host 0.0.0.0 --port 8000
