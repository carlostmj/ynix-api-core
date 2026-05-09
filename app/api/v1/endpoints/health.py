from fastapi import APIRouter
from fastapi.responses import Response

from app.core.maintenance import get_maintenance_state
from app.core.responses import success_response

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    state = get_maintenance_state()
    return success_response("API online", {"status": "ok", "maintenance": state.enabled})


@router.get("/")
def root():
    state = get_maintenance_state()
    return success_response(
        "Ynix FastAPI Core online",
        {"docs": "/docs", "health": "/health", "maintenance": state.enabled},
    )


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@router.get("/service-worker.js", include_in_schema=False)
def service_worker():
    return Response(status_code=204, media_type="application/javascript")
