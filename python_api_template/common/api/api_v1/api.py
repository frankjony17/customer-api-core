from fastapi import APIRouter

from .endpoints import healthcheck, root

api_router = APIRouter()
api_router.include_router(root.router, tags=["Common"])
api_router.include_router(healthcheck.router, prefix="/healthcheck", tags=["Common"])
