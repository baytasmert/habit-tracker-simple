"""Integration testler — habit CRUD + tracking + streak."""
from datetime import date, timedelta


def test_create_and_list_habit(client, auth_headers):
    r = client.post("/habits", json={
        "name": "Run", "description": "30m", "category": "fitness",
        "goal_days_per_week": 5,
    }, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["name"] == "Run"

    listing = client.get("/habits", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_user_only_sees_own_habits(client, auth_headers):
    client.post("/habits", json={"name": "Mine"}, headers=auth_headers)

    client.post("/register", json={
        "username": "other", "email": "other@x.com", "password": "abcdef"
    })
    login = client.post("/login", json={"email": "other@x.com", "password": "abcdef"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    r = client.get("/habits", headers=other_headers)
    assert r.json() == []


def test_track_creates_log(client, auth_headers):
    h = client.post("/habits", json={"name": "Read"}, headers=auth_headers).json()
    r = client.post(f"/habits/{h['id']}/track", json={"done": True, "notes": "ok"},
                    headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["done"] is True


def test_track_updates_existing_log_same_day(client, auth_headers):
    h = client.post("/habits", json={"name": "Read"}, headers=auth_headers).json()
    client.post(f"/habits/{h['id']}/track", json={"done": True}, headers=auth_headers)
    r = client.post(f"/habits/{h['id']}/track", json={"done": False, "notes": "skipped"},
                    headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["done"] is False


def test_track_unknown_habit_404(client, auth_headers):
    r = client.post("/habits/999/track", json={"done": True}, headers=auth_headers)
    assert r.status_code == 404


def test_streak_calculation(client, auth_headers):
    h = client.post("/habits", json={"name": "Meditate"}, headers=auth_headers).json()
    today = date.today()
    for i in range(3):
        d = (today - timedelta(days=i)).isoformat()
        client.post(f"/habits/{h['id']}/track",
                    json={"done": True, "log_date": d}, headers=auth_headers)

    r = client.get(f"/habits/{h['id']}/streak", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["current_streak"] == 3
    assert body["total_completed"] == 3


def test_streak_breaks_on_gap(client, auth_headers):
    h = client.post("/habits", json={"name": "Meditate"}, headers=auth_headers).json()
    today = date.today()
    # done today, skipped yesterday, done 2 days ago → streak = 1
    client.post(f"/habits/{h['id']}/track",
                json={"done": True, "log_date": today.isoformat()}, headers=auth_headers)
    client.post(f"/habits/{h['id']}/track",
                json={"done": True, "log_date": (today - timedelta(days=2)).isoformat()},
                headers=auth_headers)

    r = client.get(f"/habits/{h['id']}/streak", headers=auth_headers)
    assert r.json()["current_streak"] == 1


def test_streak_unknown_habit_404(client, auth_headers):
    r = client.get("/habits/999/streak", headers=auth_headers)
    assert r.status_code == 404


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_metrics_endpoint(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
