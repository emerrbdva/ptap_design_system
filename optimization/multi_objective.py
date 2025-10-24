"""
Optimización Multiobjetivo para Diseño de PTAP
Minimiza costos mientras maximiza eficiencia y cumplimiento normativo
Utiliza scipy.optimize (100% gratuito y open source)
"""
import numpy as np
from scipy.optimize import minimize, differential_evolution, NonlinearConstraint
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass


@dataclass
class ResultadoOptimizacion:
    """Resultado de la optimización"""
    exito: bool
    parametros_optimos: Dict[str, float]
    costo_total: float
    eficiencia: float
    conformidad_ras: float
    num_iteraciones: int
    mensaje: str


class OptimizadorMultiobjetivo:
    """
    Optimizador multiobjetivo para diseño de PTAP
    Objetivos:
    1. Minimizar costos CAPEX + VPN(OPEX)
    2. Maximizar eficiencia de remoción
    3. Maximizar conformidad normativa
    """
    
    def __init__(self, estimador_costos, validador_ras):
        self.estimador_costos = estimador_costos
        self.validador_ras = validador_ras
        
        # Pesos para función objetivo ponderada
        self.peso_costo = 0.4
        self.peso_eficiencia = 0.3
        self.peso_conformidad = 0.3
    
    def optimizar_diseño(
        self, 
        parametros_fijos: Dict,
        variables_optimizar: List[str],
        metodo: str = 'differential_evolution'
    ) -> ResultadoOptimizacion:
        """
        Optimiza el diseño de la PTAP
        
        Args:
            parametros_fijos: Parámetros que no cambian (caudal, calidad agua cruda, etc.)
            variables_optimizar: Lista de variables a optimizar
            metodo: 'differential_evolution', 'slsqp', 'trust-constr'
        """
        
        # Definir límites para cada variable
        limites = self._definir_limites(variables_optimizar)
        
        # Punto inicial
        x0 = self._generar_punto_inicial(variables_optimizar, limites)
        
        # Función objetivo
        def objetivo(x):
            return self._funcion_objetivo(x, variables_optimizar, parametros_fijos)
        
        # Restricciones
        restricciones = self._definir_restricciones(variables_optimizar, parametros_fijos)
        
        # Ejecutar optimización
        if metodo == 'differential_evolution':
            resultado = differential_evolution(
                objetivo,
                bounds=limites,
                maxiter=100,
                popsize=15,
                tol=0.01,
                seed=42,
                workers=1
            )
        elif metodo == 'slsqp':
            resultado = minimize(
                objetivo,
                x0=x0,
                method='SLSQP',
                bounds=limites,
                constraints=restricciones,
                options={'maxiter': 200, 'ftol': 1e-6}
            )
        else:  # trust-constr
            resultado = minimize(
                objetivo,
                x0=x0,
                method='trust-constr',
                bounds=limites,
                constraints=restricciones,
                options={'maxiter': 200}
            )
        
        # Procesar resultado
        return self._procesar_resultado(resultado, variables_optimizar, parametros_fijos)
    
    def _definir_limites(self, variables: List[str]) -> List[Tuple[float, float]]:
        """Define límites para cada variable según RAS 2017"""
        limites_dict = {
            # Mezcla rápida
            'gradiente_mezcla_rapida': (700, 1500),  # s⁻¹
            'tiempo_mezcla_rapida': (10, 60),  # s
            'dosis_coagulante': (10, 100),  # mg/L
            
            # Floculación
            'gradiente_floculacion': (20, 80),  # s⁻¹
            'tiempo_floculacion': (1200, 2400),  # s
            'numero_camaras_floc': (2, 4),  # unidades
            
            # Sedimentación
            'carga_superficial': (10, 40),  # m³/m²/día
            'tiempo_sedimentacion': (7200, 14400),  # s
            
            # Filtración
            'tasa_filtracion': (120, 360),  # m³/m²/día
            'espesor_arena': (0.6, 0.8),  # m
            'numero_filtros': (2, 6),  # unidades
            
            # Desinfección
            'dosis_cloro': (0.5, 8.0),  # mg/L
            'tiempo_contacto': (1800, 3600),  # s
        }
        
        return [limites_dict[var] for var in variables]
    
    def _generar_punto_inicial(self, variables: List[str], limites: List[Tuple]) -> np.ndarray:
        """Genera punto inicial en el centro del espacio factible"""
        return np.array([(lim[0] + lim[1]) / 2 for lim in limites])
    
    def _funcion_objetivo(self, x: np.ndarray, variables: List[str], parametros_fijos: Dict) -> float:
        """
        Función objetivo multiobjetivo ponderada
        Retorna valor a minimizar (menor es mejor)
        """
        
        # Construir diseño completo
        diseño = parametros_fijos.copy()
        for i, var in enumerate(variables):
            diseño[var] = x[i]
        
        # Calcular costos (normalizado)
        try:
            analisis = self.estimador_costos.analisis_financiero_completo(diseño)
            vpn_total = analisis['vpn_total_25años']
            # Normalizar: costo típico 50 L/s ~ 2,000,000,000 COP
            costo_norm = vpn_total / 2e9
        except Exception:
            costo_norm = 10  # Penalización por error
        
        # Calcular eficiencia (estimada paramétricamente)
        eficiencia = self._estimar_eficiencia(diseño)
        # Convertir a objetivo de minimización (1 - eficiencia)
        eficiencia_obj = 1 - eficiencia
        
        # Calcular conformidad RAS
        conformidad = self._calcular_conformidad(diseño)
        # Convertir a objetivo de minimización (1 - conformidad)
        conformidad_obj = 1 - conformidad
        
        # Función objetivo ponderada
        f = (
            self.peso_costo * costo_norm +
            self.peso_eficiencia * eficiencia_obj +
            self.peso_conformidad * conformidad_obj
        )
        
        return f
    
    def _estimar_eficiencia(self, diseño: Dict) -> float:
        """
        Estima eficiencia global de remoción
        Basado en modelos empíricos
        """
        
        # Eficiencia de cada proceso (valores típicos)
        
        # Mezcla rápida + coagulación
        dosis_coag = diseño.get('dosis_coagulante', 25)
        grad_mezcla = diseño.get('gradiente_mezcla_rapida', 1000)
        ef_coag = min(0.95, 0.3 + (dosis_coag / 100) + (grad_mezcla - 700) / 3000)
        
        # Floculación
        grad_floc = diseño.get('gradiente_floculacion', 50)
        tiempo_floc = diseño.get('tiempo_floculacion', 1800)
        ef_floc = min(0.98, 0.7 + (grad_floc - 20) / 200 + (tiempo_floc - 1200) / 6000)
        
        # Sedimentación
        carga_sup = diseño.get('carga_superficial', 25)
        ef_sed = min(0.95, 1.1 - (carga_sup / 100))
        
        # Filtración
        tasa_filt = diseño.get('tasa_filtracion', 240)
        espesor_arena = diseño.get('espesor_arena', 0.7)
        ef_filt = min(0.99, 0.85 + espesor_arena * 0.1 - (tasa_filt - 120) / 1200)
        
        # Eficiencia global (serie)
        eficiencia_global = ef_coag * ef_floc * ef_sed * ef_filt
        
        return min(1.0, max(0.0, eficiencia_global))
    
    def _calcular_conformidad(self, diseño: Dict) -> float:
        """Calcula grado de conformidad con RAS 2017 (0 a 1)"""
        
        criterios_cumplidos = 0
        criterios_totales = 0
        
        # Verificar mezcla rápida
        grad_mr = diseño.get('gradiente_mezcla_rapida', 0)
        if 700 <= grad_mr <= 1500:
            criterios_cumplidos += 1
        criterios_totales += 1
        
        tiempo_mr = diseño.get('tiempo_mezcla_rapida', 0)
        if 10 <= tiempo_mr <= 60:
            criterios_cumplidos += 1
        criterios_totales += 1
        
        # Verificar floculación
        grad_floc = diseño.get('gradiente_floculacion', 0)
        if 20 <= grad_floc <= 80:
            criterios_cumplidos += 1
        criterios_totales += 1
        
        tiempo_floc = diseño.get('tiempo_floculacion', 0)
        if 1200 <= tiempo_floc <= 2400:
            criterios_cumplidos += 1
        criterios_totales += 1
        
        # Verificar sedimentación
        carga_sup = diseño.get('carga_superficial', 0)
        if 10 <= carga_sup <= 40:
            criterios_cumplidos += 1
        criterios_totales += 1
        
        # Verificar filtración
        tasa_filt = diseño.get('tasa_filtracion', 0)
        if 120 <= tasa_filt <= 360:
            criterios_cumplidos += 1
        criterios_totales += 1
        
        num_filtros = diseño.get('numero_filtros', 0)
        if num_filtros >= 2:
            criterios_cumplidos += 1
        criterios_totales += 1
        
        return criterios_cumplidos / criterios_totales if criterios_totales > 0 else 0
    
    def _definir_restricciones(self, variables: List[str], parametros_fijos: Dict) -> List:
        """Define restricciones adicionales"""
        restricciones = []
        
        # Restricción: número de filtros debe ser entero
        if 'numero_filtros' in variables:
            idx = variables.index('numero_filtros')
            
            def filtros_enteros(x):
                return np.abs(x[idx] - np.round(x[idx]))
            
            restricciones.append({
                'type': 'eq',
                'fun': filtros_enteros
            })
        
        # Restricción: número de cámaras floculación debe ser entero
        if 'numero_camaras_floc' in variables:
            idx = variables.index('numero_camaras_floc')
            
            def camaras_enteras(x):
                return np.abs(x[idx] - np.round(x[idx]))
            
            restricciones.append({
                'type': 'eq',
                'fun': camaras_enteras
            })
        
        return restricciones
    
    def _procesar_resultado(
        self, 
        resultado, 
        variables: List[str], 
        parametros_fijos: Dict
    ) -> ResultadoOptimizacion:
        """Procesa el resultado de la optimización"""
        
        # Extraer parámetros óptimos
        x_opt = resultado.x
        parametros_optimos = {var: x_opt[i] for i, var in enumerate(variables)}
        
        # Redondear enteros
        if 'numero_filtros' in parametros_optimos:
            parametros_optimos['numero_filtros'] = int(np.round(parametros_optimos['numero_filtros']))
        if 'numero_camaras_floc' in parametros_optimos:
            parametros_optimos['numero_camaras_floc'] = int(np.round(parametros_optimos['numero_camaras_floc']))
        
        # Diseño completo
        diseño_optimo = {**parametros_fijos, **parametros_optimos}
        
        # Calcular métricas
        try:
            analisis = self.estimador_costos.analisis_financiero_completo(diseño_optimo)
            costo_total = analisis['vpn_total_25años']
        except Exception:
            costo_total = float('inf')
        
        eficiencia = self._estimar_eficiencia(diseño_optimo)
        conformidad = self._calcular_conformidad(diseño_optimo)
        
        return ResultadoOptimizacion(
            exito=resultado.success if hasattr(resultado, 'success') else True,
            parametros_optimos=parametros_optimos,
            costo_total=costo_total,
            eficiencia=eficiencia,
            conformidad_ras=conformidad,
            num_iteraciones=resultado.nit if hasattr(resultado, 'nit') else resultado.nfev,
            mensaje=resultado.message if hasattr(resultado, 'message') else "Optimización completada"
        )
    
    def optimizacion_pareto(
        self, 
        parametros_fijos: Dict,
        variables_optimizar: List[str],
        num_puntos: int = 10
    ) -> List[ResultadoOptimizacion]:
        """
        Genera frontera de Pareto variando los pesos de los objetivos
        """
        
        resultados_pareto = []
        
        # Variar pesos entre costo y eficiencia
        for i in range(num_puntos):
            peso_costo_i = i / (num_puntos - 1)
            peso_eficiencia_i = 1 - peso_costo_i
            
            # Actualizar pesos
            self.peso_costo = peso_costo_i * 0.7
            self.peso_eficiencia = peso_eficiencia_i * 0.7
            self.peso_conformidad = 0.3  # Conformidad siempre importante
            
            # Optimizar
            resultado = self.optimizar_diseño(
                parametros_fijos,
                variables_optimizar,
                metodo='differential_evolution'
            )
            
            resultados_pareto.append(resultado)
        
        return resultados_pareto
    
    def analisis_sensibilidad(
        self, 
        diseño_base: Dict,
        variable: str,
        rango_variacion: Tuple[float, float],
        num_puntos: int = 20
    ) -> Dict:
        """
        Análisis de sensibilidad de una variable
        """
        
        valores = np.linspace(rango_variacion[0], rango_variacion[1], num_puntos)
        
        costos = []
        eficiencias = []
        conformidades = []
        
        for valor in valores:
            diseño_temp = diseño_base.copy()
            diseño_temp[variable] = valor
            
            try:
                analisis = self.estimador_costos.analisis_financiero_completo(diseño_temp)
                costo = analisis['vpn_total_25años']
            except Exception:
                costo = None
            
            eficiencia = self._estimar_eficiencia(diseño_temp)
            conformidad = self._calcular_conformidad(diseño_temp)
            
            costos.append(costo)
            eficiencias.append(eficiencia)
            conformidades.append(conformidad)
        
        return {
            'variable': variable,
            'valores': valores.tolist(),
            'costos': costos,
            'eficiencias': eficiencias,
            'conformidades': conformidades
        }
