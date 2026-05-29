"""
Habit Tracker API — saf JSON REST API.

6 ana endpoint (rubric: 4-6) + auth + health + metrics + S3 yardımcıları.
Frontend ayrı bir servistir (NGINX → frontend/); bu API HTML döndürmez.
"""
from datetime import date, timedelta
import time

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from . import models, schemas, auth, s3_client
from .database import engine, get_db
from .tracing import setup_tracing


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Habit Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry → Jaeger (sadece ENABLE_TRACING=true ise aktif)
setup_tracing(app, engine)

# ── Prometheus ───────────────────────────────────────────────────
REQ_TOTAL = Counter("http_requests_total", "Total HTTP requests",
                    ["method", "endpoint", "status"])
REQ_DURATION = Histogram("http_request_duration_seconds", "Request duration",
                         ["method", "endpoint"])


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    path = request.url.path
    REQ_TOTAL.labels(request.method, path, response.status_code).inc()
    REQ_DURATION.labels(request.method, path).observe(elapsed)
    return response


# ── Health / Metrics ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ── Auth helpers ────────────────────────────────────────────────
def get_current_user(
    email: str = Depends(auth.get_current_user_email),
    db: Session = Depends(get_db),
) -> models.User:
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ── Endpoint 1: POST /register ──────────────────────────────────
@app.post("/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        username=payload.username,
        email=payload.email,
        hashed_password=auth.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Endpoint 2: POST /login ─────────────────────────────────────
@app.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth.create_access_token(subject=user.email)
    return schemas.Token(access_token=token)


# ── Endpoint 3: POST /habits ────────────────────────────────────
@app.post("/habits", response_model=schemas.HabitOut, status_code=201)
def create_habit(
    payload: schemas.HabitCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = models.Habit(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        category=payload.category,
        goal_days_per_week=payload.goal_days_per_week,
        created_at=date.today(),
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


# ── Endpoint 4: GET /habits ─────────────────────────────────────
@app.get("/habits", response_model=list[schemas.HabitOut])
def list_habits(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(models.Habit).filter(models.Habit.user_id == user.id).all()


# ── Endpoint 5: POST /habits/{id}/track ─────────────────────────
@app.post("/habits/{habit_id}/track", response_model=schemas.HabitLogOut, status_code=201)
def track_habit(
    habit_id: int,
    payload: schemas.HabitLogCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id, models.Habit.user_id == user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    log_date = payload.log_date or date.today()
    existing = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.log_date == log_date,
    ).first()
    if existing:
        existing.done = payload.done
        existing.notes = payload.notes
        db.commit()
        db.refresh(existing)
        return existing

    log = models.HabitLog(
        habit_id=habit_id,
        log_date=log_date,
        done=payload.done,
        notes=payload.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ── Endpoint 6: GET /habits/{id}/streak ─────────────────────────
@app.get("/habits/{habit_id}/streak", response_model=schemas.StreakOut)
def get_streak(
    habit_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id, models.Habit.user_id == user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.done == True,  # noqa: E712
    ).order_by(models.HabitLog.log_date.desc()).all()

    streak = 0
    today = date.today()
    for i, log in enumerate(logs):
        if log.log_date == today - timedelta(days=i):
            streak += 1
        else:
            break

    return schemas.StreakOut(
        habit_id=habit_id,
        current_streak=streak,
        total_completed=len(logs),
    )


# ── S3 (LocalStack) — habit progress photo ──────────────────────
def _get_habit_for_user(db: Session, habit_id: int, user_id: int) -> models.Habit:
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id, models.Habit.user_id == user_id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.post("/habits/{habit_id}/photo", status_code=201)
def upload_habit_photo(
    habit_id: int,
    file: UploadFile = File(...),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_habit_for_user(db, habit_id, user.id)
    body = file.file.read()
    key = f"habits/{habit_id}/{file.filename}"
    url = s3_client.upload_photo(key, body, file.content_type or "image/jpeg")
    return {"key": key, "url": url, "size_bytes": len(body)}


@app.get("/habits/{habit_id}/photos")
def list_habit_photos(
    habit_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_habit_for_user(db, habit_id, user.id)
    keys = s3_client.list_photos(prefix=f"habits/{habit_id}/")
    return {"habit_id": habit_id, "count": len(keys), "keys": keys}
