from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings


router = APIRouter()


@router.get("/documents", tags=["Documents"])
async def list_documents() -> JSONResponse:
    import json
    from pathlib import Path
    p = Path(settings.documents_json)
    if not p.exists():
        return JSONResponse({"documents": []})
    data = json.loads(p.read_text(encoding="utf-8"))
    return JSONResponse({"documents": list(data.values())}) 