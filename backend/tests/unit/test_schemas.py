"""Unit test — Pydantic sema dogrulama (DB/HTTP yok, saf validation)."""
import pytest
from pydantic import ValidationError

from src import schemas


def test_usercreate_valid():
    u = schemas.UserCreate(username="alice", email="a@b.com", password="secret1")
    assert u.email == "a@b.com"
    assert u.username == "alice"


def test_usercreate_short_password_rejected():
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="alice", email="a@b.com", password="123")


def test_usercreate_bad_email_rejected():
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="alice", email="not-an-email", password="secret1")


def test_usercreate_short_username_rejected():
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="ab", email="a@b.com", password="secret1")


def test_habitcreate_valid_defaults():
    h = schemas.HabitCreate(name="Sabah yuruyusu")
    assert h.goal_days_per_week == 7  # varsayilan
    assert h.description is None


def test_habitcreate_goal_above_range_rejected():
    with pytest.raises(ValidationError):
        schemas.HabitCreate(name="Walk", goal_days_per_week=8)


def test_habitcreate_goal_below_range_rejected():
    with pytest.raises(ValidationError):
        schemas.HabitCreate(name="Walk", goal_days_per_week=0)


def test_habitcreate_empty_name_rejected():
    with pytest.raises(ValidationError):
        schemas.HabitCreate(name="")


def test_habitlogcreate_defaults():
    log = schemas.HabitLogCreate()
    assert log.done is True
    assert log.mood is None
    assert log.log_date is None


def test_token_default_type_bearer():
    t = schemas.Token(access_token="abc.def.ghi")
    assert t.token_type == "bearer"
