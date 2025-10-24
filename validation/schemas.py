"""
Modelos Pydantic para Validación de Datos de Entrada
Proporciona validación robusta con tipos estrictos para todos los parámetros
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime


class ParametrosAguaCruda(BaseModel):
    """Parámetros de calidad de agua cruda"""
    
    caudal: float = Field(
        ..., 
        gt=0, 
        lt=10000, 
        description="Caudal de diseño en L/s"
    )
    temperatura: float = Field(
        default=18.0,
        ge=4.0,
        le=35.0,
        description="Temperatura del agua en °C"
    )
    turbiedad: float = Field(
        ...,
        ge=0,
        le=10000,
        description="Turbiedad en NTU"
    )
    color: float = Field(
        default=0,
        ge=0,
        le=500,
        description="Color aparente en UPC (Unidades Platino-Cobalto)"
    )
    ph: float = Field(
        ...,
        ge=4.0,
        le=10.0,
        description="pH del agua"
    )
    alcalinidad: Optional[float] = Field(
        None,
        ge=0,
        le=500,
        description="Alcalinidad total en mg/L CaCO3"
    )
    dureza: Optional[float] = Field(
        None,
        ge=0,
        le=1000,
        description="Dureza total en mg/L CaCO3"
    )
    hierro: Optional[float] = Field(
        None,
        ge=0,
        le=50,
        description="Concentración de hierro en mg/L"
    )
    manganeso: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Concentración de manganeso en mg/L"
    )
    coliformes_totales: Optional[int] = Field(
        None,
        ge=0,
        description="Coliformes totales en UFC/100mL"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "caudal": 50.0,
                "temperatura": 18.0,
                "turbiedad": 25.0,
                "color": 40.0,
                "ph": 7.2,
                "alcalinidad": 80.0,
                "dureza": 120.0,
                "hierro": 0.8,
                "manganeso": 0.15,
                "coliformes_totales": 5000
            }
        }


class ParametrosProyecto(BaseModel):
    """Parámetros generales del proyecto"""
    
    nombre: str = Field(..., min_length=3, max_length=200, description="Nombre del proyecto")
    ubicacion: str = Field(..., min_length=3, max_length=200, description="Ubicación (municipio, departamento)")
    poblacion_diseño: int = Field(..., gt=0, le=10000000, description="Población de diseño")
    dotacion: float = Field(default=150, gt=0, le=500, description="Dotación en L/hab/día")
    periodo_diseño: int = Field(default=25, gt=5, le=50, description="Período de diseño en años")
    latitud: Optional[float] = Field(None, ge=-90, le=90, description="Latitud del proyecto")
    longitud: Optional[float] = Field(None, ge=-180, le=180, description="Longitud del proyecto")
    altitud: Optional[float] = Field(None, ge=0, le=5000, description="Altitud en msnm")
    
    @field_validator('nombre', 'ubicacion')
    @classmethod
    def validar_texto(cls, v):
        """Validar que el texto no esté vacío o solo contenga espacios"""
        if not v or not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v.strip()


class DiseñoAireacion(BaseModel):
    """Parámetros de diseño para aireación"""
    
    tipo: Literal['cascada', 'bandejas', 'difusion'] = Field(
        ..., 
        description="Tipo de sistema de aireación"
    )
    numero_bandejas: int = Field(default=4, ge=3, le=8, description="Número de bandejas (para tipo cascada)")
    altura_caida: float = Field(default=0.3, ge=0.15, le=0.6, description="Altura de caída por bandeja en m")
    objetivo_remocion: Optional[str] = Field(
        None, 
        description="Contaminante objetivo (hierro, manganeso, CO2, H2S)"
    )


class DiseñoMezclaRapida(BaseModel):
    """Parámetros de diseño para mezcla rápida"""
    
    tipo: Literal['resalto_hidraulico', 'mecanica', 'tuberia'] = Field(
        ..., 
        description="Tipo de mezclador rápido"
    )
    gradiente_velocidad: float = Field(
        default=1000,
        ge=700,
        le=1500,
        description="Gradiente de velocidad en s⁻¹"
    )
    tiempo_retencion: float = Field(
        default=30,
        ge=10,
        le=60,
        description="Tiempo de retención en segundos"
    )
    dosis_coagulante: Optional[float] = Field(
        None,
        ge=0,
        le=200,
        description="Dosis de coagulante en mg/L"
    )
    tipo_coagulante: Optional[Literal['sulfato_aluminio', 'pac', 'cloruro_ferrico']] = Field(
        None,
        description="Tipo de coagulante"
    )


class DiseñoFloculacion(BaseModel):
    """Parámetros de diseño para floculación"""
    
    tipo: Literal['pantallas', 'mecanica', 'alabes'] = Field(
        ...,
        description="Tipo de floculador"
    )
    numero_camaras: int = Field(default=3, ge=2, le=4, description="Número de cámaras de floculación")
    gradiente_velocidad: float = Field(
        default=50,
        ge=20,
        le=80,
        description="Gradiente de velocidad promedio en s⁻¹"
    )
    tiempo_retencion: float = Field(
        default=1800,
        ge=1200,
        le=2400,
        description="Tiempo de retención total en segundos"
    )
    
    @field_validator('tiempo_retencion')
    @classmethod
    def validar_tiempo_minimo(cls, v):
        """Validar que el tiempo sea suficiente"""
        if v < 1200:
            raise ValueError("El tiempo de retención debe ser mínimo 20 minutos (1200 s)")
        return v


class DiseñoSedimentacion(BaseModel):
    """Parámetros de diseño para sedimentación"""
    
    tipo: Literal['convencional', 'alta_tasa', 'laminar'] = Field(
        ...,
        description="Tipo de sedimentador"
    )
    carga_superficial: float = Field(
        default=25.0,
        ge=10.0,
        le=40.0,
        description="Carga superficial en m³/m²/día"
    )
    tiempo_retencion: float = Field(
        default=10800,
        ge=7200,
        le=14400,
        description="Tiempo de retención en segundos"
    )
    numero_modulos: int = Field(default=2, ge=1, le=4, description="Número de módulos")
    
    @model_validator(mode='after')
    def validar_tipo_carga(self):
        """Validar que la carga superficial sea apropiada para el tipo"""
        if self.tipo == 'alta_tasa' and self.carga_superficial > 40:
            raise ValueError("Carga superficial muy alta para sedimentadores de alta tasa")
        elif self.tipo == 'convencional' and self.carga_superficial > 25:
            raise ValueError("Carga superficial muy alta para sedimentadores convencionales")
        
        return self


class DiseñoFiltracion(BaseModel):
    """Parámetros de diseño para filtración"""
    
    tipo: Literal['rapida_gravedad', 'lenta', 'presion'] = Field(
        ...,
        description="Tipo de filtración"
    )
    tasa_filtracion: float = Field(
        default=240,
        ge=120,
        le=360,
        description="Tasa de filtración en m³/m²/día"
    )
    numero_filtros: int = Field(
        default=2,
        ge=2,
        le=8,
        description="Número de unidades de filtración"
    )
    espesor_lecho_arena: float = Field(
        default=0.7,
        ge=0.6,
        le=0.8,
        description="Espesor del lecho de arena en m"
    )
    espesor_lecho_antracita: Optional[float] = Field(
        None,
        ge=0.3,
        le=0.6,
        description="Espesor del lecho de antracita en m (si es lecho dual)"
    )
    
    @field_validator('numero_filtros')
    @classmethod
    def validar_minimo_filtros(cls, v):
        """Validar que haya al menos 2 filtros (RAS 2017)"""
        if v < 2:
            raise ValueError("Se requieren mínimo 2 unidades de filtración según RAS 2017")
        return v


class DiseñoDesinfeccion(BaseModel):
    """Parámetros de diseño para desinfección"""
    
    tipo: Literal['cloro_gas', 'hipoclorito_sodio', 'hipoclorito_calcio', 'uv', 'ozono'] = Field(
        ...,
        description="Tipo de desinfección"
    )
    dosis_cloro: Optional[float] = Field(
        None,
        ge=0.5,
        le=10.0,
        description="Dosis de cloro en mg/L"
    )
    tiempo_contacto: float = Field(
        default=1800,
        ge=1800,
        le=3600,
        description="Tiempo de contacto en segundos"
    )
    cloro_residual_objetivo: float = Field(
        default=0.5,
        ge=0.3,
        le=2.0,
        description="Cloro residual objetivo en mg/L"
    )
    
    @model_validator(mode='after')
    def validar_parametros_cloro(self):
        """Validar que si el tipo usa cloro, se especifique la dosis"""
        if self.tipo in ['cloro_gas', 'hipoclorito_sodio', 'hipoclorito_calcio'] and self.dosis_cloro is None:
            raise ValueError(f"Debe especificar dosis_cloro para el tipo {self.tipo}")
        
        return self


class DiseñoCompleto(BaseModel):
    """Modelo completo de diseño de PTAP"""
    
    proyecto: ParametrosProyecto
    agua_cruda: ParametrosAguaCruda
    aireacion: Optional[DiseñoAireacion] = None
    mezcla_rapida: DiseñoMezclaRapida
    floculacion: DiseñoFloculacion
    sedimentacion: DiseñoSedimentacion
    filtracion: DiseñoFiltracion
    desinfeccion: DiseñoDesinfeccion
    
    fecha_diseño: datetime = Field(default_factory=datetime.now)
    diseñador: Optional[str] = Field(None, max_length=200)
    observaciones: Optional[str] = Field(None, max_length=2000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "proyecto": {
                    "nombre": "PTAP Municipio Ejemplo",
                    "ubicacion": "Municipio Ejemplo, Departamento",
                    "poblacion_diseño": 10000,
                    "dotacion": 150,
                    "periodo_diseño": 25
                },
                "agua_cruda": {
                    "caudal": 50.0,
                    "temperatura": 18.0,
                    "turbiedad": 25.0,
                    "color": 40.0,
                    "ph": 7.2
                },
                "mezcla_rapida": {
                    "tipo": "resalto_hidraulico",
                    "gradiente_velocidad": 1000,
                    "tiempo_retencion": 30
                },
                "floculacion": {
                    "tipo": "pantallas",
                    "numero_camaras": 3,
                    "gradiente_velocidad": 50,
                    "tiempo_retencion": 1800
                },
                "sedimentacion": {
                    "tipo": "alta_tasa",
                    "carga_superficial": 25.0,
                    "tiempo_retencion": 10800,
                    "numero_modulos": 2
                },
                "filtracion": {
                    "tipo": "rapida_gravedad",
                    "tasa_filtracion": 240,
                    "numero_filtros": 2,
                    "espesor_lecho_arena": 0.7
                },
                "desinfeccion": {
                    "tipo": "cloro_gas",
                    "dosis_cloro": 2.5,
                    "tiempo_contacto": 1800,
                    "cloro_residual_objetivo": 0.5
                }
            }
        }
    
    def dict_para_calculo(self) -> dict:
        """Convierte el modelo a diccionario para módulos de cálculo"""
        return self.model_dump(exclude={'fecha_diseño', 'diseñador', 'observaciones'})
    
    def validar_contra_ras(self) -> dict:
        """Validación preliminar contra criterios RAS 2017"""
        errores = []
        advertencias = []
        
        # Validar mezcla rápida
        if not (700 <= self.mezcla_rapida.gradiente_velocidad <= 1500):
            errores.append("Gradiente mezcla rápida fuera de rango RAS (700-1500 s⁻¹)")
        
        # Validar floculación
        if not (20 <= self.floculacion.gradiente_velocidad <= 80):
            errores.append("Gradiente floculación fuera de rango RAS (20-80 s⁻¹)")
        
        # Validar sedimentación
        if not (10 <= self.sedimentacion.carga_superficial <= 40):
            errores.append("Carga superficial fuera de rango RAS (10-40 m³/m²/día)")
        
        # Validar filtración
        if not (120 <= self.filtracion.tasa_filtracion <= 360):
            errores.append("Tasa filtración fuera de rango RAS (120-360 m³/m²/día)")
        
        if self.filtracion.numero_filtros < 2:
            errores.append("RAS 2017 requiere mínimo 2 filtros")
        
        # Validar desinfección
        if self.desinfeccion.tiempo_contacto < 1800:
            advertencias.append("Tiempo de contacto < 30 min puede ser insuficiente")
        
        return {
            "valido": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias
        }
