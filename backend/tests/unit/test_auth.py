"""Unit testler — sadece auth modülü, DB yok."""
from datetime import timedelta  # noqa: F401

import pytest
from fastapi import HTTPException
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


def test_hash_is_salted_unique():
    a = auth.hash_password("samepass")
    b = auth.hash_password("samepass")
    assert a != b  # rastgele salt -> ayni sifre farkli hash
    assert auth.verify_password("samepass", a)
    assert auth.verify_password("samepass", b)


def test_get_current_user_email_valid_token():
    token = auth.create_access_token(subject="me@x.com")
    assert auth.get_current_user_email(token) == "me@x.com"


def test_get_current_user_email_rejects_garbage():
    with pytest.raises(HTTPException) as e:
        auth.get_current_user_email("not-a-jwt")
    assert e.value.status_code == 401


def test_get_current_user_email_rejects_wrong_secret():
    bad = jwt.encode({"sub": "x@y.com"}, "wrong-secret", algorithm=auth.ALGORITHM)
    with pytest.raises(HTTPException):
        auth.get_current_user_email(bad)


def test_get_current_user_email_rejects_none():
    with pytest.raises(HTTPException) as e:
        auth.get_current_user_email(None)
    assert e.value.status_code == 401


def test_get_current_user_email_rejects_missing_sub():
    token = jwt.encode({"foo": "bar"}, settings.secret_key, algorithm=auth.ALGORITHM)
    with pytest.raises(HTTPException):
        auth.get_current_user_email(token)
