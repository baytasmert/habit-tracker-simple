from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ── User ──────────────────────────────────────────
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Habit ─────────────────────────────────────────
class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    goal_days_per_week: int = Field(default=7, ge=1, le=7)


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    goal_days_per_week: int
    created_at: date


# ── HabitLog ──────────────────────────────────────
class HabitLogCreate(BaseModel):
    done: bool = True
    log_date: Optional[date] = None
    notes: Optional[str] = None
    mood: Optional[str] = None


class HabitLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    habit_id: int
    log_date: date
    done: bool
    notes: Optional[str]
    mood: Optional[str] = None
    photo_key: Optional[str] = None


class StreakOut(BaseModel):
    habit_id: int
    current_streak: int
    total_completed: int
