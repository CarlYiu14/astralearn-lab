import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps.auth import get_current_user
from app.deps.course_access import require_course_faculty, require_course_member
from app.models import CourseDocument, User
from app.schemas.document import (
    DocumentProcessRequest,
    DocumentProcessResponse,
    DocumentUploadResponse,
)
from app.services import document_ingest
from app.services.audit_service import write_audit

router = APIRouter(tags=["documents"])


@router.post(
    "/courses/{course_id}/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    course_id: uuid.UUID,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> CourseDocument:
    require_course_faculty(db, course_id=course_id, user=current)

    document_id = uuid.uuid4()
    original_name = file.filename or "upload.txt"
    storage_path = document_ingest.build_storage_path(
        course_id=course_id, document_id=document_id, original_name=original_name
    )
    document_ingest.ensure_parent_exists(storage_path)

    try:
        content = await file.read()
        storage_path.write_bytes(content)
    except OSError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    document = CourseDocument(
        id=document_id,
        course_id=course_id,
        source_type="upload",
        title=original_name,
        file_path=str(storage_path),
        status="uploaded",
    )
    db.add(document)
    write_audit(
        db,
        action="document.upload",
        actor_user_id=current.id,
        course_id=course_id,
        resource_type="course_document",
        resource_id=document.id,
        detail={"title": original_name},
        request=request,
    )
    db.commit()
    db.refresh(document)
    return document


@router.post(
    "/courses/{course_id}/documents/{document_id}/process", response_model=DocumentProcessResponse
)
def process_document(
    course_id: uuid.UUID,
    document_id: uuid.UUID,
    payload: DocumentProcessRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> DocumentProcessResponse:
    _ = payload  # future: async queue mode

    require_course_faculty(db, course_id=course_id, user=current)

    document = db.get(CourseDocument, document_id)
    if document is None or document.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if not Path(document.file_path).exists():
        document.status = "failed"
        db.add(document)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stored file is missing on disk")

    try:
        result = document_ingest.process_document_to_chunks(db, document)
    except ValueError as exc:
        document.status = "failed"
        db.add(document)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except OSError as exc:
        document.status = "failed"
        db.add(document)
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return DocumentProcessResponse(
        id=document.id,
        course_id=document.course_id,
        status=document.status,
        chunk_count=result.chunk_count,
        char_count=result.char_count,
    )


@router.get("/courses/{course_id}/documents", response_model=list[DocumentUploadResponse])
def list_documents(
    course_id: uuid.UUID, db: Session = Depends(get_db), current: User = Depends(get_current_user)
) -> list[CourseDocument]:
    require_course_member(db, course_id=course_id, user=current)

    rows = db.execute(
        select(CourseDocument).where(CourseDocument.course_id == course_id).order_by(CourseDocument.created_at.desc())
    ).scalars()
    return list(rows)
