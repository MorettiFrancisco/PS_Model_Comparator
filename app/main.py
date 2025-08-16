"""
API Principal del PS Model Comparator
Endpoints para comparación de modelos de IA con imágenes
"""

import asyncio
import time
import tempfile
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    ComparisonResponse,
    ModelMetricsSummary,
    ComparisonSummary,
    ModelResponse,
)
from .image_utils import process_image, image_to_base64, validate_image_file
from .model_executor import execute_model
from .model_config import get_available_models
from .validation import parse_models_config, validate_models_for_comparison
from .metrics import ModelMetricsAnalyzer

# Inicializar aplicación FastAPI
app = FastAPI(title="PS Model Comparator", version="1.0.0")

# Inicializar analizadores de métricas
text_metrics_analyzer = ModelMetricsAnalyzer()
# No inicializar multimodal_metrics_analyzer aquí para ahorrar memoria

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/compare-models", response_model=ComparisonResponse)
async def compare_models(
    image: UploadFile = File(..., description="Imagen a analizar"),
    models: str = Form(
        ...,
        description='Configuración JSON de modelos (ej: \'[{"provider":"gemini"},{"provider":"ollama","model_name":"llama3.2-vision:11b"}]\')',
    ),
):
    """
    Endpoint principal que compara múltiples modelos con métricas completas

    Incluye:
    - Métricas de texto (calidad, rendimiento, contenido)
    - Métricas multimodales (CLIP score, detección de objetos, alucinaciones)
    """
    try:
        print(f"🔍 DEBUG: Received models parameter: {models}")
        print(f"🔍 DEBUG: Image filename: {image.filename}")

        # Validar imagen
        try:
            validate_image_file(image.content_type or "image/jpeg")
            print("🔍 DEBUG: Image validation passed")
        except Exception as e:
            print(f"🔍 DEBUG: Image validation failed: {e}")
            raise

        # Parsear y validar modelos
        try:
            models_config = parse_models_config(models)
            print(f"🔍 DEBUG: Parsed models config: {models_config}")
        except Exception as e:
            print(f"🔍 DEBUG: Models parsing failed: {e}")
            raise

        try:
            validate_models_for_comparison(models_config)
            print("🔍 DEBUG: Models validation passed")
        except Exception as e:
            print(f"🔍 DEBUG: Models validation failed: {e}")
            raise

        # Leer y procesar imagen
        image_content = await image.read()
        image_pil, image_info = process_image(image_content)
        image_base64 = image_to_base64(image_content)

        # Crear archivo temporal para análisis multimodal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image_content)
            temp_image_path = temp_file.name

        if not models_config:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron modelos válidos para comparar",
            )

        # Ejecutar modelos secuencialmente
        results = []
        total_start_time = time.time()

        print(f"🚀 Iniciando comparación con {len(models_config)} modelos...")

        for i, model_config in enumerate(models_config, 1):
            model_name = model_config.model_name or model_config.provider
            print(f"📊 Procesando modelo {i}/{len(models_config)}: {model_name}")

            try:
                result = await execute_model(model_config, image_base64, image_info)
                results.append(result)
                print(f"✅ {model_name} completado en {result.execution_time:.2f}s")
            except Exception as e:
                print(f"❌ Error en {model_name}: {str(e)[:100]}...")
                # Crear un resultado de error para mantener el tracking
                error_result = ModelResponse(
                    model_name=model_config.model_name
                    or f"{model_config.provider}-unknown",
                    provider=model_config.provider,
                    response="",
                    execution_time=0.0,
                    success=False,
                    error=str(e),
                )
                results.append(error_result)

            # Pequeña pausa entre modelos para evitar sobrecarga
            await asyncio.sleep(0.5)

        total_execution_time = time.time() - total_start_time

        if not results:
            raise HTTPException(
                status_code=500,
                detail="Ningún modelo pudo procesar la imagen correctamente",
            )

        # 1. Analizar métricas de texto
        text_comparison = text_metrics_analyzer.compare_models(results)
        text_recommendation = text_metrics_analyzer.get_recommendation(text_comparison)

        # 2. Analizar métricas multimodales DESPUÉS de completar todos los modelos
        print(
            "🔍 DEBUG: Iniciando análisis multimodal después de completar todos los modelos..."
        )
        multimodal_results = {}

        try:
            # Crear analizador multimodal solo cuando se necesite
            from .metrics import MultimodalMetricsAnalyzer

            multimodal_analyzer = MultimodalMetricsAnalyzer()

            for result in results:
                if result.success:
                    try:
                        # Extraer el texto de la respuesta
                        response_text = (
                            result.response
                            if isinstance(result.response, str)
                            else str(result.response)
                        )

                        mm_metrics = multimodal_analyzer.analyze_multimodal(
                            temp_image_path, response_text
                        )
                        multimodal_results[result.model_name] = {
                            "itm_score": mm_metrics.itm_score,
                            "object_precision": mm_metrics.object_precision,
                            "object_recall": mm_metrics.object_recall,
                            "hallucination_rate": mm_metrics.hallucination_rate,
                            "robustness_score": mm_metrics.robustness_score,
                            "safety_flag": mm_metrics.safety_flag,
                        }
                    except Exception as e:
                        print(
                            f"Error en métricas multimodales para {result.model_name}: {e}"
                        )
                        multimodal_results[result.model_name] = {
                            "itm_score": 0.0,
                            "object_precision": 0.0,
                            "object_recall": 0.0,
                            "hallucination_rate": 1.0,
                            "robustness_score": 0.0,
                            "safety_flag": True,
                        }
        except Exception as e:
            print(f"Error inicializando analizador multimodal: {e}")
            # Si no se puede inicializar, usar valores por defecto para todos
            for result in results:
                if result.success:
                    multimodal_results[result.model_name] = {
                        "itm_score": 0.0,
                        "object_precision": 0.0,
                        "object_recall": 0.0,
                        "hallucination_rate": 1.0,
                        "robustness_score": 0.0,
                        "safety_flag": True,
                    }

        # Limpiar archivo temporal
        try:
            os.unlink(temp_image_path)
        except Exception:
            pass

        # 3. Crear resumen combinado de métricas
        metrics_summary = []
        for model_name, model_metrics in text_comparison.metrics_by_model.items():
            mm_data = multimodal_results.get(model_name, {})

            # Calcular puntuación multimodal combinada
            multimodal_score = (
                mm_data.get("itm_score", 0) * 0.4
                + mm_data.get("object_precision", 0) * 0.3
                + (1 - mm_data.get("hallucination_rate", 1)) * 0.3
            ) * 10  # Escalar a 0-10

            # Puntuación final combinada (70% texto, 30% multimodal)
            combined_score = (model_metrics.overall_score * 0.7) + (
                multimodal_score * 0.3
            )

            metrics_summary.append(
                ModelMetricsSummary(
                    model_name=model_name,
                    provider=model_metrics.provider,
                    execution_time=model_metrics.execution_time,
                    success_rate=model_metrics.success_rate,
                    quality_score=model_metrics.quality_score,
                    word_count=model_metrics.word_count,
                    has_detailed_description=model_metrics.has_detailed_description,
                    uses_spanish=model_metrics.uses_spanish,
                    overall_score=combined_score,
                    # Métricas multimodales
                    itm_score=mm_data.get("itm_score", 0.0),
                    object_precision=mm_data.get("object_precision", 0.0),
                    object_recall=mm_data.get("object_recall", 0.0),
                    hallucination_rate=mm_data.get("hallucination_rate", 1.0),
                    multimodal_score=multimodal_score,
                )
            )

        # Determinar ganador basado en puntuación combinada
        winner = max(metrics_summary, key=lambda x: x.overall_score)

        # Generar recomendación mejorada
        combined_recommendation = f"""
🏆 **Ganador: {winner.model_name}** (Puntuación: {winner.overall_score:.1f}/10)

📊 **Análisis Textual:** {text_recommendation}

🖼️ **Análisis Multimodal:**
- ITM Score: {winner.itm_score:.3f} (probabilidad de correspondencia imagen-texto)
- Precisión de objetos: {winner.object_precision:.1%}
- Tasa de alucinación: {winner.hallucination_rate:.1%}

💡 **Fortalezas del ganador:**
- Calidad de texto: {winner.quality_score:.1f}/10
- Precisión multimodal: {winner.multimodal_score:.1f}/10
- Velocidad: {winner.execution_time:.1f}s
"""

        return ComparisonResponse(
            results=results,
            total_execution_time=total_execution_time,
            summary=ComparisonSummary(
                total_models=len(results),
                fastest_model=text_comparison.fastest_model,
                most_detailed_model=text_comparison.most_detailed_model,
                highest_quality_model=winner.model_name,
                winner=winner.model_name,
                recommendation=combined_recommendation.strip(),
                metrics_summary=metrics_summary,
            ),
            image_info={
                "filename": image.filename,
                "size": image_info.get("size", "unknown"),
                "format": image_info.get("format", "unknown"),
                "base64": image_base64,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        try:
            if "temp_image_path" in locals():
                os.unlink(temp_image_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/available-models")
async def get_available_models_endpoint():
    """
    Endpoint para obtener los modelos disponibles

    Returns:
        Lista de modelos disponibles por proveedor
    """
    return get_available_models()


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "service": "PS Model Comparator"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
