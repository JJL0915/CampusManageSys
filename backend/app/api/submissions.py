import json

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.responses import success
from app.db.session import get_db
from app.models.user import User
from app.schemas.submission_schema import GradeRequest, SubmissionCreate, SubmissionUpdate
from app.services import submission_service

router = APIRouter(prefix="/submissions", tags=["提交与批改"])


def _parse_keep_attachment_ids(raw: str | None) -> set[int] | None:
    if raw is None:
        return None
    if not raw.strip():
        return set()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = [item for item in raw.split(",") if item.strip()]
    return {int(item) for item in value}


@router.get("")
def list_submissions(
    assignment_id: int | None = Query(default=None),
    course_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = submission_service.list_submissions(
        db,
        user,
        assignment_id=assignment_id,
        course_id=course_id,
        status=status,
    )
    return success([item.model_dump() for item in data])


@router.post("")
def submit_assignment(payload: SubmissionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(submission_service.submit_assignment(db, user, payload).model_dump())


@router.post("/with-files")
def submit_assignment_with_files(
    assignment_id: int = Form(...),
    content: str = Form(default=""),
    files: list[UploadFile] | None = File(default=None),
    keep_attachment_ids: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(
        submission_service.submit_assignment_with_files(
            db,
            user,
            assignment_id,
            content,
            files,
            _parse_keep_attachment_ids(keep_attachment_ids),
        ).model_dump()
    )


@router.put("/{submission_id}")
def update_submission(
    submission_id: int,
    payload: SubmissionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(submission_service.update_submission(db, user, submission_id, payload).model_dump())


@router.put("/{submission_id}/with-files")
def update_submission_with_files(
    submission_id: int,
    content: str = Form(default=""),
    files: list[UploadFile] | None = File(default=None),
    keep_attachment_ids: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(
        submission_service.update_submission_with_files(
            db,
            user,
            submission_id,
            content,
            files,
            _parse_keep_attachment_ids(keep_attachment_ids),
        ).model_dump()
    )


@router.post("/{submission_id}/grade")
def grade_submission(
    submission_id: int,
    payload: GradeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(submission_service.grade_submission(db, user, submission_id, payload).model_dump())
