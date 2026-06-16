from fastapi import APIRouter

from app.api.routes import health, trade

api_router = APIRouter()

api_router.include_router(trade.router)
api_router.include_router(health.router)