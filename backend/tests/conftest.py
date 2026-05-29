"""Pytest fixtures — SQLite in-memory DB for unit/integration testleri."""
import os

# Set test env BEFORE src imports
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from src.database import Base, get_db  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_engine):
    SessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def _override():
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    client.post("/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "secret123",
    })
    r = client.post("/login", json={
        "email": "alice@example.com",
        "password": "secret123",
    })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
