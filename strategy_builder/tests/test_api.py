"""strategy_builder FastAPI 스모크 테스트"""


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "KIS Strategy Builder" in data["message"]


def test_cors_not_wildcard(client):
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    acl = resp.headers.get("access-control-allow-origin", "")
    assert acl != "*", "CORS should not allow wildcard origin"
    assert acl == "http://localhost:3000"


def test_cors_rejects_unknown_origin(client):
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    acl = resp.headers.get("access-control-allow-origin", "")
    assert acl != "http://evil.com", "CORS should reject unknown origins"


def test_auth_status_unauthenticated(client):
    resp = client.get("/api/auth/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is False


def test_docs_available(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_unknown_endpoint_404(client):
    resp = client.get("/api/nonexistent")
    assert resp.status_code == 404
