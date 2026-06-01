import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}

    def connect(self, key: str, websocket: WebSocket) -> None:
        self._connections.setdefault(key, set()).add(websocket)

    def disconnect(self, key: str, websocket: WebSocket) -> None:
        connections = self._connections.get(key)
        if connections:
            connections.discard(websocket)
            if not connections:
                del self._connections[key]

    async def push(self, key: str, message: dict) -> None:
        for websocket in list(self._connections.get(key, ())):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning("HUD push failed for %s: %s", key, e)


manager = ConnectionManager()
