from fastapi import APIRouter, HTTPException

import providers
from models.solve import RekeyRequest, StartSessionRequest
from services import crypto, sessions

router = APIRouter()


def _establish_channel(session_id: str, client_public_key: str) -> str:
    server_private, server_public = crypto.generate_keypair()
    root = crypto.derive_root(server_private, client_public_key)
    sessions.set_channel(session_id, crypto.SecureChannel(root))
    return server_public


@router.post("/start")
async def start(req: StartSessionRequest):
    if req.provider and req.provider != "ensemble" and req.provider not in providers.available_providers():
        raise HTTPException(status_code=422, detail=f"provider not available: {req.provider}")

    session = sessions.create(mode=req.mode, provider=req.provider, translate_to=req.translate_to)

    response = {
        "session_id": session["id"],
        "mode": session["mode"],
        "provider": session["provider"],
        "translate_to": session["translate_to"],
        "available_providers": providers.available_providers(),
        "encrypted": False,
    }

    if req.client_public_key:
        server_public = _establish_channel(session["id"], req.client_public_key)
        response["server_public_key"] = server_public
        response["encrypted"] = True

    return response


@router.post("/rekey")
async def rekey(req: RekeyRequest):
    if sessions.get(req.session_id) is None:
        raise HTTPException(status_code=404, detail="unknown session_id")
    server_public = _establish_channel(req.session_id, req.client_public_key)
    return {"server_public_key": server_public}
