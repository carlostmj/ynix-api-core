from dataclasses import dataclass
from typing import Any

SUPPORTED_LANGUAGES = ("python", "php", "javascript", "curl")


@dataclass(frozen=True)
class SdkEndpoint:
    method: str
    path: str
    name: str
    scopes: list[str]


class SdkGenerator:
    def __init__(self, openapi_schema: dict[str, Any]) -> None:
        self.openapi_schema = openapi_schema

    def endpoints(self) -> list[SdkEndpoint]:
        endpoints: list[SdkEndpoint] = []
        for path, methods in self.openapi_schema.get("paths", {}).items():
            for method, definition in methods.items():
                endpoints.append(
                    SdkEndpoint(
                        method=method.upper(),
                        path=path,
                        name=definition.get("operationId", f"{method}_{path}"),
                        scopes=definition.get("x-scopes", []),
                    )
                )
        return endpoints

    def generate(self, language: str) -> str:
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Linguagem nao suportada: {language}")
        return f"SDK generator base preparado para {language}. Endpoints: {len(self.endpoints())}"
