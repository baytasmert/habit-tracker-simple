"""Unit test — sinir (boundary) ve negatif testler (saf Pydantic validation).

Gercek kisitlar (schemas.py):
  username 3-50 · password 6-72 · goal_days_per_week 1-7 · habit name 1-100
"""
import pytest
from pydantic import ValidationError

from src import schemas


# ── SINIR: limitteki degerler KABUL edilmeli ───────────────────────
@pytest.mark.parametrize("length", [3, 50])  # min, max
def test_username_at_boundary_accepted(length):
    u = schemas.UserCreate(username="a" * length, email="a@b.com", password="secret1")
    assert len(u.username) == length


@pytest.mark.parametrize("length", [6, 72])  # min, max
def test_password_at_boundary_accepted(length):
    u = schemas.UserCreate(username="alice", email="a@b.com", password="a" * length)
    assert len(u.password) == length


@pytest.mark.parametrize("goal", [1, 7])  # min, max
def test_goal_at_boundary_accepted(goal):
    h = schemas.HabitCreate(name="Walk", goal_days_per_week=goal)
    assert h.goal_days_per_week == goal


@pytest.mark.parametrize("length", [1, 100])  # min, max
def test_habit_name_at_boundary_accepted(length):
    h = schemas.HabitCreate(name="x" * length)
    assert len(h.name) == length


# ── SINIR: limitin bir disi REDDEDILMELI ───────────────────────────
@pytest.mark.parametrize("length", [2, 51])  # min-1, max+1
def test_username_outside_boundary_rejected(length):
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="a" * length, email="a@b.com", password="secret1")


@pytest.mark.parametrize("length", [5, 73])  # min-1, max+1
def test_password_outside_boundary_rejected(length):
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="alice", email="a@b.com", password="a" * length)


@pytest.mark.parametrize("goal", [0, 8])  # min-1, max+1
def test_goal_outside_boundary_rejected(goal):
    with pytest.raises(ValidationError):
        schemas.HabitCreate(name="Walk", goal_days_per_week=goal)


@pytest.mark.parametrize("length", [0, 101])  # min-1, max+1
def test_habit_name_outside_boundary_rejected(length):
    with pytest.raises(ValidationError):
        schemas.HabitCreate(name="x" * length)


# ── NEGATIF: eksik alan / gecersiz tip / bozuk e-posta ──────────────
def test_usercreate_missing_email_rejected():
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="alice", password="secret1")


def test_usercreate_missing_password_rejected():
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="alice", email="a@b.com")


def test_goal_non_numeric_rejected():
    with pytest.raises(ValidationError):
        schemas.HabitCreate(name="Walk", goal_days_per_week="cok")


@pytest.mark.parametrize("bad_email", ["", "plainaddress", "a@", "@b.com", "a b@c.com"])
def test_invalid_emails_rejected(bad_email):
    with pytest.raises(ValidationError):
        schemas.UserCreate(username="alice", email=bad_email, password="secret1")
