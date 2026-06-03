import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import capture, device, display, health, notes, session, ws
from services import cache, embeddings, sessions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


async def _purge_loop():
    while True:
        await asyncio.sleep(settings.purge_interval_seconds)
        sessions_removed = sessions.purge_expired(settings.session_ttl_seconds)
        cache_removed = cache.purge_expired()
        if sessions_removed or cache_removed:
            logger.info("purged %d sessions, %d cache entries", sessions_removed, cache_removed)


async def _warm_embeddings():
    try:
        await asyncio.to_thread(embeddings.embed, ["warm up"])
        logger.info("embedding model warmed")
    except Exception as e:
        logger.warning("embedding warmup skipped: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(_warm_embeddings())
    task = asyncio.create_task(_purge_loop())
    yield
    task.cancel()


app = FastAPI(title="lucid", lifespan=lifespan)

_cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(capture.router, prefix="/capture", tags=["capture"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(device.router, prefix="/device", tags=["device"])
app.include_router(display.router, prefix="/display", tags=["display"])
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(ws.router, tags=["ws"])


@app.get("/")
async def root():
    return {"status": "lucid running"}
