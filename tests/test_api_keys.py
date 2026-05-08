def test_create_api_key(client):
    response = client.post("/v1/api-keys", json={"name": "Default", "scopes": ["*"]})

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["api_key"].startswith("ynix_")
    assert "key_hash" not in body["data"]


def test_authenticate_by_api_key(client):
    created = client.post("/v1/api-keys", json={"name": "Default", "scopes": ["*"]}).json()
    api_key = created["data"]["api_key"]

    response = client.get("/v1/api-keys/me", headers={"X-API-Key": api_key})

    assert response.status_code == 200
    assert response.json()["success"] is True

