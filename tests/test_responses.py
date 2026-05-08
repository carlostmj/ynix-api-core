from app.core.responses import error_response


def test_error_response_serializes_bytes():
    response = error_response("Erro de validação", [{"input": b'{"email":"x"}'}], 422)

    assert response.status_code == 422
    body = response.body.decode("utf-8")
    assert "bytes" not in body
    assert '"success":false' in body
