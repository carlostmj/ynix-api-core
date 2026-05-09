def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "ok"


def test_root_renders_html_for_browsers(client):
    response = client.get("/", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Ynix FastAPI Core" in response.text
    assert "status: 200" in response.text
    assert "#22c55e" in response.text or "#f59e0b" in response.text


def test_root_returns_json_for_api_clients(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["docs"] == "/docs"
    assert body["data"]["health"] == "/health"
    assert "maintenance" in body["data"]


def test_standard_error_response(client):
    response = client.post("/v1/example/process", json={"name": "", "value": -1})

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["errors"]
