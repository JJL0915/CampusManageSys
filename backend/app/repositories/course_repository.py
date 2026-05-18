from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.course import Course, CourseSchedule, Enrollment, EnrollmentSetting
from app.models.user import Student, Teacher


def list_courses(db: Session) -> list[Course]:
    return list(
        db.scalars(
            select(Course).options(joinedload(Course.teacher).joinedload(Teacher.user), joinedload(Course.schedules))
        )
        .unique()
        .all()
    )


def get_course(db: Session, course_id: int) -> Course | None:
    return (
        db.execute(
            select(Course)
            .options(joinedload(Course.teacher).joinedload(Teacher.user), joinedload(Course.enrollments), joinedload(Course.schedules))
            .where(Course.id == course_id)
        )
        .unique()
        .scalar_one_or_none()
    )


def create_course(db: Session, course: Course) -> Course:
    db.add(course)
    db.flush()
    db.refresh(course)
    return course


def delete_course(db: Session, course: Course) -> None:
    db.delete(course)


def get_enrollment(db: Session, student_id: int, course_id: int) -> Enrollment | None:
    return db.scalar(select(Enrollment).where(Enrollment.student_id == student_id, Enrollment.course_id == course_id))


def count_course_enrollments(db: Session, course_id: int) -> int:
    return db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)) or 0


def create_enrollment(db: Session, enrollment: Enrollment) -> Enrollment:
    db.add(enrollment)
    db.flush()
    db.refresh(enrollment)
    return enrollment


def delete_enrollment(db: Session, enrollment: Enrollment) -> None:
    db.delete(enrollment)


def list_course_students(db: Session, course_id: int) -> list[Enrollment]:
    return list(
        db.scalars(
            select(Enrollment)
            .options(joinedload(Enrollment.student).joinedload(Student.user))
            .where(Enrollment.course_id == course_id)
            .order_by(Enrollment.selected_at.desc())
        )
        .unique()
        .all()
    )


def list_student_enrollments(db: Session, student_id: int) -> list[Enrollment]:
    return list(
        db.scalars(
            select(Enrollment)
            .options(joinedload(Enrollment.course).joinedload(Course.schedules), joinedload(Enrollment.course).joinedload(Course.teacher).joinedload(Teacher.user))
            .where(Enrollment.student_id == student_id)
        )
        .unique()
        .all()
    )


def get_enrollment_setting(db: Session) -> EnrollmentSetting | None:
    return db.scalar(select(EnrollmentSetting).order_by(EnrollmentSetting.id.asc()).limit(1))


def save_enrollment_setting(db: Session, setting: EnrollmentSetting) -> EnrollmentSetting:
    db.add(setting)
    db.flush()
    db.refresh(setting)
    return setting
