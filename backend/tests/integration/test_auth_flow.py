"""Integration testler — register + login + token."""


def test_register_creates_user(client):
    r = client.post("/register", json={
        "username": "bob",
        "email": "bob@example.com",
        "password": "pass1234",
    })
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "bob"
    assert body["email"] == "bob@example.com"
    assert "id" in body
    assert "hashed_password" not in body


def test_register_duplicate_email_fails(client):
    payload = {"username": "user1", "email": "a@x.com", "password": "abcdef"}
    payload2 = {"username": "user2", "email": "a@x.com", "password": "abcdef"}
    assert client.post("/register", json=payload).status_code == 201
    r = client.post("/register", json=payload2)
    assert r.status_code == 400


def test_register_duplicate_username_fails(client):
    payload = {"username": "samename", "email": "x1@x.com", "password": "abcdef"}
    payload2 = {"username": "samename", "email": "x2@x.com", "password": "abcdef"}
    assert client.post("/register", json=payload).status_code == 201
    r = client.post("/register", json=payload2)
    assert r.status_code == 400


def test_login_returns_token(client):
    client.post("/register", json={
        "username": "carol", "email": "c@x.com", "password": "abcdef"
    })
    r = client.post("/login", json={"email": "c@x.com", "password": "abcdef"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token


def test_login_wrong_password(client):
    client.post("/register", json={
        "username": "dan", "email": "d@x.com", "password": "abcdef"
    })
    r = client.post("/login", json={"email": "d@x.com", "password": "wrong"})
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post("/login", json={"email": "nobody@x.com", "password": "abcdef"})
    assert r.status_code == 401


def test_protected_endpoint_without_token(client):
    r = client.get("/habits")
    assert r.status_code == 401


def test_protected_endpoint_with_invalid_token(client):
    r = client.get("/habits", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401
