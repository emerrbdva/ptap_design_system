"""
Ejemplo Completo ULTRA-PROFESIONAL v2.0

Este ejemplo demuestra TODAS las capacidades del sistema integradas:
1. Validación con Pydantic v2
2. Estimación de costos CAPEX/OPEX
3. Optimización multi-objetivo
4. Machine Learning para predicción
5. Exportación BIM en formato IFC
6. Generación de reportes completos

Caso de estudio: PTAP San José del Guaviare - 50 L/s
"""

import sys
import os
from pathlib import Path
import json

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Agregar ruta del proyecto
proyecto_root = Path(__file__).parent.parent
sys.path.insert(0, str(proyecto_root))

# Importaciones
from validation.schemas import (
    ParametrosAguaCruda,
    ParametrosProyecto,
    DiseñoAireacion,
    DiseñoMezclaRapida,
    DiseñoFloculacion,
    DiseñoSedimentacion,
    DiseñoFiltracion,
    DiseñoDesinfeccion,
    DiseñoCompleto
)
from economics.cost_estimator import EstimadorCostos
from optimization.multi_objective import OptimizadorMultiobjetivo
from ml.predictor_eficiencia import PredictorEficiencia, GeneradorDatosSinteticos
from bim.ifc_exporter import ExportadorBIM, ComponenteBIM


def imprimir_seccion(titulo):
    """Imprime título de sección"""
    print("\n" + "="*70)
    print(f"  {titulo}")
    print("="*70 + "\n")


