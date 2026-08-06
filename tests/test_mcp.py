from starlette.testclient import TestClient

from shopflow.mcp_server import app, mcp_app


def test_mcp_http_app_is_asgi_callable():
    assert callable(mcp_app)
    assert callable(app)


def test_vercel_rewrite_path_accepts_mcp_initialize():
    with TestClient(app) as client:
        response = client.post(
            "/api/index.py",
            headers={"accept": "application/json, text/event-stream"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "vercel-path-test", "version": "1.0"},
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["result"]["serverInfo"]["name"] == "shopflow-delivery-knowledge"
