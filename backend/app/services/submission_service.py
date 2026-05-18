from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFound, PermissionDenied
from app.models.attachment import SubmissionAttachment
from app.models.submission import Submission
from app.models.user import User
from app.repositories import (
    assignment_repository,
    course_repository,
    log_repository,
    submission_repository,
)
from app.schemas.attachment_schema import AttachmentOut
from app.schemas.submission_schema import (
    GradeRequest,
    SubmissionCreate,
    SubmissionOut,
    SubmissionUpdate,
)
from app.services.file_service import (
    StoredUpload,
    delete_stored_file,
    save_upload_files,
)


def _student_id(user: User) -> int:
    if not user.student_profile:
        raise PermissionDenied("当前用户不是学生")
    return user.student_profile.id


def _teacher_id(user: User) -> int:
    if not user.teacher_profile:
        raise PermissionDenied("当前用户不是教师")
    return user.teacher_profile.id


def _attachment_out(attachment: SubmissionAttachment) -> AttachmentOut:
    return AttachmentOut(
        id=attachment.id,
        original_name=attachment.original_name,
        url=attachment.url,
        content_type=attachment.content_type,
        size=attachment.size,
        is_image=attachment.is_image,
        created_at=attachment.created_at,
    )


def _append_attachments(submission: Submission, uploads: list[StoredUpload]) -> None:
    for upload in uploads:
        submission.attachments.append(
            SubmissionAttachment(
                original_name=upload.original_name,
                stored_name=upload.stored_name,
                file_path=upload.file_path,
                url=upload.url,
                content_type=upload.content_type,
                size=upload.size,
                is_image=upload.is_image,
            )
        )


def _sync_attachments(
    submission: Submission,
    uploads: list[StoredUpload],
    keep_attachment_ids: set[int] | None,
) -> None:
    if keep_attachment_ids is not None:
        for attachment in list(submission.attachments):
            if attachment.id not in keep_attachment_ids:
                delete_stored_file(attachment.file_path)
                submission.attachments.remove(attachment)
    _append_attachments(submission, uploads)


def _submission_out(submission: Submission) -> SubmissionOut:
    assignment = submission.assignment
    course = assignment.course
    return SubmissionOut(
        id=submission.id,
        assignment_id=submission.assignment_id,
        assignment_title=assignment.title,
        course_id=course.id,
        course_name=course.name,
        student_id=submission.student_id,
        student_no=submission.student.student_no,
        student_name=submission.student.user.real_name,
        content=submission.content,
        grade=submission.grade,
        feedback=submission.feedback,
        submit_time=submission.submit_time,
        graded_at=submission.graded_at,
        status=submission.status,
        attachments=[_attachment_out(item) for item in submission.attachments],
    )


def submit_assignment(
    db: Session, user: User, payload: SubmissionCreate
) -> SubmissionOut:
    return submit_assignment_with_files(
        db, user, payload.assignment_id, payload.content, files=None
    )


def submit_assignment_with_files(
    db: Session,
    user: User,
    assignment_id: int,
    content: str,
    files: list[UploadFile] | None = None,
    keep_attachment_ids: set[int] | None = None,
) -> SubmissionOut:
    student_id = _student_id(user)
    assignment = assignment_repository.get_assignment(db, assignment_id)
    if assignment is None:
        raise NotFound("作业不存在")
    if not course_repository.get_enrollment(db, student_id, assignment.course_id):
        raise PermissionDenied("未选该课程，不能提交作业")
    if assignment.deadline < datetime.utcnow():
        raise AppError("作业已截止")
    uploads = save_upload_files(files, "submissions")
    submission = submission_repository.get_submission_by_assignment_student(
        db, assignment.id, student_id
    )
    has_kept_attachment = bool(keep_attachment_ids) if submission is not None else False
    if not content.strip() and not uploads and not has_kept_attachment:
        raise AppError("请填写提交说明或上传附件")
    if submission is None:
        submission = Submission(
            assignment_id=assignment.id,
            student_id=student_id,
            content=content,
            status="submitted",
        )
    else:
        submission.content = content
        submission.status = "submitted"
        submission.grade = None
        submission.feedback = None
        submission.graded_at = None
        submission.submit_time = datetime.utcnow()
    submission_repository.save_submission(db, submission)
    _sync_attachments(submission, uploads, keep_attachment_ids)
    log_repository.add_log(
        db, user.id, "submission.submit", f"提交作业：{assignment.title}"
    )
    db.commit()
    db.refresh(submission)
    return _submission_out(submission)


def update_submission(
    db: Session, user: User, submission_id: int, payload: SubmissionUpdate
) -> SubmissionOut:
    return update_submission_with_files(
        db, user, submission_id, payload.content, files=None, keep_attachment_ids=None
    )


def update_submission_with_files(
    db: Session,
    user: User,
    submission_id: int,
    content: str,
    files: list[UploadFile] | None = None,
    keep_attachment_ids: set[int] | None = None,
) -> SubmissionOut:
    student_id = _student_id(user)
    submission = submission_repository.get_submission(db, submission_id)
    if submission is None:
        raise NotFound("提交记录不存在")
    if submission.student_id != student_id:
        raise PermissionDenied("只能修改自己的提交")
    if submission.assignment.deadline < datetime.utcnow():
        raise AppError("作业已截止")
    uploads = save_upload_files(files, "submissions")
    kept_ids = (
        {attachment.id for attachment in submission.attachments}
        if keep_attachment_ids is None
        else keep_attachment_ids
    )
    if not content.strip() and not uploads and not kept_ids:
        raise AppError("请填写提交说明或上传附件")
    submission.content = content
    submission.status = "submitted"
    submission.grade = None
    submission.feedback = None
    submission.graded_at = None
    submission.submit_time = datetime.utcnow()
    _sync_attachments(submission, uploads, kept_ids)
    log_repository.add_log(
        db, user.id, "submission.update", f"修改提交：{submission.assignment.title}"
    )
    db.commit()
    db.refresh(submission)
    return _submission_out(submission)


def list_submissions(
    db: Session,
    user: User,
    assignment_id: int | None = None,
    course_id: int | None = None,
    status: str | None = None,
) -> list[SubmissionOut]:
    submissions = submission_repository.list_submissions(db)
    if assignment_id:
        submissions = [
            item for item in submissions if item.assignment_id == assignment_id
        ]
    if course_id:
        submissions = [
            item for item in submissions if item.assignment.course_id == course_id
        ]
    if status:
        submissions = [item for item in submissions if item.status == status]
    if user.role == "student":
        student_id = _student_id(user)
        submissions = [item for item in submissions if item.student_id == student_id]
    elif user.role == "teacher":
        teacher_id = _teacher_id(user)
        submissions = [
            item
            for item in submissions
            if item.assignment.course.teacher_id == teacher_id
        ]
    elif user.role != "admin":
        raise PermissionDenied()
    return [_submission_out(item) for item in submissions]


def grade_submission(
    db: Session, user: User, submission_id: int, payload: GradeRequest
) -> SubmissionOut:
    teacher_id = _teacher_id(user)
    submission = submission_repository.get_submission(db, submission_id)
    if submission is None:
        raise NotFound("提交记录不存在")
    if submission.assignment.course.teacher_id != teacher_id:
        raise PermissionDenied("只能批改本人课程作业")
    submission.grade = payload.grade
    submission.feedback = payload.feedback
    submission.status = "graded"
    submission.graded_at = datetime.utcnow()
    log_repository.add_log(
        db, user.id, "submission.grade", f"批改作业：{submission.assignment.title}"
    )
    db.commit()
    db.refresh(submission)
    return _submission_out(submission)
