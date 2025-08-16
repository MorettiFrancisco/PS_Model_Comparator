"""
Configuración y datos de modelos disponibles
"""

from typing import Dict, Any, Union, List


def get_available_models() -> Dict[str, Any]:
    """
    Retorna información sobre los modelos disponibles

    Returns:
        Diccionario con información de modelos por proveedor
    """
    return {
        "gemini": {
            "models": ["gemini-1.5-flash"],
            "provider": "gemini",
            "capabilities": ["text", "vision"],
        },
        "ollama": {
            "models": ["gemma3:4b", "qwen2.5vl:7b"],
            "provider": "ollama",
            "capabilities": {
                "gemma3:4b": ["text", "vision"],
                "qwen2.5vl:7b": ["text", "vision"],
            },
            "note": "Estos modelos están configurados en el docker-compose.yml y se descargan automáticamente",
        },
    }


def get_model_capabilities(
    provider: str, model_name: Union[str, None] = None
) -> List[str]:
    """
    Obtiene las capacidades de un modelo específico

    Args:
        provider: Proveedor del modelo ("gemini" o "ollama")
        model_name: Nombre del modelo (para ollama)

    Returns:
        Lista de capacidades del modelo
    """
    models_info = get_available_models()

    if provider == "gemini":
        return models_info["gemini"]["capabilities"]
    elif provider == "ollama" and model_name:
        capabilities = models_info["ollama"]["capabilities"]
        return capabilities.get(model_name, ["text"])

    return ["text"]  # Default fallback


def has_vision_capability(provider: str, model_name: Union[str, None] = None) -> bool:
    """
    Verifica si un modelo tiene capacidades de visión

    Args:
        provider: Proveedor del modelo
        model_name: Nombre del modelo

    Returns:
        True si el modelo puede procesar imágenes
    """
    capabilities = get_model_capabilities(provider, model_name)
    return "vision" in capabilities
