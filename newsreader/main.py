import os

print("API_KEY:", os.getenv("API_KEY"))

from fastapi import FastAPI
from newsreader.api.routers import user_router, news_router
from newsreader.container import Container
from newsreader.db import database, init_db
from contextlib import asynccontextmanager
from typing import AsyncGenerator

container = Container()
container.wire(modules=["newsreader.api.routers"])


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Lifespan function working on app startup."""
    await init_db()
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(debug=True, lifespan=lifespan)
app.include_router(user_router, prefix="/user")
app.include_router(news_router, prefix="/news")
