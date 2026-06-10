from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import trade
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield

app = FastAPI(lifespan=lifespan, title="Crypto Data Platform")
app.include_router(trade.router)