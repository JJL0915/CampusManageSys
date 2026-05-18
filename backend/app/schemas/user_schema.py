from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    real_name: str = Field(min_length=1, max_length=64)
    student_no: str = Field(min_length=1, max_length=32)
    major: str | None = None
    class_name: str | None = None


class StudentUpdate(BaseModel):
    real_name: str = Field(min_length=1, max_length=64)
    student_no: str = Field(min_length=1, max_length=32)
    major: str | None = None
    class_name: str | None = None
    is_active: bool = True


class StudentAdminOut(BaseModel):
    id: int
    user_id: int
    username: str
    real_name: str
    student_no: str
    major: str | None
    class_name: str | None
    is_active: bool


class TeacherCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    real_name: str = Field(min_length=1, max_length=64)
    teacher_no: str = Field(min_length=1, max_length=32)
    title: str | None = None
    department: str | None = None


class TeacherUpdate(BaseModel):
    real_name: str = Field(min_length=1, max_length=64)
    teacher_no: str = Field(min_length=1, max_length=32)
    title: str | None = None
    department: str | None = None
    is_active: bool = True


class TeacherAdminOut(BaseModel):
    id: int
    user_id: int
    username: str
    real_name: str
    teacher_no: str
    title: str | None
    department: str | None
    is_active: bool

