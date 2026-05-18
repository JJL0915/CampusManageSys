from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.responses import success
from app.db.session import get_db
from app.models.user import User
from app.schemas.user_schema import StudentCreate, StudentUpdate, TeacherCreate, TeacherUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/students")
def list_students(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = user_service.list_students(db, user)
    return success([item.model_dump() for item in data])


@router.post("/students")
def create_student(payload: StudentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(user_service.create_student(db, user, payload).model_dump())


@router.put("/students/{student_id}")
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(user_service.update_student(db, user, student_id, payload).model_dump())


@router.get("/teachers")
def list_teachers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = user_service.list_teachers(db, user)
    return success([item.model_dump() for item in data])


@router.post("/teachers")
def create_teacher(payload: TeacherCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(user_service.create_teacher(db, user, payload).model_dump())


@router.put("/teachers/{teacher_id}")
def update_teacher(
    teacher_id: int,
    payload: TeacherUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(user_service.update_teacher(db, user, teacher_id, payload).model_dump())


@router.post("/{user_id}/disable")
def disable_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user_service.disable_user(db, user, user_id)
    return success(None, message="账号已停用")

