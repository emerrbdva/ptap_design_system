"""
API REST para diseño de PTAP usando FastAPI.

Endpoints disponibles:
- POST /api/validar: Valida parámetros de entrada
- POST /api/diseñar: Diseña PTAP completa
- POST /api/estimar-costos: Estima CAPEX/OPEX
- POST /api/optimizar: Optimiza diseño multi-objetivo
- POST /api/predecir-eficiencia: Predice eficiencia con ML
- GET /api/costos/items: Lista items de costo
- GET /: Frontend HTML
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Agregar ruta del proyecto al path
proyecto_root = Path(__file__).parent.parent
sys.path.insert(0, str(proyecto_root))

# Importar módulos del sistema (con manejo de errores)
try:
    from validation.schemas import (
        ParametrosAguaCruda,
        ParametrosProyecto,
        DiseñoCompleto
    )
    HAS_VALIDATION = True
except ImportError:
    HAS_VALIDATION = False

try:
    from economics.cost_estimator import EstimadorCostos
    HAS_ECONOMICS = True
except ImportError:
    HAS_ECONOMICS = False

try:
    from optimization.multi_objective import OptimizadorMultiobjetivo
    HAS_OPTIMIZATION = True
except ImportError:
    HAS_OPTIMIZATION = False

try:
    from ml.predictor_eficiencia import PredictorEficiencia, GeneradorDatosSinteticos
    HAS_ML = True
except ImportError:
    HAS_ML = False


# Crear aplicación FastAPI
app = FastAPI(
    title="PTAP Design API",
    description="API REST para diseño de Plantas de Tratamiento de Agua Potable",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS (permitir requests desde navegadores)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (HTML, CSS, JS)
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ============================================================================
# MODELOS PYDANTIC PARA API
# ============================================================================

class ParametrosValidacionRequest(BaseModel):
    """Request para validación de parámetros"""
    caudal: float = Field(..., gt=0, le=10000, description="Caudal en L/s")
    turbiedad: float = Field(..., ge=0, le=10000, description="Turbiedad en NTU")
    ph: float = Field(..., ge=4, le=10, description="pH del agua cruda")
    temperatura: float = Field(default=20, ge=4, le=35, description="Temperatura en °C")
    color: Optional[float] = Field(default=None, ge=0, le=1000, description="Color en UPC")
    
    class Config:
        json_schema_extra = {
            "example": {
                "caudal": 50,
                "turbiedad": 45,
                "ph": 7.2,
                "temperatura": 22,
                "color": 80
            }
        }


class DiseñoRequest(BaseModel):
    """Request para diseño completo de PTAP"""
    # Parámetros proyecto
    nombre_proyecto: str = Field(..., min_length=3, description="Nombre del proyecto")
    poblacion_diseño: int = Field(..., gt=0, description="Población de diseño")
    
    # Parámetros agua cruda
    caudal: float = Field(..., gt=0, le=10000)
    turbiedad: float = Field(..., ge=0, le=10000)
    ph: float = Field(..., ge=4, le=10)
    temperatura: float = Field(default=20, ge=4, le=35)
    
    # Parámetros de diseño (opcionales, se calcularán si no se proveen)
    dosis_coagulante: Optional[float] = Field(default=None, ge=0, le=200)
    gradiente_mezcla: Optional[float] = Field(default=None, ge=700, le=1500)
    gradiente_floculacion: Optional[float] = Field(default=None, ge=20, le=80)
    
    class Config:
        json_schema_extra = {
            "example": {
                "nombre_proyecto": "PTAP San José",
                "poblacion_diseño": 15000,
                "caudal": 50,
                "turbiedad": 45,
                "ph": 7.2,
                "temperatura": 22
            }
        }


class CostosRequest(BaseModel):
    """Request para estimación de costos"""
    caudal: float = Field(..., gt=0, description="Caudal en L/s")
    dosis_coagulante: float = Field(default=30, ge=0, le=200, description="Dosis coagulante mg/L")
    dosis_cloro: float = Field(default=2, ge=0, le=10, description="Dosis cloro mg/L")
    
    class Config:
        json_schema_extra = {
            "example": {
                "caudal": 50,
                "dosis_coagulante": 30,
                "dosis_cloro": 2
            }
        }


class OptimizacionRequest(BaseModel):
    """Request para optimización multi-objetivo"""
    caudal: float = Field(..., gt=0)
    turbiedad: float = Field(..., ge=0)
    ph: float = Field(..., ge=4, le=10)
    
    # Pesos de objetivos
    peso_costo: float = Field(default=0.4, ge=0, le=1)
    peso_eficiencia: float = Field(default=0.3, ge=0, le=1)
    peso_conformidad: float = Field(default=0.3, ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "caudal": 50,
                "turbiedad": 45,
                "ph": 7.2,
                "peso_costo": 0.4,
                "peso_eficiencia": 0.3,
                "peso_conformidad": 0.3
            }
        }


class PrediccionRequest(BaseModel):
    """Request para predicción de eficiencia con ML"""
    turbiedad_entrada: float = Field(..., ge=5, le=500)
    ph_entrada: float = Field(..., ge=6, le=8.5)
    temperatura: float = Field(..., ge=15, le=30)
    dosis_coagulante: float = Field(..., ge=5, le=80)
    gradiente_mezcla: float = Field(..., ge=700, le=1500)
    tiempo_mezcla: float = Field(..., ge=10, le=60)
    gradiente_floculacion: float = Field(..., ge=20, le=80)
    tiempo_floculacion: float = Field(..., ge=1200, le=2400)
    carga_superficial: float = Field(..., ge=10, le=40)
    tasa_filtracion: float = Field(..., ge=120, le=360)
    
    class Config:
        json_schema_extra = {
            "example": {
                "turbiedad_entrada": 45,
                "ph_entrada": 7.2,
                "temperatura": 22,
                "dosis_coagulante": 30,
                "gradiente_mezcla": 1000,
                "tiempo_mezcla": 30,
                "gradiente_floculacion": 50,
                "tiempo_floculacion": 1800,
                "carga_superficial": 25,
                "tasa_filtracion": 240
            }
        }


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal - Frontend HTML"""
    html_file = Path(__file__).parent / "static" / "index.html"
    
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PTAP Design API</title>
            <style>
                body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #007bff; }
                .status { padding: 10px; background: #e8f4f8; border-radius: 5px; margin: 20px 0; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>🌊 PTAP Design API</h1>
            <div class="status">
                <p><strong>Estado:</strong> ✅ API funcionando correctamente</p>
                <p><strong>Versión:</strong> 2.0.0</p>
            </div>
            <h2>Documentación</h2>
            <ul>
                <li><a href="/docs">📖 Swagger UI (Documentación interactiva)</a></li>
                <li><a href="/redoc">📘 ReDoc (Documentación alternativa)</a></li>
            </ul>
            <h2>Endpoints Disponibles</h2>
            <ul>
                <li><code>POST /api/validar</code> - Validar parámetros de entrada</li>
                <li><code>POST /api/diseñar</code> - Diseñar PTAP completa</li>
                <li><code>POST /api/estimar-costos</code> - Estimar CAPEX/OPEX</li>
                <li><code>POST /api/optimizar</code> - Optimizar diseño</li>
                <li><code>POST /api/predecir-eficiencia</code> - Predecir eficiencia (ML)</li>
                <li><code>GET /api/costos/items</code> - Listar items de costo</li>
            </ul>
        </body>
        </html>
        """)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "modules": {
            "validation": HAS_VALIDATION,
            "economics": HAS_ECONOMICS,
            "optimization": HAS_OPTIMIZATION,
            "machine_learning": HAS_ML
        }
    }


@app.post("/api/validar")
async def validar_parametros(params: ParametrosValidacionRequest):
    """
    Valida parámetros de entrada usando Pydantic.
    
    Retorna información sobre conformidad con RAS 2017.
    """
    if not HAS_VALIDATION:
        raise HTTPException(status_code=503, detail="Módulo de validación no disponible")
    
    try:
        # Validar con Pydantic (ya valida en el request)
        resultado = {
            "valido": True,
            "mensaje": "Parámetros válidos",
            "parametros": params.model_dump(),
            "advertencias": []
        }
        
        # Advertencias según rangos típicos
        if params.turbiedad > 100:
            resultado["advertencias"].append("Turbiedad alta - considerar pretratamiento")
        
        if params.ph < 6.5 or params.ph > 8.0:
            resultado["advertencias"].append("pH fuera de rango óptimo (6.5-8.0)")
        
        if params.caudal > 1000:
            resultado["advertencias"].append("Caudal alto - considerar PTAP modular")
        
        return resultado
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/estimar-costos")
async def estimar_costos(request: CostosRequest):
    """
    Estima CAPEX, OPEX y análisis financiero.
    
    Retorna costos detallados en COP.
    """
    if not HAS_ECONOMICS:
        raise HTTPException(status_code=503, detail="Módulo de economía no disponible")
    
    try:
        estimador = EstimadorCostos()
        
        # Estimar CAPEX
        capex = estimador.estimar_capex({
            'caudal': request.caudal,
            'tipo_mezcla': 'resalto_hidraulico',
            'tipo_floculacion': 'pantallas',
            'tipo_sedimentacion': 'alta_tasa',
            'tipo_filtracion': 'rapida_gravedad',
            'numero_filtros': max(2, int(request.caudal / 25) + 1)
        })
        
        # Estimar OPEX
        caudal_m3_dia = request.caudal * 86.4
        opex = estimador.estimar_opex(
            {
                'dosis_coagulante': request.dosis_coagulante,
                'dosis_cloro': request.dosis_cloro
            },
            caudal_m3_dia
        )
        
        # Análisis financiero
        financiero = estimador.analisis_financiero_completo(capex, opex, caudal_m3_dia)
        
        return {
            "capex": {
                "total": capex['total_capex'],
                "obra_civil": capex['obra_civil']['subtotal'],
                "equipos": capex['equipos']['subtotal'],
                "tuberias": capex['tuberias']['subtotal'],
                "costo_unitario_ls": capex['costo_unitario_ls']
            },
            "opex": {
                "total_anual": opex['total_opex_anual'],
                "quimicos": opex['quimicos']['subtotal'],
                "energia": opex['energia']['subtotal'],
                "personal": opex['personal']['subtotal'],
                "mantenimiento": opex['mantenimiento'],
                "costo_m3": opex['costo_por_m3']
            },
            "financiero": {
                "vpn_25_años": financiero['vpn_total'],
                "costo_nivelado_m3": financiero['costo_nivelado_m3'],
                "tir": financiero.get('tir', 0)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en estimación: {str(e)}")


@app.post("/api/optimizar")
async def optimizar_diseño(request: OptimizacionRequest):
    """
    Optimiza diseño usando algoritmo multi-objetivo.
    
    Retorna parámetros óptimos balanceando costo, eficiencia y conformidad.
    """
    if not HAS_OPTIMIZATION:
        raise HTTPException(status_code=503, detail="Módulo de optimización no disponible")
    
    try:
        # Validar que pesos sumen 1.0
        suma_pesos = request.peso_costo + request.peso_eficiencia + request.peso_conformidad
        if abs(suma_pesos - 1.0) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Los pesos deben sumar 1.0 (actual: {suma_pesos:.2f})"
            )
        
        optimizador = OptimizadorMultiobjetivo(
            peso_costo=request.peso_costo,
            peso_eficiencia=request.peso_eficiencia,
            peso_conformidad=request.peso_conformidad
        )
        
        parametros_fijos = {
            'caudal': request.caudal,
            'turbiedad': request.turbiedad,
            'ph': request.ph,
            'temperatura': 20,
            'numero_filtros': max(2, int(request.caudal / 25) + 1)
        }
        
        variables = [
            'gradiente_mezcla_rapida',
            'dosis_coagulante',
            'gradiente_floculacion',
            'tiempo_floculacion',
            'carga_superficial',
            'tasa_filtracion',
            'dosis_cloro'
        ]
        
        resultado = optimizador.optimizar_diseño(
            parametros_fijos=parametros_fijos,
            variables_optimizar=variables,
            metodo='differential_evolution'
        )
        
        if resultado.exito:
            return {
                "exito": True,
                "parametros_optimos": resultado.parametros_optimos,
                "metricas": {
                    "costo_vpn": resultado.costo_total,
                    "eficiencia": resultado.eficiencia,
                    "conformidad_ras": resultado.conformidad_ras
                },
                "iteraciones": resultado.num_iteraciones,
                "mensaje": resultado.mensaje
            }
        else:
            return {
                "exito": False,
                "mensaje": resultado.mensaje
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en optimización: {str(e)}")


@app.post("/api/predecir-eficiencia")
async def predecir_eficiencia(request: PrediccionRequest):
    """
    Predice eficiencia de remoción usando Machine Learning.
    
    Usa modelo Random Forest pre-entrenado con datos sintéticos.
    """
    if not HAS_ML:
        raise HTTPException(status_code=503, detail="Módulo de ML no disponible")
    
    try:
        # Cargar o entrenar modelo
        predictor = PredictorEficiencia()
        
        # Intentar cargar modelo existente
        try:
            predictor.cargar('ml/modelos')
        except FileNotFoundError:
            # Si no existe, entrenar con datos sintéticos
            generador = GeneradorDatosSinteticos()
            datos = generador.generar_dataset(n_samples=1000)
            resultado_entrenamiento = predictor.entrenar(datos)
            predictor.guardar('ml/modelos')
        
        # Predecir
        parametros = request.model_dump()
        eficiencia = predictor.predecir(parametros)
        
        # Obtener importancia de features
        importancia = predictor.analizar_importancia()
        
        return {
            "eficiencia_predicha": float(eficiencia),
            "eficiencia_porcentaje": float(eficiencia * 100),
            "parametros_entrada": parametros,
            "variables_mas_importantes": dict(list(importancia.items())[:5]),
            "modelo_info": predictor.obtener_estadisticas()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.get("/api/costos/items")
async def listar_items_costo():
    """
    Lista todos los items de costo disponibles en la base de datos.
    """
    if not HAS_ECONOMICS:
        raise HTTPException(status_code=503, detail="Módulo de economía no disponible")
    
    try:
        estimador = EstimadorCostos()
        items = estimador.base_datos._cargar_base_datos()
        
        return {
            "total_items": len(items),
            "items": [
                {
                    "codigo": item['codigo'],
                    "descripcion": item['descripcion'],
                    "precio_unitario": item['precio_unitario'],
                    "unidad": item['unidad']
                }
                for item in items
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/diseñar")
async def diseñar_ptap(request: DiseñoRequest):
    """
    Diseño completo de PTAP (endpoint integrado).
    
    Combina validación, diseño, costos y optimización.
    """
    try:
        # Paso 1: Validación
        validacion = await validar_parametros(ParametrosValidacionRequest(
            caudal=request.caudal,
            turbiedad=request.turbiedad,
            ph=request.ph,
            temperatura=request.temperatura
        ))
        
        # Paso 2: Costos
        costos = await estimar_costos(CostosRequest(
            caudal=request.caudal,
            dosis_coagulante=request.dosis_coagulante or 30,
            dosis_cloro=2
        ))
        
        # Paso 3: Optimización (opcional)
        optimizacion = None
        if HAS_OPTIMIZATION:
            try:
                optimizacion = await optimizar_diseño(OptimizacionRequest(
                    caudal=request.caudal,
                    turbiedad=request.turbiedad,
                    ph=request.ph
                ))
            except:
                pass
        
        return {
            "proyecto": request.nombre_proyecto,
            "poblacion": request.poblacion_diseño,
            "validacion": validacion,
            "costos": costos,
            "optimizacion": optimizacion,
            "timestamp": "2025-10-11"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en diseño: {str(e)}")


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🌊 PTAP Design API Server")
    print("="*60)
    print(f"Validation: {'✅' if HAS_VALIDATION else '❌'}")
    print(f"Economics: {'✅' if HAS_ECONOMICS else '❌'}")
    print(f"Optimization: {'✅' if HAS_OPTIMIZATION else '❌'}")
    print(f"Machine Learning: {'✅' if HAS_ML else '❌'}")
    print("="*60)
    print("\nIniciando servidor en http://localhost:8000")
    print("Documentación: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
