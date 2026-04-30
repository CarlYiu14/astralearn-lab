from __future__ import annotations

import uuid


def test_register_login_me_and_refresh_rotation(client):
    email = f"u_{uuid.uuid4().hex[:14]}@t.example"
    r = client.post("/auth/register", json={"email": email, "password": "longpassword1", "name": "Pytest"})
    assert r.status_code == 201
    body = r.json()
    assert "access_token" in body and "refresh_token" in body
    access = body["access_token"]
    refresh = body["refresh_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == email

    r2 = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["refresh_token"] != refresh
    access2 = body2["access_token"]

    reuse = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert reuse.status_code == 401

    me2 = client.get("/auth/me", headers={"Authorization": f"Bearer {access2}"})
    assert me2.status_code == 200


def test_me_without_token(client):
    r = client.get("/auth/me")
    assert r.status_code == 401
