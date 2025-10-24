"""
Conector a Datos Abiertos Colombia

Cliente para el portal de Datos Abiertos de Colombia usando SODA API (Socrata).
Incluye manejo de límites de tasa, reintentos, cache local y snapshots con metadatos.

Portal: https://www.datos.gov.co
API: https://www.datos.gov.co/resource
Documentación: https://herramientas.datos.gov.co
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, List, Optional, Any
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatasetMetadata:
    """Metadatos de dataset consultado"""
    dataset_id: str
    title: str
    description: str
    url: str
    query: Optional[str]
    timestamp: str
    rows_returned: int
    cache_hit: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)


class DatosAbiertosConnector:
    """
    Conector a Datos Abiertos Colombia (SODA/SoQL).
    
    Características:
    - Consultas SoQL (Socrata Query Language)
    - Rate limiting automático
    - Reintentos con backoff exponencial
    - Cache local con TTL
    - Snapshots con metadatos
    """
    
    def __init__(
        self,
        base_url: str = "https://www.datos.gov.co",
        rate_limit: int = 1000,  # requests/hour
        cache_ttl: int = 86400,  # 24 horas
        cache_dir: str = "data/cache/datos_abiertos",
        snapshot_dir: str = "data/snapshots/datos_abiertos"
    ):
        """
        Inicializar conector.
        
        Args:
            base_url: URL base del portal
            rate_limit: Límite de requests por hora
            cache_ttl: Tiempo de vida del cache (segundos)
            cache_dir: Directorio de cache
            snapshot_dir: Directorio de snapshots
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/resource"
        self.rate_limit = rate_limit
        self.cache_ttl = cache_ttl
        self.cache_dir = Path(cache_dir)
        self.snapshot_dir = Path(snapshot_dir)
        
        # Crear directorios
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Control de tasa
        self.requests_made = []
        self.requests_per_second = 2
        
        # Configurar sesión con reintentos
        self.session = self._create_session()
        
        logger.info(f"DatosAbiertosConnector inicializado: {base_url}")
    
    def _create_session(self) -> requests.Session:
        """Crear sesión con reintentos y backoff"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _check_rate_limit(self):
        """Verificar y aplicar rate limiting"""
        now = time.time()
        
        # Limpiar requests antiguos (> 1 hora)
        self.requests_made = [
            t for t in self.requests_made 
            if now - t < 3600
        ]
        
        # Verificar límite por hora
        if len(self.requests_made) >= self.rate_limit:
            wait_time = 3600 - (now - self.requests_made[0])
            logger.warning(f"Rate limit alcanzado. Esperando {wait_time:.0f}s")
            time.sleep(wait_time)
            self.requests_made = []
        
        # Rate limiting por segundo
        if len(self.requests_made) > 0:
            time_since_last = now - self.requests_made[-1]
            if time_since_last < (1.0 / self.requests_per_second):
                time.sleep(1.0 / self.requests_per_second)
        
        self.requests_made.append(time.time())
    
    def _get_cache_key(self, dataset_id: str, query: Optional[str] = None) -> str:
        """Generar clave de cache"""
        content = f"{dataset_id}:{query or ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Recuperar datos del cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        # Verificar TTL
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > self.cache_ttl:
            logger.debug(f"Cache expirado: {cache_key}")
            cache_file.unlink()
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            logger.debug(f"Cache hit: {cache_key}")
            return json.load(f)
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Guardar datos en cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Guardado en cache: {cache_key}")
    
    def query_dataset(
        self,
        dataset_id: str,
        select: Optional[str] = None,
        where: Optional[str] = None,
        order: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Consultar dataset con SoQL.
        
        Args:
            dataset_id: ID del dataset (ej: 'abcd-1234')
            select: Campos a seleccionar (SoQL SELECT)
            where: Condiciones (SoQL WHERE)
            order: Ordenamiento (SoQL ORDER BY)
            limit: Límite de registros
            offset: Offset para paginación
            use_cache: Usar cache local
            
        Returns:
            Dict con datos y metadatos
        """
        # Construir query SoQL
        params = {
            "$limit": limit,
            "$offset": offset
        }
        
        if select:
            params["$select"] = select
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order
        
        query_str = "&".join(f"{k}={v}" for k, v in params.items())
        
        # Verificar cache
        cache_key = self._get_cache_key(dataset_id, query_str)
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                cached["_metadata"]["cache_hit"] = True
                return cached
        
        # Hacer request
        url = f"{self.api_endpoint}/{dataset_id}.json"
        
        self._check_rate_limit()
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Preparar resultado con metadatos
            result = {
                "data": data,
                "_metadata": {
                    "dataset_id": dataset_id,
                    "query": query_str,
                    "timestamp": datetime.now().isoformat(),
                    "rows_returned": len(data),
                    "cache_hit": False,
                    "url": url
                }
            }
            
            # Guardar en cache
            if use_cache:
                self._save_to_cache(cache_key, result)
            
            logger.info(f"Dataset consultado: {dataset_id}, {len(data)} filas")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error consultando dataset {dataset_id}: {e}")
            raise
    
    def create_snapshot(
        self,
        dataset_id: str,
        data: Dict[str, Any],
        description: str = ""
    ) -> Path:
        """
        Crear snapshot permanente de datos consultados.
        
        Args:
            dataset_id: ID del dataset
            data: Datos a guardar
            description: Descripción del snapshot
            
        Returns:
            Path al archivo de snapshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dataset_id}_{timestamp}.json"
        filepath = self.snapshot_dir / filename
        
        snapshot = {
            "dataset_id": dataset_id,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Snapshot creado: {filepath}")
        return filepath
    
    def search_datasets(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Buscar datasets en el catálogo.
        
        Args:
            query: Término de búsqueda
            limit: Límite de resultados
            
        Returns:
            Lista de datasets encontrados
        """
        # Nota: Esta es una implementación simplificada
        # La API real de búsqueda puede variar
        search_url = f"{self.base_url}/api/catalog/v1"
        params = {
            "q": query,
            "limit": limit
        }
        
        self._check_rate_limit()
        
        try:
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            results = response.json()
            
            logger.info(f"Búsqueda '{query}': {len(results.get('results', []))} resultados")
            return results.get("results", [])
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error en búsqueda: {e}")
            return []
