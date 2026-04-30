from fastapi import Header, HTTPException, status

from app.core.config import settings


def internal_api_guard(x_internal_key: str | None = Header(default=None, alias="X-Internal-Key")) -> None:
    expected = settings.internal_api_key
    if not expected or not str(expected).strip():
        return
    if (x_internal_key or "").strip() != str(expected).strip():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing or invalid X-Internal-Key")
