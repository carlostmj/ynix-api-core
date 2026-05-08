from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(
    message: str = "Operação realizada com sucesso",
    data: Any = None,
    status_code: int = 200,
) -> JSONResponse:
    content = {
        "success": True,
        "message": message,
        "data": data if data is not None else {},
        "errors": None,
    }
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content),
    )


def error_response(message: str = "Erro na requisição", errors: Any = None, status_code: int = 400) -> JSONResponse:
    content = {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors if errors is not None else {},
    }
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content),
    )


def paginated_response(
    data: list[Any],
    total: int,
    page: int,
    per_page: int,
    message: str = "Operação realizada com sucesso",
) -> JSONResponse:
    pages = (total + per_page - 1) // per_page if per_page else 0
    return success_response(
        message=message,
        data={"items": data, "meta": {"total": total, "page": page, "per_page": per_page, "pages": pages}},
    )
