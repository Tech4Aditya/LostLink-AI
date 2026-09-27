from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import re
import numpy as np

from ..config import get_settings

class MultimodalEncoder:
    """Lazy SigLIP encoder. Product APIs never import/load the model at startup."""

    def __init__(self):
        self.settings = get_settings()
        self._processor = None
        self._model = None
        self._torch = None
        self.available = False
        self.error: str | None = None

    def _load(self):
        if self._model is not None:
            return
        if not self.settings.ai_enabled:
            self.error = "AI disabled by configuration"
            return
        try:
            import torch
            from transformers import AutoProcessor, AutoModel
            device = self.settings.ai_device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            self._torch = torch
            self._processor = AutoProcessor.from_pretrained(self.settings.ai_model_id)
            self._model = AutoModel.from_pretrained(self.settings.ai_model_id)
            self._model.to(device)
            self._model.eval()
            self.available = True
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            self.available = False

    def text(self, text: str) -> list[float] | None:
        self._load()
        if not self.available:
            return None
        inputs = self._processor(text=[text], return_tensors="pt", padding="max_length", truncation=True)
        device = next(self._model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with self._torch.inference_mode():
            out = self._model.get_text_features(**inputs)
        vec = out[0].detach().float().cpu().numpy()
        vec /= max(np.linalg.norm(vec), 1e-12)
        return vec.tolist()

    def image(self, path: str) -> list[float] | None:
        self._load()
        if not self.available:
            return None
        from PIL import Image
        img = Image.open(path).convert("RGB")
        inputs = self._processor(images=img, return_tensors="pt")
        device = next(self._model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with self._torch.inference_mode():
            out = self._model.get_image_features(**inputs)
        vec = out[0].detach().float().cpu().numpy()
        vec /= max(np.linalg.norm(vec), 1e-12)
        return vec.tolist()

@lru_cache
def get_encoder():
    return MultimodalEncoder()

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())
