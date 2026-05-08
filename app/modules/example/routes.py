from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.example.controller import ExampleController
from app.modules.example.schemas import ExampleProcessRequest

router = APIRouter(prefix="/example", tags=["Example"])


@router.post("/process")
def process(payload: ExampleProcessRequest, db: Session = Depends(get_db)):
    return ExampleController(db).process(payload)