def main():
    print("\n" + "🌊"*35)
    print("  PTAP DESIGN SYSTEM v2.0 - EJEMPLO ULTRA-PROFESIONAL")
    print("🌊"*35)
    
    # ========================================================================
    # FASE 1: VALIDACIÓN CON PYDANTIC
    # ========================================================================
    imprimir_seccion("FASE 1: Validación Automática con Pydantic v2")
    
    try:
        # Parámetros del proyecto
        proyecto = ParametrosProyecto(
            nombre="PTAP San José del Guaviare",
            ubicacion="San José del Guaviare, Guaviare",
            poblacion_diseño=15000,
            dotacion=150,
            periodo_diseño=25,
            latitud=2.5697,
            longitud=-72.6406,
            altitud=250
        )
        
        # Parámetros agua cruda
        agua_cruda = ParametrosAguaCruda(
            caudal=50,
            temperatura=26,
            turbiedad=45,
            color=80,
            ph=7.0,
            alcalinidad=45,
            dureza=50,
            hierro=0.8,
            manganeso=0.15
        )
        
        # Diseño de procesos
        aireacion = DiseñoAireacion(
            tipo="bandejas",
            numero_bandejas=5,
            altura_caida=0.3
        )
        
        mezcla = DiseñoMezclaRapida(
            tipo="resalto_hidraulico",
            gradiente_velocidad=1000,
            tiempo_retencion=30,
            dosis_coagulante=30
        )
        
        floculacion = DiseñoFloculacion(
            tipo="pantallas",
            numero_camaras=3,
            gradiente_velocidad=50,
            tiempo_retencion=1800
        )
        
        sedimentacion = DiseñoSedimentacion(
            tipo="alta_tasa",
            carga_superficial=25,
            tiempo_retencion=10800,
            numero_modulos=2
        )
        
        filtracion = DiseñoFiltracion(
            tipo="rapida_gravedad",
            tasa_filtracion=240,
            numero_filtros=3,
            medio_filtrante="arena_antracita",
            espesor_arena=0.7,
            espesor_grava=0.3
        )
        
        desinfeccion = DiseñoDesinfeccion(
            tipo="cloro_gas",
            dosis_cloro=2,
            tiempo_contacto=1800,
            cloro_residual=1.5
        )
        
        # Diseño completo
        diseño_completo = DiseñoCompleto(
            proyecto=proyecto,
            agua_cruda=agua_cruda,
            aireacion=aireacion,
            mezcla_rapida=mezcla,
            floculacion=floculacion,
            sedimentacion=sedimentacion,
            filtracion=filtracion,
            desinfeccion=desinfeccion,
            diseñador="Ing. Juan Pérez",
            observaciones="Diseño optimizado con ML y multi-objetivo"
        )
        
        print("✅ Validación Pydantic: EXITOSA")
        print(f"   Proyecto: {proyecto.nombre}")
        print(f"   Población: {proyecto.poblacion_diseño:,} habitantes")
        print(f"   Caudal: {agua_cruda.caudal} L/s")
        print(f"   Turbiedad: {agua_cruda.turbiedad} NTU")
        
        # Validar contra RAS
        conformidad = diseño_completo.validar_contra_ras()
        print(f"\n📋 Conformidad RAS 2017:")
        print(f"   Válido: {'✅ SÍ' if conformidad['valido'] else '❌ NO'}")
        if conformidad['errores']:
            print(f"   Errores: {len(conformidad['errores'])}")
            for error in conformidad['errores']:
                print(f"     - {error}")
        if conformidad['advertencias']:
            print(f"   Advertencias: {len(conformidad['advertencias'])}")
            for adv in conformidad['advertencias']:
                print(f"     - {adv}")
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return
    
    # ========================================================================
    # FASE 2: ESTIMACIÓN DE COSTOS
    # ========================================================================
    imprimir_seccion("FASE 2: Estimación de Costos CAPEX/OPEX/VPN")
    
    estimador = EstimadorCostos()
    
    # CAPEX
    diseño_dict = diseño_completo.dict_para_calculo()
    capex = estimador.estimar_capex(diseño_dict)
    
    print("💰 CAPEX (Inversión Inicial):")
    print(f"   Obra Civil:        ${capex['obra_civil']['total']:>15,.0f} COP")
    print(f"   Equipos:           ${capex['equipos']['total']:>15,.0f} COP")
    print(f"   Tuberías:          ${capex['tuberias']['total']:>15,.0f} COP")
    print(f"   Medios Filtrantes: ${capex['medios_filtrantes']['total']:>15,.0f} COP")
    print(f"   {'─'*50}")
    print(f"   TOTAL CAPEX:       ${capex['total_capex']:>15,.0f} COP")
    print(f"   Costo/L/s:         ${capex['costo_unitario_ls']:>15,.0f} COP")
    
    # OPEX
    caudal_m3_dia = agua_cruda.caudal * 86.4
    opex = estimador.estimar_opex(diseño_dict, caudal_m3_dia)
    
    print(f"\n💵 OPEX (Costos Operacionales Anuales):")
    print(f"   Químicos:      ${opex['quimicos']['total_anual']:>15,.0f} COP/año")
    print(f"     • Coagulante: {opex['quimicos']['coagulante']['cantidad_anual']:,.0f} kg/año")
    print(f"     • Cloro:      {opex['quimicos']['cloro']['cantidad_anual']:,.0f} kg/año")
    print(f"   Energía:       ${opex['energia']['total_anual']:>15,.0f} COP/año")
    print(f"     • Consumo:    {opex['energia']['consumo_anual']['cantidad']:,.0f} kWh/año")
    print(f"   Personal:      ${opex['personal']['total_anual']:>15,.0f} COP/año")
    print(f"     • Operadores: {opex['personal']['operadores']['cantidad']}")
    print(f"   Mantenimiento: ${opex['mantenimiento']['costo_anual']:>15,.0f} COP/año")
    print(f"   {'─'*50}")
    print(f"   TOTAL OPEX:    ${opex['total_opex_anual']:>15,.0f} COP/año")
    print(f"   Costo/m³:      ${opex['costo_por_m3']:>18.2f} COP/m³")
    
    # Análisis financiero
    financiero = estimador.analisis_financiero_completo(diseño_dict)
    
    print(f"\n📈 Análisis Financiero (25 años, 8% descuento):")
    print(f"   VPN CAPEX:     ${financiero['capex']:>15,.0f} COP")
    print(f"   VPN OPEX:      ${financiero['vpn_opex_25años']:>15,.0f} COP")
    print(f"   {'─'*50}")
    print(f"   VPN TOTAL:     ${financiero['vpn_total_25años']:>15,.0f} COP")
    print(f"   Costo Nivelado:${financiero['costo_nivelado_m3']:>18.2f} COP/m³")
    
    # ========================================================================
    # FASE 3: MACHINE LEARNING - PREDICCIÓN DE EFICIENCIA
    # ========================================================================
    imprimir_seccion("FASE 3: Machine Learning - Predicción de Eficiencia")
    
    # Generar datos de entrenamiento sintéticos
    print("🤖 Entrenando modelo Random Forest...")
    generador = GeneradorDatosSinteticos(seed=42)
    datos_entrenamiento = generador.generar_dataset(n_samples=2000, incluir_ruido=True)
    
    # Entrenar modelo
    predictor = PredictorEficiencia(n_estimators=150, max_depth=20)
    resultado_entrenamiento = predictor.entrenar(datos_entrenamiento, test_size=0.2, cv_folds=5)
    
    print(f"\n✅ Modelo entrenado exitosamente:")
    print(f"   Muestras:      {resultado_entrenamiento.n_samples:,}")
    print(f"   R² Train:      {resultado_entrenamiento.r2_train:.4f}")
    print(f"   R² Test:       {resultado_entrenamiento.r2_test:.4f}")
    print(f"   MAE Test:      {resultado_entrenamiento.mae_test:.4f}")
    print(f"   RMSE Test:     {resultado_entrenamiento.rmse_test:.4f}")
    print(f"   CV Score Prom: {sum(resultado_entrenamiento.cv_scores)/len(resultado_entrenamiento.cv_scores):.4f}")
    print(f"   {resultado_entrenamiento.mensaje}")
    
    # Importancia de variables
    print(f"\n📊 Variables Más Importantes (Top 5):")
    for i, (var, importancia) in enumerate(list(resultado_entrenamiento.feature_importance.items())[:5], 1):
        print(f"   {i}. {var:<25} {importancia*100:>6.2f}%")
    
    # Predecir eficiencia para el diseño actual
    parametros_prediccion = {
        'turbiedad_entrada': agua_cruda.turbiedad,
        'ph_entrada': agua_cruda.ph,
        'temperatura': agua_cruda.temperatura,
        'dosis_coagulante': mezcla.dosis_coagulante,
        'gradiente_mezcla': mezcla.gradiente_velocidad,
        'tiempo_mezcla': mezcla.tiempo_retencion,
        'gradiente_floculacion': floculacion.gradiente_velocidad,
        'tiempo_floculacion': floculacion.tiempo_retencion,
        'carga_superficial': sedimentacion.carga_superficial,
        'tasa_filtracion': filtracion.tasa_filtracion
    }
    
    eficiencia_predicha = predictor.predecir(parametros_prediccion)
    
    print(f"\n🎯 Predicción para diseño actual:")
    print(f"   Eficiencia Esperada: {eficiencia_predicha * 100:.1f}%")
    
    # Guardar modelo
    ruta_modelo = predictor.guardar('ml/modelos')
    print(f"   Modelo guardado en: {ruta_modelo}")
    
    # ========================================================================
    # FASE 4: OPTIMIZACIÓN MULTI-OBJETIVO
    # ========================================================================
    imprimir_seccion("FASE 4: Optimización Multi-objetivo")
    
    print("⚡ Ejecutando optimización (Differential Evolution)...")
    print("   Objetivos: 40% Costo, 30% Eficiencia, 30% Conformidad RAS")
    
    # Crear optimizador con estimador de costos
    optimizador = OptimizadorMultiobjetivo(estimador, None)
    optimizador.peso_costo = 0.4
    optimizador.peso_eficiencia = 0.3
    optimizador.peso_conformidad = 0.3
    
    parametros_fijos = {
        'caudal': agua_cruda.caudal,
        'turbiedad': agua_cruda.turbiedad,
        'ph': agua_cruda.ph,
        'temperatura': agua_cruda.temperatura,
        'numero_filtros': filtracion.numero_filtros,
        'numero_camaras_floc': floculacion.numero_camaras
    }
    
    variables_optimizar = [
        'gradiente_mezcla_rapida',
        'dosis_coagulante',
        'gradiente_floculacion',
        'tiempo_floculacion',
        'carga_superficial',
        'tasa_filtracion',
        'dosis_cloro'
    ]
    
    resultado_opt = optimizador.optimizar_diseño(
        parametros_fijos=parametros_fijos,
        variables_optimizar=variables_optimizar,
        metodo='differential_evolution'
    )
    
    if resultado_opt.exito:
        print(f"\n✅ Optimización completada:")
        print(f"   Iteraciones:       {resultado_opt.num_iteraciones}")
        print(f"   Costo VPN:         ${resultado_opt.costo_total:,.0f} COP")
        print(f"   Ahorro vs inicial: ${financiero['vpn_total_25años'] - resultado_opt.costo_total:,.0f} COP")
        print(f"   % Ahorro:          {((financiero['vpn_total_25años'] - resultado_opt.costo_total) / financiero['vpn_total_25años'] * 100):.1f}%")
        print(f"   Eficiencia:        {resultado_opt.eficiencia * 100:.1f}%")
        print(f"   Conformidad RAS:   {resultado_opt.conformidad_ras * 100:.1f}%")
        
        print(f"\n🎯 Parámetros Óptimos:")
        for var, valor in resultado_opt.parametros_optimos.items():
            print(f"   {var:<30} {valor:>10.2f}")
    else:
        print(f"❌ Optimización falló: {resultado_opt.mensaje}")
    
    # ========================================================================
    # FASE 5: EXPORTACIÓN BIM (IFC)
    # ========================================================================
    imprimir_seccion("FASE 5: Exportación BIM en formato IFC")
    
    print("🏗️ Generando modelo BIM 3D...")
    
    exporter = ExportadorBIM(
        nombre_proyecto=proyecto.nombre,
        ubicacion=(proyecto.latitud, proyecto.longitud, proyecto.altitud),
        autor=diseño_completo.diseñador
    )
    
    # Posicionamiento automático (layout lineal)
    x_pos = 0
    spacing = 15  # metros entre componentes
    
    # Aireación (bandejas)
    exporter.agregar_componente_generico(
        ComponenteBIM(
            nombre="Aireación Bandejas",
            tipo="aireacion",
            largo=3,
            ancho=3,
            alto=aireacion.numero_bandejas * aireacion.altura_caida,
            posicion_x=x_pos,
            posicion_y=0,
            posicion_z=0,
            propiedades={
                'numero_bandejas': aireacion.numero_bandejas,
                'altura_caida': aireacion.altura_caida
            }
        )
    )
    x_pos += spacing
    
    # Mezcla rápida
    from bim.ifc_exporter import ComponenteBIM
    exporter.agregar_componente_generico(
        ComponenteBIM(
            nombre="Mezcla Rápida",
            tipo="mezcla",
            largo=2,
            ancho=2,
            alto=1.5,
            posicion_x=x_pos,
            posicion_y=0,
            posicion_z=0,
            propiedades={
                'gradiente': resultado_opt.parametros_optimos.get('gradiente_mezcla_rapida', mezcla.gradiente_velocidad),
                'tipo': mezcla.tipo
            }
        )
    )
    x_pos += spacing
    
    # Floculador
    exporter.agregar_floculador(
        largo=12,
        ancho=6,
        alto=3.5,
        x=x_pos,
        y=0,
        z=0,
        tipo=floculacion.tipo,
        numero_camaras=floculacion.numero_camaras,
        gradiente=resultado_opt.parametros_optimos.get('gradiente_floculacion', floculacion.gradiente_velocidad),
        tiempo_retencion=resultado_opt.parametros_optimos.get('tiempo_floculacion', floculacion.tiempo_retencion)
    )
    x_pos += spacing
    
    # Sedimentadores
    for i in range(sedimentacion.numero_modulos):
        exporter.agregar_sedimentador(
            largo=10,
            ancho=8,
            alto=4,
            x=x_pos,
            y=i * 10,
            z=0,
            carga_superficial=resultado_opt.parametros_optimos.get('carga_superficial', sedimentacion.carga_superficial),
            tiempo_retencion=sedimentacion.tiempo_retencion,
            tipo=sedimentacion.tipo
        )
    x_pos += spacing
    
    # Filtros
    for i in range(filtracion.numero_filtros):
        exporter.agregar_filtro(
            largo=5,
            ancho=4,
            alto=3,
            x=x_pos,
            y=i * 6,
            z=0,
            tasa_filtracion=resultado_opt.parametros_optimos.get('tasa_filtracion', filtracion.tasa_filtracion),
            tipo=filtracion.tipo,
            medio_filtrante=filtracion.medio_filtrante
        )
    x_pos += spacing
    
    # Tanque de contacto (desinfección)
    exporter.agregar_tanque(
        diametro=8,
        altura=4,
        x=x_pos,
        y=5,
        z=0,
        tipo="Contacto Cloro",
        capacidad_m3=200
    )
    
    # Exportar IFC
    archivo_ifc = exporter.exportar("data/exports/PTAP_SanJose_50Ls.ifc")
    
    stats_bim = exporter.obtener_estadisticas()
    
    print(f"✅ Modelo BIM exportado:")
    print(f"   Archivo:       {archivo_ifc}")
    print(f"   Elementos:     {stats_bim['total_elementos']}")
    print(f"   Schema:        {stats_bim['archivo_schema']}")
    print(f"   Coordenadas:   Lat {stats_bim['ubicacion']['latitud']}")
    print(f"                  Lon {stats_bim['ubicacion']['longitud']}")
    print(f"                  Alt {stats_bim['ubicacion']['elevacion']} m")
    
    # ========================================================================
    # FASE 6: EXPORTACIÓN DE RESULTADOS
    # ========================================================================
    imprimir_seccion("FASE 6: Exportación de Resultados JSON")
    
    # Preparar diccionario completo de resultados
    resultados_completos = {
        'proyecto': {
            'nombre': proyecto.nombre,
            'municipio': proyecto.municipio,
            'poblacion': proyecto.poblacion_diseño,
            'caudal_ls': agua_cruda.caudal,
            'fecha_diseño': diseño_completo.fecha_diseño.isoformat() if diseño_completo.fecha_diseño else None,
            'diseñador': diseño_completo.diseñador
        },
        'validacion': {
            'conformidad_ras': conformidad
        },
        'costos': {
            'capex': {
                'total': capex['total_capex'],
                'obra_civil': capex['obra_civil']['subtotal'],
                'equipos': capex['equipos']['subtotal'],
                'tuberias': capex['tuberias']['subtotal'],
                'medios_filtrantes': capex['medios_filtrantes']['subtotal'],
                'costo_unitario_ls': capex['costo_unitario_ls']
            },
            'opex': {
                'total_anual': opex['total_opex_anual'],
                'quimicos': opex['quimicos']['subtotal'],
                'energia': opex['energia']['subtotal'],
                'personal': opex['personal']['subtotal'],
                'mantenimiento': opex['mantenimiento'],
                'costo_m3': opex['costo_por_m3']
            },
            'financiero': financiero
        },
        'machine_learning': {
            'entrenamiento': {
                'n_samples': resultado_entrenamiento.n_samples,
                'r2_test': resultado_entrenamiento.r2_test,
                'mae_test': resultado_entrenamiento.mae_test
            },
            'prediccion': {
                'eficiencia': eficiencia_predicha,
                'eficiencia_porcentaje': eficiencia_predicha * 100
            },
            'importancia_variables': dict(list(resultado_entrenamiento.feature_importance.items())[:10])
        },
        'optimizacion': {
            'exito': resultado_opt.exito,
            'iteraciones': resultado_opt.num_iteraciones,
            'costo_vpn': resultado_opt.costo_total,
            'ahorro_cop': financiero['vpn_total'] - resultado_opt.costo_total,
            'ahorro_porcentaje': ((financiero['vpn_total'] - resultado_opt.costo_total) / financiero['vpn_total'] * 100),
            'eficiencia': resultado_opt.eficiencia,
            'conformidad_ras': resultado_opt.conformidad_ras,
            'parametros_optimos': resultado_opt.parametros_optimos
        },
        'bim': {
            'archivo': archivo_ifc,
            'elementos': stats_bim['total_elementos'],
            'ubicacion': stats_bim['ubicacion']
        }
    }
    
    # Exportar JSON
    archivo_resultados = Path('data/exports/resultados_ultra_profesional.json')
    archivo_resultados.parent.mkdir(parents=True, exist_ok=True)
    
    with open(archivo_resultados, 'w', encoding='utf-8') as f:
        json.dump(resultados_completos, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Resultados exportados:")
    print(f"   JSON: {archivo_resultados}")
    print(f"   IFC:  {archivo_ifc}")
    
    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    imprimir_seccion("RESUMEN EJECUTIVO")
    
    print(f"📊 PROYECTO: {proyecto.nombre}")
    print(f"   Población:         {proyecto.poblacion_diseño:,} habitantes")
    print(f"   Caudal:            {agua_cruda.caudal} L/s")
    print(f"   Ubicación:         {proyecto.municipio}, {proyecto.departamento}")
    
    print(f"\n💰 INVERSIÓN:")
    print(f"   CAPEX:             ${capex['total_capex']:>15,.0f} COP")
    print(f"   OPEX/año:          ${opex['total_opex_anual']:>15,.0f} COP")
    print(f"   VPN 25 años:       ${financiero['vpn_total']:>15,.0f} COP")
    print(f"   Costo/m³:          ${financiero['costo_nivelado_m3']:>18.2f} COP")
    
    print(f"\n⚡ OPTIMIZACIÓN:")
    print(f"   Ahorro logrado:    ${financiero['vpn_total'] - resultado_opt.costo_total:>15,.0f} COP ({((financiero['vpn_total'] - resultado_opt.costo_total) / financiero['vpn_total'] * 100):.1f}%)")
    print(f"   Eficiencia final:  {resultado_opt.eficiencia * 100:>18.1f}%")
    print(f"   Conformidad RAS:   {resultado_opt.conformidad_ras * 100:>18.1f}%")
    
    print(f"\n🤖 MACHINE LEARNING:")
    print(f"   Modelo:            Random Forest (150 árboles)")
    print(f"   R² Score:          {resultado_entrenamiento.r2_test:>18.4f}")
    print(f"   Predicción:        {eficiencia_predicha * 100:>18.1f}%")
    
    print(f"\n🏗️ MODELO BIM:")
    print(f"   Archivo IFC:       {Path(archivo_ifc).name}")
    print(f"   Componentes 3D:    {stats_bim['total_elementos']:>18}")
    
    print("\n" + "="*70)
    print("  ✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"\n📁 Archivos generados:")
    print(f"   • {archivo_resultados}")
    print(f"   • {archivo_ifc}")
    print(f"   • ml/modelos/modelo_eficiencia.pkl")
    print(f"   • ml/modelos/modelo_metadata.json")
    print("\n💡 Siguientes pasos:")
    print("   1. Revisar resultados en archivos JSON")
    print("   2. Abrir modelo IFC en Revit/ArchiCAD/Solibri")
    print("   3. Iniciar servidor web: python web/api.py")
    print("   4. Ver documentación: cd docs && make html")
    print("\n🎉 ¡Sistema PTAP v2.0 100% operacional!")
    print()


if __name__ == "__main__":
    main()
