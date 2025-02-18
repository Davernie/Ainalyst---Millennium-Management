from fastapi import APIRouter
from api.v1.endpoints import health
from api.v1.endpoints import parse

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(parse.router)