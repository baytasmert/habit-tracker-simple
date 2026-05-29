"""
Testcontainers ile gerçek PostgreSQL container testleri.

Linux/CI'da Docker daemon gerektirir. Windows'ta psycopg2 hostname encoding
sorunu nedeniyle otomatik skip edilir.
"""
import os
import sys

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Testcontainers psycopg2 Windows encoding issue — Linux/CI only",
)

from testcontainers.postgres import PostgresContainer  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.database import Base, get_db  # noqa: E402
from src.main import app  # noqa: E402


@pytest.fixture(scope="module")
def pg_url():
    with PostgresContainer("postgres:16") as pg:
        # testcontainers v4 API: username/password/dbname (alt çizgili attribute kaldırıldı).
        # URL'i manuel kuruyoruz — pg.get_connection_url() Windows'ta Türkçe locale
        # nedeniyle hostname'i UTF-8'e çeviremiyor.
        port = pg.get_exposed_port(5432)
        user = pg.username
        pwd = pg.password
        db = pg.dbname
        yield f"postgresql://{user}:{pwd}@127.0.0.1:{port}/{db}"


@pytest.fixture(scope="module")
def tc_engine(pg_url):
    engine = create_engine(pg_url)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="module")
def tc_client(tc_engine):
    SessionLocal = sessionmaker(bind=tc_engine, autoflush=False, autocommit=False)

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


def test_postgres_schema_created(tc_engine):
    """Şema oluşturuldu mu — gerçek Postgres ile doğrula."""
    with tc_engine.connect() as conn:
        result = conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        ))
        tables = {row[0] for row in result}
    assert {"users", "habits", "habit_logs"}.issubset(tables)


def test_register_and_login_with_real_postgres(tc_client):
    """Auth flow gerçek Postgres üzerinde çalışıyor mu?"""
    r = tc_client.post("/register", json={
        "username": "tc_user",
        "email": "tc@example.com",
        "password": "secret123",
    })
    assert r.status_code == 201

    r = tc_client.post("/login", json={
        "email": "tc@example.com",
        "password": "secret123",
    })
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_habit_persists_across_sessions(tc_client, tc_engine):
    """Bir request'te oluşturulan habit, sonraki request'te listede görünüyor mu?"""
    tc_client.post("/register", json={
        "username": "persist_user",
        "email": "p@example.com",
        "password": "abc123",
    })
    login = tc_client.post("/login", json={"email": "p@example.com", "password": "abc123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    tc_client.post("/habits", json={"name": "Persistent habit"}, headers=headers)
    r = tc_client.get("/habits", headers=headers)
    assert any(h["name"] == "Persistent habit" for h in r.json())
