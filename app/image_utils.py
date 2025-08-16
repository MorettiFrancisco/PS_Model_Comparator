"""
Utilidades para procesamiento de imágenes
"""

import io
import base64
from typing import Dict, Any, Tuple
from PIL import Image
from fastapi import HTTPException


def process_image(image_file: bytes) -> Tuple[Image.Image, Dict[str, Any]]:
    """
    Procesa la imagen subida y extrae información básica

    Args:
        image_file: Bytes de la imagen

    Returns:
        Tupla con la imagen PIL y información de la imagen
    """
    try:
        image = Image.open(io.BytesIO(image_file))

        # Información básica de la imagen
        image_info = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "width": image.width,
            "height": image.height,
        }

        return image, image_info
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error procesando imagen: {str(e)}"
        )


def image_to_base64(image_bytes: bytes) -> str:
    """
    Convierte bytes de imagen a base64

    Args:
        image_bytes: Bytes de la imagen

    Returns:
        String en base64
    """
    return base64.b64encode(image_bytes).decode()


def validate_image_file(content_type: str) -> None:
    """
    Valida que el archivo subido sea una imagen

    Args:
        content_type: Tipo de contenido del archivo

    Raises:
        HTTPException: Si el archivo no es una imagen válida
    """
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
