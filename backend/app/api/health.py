from fastapi import APIRouter
from ..ai.encoder import get_encoder
from ..config import get_settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    settings = get_settings()
    encoder = get_encoder()
    return {
        "status": "ok",
        "environment": settings.app_env,
        "ai_enabled": settings.ai_enabled,
        "ai_loaded": encoder.available,
        "ai_error": encoder.error,
        "model": settings.ai_model_id,
    }
