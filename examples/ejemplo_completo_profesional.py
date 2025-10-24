"""
Ejemplo Completo: Sistema Profesional Mejorado
Demuestra:
1. Validación de entrada con Pydantic
2. Estimación de costos CAPEX/OPEX
3. Optimización multiobjetivo
4. Análisis de sensibilidad
"""
import sys
from pathlib import Path
import json

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from validation.schemas import (
    ParametrosProyecto,
    ParametrosAguaCruda,
    DiseñoMezclaRapida,
    DiseñoFloculacion,
    DiseñoSedimentacion,
    DiseñoFiltracion,
    DiseñoDesinfeccion,
    DiseñoCompleto
)
from economics.cost_estimator import EstimadorCostos
from optimization.multi_objective import OptimizadorMultiobjetivo
from compliance.ras_2017 import RAS2017Validator


def main():
    print("=" * 80)
    print("SISTEMA PROFESIONAL DE DISEÑO PTAP - VERSIÓN MEJORADA")
    print("Incluye: Validación Pydantic + Costos + Optimización")
    print("=" * 80)
    print()
    
    # ========================================================================
    # FASE 1: VALIDACIÓN DE ENTRADA CON PYDANTIC
    # ========================================================================
    print("FASE 1: Validación de Entrada con Pydantic")
    print("-" * 80)
    
    try:
        # Definir parámetros del proyecto
        proyecto = ParametrosProyecto(
            nombre="PTAP San José",
            ubicacion="San José del Guaviare, Guaviare",
            poblacion_diseño=15000,
            dotacion=150,
            periodo_diseño=25,
            latitud=2.5722,
            longitud=-72.6356,
            altitud=175
        )
        print(f"✓ Proyecto validado: {proyecto.nombre}")
        
        # Definir parámetros de agua cruda
        agua_cruda = ParametrosAguaCruda(
            caudal=50.0,
            temperatura=26.0,
            turbiedad=45.0,
            color=60.0,
            ph=7.0,
            alcalinidad=75.0,
            dureza=110.0,
            hierro=1.2,
            manganeso=0.25,
            coliformes_totales=8000
        )
        print(f"✓ Agua cruda validada: Q={agua_cruda.caudal} L/s, Turbiedad={agua_cruda.turbiedad} NTU")
        
        # Definir diseño preliminar
        mezcla = DiseñoMezclaRapida(
            tipo="resalto_hidraulico",
            gradiente_velocidad=1000,
            tiempo_retencion=30,
            dosis_coagulante=30.0,
            tipo_coagulante="sulfato_aluminio"
        )
        
        floculacion = DiseñoFloculacion(
            tipo="pantallas",
            numero_camaras=3,
            gradiente_velocidad=50,
            tiempo_retencion=1800
        )
        
        sedimentacion = DiseñoSedimentacion(
            tipo="alta_tasa",
            carga_superficial=25.0,
            tiempo_retencion=10800,
            numero_modulos=2
        )
        
        filtracion = DiseñoFiltracion(
            tipo="rapida_gravedad",
            tasa_filtracion=240,
            numero_filtros=3,
            espesor_lecho_arena=0.7
        )
        
        desinfeccion = DiseñoDesinfeccion(
            tipo="cloro_gas",
            dosis_cloro=2.5,
            tiempo_contacto=1800,
            cloro_residual_objetivo=0.6
        )
        
        # Crear diseño completo
        diseño_completo = DiseñoCompleto(
            proyecto=proyecto,
            agua_cruda=agua_cruda,
            mezcla_rapida=mezcla,
            floculacion=floculacion,
            sedimentacion=sedimentacion,
            filtracion=filtracion,
            desinfeccion=desinfeccion,
            diseñador="Ing. María González"
        )
        
        print("✓ Diseño completo validado correctamente")
        
        # Validar contra RAS preliminarmente
        validacion = diseño_completo.validar_contra_ras()
        print(f"\nValidación RAS preliminar:")
        print(f"  - Estado: {'✓ CONFORME' if validacion['valido'] else '✗ NO CONFORME'}")
        if validacion['errores']:
            for error in validacion['errores']:
                print(f"  - Error: {error}")
        if validacion['advertencias']:
            for adv in validacion['advertencias']:
                print(f"  - Advertencia: {adv}")
        
    except Exception as e:
        print(f"✗ Error en validación: {e}")
        return
    
    print()
    
    # ========================================================================
    # FASE 2: ESTIMACIÓN DE COSTOS
    # ========================================================================
    print("FASE 2: Estimación de Costos CAPEX y OPEX")
    print("-" * 80)
    
    try:
        estimador = EstimadorCostos()
        
        # Convertir diseño a diccionario para estimador
        diseño_dict = {
            'caudal': agua_cruda.caudal,
            'mezcla_rapida': {
                'dosis_coagulante': mezcla.dosis_coagulante
            },
            'filtracion': {
                'area_filtracion': 25.0  # Estimado
            },
            'desinfeccion': {
                'dosis_cloro': desinfeccion.dosis_cloro
            }
        }
        
        # Estimar CAPEX
        capex = estimador.estimar_capex(diseño_dict)
        print(f"\n💰 CAPEX (Costos de Inversión):")
        print(f"  - Obra Civil: ${capex['obra_civil']['total']:,.0f} COP")
        print(f"  - Equipos: ${capex['equipos']['total']:,.0f} COP")
        print(f"  - Tuberías: ${capex['tuberias']['total']:,.0f} COP")
        print(f"  - Medios Filtrantes: ${capex['medios_filtrantes']['total']:,.0f} COP")
        print(f"  - Subtotal Directo: ${capex['subtotal_directo']:,.0f} COP")
        print(f"  - Costos Indirectos (25%): ${capex['costos_indirectos']:,.0f} COP")
        print(f"  - Imprevistos (10%): ${capex['imprevistos']:,.0f} COP")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  - TOTAL CAPEX: ${capex['total_capex']:,.0f} COP")
        print(f"  - Costo Unitario: ${capex['costo_unitario_ls']:,.0f} COP/(L/s)")
        
        # Estimar OPEX
        caudal_m3_dia = agua_cruda.caudal * 86.4
        opex = estimador.estimar_opex(diseño_dict, caudal_m3_dia)
        print(f"\n💵 OPEX (Costos de Operación Anuales):")
        print(f"  - Químicos: ${opex['quimicos']['total_anual']:,.0f} COP/año")
        print(f"    * Coagulante: {opex['quimicos']['coagulante']['cantidad_anual']:.0f} kg/año")
        print(f"    * Cloro: {opex['quimicos']['cloro']['cantidad_anual']:.0f} kg/año")
        print(f"  - Energía: ${opex['energia']['total_anual']:,.0f} COP/año")
        print(f"    * Consumo: {opex['energia']['consumo_anual']['cantidad']:.0f} kWh/año")
        print(f"  - Personal: ${opex['personal']['total_anual']:,.0f} COP/año")
        print(f"    * Operadores: {opex['personal']['operadores']['cantidad']}")
        print(f"    * Supervisores: {opex['personal']['supervisores']['cantidad']}")
        print(f"  - Mantenimiento: ${opex['mantenimiento']['costo_anual']:,.0f} COP/año")
        print(f"  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  - TOTAL OPEX: ${opex['total_opex_anual']:,.0f} COP/año")
        print(f"  - Costo por m³: ${opex['costo_por_m3']:.0f} COP/m³")
        
        # Análisis financiero completo
        analisis = estimador.analisis_financiero_completo(diseño_dict, tasa_descuento=0.08)
        print(f"\n📊 Análisis Financiero (Horizonte 25 años, 8% descuento):")
        print(f"  - VPN OPEX: ${analisis['vpn_opex_25años']:,.0f} COP")
        print(f"  - VPN Total: ${analisis['vpn_total_25años']:,.0f} COP")
        print(f"  - Costo Nivelado: ${analisis['costo_nivelado_m3']:.0f} COP/m³")
        
    except Exception as e:
        print(f"✗ Error en estimación de costos: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # ========================================================================
    # FASE 3: OPTIMIZACIÓN MULTIOBJETIVO
    # ========================================================================
    print("FASE 3: Optimización Multiobjetivo")
    print("-" * 80)
    
    try:
        # Crear validador RAS para optimización
        validador_ras = RAS2017Validator()
        
        # Inicializar optimizador
        optimizador = OptimizadorMultiobjetivo(estimador, validador_ras)
        
        # Parámetros fijos
        parametros_fijos = {
            'caudal': agua_cruda.caudal,
            'numero_filtros': 3,  # Fijo para simplificar
        }
        
        # Variables a optimizar
        variables = [
            'gradiente_mezcla_rapida',
            'dosis_coagulante',
            'gradiente_floculacion',
            'tiempo_floculacion',
            'carga_superficial',
            'tasa_filtracion',
            'dosis_cloro'
        ]
        
        print("Optimizando diseño (esto puede tomar 1-2 minutos)...")
        print(f"Variables a optimizar: {len(variables)}")
        print(f"Método: Evolución Diferencial")
        
        # Ejecutar optimización
        resultado = optimizador.optimizar_diseño(
            parametros_fijos=parametros_fijos,
            variables_optimizar=variables,
            metodo='differential_evolution'
        )
        
        print(f"\n✓ Optimización completada")
        print(f"  - Éxito: {resultado.exito}")
        print(f"  - Iteraciones: {resultado.num_iteraciones}")
        print(f"  - Mensaje: {resultado.mensaje}")
        
        print(f"\n📈 Resultados Óptimos:")
        print(f"  - Costo Total (VPN 25 años): ${resultado.costo_total:,.0f} COP")
        print(f"  - Eficiencia estimada: {resultado.eficiencia * 100:.1f}%")
        print(f"  - Conformidad RAS: {resultado.conformidad_ras * 100:.1f}%")
        
        print(f"\n🎯 Parámetros Óptimos:")
        for var, valor in resultado.parametros_optimos.items():
            print(f"  - {var}: {valor:.2f}")
        
        # Análisis de sensibilidad de una variable clave
        print(f"\n📉 Análisis de Sensibilidad: dosis_coagulante")
        diseño_base = {**parametros_fijos, **resultado.parametros_optimos}
        
        sensibilidad = optimizador.analisis_sensibilidad(
            diseño_base=diseño_base,
            variable='dosis_coagulante',
            rango_variacion=(10, 80),
            num_puntos=10
        )
        
        print(f"  Dosis (mg/L) | Eficiencia | Conformidad")
        print(f"  " + "-" * 45)
        for i in range(len(sensibilidad['valores'])):
            dosis = sensibilidad['valores'][i]
            efic = sensibilidad['eficiencias'][i]
            conf = sensibilidad['conformidades'][i]
            print(f"  {dosis:10.1f} | {efic*100:9.1f}% | {conf*100:10.1f}%")
        
    except Exception as e:
        print(f"✗ Error en optimización: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # ========================================================================
    # FASE 4: EXPORTAR RESULTADOS
    # ========================================================================
    print("FASE 4: Exportando Resultados")
    print("-" * 80)
    
    try:
        output_dir = Path(__file__).parent.parent / "data" / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Exportar diseño completo
        diseño_export = diseño_completo.model_dump()
        archivo_diseño = output_dir / "diseño_completo_profesional.json"
        with open(archivo_diseño, 'w', encoding='utf-8') as f:
            json.dump(diseño_export, f, indent=2, ensure_ascii=False, default=str)
        print(f"✓ Diseño exportado: {archivo_diseño}")
        
        # Exportar análisis de costos
        archivo_costos = output_dir / "analisis_costos.json"
        with open(archivo_costos, 'w', encoding='utf-8') as f:
            json.dump({
                'capex': capex,
                'opex': opex,
                'analisis_financiero': analisis
            }, f, indent=2, ensure_ascii=False)
        print(f"✓ Costos exportados: {archivo_costos}")
        
        # Exportar resultados de optimización
        archivo_optimizacion = output_dir / "resultados_optimizacion.json"
        with open(archivo_optimizacion, 'w', encoding='utf-8') as f:
            json.dump({
                'exito': resultado.exito,
                'parametros_optimos': resultado.parametros_optimos,
                'costo_total': resultado.costo_total,
                'eficiencia': resultado.eficiencia,
                'conformidad_ras': resultado.conformidad_ras,
                'num_iteraciones': resultado.num_iteraciones,
                'sensibilidad_coagulante': sensibilidad
            }, f, indent=2, ensure_ascii=False)
        print(f"✓ Optimización exportada: {archivo_optimizacion}")
        
    except Exception as e:
        print(f"✗ Error exportando: {e}")
    
    print()
    print("=" * 80)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)


if __name__ == "__main__":
    main()
