"""Factory Boy + Faker — gerçekçi test verisi üretimi."""
import factory
from factory import Faker
from datetime import date

from src.models import User, Habit, HabitLog
from src.auth import hash_password


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = Faker("user_name")
    email = Faker("email")
    hashed_password = factory.LazyFunction(lambda: hash_password("default_password"))


class HabitFactory(factory.Factory):
    class Meta:
        model = Habit

    name = Faker("sentence", nb_words=3)
    description = Faker("sentence")
    category = Faker("random_element", elements=["health", "fitness", "study", "mindfulness"])
    goal_days_per_week = Faker("random_int", min=1, max=7)
    created_at = factory.LazyFunction(date.today)


class HabitLogFactory(factory.Factory):
    class Meta:
        model = HabitLog

    log_date = factory.LazyFunction(date.today)
    done = True
    notes = Faker("sentence")
