from __future__ import annotations


def test_health_ok(client):
    r = client.get("/internal/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_database(client):
    r = client.get("/internal/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"


def test_x_request_id_on_response(client):
    r = client.get("/internal/health")
    assert r.status_code == 200
    rid = r.headers.get("X-Request-ID") or r.headers.get("x-request-id")
    assert rid and len(rid) >= 8
