"""
Calculadora de Materiales para Proyectos PTAP

Sistema integral de cálculo y optimización de materiales:
- Cuantificación automática desde geometrías 3D/BIM
- Base de datos de proveedores y precios regionales
- Optimización de compras y logística
- Análisis de disponibilidad y tiempos de entrega
- Gestión de desperdicios y rendimientos
- Programación de suministros según cronograma
- Evaluación de materiales alternativos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import math
from pathlib import Path

class MaterialCategory(Enum):
    """Categorías de materiales"""
    CEMENT = "Cemento"
    AGGREGATES = "Agregados"
    STEEL = "Acero"
    PIPES = "Tuberías"
    FITTINGS = "Accesorios"
    CHEMICALS = "Químicos"
    EQUIPMENT = "Equipos"
    ELECTRICAL = "Eléctricos"
    INSTRUMENTS = "Instrumentos"
    CONSUMABLES = "Consumibles"

class MaterialUnit(Enum):
    """Unidades de medida de materiales"""
    KG = "kg"
    TON = "ton"
    M3 = "m3"
    M2 = "m2"
    M = "m"
    PIECES = "pcs"
    LITERS = "L"
    BAGS = "bultos"

class SupplierType(Enum):
    """Tipos de proveedores"""
    MANUFACTURER = "Fabricante"
    DISTRIBUTOR = "Distribuidor"
    RETAILER = "Minorista"
    IMPORTER = "Importador"
    LOCAL_SUPPLIER = "Proveedor local"

@dataclass
class MaterialSpecification:
    """Especificación técnica de material"""
    name: str
    category: MaterialCategory
    unit: MaterialUnit
    technical_specs: Dict
    quality_standards: List[str]
    alternatives: List[str] = field(default_factory=list)
    waste_factor: float = 0.05  # 5% desperdicio por defecto
    bulk_discount_threshold: float = 0  # Cantidad mínima descuento
    
@dataclass
class MaterialPrice:
    """Precio de material por proveedor"""
    material_name: str
    supplier_name: str
    supplier_type: SupplierType
    unit_price: float
    currency: str
    minimum_quantity: float
    delivery_time_days: int
    location: str
    date_updated: datetime
    bulk_discounts: Dict[float, float] = field(default_factory=dict)  # cantidad: descuento%
    payment_terms: str = "Contado"
    warranty_months: int = 12

@dataclass
class MaterialQuantity:
    """Cantidad requerida de material"""
    material_name: str
    gross_quantity: float  # Cantidad bruta calculada
    net_quantity: float   # Cantidad neta con desperdicio
    unit: MaterialUnit
    required_date: datetime
    priority: str = "Medium"  # High, Medium, Low
    notes: str = ""

@dataclass
class ProcurementPlan:
    """Plan de procuración de materiales"""
    material_requirements: List[MaterialQuantity]
    supplier_selections: Dict[str, str]  # material: supplier
    delivery_schedule: Dict[str, datetime]
    total_cost: float
    cost_breakdown: Dict[MaterialCategory, float]
    logistics_plan: Dict
    risk_assessment: Dict
    
class MaterialCalculator:
    """
    Calculadora integral de materiales para proyectos PTAP
    
    Funcionalidades:
    - Cuantificación automática desde modelos BIM/3D
    - Base de datos de materiales y especificaciones
    - Optimización de proveedores y costos
    - Programación de suministros
    - Análisis de alternativas
    - Gestión de desperdicios
    """
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or self._default_config()
        
        # Base de datos de materiales
        self.material_specifications = self._initialize_material_database()
        self.supplier_database = self._initialize_supplier_database()
        self.price_history = self._initialize_price_history()
        
        # Configuraciones regionales
        self.regional_factors = self._load_regional_factors()
        self.logistics_costs = self._load_logistics_costs()
        
    def _default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            'base_currency': 'COP',
            'default_waste_factor': 0.05,  # 5%
            'price_validity_days': 30,
            'preferred_supplier_bonus': 0.05,  # 5% descuento preferencial
            'bulk_discount_threshold': 1000000,  # COP
            'max_delivery_time_days': 45,
            'quality_priority_weight': 0.4,
            'cost_priority_weight': 0.4,
            'delivery_priority_weight': 0.2
        }
    
    def _initialize_material_database(self) -> Dict[str, MaterialSpecification]:
        """Inicializa base de datos de especificaciones de materiales"""
        materials = {}
        
        # Cemento
        materials['cement_portland_type1'] = MaterialSpecification(
            name="Cemento Portland Tipo I",
            category=MaterialCategory.CEMENT,
            unit=MaterialUnit.BAGS,
            technical_specs={
                'compressive_strength_28d': '21 MPa mínimo',
                'fineness_blaine': '2800-3500 cm2/g',
                'setting_time_initial': '45-375 min',
                'weight_per_bag': '50 kg'
            },
            quality_standards=['NTC 121', 'ASTM C150', 'ICONTEC'],
            alternatives=['cement_portland_type2', 'cement_blended'],
            waste_factor=0.03  # 3% para cemento
        )
        
        # Agregado fino
        materials['fine_aggregate'] = MaterialSpecification(
            name="Arena de río lavada",
            category=MaterialCategory.AGGREGATES,
            unit=MaterialUnit.M3,
            technical_specs={
                'fineness_modulus': '2.3-3.1',
                'organic_impurities': 'Máximo 3% (NTC 127)',
                'moisture_content': 'Máximo 5%',
                'density': '1600 kg/m3 promedio'
            },
            quality_standards=['NTC 174', 'ASTM C33'],
            alternatives=['manufactured_sand', 'crushed_sand'],
            waste_factor=0.08  # 8% para agregados
        )
        
        # Agregado grueso
        materials['coarse_aggregate'] = MaterialSpecification(
            name="Grava triturada 3/4"",
            category=MaterialCategory.AGGREGATES,
            unit=MaterialUnit.M3,
            technical_specs={
                'maximum_size': '19 mm (3/4")',
                'abrasion_resistance': 'Máximo 50% (NTC 93)',
                'absorption': 'Máximo 3%',
                'density': '1450 kg/m3 promedio'
            },
            quality_standards=['NTC 174', 'ASTM C33'],
            alternatives=['river_gravel', 'recycled_aggregate'],
            waste_factor=0.06  # 6% para grava
        )
        
        # Acero de refuerzo
        materials['steel_rebar_60k'] = MaterialSpecification(
            name="Varilla corrugada 60k",
            category=MaterialCategory.STEEL,
            unit=MaterialUnit.KG,
            technical_specs={
                'yield_strength': '420 MPa (60 ksi)',
                'tensile_strength': '630 MPa mínimo',
                'elongation': '12% mínimo',
                'diameter_range': '6mm - 32mm'
            },
            quality_standards=['NTC 2289', 'ASTM A615', 'ICONTEC 248'],
            alternatives=['steel_rebar_40k', 'stainless_steel_rebar'],
            waste_factor=0.10  # 10% para acero (cortes, traslapes)
        )
        
        # Tubería PVC
        materials['pvc_pipe_pressure'] = MaterialSpecification(
            name="Tubería PVC presión RDE-41",
            category=MaterialCategory.PIPES,
            unit=MaterialUnit.M,
            technical_specs={
                'pressure_rating': '1.0 MPa (10 bar)',
                'diameter_range': '50mm - 500mm',
                'material': 'PVC-U',
                'standard_length': '6 metros'
            },
            quality_standards=['NTC 382', 'ASTM D1785', 'ISO 1452'],
            alternatives=['hdpe_pipe', 'steel_pipe'],
            waste_factor=0.05  # 5% para tubería
        )
        
        # Accesorios PVC
        materials['pvc_fittings'] = MaterialSpecification(
            name="Accesorios PVC presión",
            category=MaterialCategory.FITTINGS,
            unit=MaterialUnit.PIECES,
            technical_specs={
                'pressure_rating': '1.0 MPa',
                'types': ['codos', 'tés', 'reducciones', 'tapones'],
                'connection': 'Cementado'
            },
            quality_standards=['NTC 382', 'ASTM D2466'],
            waste_factor=0.02  # 2% para accesorios
        )
        
        # Químicos
        materials['coagulant_aluminum_sulfate'] = MaterialSpecification(
            name="Sulfato de aluminio (Coagulante)",
            category=MaterialCategory.CHEMICALS,
            unit=MaterialUnit.KG,
            technical_specs={
                'al2o3_content': '17% mínimo',
                'water_solubility': '100%',
                'ph_solution': '3.5 - 5.0',
                'iron_content': '1.5% máximo'
            },
            quality_standards=['AWWA B403', 'NTC 1126'],
            alternatives=['polyaluminum_chloride', 'ferric_chloride'],
            waste_factor=0.01  # 1% para químicos
        )
        
        return materials
    
    def _initialize_supplier_database(self) -> Dict[str, Dict]:
        """Inicializa base de datos de proveedores"""
        suppliers = {
            'cemex_colombia': {
                'name': 'CEMEX Colombia',
                'type': SupplierType.MANUFACTURER,
                'location': 'Bogotá',
                'products': ['cement_portland_type1'],
                'rating': 4.5,
                'certifications': ['ISO 9001', 'ISO 14001'],
                'payment_terms': ['Contado', '30 días'],
                'delivery_coverage': ['Nacional'],
                'contact': {
                    'phone': '+57-1-555-0001',
                    'email': 'ventas@cemex.com.co',
                    'website': 'www.cemex.com.co'
                }
            },
            'argos_colombia': {
                'name': 'Cementos Argos',
                'type': SupplierType.MANUFACTURER,
                'location': 'Medellín',
                'products': ['cement_portland_type1', 'fine_aggregate'],
                'rating': 4.3,
                'certifications': ['ISO 9001', 'OHSAS 18001'],
                'payment_terms': ['Contado', '45 días'],
                'delivery_coverage': ['Nacional', 'Internacional']
            },
            'pavco_mexichem': {
                'name': 'PAVCO - Mexichem',
                'type': SupplierType.MANUFACTURER,
                'location': 'Bogotá',
                'products': ['pvc_pipe_pressure', 'pvc_fittings'],
                'rating': 4.7,
                'certifications': ['ISO 9001', 'ICONTEC'],
                'payment_terms': ['Contado', '60 días'],
                'delivery_coverage': ['Nacional']
            },
            'gerdau_diaco': {
                'name': 'Gerdau Diaco',
                'type': SupplierType.MANUFACTURER,
                'location': 'Tocancipá',
                'products': ['steel_rebar_60k'],
                'rating': 4.4,
                'certifications': ['ISO 9001', 'ICONTEC 248'],
                'payment_terms': ['Contado', '30 días'],
                'delivery_coverage': ['Nacional']
            },
            'agregados_el_cairo': {
                'name': 'Agregados El Cairo',
                'type': SupplierType.LOCAL_SUPPLIER,
                'location': 'Cundinamarca',
                'products': ['fine_aggregate', 'coarse_aggregate'],
                'rating': 4.1,
                'certifications': ['ICONTEC'],
                'payment_terms': ['Contado'],
                'delivery_coverage': ['Regional']
            }
        }
        
        return suppliers
    
    def _initialize_price_history(self) -> Dict:
        """Inicializa historial de precios"""
        return {
            'cement_portland_type1': {
                'current_price_range': {'min': 18000, 'max': 22000, 'avg': 20000},  # COP/bulto
                'price_trend': 'stable',
                'volatility': 0.08,  # 8%
                'seasonal_factors': {'dry_season': 1.05, 'rainy_season': 0.98}
            },
            'fine_aggregate': {
                'current_price_range': {'min': 45000, 'max': 65000, 'avg': 55000},  # COP/m3
                'price_trend': 'increasing',
                'volatility': 0.12,
                'seasonal_factors': {'dry_season': 1.10, 'rainy_season': 0.90}
            },
            'coarse_aggregate': {
                'current_price_range': {'min': 42000, 'max': 58000, 'avg': 50000},  # COP/m3
                'price_trend': 'increasing',
                'volatility': 0.10,
                'seasonal_factors': {'dry_season': 1.08, 'rainy_season': 0.92}
            },
            'steel_rebar_60k': {
                'current_price_range': {'min': 2800, 'max': 3200, 'avg': 3000},  # COP/kg
                'price_trend': 'volatile',
                'volatility': 0.18,
                'seasonal_factors': {'high_construction': 1.12, 'low_construction': 0.88}
            },
            'pvc_pipe_pressure': {
                'current_price_range': {'min': 15000, 'max': 45000, 'avg': 25000},  # COP/m (varía por diámetro)
                'price_trend': 'stable',
                'volatility': 0.06,
                'seasonal_factors': {'normal': 1.0}
            }
        }
    
    def _load_regional_factors(self) -> Dict:
        """Factores de ajuste regional"""
        return {
            'Bogotá': {
                'availability_factor': 1.0,
                'transportation_factor': 1.0,
                'competition_factor': 1.0
            },
            'Medellín': {
                'availability_factor': 0.95,
                'transportation_factor': 1.05,
                'competition_factor': 0.98
            },
            'Cali': {
                'availability_factor': 0.90,
                'transportation_factor': 1.08,
                'competition_factor': 0.96
            },
            'remote_areas': {
                'availability_factor': 0.75,
                'transportation_factor': 1.35,
                'competition_factor': 0.85
            }
        }
    
    def _load_logistics_costs(self) -> Dict:
        """Costos logísticos por tipo de material"""
        return {
            MaterialCategory.CEMENT: {
                'cost_per_km_per_ton': 150,  # COP
                'handling_cost_per_ton': 5000,
                'storage_cost_per_ton_per_day': 100
            },
            MaterialCategory.AGGREGATES: {
                'cost_per_km_per_ton': 120,
                'handling_cost_per_ton': 3000,
                'storage_cost_per_ton_per_day': 50
            },
            MaterialCategory.STEEL: {
                'cost_per_km_per_ton': 200,
                'handling_cost_per_ton': 8000,
                'storage_cost_per_ton_per_day': 150
            },
            MaterialCategory.PIPES: {
                'cost_per_km_per_ton': 180,
                'handling_cost_per_ton': 6000,
                'storage_cost_per_ton_per_day': 80
            }
        }
    
    def calculate_material_requirements(self, 
                                      design_parameters: Dict,
                                      construction_methods: Dict = None) -> List[MaterialQuantity]:
        """
        Calcula requerimientos de materiales desde parámetros de diseño
        
        Args:
            design_parameters: Parámetros del diseño PTAP
            construction_methods: Métodos constructivos especificados
            
        Returns:
            Lista de MaterialQuantity requeridas
        """
        try:
            self.logger.info("Calculando requerimientos de materiales")
            
            material_requirements = []
            project_start = datetime.now() + timedelta(days=60)  # Inicio en 2 meses
            
            # Extraer cantidades de obra
            concrete_volume = design_parameters.get('concrete_volume_total_m3', 0)
            steel_weight = design_parameters.get('steel_weight_total_kg', 0)
            piping_length = design_parameters.get('piping_length_total_m', 0)
            
            if concrete_volume == 0:
                concrete_volume = self._estimate_concrete_volume(design_parameters)
            
            if steel_weight == 0:
                steel_weight = concrete_volume * 120  # 120 kg/m3 promedio
            
            if piping_length == 0:
                piping_length = design_parameters.get('caudal_diseno_ls', 50) * 3  # Factor empírico
            
            # Cemento (7.5 bultos por m3 de concreto)
            cement_bags = concrete_volume * 7.5
            cement_spec = self.material_specifications['cement_portland_type1']
            cement_with_waste = cement_bags * (1 + cement_spec.waste_factor)
            
            material_requirements.append(MaterialQuantity(
                material_name='cement_portland_type1',
                gross_quantity=cement_bags,
                net_quantity=cement_with_waste,
                unit=MaterialUnit.BAGS,
                required_date=project_start + timedelta(days=30),
                priority='High',
                notes='Requerido para fundaciones y estructuras'
            ))
            
            # Arena (0.5 m3 por m3 de concreto)
            fine_agg_volume = concrete_volume * 0.5
            fine_agg_spec = self.material_specifications['fine_aggregate']
            fine_agg_with_waste = fine_agg_volume * (1 + fine_agg_spec.waste_factor)
            
            material_requirements.append(MaterialQuantity(
                material_name='fine_aggregate',
                gross_quantity=fine_agg_volume,
                net_quantity=fine_agg_with_waste,
                unit=MaterialUnit.M3,
                required_date=project_start + timedelta(days=25),
                priority='High',
                notes='Arena lavada para concreto estructural'
            ))
            
            # Grava (0.8 m3 por m3 de concreto)
            coarse_agg_volume = concrete_volume * 0.8
            coarse_agg_spec = self.material_specifications['coarse_aggregate']
            coarse_agg_with_waste = coarse_agg_volume * (1 + coarse_agg_spec.waste_factor)
            
            material_requirements.append(MaterialQuantity(
                material_name='coarse_aggregate',
                gross_quantity=coarse_agg_volume,
                net_quantity=coarse_agg_with_waste,
                unit=MaterialUnit.M3,
                required_date=project_start + timedelta(days=25),
                priority='High',
                notes='Grava triturada 3/4" para concreto'
            ))
            
            # Acero de refuerzo
            steel_spec = self.material_specifications['steel_rebar_60k']
            steel_with_waste = steel_weight * (1 + steel_spec.waste_factor)
            
            material_requirements.append(MaterialQuantity(
                material_name='steel_rebar_60k',
                gross_quantity=steel_weight,
                net_quantity=steel_with_waste,
                unit=MaterialUnit.KG,
                required_date=project_start + timedelta(days=20),
                priority='High',
                notes='Varilla corrugada 60k diversos diámetros'
            ))
            
            # Tubería PVC
            pvc_spec = self.material_specifications['pvc_pipe_pressure']
            piping_with_waste = piping_length * (1 + pvc_spec.waste_factor)
            
            material_requirements.append(MaterialQuantity(
                material_name='pvc_pipe_pressure',
                gross_quantity=piping_length,
                net_quantity=piping_with_waste,
                unit=MaterialUnit.M,
                required_date=project_start + timedelta(days=45),
                priority='Medium',
                notes='Tubería PVC presión diversos diámetros'
            ))
            
            # Accesorios PVC (15% del metraje de tubería)
            fittings_quantity = piping_length * 0.15
            fittings_spec = self.material_specifications['pvc_fittings']
            fittings_with_waste = fittings_quantity * (1 + fittings_spec.waste_factor)
            
            material_requirements.append(MaterialQuantity(
                material_name='pvc_fittings',
                gross_quantity=fittings_quantity,
                net_quantity=fittings_with_waste,
                unit=MaterialUnit.PIECES,
                required_date=project_start + timedelta(days=45),
                priority='Medium',
                notes='Accesorios PVC: codos, tés, reducciones'
            ))
            
            # Químicos de tratamiento
            caudal_ls = design_parameters.get('caudal_diseno_ls', 50)
            chemical_consumption_annual = caudal_ls * 0.365 * 365  # kg/año estimado
            
            material_requirements.append(MaterialQuantity(
                material_name='coagulant_aluminum_sulfate',
                gross_quantity=chemical_consumption_annual,
                net_quantity=chemical_consumption_annual * 1.01,  # 1% desperdicio
                unit=MaterialUnit.KG,
                required_date=project_start + timedelta(days=90),
                priority='Low',
                notes='Coagulante para tratamiento - suministro anual'
            ))
            
            self.logger.info(f"Calculados {len(material_requirements)} tipos de materiales")
            return material_requirements
            
        except Exception as e:
            self.logger.error(f"Error calculando requerimientos: {e}")
            return []
    
    def _estimate_concrete_volume(self, design_parameters: Dict) -> float:
        """Estima volumen total de concreto"""
        caudal_ls = design_parameters.get('caudal_diseno_ls', 50)
        
        # Estimación paramétrica basada en caudal
        if caudal_ls <= 25:
            concrete_factor = 4.0  # m3 por L/s
        elif caudal_ls <= 100:
            concrete_factor = 3.5
        elif caudal_ls <= 300:
            concrete_factor = 3.0
        else:
            concrete_factor = 2.5
        
        estimated_volume = caudal_ls * concrete_factor
        
        # Ajustar por procesos incluidos
        if design_parameters.get('incluir_sedimentacion', True):
            estimated_volume *= 1.3
        
        if design_parameters.get('incluir_filtracion', True):
            estimated_volume *= 1.2
        
        if design_parameters.get('incluir_floculacion', True):
            estimated_volume *= 1.1
        
        return estimated_volume
    
    def optimize_supplier_selection(self, 
                                  material_requirements: List[MaterialQuantity],
                                  project_location: str = 'Bogotá',
                                  optimization_criteria: Dict = None) -> ProcurementPlan:
        """
        Optimiza selección de proveedores
        
        Args:
            material_requirements: Requerimientos de materiales
            project_location: Ubicación del proyecto
            optimization_criteria: Criterios de optimización
            
        Returns:
            Plan de procuración optimizado
        """
        try:
            if not optimization_criteria:
                optimization_criteria = {
                    'cost_weight': 0.5,
                    'quality_weight': 0.3,
                    'delivery_weight': 0.2
                }
            
            self.logger.info(f"Optimizando proveedores para {len(material_requirements)} materiales")
            
            supplier_selections = {}
            delivery_schedule = {}
            cost_breakdown = {category: 0.0 for category in MaterialCategory}
            total_cost = 0
            
            for req in material_requirements:
                material_name = req.material_name
                
                # Obtener materiales especificación
                if material_name not in self.material_specifications:
                    self.logger.warning(f"Material {material_name} no encontrado en especificaciones")
                    continue
                
                material_spec = self.material_specifications[material_name]
                
                # Encontrar proveedores disponibles
                available_suppliers = self._find_suppliers_for_material(material_name)
                
                if not available_suppliers:
                    self.logger.warning(f"No se encontraron proveedores para {material_name}")
                    continue
                
                # Evaluar proveedores
                best_supplier, best_price, delivery_date = self._evaluate_suppliers(
                    available_suppliers, req, project_location, optimization_criteria
                )
                
                if best_supplier:
                    supplier_selections[material_name] = best_supplier
                    delivery_schedule[material_name] = delivery_date
                    
                    material_cost = req.net_quantity * best_price
                    total_cost += material_cost
                    cost_breakdown[material_spec.category] += material_cost
            
            # Crear plan logístico
            logistics_plan = self._create_logistics_plan(
                material_requirements, supplier_selections, project_location
            )
            
            # Evaluación de riesgos
            risk_assessment = self._assess_procurement_risks(
                material_requirements, supplier_selections
            )
            
            procurement_plan = ProcurementPlan(
                material_requirements=material_requirements,
                supplier_selections=supplier_selections,
                delivery_schedule=delivery_schedule,
                total_cost=total_cost,
                cost_breakdown=cost_breakdown,
                logistics_plan=logistics_plan,
                risk_assessment=risk_assessment
            )
            
            self.logger.info(f"Plan de procuración optimizado. Costo total: ${total_cost:,.0f} COP")
            return procurement_plan
            
        except Exception as e:
            self.logger.error(f"Error optimizando proveedores: {e}")
            raise
    
    def _find_suppliers_for_material(self, material_name: str) -> List[str]:
        """Encuentra proveedores disponibles para un material"""
        available_suppliers = []
        
        for supplier_id, supplier_info in self.supplier_database.items():
            if material_name in supplier_info.get('products', []):
                available_suppliers.append(supplier_id)
        
        return available_suppliers
    
    def _evaluate_suppliers(self, 
                          suppliers: List[str], 
                          requirement: MaterialQuantity,
                          project_location: str,
                          criteria: Dict) -> Tuple[str, float, datetime]:
        """Evalúa proveedores para un material específico"""
        best_supplier = None
        best_score = -1
        best_price = float('inf')
        best_delivery = None
        
        material_name = requirement.material_name
        
        for supplier_id in suppliers:
            supplier_info = self.supplier_database[supplier_id]
            
            # Obtener precio
            price = self._get_material_price(material_name, supplier_id, requirement.net_quantity)
            
            # Calcular tiempo de entrega
            base_delivery = 15  # Días base
            location_delay = self._calculate_location_delay(supplier_info['location'], project_location)
            delivery_time = base_delivery + location_delay
            delivery_date = datetime.now() + timedelta(days=delivery_time)
            
            # Calcular puntaje de calidad
            quality_score = supplier_info.get('rating', 3.0) / 5.0  # Normalizar a 0-1
            
            # Calcular puntaje de costo (inverso normalizado)
            if material_name in self.price_history:
                avg_market_price = self.price_history[material_name]['current_price_range']['avg']
                cost_score = min(1.0, avg_market_price / price) if price > 0 else 0
            else:
                cost_score = 0.5  # Puntaje neutro si no hay referencia
            
            # Calcular puntaje de entrega
            max_acceptable_delivery = 30  # Días
            delivery_score = max(0, (max_acceptable_delivery - delivery_time) / max_acceptable_delivery)
            
            # Puntaje total ponderado
            total_score = (
                cost_score * criteria['cost_weight'] +
                quality_score * criteria['quality_weight'] +
                delivery_score * criteria['delivery_weight']
            )
            
            if total_score > best_score:
                best_score = total_score
                best_supplier = supplier_id
                best_price = price
                best_delivery = delivery_date
        
        return best_supplier, best_price, best_delivery
    
    def _get_material_price(self, material_name: str, supplier_id: str, quantity: float) -> float:
        """Obtiene precio de material de proveedor específico"""
        if material_name in self.price_history:
            price_info = self.price_history[material_name]
            base_price = price_info['current_price_range']['avg']
            
            # Aplicar descuentos por volumen
            if quantity >= 1000:  # Cantidad grande
                volume_discount = 0.05  # 5%
                base_price *= (1 - volume_discount)
            
            # Aplicar factor de proveedor
            supplier_info = self.supplier_database.get(supplier_id, {})
            if supplier_info.get('type') == SupplierType.MANUFACTURER:
                base_price *= 0.95  # 5% descuento fabricante
            elif supplier_info.get('type') == SupplierType.DISTRIBUTOR:
                base_price *= 1.02  # 2% recargo distribuidor
            
            return base_price
        
        return 0.0
    
    def _calculate_location_delay(self, supplier_location: str, project_location: str) -> int:
        """Calcula retraso por ubicación"""
        if supplier_location == project_location:
            return 0
        elif supplier_location in ['Bogotá', 'Medellín', 'Cali'] and project_location in ['Bogotá', 'Medellín', 'Cali']:
            return 2  # 2 días entre ciudades principales
        else:
            return 7  # 7 días para ubicaciones remotas
    
    def _create_logistics_plan(self, 
                             requirements: List[MaterialQuantity],
                             suppliers: Dict[str, str],
                             project_location: str) -> Dict:
        """Crea plan logístico"""
        logistics_plan = {
            'transportation_cost': 0,
            'storage_requirements': {},
            'delivery_sequence': [],
            'special_handling': []
        }
        
        for req in requirements:
            material_name = req.material_name
            if material_name in suppliers:
                supplier_id = suppliers[material_name]
                supplier_info = self.supplier_database[supplier_id]
                
                # Calcular costo de transporte
                distance_km = self._estimate_distance(
                    supplier_info['location'], project_location
                )
                
                material_spec = self.material_specifications[material_name]
                category = material_spec.category
                
                if category in self.logistics_costs:
                    logistics_costs = self.logistics_costs[category]
                    
                    # Estimar peso para cálculo de transporte
                    estimated_weight = self._estimate_material_weight(req)
                    
                    transport_cost = (
                        estimated_weight * distance_km * 
                        logistics_costs['cost_per_km_per_ton'] / 1000
                    )
                    
                    logistics_plan['transportation_cost'] += transport_cost
                
                # Programar entrega
                logistics_plan['delivery_sequence'].append({
                    'material': material_name,
                    'supplier': supplier_id,
                    'quantity': req.net_quantity,
                    'required_date': req.required_date,
                    'priority': req.priority
                })
        
        # Ordenar por fecha requerida y prioridad
        logistics_plan['delivery_sequence'].sort(
            key=lambda x: (x['required_date'], x['priority'])
        )
        
        return logistics_plan
    
    def _assess_procurement_risks(self, 
                                requirements: List[MaterialQuantity],
                                suppliers: Dict[str, str]) -> Dict:
        """Evalúa riesgos de procuración"""
        risks = {
            'supply_chain_risks': [],
            'price_volatility_risks': [],
            'delivery_risks': [],
            'quality_risks': [],
            'mitigation_strategies': []
        }
        
        # Evaluar riesgos por material
        for req in requirements:
            material_name = req.material_name
            
            # Riesgo de volatilidad de precios
            if material_name in self.price_history:
                volatility = self.price_history[material_name].get('volatility', 0)
                if volatility > 0.15:  # Alta volatilidad
                    risks['price_volatility_risks'].append({
                        'material': material_name,
                        'volatility': volatility,
                        'recommendation': 'Considerar compra anticipada o contratos a precio fijo'
                    })
            
            # Riesgo de proveedor único
            available_suppliers = self._find_suppliers_for_material(material_name)
            if len(available_suppliers) == 1:
                risks['supply_chain_risks'].append({
                    'material': material_name,
                    'risk': 'Proveedor único',
                    'recommendation': 'Identificar proveedores alternativos'
                })
        
        # Estrategias de mitigación generales
        risks['mitigation_strategies'] = [
            'Mantener inventario de seguridad para materiales críticos',
            'Establecer contratos marco con proveedores principales',
            'Diversificar proveedores por categoría de material',
            'Implementar seguimiento continuo de precios de mercado'
        ]
        
        return risks
    
    def _estimate_distance(self, origin: str, destination: str) -> float:
        """Estima distancia entre ubicaciones (simplificado)"""
        distances = {
            ('Bogotá', 'Medellín'): 420,
            ('Bogotá', 'Cali'): 460,
            ('Medellín', 'Cali'): 420,
            ('Bogotá', 'Bogotá'): 0,
            ('Medellín', 'Medellín'): 0,
            ('Cali', 'Cali'): 0
        }
        
        key = (origin, destination)
        return distances.get(key, distances.get((destination, origin), 300))
    
    def _estimate_material_weight(self, requirement: MaterialQuantity) -> float:
        """Estima peso de material en toneladas"""
        material_name = requirement.material_name
        quantity = requirement.net_quantity
        
        # Factores de conversión aproximados
        weight_factors = {
            'cement_portland_type1': 0.05,     # 50kg por bulto
            'fine_aggregate': 1.6,            # 1.6 ton/m3
            'coarse_aggregate': 1.45,         # 1.45 ton/m3
            'steel_rebar_60k': 0.001,         # ya está en kg
            'pvc_pipe_pressure': 0.01,        # ~10 kg/m promedio
            'pvc_fittings': 0.002             # ~2 kg/pieza promedio
        }
        
        weight_factor = weight_factors.get(material_name, 0.1)
        return quantity * weight_factor
    
    def generate_procurement_report(self, procurement_plan: ProcurementPlan, 
                                  output_path: str = None) -> Dict:
        """Genera reporte de plan de procuración"""
        try:
            report = {
                'executive_summary': {
                    'total_materials': len(procurement_plan.material_requirements),
                    'total_cost': procurement_plan.total_cost,
                    'selected_suppliers': len(set(procurement_plan.supplier_selections.values())),
                    'delivery_timespan_days': self._calculate_delivery_timespan(procurement_plan),
                    'critical_path_items': self._identify_critical_path_items(procurement_plan)
                },
                'cost_breakdown_by_category': {
                    category.value: cost for category, cost in procurement_plan.cost_breakdown.items()
                },
                'supplier_summary': self._create_supplier_summary(procurement_plan),
                'delivery_schedule': self._format_delivery_schedule(procurement_plan),
                'risk_assessment': procurement_plan.risk_assessment,
                'recommendations': self._generate_procurement_recommendations(procurement_plan)
            }
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                self.logger.info(f"Reporte de procuración exportado: {output_path}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {}
    
    def _calculate_delivery_timespan(self, plan: ProcurementPlan) -> int:
        """Calcula tiempo total de entregas"""
        if not plan.delivery_schedule:
            return 0
        
        dates = list(plan.delivery_schedule.values())
        return (max(dates) - min(dates)).days
    
    def _identify_critical_path_items(self, plan: ProcurementPlan) -> List[str]:
        """Identifica materiales en ruta crítica"""
        critical_items = []
        
        for req in plan.material_requirements:
            if req.priority == 'High':
                critical_items.append(req.material_name)
        
        return critical_items
    
    def _create_supplier_summary(self, plan: ProcurementPlan) -> Dict:
        """Crea resumen de proveedores seleccionados"""
        supplier_summary = {}
        
        for material, supplier_id in plan.supplier_selections.items():
            if supplier_id not in supplier_summary:
                supplier_info = self.supplier_database.get(supplier_id, {})
                supplier_summary[supplier_id] = {
                    'name': supplier_info.get('name', supplier_id),
                    'location': supplier_info.get('location', 'Desconocida'),
                    'rating': supplier_info.get('rating', 0),
                    'materials_supplied': [],
                    'total_value': 0
                }
            
            supplier_summary[supplier_id]['materials_supplied'].append(material)
            
            # Calcular valor total por proveedor
            for req in plan.material_requirements:
                if req.material_name == material:
                    material_cost = req.net_quantity * self._get_material_price(
                        material, supplier_id, req.net_quantity
                    )
                    supplier_summary[supplier_id]['total_value'] += material_cost
        
        return supplier_summary
    
    def _format_delivery_schedule(self, plan: ProcurementPlan) -> List[Dict]:
        """Formatea cronograma de entregas"""
        schedule = []
        
        for material, delivery_date in plan.delivery_schedule.items():
            # Encontrar requerimiento correspondiente
            for req in plan.material_requirements:
                if req.material_name == material:
                    schedule.append({
                        'material': material,
                        'quantity': req.net_quantity,
                        'unit': req.unit.value,
                        'delivery_date': delivery_date.strftime('%Y-%m-%d'),
                        'supplier': plan.supplier_selections.get(material, 'No asignado'),
                        'priority': req.priority
                    })
                    break
        
        # Ordenar por fecha de entrega
        schedule.sort(key=lambda x: x['delivery_date'])
        
        return schedule
    
    def _generate_procurement_recommendations(self, plan: ProcurementPlan) -> List[str]:
        """Genera recomendaciones para procuración"""
        recommendations = []
        
        # Análisis de costo
        total_cost = plan.total_cost
        if total_cost > 500000000:  # > 500M COP
            recommendations.append(
                "Costo total alto. Considerar negociación de descuentos por volumen "
                "o contratos marco con proveedores principales."
            )
        
        # Análisis de proveedores
        unique_suppliers = len(set(plan.supplier_selections.values()))
        if unique_suppliers < 3:
            recommendations.append(
                "Pocos proveedores seleccionados. Considerar diversificación "
                "para reducir riesgos de suministro."
            )
        
        # Análisis de tiempos
        delivery_span = self._calculate_delivery_timespan(plan)
        if delivery_span > 90:
            recommendations.append(
                "Cronograma de entregas extenso. Evaluar posibilidad de "
                "acelerar entregas críticas o ajustar secuencia constructiva."
            )
        
        return recommendations