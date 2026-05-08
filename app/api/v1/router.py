from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.core.modules import load_module_routes

router = APIRouter()
router.include_router(health.router)
load_module_routes(router)
