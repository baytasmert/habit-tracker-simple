"""S3 fotoğraf endpoint'leri — s3_client mocklanır."""
import io
from unittest.mock import patch


def test_upload_photo_unknown_habit_404(client, auth_headers):
    files = {"file": ("a.jpg", io.BytesIO(b"data"), "image/jpeg")}
    r = client.post("/habits/999/photo", files=files, headers=auth_headers)
    assert r.status_code == 404


@patch("src.main.s3_client.upload_photo", return_value="s3://habit-photos/key")
def test_upload_photo_success(mock_upload, client, auth_headers):
    habit = client.post("/habits", json={"name": "Run"}, headers=auth_headers).json()
    files = {"file": ("run.jpg", io.BytesIO(b"xxxx"), "image/jpeg")}
    r = client.post(f"/habits/{habit['id']}/photo", files=files, headers=auth_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["size_bytes"] == 4
    assert body["url"].startswith("s3://")
    mock_upload.assert_called_once()


@patch("src.main.s3_client.list_photos", return_value=["habits/1/a.jpg", "habits/1/b.png"])
def test_list_photos_success(mock_list, client, auth_headers):
    habit = client.post("/habits", json={"name": "Read"}, headers=auth_headers).json()
    r = client.get(f"/habits/{habit['id']}/photos", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 2
    assert body["keys"] == ["habits/1/a.jpg", "habits/1/b.png"]


def test_list_photos_unknown_habit_404(client, auth_headers):
    r = client.get("/habits/999/photos", headers=auth_headers)
    assert r.status_code == 404


@patch("src.main.s3_client.get_photo", return_value=(b"\xff\xd8jpegdata", "image/jpeg"))
def test_get_photo_file_success(mock_get, client, auth_headers):
    habit = client.post("/habits", json={"name": "Yoga"}, headers=auth_headers).json()
    key = f"habits/{habit['id']}/2026-05-29/a.jpg"
    r = client.get(f"/habits/{habit['id']}/photo-file?key={key}", headers=auth_headers)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/jpeg"
    assert r.content == b"\xff\xd8jpegdata"


def test_get_photo_file_foreign_key_403(client, auth_headers):
    """Başka habit'in key'i istenirse 403."""
    habit = client.post("/habits", json={"name": "Yoga"}, headers=auth_headers).json()
    r = client.get(f"/habits/{habit['id']}/photo-file?key=habits/999/x.jpg",
                   headers=auth_headers)
    assert r.status_code == 403
