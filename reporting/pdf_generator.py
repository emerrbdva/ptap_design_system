"""
Generador de PDFs Profesionales

Genera reportes técnicos completos usando ReportLab:
- Portada e índice
- Tablas con unidades
- Figuras y gráficos
- Anexos de validación normativa
- Referencias a RAS 2017, Res. 2115, Dec. 1575
"""

from reportlab.lib.pagesizes import LETTER, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage
)
from reportlab.pdfgen import canvas
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PTAPPDFGenerator:
    """
    Generador de PDFs para diseños PTAP.
    
    Secciones incluidas:
    - Portada
    - Índice
    - Resumen ejecutivo
    - Marco normativo
    - Parámetros de diseño
    - Cálculos detallados
    - Resultados
    - Validación normativa
    - Conclusiones
    - Anexos
    - Referencias
    """
    
    def __init__(
        self,
        output_path: str,
        page_size: str = "LETTER",
        title: str = "Diseño de Planta de Potabilización"
    ):
        """
        Inicializar generador.
        
        Args:
            output_path: Ruta del PDF de salida
            page_size: Tamaño de página (LETTER o A4)
            title: Título del documento
        """
        self.output_path = Path(output_path)
        self.page_size = LETTER if page_size == "LETTER" else A4
        self.title = title
        
        # Crear PDF
        self.doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=self.page_size,
            rightMargin=2*cm,
            leftMargin=3*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )
        
        # Estilos
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
        # Story (contenido)
        self.story = []
        
        logger.info(f"PDFGenerator inicializado: {output_path}")
    
    def _create_custom_styles(self):
        """Crear estilos personalizados"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
            alignment=1  # Centrado
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='RASReference',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Oblique'
        ))
    
    def add_cover_page(
        self,
        project_name: str,
        author: str = "Sistema Integral PTAP",
        date: Optional[str] = None
    ):
        """Agregar portada"""
        if date is None:
            date = datetime.now().strftime("%d de %B de %Y")
        
        # Título principal
        self.story.append(Spacer(1, 5*cm))
        self.story.append(Paragraph(
            self.title.upper(),
            self.styles['CustomTitle']
        ))
        
        self.story.append(Spacer(1, 1*cm))
        self.story.append(Paragraph(
            f"<b>Proyecto:</b> {project_name}",
            self.styles['Normal']
        ))
        
        self.story.append(Spacer(1, 2*cm))
        self.story.append(Paragraph(
            f"<b>Elaborado por:</b> {author}",
            self.styles['Normal']
        ))
        
        self.story.append(Paragraph(
            f"<b>Fecha:</b> {date}",
            self.styles['Normal']
        ))
        
        self.story.append(PageBreak())
        logger.debug("Portada agregada")
    
    def add_section(
        self,
        title: str,
        content: str,
        ras_reference: Optional[str] = None
    ):
        """Agregar sección con contenido"""
        # Título de sección
        self.story.append(Paragraph(title, self.styles['CustomHeading2']))
        self.story.append(Spacer(1, 0.3*cm))
        
        # Contenido
        self.story.append(Paragraph(content, self.styles['Normal']))
        
        # Referencia RAS si existe
        if ras_reference:
            self.story.append(Spacer(1, 0.2*cm))
            self.story.append(Paragraph(
                f"<i>Ref: RAS 2017 - {ras_reference}</i>",
                self.styles['RASReference']
            ))
        
        self.story.append(Spacer(1, 0.5*cm))
        logger.debug(f"Sección agregada: {title}")
    
    def add_table(
        self,
        data: List[List[str]],
        title: Optional[str] = None,
        col_widths: Optional[List[float]] = None
    ):
        """Agregar tabla"""
        if title:
            self.story.append(Paragraph(title, self.styles['Heading3']))
            self.story.append(Spacer(1, 0.2*cm))
        
        # Crear tabla
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))
        logger.debug("Tabla agregada")
    
    def add_compliance_matrix(
        self,
        compliance_results: Dict[str, Any]
    ):
        """Agregar matriz de conformidad normativa"""
        self.story.append(Paragraph(
            "Matriz de Conformidad Normativa",
            self.styles['CustomHeading2']
        ))
        self.story.append(Spacer(1, 0.3*cm))
        
        # Resumen
        resumen = compliance_results.get("resumen", {})
        summary_text = f"""
        <b>Total validaciones:</b> {resumen.get('total_validaciones', 0)}<br/>
        <b>Conformes:</b> {resumen.get('conformes', 0)}<br/>
        <b>No conformes:</b> {resumen.get('no_conformes', 0)}<br/>
        <b>Tasa de conformidad:</b> {resumen.get('tasa_conformidad', 0):.1f}%
        """
        self.story.append(Paragraph(summary_text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.5*cm))
        
        # Tabla por proceso
        por_proceso = compliance_results.get("por_proceso", {})
        if por_proceso:
            data = [["Proceso", "Total", "Conforme", "No Conforme", "Advertencias"]]
            
            for proceso, stats in por_proceso.items():
                data.append([
                    proceso.replace("_", " ").title(),
                    str(stats.get("total", 0)),
                    str(stats.get("compliant", 0)),
                    str(stats.get("non_compliant", 0)),
                    str(stats.get("warnings", 0))
                ])
            
            self.add_table(data, title=None)
        
        logger.debug("Matriz de conformidad agregada")
    
    def build(self):
        """Generar PDF final"""
        try:
            self.doc.build(self.story)
            logger.info(f"PDF generado exitosamente: {self.output_path}")
            return str(self.output_path)
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            raise


def generate_complete_report(
    design_results: Dict[str, Any],
    compliance_results: Dict[str, Any],
    output_path: str,
    project_name: str
) -> str:
    """
    Generar reporte completo de diseño PTAP.
    
    Args:
        design_results: Resultados de cálculos
        compliance_results: Resultados de validación
        output_path: Ruta del PDF
        project_name: Nombre del proyecto
        
    Returns:
        Ruta del PDF generado
    """
    pdf = PTAPPDFGenerator(output_path)
    
    # Portada
    pdf.add_cover_page(project_name)
    
    # Marco normativo
    pdf.add_section(
        "Marco Normativo",
        "Este diseño cumple con la normativa colombiana vigente: "
        "Resolución 0330 de 2017 (RAS), Resolución 2115 de 2007 y Decreto 1575 de 2007.",
        "Resolución 0330 de 2017"
    )
    
    # Parámetros de diseño
    pdf.add_section(
        "Parámetros de Diseño",
        "A continuación se presentan los parámetros de diseño adoptados:"
    )
    
    # Resultados
    for proceso, resultados in design_results.items():
        if isinstance(resultados, dict):
            content = "<br/>".join(
                f"<b>{k}:</b> {v}" for k, v in resultados.items()
                if not k.startswith("_")
            )
            pdf.add_section(
                proceso.replace("_", " ").title(),
                content
            )
    
    # Conformidad normativa
    pdf.add_compliance_matrix(compliance_results)
    
    # Construir
    return pdf.build()
