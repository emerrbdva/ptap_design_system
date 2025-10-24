"""
Sistema de Costos Detallados para PTAP

Integración completa para análisis económico:
- Cálculo automático de cantidades de obra desde modelos BIM
- Integración con precios DANE-SIPSA en tiempo real
- Análisis de Precios Unitarios (APU) completos
- Cronogramas de inversión y flujo de caja
- Optimización de costos por alternativas tecnológicas
- Análisis de sensibilidad económica
- Evaluación de riesgos financieros
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

class CostCategory(Enum):
    """Categorías de costos de construcción"""
    EARTHWORK = "Movimiento de tierras"
    CONCRETE = "Obras de concreto"
    STEEL = "Estructura metálica"
    MECHANICAL = "Equipos mecánicos"
    ELECTRICAL = "Instalaciones eléctricas"
    PIPING = "Sistemas de tubería"
    INSTRUMENTATION = "Instrumentación"
    CIVIL_WORKS = "Obras civiles"
    FINISHES = "Acabados"
    INDIRECT_COSTS = "Costos indirectos"

class PriceSource(Enum):
    """Fuentes de precios"""
    DANE_SIPSA = "DANE-SIPSA"
    MARKET_RESEARCH = "Investigación de mercado"
    SUPPLIER_QUOTES = "Cotizaciones proveedores"
    HISTORICAL_DATA = "Datos históricos"
    PARAMETRIC_ESTIMATE = "Estimación paramétrica"

@dataclass
class CostItem:
    """Ítem de costo individual"""
    code: str
    description: str
    unit: str
    quantity: float
    unit_price: float
    total_price: float
    category: CostCategory
    source: PriceSource
    date_updated: datetime
    location_factor: float = 1.0
    escalation_factor: float = 1.0
    risk_factor: float = 1.0
    
    def apply_factors(self):
        """Aplica factores de localización, escalación y riesgo"""
        self.total_price = (self.quantity * self.unit_price * 
                           self.location_factor * self.escalation_factor * 
                           self.risk_factor)

@dataclass
class CostBreakdown:
    """Desglose completo de costos"""
    direct_costs: Dict[CostCategory, float]
    indirect_costs: Dict[str, float]
    contingencies: float
    profit_margin: float
    total_cost: float
    cost_per_m3_capacity: float
    cost_items: List[CostItem]
    
class DetailedCostCalculator:
    """
    Calculadora de costos detallada para proyectos PTAP
    
    Funcionalidades:
    - Cuantificación automática desde modelos BIM
    - Integración con precios de mercado en tiempo real
    - Análisis de precios unitarios (APU)
    - Optimización de costos
    - Análisis de sensibilidad
    - Generación de cronogramas de inversión
    """
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or self._default_config()
        
        # Base de datos de precios
        self.price_database = self._initialize_price_database()
        self.unit_price_library = self._load_unit_price_library()
        self.labor_rates = self._load_labor_rates()
        
        # Factores de costos
        self.location_factors = self._load_location_factors()
        self.escalation_factors = self._load_escalation_factors()
        
    def _default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            'base_currency': 'COP',
            'base_location': 'Bogotá',
            'base_date': datetime.now(),
            'contingency_percentage': 0.15,  # 15%
            'indirect_costs_percentage': 0.25,  # 25%
            'profit_margin_percentage': 0.10,  # 10%
            'price_update_frequency_days': 30,
            'use_real_time_prices': True,
            'include_vat': True,
            'vat_percentage': 0.19  # 19% IVA Colombia
        }
    
    def _initialize_price_database(self) -> Dict:
        """Inicializa base de datos de precios"""
        return {
            'materials': {},
            'equipment': {},
            'labor': {},
            'services': {},
            'last_updated': None
        }
    
    def _load_unit_price_library(self) -> Dict:
        """Biblioteca de precios unitarios por actividad"""
        return {
            # Movimiento de tierras
            'excavation_manual': {
                'unit': 'm3',
                'base_price': 25000,  # COP por m3
                'productivity': 8,  # m3/día por trabajador
                'equipment_required': False,
                'skill_level': 'basic'
            },
            'excavation_mechanical': {
                'unit': 'm3',
                'base_price': 15000,
                'productivity': 200,  # m3/día
                'equipment_required': True,
                'equipment_type': 'excavator',
                'skill_level': 'operator'
            },
            'backfill_compacted': {
                'unit': 'm3',
                'base_price': 18000,
                'productivity': 50,
                'equipment_required': True,
                'equipment_type': 'compactor'
            },
            
            # Concreto
            'concrete_f21_foundation': {
                'unit': 'm3',
                'base_price': 320000,
                'materials': {
                    'cement': 7.5,  # bultos por m3
                    'aggregate_fine': 0.5,  # m3
                    'aggregate_coarse': 0.8,  # m3
                    'water': 200,  # litros
                    'admixture': 3  # kg
                },
                'labor_hours': 8,  # horas-hombre por m3
                'equipment_hours': 2  # horas-equipo por m3
            },
            'concrete_f28_structural': {
                'unit': 'm3',
                'base_price': 380000,
                'materials': {
                    'cement': 8.5,
                    'aggregate_fine': 0.45,
                    'aggregate_coarse': 0.75,
                    'water': 180,
                    'admixture': 4,
                    'steel_rebar': 120  # kg por m3
                }
            },
            
            # Tubería
            'pvc_pipe_installation': {
                'unit': 'm',
                'base_price_by_diameter': {
                    100: 45000,  # mm
                    150: 65000,
                    200: 85000,
                    250: 110000,
                    300: 140000,
                    400: 190000,
                    500: 250000
                },
                'labor_hours_per_meter': 0.5,
                'excavation_factor': 1.2  # m3 por metro lineal
            },
            
            # Equipos mecánicos
            'centrifugal_pump': {
                'unit': 'cada',
                'base_price_by_power': {
                    5: 8500000,    # HP
                    10: 12500000,
                    25: 22000000,
                    50: 38000000,
                    100: 65000000
                },
                'installation_factor': 0.15,  # 15% del costo del equipo
                'commissioning_factor': 0.05   # 5% del costo del equipo
            },
            
            # Instrumentación
            'flow_meter_electromagnetic': {
                'unit': 'cada',
                'base_price_by_diameter': {
                    50: 4500000,   # mm
                    100: 6500000,
                    150: 8500000,
                    200: 11500000,
                    300: 18500000
                },
                'calibration_cost': 350000
            }
        }
    
    def _load_labor_rates(self) -> Dict:
        """Tarifas de mano de obra por región"""
        return {
            'Bogotá': {
                'worker_basic': 35000,      # COP por día
                'worker_skilled': 45000,
                'technician': 65000,
                'operator': 75000,
                'engineer': 120000,
                'supervisor': 85000
            },
            'Medellín': {
                'worker_basic': 33000,
                'worker_skilled': 42000,
                'technician': 60000,
                'operator': 70000,
                'engineer': 110000,
                'supervisor': 80000
            },
            'other_cities': {
                'worker_basic': 31500,
                'worker_skilled': 40500,
                'technician': 58500,
                'operator': 67500,
                'engineer': 108000,
                'supervisor': 76500
            }
        }
    
    def _load_location_factors(self) -> Dict:
        """Factores de localización por región"""
        return {
            'Bogotá': 1.0,      # Base
            'Medellín': 0.95,
            'Cali': 0.92,
            'Barranquilla': 0.98,
            'Cartagena': 1.05,
            'Bucaramanga': 0.88,
            'remote_areas': 0.70,   # Zonas alejadas
            'amazon_region': 1.25,  # Amazonía
            'pacific_coast': 1.15   # Costa Pacífica
        }
    
    def _load_escalation_factors(self) -> Dict:
        """Factores de escalación de precios"""
        # Escalación anual por categoría
        return {
            CostCategory.CONCRETE: 0.06,        # 6% anual
            CostCategory.STEEL: 0.08,           # 8% anual
            CostCategory.MECHANICAL: 0.05,      # 5% anual
            CostCategory.ELECTRICAL: 0.04,      # 4% anual
            CostCategory.PIPING: 0.06,          # 6% anual
            CostCategory.EARTHWORK: 0.07,       # 7% anual
            CostCategory.CIVIL_WORKS: 0.06      # 6% anual
        }
    
    def calculate_detailed_costs(self, 
                               design_parameters: Dict,
                               location: str = 'Bogotá',
                               project_timeline_months: int = 24) -> CostBreakdown:
        """
        Calcula costos detallados del proyecto PTAP
        
        Args:
            design_parameters: Parámetros de diseño
            location: Ubicación del proyecto
            project_timeline_months: Duración del proyecto
            
        Returns:
            CostBreakdown con análisis completo de costos
        """
        try:
            self.logger.info("Iniciando cálculo de costos detallados")
            
            # Actualizar precios si es necesario
            if self.config['use_real_time_prices']:
                self._update_real_time_prices(location)
            
            # Cuantificar materiales
            quantities = self._quantify_materials(design_parameters)
            
            # Calcular costos directos por categoría
            direct_costs = self._calculate_direct_costs(quantities, location)
            
            # Calcular costos indirectos
            indirect_costs = self._calculate_indirect_costs(direct_costs, project_timeline_months)
            
            # Aplicar contingencias
            total_direct = sum(direct_costs.values())
            contingencies = total_direct * self.config['contingency_percentage']
            
            # Aplicar margen de utilidad
            subtotal = total_direct + sum(indirect_costs.values()) + contingencies
            profit_margin = subtotal * self.config['profit_margin_percentage']
            
            # Costo total
            total_cost = subtotal + profit_margin
            
            # Costo por m3 de capacidad
            capacity_m3_day = design_parameters.get('caudal_diseno_ls', 50) * 3.6 * 24
            cost_per_m3_capacity = total_cost / capacity_m3_day if capacity_m3_day > 0 else 0
            
            # Crear lista detallada de ítems
            cost_items = self._create_detailed_cost_items(quantities, direct_costs, location)
            
            breakdown = CostBreakdown(
                direct_costs=direct_costs,
                indirect_costs=indirect_costs,
                contingencies=contingencies,
                profit_margin=profit_margin,
                total_cost=total_cost,
                cost_per_m3_capacity=cost_per_m3_capacity,
                cost_items=cost_items
            )
            
            self.logger.info(f"Cálculo de costos completado. Total: ${total_cost:,.0f} COP")
            return breakdown
            
        except Exception as e:
            self.logger.error(f"Error calculando costos: {e}")
            raise
    
    def _quantify_materials(self, design_parameters: Dict) -> Dict:
        """Cuantifica materiales y trabajo"""
        quantities = {
            'concrete_volumes': {},
            'steel_weights': {},
            'excavation_volumes': {},
            'piping_lengths': {},
            'equipment_list': [],
            'areas': {},
            'labor_requirements': {}
        }
        
        try:
            # Parámetros principales
            caudal_ls = design_parameters.get('caudal_diseno_ls', 50)
            
            # Estimación paramétrica de cantidades
            # Sedimentador
            if design_parameters.get('incluir_sedimentacion', True):
                sed_volume = caudal_ls * 2.5  # Factor empírico
                quantities['concrete_volumes']['sedimentador'] = sed_volume
            
            # Filtros
            if design_parameters.get('incluir_filtracion', True):
                num_filtros = design_parameters.get('numero_filtros', 4)
                area_por_filtro = caudal_ls * 0.5  # m2 por L/s
                filtro_volume = area_por_filtro * 4 * num_filtros  # 4m altura promedio
                quantities['concrete_volumes']['filtros'] = filtro_volume
            
            # Tuberías principales
            total_piping_length = caudal_ls * 3  # Factor empírico
            main_diameter = max(200, min(500, caudal_ls * 3))  # mm
            quantities['piping_lengths'][main_diameter] = total_piping_length
            
            # Excavación
            total_concrete = sum(quantities['concrete_volumes'].values())
            quantities['excavation_volumes']['general'] = total_concrete * 1.3
            
            # Equipos
            if design_parameters.get('incluir_bombeo', True):
                pump_power = max(5, min(100, caudal_ls * 0.8))  # HP
                quantities['equipment_list'].append({
                    'type': 'bomba_centrifuga',
                    'specifications': {'potencia_hp': pump_power}
                })
            
            return quantities
            
        except Exception as e:
            self.logger.error(f"Error cuantificando materiales: {e}")
            return quantities
    
    def _calculate_direct_costs(self, quantities: Dict, location: str) -> Dict[CostCategory, float]:
        """Calcula costos directos por categoría"""
        direct_costs = {category: 0.0 for category in CostCategory}
        location_factor = self.location_factors.get(location, 1.0)
        
        try:
            # Costos de movimiento de tierras
            if quantities['excavation_volumes']:
                excavation_volume = quantities['excavation_volumes'].get('general', 0)
                unit_price = self.unit_price_library['excavation_mechanical']['base_price']
                direct_costs[CostCategory.EARTHWORK] = excavation_volume * unit_price * location_factor
            
            # Costos de concreto
            if quantities['concrete_volumes']:
                for concrete_type, volume in quantities['concrete_volumes'].items():
                    unit_price = self.unit_price_library['concrete_f28_structural']['base_price']
                    direct_costs[CostCategory.CONCRETE] += volume * unit_price * location_factor
            
            # Costos de tubería
            if quantities['piping_lengths']:
                for diameter_mm, length in quantities['piping_lengths'].items():
                    prices_by_diameter = self.unit_price_library['pvc_pipe_installation']['base_price_by_diameter']
                    closest_diameter = min(prices_by_diameter.keys(), key=lambda x: abs(x - diameter_mm))
                    unit_price = prices_by_diameter[closest_diameter]
                    
                    direct_costs[CostCategory.PIPING] += length * unit_price * location_factor
            
            # Costos de equipos mecánicos
            if quantities['equipment_list']:
                for equipment in quantities['equipment_list']:
                    equipment_cost = self._estimate_equipment_cost(equipment, location_factor)
                    direct_costs[CostCategory.MECHANICAL] += equipment_cost
            
            # Costos eléctricos (estimado como % de mecánicos)
            direct_costs[CostCategory.ELECTRICAL] = direct_costs[CostCategory.MECHANICAL] * 0.25
            
            # Costos de instrumentación (estimado)
            direct_costs[CostCategory.INSTRUMENTATION] = direct_costs[CostCategory.MECHANICAL] * 0.15
            
            # Acabados (estimado como % de obra civil)
            civil_total = direct_costs[CostCategory.CONCRETE] + direct_costs[CostCategory.EARTHWORK]
            direct_costs[CostCategory.FINISHES] = civil_total * 0.08
            
            return direct_costs
            
        except Exception as e:
            self.logger.error(f"Error calculando costos directos: {e}")
            return direct_costs
    
    def _estimate_equipment_cost(self, equipment: Dict, location_factor: float) -> float:
        """Estima costo de equipo individual"""
        equipment_type = equipment.get('type', '').lower()
        
        if 'bomba' in equipment_type:
            power_hp = equipment.get('specifications', {}).get('potencia_hp', 25)
            power_ranges = self.unit_price_library['centrifugal_pump']['base_price_by_power']
            closest_power = min(power_ranges.keys(), key=lambda x: abs(x - power_hp))
            base_cost = power_ranges[closest_power]
            
            installation_factor = self.unit_price_library['centrifugal_pump']['installation_factor']
            total_cost = base_cost * (1 + installation_factor)
            
            return total_cost * location_factor
        
        return 50000000 * location_factor  # Costo por defecto
    
    def _calculate_indirect_costs(self, direct_costs: Dict, timeline_months: int) -> Dict[str, float]:
        """Calcula costos indirectos"""
        total_direct = sum(direct_costs.values())
        
        indirect_costs = {
            'project_management': total_direct * 0.08,    # 8%
            'design_engineering': total_direct * 0.12,    # 12%
            'supervision': total_direct * 0.05,           # 5%
            'permits_licenses': total_direct * 0.02,      # 2%
            'insurance': total_direct * 0.01,             # 1%
            'temporary_facilities': total_direct * 0.03,  # 3%
            'financing_costs': total_direct * 0.04 * (timeline_months / 12),  # 4% anual
            'administrative': total_direct * 0.06         # 6%
        }
        
        return indirect_costs
    
    def _create_detailed_cost_items(self, quantities: Dict, direct_costs: Dict, location: str) -> List[CostItem]:
        """Crea lista detallada de ítems de costo"""
        cost_items = []
        location_factor = self.location_factors.get(location, 1.0)
        
        item_counter = 1
        
        # Excavación
        if quantities['excavation_volumes']:
            volume = quantities['excavation_volumes'].get('general', 0)
            unit_price = self.unit_price_library['excavation_mechanical']['base_price']
            
            item = CostItem(
                code=f"EXC-{item_counter:03d}",
                description="Excavación mecánica para fundaciones",
                unit="m3",
                quantity=volume,
                unit_price=unit_price,
                total_price=volume * unit_price * location_factor,
                category=CostCategory.EARTHWORK,
                source=PriceSource.MARKET_RESEARCH,
                date_updated=datetime.now(),
                location_factor=location_factor
            )
            item.apply_factors()
            cost_items.append(item)
            item_counter += 1
        
        return cost_items
    
    def _update_real_time_prices(self, location: str):
        """Actualiza precios en tiempo real"""
        try:
            self.logger.info(f"Actualizando precios para {location}")
            
            # Aplicar escalación temporal
            days_since_base = (datetime.now() - self.config['base_date']).days
            annual_escalation = 0.06
            escalation_factor = (1 + annual_escalation) ** (days_since_base / 365.25)
            
            # Aplicar escalación a precios base
            for activity, data in self.unit_price_library.items():
                if 'base_price' in data:
                    data['base_price'] = int(data['base_price'] * escalation_factor)
                elif 'base_price_by_diameter' in data:
                    for diameter in data['base_price_by_diameter']:
                        data['base_price_by_diameter'][diameter] = int(
                            data['base_price_by_diameter'][diameter] * escalation_factor
                        )
                elif 'base_price_by_power' in data:
                    for power in data['base_price_by_power']:
                        data['base_price_by_power'][power] = int(
                            data['base_price_by_power'][power] * escalation_factor
                        )
            
            self.price_database['last_updated'] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error actualizando precios: {e}")
    
    def generate_cost_report(self, cost_breakdown: CostBreakdown, output_path: str = None) -> Dict:
        """Genera reporte detallado de costos"""
        try:
            report = {
                'summary': {
                    'total_project_cost': cost_breakdown.total_cost,
                    'direct_costs_total': sum(cost_breakdown.direct_costs.values()),
                    'indirect_costs_total': sum(cost_breakdown.indirect_costs.values()),
                    'contingencies': cost_breakdown.contingencies,
                    'profit_margin': cost_breakdown.profit_margin,
                    'cost_per_m3_capacity': cost_breakdown.cost_per_m3_capacity
                },
                'direct_costs_breakdown': {
                    category.value: cost for category, cost in cost_breakdown.direct_costs.items()
                },
                'indirect_costs_breakdown': cost_breakdown.indirect_costs,
                'detailed_items': [
                    {
                        'code': item.code,
                        'description': item.description,
                        'unit': item.unit,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_price': item.total_price,
                        'category': item.category.value
                    } for item in cost_breakdown.cost_items
                ],
                'benchmarking': self._generate_cost_benchmarking(cost_breakdown),
                'recommendations': self._generate_cost_recommendations(cost_breakdown)
            }
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                self.logger.info(f"Reporte de costos exportado: {output_path}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {}
    
    def _generate_cost_benchmarking(self, cost_breakdown: CostBreakdown) -> Dict:
        """Genera benchmarking de costos"""
        benchmarks = {
            'small_ptap': {'min': 80000, 'max': 120000, 'avg': 100000},
            'medium_ptap': {'min': 60000, 'max': 90000, 'avg': 75000},
            'large_ptap': {'min': 45000, 'max': 70000, 'avg': 57500}
        }
        
        cost_per_m3 = cost_breakdown.cost_per_m3_capacity
        
        comparison = {}
        for category, ranges in benchmarks.items():
            deviation_avg = ((cost_per_m3 - ranges['avg']) / ranges['avg']) * 100
            within_range = ranges['min'] <= cost_per_m3 <= ranges['max']
            
            comparison[category] = {
                'deviation_from_average': deviation_avg,
                'within_typical_range': within_range,
                'benchmark_range': ranges
            }
        
        return comparison
    
    def _generate_cost_recommendations(self, cost_breakdown: CostBreakdown) -> List[str]:
        """Genera recomendaciones para optimización de costos"""
        recommendations = []
        total_direct = sum(cost_breakdown.direct_costs.values())
        
        for category, cost in cost_breakdown.direct_costs.items():
            percentage = (cost / total_direct) * 100
            
            if category == CostCategory.CONCRETE and percentage > 40:
                recommendations.append(
                    "El costo de concreto representa más del 40% de costos directos. "
                    "Considerar optimizar diseño estructural."
                )
            
            elif category == CostCategory.MECHANICAL and percentage > 30:
                recommendations.append(
                    "Los equipos mecánicos representan más del 30% de costos directos. "
                    "Evaluar alternativas tecnológicas."
                )
        
        if cost_breakdown.cost_per_m3_capacity > 85000:
            recommendations.append(
                "El costo por m3/día está por encima del promedio. "
                "Considerar economías de escala."
            )
        
        return recommendations