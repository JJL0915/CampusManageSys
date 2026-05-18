from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.attachment_schema import AttachmentOut


class AssignmentCreate(BaseModel):
    course_id: int
    title: str = Field(min_length=1, max_length=128)
    description: str | None = None
    deadline: datetime


class AssignmentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    description: str | None = None
    deadline: datetime


class AssignmentOut(BaseModel):
    id: int
    course_id: int
    course_name: str
    title: str
    description: str | None
    deadline: datetime
    status: str
    submitted: bool
    submission_id: int | None
    submission_status: str | None
    grade: float | None
    max_score: int
    assignment_type: str
    required_level: str
    created_at: datetime
    attachments: list[AttachmentOut] = Field(default_factory=list)
