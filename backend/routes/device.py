from fastapi import APIRouter, HTTPException

from models.solve import HeartbeatRequest
from services import device, sessions

router = APIRouter()


@router.post("/heartbeat")
async def heartbeat(req: HeartbeatRequest):
    session = sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown session_id")
    return device.heartbeat(session, req.battery, req.temperature_c)
