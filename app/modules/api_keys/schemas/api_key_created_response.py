from .api_key_response import ApiKeyResponse


class ApiKeyCreatedResponse(ApiKeyResponse):
    api_key: str
