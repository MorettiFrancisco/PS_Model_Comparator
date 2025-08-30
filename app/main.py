import asyncio
import time
import tempfile
import os
import logging
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Inicializar aplicación FastAPI
app = FastAPI(title="PS Model Comparator", version="1.0.0")

# Inicializar analizador de métricas de texto
text_metrics_analyzer = ModelMetricsAnalyzer()

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
    try:
        logger.info(f"Received models parameter: {models}")
        logger.info(f"Image filename: {image.filename}")

        # Validar imagen
        try:
            validate_image_file(image.content_type or "image/jpeg")
            logger.info("Image validation passed")
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            raise

        # Parsear y validar modelos
        try:
            models_config = parse_models_config(models)
            logger.info(f"Parsed models config: {models_config}")
        except Exception as e:
            logger.error(f"Models parsing failed: {e}")
            raise

        try:
            validate_models_for_comparison(models_config)
            logger.info("Models validation passed")
        except Exception as e:
            logger.error(f"Models validation failed: {e}")
            raise

        # Leer y procesar imagen
        image_content = await image.read()
        image_pil, image_info = process_image(image_content)
        image_base64 = image_to_base64(image_content)

        temp_image_path = None
        try:
            # Crear archivo temporal
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
            logger.info(f"Starting comparison with {len(models_config)} models...")

            for i, model_config in enumerate(models_config, 1):
                model_name = model_config.model_name or model_config.provider
                logger.info(f"Processing model {i}/{len(models_config)}: {model_name}")

                if i > 1:
                    await asyncio.sleep(2)

                try:
                    result = await execute_model(model_config, image_base64, image_info)
                    results.append(result)
                    logger.info(
                        f"{model_name} completed in {result.execution_time:.2f}s"
                    )
                except Exception as e:
                    logger.error(f"Error in {model_name}: {str(e)[:100]}...")
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

                await asyncio.sleep(0.5)

            total_execution_time = time.time() - total_start_time

            if not results:
                raise HTTPException(
                    status_code=500,
                    detail="No models could process the image correctly",
                )

            # Analizar métricas de texto con ITM integrado
            logger.info("Starting integrated metrics analysis...")

            itm_scores = {}
            try:
                from .metrics.multimodal_metrics import MultimodalMetrics

                multimodal_analyzer = MultimodalMetrics()
                shared_references = multimodal_analyzer.generate_image_references(
                    temp_image_path, num_references=5
                )
                logger.info(f"Shared references generated: {shared_references[:3]}...")

                for result in results:
                    if result.success:
                        try:
                            response_text = (
                                result.response
                                if isinstance(result.response, str)
                                else str(result.response)
                            )
                            logger.info(
                                f"Calculating ITM score for {result.model_name}..."
                            )
                            mm_metrics = multimodal_analyzer.compute_all_optimized(
                                temp_image_path,
                                response_text,
                                shared_references,
                            )
                            itm_scores[result.model_name] = mm_metrics.itm_score
                            logger.info(
                                f"ITM score for {result.model_name}: {mm_metrics.itm_score:.4f}"
                            )
                            multimodal_analyzer._cleanup_memory()
                        except Exception as e:
                            logger.error(
                                f"Error calculating ITM for {result.model_name}: {e}"
                            )
                            itm_scores[result.model_name] = 0.0

                del multimodal_analyzer
                import gc

                gc.collect()

            except Exception as e:
                logger.error(f"Error in multimodal analysis: {e}")
                for result in results:
                    if result.success:
                        itm_scores[result.model_name] = 0.0

            # Analizar métricas de texto integrando ITM
            text_comparison = text_metrics_analyzer.compare_models_with_itm(
                results, itm_scores
            )

            # Crear resumen de métricas
            metrics_summary = []
            for model_name, model_metrics in text_comparison.metrics_by_model.items():
                metrics_summary.append(
                    ModelMetricsSummary(
                        model_name=model_name,
                        provider=model_metrics.provider,
                        execution_time=model_metrics.execution_time,
                        success_rate=model_metrics.success_rate,
                        quality_score=model_metrics.quality_score,
                        word_count=model_metrics.word_count,
                        has_detailed_description=model_metrics.has_detailed_description,
                        uses_english=model_metrics.uses_english,
                        overall_score=model_metrics.overall_score,
                        itm_score=model_metrics.itm_score,
                    )
                )

            winner = max(metrics_summary, key=lambda x: x.overall_score)
            combined_recommendation = f"{winner.model_name} mostró un excelente rendimiento. Resultados de alta calidad."

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

        finally:
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                logger.info(f"Temporary image file removed: {temp_image_path}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/available-models")
async def get_available_models_endpoint():
    return get_available_models()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "PS Model Comparator"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
