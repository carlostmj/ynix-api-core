import json
from uuid import uuid4


def make_job_payload(name: str, payload: dict | None = None, attempts: int = 0) -> str:
    return json.dumps(
        {
            "id": str(uuid4()),
            "name": name,
            "payload": payload or {},
            "attempts": attempts,
        }
    )


def parse_job_payload(raw: str) -> dict:
    return json.loads(raw)

