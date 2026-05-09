from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.base import create_router
from app.modules.example.controllers import ExampleController
from app.modules.example.requests import ExampleProcessRequest

router = create_router(prefix="/example", tags=["Example"])


@router.post("/process")
def process(payload: ExampleProcessRequest, db: Session = Depends(get_db)):
    return ExampleController(db).process(payload)
