from typing import Dict
from dataclasses import dataclass
from .text_analyze_metric import ModelMetricsAnalyzer as TextOnlyMetricsAnalyzer
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForImageTextRetrieval


@dataclass
class MultimodalMetrics:
    itm_score: float  # Cambiado de clip_score a itm_score
    object_precision: float
    object_recall: float
    hallucination_rate: float
    robustness_score: float
    safety_flag: bool


class MultimodalMetricsAnalyzer(TextOnlyMetricsAnalyzer):
    def __init__(self, device=None):
        super().__init__()
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        try:
            # Cargar BLIP-ITM base model
            model_name = "Salesforce/blip-itm-base-coco"
            self.blip_processor = BlipProcessor.from_pretrained(model_name)
            self.blip_model = BlipForImageTextRetrieval.from_pretrained(model_name)
            self.blip_model.to(self.device)
            self.blip_model.eval()
            print(
                f"✅ BLIP-ITM model {model_name} loaded successfully on {self.device}"
            )
        except Exception as e:
            print(f"⚠️  Warning: No se pudo cargar BLIP-ITM: {e}")
            self.blip_processor = None
            self.blip_model = None

        # YOLO es opcional, usar detección básica como fallback
        self.yolo_model = None
        print("ℹ️  Using keyword-based object detection (YOLO not available)")

    def compute_itm_score(self, image_path: str, caption: str) -> float:
        """Calcula el score ITM (Image-Text Matching) con BLIP"""
        if not self.blip_model or not self.blip_processor:
            return 0.5  # Score neutro si BLIP no está disponible

        try:
            print("🔍 BLIP-ITM DEBUG:")
            print(f"   Caption length: {len(caption)} chars")
            print(f"   Caption: '{caption[:100]}{'...' if len(caption) > 100 else ''}'")

            # Cargar y procesar la imagen
            image = Image.open(image_path).convert("RGB")

            # Procesar imagen y texto (BLIP puede manejar hasta 512 tokens)
            inputs = self.blip_processor(
                images=image,
                text=caption,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )

            # Mover inputs al dispositivo
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                # Obtener outputs del modelo BLIP-ITM
                outputs = self.blip_model(**inputs)

                # Debug: ver qué atributos tiene el output
                print(f"   Output type: {type(outputs)}")
                print(
                    f"   Output attributes: {[attr for attr in dir(outputs) if not attr.startswith('_')]}"
                )

                # Intentar diferentes formas de acceder a los scores
                if hasattr(outputs, "itm_score"):
                    itm_tensor = outputs.itm_score
                    print(f"   ITM tensor shape: {itm_tensor.shape}")
                    print(f"   ITM tensor values: {itm_tensor}")

                    # El tensor tiene 2 elementos [no_match_logit, match_logit]
                    # Aplicar softmax para obtener probabilidades
                    itm_probs = torch.softmax(itm_tensor, dim=-1)
                    # La probabilidad de match está en el índice [0, 1] (primera fila, segunda columna)
                    match_prob = itm_probs[0, 1].item()
                elif hasattr(outputs, "logits"):
                    # Aplicar softmax para obtener probabilidades
                    itm_probs = torch.softmax(outputs.logits, dim=1)
                    # La probabilidad de match está en el índice 1
                    match_prob = itm_probs[0][1].item()
                elif hasattr(outputs, "prediction_scores"):
                    # Algunos modelos BLIP usan prediction_scores
                    logits = outputs.prediction_scores
                    probs = torch.softmax(logits, dim=-1)
                    match_prob = (
                        probs[0][1].item()
                        if probs.shape[-1] > 1
                        else probs[0][0].item()
                    )
                elif hasattr(outputs, "last_hidden_state"):
                    # Fallback: usar el estado oculto como proxy
                    hidden_state = outputs.last_hidden_state
                    match_prob = torch.sigmoid(hidden_state.mean()).item()
                else:
                    print("   Warning: No se encontró score válido, usando 0.5")
                    match_prob = 0.5

            print(f"   ITM match probability: {match_prob:.4f}")
            return match_prob

        except Exception as e:
            print(f"Error calculando ITM score: {e}")
            return 0.0

    def compute_object_metrics(self, image_path: str, caption: str) -> Dict[str, float]:
        """Calcula precisión/recall de objetos detectados vs mencionados"""
        detected_objects = set()

        # Por ahora usar detección básica por keywords (YOLO opcional)
        caption_lower = caption.lower()
        detected_objects = {obj for obj in self.object_keywords if obj in caption_lower}

        mentioned_objects = {
            w for w in caption_lower.split() if w in self.object_keywords
        }

        tp = len(detected_objects & mentioned_objects)
        fp = len(mentioned_objects - detected_objects)
        fn = len(detected_objects - mentioned_objects)

        precision = tp / (tp + fp + 1e-6)
        recall = tp / (tp + fn + 1e-6)
        halluc_rate = fp / (len(mentioned_objects) + 1e-6)

        return {
            "object_precision": precision,
            "object_recall": recall,
            "hallucination_rate": halluc_rate,
        }

    def analyze_multimodal(self, image_path: str, caption: str) -> MultimodalMetrics:
        itm_score = self.compute_itm_score(image_path, caption)
        obj_metrics = self.compute_object_metrics(image_path, caption)

        # Placeholder de robustez y seguridad
        robustness_score = 1.0
        safety_flag = False

        return MultimodalMetrics(
            itm_score=itm_score,
            object_precision=obj_metrics["object_precision"],
            object_recall=obj_metrics["object_recall"],
            hallucination_rate=obj_metrics["hallucination_rate"],
            robustness_score=robustness_score,
            safety_flag=safety_flag,
        )
