from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.user import Student, Teacher, User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(
        select(User)
        .options(joinedload(User.student_profile), joinedload(User.teacher_profile))
        .where(User.username == username)
    )


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(
        select(User)
        .options(joinedload(User.student_profile), joinedload(User.teacher_profile))
        .where(User.id == user_id)
    )


def get_teacher(db: Session, teacher_id: int) -> Teacher | None:
    return db.get(Teacher, teacher_id)


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)


def list_students(db: Session) -> list[Student]:
    return list(db.scalars(select(Student).options(joinedload(Student.user))).all())


def list_teachers(db: Session) -> list[Teacher]:
    return list(db.scalars(select(Teacher).options(joinedload(Teacher.user))).all())


def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def create_student(db: Session, student: Student) -> Student:
    db.add(student)
    db.flush()
    db.refresh(student)
    return student


def create_teacher(db: Session, teacher: Teacher) -> Teacher:
    db.add(teacher)
    db.flush()
    db.refresh(teacher)
    return teacher
