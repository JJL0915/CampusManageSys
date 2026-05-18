from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment
from app.models.course import Course
from app.models.submission import Submission
from app.models.user import Student


def get_submission(db: Session, submission_id: int) -> Submission | None:
    return (
        db.execute(
            select(Submission)
            .options(
                joinedload(Submission.assignment).joinedload(Assignment.course),
                joinedload(Submission.student).joinedload(Student.user),
                joinedload(Submission.attachments),
            )
            .where(Submission.id == submission_id)
        )
        .unique()
        .scalar_one_or_none()
    )


def get_submission_by_assignment_student(db: Session, assignment_id: int, student_id: int) -> Submission | None:
    return (
        db.execute(
            select(Submission)
            .options(
                joinedload(Submission.assignment).joinedload(Assignment.course),
                joinedload(Submission.student).joinedload(Student.user),
                joinedload(Submission.attachments),
            )
            .where(Submission.assignment_id == assignment_id, Submission.student_id == student_id)
        )
        .unique()
        .scalar_one_or_none()
    )


def list_submissions(db: Session) -> list[Submission]:
    return list(
        db.scalars(
            select(Submission)
            .options(
                joinedload(Submission.assignment).joinedload(Assignment.course),
                joinedload(Submission.student).joinedload(Student.user),
                joinedload(Submission.attachments),
            )
            .order_by(Submission.submit_time.desc())
        )
        .unique()
        .all()
    )


def save_submission(db: Session, submission: Submission) -> Submission:
    db.add(submission)
    db.flush()
    db.refresh(submission)
    return submission
