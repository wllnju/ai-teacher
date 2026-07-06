from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api import upload, chat, voice, progress, documents, diagram

app = FastAPI(
    title=settings.app_name,
    description="AI-powered teacher with RAG and voice interaction.",
    version="0.1.0",
    debug=settings.app_debug,
)


app.include_router(upload.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(voice.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(diagram.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"}) 