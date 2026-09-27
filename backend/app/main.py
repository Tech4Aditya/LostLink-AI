from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .api import auth, reports, matches, health

settings = get_settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="LostLink API",
    version="1.0.0",
    description="Lost and found recovery with ranked candidate matching and privacy-first verification.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    # Keep browser responses useful while avoiding stack traces in the client.
    return JSONResponse(
        status_code=500,
        content={"detail": "Server error. Check the backend logs for details."},
    )


app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(matches.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"name": "LostLink", "status": "online", "docs": "/docs"}
