"""backtester FastAPI 스모크 테스트"""


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "kis_backtest"


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_docs_available(client):
    resp = client.get("/api/docs")
    assert resp.status_code == 200


def test_unknown_endpoint_404(client):
    resp = client.get("/api/nonexistent")
    assert resp.status_code == 404
