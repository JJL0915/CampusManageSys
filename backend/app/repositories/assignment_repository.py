from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment
from app.models.attachment import AssignmentAttachment
from app.models.course import Course
from app.models.user import Teacher


def list_assignments(db: Session) -> list[Assignment]:
    return list(
        db.scalars(
            select(Assignment)
            .options(
                joinedload(Assignment.course).joinedload(Course.teacher).joinedload(Teacher.user),
                joinedload(Assignment.submissions),
                joinedload(Assignment.attachments),
            )
            .order_by(Assignment.deadline.asc())
        )
        .unique()
        .all()
    )


def get_assignment(db: Session, assignment_id: int) -> Assignment | None:
    return (
        db.execute(
            select(Assignment)
            .options(
                joinedload(Assignment.course),
                joinedload(Assignment.submissions),
                joinedload(Assignment.attachments),
            )
            .where(Assignment.id == assignment_id)
        )
        .unique()
        .scalar_one_or_none()
    )


def create_assignment(db: Session, assignment: Assignment) -> Assignment:
    db.add(assignment)
    db.flush()
    db.refresh(assignment)
    return assignment


def delete_assignment(db: Session, assignment: Assignment) -> None:
    db.delete(assignment)
