from fastapi import Depends

from app.core.base import create_router
from app.modules.example.controllers import ExampleController
from app.modules.example.requests import ExampleProcessRequest

router = create_router(prefix="/example", tags=["Example"])


@router.post("/process")
def process(
    payload: ExampleProcessRequest,
    controller: ExampleController = Depends(ExampleController),
):
    return controller.process(payload)
