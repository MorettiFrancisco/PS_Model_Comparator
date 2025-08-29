"""
Modelos Pydantic para la API del PS Model Comparator
"""

from typing import List, Dict, Any, Union
from pydantic import BaseModel


class ModelConfig(BaseModel):
    """Configuración de un modelo para ejecutar"""

    provider: str  # "gemini" o "ollama"
    model_name: Union[str, None] = None  # Para ollama, especifica el modelo


class ModelResponse(BaseModel):
    """Respuesta de un modelo individual"""

    model_name: str
    provider: str
    response: str
    execution_time: float
    success: bool
    error: Union[str, None] = None


class ModelMetricsSummary(BaseModel):
    """Resumen combinado de métricas textuales y multimodales"""

    model_name: str
    provider: str
    execution_time: float
    success_rate: float

    # Métricas de texto
    quality_score: float
    word_count: int
    has_detailed_description: bool
    uses_english: bool

    # Métricas multimodales - Solo ITM Score
    itm_score: float = 0.0

    # Puntuación final combinada (basada solo en métricas de texto + ITM)
    overall_score: float


class MultimodalMetricsSummary(BaseModel):
    """Resumen de métricas multimodales"""

    itm_score: float  # Cambiado de clip_score a itm_score
    object_precision: float
    object_recall: float
    hallucination_rate: float
    robustness_score: float
    safety_flag: bool
    interpretation: Dict[str, str]


class ComparisonSummary(BaseModel):
    """Resumen de la comparación entre modelos"""

    total_models: int
    winner: str
    fastest_model: str
    most_detailed_model: str
    highest_quality_model: str
    recommendation: str
    metrics_summary: List[ModelMetricsSummary]


class ComparisonResponse(BaseModel):
    """Respuesta completa de la comparación"""

    results: List[ModelResponse]
    total_execution_time: float
    image_info: Dict[str, Any]
    summary: ComparisonSummary
