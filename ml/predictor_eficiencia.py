"""
Predictor de eficiencia de remoción usando Machine Learning.

Este módulo utiliza Random Forest (scikit-learn) para predecir la eficiencia
de remoción de turbiedad basándose en parámetros operacionales.

Características:
- Entrenamiento con datos históricos o sintéticos
- Predicción de eficiencia de remoción
- Análisis de importancia de variables
- Exportación/importación de modelos entrenados
- Curvas de aprendizaje y validación cruzada
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class ResultadoEntrenamiento:
    """Resultados del entrenamiento del modelo"""
    r2_train: float
    r2_test: float
    mae_test: float
    rmse_test: float
    cv_scores: List[float]
    feature_importance: Dict[str, float]
    n_samples: int
    mensaje: str


class GeneradorDatosSinteticos:
    """
    Genera datos sintéticos realistas para entrenamiento.
    
    Útil cuando no hay suficientes datos históricos reales.
    Genera datos basados en modelos empíricos de tratamiento.
    """
    
    def __init__(self, seed: int = 42):
        """
        Args:
            seed: Semilla para reproducibilidad
        """
        np.random.seed(seed)
    
    def generar_dataset(
        self, 
        n_samples: int = 1000,
        incluir_ruido: bool = True
    ) -> pd.DataFrame:
        """
        Genera dataset sintético de operación de PTAP.
        
        Variables generadas:
        - turbiedad_entrada: 5-500 NTU
        - ph_entrada: 6.0-8.5
        - temperatura: 15-30°C
        - dosis_coagulante: 5-80 mg/L
        - gradiente_mezcla: 700-1500 s⁻¹
        - tiempo_mezcla: 10-60 s
        - gradiente_floculacion: 20-80 s⁻¹
        - tiempo_floculacion: 1200-2400 s
        - carga_superficial: 10-40 m³/m²/día
        - tasa_filtracion: 120-360 m³/m²/día
        - eficiencia_remocion: 0.5-0.99 (calculada empíricamente)
        
        Args:
            n_samples: Número de muestras a generar
            incluir_ruido: Si True, añade ruido aleatorio realista
            
        Returns:
            DataFrame con datos sintéticos
        """
        datos = {}
        
        # Variables de entrada (distribuciones realistas)
        datos['turbiedad_entrada'] = np.random.lognormal(3.5, 0.8, n_samples)
        datos['turbiedad_entrada'] = np.clip(datos['turbiedad_entrada'], 5, 500)
        
        datos['ph_entrada'] = np.random.normal(7.0, 0.5, n_samples)
        datos['ph_entrada'] = np.clip(datos['ph_entrada'], 6.0, 8.5)
        
        datos['temperatura'] = np.random.normal(22, 4, n_samples)
        datos['temperatura'] = np.clip(datos['temperatura'], 15, 30)
        
        datos['dosis_coagulante'] = np.random.uniform(5, 80, n_samples)
        datos['gradiente_mezcla'] = np.random.uniform(700, 1500, n_samples)
        datos['tiempo_mezcla'] = np.random.uniform(10, 60, n_samples)
        datos['gradiente_floculacion'] = np.random.uniform(20, 80, n_samples)
        datos['tiempo_floculacion'] = np.random.uniform(1200, 2400, n_samples)
        datos['carga_superficial'] = np.random.uniform(10, 40, n_samples)
        datos['tasa_filtracion'] = np.random.uniform(120, 360, n_samples)
        
        # Calcular eficiencia usando modelo empírico
        eficiencias = []
        for i in range(n_samples):
            ef = self._calcular_eficiencia_empirica(
                turbiedad=datos['turbiedad_entrada'][i],
                ph=datos['ph_entrada'][i],
                temp=datos['temperatura'][i],
                dosis_coag=datos['dosis_coagulante'][i],
                grad_mezcla=datos['gradiente_mezcla'][i],
                grad_floc=datos['gradiente_floculacion'][i],
                tiempo_floc=datos['tiempo_floculacion'][i],
                carga_sup=datos['carga_superficial'][i],
                tasa_filt=datos['tasa_filtracion'][i]
            )
            
            # Añadir ruido realista (±3-5%)
            if incluir_ruido:
                ruido = np.random.normal(0, 0.03)
                ef = np.clip(ef + ruido, 0.5, 0.99)
            
            eficiencias.append(ef)
        
        datos['eficiencia_remocion'] = eficiencias
        
        return pd.DataFrame(datos)
    
    def _calcular_eficiencia_empirica(
        self,
        turbiedad: float,
        ph: float,
        temp: float,
        dosis_coag: float,
        grad_mezcla: float,
        grad_floc: float,
        tiempo_floc: float,
        carga_sup: float,
        tasa_filt: float
    ) -> float:
        """
        Modelo empírico de eficiencia basado en literatura técnica.
        
        Referencias:
        - AWWA Water Quality & Treatment Handbook
        - RAS 2017 modelos de diseño
        """
        # Eficiencia coagulación (depende de dosis y pH)
        dosis_optima = 20 + (turbiedad / 10)  # Dosis óptima estimada
        factor_dosis = 1 - abs(dosis_coag - dosis_optima) / (dosis_optima + 20)
        factor_dosis = max(0.3, min(1.0, factor_dosis))
        
        factor_ph = 1.0 if 6.5 <= ph <= 7.5 else 0.8
        
        ef_coagulacion = 0.6 + 0.3 * factor_dosis * factor_ph
        
        # Eficiencia floculación (depende de gradiente y tiempo)
        gt = grad_floc * (tiempo_floc / 60)  # Número de Camp
        if 20000 <= gt <= 100000:
            ef_floculacion = 0.85
        elif gt < 20000:
            ef_floculacion = 0.65 + 0.20 * (gt / 20000)
        else:
            ef_floculacion = 0.85 - 0.15 * ((gt - 100000) / 50000)
        ef_floculacion = max(0.5, min(0.95, ef_floculacion))
        
        # Eficiencia sedimentación (depende de carga superficial)
        if carga_sup <= 25:
            ef_sedimentacion = 0.90
        else:
            ef_sedimentacion = 0.90 - 0.01 * (carga_sup - 25)
        ef_sedimentacion = max(0.60, min(0.95, ef_sedimentacion))
        
        # Eficiencia filtración (depende de tasa)
        if tasa_filt <= 200:
            ef_filtracion = 0.95
        else:
            ef_filtracion = 0.95 - 0.001 * (tasa_filt - 200)
        ef_filtracion = max(0.75, min(0.98, ef_filtracion))
        
        # Factor temperatura (cinética de reacción)
        factor_temp = 1.0 if 20 <= temp <= 25 else 0.95
        
        # Eficiencia global (producto de eficiencias parciales)
        eficiencia_total = (
            ef_coagulacion * 
            ef_floculacion * 
            ef_sedimentacion * 
            ef_filtracion * 
            factor_temp
        )
        
        return min(0.99, eficiencia_total)


class PredictorEficiencia:
    """
    Predictor de eficiencia de remoción usando Random Forest.
    
    Características:
    - Entrenamiento con validación cruzada
    - Análisis de importancia de variables
    - Curvas de aprendizaje
    - Persistencia de modelos
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = 20,
        min_samples_split: int = 5,
        random_state: int = 42
    ):
        """
        Args:
            n_estimators: Número de árboles en el bosque
            max_depth: Profundidad máxima de árboles
            min_samples_split: Mínimo de muestras para dividir nodo
            random_state: Semilla para reproducibilidad
        """
        self.modelo = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=random_state,
            n_jobs=-1  # Usar todos los cores disponibles
        )
        self.caracteristicas: List[str] = []
        self.scaler_params: Optional[Dict] = None
        self.entrenado: bool = False
    
    def entrenar(
        self,
        datos: pd.DataFrame,
        test_size: float = 0.2,
        cv_folds: int = 5
    ) -> ResultadoEntrenamiento:
        """
        Entrena el modelo con datos históricos.
        
        Args:
            datos: DataFrame con columnas de características y 'eficiencia_remocion'
            test_size: Fracción de datos para prueba (0.0-0.5)
            cv_folds: Número de folds para validación cruzada
            
        Returns:
            ResultadoEntrenamiento con métricas de desempeño
        """
        # Separar características y target
        target_col = 'eficiencia_remocion'
        if target_col not in datos.columns:
            raise ValueError(f"DataFrame debe contener columna '{target_col}'")
        
        self.caracteristicas = [col for col in datos.columns if col != target_col]
        
        X = datos[self.caracteristicas].values
        y = datos[target_col].values
        
        # Dividir train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Entrenar modelo
        self.modelo.fit(X_train, y_train)
        self.entrenado = True
        
        # Predecir
        y_pred_train = self.modelo.predict(X_train)
        y_pred_test = self.modelo.predict(X_test)
        
        # Métricas
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        # Validación cruzada
        cv_scores = cross_val_score(
            self.modelo, X, y, cv=cv_folds, scoring='r2'
        )
        
        # Importancia de características
        feature_importance = dict(zip(
            self.caracteristicas,
            self.modelo.feature_importances_
        ))
        feature_importance = dict(sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        # Mensaje de resultado
        if r2_test >= 0.85:
            mensaje = "✅ Excelente ajuste del modelo"
        elif r2_test >= 0.70:
            mensaje = "✓ Buen ajuste del modelo"
        elif r2_test >= 0.50:
            mensaje = "⚠ Ajuste moderado - considerar más datos"
        else:
            mensaje = "❌ Ajuste pobre - revisar datos o features"
        
        return ResultadoEntrenamiento(
            r2_train=r2_train,
            r2_test=r2_test,
            mae_test=mae_test,
            rmse_test=rmse_test,
            cv_scores=cv_scores.tolist(),
            feature_importance=feature_importance,
            n_samples=len(datos),
            mensaje=mensaje
        )
    
    def predecir(
        self,
        parametros: Dict[str, float]
    ) -> float:
        """
        Predice eficiencia para nuevos parámetros.
        
        Args:
            parametros: Dict con valores de características
                Ejemplo: {
                    'turbiedad_entrada': 45,
                    'dosis_coagulante': 30,
                    'gradiente_floculacion': 50,
                    ...
                }
        
        Returns:
            Eficiencia predicha (0.0-1.0)
        """
        if not self.entrenado:
            raise RuntimeError("Modelo no entrenado. Llamar entrenar() primero.")
        
        # Validar que todas las características estén presentes
        faltantes = set(self.caracteristicas) - set(parametros.keys())
        if faltantes:
            raise ValueError(f"Faltan características: {faltantes}")
        
        # Crear array en el orden correcto
        X = np.array([[parametros[feat] for feat in self.caracteristicas]])
        
        # Predecir
        eficiencia = self.modelo.predict(X)[0]
        
        # Clip a rango válido
        return float(np.clip(eficiencia, 0.0, 1.0))
    
    def predecir_lote(
        self,
        datos: pd.DataFrame
    ) -> np.ndarray:
        """
        Predice eficiencia para múltiples casos.
        
        Args:
            datos: DataFrame con columnas de características
        
        Returns:
            Array de eficiencias predichas
        """
        if not self.entrenado:
            raise RuntimeError("Modelo no entrenado.")
        
        X = datos[self.caracteristicas].values
        predicciones = self.modelo.predict(X)
        
        return np.clip(predicciones, 0.0, 1.0)
    
    def analizar_importancia(self) -> Dict[str, float]:
        """
        Retorna importancia de cada característica.
        
        Returns:
            Dict {característica: importancia} ordenado de mayor a menor
        """
        if not self.entrenado:
            raise RuntimeError("Modelo no entrenado.")
        
        importance = dict(zip(
            self.caracteristicas,
            self.modelo.feature_importances_
        ))
        
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    def curva_aprendizaje(
        self,
        X: np.ndarray,
        y: np.ndarray,
        train_sizes: np.ndarray = np.linspace(0.1, 1.0, 10)
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula curva de aprendizaje.
        
        Args:
            X: Matriz de características
            y: Vector de targets
            train_sizes: Fracciones de datos de entrenamiento
        
        Returns:
            (train_sizes, train_scores, val_scores)
        """
        train_sizes_abs, train_scores, val_scores = learning_curve(
            self.modelo,
            X, y,
            train_sizes=train_sizes,
            cv=5,
            scoring='r2',
            n_jobs=-1
        )
        
        return train_sizes_abs, train_scores, val_scores
    
    def guardar(self, directorio: str = 'ml/modelos') -> str:
        """
        Guarda modelo entrenado en disco.
        
        Args:
            directorio: Ruta donde guardar el modelo
        
        Returns:
            Ruta del archivo guardado
        """
        if not self.entrenado:
            raise RuntimeError("Modelo no entrenado.")
        
        ruta = Path(directorio)
        ruta.mkdir(parents=True, exist_ok=True)
        
        # Guardar modelo
        archivo_modelo = ruta / 'modelo_eficiencia.pkl'
        joblib.dump(self.modelo, archivo_modelo)
        
        # Guardar metadata
        metadata = {
            'caracteristicas': self.caracteristicas,
            'n_estimators': self.modelo.n_estimators,
            'max_depth': self.modelo.max_depth,
            'feature_importances': dict(zip(
                self.caracteristicas,
                [float(x) for x in self.modelo.feature_importances_]
            ))
        }
        archivo_meta = ruta / 'modelo_metadata.json'
        with open(archivo_meta, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return str(archivo_modelo)
    
    def cargar(self, directorio: str = 'ml/modelos') -> None:
        """
        Carga modelo desde disco.
        
        Args:
            directorio: Ruta donde está el modelo
        """
        ruta = Path(directorio)
        
        # Cargar modelo
        archivo_modelo = ruta / 'modelo_eficiencia.pkl'
        if not archivo_modelo.exists():
            raise FileNotFoundError(f"No existe {archivo_modelo}")
        
        self.modelo = joblib.load(archivo_modelo)
        
        # Cargar metadata
        archivo_meta = ruta / 'modelo_metadata.json'
        if archivo_meta.exists():
            with open(archivo_meta, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                self.caracteristicas = metadata['caracteristicas']
        
        self.entrenado = True
    
    def obtener_estadisticas(self) -> Dict:
        """
        Retorna estadísticas del modelo.
        
        Returns:
            Dict con información del modelo
        """
        if not self.entrenado:
            return {'entrenado': False}
        
        return {
            'entrenado': True,
            'n_estimators': self.modelo.n_estimators,
            'max_depth': self.modelo.max_depth,
            'n_features': len(self.caracteristicas),
            'caracteristicas': self.caracteristicas,
            'importancia_top3': dict(list(self.analizar_importancia().items())[:3])
        }
