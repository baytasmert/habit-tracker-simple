"""Integration testler — günlük kayıt geçmişi (logs) + habit silme."""
from datetime import date, timedelta


def _make_habit(client, auth_headers, name="Su iç"):
    return client.post("/habits", json={"name": name}, headers=auth_headers).json()


def test_logs_empty_for_new_habit(client, auth_headers):
    habit = _make_habit(client, auth_headers)
    r = client.get(f"/habits/{habit['id']}/logs", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_logs_returns_tracked_days_desc(client, auth_headers):
    habit = _make_habit(client, auth_headers)
    today = date.today()
    for i in range(3):
        d = (today - timedelta(days=i)).isoformat()
        client.post(f"/habits/{habit['id']}/track",
                    json={"done": True, "log_date": d, "notes": f"gun {i}"},
                    headers=auth_headers)

    r = client.get(f"/habits/{habit['id']}/logs", headers=auth_headers)
    logs = r.json()
    assert len(logs) == 3
    # En yeni gün en başta (desc)
    assert logs[0]["log_date"] == today.isoformat()
    assert logs[0]["notes"] == "gun 0"
    assert logs[-1]["log_date"] == (today - timedelta(days=2)).isoformat()


def test_logs_unknown_habit_404(client, auth_headers):
    r = client.get("/habits/999/logs", headers=auth_headers)
    assert r.status_code == 404


def test_track_is_idempotent_per_day(client, auth_headers):
    """Aynı güne iki track → tek kayıt (upsert), günde 1 kere."""
    habit = _make_habit(client, auth_headers)
    today = date.today().isoformat()
    client.post(f"/habits/{habit['id']}/track",
                json={"done": True, "log_date": today, "notes": "ilk"},
                headers=auth_headers)
    client.post(f"/habits/{habit['id']}/track",
                json={"done": True, "log_date": today, "notes": "guncel"},
                headers=auth_headers)

    logs = client.get(f"/habits/{habit['id']}/logs", headers=auth_headers).json()
    assert len(logs) == 1
    assert logs[0]["notes"] == "guncel"


def test_delete_habit(client, auth_headers):
    habit = _make_habit(client, auth_headers)
    r = client.delete(f"/habits/{habit['id']}", headers=auth_headers)
    assert r.status_code == 204

    listing = client.get("/habits", headers=auth_headers).json()
    assert listing == []


def test_delete_unknown_habit_404(client, auth_headers):
    r = client.delete("/habits/999", headers=auth_headers)
    assert r.status_code == 404
