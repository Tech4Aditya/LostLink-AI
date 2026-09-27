from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from .config import get_settings

ALLOWED = {"image/jpeg", "image/png", "image/webp"}

async def save_upload(file: UploadFile) -> tuple[str, str]:
    settings = get_settings()
    if file.content_type not in ALLOWED:
        raise ValueError("Only JPEG, PNG and WebP images are supported")
    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise ValueError("Image exceeds configured size limit")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[file.content_type]
    name = f"{uuid4().hex}{ext}"
    root = Path(settings.upload_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_bytes(data)
    return str(path), file.content_type
