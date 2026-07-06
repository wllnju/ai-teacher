from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/progress/{session_id}", tags=["Progress"])
async def get_progress(session_id: str) -> JSONResponse:
    return JSONResponse({
        "session_id": session_id,
        "mastery": 0.0,
        "quizzes_completed": 0,
        "resources_viewed": 0,
        "message": "TODO: fetch mastery tracking",
    }) 