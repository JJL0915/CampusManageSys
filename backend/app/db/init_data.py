from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.assignment import Assignment
from app.models.course import Course, CourseSchedule, Enrollment, EnrollmentSetting
from app.models.log import OperationLog
from app.models.submission import Submission
from app.models.user import Student, Teacher, User


def _ensure_enrollment_setting(db: Session) -> None:
    if db.scalar(select(EnrollmentSetting).limit(1)):
        return
    now = datetime.utcnow()
    db.add(
        EnrollmentSetting(
            term="2025-2026-2",
            is_open=True,
            start_time=now - timedelta(days=30),
            end_time=now + timedelta(days=30),
            current_week=12,
        )
    )


def _ensure_course_schedules(db: Session) -> None:
    schedule_map = {
        "软件工程": [
            dict(weekday=1, start_section=1, end_section=2, start_time="08:00", end_time="09:35", classroom="教室 A301", weeks="1-16"),
            dict(weekday=4, start_section=1, end_section=2, start_time="08:00", end_time="09:35", classroom="教室 A301", weeks="1-16"),
            dict(weekday=2, start_section=7, end_section=8, start_time="16:00", end_time="17:35", classroom="教室 A301", weeks="1-16"),
        ],
        "数据库系统": [
            dict(weekday=2, start_section=1, end_section=2, start_time="08:00", end_time="09:35", classroom="教室 B204", weeks="1-16"),
            dict(weekday=5, start_section=1, end_section=2, start_time="08:00", end_time="09:35", classroom="教室 B204", weeks="1-16"),
        ],
        "Web 应用开发": [
            dict(weekday=2, start_section=5, end_section=6, start_time="14:00", end_time="15:35", classroom="实验楼 C302", weeks="1-16"),
            dict(weekday=4, start_section=5, end_section=6, start_time="14:00", end_time="15:35", classroom="实验楼 C302", weeks="1-16"),
        ],
    }
    for course_name, schedules in schedule_map.items():
        course = db.scalar(select(Course).where(Course.name == course_name))
        if course is None:
            continue
        if db.scalar(select(CourseSchedule).where(CourseSchedule.course_id == course.id).limit(1)):
            continue
        for item in schedules:
            db.add(CourseSchedule(course_id=course.id, term="2025-2026-2", **item))


def init_demo_data(db: Session) -> None:
    if db.scalar(select(User).where(User.username == "admin")):
        _ensure_enrollment_setting(db)
        _ensure_course_schedules(db)
        db.commit()
        return

    admin = User(username="admin", password_hash=hash_password("admin123"), real_name="系统管理员", role="admin")
    teacher_user = User(username="teacher1", password_hash=hash_password("123456"), real_name="李老师", role="teacher")
    teacher_user_2 = User(username="teacher2", password_hash=hash_password("123456"), real_name="王老师", role="teacher")
    student_user = User(username="student1", password_hash=hash_password("123456"), real_name="张同学", role="student")
    student_user_2 = User(username="student2", password_hash=hash_password("123456"), real_name="陈同学", role="student")
    db.add_all([admin, teacher_user, teacher_user_2, student_user, student_user_2])
    db.flush()

    teacher = Teacher(user_id=teacher_user.id, teacher_no="T2026001", title="副教授", department="计算机学院")
    teacher_2 = Teacher(user_id=teacher_user_2.id, teacher_no="T2026002", title="讲师", department="软件学院")
    student = Student(user_id=student_user.id, student_no="S2026001", major="软件工程", class_name="软工 1 班")
    student_2 = Student(user_id=student_user_2.id, student_no="S2026002", major="计算机科学", class_name="计科 2 班")
    db.add_all([teacher, teacher_2, student, student_2])
    db.flush()

    course_1 = Course(name="软件工程", description="覆盖需求分析、概要设计、详细设计和项目管理。", teacher_id=teacher.id, credit=3, capacity=60)
    course_2 = Course(name="数据库系统", description="学习关系模型、SQL、事务和索引优化。", teacher_id=teacher.id, credit=3, capacity=50)
    course_3 = Course(name="Web 应用开发", description="前后端分离应用开发实践。", teacher_id=teacher_2.id, credit=2, capacity=45)
    db.add_all([course_1, course_2, course_3])
    db.flush()
    _ensure_enrollment_setting(db)
    _ensure_course_schedules(db)

    db.add_all(
        [
            Enrollment(student_id=student.id, course_id=course_1.id),
            Enrollment(student_id=student.id, course_id=course_2.id),
            Enrollment(student_id=student_2.id, course_id=course_1.id),
        ]
    )
    db.flush()

    assignment_1 = Assignment(
        course_id=course_1.id,
        title="需求分析报告",
        description="围绕在线选课和作业管理系统提交需求分析文档。",
        deadline=datetime.utcnow() + timedelta(days=15),
    )
    assignment_2 = Assignment(
        course_id=course_1.id,
        title="详细设计说明",
        description="提交类设计、数据设计和构件设计说明。",
        deadline=datetime.utcnow() + timedelta(days=25),
    )
    assignment_3 = Assignment(
        course_id=course_2.id,
        title="SQL 查询练习",
        description="完成多表查询和聚合统计练习。",
        deadline=datetime.utcnow() + timedelta(days=10),
    )
    db.add_all([assignment_1, assignment_2, assignment_3])
    db.flush()

    db.add_all(
        [
            Submission(
                assignment_id=assignment_1.id,
                student_id=student.id,
                content="已完成需求分析报告初稿。",
                grade=92,
                feedback="结构完整，业务流程清晰。",
                graded_at=datetime.utcnow(),
                status="graded",
            ),
            Submission(
                assignment_id=assignment_1.id,
                student_id=student_2.id,
                content="提交需求分析报告。",
                status="submitted",
            ),
        ]
    )
    db.add_all(
        [
            OperationLog(user_id=admin.id, action="system.seed", detail="初始化演示数据"),
            OperationLog(user_id=teacher_user.id, action="assignment.create", detail="发布作业：需求分析报告"),
            OperationLog(user_id=student_user.id, action="submission.submit", detail="提交作业：需求分析报告"),
        ]
    )
    db.commit()
