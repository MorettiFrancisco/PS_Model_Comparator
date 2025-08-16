"""
Utilidades de validación para la API
"""

import json
from typing import List
from fastapi import HTTPException
from .models import ModelConfig


def parse_models_config(models_json: str) -> List[ModelConfig]:
    """
    Parsea y valida la configuración de modelos desde JSON

    Args:
        models_json: String JSON con configuraciones de modelos

    Returns:
        Lista de configuraciones de modelos validadas

    Raises:
        HTTPException: Si hay errores en la configuración
    """
    try:
        print(f"🔍 DEBUG: Parsing models JSON: '{models_json}'")
        models_config = json.loads(models_json)
        model_configs = []

        for config in models_config:
            # Validar que tenga provider
            if not isinstance(config, dict) or "provider" not in config:
                raise ValueError("Cada configuración debe ser un objeto con 'provider'")

            provider = config["provider"]
            model_name = config.get("model_name", None)
            model_configs.append(ModelConfig(provider=provider, model_name=model_name))

        print(f"🔍 DEBUG: Final model configs: {model_configs}")
        return model_configs

    except (json.JSONDecodeError, ValueError) as e:
        print(f"🔍 DEBUG: Exception in parse_models_config: {e}")
        raise HTTPException(
            status_code=400, detail=f"Error en configuración de modelos: {str(e)}"
        )


def validate_models_for_comparison(model_configs: List[ModelConfig]) -> None:
    """
    Valida que la configuración de modelos sea válida para comparación

    Args:
        model_configs: Lista de configuraciones de modelos

    Raises:
        HTTPException: Si la configuración no es válida para comparación
    """
    if len(model_configs) < 2:
        raise HTTPException(
            status_code=400, detail="Se requieren al menos 2 modelos para comparar"
        )

    # Verificar que los proveedores sean válidos
    valid_providers = {"gemini", "ollama"}
    for config in model_configs:
        if config.provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Proveedor no válido: {config.provider}. "
                f"Proveedores válidos: {', '.join(valid_providers)}",
            )
