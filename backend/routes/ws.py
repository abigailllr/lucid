import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services import sessions
from services.connection_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    session_id = websocket.query_params.get("session")
    if not session_id or sessions.get(session_id) is None:
        await websocket.close(code=4001)
        return

    manager.connect(session_id, websocket)
    logger.info("HUD connected: %s", session_id)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
        logger.info("HUD disconnected: %s", session_id)
