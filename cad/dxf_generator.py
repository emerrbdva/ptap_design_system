"""
Generador de archivos DXF (AutoCAD)

Genera planos técnicos de plantas de potabilización usando ezdxf.
Compatible con AutoCAD y otros programas CAD estándar.
"""

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PTAPDXFGenerator:
    """
    Generador de planos DXF para PTAP.
    
    Genera:
    - Vista en planta por proceso unitario
    - Cortes y elevaciones
    - Layout general
    - Capas organizadas
    - Bloques reutilizables
    """
    
    def __init__(
        self,
        output_path: str,
        dxf_version: str = "R2018"
    ):
        """
        Inicializar generador DXF.
        
        Args:
            output_path: Ruta del archivo DXF
            dxf_version: Versión de DXF (R2018, R2013, etc.)
        """
        self.output_path = Path(output_path)
        self.doc = ezdxf.new(dxf_version)
        self.msp = self.doc.modelspace()
        
        # Crear capas
        self._create_layers()
        
        logger.info(f"DXFGenerator inicializado: {output_path}")
    
    def _create_layers(self):
        """Crear capas estándar"""
        layers = {
            "GENERAL": colors.WHITE,
            "ESTRUCTURAL": colors.CYAN,
            "HIDRAULICO": colors.BLUE,
            "MECANICO": colors.GREEN,
            "ELECTRICO": colors.RED,
            "INSTRUMENTACION": colors.MAGENTA,
            "DIMENSIONES": colors.YELLOW,
            "TEXTOS": colors.WHITE
        }
        
        for layer_name, color in layers.items():
            self.doc.layers.add(layer_name, color=color)
        
        logger.debug(f"{len(layers)} capas creadas")
    
    def add_rectangle(
        self,
        x: float, y: float,
        width: float, height: float,
        layer: str = "GENERAL"
    ):
        """Agregar rectángulo (vista en planta)"""
        points = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
            (x, y)  # Cerrar
        ]
        
        self.msp.add_lwpolyline(points, dxfattribs={"layer": layer})
        logger.debug(f"Rectángulo agregado: {width}x{height}")
    
    def add_text(
        self,
        text: str,
        x: float, y: float,
        height: float = 2.5,
        layer: str = "TEXTOS"
    ):
        """Agregar texto"""
        self.msp.add_text(
            text,
            dxfattribs={
                "layer": layer,
                "height": height
            }
        ).set_placement((x, y), align=TextEntityAlignment.LEFT)
        
        logger.debug(f"Texto agregado: {text}")
    
    def add_dimension(
        self,
        base: Tuple[float, float],
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        text: Optional[str] = None,
        layer: str = "DIMENSIONES"
    ):
        """Agregar dimensión lineal"""
        dim = self.msp.add_linear_dim(
            base=base,
            p1=p1,
            p2=p2,
            dimstyle="EZDXF",
            override={"dimtxt": 2.0},
            dxfattribs={"layer": layer}
        )
        
        if text:
            dim.render()
        
        logger.debug("Dimensión agregada")
    
    def add_process_unit(
        self,
        name: str,
        x: float, y: float,
        width: float, height: float,
        details: Optional[Dict[str, any]] = None
    ):
        """
        Agregar unidad de proceso.
        
        Args:
            name: Nombre del proceso
            x, y: Coordenadas
            width, height: Dimensiones
            details: Detalles adicionales
        """
        # Rectángulo principal
        self.add_rectangle(x, y, width, height, "HIDRAULICO")
        
        # Texto del nombre
        self.add_text(name, x + width/2, y + height + 1)
        
        # Dimensiones
        self.add_dimension(
            base=(x, y - 2),
            p1=(x, y),
            p2=(x + width, y),
            text=f"{width:.2f} m"
        )
        
        self.add_dimension(
            base=(x - 2, y),
            p1=(x, y),
            p2=(x, y + height),
            text=f"{height:.2f} m"
        )
        
        logger.info(f"Unidad de proceso '{name}' agregada")
    
    def add_flow_arrow(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        layer: str = "HIDRAULICO"
    ):
        """Agregar flecha de flujo"""
        # Línea principal
        self.msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})
        
        # Punta de flecha (simplificada)
        # TODO: Implementar punta de flecha real
        
        logger.debug("Flecha de flujo agregada")
    
    def save(self) -> str:
        """Guardar archivo DXF"""
        try:
            self.doc.saveas(self.output_path)
            logger.info(f"DXF guardado: {self.output_path}")
            return str(self.output_path)
        except Exception as e:
            logger.error(f"Error guardando DXF: {e}")
            raise


def generate_ptap_layout(
    design_results: Dict[str, Dict[str, any]],
    output_path: str,
    scale: float = 1.0
) -> str:
    """
    Generar layout completo de PTAP.
    
    Args:
        design_results: Resultados de diseño
        output_path: Ruta del DXF
        scale: Escala del dibujo
        
    Returns:
        Ruta del archivo generado
    """
    dxf = PTAPDXFGenerator(output_path)
    
    # Disposición en secuencia horizontal
    x_offset = 0
    y_base = 0
    spacing = 5  # Espaciado entre unidades
    
    # Procesos típicos en orden
    process_order = [
        "aireacion",
        "mezcla_rapida",
        "floculacion",
        "sedimentacion",
        "filtracion",
        "desinfeccion"
    ]
    
    for proceso in process_order:
        if proceso in design_results:
            data = design_results[proceso]
            
            # Extraer dimensiones
            width = float(data.get("ancho", data.get("lado_filtro", data.get("lado_camara", 5))))
            length = float(data.get("longitud", width))
            
            # Agregar unidad
            dxf.add_process_unit(
                name=proceso.replace("_", " ").title(),
                x=x_offset,
                y=y_base,
                width=width * scale,
                height=length * scale,
                details=data
            )
            
            # Flecha de flujo al siguiente
            if proceso != process_order[-1]:
                dxf.add_flow_arrow(
                    x_offset + width * scale,
                    y_base + length * scale / 2,
                    x_offset + width * scale + spacing,
                    y_base + length * scale / 2
                )
            
            x_offset += width * scale + spacing
    
    return dxf.save()
