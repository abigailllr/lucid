from fastapi import APIRouter, HTTPException

from services import sessions

router = APIRouter()


@router.get("/last/{session_id}")
async def last(session_id: str):
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown session_id")
    return {"last_solution": session.get("last_solution")}
