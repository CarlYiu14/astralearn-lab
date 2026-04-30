from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.core.security import hash_password  # noqa: E402
from app.models import Course, CourseMember, User  # noqa: E402


def _get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "postgresql+psycopg://astralearn:astralearn@localhost:5432/astralearn")


def main() -> None:
    email = os.environ.get("SEED_USER_EMAIL", "dev@local.test").lower()
    name = os.environ.get("SEED_USER_NAME", "Local Dev")
    course_title = os.environ.get("SEED_COURSE_TITLE", "CS-LOCAL: Prototype Course")
    seed_password = os.environ.get("SEED_USER_PASSWORD", "devpassword123")

    engine = create_engine(_get_database_url(), pool_pre_ping=True)

    with Session(engine) as session:
        user = session.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if user is None:
            user = User(
                id=uuid.uuid4(),
                email=email,
                name=name,
                role="instructor",
                password_hash=hash_password(seed_password),
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        elif user.password_hash is None:
            user.password_hash = hash_password(seed_password)
            session.add(user)
            session.commit()
            session.refresh(user)

        course = Course(
            id=uuid.uuid4(),
            owner_id=user.id,
            title=course_title,
            code="LOCAL-101",
            term="2026S",
            description="Seeded for local dev workflows.",
        )
        session.add(course)
        session.flush()

        session.add(CourseMember(course_id=course.id, user_id=user.id, role="owner"))
        session.commit()

        user_id = user.id
        course_id = course.id

    print("Seeded user + course")
    print(f"USER_ID={user_id}")
    print(f"COURSE_ID={course_id}")
    print(f"LOGIN_EMAIL={email}")
    print("(password from SEED_USER_PASSWORD or default devpassword123)")
    print("Golden QA env (optional): GOLDEN_EMAIL=<same as LOGIN_EMAIL> GOLDEN_PASSWORD=<password> GOLDEN_COURSE_ID=<COURSE_ID>")


if __name__ == "__main__":
    main()
