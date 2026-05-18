from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.responses import success
from app.db.session import get_db
from app.models.user import User
from app.schemas.assignment_schema import AssignmentCreate, AssignmentUpdate
from app.services import assignment_service

router = APIRouter(prefix="/assignments", tags=["作业"])


@router.get("")
def list_assignments(
    course_id: int | None = Query(default=None),
    only_mine: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = assignment_service.list_assignments(db, user, course_id=course_id, only_mine=only_mine)
    return success([item.model_dump() for item in data])


@router.post("")
def create_assignment(payload: AssignmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(assignment_service.create_assignment(db, user, payload).model_dump())


@router.post("/with-files")
def create_assignment_with_files(
    course_id: int = Form(...),
    title: str = Form(...),
    deadline: datetime = Form(...),
    description: str | None = Form(default=None),
    files: list[UploadFile] | None = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    payload = AssignmentCreate(course_id=course_id, title=title, description=description, deadline=deadline)
    return success(assignment_service.create_assignment_with_files(db, user, payload, files).model_dump())


@router.get("/{assignment_id}")
def get_assignment(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(assignment_service.get_assignment(db, user, assignment_id).model_dump())


@router.put("/{assignment_id}")
def update_assignment(
    assignment_id: int,
    payload: AssignmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(assignment_service.update_assignment(db, user, assignment_id, payload).model_dump())


@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    assignment_service.delete_assignment(db, user, assignment_id)
    return success(None, message="删除成功")
