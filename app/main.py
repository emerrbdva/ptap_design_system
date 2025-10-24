"""
Aplicación Principal del Sistema PTAP

Script principal para diseño completo de plantas de potabilización.
Integra todos los módulos: cálculos, validación, IA, reportes y CAD.
"""

import sys
from pathlib import Path
import yaml
import logging
from typing import Dict, Any, Optional
from pint import UnitRegistry

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.calculations import TreatmentCalculator
from core.hydraulics import HydraulicSimulator
from compliance.ras_2017 import RAS2017Validator
from compliance.res_2115 import Resolucion2115Validator
from ai.model_router import AIModelRouter
from reporting.pdf_generator import generate_complete_report
from cad.dxf_generator import generate_ptap_layout

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ptap_design.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
ureg = UnitRegistry()
Q_ = ureg.Quantity


class PTAPDesigner:
    """
    Diseñador integral de plantas de potabilización.
    
    Flujo completo:
    1. Ingreso de parámetros de agua cruda
    2. Selección de tren de tratamiento
    3. Dimensionamiento de procesos
    4. Simulación hidráulica
    5. Validación normativa (RAS, Res. 2115)
    6. Generación de reportes (PDF, Excel, DXF)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar diseñador.
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        # Cargar configuración
        if config_path:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
        
        # Inicializar módulos
        self.calculator = TreatmentCalculator(self.config.get('treatment_processes'))
        self.simulator = HydraulicSimulator(temperatura=15.0)
        self.ras_validator = RAS2017Validator()
        self.quality_validator = Resolucion2115Validator()
        
        # IA (opcional, requiere Ollama ejecutándose)
        try:
            self.ai_router = AIModelRouter(config_path)
            self.ai_enabled = True
        except Exception as e:
            logger.warning(f"IA no disponible: {e}")
            self.ai_enabled = False
        
        # Resultados
        self.design_results = {}
        self.compliance_results = {}
        
        logger.info("PTAPDesigner inicializado")
    
    def set_raw_water_parameters(
        self,
        caudal: float,  # L/s
        turbidez: float,  # NTU
        color: float,  # UPC
        ph: float,
        temperatura: float = 15.0  # °C
    ):
        """
        Establecer parámetros de agua cruda.
        
        Args:
            caudal: Caudal de diseño [L/s]
            turbidez: Turbiedad [NTU]
            color: Color aparente [UPC]
            ph: pH
            temperatura: Temperatura [°C]
        """
        self.raw_water = {
            "caudal": Q_(caudal, 'L/s').to('m**3/s'),
            "turbidez": turbidez,
            "color": color,
            "ph": ph,
            "temperatura": temperatura
        }
        
        logger.info(f"Parámetros de agua cruda: Q={caudal} L/s, Turbidez={turbidez} NTU")
    
    def design_complete_train(self) -> Dict[str, Any]:
        """
        Diseñar tren de tratamiento completo.
        
        Secuencia:
        1. Aireación
        2. Mezcla rápida
        3. Floculación
        4. Sedimentación
        5. Filtración
        6. Desinfección
        
        Returns:
            Dict con todos los resultados
        """
        Q = self.raw_water["caudal"]
        
        logger.info("=== Iniciando diseño completo de PTAP ===")
        
        # 1. AIREACIÓN
        logger.info("--- Diseñando Aireación ---")
        aireacion = self.calculator.calcular_aireacion(
            caudal=Q,
            tiempo_contacto=Q_(20, 'minute'),
            carga_superficial=Q_(40, 'm**3/(m**2*hour)')
        )
        self.design_results['aireacion'] = aireacion
        
        # 2. MEZCLA RÁPIDA
        logger.info("--- Diseñando Mezcla Rápida ---")
        mezcla_rapida = self.calculator.calcular_mezcla_rapida(
            caudal=Q,
            gradiente_velocidad=Q_(1000, '1/s'),
            tiempo_retencion=Q_(30, 's'),
            temperatura=self.raw_water["temperatura"]
        )
        self.design_results['mezcla_rapida'] = mezcla_rapida
        
        # 3. FLOCULACIÓN
        logger.info("--- Diseñando Floculación ---")
        floculacion = self.calculator.calcular_floculacion(
            caudal=Q,
            gradiente_velocidad=Q_(40, '1/s'),
            tiempo_retencion=Q_(25, 'minute'),
            temperatura=self.raw_water["temperatura"],
            num_camaras=3
        )
        self.design_results['floculacion'] = floculacion
        
        # 4. SEDIMENTACIÓN
        logger.info("--- Diseñando Sedimentación ---")
        sedimentacion = self.calculator.calcular_sedimentacion(
            caudal=Q,
            carga_superficial=Q_(30, 'm**3/(m**2*day)'),
            tiempo_retencion=Q_(2.5, 'hour'),
            profundidad=Q_(3.5, 'm')
        )
        self.design_results['sedimentacion'] = sedimentacion
        
        # 5. FILTRACIÓN
        logger.info("--- Diseñando Filtración ---")
        filtracion = self.calculator.calcular_filtracion(
            caudal=Q,
            tasa_filtracion=Q_(200, 'm**3/(m**2*day)'),
            num_filtros=4,
            profundidad_lecho=Q_(0.8, 'm')
        )
        self.design_results['filtracion'] = filtracion
        
        # 6. DESINFECCIÓN
        logger.info("--- Diseñando Desinfección ---")
        desinfeccion = self.calculator.calcular_desinfeccion(
            caudal=Q,
            tiempo_contacto=Q_(25, 'minute'),
            dosis_cloro=Q_(1.5, 'mg/L')
        )
        self.design_results['desinfeccion'] = desinfeccion
        
        logger.info("=== Diseño completo finalizado ===")
        return self.design_results
    
    def validate_design(self) -> Dict[str, Any]:
        """
        Validar diseño contra RAS 2017.
        
        Returns:
            Resultados de validación
        """
        logger.info("=== Validando conformidad RAS 2017 ===")
        
        # Preparar parámetros para validación
        validation_params = {}
        
        # Mezcla rápida
        if 'mezcla_rapida' in self.design_results:
            validation_params['mezcla_rapida'] = {
                'gradiente_velocidad': self.design_results['mezcla_rapida']['gradiente_velocidad'].magnitude,
                'tiempo_retencion': self.design_results['mezcla_rapida']['tiempo_retencion'].magnitude
            }
        
        # Floculación
        if 'floculacion' in self.design_results:
            validation_params['floculacion'] = {
                'gradiente_velocidad': self.design_results['floculacion']['gradiente_promedio'].magnitude,
                'tiempo_retencion': self.design_results['floculacion']['tiempo_retencion_total'].to('minute').magnitude,
                'num_camaras': self.design_results['floculacion']['num_camaras']
            }
        
        # Sedimentación
        if 'sedimentacion' in self.design_results:
            validation_params['sedimentacion'] = {
                'carga_superficial': 30.0,  # Valor usado en diseño
                'velocidad_horizontal': self.design_results['sedimentacion']['velocidad_horizontal'].magnitude,
                'tiempo_retencion': self.design_results['sedimentacion']['tiempo_retencion'].magnitude,
                'profundidad': self.design_results['sedimentacion']['profundidad'].magnitude
            }
        
        # Validar
        self.compliance_results = self.ras_validator.validate_all(validation_params)
        
        # Generar matriz
        matrix = self.ras_validator.generate_compliance_matrix()
        
        logger.info(f"Validación completa: {matrix['resumen']['tasa_conformidad']:.1f}% conforme")
        return matrix
    
    def generate_reports(
        self,
        project_name: str,
        output_dir: str = "data/exports"
    ) -> Dict[str, str]:
        """
        Generar todos los reportes.
        
        Args:
            project_name: Nombre del proyecto
            output_dir: Directorio de salida
            
        Returns:
            Dict con rutas de archivos generados
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        reports = {}
        
        # PDF
        logger.info("Generando reporte PDF...")
        pdf_path = output_path / f"{project_name}_diseño_ptap.pdf"
        try:
            reports['pdf'] = generate_complete_report(
                self.design_results,
                self.ras_validator.generate_compliance_matrix(),
                str(pdf_path),
                project_name
            )
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
        
        # DXF
        logger.info("Generando plano DXF...")
        dxf_path = output_path / f"{project_name}_layout.dxf"
        try:
            # Convertir resultados a formato serializable
            design_simple = {}
            for key, value in self.design_results.items():
                if isinstance(value, dict):
                    design_simple[key] = {
                        k: v.magnitude if hasattr(v, 'magnitude') else v
                        for k, v in value.items()
                        if not k.startswith('_')
                    }
            
            reports['dxf'] = generate_ptap_layout(
                design_simple,
                str(dxf_path)
            )
        except Exception as e:
            logger.error(f"Error generando DXF: {e}")
        
        # Trazabilidad
        logger.info("Exportando trazabilidad...")
        trace_path = output_path / f"{project_name}_trazabilidad.json"
        try:
            self.calculator.export_traces(str(trace_path))
            reports['traceability'] = str(trace_path)
        except Exception as e:
            logger.error(f"Error exportando trazabilidad: {e}")
        
        logger.info(f"Reportes generados: {list(reports.keys())}")
        return reports


