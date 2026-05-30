from datetime import datetime

from pydantic import BaseModel, Field


class StatCard(BaseModel):
    label: str
    value: int | float
    trend: str


class NameValue(BaseModel):
    name: str
    value: int | float


class GradeBucket(BaseModel):
    range: str
    count: int


class CourseAssignmentStat(BaseModel):
    course: str
    assignments: int
    submissions: int


class CourseGradeStat(BaseModel):
    course: str
    average: float
    graded_count: int


class RecentActivity(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime


class OperationLogItem(BaseModel):
    id: int
    created_at: datetime
    operator: str
    operator_role: str
    action: str
    detail: str | None
    module: str
    tone: str


class OverviewStats(BaseModel):
    cards: list[StatCard]
    submission_status: list[NameValue]
    grade_distribution: list[GradeBucket]
    course_assignment_counts: list[CourseAssignmentStat]
    grade_by_course: list[CourseGradeStat]
    weekly_schedule: list[dict]
    recent_activities: list[RecentActivity]
    role_distribution: list[NameValue] = Field(default_factory=list)
    course_status: list[NameValue] = Field(default_factory=list)
    operation_logs: list[OperationLogItem] = Field(default_factory=list)
