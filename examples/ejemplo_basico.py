"""
Ejemplo Básico de Uso del Sistema PTAP

Este script demuestra el uso básico del sistema para diseñar
una planta de potabilización pequeña (50 L/s).
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pint import UnitRegistry
from core.calculations import TreatmentCalculator
from core.hydraulics import HydraulicSimulator
from compliance.ras_2017 import RAS2017Validator

ureg = UnitRegistry()
Q_ = ureg.Quantity

def ejemplo_basico():
    """Ejemplo básico de diseño de PTAP"""
    
    print("=" * 70)
    print("EJEMPLO BÁSICO - DISEÑO PTAP 50 L/s")
    print("=" * 70)
    print()
    
    # ==========================================================================
    # PASO 1: CREAR CALCULADORA
    # ==========================================================================
    print("📊 Paso 1: Inicializando calculadora...")
    calc = TreatmentCalculator()
    print("✓ Calculadora lista\n")
    
    # ==========================================================================
    # PASO 2: PARÁMETROS DE DISEÑO
    # ==========================================================================
    print("📋 Paso 2: Definiendo parámetros de diseño...")
    
    Q = Q_(50, 'L/s').to('m**3/s')  # Caudal
    print(f"  Caudal de diseño: {Q.to('L/s')}")
    print(f"  Turbiedad agua cruda: 20 NTU")
    print(f"  Color aparente: 30 UPC")
    print(f"  pH: 7.2")
    print()
    
    # ==========================================================================
    # PASO 3: MEZCLA RÁPIDA
    # ==========================================================================
    print("⚡ Paso 3: Diseñando mezcla rápida...")
    
    mezcla = calc.calcular_mezcla_rapida(
        caudal=Q,
        gradiente_velocidad=Q_(1000, '1/s'),
        tiempo_retencion=Q_(30, 's'),
        temperatura=15.0
    )
    
    print(f"  Volumen cámara: {mezcla['volumen']:.4f}")
    print(f"  Potencia requerida: {mezcla['potencia']:.2f}")
    print(f"  Lado cámara (cúbica): {mezcla['lado_camara']:.3f}")
    print()
    
    # ==========================================================================
    # PASO 4: FLOCULACIÓN
    # ==========================================================================
    print("🌀 Paso 4: Diseñando floculación...")
    
    floculacion = calc.calcular_floculacion(
        caudal=Q,
        gradiente_velocidad=Q_(40, '1/s'),
        tiempo_retencion=Q_(25, 'minute'),
        temperatura=15.0,
        num_camaras=3
    )
    
    print(f"  Volumen total: {floculacion['volumen_total']:.3f}")
    print(f"  Potencia total: {floculacion['potencia_total']:.2f}")
    print(f"  Número de cámaras: {floculacion['num_camaras']}")
    
    print("\n  Gradientes por cámara:")
    for camara in floculacion['camaras']:
        print(f"    Cámara {camara['numero']}: G = {camara['gradiente']:.1f}")
    print()
    
    # ==========================================================================
    # PASO 5: SEDIMENTACIÓN
    # ==========================================================================
    print("⬇️  Paso 5: Diseñando sedimentación...")
    
    sedimentacion = calc.calcular_sedimentacion(
        caudal=Q,
        carga_superficial=Q_(30, 'm**3/(m**2*day)'),
        tiempo_retencion=Q_(2.5, 'hour'),
        profundidad=Q_(3.5, 'm')
    )
    
    print(f"  Área superficial: {sedimentacion['area_superficial']:.2f}")
    print(f"  Dimensiones: L={sedimentacion['longitud']:.2f} x B={sedimentacion['ancho']:.2f}")
    print(f"  Velocidad horizontal: {sedimentacion['velocidad_horizontal']:.3f}")
    print()
    
    # ==========================================================================
    # PASO 6: FILTRACIÓN
    # ==========================================================================
    print("🔬 Paso 6: Diseñando filtración...")
    
    filtracion = calc.calcular_filtracion(
        caudal=Q,
        tasa_filtracion=Q_(200, 'm**3/(m**2*day)'),
        num_filtros=4,
        profundidad_lecho=Q_(0.8, 'm')
    )
    
    print(f"  Área total filtración: {filtracion['area_total']:.2f}")
    print(f"  Área por filtro: {filtracion['area_por_filtro']:.2f}")
    print(f"  Lado filtro (cuadrado): {filtracion['lado_filtro']:.2f}")
    print(f"  Número de filtros: {filtracion['num_filtros']}")
    print()
    
    # ==========================================================================
    # PASO 7: DESINFECCIÓN
    # ==========================================================================
    print("💧 Paso 7: Diseñando desinfección...")
    
    desinfeccion = calc.calcular_desinfeccion(
        caudal=Q,
        tiempo_contacto=Q_(25, 'minute'),
        dosis_cloro=Q_(1.5, 'mg/L')
    )
    
    print(f"  Volumen tanque: {desinfeccion['volumen']:.3f}")
    print(f"  Valor CT: {desinfeccion['CT']:.2f}")
    print(f"  Consumo cloro: {desinfeccion['consumo_cloro']:.3f}")
    print()
    
    # ==========================================================================
    # PASO 8: VALIDACIÓN NORMATIVA
    # ==========================================================================
    print("✅ Paso 8: Validando conformidad RAS 2017...")
    
    validator = RAS2017Validator()
    
    # Validar mezcla rápida
    params_mezcla = {
        'gradiente_velocidad': 1000.0,
        'tiempo_retencion': 30.0
    }
    resultados_mezcla = validator.validate_process('mezcla_rapida', params_mezcla)
    
    # Validar floculación
    params_floc = {
        'gradiente_velocidad': 40.0,
        'tiempo_retencion': 25.0,
        'num_camaras': 3.0
    }
    resultados_floc = validator.validate_process('floculacion', params_floc)
    
    # Validar sedimentación
    params_sed = {
        'carga_superficial': 30.0,
        'velocidad_horizontal': sedimentacion['velocidad_horizontal'].magnitude,
        'tiempo_retencion': 2.5,
        'profundidad': 3.5
    }
    resultados_sed = validator.validate_process('sedimentacion', params_sed)
    
    # Validar filtración
    params_filt = {
        'tasa_filtracion': 200.0,
        'profundidad_lecho': 0.8,
        'num_filtros': 4.0
    }
    resultados_filt = validator.validate_process('filtracion', params_filt)
    
    # Validar desinfección
    params_desinf = {
        'tiempo_contacto': 25.0,
        'dosis_cloro': 1.5,
        'CT': desinfeccion['CT'].magnitude
    }
    resultados_desinf = validator.validate_process('desinfeccion', params_desinf)
    
    # Matriz de conformidad
    matriz = validator.generate_compliance_matrix()
    
    print(f"\n  Total validaciones: {matriz['resumen']['total_validaciones']}")
    print(f"  Conformes: {matriz['resumen']['conformes']}")
    print(f"  No conformes: {matriz['resumen']['no_conformes']}")
    print(f"  Tasa conformidad: {matriz['resumen']['tasa_conformidad']:.1f}%")
    print()
    
    # ==========================================================================
    # PASO 9: EXPORTAR TRAZABILIDAD
    # ==========================================================================
    print("📝 Paso 9: Exportando trazabilidad...")
    
    Path("data/exports").mkdir(parents=True, exist_ok=True)
    trace_file = "data/exports/ejemplo_basico_trazabilidad.json"
    calc.export_traces(trace_file)
    print(f"  ✓ Trazabilidad guardada en: {trace_file}")
    print()
    
    # Exportar validación
    compliance_file = "data/exports/ejemplo_basico_conformidad.json"
    validator.export_results(compliance_file)
    print(f"  ✓ Conformidad guardada en: {compliance_file}")
    print()
    
    # ==========================================================================
    # RESUMEN FINAL
    # ==========================================================================
    print("=" * 70)
    print("DISEÑO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print("\nResumen del diseño:")
    print(f"  • Caudal: {Q.to('L/s')}")
    print(f"  • Procesos diseñados: 5")
    print(f"  • Conformidad RAS: {matriz['resumen']['tasa_conformidad']:.1f}%")
    print(f"  • Archivos generados: 2")
    print("\nPara un diseño completo con reportes PDF/DXF, usa:")
    print("  python app/main.py")
    print("=" * 70)


if __name__ == "__main__":
    try:
        ejemplo_basico()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
