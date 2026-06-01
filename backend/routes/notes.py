import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import notes, sessions

router = APIRouter()


class AddNotesRequest(BaseModel):
    session_id: str
    text: str


def _require(session_id: str) -> dict:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown session_id")
    return session


@router.post("/add")
async def add(req: AddNotesRequest):
    session = _require(req.session_id)
    added = await asyncio.to_thread(notes.add, session, req.text)
    return {"added_chunks": added, "total": notes.count(session)}


@router.get("/{session_id}")
async def info(session_id: str):
    session = _require(session_id)
    return {"total": notes.count(session)}


@router.delete("/{session_id}")
async def clear(session_id: str):
    session = _require(session_id)
    notes.clear(session)
    return {"total": 0}
