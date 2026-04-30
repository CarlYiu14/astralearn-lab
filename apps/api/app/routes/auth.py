from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.deps.auth import get_current_user, get_current_user_optional
from app.models import AuditLogEntry, User
from app.schemas.audit import AuditLogEntryOut
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse, UserPublic
from app.services.audit_service import write_audit
from app.services.refresh_token_service import (
    issue_refresh_token,
    revoke_all_for_user,
    revoke_refresh_by_plain,
    rotate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(access: str, refresh: str) -> TokenResponse:
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        refresh_expires_in=settings.refresh_token_expire_days * 86400,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.execute(select(User).where(User.email == str(payload.email).lower())).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=str(payload.email).lower(),
        name=payload.name,
        password_hash=hash_password(payload.password),
        role="student",
    )
    db.add(user)
    db.flush()
    refresh_plain = issue_refresh_token(db, user_id=user.id, request=request)
    write_audit(
        db,
        action="auth.register",
        actor_user_id=user.id,
        detail={"email": user.email},
        request=request,
    )
    db.commit()
    db.refresh(user)

    access = create_access_token(user_id=user.id)
    return _token_response(access, refresh_plain)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.execute(select(User).where(User.email == str(payload.email).lower())).scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        write_audit(db, action="auth.login.failure", detail={"reason": "invalid_credentials"}, request=request)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    refresh_plain = issue_refresh_token(db, user_id=user.id, request=request)
    write_audit(db, action="auth.login.success", actor_user_id=user.id, request=request)
    db.commit()

    access = create_access_token(user_id=user.id)
    return _token_response(access, refresh_plain)


@router.post("/refresh", response_model=TokenResponse)
def exchange_refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        user, access, new_refresh = rotate_refresh_token(db, plain=payload.refresh_token, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token") from exc

    write_audit(db, action="auth.refresh", actor_user_id=user.id, request=request)
    db.commit()
    return _token_response(access, new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current: User | None = Depends(get_current_user_optional),
    payload: LogoutRequest = Body(default_factory=LogoutRequest),
) -> None:
    if payload.revoke_all_sessions:
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Valid access token required to revoke all sessions",
            )
        revoke_all_for_user(db, user_id=current.id)
        write_audit(db, action="auth.logout_all", actor_user_id=current.id, request=request)
        db.commit()
        return

    if payload.refresh_token:
        owner_id = revoke_refresh_by_plain(db, plain=payload.refresh_token)
        write_audit(db, action="auth.logout", actor_user_id=owner_id or (current.id if current else None), request=request)
        db.commit()
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provide refresh_token or set revoke_all_sessions with Authorization",
    )


@router.get("/me", response_model=UserPublic)
def me(current: User = Depends(get_current_user)) -> User:
    return current


@router.get("/audit/me", response_model=list[AuditLogEntryOut])
def my_audit_log(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AuditLogEntry]:
    rows = db.execute(
        select(AuditLogEntry)
        .where(AuditLogEntry.actor_user_id == current.id)
        .order_by(desc(AuditLogEntry.created_at))
        .limit(limit)
    ).scalars()
    return list(rows)
