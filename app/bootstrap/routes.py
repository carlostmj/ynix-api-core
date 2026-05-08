from fastapi import FastAPI

from app.api.v1.endpoints.health import router as root_health_router
from app.api.v1.router import router as api_v1_router


def register_routes(app: FastAPI) -> None:
    app.include_router(root_health_router)
    app.include_router(api_v1_router, prefix="/v1")