def main():
    """Función principal de ejemplo"""
    print("=" * 70)
    print("SISTEMA INTEGRAL DE DISEÑO DE PLANTAS DE POTABILIZACIÓN (PTAP)")
    print("Versión 1.0.0")
    print("=" * 70)
    print()
    
    # Crear diseñador
    config_path = "config/config.yaml"
    if Path(config_path).exists():
        designer = PTAPDesigner(config_path)
    else:
        print("⚠️  Archivo de configuración no encontrado, usando valores por defecto")
        designer = PTAPDesigner()
    
    # Parámetros de ejemplo
    print("Configurando parámetros de agua cruda...")
    designer.set_raw_water_parameters(
        caudal=50.0,  # L/s
        turbidez=20.0,  # NTU
        color=30.0,  # UPC
        ph=7.2,
        temperatura=15.0  # °C
    )
    
    # Diseñar
    print("\nDiseñando tren de tratamiento completo...")
    results = designer.design_complete_train()
    
    print("\n✓ Diseño completado")
    print(f"  - Procesos diseñados: {len(results)}")
    
    # Validar
    print("\nValidando conformidad normativa...")
    compliance = designer.validate_design()
    
    print(f"\n✓ Validación completada")
    print(f"  - Conformidad: {compliance['resumen']['tasa_conformidad']:.1f}%")
    print(f"  - Conformes: {compliance['resumen']['conformes']}")
    print(f"  - No conformes: {compliance['resumen']['no_conformes']}")
    
    # Generar reportes
    print("\nGenerando reportes...")
    reports = designer.generate_reports(
        project_name="PTAP_Ejemplo_50Ls",
        output_dir="data/exports"
    )
    
    print(f"\n✓ Reportes generados:")
    for tipo, ruta in reports.items():
        print(f"  - {tipo.upper()}: {ruta}")
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 70)


if __name__ == "__main__":
    # Crear directorio de logs
    Path("logs").mkdir(exist_ok=True)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        logger.exception("Error fatal en la aplicación")
        print(f"\n❌ Error: {e}")
        sys.exit(1)
