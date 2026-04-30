from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.database import get_db
from app.middleware.request_context import RequestContextMiddleware
from app.routes.auth import router as auth_router
from app.routes.courses import router as courses_router
from app.routes.documents import router as documents_router
from app.routes.qa import router as qa_router
from app.routes.graph import router as graph_router
from app.routes.lessons import router as lessons_router
from app.routes.assessment import router as assessment_router
from app.routes.jobs import router as jobs_router


configure_logging()

app = FastAPI(
    title="AstraLearn API",
    version=settings.app_version,
    description="Core API for AstraLearn OS.",
)

origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(RequestContextMiddleware)

app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(documents_router)
app.include_router(qa_router)
app.include_router(graph_router)
app.include_router(lessons_router)
app.include_router(assessment_router)
app.include_router(jobs_router)


@app.get("/internal/health")
def healthcheck() -> dict[str, str]:
    """Process liveness (no external dependencies)."""
    return {"status": "ok"}


@app.get("/internal/ready")
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:
    """Kubernetes-style readiness: PostgreSQL must accept a trivial query."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unreachable",
        ) from exc
    return {"status": "ready", "database": "ok"}
