from dataclasses import dataclass
from typing import Dict, List, Any
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

    # Multimodal
    itm_score: float  # <-- nuevo campo

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
    def __init__(self):
        # Palabras clave organizadas en categorías
        self.color_keywords = {"red", "blue", "green", "yellow", "black", "white"}
        self.object_keywords = {"dog", "cat", "car", "tree", "person", "sign"}
        self.people_keywords = {
            "person",
            "people",
            "man",
            "woman",
            "child",
            "boy",
            "girl",
            "human",
        }
        self.action_keywords = {
            "running",
            "walking",
            "sitting",
            "standing",
            "jumping",
            "playing",
            "eating",
            "drinking",
        }
        self.text_keywords = {"text", "letter", "word"}
        self.scene_keywords = {"indoor", "outdoor", "street", "park", "room"}
        self.english_indicators = {
            "the",
            "and",
            "is",
            "in",
            "it",
            "you",
            "that",
            "he",
            "was",
            "for",
            "on",
            "are",
            "with",
            "as",
            "his",
            "they",
            "be",
            "at",
            "one",
            "have",
            "this",
            "from",
            "or",
            "had",
            "by",
            "hot",
            "but",
            "some",
            "what",
            "there",
            "we",
            "can",
            "out",
            "other",
            "were",
            "all",
            "your",
            "when",
            "up",
            "use",
            "word",
            "how",
            "said",
            "each",
            "which",
            "she",
            "do",
            "their",
            "time",
            "if",
            "will",
            "way",
            "about",
            "many",
            "then",
            "them",
            "would",
            "write",
            "like",
            "so",
            "these",
            "her",
            "long",
            "make",
            "thing",
            "see",
            "him",
            "two",
            "has",
            "look",
            "more",
            "day",
            "could",
            "go",
            "come",
            "did",
            "my",
            "sound",
            "no",
            "most",
            "number",
            "who",
            "over",
            "know",
            "water",
            "than",
            "call",
            "first",
            "may",
            "down",
            "side",
            "been",
            "now",
            "find",
        }

        # Números del 0 al 20
        self.number_words = {
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
            "twenty",
        }

    def analyze_model_response(
        self, response: ModelResponse, itm_score: float = 0.0
    ) -> ModelMetrics:
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
                itm_score=itm_score,
                quality_score=0.0,
                overall_score=0.0,
            )

        content_metrics = self.analyze_content_quality(response.response)
        quality_score = self.calculate_quality_score(content_metrics, itm_score)
        performance_score = self.calculate_performance_score(
            response.execution_time, response.success
        )

        if response.execution_time < 10:
            overall_score = (quality_score * 0.5) + (performance_score * 0.5)
        elif response.execution_time > 60:
            overall_score = (quality_score * 0.7) + (performance_score * 0.3)
        else:
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
            itm_score=itm_score,
            quality_score=quality_score,
            overall_score=overall_score,
        )

    def analyze_content_quality(self, response: str) -> Dict[str, Any]:
        """Analiza la calidad del contenido de la respuesta"""
        response_lower = response.lower()
        words = response_lower.split()
        sentences = response.split(".")

        return {
            "response_length": len(response),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "mentions_colors": any(c in response_lower for c in self.color_keywords),
            "mentions_objects": any(o in response_lower for o in self.object_keywords),
            "mentions_people": any(p in response_lower for p in self.people_keywords),
            "mentions_text": any(t in response_lower for t in self.text_keywords),
            "mentions_actions": any(a in response_lower for a in self.action_keywords),
            "uses_english": sum(
                1 for w in self.english_indicators if w in response_lower
            )
            > 3,
            "has_detailed_description": len(words) > 20,
            "well_structured": len(sentences) > 2 and not response.startswith("Sorry"),
            "has_specific_details": any(
                kw in response_lower
                for kw in self.color_keywords
                | self.object_keywords
                | self.people_keywords
            ),
        }

    def calculate_quality_score(
        self, content_metrics: Dict[str, Any], itm_score: float = 0.0
    ) -> float:
        """Calcula una puntuación híbrida: texto + ITM score"""
        score = 0.0

        # ---- Texto ----
        word_count = content_metrics["word_count"]
        if 20 <= word_count <= 200:
            score += 2.0
        elif 10 <= word_count < 20:
            score += 1.0
        elif word_count > 200:
            score += 1.5

        if content_metrics["has_detailed_description"]:
            score += 2.0
        if content_metrics["well_structured"]:
            score += 2.0
        if content_metrics["uses_english"]:
            score += 1.5
        if content_metrics["has_specific_details"]:
            score += 1.5

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

        # ---- Multimodal (ITM) ----
        itm_component = itm_score * 10.0  # normalizar [0–1] → [0–10]

        # Combinar: 70% texto + 30% itm
        final_score = (score * 0.7) + (itm_component * 0.3)

        return min(final_score, 10.0)

    def compare_models_with_itm(
        self, responses: List[ModelResponse], itm_scores: Dict[str, float]
    ) -> ComparisonMetrics:
        """Compara múltiples modelos integrando ITM scores en el análisis"""
        if not responses:
            raise ValueError("No hay respuestas para comparar")

        # Analizar cada modelo con su ITM score correspondiente
        model_metrics = {}
        for response in responses:
            itm_score = itm_scores.get(response.model_name, 0.0)
            metrics = self.analyze_model_response(response, itm_score=itm_score)
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

    def calculate_performance_score(
        self, execution_time: float, success: bool
    ) -> float:
        """Calcula una puntuación de rendimiento"""
        if not success:
            return 0.0

        if execution_time <= 3:
            return 10.0
        elif execution_time <= 5:
            return 9.5
        elif execution_time <= 10:
            return 9.0
        elif execution_time <= 15:
            return 8.0
        elif execution_time <= 30:
            return 7.0
        elif execution_time <= 60:
            return 5.0
        elif execution_time <= 120:
            return 3.0
        else:
            return 1.0

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
