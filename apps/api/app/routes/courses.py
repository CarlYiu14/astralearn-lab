import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.deps.auth import get_current_user
from app.deps.course_access import get_course_or_404, require_course_faculty, require_course_member
from app.models import AuditLogEntry, Course, CourseMember, User
from app.schemas.audit import AuditLogEntryOut
from app.schemas.course import CourseCreateRequest, CourseResponse
from app.schemas.members import CourseMemberInviteRequest, CourseMemberOut
from app.services.audit_service import write_audit

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseResponse])
def list_my_courses(db: Session = Depends(get_db), current: User = Depends(get_current_user)) -> list[Course]:
    stmt = (
        select(Course)
        .join(CourseMember, CourseMember.course_id == Course.id)
        .where(CourseMember.user_id == current.id)
        .order_by(Course.created_at.desc())
    )
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Course:
    course = Course(
        owner_id=current.id,
        title=payload.title,
        code=payload.code,
        term=payload.term,
        description=payload.description,
    )
    db.add(course)
    db.flush()

    db.add(CourseMember(course_id=course.id, user_id=current.id, role="owner"))
    write_audit(
        db,
        action="course.create",
        actor_user_id=current.id,
        course_id=course.id,
        resource_type="course",
        resource_id=course.id,
        detail={"title": course.title},
        request=request,
    )
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}/members", response_model=list[CourseMemberOut])
def list_course_members(
    course_id: uuid.UUID, db: Session = Depends(get_db), current: User = Depends(get_current_user)
) -> list[CourseMemberOut]:
    require_course_faculty(db, course_id=course_id, user=current)

    rows = db.execute(
        select(CourseMember, User)
        .join(User, User.id == CourseMember.user_id)
        .where(CourseMember.course_id == course_id)
        .order_by(User.email)
    ).all()
    return [
        CourseMemberOut(user_id=u.id, email=u.email, name=u.name, role=m.role) for m, u in rows
    ]


@router.get("/{course_id}/audit-log", response_model=list[AuditLogEntryOut])
def list_course_audit_log(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    limit: int = Query(default=80, ge=1, le=500),
) -> list[AuditLogEntry]:
    require_course_faculty(db, course_id=course_id, user=current)
    rows = db.execute(
        select(AuditLogEntry)
        .where(AuditLogEntry.course_id == course_id)
        .order_by(desc(AuditLogEntry.created_at))
        .limit(limit)
    ).scalars()
    return list(rows)


@router.post(
    "/{course_id}/members",
    response_model=CourseMemberOut,
    status_code=status.HTTP_201_CREATED,
)
def invite_course_member(
    course_id: uuid.UUID,
    payload: CourseMemberInviteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> CourseMemberOut:
    actor = require_course_faculty(db, course_id=course_id, user=current)

    if payload.role not in {"student", "instructor"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role must be student or instructor")

    if payload.role == "instructor" and actor.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only course owners can invite instructors",
        )

    invitee = db.execute(select(User).where(User.email == str(payload.email).lower())).scalar_one_or_none()
    if invitee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user with that email; they must register first",
        )

    member = CourseMember(course_id=course_id, user_id=invitee.id, role=payload.role)
    db.add(member)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this course",
        ) from None

    db.refresh(member)
    write_audit(
        db,
        action="course.member_invite",
        actor_user_id=current.id,
        course_id=course_id,
        resource_type="user",
        resource_id=invitee.id,
        detail={"email": invitee.email, "role": member.role},
        request=request,
    )
    db.commit()
    return CourseMemberOut(user_id=invitee.id, email=invitee.email, name=invitee.name, role=member.role)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db), current: User = Depends(get_current_user)) -> Course:
    require_course_member(db, course_id=course_id, user=current)
    return get_course_or_404(db, course_id)
