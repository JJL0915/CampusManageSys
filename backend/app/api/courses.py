from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.responses import success
from app.db.session import get_db
from app.models.user import User
from app.schemas.course_schema import CourseCreate, CourseUpdate, EnrollmentSettingUpdate
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["课程"])


@router.get("")
def list_courses(
    keyword: str | None = Query(default=None),
    only_mine: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = course_service.list_courses(db, user, keyword=keyword, only_mine=only_mine)
    return success([item.model_dump() for item in data])


@router.post("")
def create_course(payload: CourseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(course_service.create_course(db, user, payload).model_dump())


@router.get("/schedule/weekly")
def weekly_schedule(
    week: int | None = Query(default=None),
    term: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = course_service.get_weekly_schedule(db, user, week=week, term=term)
    return success([item.model_dump() for item in data])


@router.get("/enrollment/settings")
def get_enrollment_setting(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(course_service.get_enrollment_setting(db, user).model_dump())


@router.put("/enrollment/settings")
def update_enrollment_setting(
    payload: EnrollmentSettingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(course_service.update_enrollment_setting(db, user, payload).model_dump())


@router.put("/{course_id}")
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(course_service.update_course(db, user, course_id, payload).model_dump())


@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course_service.delete_course(db, user, course_id)
    return success(None, message="删除成功")


@router.post("/{course_id}/enroll")
def enroll_course(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success(course_service.enroll_course(db, user, course_id).model_dump())


@router.delete("/{course_id}/enroll")
def cancel_enrollment(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course_service.cancel_enrollment(db, user, course_id)
    return success(None, message="退课成功")


@router.delete("/{course_id}/students/{student_id}/enroll")
def admin_remove_enrollment(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course_service.admin_remove_enrollment(db, user, course_id, student_id)
    return success(None, message="退课成功")


@router.get("/{course_id}/students")
def list_course_students(course_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = course_service.list_course_students(db, user, course_id)
    return success([item.model_dump() for item in data])
