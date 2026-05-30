from collections import Counter

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import (
    assignment_repository,
    course_repository,
    log_repository,
    submission_repository,
    user_repository,
)
from app.services import course_service

ROLE_LABELS = {
    "student": "学生",
    "teacher": "教师",
    "admin": "管理员",
}

ACTION_MODULES = {
    "system": ("系统日志", "blue"),
    "user": ("用户管理", "blue"),
    "course": ("课程管理", "green"),
    "assignment": ("作业管理", "orange"),
    "submission": ("提交批改", "violet"),
    "enrollment": ("选课设置", "blue"),
}

ACTION_LABELS = {
    "system.seed": "初始化演示数据",
    "user.student.create": "新增学生",
    "user.student.update": "修改学生",
    "user.teacher.create": "新增教师",
    "user.teacher.update": "修改教师",
    "user.disable": "停用账号",
    "course.create": "创建课程",
    "course.update": "修改课程",
    "course.delete": "删除课程",
    "course.enroll": "选择课程",
    "course.admin_drop": "管理员退课",
    "assignment.create": "发布作业",
    "assignment.update": "修改作业",
    "assignment.delete": "删除作业",
    "submission.submit": "提交作业",
    "submission.create": "提交作业",
    "submission.update": "修改提交",
    "submission.grade": "发布成绩",
    "enrollment.setting": "更新选课设置",
}


def _bucket(grade: float | None) -> str | None:
    if grade is None:
        return None
    if grade >= 90:
        return "90-100"
    if grade >= 80:
        return "80-89"
    if grade >= 70:
        return "70-79"
    if grade >= 60:
        return "60-69"
    return "0-59"


def _action_module(action: str) -> tuple[str, str]:
    prefix = action.split(".", 1)[0]
    return ACTION_MODULES.get(prefix, ("系统操作", "blue"))


def _admin_overview(db: Session) -> dict:
    users = user_repository.list_users(db)
    courses = course_repository.list_courses(db)
    assignments = assignment_repository.list_assignments(db)
    role_counter = Counter(user.role for user in users)
    active_count = sum(1 for item in users if item.is_active)
    scheduled_count = sum(1 for item in courses if item.schedules)
    assignment_course_ids = {item.course_id for item in assignments}

    logs = []
    for item in log_repository.list_recent_logs(db, limit=6):
        operator = (
            user_repository.get_user_by_id(db, item.user_id) if item.user_id else None
        )
        module, tone = _action_module(item.action)
        logs.append(
            {
                "id": item.id,
                "created_at": item.created_at,
                "operator": operator.real_name if operator else "系统",
                "operator_role": (
                    ROLE_LABELS.get(operator.role, "系统") if operator else "系统"
                ),
                "action": ACTION_LABELS.get(item.action, item.action),
                "detail": item.detail,
                "module": module,
                "tone": tone,
            }
        )

    return {
        "cards": [
            {
                "label": "用户总数",
                "value": len(users),
                "trend": f"启用 {active_count} / 停用 {len(users) - active_count}",
            },
            {
                "label": "教师数",
                "value": role_counter.get("teacher", 0),
                "trend": "教师账号",
            },
            {
                "label": "学生数",
                "value": role_counter.get("student", 0),
                "trend": "学生账号",
            },
            {"label": "课程数", "value": len(courses), "trend": "全部课程"},
        ],
        "submission_status": [],
        "grade_distribution": [],
        "course_assignment_counts": [],
        "grade_by_course": [],
        "weekly_schedule": [],
        "recent_activities": [],
        "role_distribution": [
            {"name": ROLE_LABELS["student"], "value": role_counter.get("student", 0)},
            {"name": ROLE_LABELS["teacher"], "value": role_counter.get("teacher", 0)},
            {"name": ROLE_LABELS["admin"], "value": role_counter.get("admin", 0)},
        ],
        "course_status": [
            {"name": "已排课", "value": scheduled_count},
            {"name": "未排课", "value": len(courses) - scheduled_count},
            {"name": "有作业", "value": len(assignment_course_ids)},
            {"name": "无作业", "value": len(courses) - len(assignment_course_ids)},
        ],
        "operation_logs": logs,
    }


def get_overview(db: Session, user: User) -> dict:
    if user.role == "admin":
        return _admin_overview(db)

    courses = course_repository.list_courses(db)
    assignments = assignment_repository.list_assignments(db)
    submissions = submission_repository.list_submissions(db)

    if user.role == "student":
        student_id = user.student_profile.id if user.student_profile else 0
        courses = [
            course
            for course in courses
            if course_repository.get_enrollment(db, student_id, course.id)
        ]
        course_ids = {course.id for course in courses}
        assignments = [item for item in assignments if item.course_id in course_ids]
        submissions = [item for item in submissions if item.student_id == student_id]
    elif user.role == "teacher":
        teacher_id = user.teacher_profile.id if user.teacher_profile else 0
        courses = [course for course in courses if course.teacher_id == teacher_id]
        assignments = [
            item for item in assignments if item.course.teacher_id == teacher_id
        ]
        submissions = [
            item
            for item in submissions
            if item.assignment.course.teacher_id == teacher_id
        ]

    status_counter = Counter(item.status for item in submissions)
    grade_counter = Counter(filter(None, (_bucket(item.grade) for item in submissions)))
    graded_submissions = [item for item in submissions if item.grade is not None]
    average_grade = round(
        sum(item.grade or 0 for item in graded_submissions)
        / max(1, len(graded_submissions)),
        1,
    )

    course_stats = []
    grade_by_course = []
    for course in courses:
        related_assignments = [
            item for item in assignments if item.course_id == course.id
        ]
        related_assignment_ids = {item.id for item in related_assignments}
        related_submissions = [
            item for item in submissions if item.assignment_id in related_assignment_ids
        ]
        related_grades = [
            item.grade for item in related_submissions if item.grade is not None
        ]
        course_stats.append(
            {
                "course": course.name,
                "assignments": len(related_assignments),
                "submissions": len(related_submissions),
            }
        )
        grade_by_course.append(
            {
                "course": course.name,
                "average": round(sum(related_grades) / max(1, len(related_grades)), 1),
                "graded_count": len(related_grades),
            }
        )

    return {
        "cards": [
            {"label": "课程数", "value": len(courses), "trend": "当前范围"},
            {"label": "作业数", "value": len(assignments), "trend": "已发布"},
            {"label": "提交数", "value": len(submissions), "trend": "含已批改"},
            {"label": "平均分", "value": average_grade, "trend": "已批改"},
        ],
        "submission_status": [
            {"name": "待批改", "value": status_counter.get("submitted", 0)},
            {"name": "已批改", "value": status_counter.get("graded", 0)},
        ],
        "grade_distribution": [
            {"range": label, "count": grade_counter.get(label, 0)}
            for label in ["90-100", "80-89", "70-79", "60-69", "0-59"]
        ],
        "course_assignment_counts": course_stats,
        "grade_by_course": grade_by_course,
        "weekly_schedule": [
            item.model_dump() for item in course_service.get_weekly_schedule(db, user)
        ],
        "recent_activities": [],
        "role_distribution": [],
        "course_status": [],
        "operation_logs": [],
    }
