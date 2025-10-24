"""
Hub Centralizado de Datos Gubernamentales
Orquestación de todos los conectores gubernamentales con cache inteligente
"""

import asyncio
import aiofiles
import json
import pandas as pd
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path
import hashlib

from .dane import DANEConnector
from .cra import CRAConnector
from .ideam import IDEAMConnector
from .siac import SIACConnector

class GovernmentDataHub:
    """
    Hub centralizado para integrar todos los datos gubernamentales
    
    Funcionalidades:
    - Orquestación de múltiples APIs gubernamentales
    - Cache inteligente unificado
    - Sincronización de datos
    - Validación cruzada de información
    - Generación de reportes consolidados
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.cache_dir = Path(self.config.get('cache_directory', 'cache/government_data'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar conectores
        self.dane = DANEConnector(self.config.get('dane', {}))
        self.cra = CRAConnector(self.config.get('cra', {}))
        self.ideam = IDEAMConnector(self.config.get('ideam', {}))
        self.siac = SIACConnector(self.config.get('siac', {}))
        
        # Cache inteligente
        self.cache_manager = IntelligentCacheManager(self.cache_dir)
        
        # Logger
        self.logger = self._setup_logger()
    
    def _load_config(self, config_path: str) -> Dict:
        """Carga configuración del hub"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'cache_directory': 'cache/government_data',
            'cache_ttl_days': {
                'demographic': 30,
                'tariffs': 1,
                'weather': 0.25,  # 6 horas
                'regulatory': 7
            },
            'sync_interval_hours': 24,
            'max_retries': 3,
            'timeout_seconds': 30
        }
    
    async def get_comprehensive_project_data(self, 
                                           municipality_code: str,
                                           project_params: Dict) -> Dict:
        """
        Obtiene datos completos para un proyecto de PTAP
        
        Args:
            municipality_code: Código DIVIPOLA del municipio
            project_params: Parámetros del proyecto
            
        Returns:
            Dict con todos los datos necesarios para el proyecto
        """
        try:
            # Ejecutar consultas en paralelo
            tasks = [
                self._get_demographic_data(municipality_code),
                self._get_economic_data(municipality_code),
                self._get_environmental_data(municipality_code, project_params),
                self._get_regulatory_data(),
                self._get_geographic_data(municipality_code)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Consolidar resultados
            consolidated_data = {
                'municipality_code': municipality_code,
                'timestamp': datetime.now().isoformat(),
                'demographic': results[0] if not isinstance(results[0], Exception) else {},
                'economic': results[1] if not isinstance(results[1], Exception) else {},
                'environmental': results[2] if not isinstance(results[2], Exception) else {},
                'regulatory': results[3] if not isinstance(results[3], Exception) else {},
                'geographic': results[4] if not isinstance(results[4], Exception) else {},
                'errors': [str(r) for r in results if isinstance(r, Exception)]
            }
            
            # Cache consolidado
            cache_key = f"comprehensive_{municipality_code}_{self._hash_params(project_params)}"
            await self.cache_manager.store(cache_key, consolidated_data, ttl_hours=6)
            
            return consolidated_data
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos completos: {e}")
            return {'error': str(e)}
    
    async def _get_demographic_data(self, municipality_code: str) -> Dict:
        """Obtiene datos demográficos consolidados"""
        try:
            # Información básica del municipio
            municipality_info = self.dane.get_municipality_info(municipality_code)
            
            # Proyecciones poblacionales
            population_projections = self.dane.get_population_projections(
                municipality_code, 2025, 2050)
            
            # Indicadores socioeconómicos
            socioeconomic = self.dane.get_socioeconomic_indicators(municipality_code)
            
            # Población de diseño
            design_population = self.dane.calculate_design_population(municipality_code, 25)
            
            return {
                'municipality_info': municipality_info,
                'population_projections': population_projections.to_dict('records') if not population_projections.empty else [],
                'socioeconomic_indicators': socioeconomic,
                'design_population': design_population
            }
            
        except Exception as e:
            self.logger.error(f"Error datos demográficos: {e}")
            return {'error': str(e)}
    
    async def _get_economic_data(self, municipality_code: str) -> Dict:
        """Obtiene datos económicos y tarifarios"""
        try:
            # Estructura tarifaria
            tariffs = self.cra.get_water_tariffs(municipality_code)
            
            # Indicadores de eficiencia
            efficiency = self.cra.get_efficiency_indicators(f"Empresa_{municipality_code}")
            
            # Marco regulatorio
            regulatory_framework = self.cra.get_regulatory_framework()
            
            return {
                'tariff_structure': tariffs,
                'efficiency_indicators': efficiency,
                'regulatory_framework': regulatory_framework
            }
            
        except Exception as e:
            self.logger.error(f"Error datos económicos: {e}")
            return {'error': str(e)}
    
    async def _get_environmental_data(self, municipality_code: str, 
                                    project_params: Dict) -> Dict:
        """Obtiene datos ambientales y climáticos"""
        try:
            # Coordenadas del municipio (obtener de DANE o usar aproximadas)
            coords = self._get_municipality_coordinates(municipality_code)
            
            # Datos hidrometeorolgicos
            weather_data = self.ideam.get_weather_data(
                coords['lat'], coords['lon'], 
                datetime.now() - timedelta(days=365), datetime.now())
            
            # Información de cuencas
            watershed_info = self.siac.get_watershed_info(coords['lat'], coords['lon'])
            
            # Calidad del agua (si está disponible)
            water_quality = self.siac.get_water_quality_data(
                coords['lat'], coords['lon'])
            
            return {
                'coordinates': coords,
                'weather_data': weather_data,
                'watershed_info': watershed_info,
                'water_quality': water_quality
            }
            
        except Exception as e:
            self.logger.error(f"Error datos ambientales: {e}")
            return {'error': str(e)}
    
    async def _get_regulatory_data(self) -> Dict:
        """Obtiene datos regulatorios actualizados"""
        try:
            regulatory_data = self.cra.get_regulatory_framework()
            return regulatory_data
            
        except Exception as e:
            self.logger.error(f"Error datos regulatorios: {e}")
            return {'error': str(e)}
    
    async def _get_geographic_data(self, municipality_code: str) -> Dict:
        """Obtiene datos geográficos y topográficos"""
        try:
            # Información geográfica básica
            coords = self._get_municipality_coordinates(municipality_code)
            elevation = self._get_elevation_data(coords['lat'], coords['lon'])
            
            return {
                'coordinates': coords,
                'elevation': elevation,
                'geographic_zone': self._determine_geographic_zone(coords)
            }
            
        except Exception as e:
            self.logger.error(f"Error datos geográficos: {e}")
            return {'error': str(e)}
    
    def generate_project_summary(self, comprehensive_data: Dict) -> Dict:
        """
        Genera resumen ejecutivo del proyecto basado en datos consolidados
        
        Args:
            comprehensive_data: Datos consolidados del proyecto
            
        Returns:
            Dict con resumen ejecutivo
        """
        try:
            demographic = comprehensive_data.get('demographic', {})
            economic = comprehensive_data.get('economic', {})
            environmental = comprehensive_data.get('environmental', {})
            
            # Extraer información clave
            municipality_info = demographic.get('municipality_info', {})
            design_pop = demographic.get('design_population', {})
            tariffs = economic.get('tariff_structure', {})
            
            # Generar resumen
            summary = {
                'proyecto': {
                    'municipio': municipality_info.get('nombre', 'N/A'),
                    'departamento': municipality_info.get('departamento', 'N/A'),
                    'codigo_divipola': comprehensive_data.get('municipality_code', 'N/A')
                },
                'poblacion': {
                    'actual': design_pop.get('poblacion_actual', 0),
                    'diseno': design_pop.get('poblacion_diseno', 0),
                    'tasa_crecimiento': design_pop.get('tasa_crecimiento', 0)
                },
                'aspectos_economicos': {
                    'tarifa_media_m3': tariffs.get('tarifas_acueducto', {}).get('estrato_3', {}).get('consumo_basico', 0),
                    'tiene_subsidios': len(tariffs.get('subsidios', {})) > 0
                },
                'aspectos_ambientales': {
                    'coordenadas': environmental.get('coordinates', {}),
                    'datos_climaticos_disponibles': 'weather_data' in environmental
                },
                'fecha_generacion': datetime.now().isoformat(),
                'completitud_datos': self._calculate_data_completeness(comprehensive_data)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen: {e}")
            return {'error': str(e)}
    
    def _calculate_data_completeness(self, data: Dict) -> Dict:
        """Calcula completitud de los datos obtenidos"""
        completeness = {
            'demograficos': 0,
            'economicos': 0,
            'ambientales': 0,
            'regulatorios': 0,
            'geograficos': 0
        }
        
        # Evaluar completitud de cada categoría
        demographic = data.get('demographic', {})
        if demographic and 'error' not in demographic:
            completeness['demograficos'] = 85 if demographic.get('design_population') else 50
        
        economic = data.get('economic', {})
        if economic and 'error' not in economic:
            completeness['economicos'] = 90 if economic.get('tariff_structure') else 60
        
        environmental = data.get('environmental', {})
        if environmental and 'error' not in environmental:
            completeness['ambientales'] = 75 if environmental.get('weather_data') else 40
        
        regulatory = data.get('regulatory', {})
        if regulatory and 'error' not in regulatory:
            completeness['regulatorios'] = 95
        
        geographic = data.get('geographic', {})
        if geographic and 'error' not in geographic:
            completeness['geograficos'] = 80
        
        completeness['total'] = sum(completeness.values()) / len(completeness)
        
        return completeness
    
    def _get_municipality_coordinates(self, municipality_code: str) -> Dict:
        """Obtiene coordenadas del municipio"""
        # Coordenadas aproximadas para municipios principales
        coords_db = {
            '11001': {'lat': 4.7110, 'lon': -74.0721},  # Bogotá
            '05001': {'lat': 6.2442, 'lon': -75.5812},  # Medellín
            '76001': {'lat': 3.4516, 'lon': -76.5320},  # Cali
        }
        
        return coords_db.get(municipality_code, {'lat': 4.0, 'lon': -74.0})
    
    def _hash_params(self, params: Dict) -> str:
        """Genera hash de parámetros para cache"""
        param_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(param_str.encode()).hexdigest()[:8]
    
    def _setup_logger(self) -> logging.Logger:
        """Configura logger para el hub"""
        logger = logging.getLogger('GovernmentDataHub')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

class IntelligentCacheManager:
    """Gestor de cache inteligente para datos gubernamentales"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = cache_dir / 'cache_metadata.json'
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Carga metadatos del cache"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    async def store(self, key: str, data: Any, ttl_hours: int = 24):
        """Almacena datos en cache"""
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            # Almacenar datos
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, default=str, indent=2))
            
            # Actualizar metadatos
            self.metadata[key] = {
                'timestamp': datetime.now().isoformat(),
                'ttl_hours': ttl_hours,
                'expires_at': (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
                'file_path': str(cache_file)
            }
            
            await self._save_metadata()
            
        except Exception as e:
            logging.error(f"Error almacenando en cache: {e}")
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """Recupera datos del cache si no han expirado"""
        try:
            if key not in self.metadata:
                return None
            
            metadata = self.metadata[key]
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            
            if datetime.now() > expires_at:
                await self._remove_expired_entry(key)
                return None
            
            cache_file = Path(metadata['file_path'])
            if not cache_file.exists():
                return None
            
            async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            logging.error(f"Error recuperando del cache: {e}")
            return None
    
    async def _save_metadata(self):
        """Guarda metadatos del cache"""
        try:
            async with aiofiles.open(self.metadata_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.metadata, indent=2, default=str))
        except Exception as e:
            logging.error(f"Error guardando metadatos: {e}")
    
    async def _remove_expired_entry(self, key: str):
        """Elimina entrada expirada del cache"""
        try:
            if key in self.metadata:
                cache_file = Path(self.metadata[key]['file_path'])
                if cache_file.exists():
                    cache_file.unlink()
                del self.metadata[key]
                await self._save_metadata()
        except Exception as e:
            logging.error(f"Error eliminando entrada expirada: {e}")
