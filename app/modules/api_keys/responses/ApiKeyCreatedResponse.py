from .ApiKeyResponse import ApiKeyResponse


class ApiKeyCreatedResponse(ApiKeyResponse):
    api_key: str
