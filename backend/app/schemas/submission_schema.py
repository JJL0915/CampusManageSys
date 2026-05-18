from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.attachment_schema import AttachmentOut


class SubmissionCreate(BaseModel):
    assignment_id: int
    content: str = Field(min_length=1)


class SubmissionUpdate(BaseModel):
    content: str = Field(min_length=1)


class GradeRequest(BaseModel):
    grade: float = Field(ge=0, le=100)
    feedback: str | None = None


class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    assignment_title: str
    course_id: int
    course_name: str
    student_id: int
    student_no: str
    student_name: str
    content: str
    grade: float | None
    feedback: str | None
    submit_time: datetime
    graded_at: datetime | None
    status: str
    attachments: list[AttachmentOut] = Field(default_factory=list)
