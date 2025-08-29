from typing import Dict, List, Any
from dataclasses import dataclass
import torch
import gc
from transformers import BlipProcessor, BlipForImageTextRetrieval
from PIL import Image


@dataclass
class MultimodalModelMetrics:
    """Métricas detalladas de un modelo multimodal - Solo ITM Score"""

    itm_score: float = 0.0


class MultimodalMetrics:
    def __init__(self):
        # Solo modelos BLIP para ITM
        self.blip_processor = None
        self.blip_model = None

        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _load_blip_models(self):
        """Carga los modelos BLIP bajo demanda"""
        if self.blip_processor is None or self.blip_model is None:
            print("[DEBUG] Cargando modelos BLIP...")
            self.blip_processor = BlipProcessor.from_pretrained(
                "Salesforce/blip-itm-base-coco"
            )
            self.blip_model = BlipForImageTextRetrieval.from_pretrained(
                "Salesforce/blip-itm-base-coco"
            ).to(self.device)
            print("[DEBUG] Modelos BLIP cargados correctamente")

    def _unload_blip_models(self):
        """Libera los modelos BLIP de memoria"""
        if self.blip_model is not None:
            self.blip_model.cpu()  # Mover a CPU primero
            del self.blip_model
            self.blip_model = None

        if self.blip_processor is not None:
            del self.blip_processor
            self.blip_processor = None

    def _cleanup_memory(self):
        """Limpieza general de memoria"""
        print("[DEBUG] Liberando memoria...")

        # Liberar modelos BLIP
        self._unload_blip_models()

        # Limpieza de PyTorch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        # Garbage collection
        gc.collect()
        gc.collect()
        gc.collect()

        print("[DEBUG] Memoria liberada")

    def compute_itm_score(self, image_path: str, caption: str) -> float:
        """
        Calcula ITM score (imagen-texto matching) usando BLIP.
        """
        try:
            print(f"[DEBUG][ITM] Calculando ITM score para: {caption[:50]}...")

            # Cargar modelos BLIP
            self._load_blip_models()

            # Procesar imagen y texto
            image = Image.open(image_path).convert("RGB")
            inputs = self.blip_processor(image, caption, return_tensors="pt").to(
                self.device
            )

            with torch.no_grad():
                outputs = self.blip_model(**inputs)

            # Calcular score
            if hasattr(outputs, "itm_score") and outputs.itm_score is not None:
                itm_tensor = outputs.itm_score
                if itm_tensor.numel() > 1:
                    match_prob = torch.sigmoid(itm_tensor[0]).item()
                else:
                    match_prob = torch.sigmoid(itm_tensor).item()
            elif hasattr(outputs, "logits") and outputs.logits is not None:
                itm_probs = torch.softmax(outputs.logits, dim=1)
                match_prob = itm_probs[0][1].item()
            else:
                match_prob = 0.5

            print(f"[DEBUG][ITM] Score calculado: {match_prob:.4f}")
            return float(match_prob)

        except Exception as e:
            print(f"[ERROR][ITM Score] {e}")
            import traceback

            print(f"[ERROR][ITM Score] Traceback: {traceback.format_exc()}")
            return 0.0
        finally:
            # Liberar modelos después de usar
            self._unload_blip_models()
            self._cleanup_memory()

    def compute_all_optimized(
        self, image_path: str, caption: str, references: List[str] | None = None
    ) -> MultimodalModelMetrics:
        """
        Calcula solo ITM score - versión simplificada sin otros modelos.
        """
        try:
            print(f"[DEBUG] Calculando solo ITM score para: {caption[:50]}...")

            # Solo calcular ITM score
            itm_score = self.compute_itm_score(image_path, caption)

            print(f"[DEBUG] ITM Score final: {itm_score:.4f}")

            return MultimodalModelMetrics(itm_score=float(itm_score))

        except Exception as e:
            print(f"[ERROR][Compute All Optimized] {e}")
            import traceback

            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            return MultimodalModelMetrics()

    def generate_image_references(
        self, image_path: str, num_references: int = 5
    ) -> List[str]:
        """
        Genera referencias simples sin usar modelos adicionales.
        """
        # Referencias genéricas para mantener compatibilidad
        return [
            "A detailed view of various visual elements",
            "A composition with multiple distinguishable features",
            "A scene with clearly visible objects and details",
            "An image containing recognizable elements",
            "A photograph with distinct visual components",
        ][:num_references]
