from shopflow.mcp_server import mcp_app


def test_mcp_http_app_is_asgi_callable():
    assert callable(mcp_app)
