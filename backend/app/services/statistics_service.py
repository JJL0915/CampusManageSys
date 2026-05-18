from collections import Counter

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import assignment_repository, course_repository, submission_repository
from app.services import course_service


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


def get_overview(db: Session, user: User) -> dict:
    courses = course_repository.list_courses(db)
    assignments = assignment_repository.list_assignments(db)
    submissions = submission_repository.list_submissions(db)

    if user.role == "student":
        student_id = user.student_profile.id if user.student_profile else 0
        courses = [course for course in courses if course_repository.get_enrollment(db, student_id, course.id)]
        course_ids = {course.id for course in courses}
        assignments = [item for item in assignments if item.course_id in course_ids]
        submissions = [item for item in submissions if item.student_id == student_id]
    elif user.role == "teacher":
        teacher_id = user.teacher_profile.id if user.teacher_profile else 0
        courses = [course for course in courses if course.teacher_id == teacher_id]
        assignments = [item for item in assignments if item.course.teacher_id == teacher_id]
        submissions = [item for item in submissions if item.assignment.course.teacher_id == teacher_id]

    status_counter = Counter(item.status for item in submissions)
    grade_counter = Counter(filter(None, (_bucket(item.grade) for item in submissions)))
    graded_submissions = [item for item in submissions if item.grade is not None]
    average_grade = round(sum(item.grade or 0 for item in graded_submissions) / max(1, len(graded_submissions)), 1)

    course_stats = []
    grade_by_course = []
    for course in courses:
        related_assignments = [item for item in assignments if item.course_id == course.id]
        related_assignment_ids = {item.id for item in related_assignments}
        related_submissions = [item for item in submissions if item.assignment_id in related_assignment_ids]
        related_grades = [item.grade for item in related_submissions if item.grade is not None]
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
        "weekly_schedule": [item.model_dump() for item in course_service.get_weekly_schedule(db, user)],
        "recent_activities": [],
    }
