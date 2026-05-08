def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "ok"


def test_standard_error_response(client):
    response = client.post("/v1/example/process", json={"name": "", "value": -1})

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["errors"]

