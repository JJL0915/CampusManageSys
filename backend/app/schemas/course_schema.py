from datetime import datetime

from pydantic import BaseModel, Field


class CourseScheduleBase(BaseModel):
    weekday: int = Field(ge=1, le=7)
    start_section: int = Field(ge=1, le=9)
    end_section: int = Field(ge=1, le=10)
    start_time: str = Field(default="08:00", max_length=5)
    end_time: str = Field(default="09:35", max_length=5)
    classroom: str = Field(default="", max_length=64)
    weeks: str = Field(default="1-16", max_length=64)
    term: str = Field(default="2025-2026-2", max_length=32)


class CourseScheduleCreate(CourseScheduleBase):
    pass


class CourseScheduleOut(CourseScheduleBase):
    id: int
    course_id: int


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    teacher_id: int
    credit: int = Field(default=2, ge=1, le=8)
    capacity: int = Field(default=60, ge=1, le=500)
    schedules: list[CourseScheduleCreate] = Field(default_factory=list)


class CourseUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    teacher_id: int
    credit: int = Field(default=2, ge=1, le=8)
    capacity: int = Field(default=60, ge=1, le=500)
    schedules: list[CourseScheduleCreate] = Field(default_factory=list)


class CourseOut(BaseModel):
    id: int
    name: str
    description: str | None
    teacher_id: int
    teacher_name: str
    credit: int
    capacity: int
    selected_count: int
    is_selected: bool
    created_at: datetime
    schedules: list[CourseScheduleOut]


class CourseStudentOut(BaseModel):
    student_id: int
    student_no: str
    real_name: str
    major: str | None
    class_name: str | None
    selected_at: datetime


class EnrollmentSettingOut(BaseModel):
    id: int
    term: str
    is_open: bool
    start_time: datetime
    end_time: datetime
    current_week: int


class EnrollmentSettingUpdate(BaseModel):
    term: str = Field(max_length=32)
    is_open: bool
    start_time: datetime
    end_time: datetime
    current_week: int = Field(ge=1, le=30)


class WeeklyScheduleItem(BaseModel):
    course_id: int
    course_name: str
    teacher_name: str
    weekday: int
    start_section: int
    end_section: int
    start_time: str
    end_time: str
    classroom: str
    weeks: str
    term: str
