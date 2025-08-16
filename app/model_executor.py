"""
Lógica de ejecución de modelos y comparación
"""

import time
from typing import Dict, Any, List
from .models import ModelConfig, ModelResponse
from .agent import imagen_agente_analizador
from .model_config import has_vision_capability


def get_model_display_name(model_config: ModelConfig) -> str:
    """
    Obtiene el nombre de visualización del modelo

    Args:
        model_config: Configuración del modelo

    Returns:
        Nombre del modelo para mostrar
    """
    if model_config.provider == "gemini":
        return "gemini-1.5-flash"
    else:
        return model_config.model_name or "gemma3:4b"


def get_model_prompt(model_config: ModelConfig, image_info: Dict[str, Any]) -> str:
    """
    Genera el prompt apropiado según el modelo y sus capacidades

    Args:
        model_config: Configuración del modelo
        image_info: Información de la imagen

    Returns:
        Prompt para enviar al modelo
    """
    if model_config.provider == "gemini":
        # Gemini puede manejar imágenes directamente
        return "Analiza esta imagen según las instrucciones del sistema."
    else:
        # Para Ollama, verificar si el modelo tiene capacidades de visión
        if has_vision_capability(model_config.provider, model_config.model_name):
            # Modelo con capacidades de visión - puede procesar la imagen
            return (
                f"Analiza esta imagen según las instrucciones del sistema. "
                f"La imagen está en formato {image_info['format']} con dimensiones "
                f"{image_info['width']}x{image_info['height']} píxeles."
            )
        else:
            # Modelo solo de texto - usar descripción
            return (
                f"Analiza una imagen educativa con las siguientes características: "
                f"Formato: {image_info['format']}, "
                f"Tamaño: {image_info['width']}x{image_info['height']} píxeles, "
                f"Modo de color: {image_info['mode']}. "
                f"Proporciona un análisis detallado de lo que podría contener una imagen educativa "
                f"con estas características técnicas."
            )


async def execute_model(
    model_config: ModelConfig, image_base64: str, image_info: Dict[str, Any]
) -> ModelResponse:
    """
    Ejecuta un modelo específico con la imagen

    Args:
        model_config: Configuración del modelo
        image_base64: Imagen en formato base64
        image_info: Información de la imagen

    Returns:
        Respuesta del modelo con métricas
    """
    start_time = time.time()
    model_display_name = get_model_display_name(model_config)

    try:
        # Obtener el agente según la configuración
        agent = imagen_agente_analizador.get_agent(
            provider=model_config.provider, model_name=model_config.model_name
        )

        # Generar el prompt apropiado
        prompt = get_model_prompt(model_config, image_info)

        # Ejecutar el agente
        if model_config.provider == "gemini" or has_vision_capability(
            model_config.provider, model_config.model_name
        ):
            # Para modelos con capacidades de visión, pasar la imagen
            from pydantic_ai import BinaryContent
            import base64

            # Convertir base64 a bytes
            image_data = base64.b64decode(
                image_base64.split(",")[1] if "," in image_base64 else image_base64
            )

            # Crear contenido binario para la imagen
            binary_content = BinaryContent(
                data=image_data, media_type=f"image/{image_info['format'].lower()}"
            )

            # Ejecutar con imagen como parte del prompt
            result = await agent.run([prompt, binary_content])
        else:
            # Para modelos solo de texto
            result = await agent.run(prompt)

        execution_time = time.time() - start_time

        # Extraer el texto de la respuesta del AgentRunResult de pydantic-ai
        if hasattr(result, "output"):
            response_text = result.output
        elif hasattr(result, "data"):
            response_text = result.data
        else:
            response_text = str(result) if result else "Sin respuesta"

        return ModelResponse(
            model_name=model_display_name,
            provider=model_config.provider,
            response=response_text,
            execution_time=execution_time,
            success=True,
        )

    except Exception as e:
        execution_time = time.time() - start_time

        return ModelResponse(
            model_name=model_display_name,
            provider=model_config.provider,
            response="",
            execution_time=execution_time,
            success=False,
            error=str(e),
        )


def validate_model_configs(model_configs: List[ModelConfig]) -> None:
    """
    Valida la configuración de modelos

    Args:
        model_configs: Lista de configuraciones de modelos

    Raises:
        ValueError: Si la configuración no es válida
    """
    if len(model_configs) < 2:
        raise ValueError("Se requieren al menos 2 modelos para comparar")
