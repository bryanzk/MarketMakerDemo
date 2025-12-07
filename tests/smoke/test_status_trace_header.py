from fastapi.testclient import TestClient

import server


def test_status_includes_trace_header_and_ok_flag():
    """Smoke test: /api/status returns ok payload and trace header."""
    client = TestClient(server.app)

    response = client.get("/api/status")

    assert response.status_code == 200
    assert "X-Trace-ID" in response.headers
    data = response.json()
    assert "ok" in data or "active" in data  # backward compatible keys
