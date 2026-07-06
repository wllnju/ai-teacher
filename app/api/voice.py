from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/voice/status", tags=["Voice"])
async def voice_status() -> JSONResponse:
    return JSONResponse({"enabled": True, "interruption_supported": True})


@router.websocket("/ws/voice")
async def voice_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket.send_json({
                "event": "transcript",
                "text": "TODO: transcribe audio",
            })
            await websocket.send_json({
                "event": "audio",
                "bytes": "",
            })
    except WebSocketDisconnect:
        pass 