# api/v1/__init__.py
from fastapi import APIRouter
from .endpoints import health,parse,returnlog


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(parse.router)
api_router.include_router(returnlog.router)

