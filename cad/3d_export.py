"""
Exportación 3D/IFC para Modelos PTAP

Capacidades de exportación y visualización 3D:
- Exportación a formatos IFC (Industry Foundation Classes)
- Visualización 3D interactiva con Open3D
- Exportación a formatos de malla (STL, PLY, OBJ)
- Generación de renders fotorrealistas
- Creación de recorridos virtuales
- Integración con software BIM comercial
- Exportación para realidad virtual/aumentada
"""

import open3d as o3d
import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import math

# Importar módulos del sistema
from ..bim.basic_bim import PTAPBIMGenerator, PTAPBIMModel, BIMElement, IFCElementType
from ..bim.architectural_generator import ArchitecturalGenerator, PTAPLayout

class ExportFormat(Enum):
    """Formatos de exportación 3D disponibles"""
    IFC = "ifc"
    STL = "stl"
    PLY = "ply"
    OBJ = "obj"
    GLTF = "gltf"
    USD = "usd"
    STEP = "step"
    FBX = "fbx"

class VisualizationMode(Enum):
    """Modos de visualización 3D"""
    WIREFRAME = "wireframe"
    SOLID = "solid"
    TEXTURED = "textured"
    TECHNICAL = "technical"
    PHOTOREALISTIC = "photorealistic"
    XRAY = "xray"

