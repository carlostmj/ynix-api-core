def test_admin_login_and_health(client):
    login = client.post(
        "/v1/admin/auth/login",
        json={"email": "admin@example.com", "password": "admin123456"},
    )

    assert login.status_code == 200
    token = login.json()["data"]["access_token"]

    health = client.get("/v1/admin/system/health", headers={"Authorization": f"Bearer {token}"})

    assert health.status_code == 200
    assert health.json()["success"] is True
    assert health.json()["data"]["database"] == "ok"
