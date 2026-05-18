from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFound, PermissionDenied
from app.core.security import hash_password
from app.models.user import Student, Teacher, User
from app.repositories import log_repository, user_repository
from app.schemas.user_schema import (
    StudentAdminOut,
    StudentCreate,
    StudentUpdate,
    TeacherAdminOut,
    TeacherCreate,
    TeacherUpdate,
)


def _ensure_admin(user: User) -> None:
    if user.role != "admin":
        raise PermissionDenied()


def _student_out(student: Student) -> StudentAdminOut:
    return StudentAdminOut(
        id=student.id,
        user_id=student.user_id,
        username=student.user.username,
        real_name=student.user.real_name,
        student_no=student.student_no,
        major=student.major,
        class_name=student.class_name,
        is_active=student.user.is_active,
    )


def _teacher_out(teacher: Teacher) -> TeacherAdminOut:
    return TeacherAdminOut(
        id=teacher.id,
        user_id=teacher.user_id,
        username=teacher.user.username,
        real_name=teacher.user.real_name,
        teacher_no=teacher.teacher_no,
        title=teacher.title,
        department=teacher.department,
        is_active=teacher.user.is_active,
    )


def list_students(db: Session, user: User) -> list[StudentAdminOut]:
    _ensure_admin(user)
    return [_student_out(item) for item in user_repository.list_students(db)]


def list_teachers(db: Session, user: User) -> list[TeacherAdminOut]:
    _ensure_admin(user)
    return [_teacher_out(item) for item in user_repository.list_teachers(db)]


def create_student(db: Session, user: User, payload: StudentCreate) -> StudentAdminOut:
    _ensure_admin(user)
    if user_repository.get_user_by_username(db, payload.username):
        raise AppError("用户名已存在")
    account = user_repository.create_user(
        db,
        User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            real_name=payload.real_name,
            role="student",
        ),
    )
    student = user_repository.create_student(
        db,
        Student(
            user_id=account.id,
            student_no=payload.student_no,
            major=payload.major,
            class_name=payload.class_name,
        ),
    )
    log_repository.add_log(db, user.id, "user.student.create", f"新增学生：{payload.real_name}")
    db.commit()
    db.refresh(student)
    return _student_out(student)


def update_student(db: Session, user: User, student_id: int, payload: StudentUpdate) -> StudentAdminOut:
    _ensure_admin(user)
    student = user_repository.get_student(db, student_id)
    if student is None:
        raise NotFound("学生不存在")
    student.user.real_name = payload.real_name
    student.user.is_active = payload.is_active
    student.student_no = payload.student_no
    student.major = payload.major
    student.class_name = payload.class_name
    log_repository.add_log(db, user.id, "user.student.update", f"修改学生：{payload.real_name}")
    db.commit()
    db.refresh(student)
    return _student_out(student)


def create_teacher(db: Session, user: User, payload: TeacherCreate) -> TeacherAdminOut:
    _ensure_admin(user)
    if user_repository.get_user_by_username(db, payload.username):
        raise AppError("用户名已存在")
    account = user_repository.create_user(
        db,
        User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            real_name=payload.real_name,
            role="teacher",
        ),
    )
    teacher = user_repository.create_teacher(
        db,
        Teacher(
            user_id=account.id,
            teacher_no=payload.teacher_no,
            title=payload.title,
            department=payload.department,
        ),
    )
    log_repository.add_log(db, user.id, "user.teacher.create", f"新增教师：{payload.real_name}")
    db.commit()
    db.refresh(teacher)
    return _teacher_out(teacher)


def update_teacher(db: Session, user: User, teacher_id: int, payload: TeacherUpdate) -> TeacherAdminOut:
    _ensure_admin(user)
    teacher = user_repository.get_teacher(db, teacher_id)
    if teacher is None:
        raise NotFound("教师不存在")
    teacher.user.real_name = payload.real_name
    teacher.user.is_active = payload.is_active
    teacher.teacher_no = payload.teacher_no
    teacher.title = payload.title
    teacher.department = payload.department
    log_repository.add_log(db, user.id, "user.teacher.update", f"修改教师：{payload.real_name}")
    db.commit()
    db.refresh(teacher)
    return _teacher_out(teacher)


def disable_user(db: Session, user: User, user_id: int) -> None:
    _ensure_admin(user)
    target = user_repository.get_user_by_id(db, user_id)
    if target is None:
        raise NotFound("用户不存在")
    if target.id == user.id:
        raise AppError("不能停用当前登录账号")
    target.is_active = False
    log_repository.add_log(db, user.id, "user.disable", f"停用账号：{target.username}")
    db.commit()

