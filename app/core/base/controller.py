from typing import Any

from app.core.responses import error_response, paginated_response, success_response


class BaseController:
    def success(self, message: str = "Operacao realizada com sucesso", data: Any = None, status_code: int = 200):
        return success_response(message, data, status_code)

    def error(self, message: str = "Erro na requisicao", errors: Any = None, status_code: int = 400):
        return error_response(message, errors, status_code)

    def paginated(self, data: list[Any], total: int, page: int, per_page: int, message: str = "Operacao realizada"):
        return paginated_response(data, total, page, per_page, message)
