from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.middlewares.context import RequestContextMiddleware
from app.core.middlewares.rate_limit import RateLimitState, rate_limit_lock, rate_limit_store, rate_limit_store_ttl_seconds


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
