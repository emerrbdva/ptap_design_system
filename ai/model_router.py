"""
Router de Modelos de IA

Orquestador de modelos de IA locales vía Ollama:
- DeepSeek-R1: Razonamiento técnico y planificación
- Qwen2.5-Math: Resolución matemática
- Mistral-7B-Instruct: Redacción técnica en español

POLÍTICA CRÍTICA: Ningún cálculo numérico proviene directamente de LLMs.
Todos los números son calculados por SymPy/SciPy/Pint y devueltos al LLM.
"""

import ollama
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuración de un modelo"""
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    system_prompt: str


class AIModelRouter:
    """
    Router para orquestar modelos de IA local.
    
    Determina qué modelo usar según la intención y ejecuta la consulta
    apropiada, manteniendo la política de exactitud (no números de LLMs).
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar router.
        
        Args:
            config_path: Ruta al archivo de configuración YAML
        """
        # Cargar configuración
        if config_path:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                ai_config = config.get("ai_models", {})
        else:
            # Configuración por defecto
            ai_config = self._default_config()
        
        # Configurar modelos
        self.reasoning_config = ModelConfig(**ai_config["reasoning"])
        self.math_config = ModelConfig(**ai_config["math"])
        self.writing_config = ModelConfig(**ai_config["writing"])
        
        # Verificar conexión a Ollama
        self.ollama_host = ai_config.get("ollama", {}).get("host", "http://localhost:11434")
        self._verify_ollama_connection()
        
        logger.info("AIModelRouter inicializado")
    
    def _default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            "ollama": {"host": "http://localhost:11434"},
            "reasoning": {
                "model": "deepseek-r1:8b",
                "temperature": 0.1,
                "top_p": 0.9,
                "max_tokens": 4096,
                "system_prompt": "Eres un ingeniero sanitario experto. Razona paso a paso."
            },
            "math": {
                "model": "qwen2.5-math:7b",
                "temperature": 0.0,
                "top_p": 0.95,
                "max_tokens": 2048,
                "system_prompt": "Estructura problemas matemáticos paso a paso."
            },
            "writing": {
                "model": "mistral:7b-instruct-v0.3",
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 8192,
                "system_prompt": "Redacta documentos técnicos profesionales en español."
            }
        }
    
    def _verify_ollama_connection(self):
        """Verificar que Ollama esté ejecutándose"""
        try:
            models = ollama.list()
            logger.info(f"Ollama conectado: {len(models.get('models', []))} modelos disponibles")
        except Exception as e:
            logger.error(f"No se puede conectar a Ollama: {e}")
            logger.error("Asegúrate de que Ollama esté ejecutándose: ollama serve")
    
    def _call_model(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Llamar a un modelo vía Ollama.
        
        Args:
            model: Nombre del modelo
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema
            temperature: Temperatura
            max_tokens: Tokens máximos
            
        Returns:
            Respuesta del modelo
        """
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            logger.error(f"Error llamando modelo {model}: {e}")
            raise
    
    def reason(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> str:
        """
        Razonamiento técnico con DeepSeek-R1.
        
        Usado para:
        - Planificación de trenes de tratamiento
        - Decisiones técnicas complejas
        - Auditoría de cadenas de razonamiento
        
        Args:
            prompt: Pregunta o problema
            context: Contexto adicional
            
        Returns:
            Cadena de razonamiento
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        logger.info(f"[DeepSeek-R1] Razonamiento: {prompt[:100]}...")
        
        response = self._call_model(
            model=self.reasoning_config.model,
            prompt=full_prompt,
            system_prompt=self.reasoning_config.system_prompt,
            temperature=self.reasoning_config.temperature,
            max_tokens=self.reasoning_config.max_tokens
        )
        
        return response
    
    def solve_math(
        self,
        problem: str,
        variables: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Resolución matemática con Qwen2.5-Math.
        
        IMPORTANTE: Este modelo ESTRUCTURA el problema matemático,
        pero NO devuelve el resultado final. El cálculo real se hace
        con SymPy/SciPy.
        
        Args:
            problem: Problema matemático
            variables: Variables conocidas
            
        Returns:
            Estructura del problema y fórmulas simbólicas
        """
        vars_str = ""
        if variables:
            vars_str = "\n\nVariables conocidas:\n" + "\n".join(
                f"{k} = {v}" for k, v in variables.items()
            )
        
        full_prompt = f"{problem}{vars_str}\n\nEstructura el problema y proporciona las fórmulas simbólicas necesarias."
        
        logger.info(f"[Qwen2.5-Math] Problema matemático: {problem[:100]}...")
        
        response = self._call_model(
            model=self.math_config.model,
            prompt=full_prompt,
            system_prompt=self.math_config.system_prompt,
            temperature=self.math_config.temperature,
            max_tokens=self.math_config.max_tokens
        )
        
        logger.warning("⚠️ RECUERDA: Verificar cálculos con SymPy/SciPy, no usar números del LLM")
        
        return response
    
    def write_technical(
        self,
        topic: str,
        content_type: Literal["memoria", "marco_normativo", "resumen", "seccion"],
        context: Optional[Dict[str, Any]] = None,
        ras_references: Optional[List[str]] = None
    ) -> str:
        """
        Redacción técnica con Mistral-7B-Instruct.
        
        Usado para:
        - Memorias de cálculo
        - Marco normativo
        - Resúmenes ejecutivos
        - Secciones de informes
        
        Args:
            topic: Tema a redactar
            content_type: Tipo de contenido
            context: Contexto adicional (datos, resultados)
            ras_references: Referencias al RAS a incluir
            
        Returns:
            Texto redactado
        """
        prompt = f"Redacta un(a) {content_type} sobre: {topic}\n\n"
        
        if context:
            prompt += "Contexto y datos:\n"
            for key, value in context.items():
                prompt += f"- {key}: {value}\n"
            prompt += "\n"
        
        if ras_references:
            prompt += "Referencias normativas a incluir:\n"
            for ref in ras_references:
                prompt += f"- RAS 2017 {ref}\n"
            prompt += "\n"
        
        prompt += "Redacta de forma profesional, técnica y formal en español."
        
        logger.info(f"[Mistral-7B] Redacción {content_type}: {topic[:100]}...")
        
        response = self._call_model(
            model=self.writing_config.model,
            prompt=prompt,
            system_prompt=self.writing_config.system_prompt,
            temperature=self.writing_config.temperature,
            max_tokens=self.writing_config.max_tokens
        )
        
        return response
    
    def route_intent(
        self,
        user_query: str,
        intent: Optional[Literal["reason", "math", "write"]] = None
    ) -> str:
        """
        Router automático de intención.
        
        Si no se especifica intent, detecta automáticamente.
        
        Args:
            user_query: Consulta del usuario
            intent: Intención (opcional)
            
        Returns:
            Respuesta del modelo apropiado
        """
        # Si no hay intent, detectar
        if intent is None:
            intent = self._detect_intent(user_query)
        
        if intent == "reason":
            return self.reason(user_query)
        elif intent == "math":
            return self.solve_math(user_query)
        elif intent == "write":
            return self.write_technical(user_query, "seccion")
        else:
            logger.warning(f"Intent desconocido: {intent}")
            return self.reason(user_query)
    
    def _detect_intent(self, query: str) -> str:
        """Detectar intención simple basada en keywords"""
        query_lower = query.lower()
        
        # Math keywords
        math_keywords = ["calcular", "ecuación", "fórmula", "derivar", "integral", "resolver"]
        if any(kw in query_lower for kw in math_keywords):
            return "math"
        
        # Write keywords
        write_keywords = ["redactar", "escribir", "memoria", "informe", "documento"]
        if any(kw in query_lower for kw in write_keywords):
            return "write"
        
        # Default: reasoning
        return "reason"
