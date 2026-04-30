from __future__ import annotations

import uuid
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLogEntry


def _client_ip(request: Request | None) -> str | None:
    if request is None or request.client is None:
        return None
    return request.client.host


def _user_agent(request: Request | None) -> str | None:
    if request is None:
        return None
    return request.headers.get("user-agent")


def write_audit(
    db: Session,
    *,
    action: str,
    actor_user_id: uuid.UUID | None = None,
    course_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: uuid.UUID | None = None,
    detail: dict[str, Any] | None = None,
    request: Request | None = None,
) -> None:
    db.add(
        AuditLogEntry(
            id=uuid.uuid4(),
            actor_user_id=actor_user_id,
            action=action,
            course_id=course_id,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
    )
