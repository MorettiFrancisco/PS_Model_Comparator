from typing import Dict, List, Any
from dataclasses import dataclass
from ..models import ModelResponse


@dataclass
class ModelMetrics:
    """Métricas detalladas de un modelo"""

    model_name: str
    provider: str

    # Métricas de rendimiento
    execution_time: float
    success_rate: float

    # Métricas de calidad de respuesta
    response_length: int
    word_count: int
    sentence_count: int

    # Métricas de contenido
    has_detailed_description: bool
    mentions_colors: bool
    mentions_objects: bool
    mentions_people: bool
    mentions_text: bool
    mentions_actions: bool

    # Métricas de idioma y estructura
    uses_english: bool
    well_structured: bool
    has_specific_details: bool

    # Puntuación general
    quality_score: float
    overall_score: float


@dataclass
class ComparisonMetrics:
    """Métricas de comparación entre modelos"""

    total_models: int
    fastest_model: str
    slowest_model: str
    most_detailed_model: str
    highest_quality_model: str
    winner: str
    metrics_by_model: Dict[str, ModelMetrics]


class ModelMetricsAnalyzer:
    """Analizador de métricas para modelos de IA"""

    def __init__(self):
        # Updated for English language analysis
        self.english_indicators = [
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "this",
            "that",
            "image",
            "shows",
            "contains",
            "displays",
            "features",
            "depicts",
        ]

        self.color_keywords = [
            "red",
            "blue",
            "green",
            "yellow",
            "black",
            "white",
            "gray",
            "grey",
            "pink",
            "purple",
            "orange",
            "brown",
            "violet",
            "color",
            "colors",
            "colored",
        ]

        self.object_keywords = [
            "object",
            "table",
            "chair",
            "car",
            "house",
            "tree",
            "flower",
            "animal",
            "book",
            "computer",
            "phone",
            "bottle",
            "box",
            "building",
            "vehicle",
            "booth",
            "toll",
            "gate",
            "sign",
            "road",
            "lane",
        ]

        self.people_keywords = [
            "person",
            "man",
            "woman",
            "child",
            "boy",
            "girl",
            "people",
            "face",
            "human",
            "individual",
            "figure",
            "driver",
            "worker",
        ]

        self.text_keywords = [
            "text",
            "letters",
            "words",
            "written",
            "writing",
            "title",
            "sign",
            "poster",
            "label",
            "message",
            "inscription",
        ]

        self.action_keywords = [
            "walking",
            "running",
            "jumping",
            "moving",
            "doing",
            "performing",
            "working",
            "playing",
            "eating",
            "standing",
            "sitting",
            "waiting",
            "driving",
        ]

    def analyze_content_quality(self, response: str) -> Dict[str, Any]:
        """Analiza la calidad del contenido de la respuesta"""
        response_lower = response.lower()
        words = response_lower.split()
        sentences = response.split(".")

        return {
            "response_length": len(response),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "mentions_colors": any(
                color in response_lower for color in self.color_keywords
            ),
            "mentions_objects": any(
                obj in response_lower for obj in self.object_keywords
            ),
            "mentions_people": any(
                person in response_lower for person in self.people_keywords
            ),
            "mentions_text": any(text in response_lower for text in self.text_keywords),
            "mentions_actions": any(
                action in response_lower for action in self.action_keywords
            ),
            "uses_english": sum(
                1 for word in self.english_indicators if word in response_lower
            )
            > 3,
            "has_detailed_description": len(words) > 20,
            "well_structured": len(sentences) > 2 and not response.startswith("Sorry"),
            "has_specific_details": any(
                keyword in response_lower
                for keyword in self.color_keywords
                + self.object_keywords
                + self.people_keywords
            ),
        }

    def calculate_quality_score(self, content_metrics: Dict[str, Any]) -> float:
        """Calcula una puntuación de calidad basada en las métricas de contenido"""
        score = 0.0

        # Puntuación base por longitud apropiada (20-200 palabras es ideal)
        word_count = content_metrics["word_count"]
        if 20 <= word_count <= 200:
            score += 2.0
        elif 10 <= word_count < 20:
            score += 1.0
        elif word_count > 200:
            score += 1.5

        # Bonificaciones por características específicas
        if content_metrics["has_detailed_description"]:
            score += 2.0
        if content_metrics["well_structured"]:
            score += 2.0
        if content_metrics["uses_english"]:
            score += 1.5
        if content_metrics["has_specific_details"]:
            score += 1.5

        # Bonificaciones por mencionar diferentes tipos de contenido
        content_variety = sum(
            [
                content_metrics["mentions_colors"],
                content_metrics["mentions_objects"],
                content_metrics["mentions_people"],
                content_metrics["mentions_text"],
                content_metrics["mentions_actions"],
            ]
        )
        score += content_variety * 0.5

        return min(score, 10.0)  # Máximo 10 puntos

    def calculate_performance_score(
        self, execution_time: float, success: bool
    ) -> float:
        """Calcula una puntuación de rendimiento más granular"""
        if not success:
            return 0.0

        # Puntuación base según tiempo de ejecución con umbrales más específicos
        if execution_time <= 3:
            return 10.0  # Excelente: ≤ 3 segundos
        elif execution_time <= 5:
            return 9.5  # Muy bueno: 3-5 segundos
        elif execution_time <= 10:
            return 9.0  # Bueno: 5-10 segundos
        elif execution_time <= 15:
            return 8.0  # Aceptable: 10-15 segundos
        elif execution_time <= 30:
            return 7.0  # Regular: 15-30 segundos
        elif execution_time <= 60:
            return 5.0  # Lento: 30-60 segundos
        elif execution_time <= 120:
            return 3.0  # Muy lento: 1-2 minutos
        else:
            return 1.0  # Extremadamente lento: > 2 minutos

    def analyze_model_response(self, response: ModelResponse) -> ModelMetrics:
        """Analiza una respuesta individual del modelo"""
        if not response.success:
            return ModelMetrics(
                model_name=response.model_name,
                provider=response.provider,
                execution_time=response.execution_time,
                success_rate=0.0,
                response_length=0,
                word_count=0,
                sentence_count=0,
                has_detailed_description=False,
                mentions_colors=False,
                mentions_objects=False,
                mentions_people=False,
                mentions_text=False,
                mentions_actions=False,
                uses_english=False,
                well_structured=False,
                has_specific_details=False,
                quality_score=0.0,
                overall_score=0.0,
            )

        content_metrics = self.analyze_content_quality(response.response)
        quality_score = self.calculate_quality_score(content_metrics)
        performance_score = self.calculate_performance_score(
            response.execution_time, response.success
        )

        # Puntuación general adaptativa basada en la velocidad
        # Si el modelo es muy rápido (< 10s), dar más peso al rendimiento
        # Si es lento (> 30s), dar más peso a la calidad
        if response.execution_time < 10:
            # Modelos rápidos: 50% calidad, 50% rendimiento
            overall_score = (quality_score * 0.5) + (performance_score * 0.5)
        elif response.execution_time > 60:
            # Modelos lentos: 70% calidad, 30% rendimiento
            overall_score = (quality_score * 0.7) + (performance_score * 0.3)
        else:
            # Velocidad normal: 60% calidad, 40% rendimiento
            overall_score = (quality_score * 0.6) + (performance_score * 0.4)

        return ModelMetrics(
            model_name=response.model_name,
            provider=response.provider,
            execution_time=response.execution_time,
            success_rate=1.0 if response.success else 0.0,
            response_length=content_metrics["response_length"],
            word_count=content_metrics["word_count"],
            sentence_count=content_metrics["sentence_count"],
            has_detailed_description=content_metrics["has_detailed_description"],
            mentions_colors=content_metrics["mentions_colors"],
            mentions_objects=content_metrics["mentions_objects"],
            mentions_people=content_metrics["mentions_people"],
            mentions_text=content_metrics["mentions_text"],
            mentions_actions=content_metrics["mentions_actions"],
            uses_english=content_metrics["uses_english"],
            well_structured=content_metrics["well_structured"],
            has_specific_details=content_metrics["has_specific_details"],
            quality_score=quality_score,
            overall_score=overall_score,
        )

    def compare_models(self, responses: List[ModelResponse]) -> ComparisonMetrics:
        """Compara múltiples modelos y determina el ganador"""
        if not responses:
            raise ValueError("No hay respuestas para comparar")

        # Analizar cada modelo
        model_metrics = {}
        for response in responses:
            metrics = self.analyze_model_response(response)
            model_metrics[response.model_name] = metrics

        # Encontrar el mejor en cada categoría
        successful_metrics = [m for m in model_metrics.values() if m.success_rate > 0]

        if not successful_metrics:
            # Si ningún modelo tuvo éxito
            fastest_model = min(
                model_metrics.values(), key=lambda x: x.execution_time
            ).model_name
            return ComparisonMetrics(
                total_models=len(responses),
                fastest_model=fastest_model,
                slowest_model=max(
                    model_metrics.values(), key=lambda x: x.execution_time
                ).model_name,
                most_detailed_model="N/A",
                highest_quality_model="N/A",
                winner="N/A - Ningún modelo tuvo éxito",
                metrics_by_model=model_metrics,
            )

        fastest_model = min(
            successful_metrics, key=lambda x: x.execution_time
        ).model_name
        slowest_model = max(
            model_metrics.values(), key=lambda x: x.execution_time
        ).model_name
        most_detailed_model = max(
            successful_metrics, key=lambda x: x.word_count
        ).model_name
        highest_quality_model = max(
            successful_metrics, key=lambda x: x.quality_score
        ).model_name
        winner = max(successful_metrics, key=lambda x: x.overall_score).model_name

        return ComparisonMetrics(
            total_models=len(responses),
            fastest_model=fastest_model,
            slowest_model=slowest_model,
            most_detailed_model=most_detailed_model,
            highest_quality_model=highest_quality_model,
            winner=winner,
            metrics_by_model=model_metrics,
        )

    def get_recommendation(self, comparison: ComparisonMetrics) -> str:
        """Genera una recomendación basada en las métricas"""
        winner_metrics = comparison.metrics_by_model[comparison.winner]

        if winner_metrics.overall_score < 3:
            return "⚠️ Ningún modelo mostró un rendimiento satisfactorio. Considera revisar la imagen o los modelos."
        elif winner_metrics.overall_score < 6:
            return f"🥉 {comparison.winner} fue el mejor, pero con rendimiento moderado. Hay margen de mejora."
        elif winner_metrics.overall_score < 8:
            return f"🥈 {comparison.winner} mostró un buen rendimiento general. Resultados satisfactorios."
        else:
            return f"🥇 {comparison.winner} mostró un excelente rendimiento. Resultados de alta calidad."


# Instancia global del analizador
metrics_analyzer = ModelMetricsAnalyzer()
