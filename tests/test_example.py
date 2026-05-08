def test_example_process(client):
    response = client.post("/v1/example/process", json={"name": "Carlos", "value": 100})

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Processado com sucesso",
        "data": {"name": "Carlos", "value": 100, "processed": True},
        "errors": None,
    }

