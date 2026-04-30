from __future__ import annotations

import uuid


def _register(client, label: str) -> tuple[str, str]:
    email = f"{label}_{uuid.uuid4().hex[:10]}@t.example"
    r = client.post("/auth/register", json={"email": email, "password": "longpassword1"})
    assert r.status_code == 201, r.text
    return email, r.json()["access_token"]


def test_create_course_and_list(client):
    _, token = _register(client, "owner")
    r = client.post(
        "/courses",
        json={"title": "Day 10 Integration Course"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, r.text
    course_id = r.json()["id"]

    r2 = client.get("/courses", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    courses = r2.json()
    assert len(courses) == 1
    assert courses[0]["id"] == course_id


def test_non_member_cannot_get_course(client):
    _, token_a = _register(client, "a")
    r = client.post(
        "/courses",
        json={"title": "Private course"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 201
    course_id = r.json()["id"]

    _, token_b = _register(client, "b")
    r2 = client.get(f"/courses/{course_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert r2.status_code == 403
