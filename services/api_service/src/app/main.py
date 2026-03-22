from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.event_publisher import event_publisher


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await event_publisher.start()
    try:
        yield
    finally:
        await event_publisher.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)