class RenderQuality(Enum):
    """Calidades de renderizado"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class Mesh3D:
    """Malla 3D básica"""
    vertices: np.ndarray
    faces: np.ndarray
    normals: Optional[np.ndarray] = None
    colors: Optional[np.ndarray] = None
    textures: Optional[Dict] = None
    material_properties: Optional[Dict] = None

@dataclass
class Scene3D:
    """Escena 3D completa"""
    meshes: List[Mesh3D]
    lights: List[Dict]
    cameras: List[Dict]
    environment: Dict
    metadata: Dict

@dataclass
class ExportOptions:
    """Opciones de exportación"""
    format: ExportFormat
    quality: RenderQuality
    include_materials: bool = True
    include_textures: bool = True
    include_lights: bool = True
    coordinate_system: str = "right_handed"  # "left_handed", "right_handed"
    units: str = "meters"  # "meters", "millimeters", "feet"
    level_of_detail: str = "medium"  # "low", "medium", "high"
    compression: bool = False
    metadata: Dict = None

class PTAP3DExporter:
    """
    Exportador 3D para modelos PTAP
    
    Funcionalidades:
    - Conversión de modelos BIM a geometrías 3D
    - Visualización interactiva en tiempo real
    - Exportación a múltiples formatos
    - Generación de renders de alta calidad
    - Recorridos virtuales automatizados
    - Compatibilidad con software BIM
    """
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or self._default_config()
        
        # Componentes auxiliares
        self.bim_generator = PTAPBIMGenerator()
        self.arch_generator = ArchitecturalGenerator()
        
        # Biblioteca de materiales 3D
        self.material_library = self._initialize_material_library()
        self.texture_library = self._initialize_texture_library()
        
        # Configuración de renderizado
        self.render_settings = self._initialize_render_settings()
    
    def _default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            'default_resolution': (1920, 1080),
            'default_quality': RenderQuality.MEDIUM.value,
            'enable_shadows': True,
            'enable_reflections': True,
            'enable_ambient_occlusion': True,
            'max_polygon_count': 1000000,
            'texture_resolution': 1024,
            'light_intensity': 1.0,
            'camera_settings': {
                'fov': 60,
                'near_clip': 0.1,
                'far_clip': 1000.0
            }
        }
    
    def _initialize_material_library(self) -> Dict:
        """Biblioteca de materiales 3D"""
        return {
            'concrete': {
                'base_color': (0.7, 0.7, 0.7, 1.0),
                'roughness': 0.8,
                'metallic': 0.0,
                'specular': 0.2,
                'normal_strength': 1.0,
                'texture_scale': (4.0, 4.0)
            },
            'steel': {
                'base_color': (0.5, 0.5, 0.6, 1.0),
                'roughness': 0.3,
                'metallic': 0.9,
                'specular': 0.9,
                'normal_strength': 0.5,
                'texture_scale': (1.0, 1.0)
            },
            'pvc': {
                'base_color': (0.9, 0.9, 0.95, 1.0),
                'roughness': 0.4,
                'metallic': 0.0,
                'specular': 0.6,
                'normal_strength': 0.2,
                'texture_scale': (2.0, 2.0)
            },
            'water': {
                'base_color': (0.2, 0.4, 0.8, 0.7),
                'roughness': 0.0,
                'metallic': 0.0,
                'specular': 1.0,
                'transparency': 0.3,
                'refraction_index': 1.33
            },
            'glass': {
                'base_color': (0.9, 0.95, 1.0, 0.1),
                'roughness': 0.0,
                'metallic': 0.0,
                'specular': 1.0,
                'transparency': 0.9,
                'refraction_index': 1.52
            }
        }
    
    def _initialize_texture_library(self) -> Dict:
        """Biblioteca de texturas procedurales"""
        return {
            'concrete_texture': {
                'type': 'procedural',
                'pattern': 'noise',
                'scale': 0.1,
                'octaves': 4,
                'persistence': 0.5
            },
            'steel_texture': {
                'type': 'procedural',
                'pattern': 'brushed_metal',
                'direction': 'horizontal',
                'intensity': 0.3
            },
            'water_texture': {
                'type': 'animated',
                'pattern': 'waves',
                'amplitude': 0.02,
                'frequency': 2.0,
                'speed': 1.0
            }
        }
    
    def _initialize_render_settings(self) -> Dict:
        """Configuración de renderizado por calidad"""
        return {
            RenderQuality.LOW.value: {
                'samples': 16,
                'bounces': 2,
                'resolution_scale': 0.5,
                'shadow_quality': 'low',
                'texture_filtering': 'bilinear'
            },
            RenderQuality.MEDIUM.value: {
                'samples': 64,
                'bounces': 4,
                'resolution_scale': 1.0,
                'shadow_quality': 'medium',
                'texture_filtering': 'trilinear'
            },
            RenderQuality.HIGH.value: {
                'samples': 256,
                'bounces': 8,
                'resolution_scale': 1.5,
                'shadow_quality': 'high',
                'texture_filtering': 'anisotropic'
            },
            RenderQuality.ULTRA.value: {
                'samples': 1024,
                'bounces': 12,
                'resolution_scale': 2.0,
                'shadow_quality': 'ultra',
                'texture_filtering': 'anisotropic_16x'
            }
        }
    
    def export_complete_3d_model(self, 
                                bim_model: PTAPBIMModel,
                                output_directory: str,
                                export_options: ExportOptions = None) -> Dict[str, str]:
        """
        Exporta modelo 3D completo en múltiples formatos
        
        Args:
            bim_model: Modelo BIM de PTAP
            output_directory: Directorio de salida
            export_options: Opciones de exportación
            
        Returns:
            Dict con rutas de archivos generados
        """
        try:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if not export_options:
                export_options = ExportOptions(
                    format=ExportFormat.IFC,
                    quality=RenderQuality.MEDIUM
                )
            
            # Generar escena 3D desde modelo BIM
            scene_3d = self._convert_bim_to_3d_scene(bim_model)
            
            exported_files = {}
            
            # Exportar IFC (formato nativo BIM)
            if export_options.format == ExportFormat.IFC or True:  # Siempre exportar IFC
                ifc_file = output_dir / 'ptap_model.ifc'
                ifc_path = self.bim_generator.export_to_ifc(bim_model, str(ifc_file))
                exported_files['ifc'] = ifc_path
            
            # Exportar malla 3D para visualización
            mesh_file = output_dir / f'ptap_model.{export_options.format.value}'
            mesh_path = self._export_3d_mesh(scene_3d, str(mesh_file), export_options)
            exported_files['mesh'] = mesh_path
            
            # Generar renders de vista
            renders_dir = output_dir / 'renders'
            render_paths = self._generate_standard_renders(scene_3d, str(renders_dir), export_options)
            exported_files.update(render_paths)
            
            # Generar modelo web interactivo
            web_model = self._generate_web_viewer(scene_3d, output_dir)
            if web_model:
                exported_files['web_viewer'] = web_model
            
            # Exportar datos de recorrido virtual
            virtual_tour = self._generate_virtual_tour_data(scene_3d, output_dir)
            if virtual_tour:
                exported_files['virtual_tour'] = virtual_tour
            
            self.logger.info(f"Modelos 3D exportados a: {output_dir}")
            return exported_files
            
        except Exception as e:
            self.logger.error(f"Error exportando modelos 3D: {e}")
            raise
    
    def _convert_bim_to_3d_scene(self, bim_model: PTAPBIMModel) -> Scene3D:
        """
        Convierte modelo BIM a escena 3D
        
        Args:
            bim_model: Modelo BIM
            
        Returns:
            Scene3D con geometrías 3D
        """
        try:
            meshes = []
            
            # Procesar elementos estructurales
            for element in bim_model.building_elements:
                mesh = self._create_mesh_from_bim_element(element)
                if mesh:
                    meshes.append(mesh)
            
            # Procesar equipos
            for element in bim_model.equipment_elements:
                mesh = self._create_mesh_from_bim_element(element)
                if mesh:
                    meshes.append(mesh)
            
            # Procesar tuberías
            for element in bim_model.piping_elements:
                mesh = self._create_pipe_mesh(element)
                if mesh:
                    meshes.append(mesh)
            
            # Procesar instrumentación
            for element in bim_model.instrumentation_elements:
                mesh = self._create_instrument_mesh(element)
                if mesh:
                    meshes.append(mesh)
            
            # Configurar iluminación
            lights = self._setup_scene_lighting()
            
            # Configurar cámaras
            cameras = self._setup_scene_cameras(bim_model)
            
            # Configurar entorno
            environment = self._setup_environment()
            
            scene = Scene3D(
                meshes=meshes,
                lights=lights,
                cameras=cameras,
                environment=environment,
                metadata={
                    'project_name': bim_model.project_info.get('name', 'PTAP Project'),
                    'creation_date': str(np.datetime64('now')),
                    'total_elements': len(meshes)
                }
            )
            
            return scene
            
        except Exception as e:
            self.logger.error(f"Error convirtiendo BIM a 3D: {e}")
            raise
    
    def _create_mesh_from_bim_element(self, element: BIMElement) -> Optional[Mesh3D]:
        """
        Crea malla 3D desde elemento BIM
        
        Args:
            element: Elemento BIM
            
        Returns:
            Mesh3D generada
        """
        try:
            if element.element_type == IFCElementType.WALL:
                return self._create_wall_mesh(element)
            elif element.element_type == IFCElementType.SLAB:
                return self._create_slab_mesh(element)
            elif element.element_type == IFCElementType.COLUMN:
                return self._create_column_mesh(element)
            elif element.element_type == IFCElementType.BEAM:
                return self._create_beam_mesh(element)
            elif element.element_type == IFCElementType.TANK:
                return self._create_tank_mesh(element)
            elif element.element_type == IFCElementType.EQUIPMENT:
                return self._create_equipment_mesh(element)
            else:
                return self._create_generic_box_mesh(element)
                
        except Exception as e:
            self.logger.error(f"Error creando malla para elemento {element.name}: {e}")
            return None
    
    def _create_wall_mesh(self, wall: BIMElement) -> Mesh3D:
        """Crea malla para muro"""
        geometry = wall.geometry
        length = geometry.get('length', 5.0)
        height = geometry.get('height', 3.0)
        thickness = geometry.get('thickness', 0.2)
        
        # Crear box mesh para el muro
        vertices = np.array([
            [0, 0, 0], [length, 0, 0], [length, thickness, 0], [0, thickness, 0],  # Base
            [0, 0, height], [length, 0, height], [length, thickness, height], [0, thickness, height]  # Top
        ])
        
        # Caras del cubo (12 triángulos, 2 por cara)
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # Bottom
            [4, 7, 6], [4, 6, 5],  # Top
            [0, 4, 5], [0, 5, 1],  # Front
            [2, 6, 7], [2, 7, 3],  # Back
            [0, 3, 7], [0, 7, 4],  # Left
            [1, 5, 6], [1, 6, 2]   # Right
        ])
        
        # Trasladar a posición
        vertices += np.array(wall.location)
        
        # Asignar material
        material_props = self.material_library.get('concrete', {})
        
        return Mesh3D(
            vertices=vertices,
            faces=faces,
            material_properties=material_props
        )
    
    def _create_slab_mesh(self, slab: BIMElement) -> Mesh3D:
        """Crea malla para losa"""
        geometry = slab.geometry
        length = geometry.get('length', 10.0)
        width = geometry.get('width', 10.0)
        thickness = geometry.get('thickness', 0.15)
        
        vertices = np.array([
            [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],  # Bottom
            [0, 0, thickness], [length, 0, thickness], [length, width, thickness], [0, width, thickness]  # Top
        ])
        
        faces = np.array([
            [0, 2, 1], [0, 3, 2],  # Bottom
            [4, 5, 6], [4, 6, 7],  # Top
            [0, 1, 5], [0, 5, 4],  # Front
            [2, 7, 6], [2, 3, 7],  # Back
            [0, 4, 7], [0, 7, 3],  # Left
            [1, 2, 6], [1, 6, 5]   # Right
        ])
        
        vertices += np.array(slab.location)
        
        return Mesh3D(
            vertices=vertices,
            faces=faces,
            material_properties=self.material_library.get('concrete', {})
        )
    
    def _create_tank_mesh(self, tank: BIMElement) -> Mesh3D:
        """Crea malla para tanque/sedimentador"""
        geometry = tank.geometry
        length = geometry.get('length', 20.0)
        width = geometry.get('width', 5.0)
        height = geometry.get('height', 4.0)
        wall_thickness = 0.3
        
        # Crear geometría de tanque (con paredes)
        meshes = []
        
        # Piso
        floor_vertices = np.array([
            [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
            [0, 0, wall_thickness], [length, 0, wall_thickness], 
            [length, width, wall_thickness], [0, width, wall_thickness]
        ])
        
        # Paredes laterales
        wall_positions = [
            ([0, 0, 0], [wall_thickness, width, height]),  # Izquierda
            ([length-wall_thickness, 0, 0], [length, width, height]),  # Derecha
            ([0, 0, 0], [length, wall_thickness, height]),  # Frontal
            ([0, width-wall_thickness, 0], [length, width, height])   # Trasera
        ]
        
        # Por simplicidad, crear un box sólido
        vertices = np.array([
            [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
            [0, 0, height], [length, 0, height], [length, width, height], [0, width, height]
        ])
        
        faces = np.array([
            [0, 2, 1], [0, 3, 2],  # Bottom
            [4, 5, 6], [4, 6, 7],  # Top
            [0, 1, 5], [0, 5, 4],  # Front
            [2, 7, 6], [2, 3, 7],  # Back
            [0, 4, 7], [0, 7, 3],  # Left
            [1, 2, 6], [1, 6, 5]   # Right
        ])
        
        vertices += np.array(tank.location)
        
        # Añadir agua dentro del tanque
        water_level = height * 0.8  # 80% lleno
        water_vertices = vertices.copy()
        water_vertices[4:, 2] = tank.location[2] + water_level  # Ajustar nivel superior
        
        return Mesh3D(
            vertices=vertices,
            faces=faces,
            material_properties=self.material_library.get('concrete', {})
        )
    
    def _create_pipe_mesh(self, pipe: BIMElement) -> Optional[Mesh3D]:
        """Crea malla para tubería"""
        # Implementación simplificada - crear cilindro
        geometry = pipe.geometry
        diameter = geometry.get('diameter', 0.2)
        length = geometry.get('length', 5.0)
        
        # Generar cilindro usando paramétrica
        segments = 16
        vertices = []
        faces = []
        
        # Vértices del cilindro
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            x = diameter/2 * np.cos(angle)
            y = diameter/2 * np.sin(angle)
            
            # Extremo inicial
            vertices.append([0, x, y])
            # Extremo final
            vertices.append([length, x, y])
        
        vertices = np.array(vertices)
        
        # Generar caras del cilindro
        for i in range(segments):
            i1 = i * 2
            i2 = ((i + 1) % segments) * 2
            
            # Cara lateral (2 triángulos)
            faces.append([i1, i2, i2 + 1])
            faces.append([i1, i2 + 1, i1 + 1])
        
        faces = np.array(faces)
        vertices += np.array(pipe.location)
        
        return Mesh3D(
            vertices=vertices,
            faces=faces,
            material_properties=self.material_library.get('pvc', {})
        )
    
    def _export_3d_mesh(self, scene: Scene3D, output_path: str, 
                       export_options: ExportOptions) -> str:
        """
        Exporta escena 3D a archivo
        
        Args:
            scene: Escena 3D
            output_path: Ruta de salida
            export_options: Opciones de exportación
            
        Returns:
            Ruta del archivo exportado
        """
        try:
            # Combinar todas las mallas en una sola
            combined_vertices = []
            combined_faces = []
            vertex_offset = 0
            
            for mesh in scene.meshes:
                combined_vertices.append(mesh.vertices)
                # Ajustar índices de caras
                adjusted_faces = mesh.faces + vertex_offset
                combined_faces.append(adjusted_faces)
                vertex_offset += len(mesh.vertices)
            
            if not combined_vertices:
                raise ValueError("No hay mallas para exportar")
            
            vertices = np.vstack(combined_vertices)
            faces = np.vstack(combined_faces)
            
            # Crear malla de Open3D
            mesh_o3d = o3d.geometry.TriangleMesh()
            mesh_o3d.vertices = o3d.utility.Vector3dVector(vertices)
            mesh_o3d.triangles = o3d.utility.Vector3iVector(faces)
            
            # Calcular normales
            mesh_o3d.compute_vertex_normals()
            
            # Exportar según formato
            if export_options.format == ExportFormat.STL:
                success = o3d.io.write_triangle_mesh(output_path, mesh_o3d)
            elif export_options.format == ExportFormat.PLY:
                success = o3d.io.write_triangle_mesh(output_path, mesh_o3d)
            elif export_options.format == ExportFormat.OBJ:
                success = o3d.io.write_triangle_mesh(output_path, mesh_o3d)
            else:
                # Usar trimesh para otros formatos
                mesh_trimesh = trimesh.Trimesh(vertices=vertices, faces=faces)
                mesh_trimesh.export(output_path)
                success = True
            
            if success:
                self.logger.info(f"Malla 3D exportada: {output_path}")
                return output_path
            else:
                raise Exception(f"Error exportando a {export_options.format.value}")
                
        except Exception as e:
            self.logger.error(f"Error exportando malla 3D: {e}")
            raise
    
    def visualize_interactive_3d(self, scene: Scene3D, 
                               mode: VisualizationMode = VisualizationMode.SOLID):
        """
        Visualiza escena 3D de forma interactiva
        
        Args:
            scene: Escena 3D
            mode: Modo de visualización
        """
        try:
            # Crear visualizador
            vis = o3d.visualization.Visualizer()
            vis.create_window("PTAP 3D Model", 1920, 1080)
            
            # Añadir mallas a la visualización
            for mesh_data in scene.meshes:
                mesh_o3d = o3d.geometry.TriangleMesh()
                mesh_o3d.vertices = o3d.utility.Vector3dVector(mesh_data.vertices)
                mesh_o3d.triangles = o3d.utility.Vector3iVector(mesh_data.faces)
                mesh_o3d.compute_vertex_normals()
                
                # Aplicar colores según material
                if mesh_data.material_properties:
                    color = mesh_data.material_properties.get('base_color', (0.7, 0.7, 0.7, 1.0))
                    mesh_o3d.paint_uniform_color(color[:3])
                
                vis.add_geometry(mesh_o3d)
            
            # Configurar vista
            ctr = vis.get_view_control()
            ctr.set_zoom(0.5)
            
            # Añadir sistema de coordenadas
            coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=5.0)
            vis.add_geometry(coord_frame)
            
            # Ejecutar visualización
            vis.run()
            vis.destroy_window()
            
        except Exception as e:
            self.logger.error(f"Error en visualización 3D: {e}")
    
    def _generate_standard_renders(self, scene: Scene3D, output_dir: str, 
                                 export_options: ExportOptions) -> Dict[str, str]:
        """Genera renders estándar desde diferentes ángulos"""
        renders = {}
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Vistas estándar
            camera_positions = {
                'isometric': {'position': [50, 50, 30], 'target': [25, 25, 5]},
                'front': {'position': [0, -50, 10], 'target': [25, 25, 5]},
                'side': {'position': [-50, 25, 10], 'target': [25, 25, 5]},
                'top': {'position': [25, 25, 100], 'target': [25, 25, 0]}
            }
            
            for view_name, camera_config in camera_positions.items():
                render_file = output_path / f'{view_name}_view.png'
                
                # Generar render (implementación simplificada)
                self._render_view(scene, camera_config, str(render_file), export_options)
                
                renders[f'{view_name}_render'] = str(render_file)
            
            return renders
            
        except Exception as e:
            self.logger.error(f"Error generando renders: {e}")
            return {}
    
    def _render_view(self, scene: Scene3D, camera_config: Dict, 
                    output_file: str, export_options: ExportOptions):
        """Renderiza vista específica"""
        try:
            # Crear visualizador offscreen
            vis = o3d.visualization.Visualizer()
            vis.create_window(visible=False)
            
            # Añadir geometrías
            for mesh_data in scene.meshes:
                mesh_o3d = o3d.geometry.TriangleMesh()
                mesh_o3d.vertices = o3d.utility.Vector3dVector(mesh_data.vertices)
                mesh_o3d.triangles = o3d.utility.Vector3iVector(mesh_data.faces)
                mesh_o3d.compute_vertex_normals()
                
                if mesh_data.material_properties:
                    color = mesh_data.material_properties.get('base_color', (0.7, 0.7, 0.7, 1.0))
                    mesh_o3d.paint_uniform_color(color[:3])
                
                vis.add_geometry(mesh_o3d)
            
            # Configurar cámara
            ctr = vis.get_view_control()
            ctr.set_lookat(camera_config['target'])
            ctr.set_front(np.array(camera_config['position']) - np.array(camera_config['target']))
            ctr.set_zoom(0.5)
            
            # Capturar imagen
            vis.poll_events()
            vis.update_renderer()
            vis.capture_screen_image(output_file)
            
            vis.destroy_window()
            
        except Exception as e:
            self.logger.error(f"Error renderizando vista: {e}")
    
    # Métodos auxiliares (implementación simplificada)
    def _create_column_mesh(self, column: BIMElement) -> Mesh3D:
        return self._create_generic_box_mesh(column)
    
    def _create_beam_mesh(self, beam: BIMElement) -> Mesh3D:
        return self._create_generic_box_mesh(beam)
    
    def _create_equipment_mesh(self, equipment: BIMElement) -> Mesh3D:
        return self._create_generic_box_mesh(equipment)
    
    def _create_instrument_mesh(self, instrument: BIMElement) -> Optional[Mesh3D]:
        return self._create_generic_box_mesh(instrument)
    
    def _create_generic_box_mesh(self, element: BIMElement) -> Mesh3D:
        """Crea malla de caja genérica"""
        # Dimensiones por defecto
        geometry = element.geometry
        length = geometry.get('length', 1.0)
        width = geometry.get('width', 1.0)
        height = geometry.get('height', 1.0)
        
        vertices = np.array([
            [0, 0, 0], [length, 0, 0], [length, width, 0], [0, width, 0],
            [0, 0, height], [length, 0, height], [length, width, height], [0, width, height]
        ])
        
        faces = np.array([
            [0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4], [2, 7, 6], [2, 3, 7],
            [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5]
        ])
        
        vertices += np.array(element.location)
        
        return Mesh3D(
            vertices=vertices,
            faces=faces,
            material_properties=self.material_library.get('steel', {})
        )
    
    def _setup_scene_lighting(self) -> List[Dict]:
        """Configura iluminación de la escena"""
        return [
            {
                'type': 'directional',
                'direction': [0.5, -0.8, -0.2],
                'intensity': 1.0,
                'color': [1.0, 1.0, 0.9]
            },
            {
                'type': 'ambient',
                'intensity': 0.3,
                'color': [0.9, 0.95, 1.0]
            }
        ]
    
    def _setup_scene_cameras(self, bim_model: PTAPBIMModel) -> List[Dict]:
        """Configura cámaras de la escena"""
        return [
            {
                'name': 'isometric',
                'position': [50, 50, 30],
                'target': [25, 25, 5],
                'fov': 60
            },
            {
                'name': 'overview',
                'position': [0, -50, 20],
                'target': [25, 25, 0],
                'fov': 45
            }
        ]
    
    def _setup_environment(self) -> Dict:
        """Configura entorno de la escena"""
        return {
            'sky_color': [0.5, 0.7, 1.0],
            'ground_color': [0.3, 0.5, 0.3],
            'fog_density': 0.001,
            'ambient_intensity': 0.2
        }
    
    def _generate_web_viewer(self, scene: Scene3D, output_dir: Path) -> Optional[str]:
        """Genera visor web interactivo"""
        # Implementación futura - exportar a three.js/babylon.js
        return None
    
    def _generate_virtual_tour_data(self, scene: Scene3D, output_dir: Path) -> Optional[str]:
        """Genera datos para recorrido virtual"""
        # Implementación futura - puntos de interés, rutas, anotaciones
        return None