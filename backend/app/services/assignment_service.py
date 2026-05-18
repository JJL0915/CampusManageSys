from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import NotFound, PermissionDenied
from app.models.assignment import Assignment
from app.models.attachment import AssignmentAttachment
from app.models.user import User
from app.repositories import assignment_repository, course_repository, log_repository
from app.schemas.attachment_schema import AttachmentOut
from app.schemas.assignment_schema import AssignmentCreate, AssignmentOut, AssignmentUpdate
from app.services.file_service import StoredUpload, save_upload_files


def _teacher_id(user: User) -> int:
    if not user.teacher_profile:
        raise PermissionDenied("当前用户不是教师")
    return user.teacher_profile.id


def _attachment_out(attachment: AssignmentAttachment) -> AttachmentOut:
    return AttachmentOut(
        id=attachment.id,
        original_name=attachment.original_name,
        url=attachment.url,
        content_type=attachment.content_type,
        size=attachment.size,
        is_image=attachment.is_image,
        created_at=attachment.created_at,
    )


def _append_attachments(assignment: Assignment, uploads: list[StoredUpload]) -> None:
    for upload in uploads:
        assignment.attachments.append(
            AssignmentAttachment(
                original_name=upload.original_name,
                stored_name=upload.stored_name,
                file_path=upload.file_path,
                url=upload.url,
                content_type=upload.content_type,
                size=upload.size,
                is_image=upload.is_image,
            )
        )


def _assignment_out(assignment: Assignment, user: User | None = None) -> AssignmentOut:
    student_id = user.student_profile.id if user and user.student_profile else None
    submission = None
    if student_id:
        submission = next((item for item in assignment.submissions if item.student_id == student_id), None)
    return AssignmentOut(
        id=assignment.id,
        course_id=assignment.course_id,
        course_name=assignment.course.name,
        title=assignment.title,
        description=assignment.description,
        deadline=assignment.deadline,
        status="closed" if assignment.deadline < datetime.utcnow() else "open",
        submitted=submission is not None,
        submission_id=submission.id if submission else None,
        submission_status=submission.status if submission else None,
        grade=submission.grade if submission else None,
        max_score=100,
        assignment_type="课程作业",
        required_level="必做",
        created_at=assignment.created_at,
        attachments=[_attachment_out(item) for item in assignment.attachments],
    )


def _check_assignment_visible(db: Session, assignment: Assignment, user: User) -> None:
    if user.role == "student":
        student_id = user.student_profile.id if user.student_profile else 0
        if not course_repository.get_enrollment(db, student_id, assignment.course_id):
            raise PermissionDenied("只能查看已选课程作业")
    elif user.role == "teacher":
        if assignment.course.teacher_id != _teacher_id(user):
            raise PermissionDenied("只能查看本人课程作业")
    elif user.role != "admin":
        raise PermissionDenied()


def list_assignments(
    db: Session,
    user: User,
    course_id: int | None = None,
    only_mine: bool = False,
) -> list[AssignmentOut]:
    assignments = assignment_repository.list_assignments(db)
    if course_id:
        assignments = [item for item in assignments if item.course_id == course_id]
    if only_mine and user.role == "teacher":
        teacher_id = _teacher_id(user)
        assignments = [item for item in assignments if item.course.teacher_id == teacher_id]
    if only_mine and user.role == "student":
        student_id = user.student_profile.id if user.student_profile else None
        assignments = [
            item
            for item in assignments
            if student_id and course_repository.get_enrollment(db, student_id, item.course_id)
        ]
    return [_assignment_out(item, user) for item in assignments]


def get_assignment(db: Session, user: User, assignment_id: int) -> AssignmentOut:
    assignment = assignment_repository.get_assignment(db, assignment_id)
    if assignment is None:
        raise NotFound("作业不存在")
    _check_assignment_visible(db, assignment, user)
    return _assignment_out(assignment, user)


def create_assignment(db: Session, user: User, payload: AssignmentCreate) -> AssignmentOut:
    return create_assignment_with_files(db, user, payload, files=None)


def create_assignment_with_files(
    db: Session,
    user: User,
    payload: AssignmentCreate,
    files: list[UploadFile] | None = None,
) -> AssignmentOut:
    teacher_id = _teacher_id(user)
    course = course_repository.get_course(db, payload.course_id)
    if course is None:
        raise NotFound("课程不存在")
    if course.teacher_id != teacher_id:
        raise PermissionDenied("只能在本人课程下发布作业")
    uploads = save_upload_files(files, "assignments")
    assignment = assignment_repository.create_assignment(
        db,
        Assignment(
            course_id=payload.course_id,
            title=payload.title,
            description=payload.description,
            deadline=payload.deadline,
        ),
    )
    _append_attachments(assignment, uploads)
    log_repository.add_log(db, user.id, "assignment.create", f"发布作业：{assignment.title}")
    db.commit()
    assignment = assignment_repository.get_assignment(db, assignment.id) or assignment
    return _assignment_out(assignment, user)


def update_assignment(db: Session, user: User, assignment_id: int, payload: AssignmentUpdate) -> AssignmentOut:
    teacher_id = _teacher_id(user)
    assignment = assignment_repository.get_assignment(db, assignment_id)
    if assignment is None:
        raise NotFound("作业不存在")
    if assignment.course.teacher_id != teacher_id:
        raise PermissionDenied("只能修改本人课程作业")
    assignment.title = payload.title
    assignment.description = payload.description
    assignment.deadline = payload.deadline
    log_repository.add_log(db, user.id, "assignment.update", f"修改作业：{assignment.title}")
    db.commit()
    assignment = assignment_repository.get_assignment(db, assignment_id) or assignment
    return _assignment_out(assignment, user)


def delete_assignment(db: Session, user: User, assignment_id: int) -> None:
    teacher_id = _teacher_id(user)
    assignment = assignment_repository.get_assignment(db, assignment_id)
    if assignment is None:
        raise NotFound("作业不存在")
    if assignment.course.teacher_id != teacher_id:
        raise PermissionDenied("只能删除本人课程作业")
    log_repository.add_log(db, user.id, "assignment.delete", f"删除作业：{assignment.title}")
    assignment_repository.delete_assignment(db, assignment)
    db.commit()
