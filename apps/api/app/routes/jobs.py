import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.internal_auth import internal_api_guard
from app.db.database import get_db
from app.models import AsyncJob
from app.schemas.job import JobStatusResponse

router = APIRouter(prefix="/internal", tags=["internal"], dependencies=[Depends(internal_api_guard)])


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)) -> AsyncJob:
    job = db.get(AsyncJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
