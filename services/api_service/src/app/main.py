from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.config import settings
from app.services.event_publisher import event_publisher


@asynccontextmanager
async def lifespan(_: FastAPI):
    await event_publisher.start()
    try:
        yield
    finally:
        await event_publisher.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)
