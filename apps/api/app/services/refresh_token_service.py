from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.models import RefreshToken, User


def _hash_plain(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def _client_ip(request: Request | None) -> str | None:
    if request is None or request.client is None:
        return None
    return request.client.host


def _user_agent(request: Request | None) -> str | None:
    if request is None:
        return None
    return request.headers.get("user-agent")


def issue_refresh_token(db: Session, *, user_id: uuid.UUID, request: Request | None) -> str:
    plain = secrets.token_urlsafe(48)
    exp = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    row = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=_hash_plain(plain),
        expires_at=exp,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )
    db.add(row)
    return plain


def rotate_refresh_token(db: Session, *, plain: str, request: Request | None) -> tuple[User, str, str]:
    """Validate opaque refresh, revoke row, issue new refresh + access (caller commits)."""
    th = _hash_plain(plain)
    row = db.execute(select(RefreshToken).where(RefreshToken.token_hash == th)).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if row is None or row.revoked_at is not None or row.expires_at <= now:
        raise ValueError("Invalid or expired refresh token")

    user = db.get(User, row.user_id)
    if user is None:
        raise ValueError("User no longer exists")

    new_plain = secrets.token_urlsafe(48)
    new_exp = now + timedelta(days=settings.refresh_token_expire_days)
    new_row = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=_hash_plain(new_plain),
        expires_at=new_exp,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )
    db.add(new_row)
    db.flush()
    row.revoked_at = now
    row.replaced_by_id = new_row.id
    db.add(row)

    access = create_access_token(user_id=user.id)
    return user, access, new_plain


def revoke_refresh_by_plain(db: Session, *, plain: str) -> uuid.UUID | None:
    """Revoke matching refresh row if active. Returns owning user id when a row was revoked."""
    th = _hash_plain(plain)
    row = db.execute(select(RefreshToken).where(RefreshToken.token_hash == th)).scalar_one_or_none()
    if row is None or row.revoked_at is not None:
        return None
    uid = row.user_id
    row.revoked_at = datetime.now(timezone.utc)
    db.add(row)
    return uid


def revoke_all_for_user(db: Session, *, user_id: uuid.UUID) -> None:
    now = datetime.now(timezone.utc)
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )
