from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from starlette.testclient import TestClient

_API_ROOT = Path(__file__).resolve().parents[2]

os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-at-least-32-characters-!!")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@127.0.0.1:5432/astralearn_test"

from app.db.database import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402


def _run_migrations() -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=_API_ROOT,
        check=True,
        env=os.environ.copy(),
    )


def _truncate_app_tables(engine) -> None:
    names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    if not names:
        return
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))


@pytest.fixture(scope="session")
def engine():
    url = os.environ["DATABASE_URL"]
    eng = create_engine(url, poolclass=NullPool, pool_pre_ping=True)
    with eng.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    _run_migrations()
    yield eng
    eng.dispose()


@pytest.fixture
def client(engine):
    bind = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        session = bind()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    _truncate_app_tables(engine)
