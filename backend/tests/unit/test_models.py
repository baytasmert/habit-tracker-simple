"""Unit test — model + Factory Boy sanity."""
from tests.factories import UserFactory, HabitFactory, HabitLogFactory


def test_user_factory_creates_unique_users():
    u1 = UserFactory.build()
    u2 = UserFactory.build()
    assert u1.username != u2.username
    assert u1.email != u2.email
    assert u1.hashed_password.startswith("$2b$")


def test_habit_factory_has_valid_goal():
    h = HabitFactory.build()
    assert 1 <= h.goal_days_per_week <= 7
    assert h.name


def test_habit_log_factory_defaults_to_done():
    log = HabitLogFactory.build()
    assert log.done is True
