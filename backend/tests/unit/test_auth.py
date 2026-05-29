"""Unit testler — sadece auth modülü, DB yok."""
from datetime import timedelta

from jose import jwt

from src import auth
from src.config import settings


def test_hash_password_returns_different_string():
    h = auth.hash_password("hello123")
    assert h != "hello123"
    assert len(h) > 20


def test_verify_password_success():
    h = auth.hash_password("secret")
    assert auth.verify_password("secret", h) is True


def test_verify_password_failure():
    h = auth.hash_password("secret")
    assert auth.verify_password("wrong", h) is False


def test_create_access_token_contains_subject():
    token = auth.create_access_token(subject="user@example.com")
    decoded = jwt.decode(token, settings.secret_key, algorithms=[auth.ALGORITHM])
    assert decoded["sub"] == "user@example.com"
    assert "exp" in decoded


def test_create_access_token_respects_expiry():
    token = auth.create_access_token(subject="x@y.com", expires_minutes=1)
    decoded = jwt.decode(token, settings.secret_key, algorithms=[auth.ALGORITHM])
    assert decoded["exp"] is not None
