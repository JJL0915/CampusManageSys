from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFound, PermissionDenied
from app.models.course import Course, CourseSchedule, Enrollment, EnrollmentSetting
from app.models.user import User
from app.repositories import course_repository, log_repository, user_repository
from app.schemas.course_schema import (
    CourseCreate,
    CourseOut,
    CourseScheduleCreate,
    CourseScheduleOut,
    CourseStudentOut,
    CourseUpdate,
    EnrollmentSettingOut,
    EnrollmentSettingUpdate,
    WeeklyScheduleItem,
)

SECTION_TIME_SLOTS = (
    (1, 2, "08:00", "09:35"),
    (3, 4, "10:00", "11:35"),
    (5, 6, "14:00", "15:35"),
    (7, 8, "16:00", "17:35"),
    (9, 10, "19:00", "20:35"),
)


def _current_student_id(user: User) -> int:
    if not user.student_profile:
        raise PermissionDenied("当前用户不是学生")
    return user.student_profile.id


def _current_teacher_id(user: User) -> int:
    if not user.teacher_profile:
        raise PermissionDenied("当前用户不是教师")
    return user.teacher_profile.id


def _section_slot(section: int) -> tuple[int, int, str, str]:
    for slot in SECTION_TIME_SLOTS:
        if section <= slot[1]:
            return slot
    return SECTION_TIME_SLOTS[-1]


def _schedule_out(item: CourseSchedule) -> CourseScheduleOut:
    start_section, end_section, start_time, end_time = _section_slot(item.start_section)
    return CourseScheduleOut(
        id=item.id,
        course_id=item.course_id,
        weekday=item.weekday,
        start_section=start_section,
        end_section=end_section,
        start_time=start_time,
        end_time=end_time,
        classroom=item.classroom,
        weeks=item.weeks,
        term=item.term,
    )


def _course_out(db: Session, course: Course, user: User | None = None) -> CourseOut:
    student_id = user.student_profile.id if user and user.student_profile else None
    selected = bool(student_id and course_repository.get_enrollment(db, student_id, course.id))
    return CourseOut(
        id=course.id,
        name=course.name,
        description=course.description,
        teacher_id=course.teacher_id,
        teacher_name=course.teacher.user.real_name,
        credit=course.credit,
        capacity=course.capacity,
        selected_count=course_repository.count_course_enrollments(db, course.id),
        is_selected=selected,
        created_at=course.created_at,
        schedules=[_schedule_out(item) for item in sorted(course.schedules, key=lambda s: (s.weekday, s.start_section))],
    )


def _default_setting() -> EnrollmentSetting:
    now = datetime.utcnow()
    return EnrollmentSetting(
        term="2025-2026-2",
        is_open=True,
        start_time=now - timedelta(days=30),
        end_time=now + timedelta(days=30),
        current_week=12,
    )


def _get_or_create_setting(db: Session) -> EnrollmentSetting:
    setting = course_repository.get_enrollment_setting(db)
    if setting is None:
        setting = course_repository.save_enrollment_setting(db, _default_setting())
        db.commit()
    return setting


def _weeks_to_set(raw: str) -> set[int]:
    result: set[int] = set()
    for part in raw.replace("周", "").split(","):
        item = part.strip()
        if not item:
            continue
        if "-" in item:
            start, end = item.split("-", 1)
            if start.strip().isdigit() and end.strip().isdigit():
                result.update(range(int(start), int(end) + 1))
        elif item.isdigit():
            result.add(int(item))
    return result


def _weeks_overlap(left: str, right: str) -> bool:
    left_weeks = _weeks_to_set(left)
    right_weeks = _weeks_to_set(right)
    if not left_weeks or not right_weeks:
        return True
    return bool(left_weeks & right_weeks)


def _section_overlap(left: CourseSchedule, right: CourseSchedule) -> bool:
    return left.start_section <= right.end_section and right.start_section <= left.end_section


def _has_schedule_conflict(db: Session, student_id: int, target: Course) -> str | None:
    for enrollment in course_repository.list_student_enrollments(db, student_id):
        course = enrollment.course
        if course.id == target.id:
            continue
        for selected_schedule in course.schedules:
            for target_schedule in target.schedules:
                if (
                    selected_schedule.term == target_schedule.term
                    and selected_schedule.weekday == target_schedule.weekday
                    and _section_overlap(selected_schedule, target_schedule)
                    and _weeks_overlap(selected_schedule.weeks, target_schedule.weeks)
                ):
                    return f"与已选课程「{course.name}」时间冲突"
    return None


def _ensure_enrollment_open(db: Session) -> None:
    setting = _get_or_create_setting(db)
    now = datetime.utcnow()
    if not setting.is_open:
        raise AppError("当前未开放选课")
    if now < setting.start_time or now > setting.end_time:
        raise AppError("当前不在选课时间范围内")


def _replace_schedules(course: Course, schedules: list[CourseScheduleCreate]) -> None:
    course.schedules.clear()
    for item in schedules:
        if item.end_section < item.start_section:
            raise AppError("课程结束节次不能小于开始节次")
        if item.start_section > 9 or item.end_section > 10:
            raise AppError("课程一天最多排到第10节")
        start_section, end_section, start_time, end_time = _section_slot(item.start_section)
        if item.start_section != start_section or item.end_section != end_section:
            raise AppError("课程节次需按1-2、3-4、5-6、7-8、9-10设置")
        course.schedules.append(
            CourseSchedule(
                weekday=item.weekday,
                start_section=start_section,
                end_section=end_section,
                start_time=start_time,
                end_time=end_time,
                classroom=item.classroom,
                weeks=item.weeks,
                term=item.term,
            )
        )


def list_courses(db: Session, user: User, keyword: str | None = None, only_mine: bool = False) -> list[CourseOut]:
    courses = course_repository.list_courses(db)
    if keyword:
        courses = [course for course in courses if keyword.lower() in course.name.lower()]
    if only_mine and user.role == "teacher":
        teacher_id = _current_teacher_id(user)
        courses = [course for course in courses if course.teacher_id == teacher_id]
    if only_mine and user.role == "student":
        student_id = _current_student_id(user)
        courses = [course for course in courses if course_repository.get_enrollment(db, student_id, course.id)]
    return [_course_out(db, course, user) for course in courses]


def create_course(db: Session, user: User, payload: CourseCreate) -> CourseOut:
    if user.role != "admin":
        raise PermissionDenied()
    teacher = user_repository.get_teacher(db, payload.teacher_id)
    if teacher is None:
        raise NotFound("教师不存在")
    course = course_repository.create_course(
        db,
        Course(
            name=payload.name,
            description=payload.description,
            teacher_id=payload.teacher_id,
            credit=payload.credit,
            capacity=payload.capacity,
        ),
    )
    _replace_schedules(course, payload.schedules)
    log_repository.add_log(db, user.id, "course.create", f"新增课程：{course.name}")
    db.commit()
    course = course_repository.get_course(db, course.id) or course
    return _course_out(db, course, user)


def update_course(db: Session, user: User, course_id: int, payload: CourseUpdate) -> CourseOut:
    if user.role != "admin":
        raise PermissionDenied()
    course = course_repository.get_course(db, course_id)
    if course is None:
        raise NotFound("课程不存在")
    if user_repository.get_teacher(db, payload.teacher_id) is None:
        raise NotFound("教师不存在")
    course.name = payload.name
    course.description = payload.description
    course.teacher_id = payload.teacher_id
    course.credit = payload.credit
    course.capacity = payload.capacity
    _replace_schedules(course, payload.schedules)
    log_repository.add_log(db, user.id, "course.update", f"修改课程：{course.name}")
    db.commit()
    course = course_repository.get_course(db, course_id) or course
    return _course_out(db, course, user)


def delete_course(db: Session, user: User, course_id: int) -> None:
    if user.role != "admin":
        raise PermissionDenied()
    course = course_repository.get_course(db, course_id)
    if course is None:
        raise NotFound("课程不存在")
    log_repository.add_log(db, user.id, "course.delete", f"删除课程：{course.name}")
    course_repository.delete_course(db, course)
    db.commit()


def enroll_course(db: Session, user: User, course_id: int) -> CourseOut:
    student_id = _current_student_id(user)
    _ensure_enrollment_open(db)
    course = course_repository.get_course(db, course_id)
    if course is None:
        raise NotFound("课程不存在")
    if course_repository.get_enrollment(db, student_id, course_id):
        raise AppError("已选该课程")
    if course_repository.count_course_enrollments(db, course_id) >= course.capacity:
        raise AppError("课程容量已满")
    conflict_message = _has_schedule_conflict(db, student_id, course)
    if conflict_message:
        raise AppError(conflict_message)
    course_repository.create_enrollment(db, Enrollment(student_id=student_id, course_id=course_id))
    log_repository.add_log(db, user.id, "course.enroll", f"选择课程：{course.name}")
    db.commit()
    course = course_repository.get_course(db, course_id) or course
    return _course_out(db, course, user)


def cancel_enrollment(db: Session, user: User, course_id: int) -> None:
    if user.role != "admin":
        raise PermissionDenied("学生不能自行退课，请联系管理员处理")
    raise AppError("请指定学生后由管理员退课")


def admin_remove_enrollment(db: Session, user: User, course_id: int, student_id: int) -> None:
    if user.role != "admin":
        raise PermissionDenied()
    enrollment = course_repository.get_enrollment(db, student_id, course_id)
    if enrollment is None:
        raise NotFound("选课记录不存在")
    course_repository.delete_enrollment(db, enrollment)
    log_repository.add_log(db, user.id, "course.admin_drop", f"管理员退课：course={course_id}, student={student_id}")
    db.commit()


def list_course_students(db: Session, user: User, course_id: int) -> list[CourseStudentOut]:
    course = course_repository.get_course(db, course_id)
    if course is None:
        raise NotFound("课程不存在")
    if user.role == "teacher" and course.teacher_id != _current_teacher_id(user):
        raise PermissionDenied("只能查看本人课程的学生")
    if user.role not in {"teacher", "admin"}:
        raise PermissionDenied()
    enrollments = course_repository.list_course_students(db, course_id)
    return [
        CourseStudentOut(
            student_id=item.student.id,
            student_no=item.student.student_no,
            real_name=item.student.user.real_name,
            major=item.student.major,
            class_name=item.student.class_name,
            selected_at=item.selected_at,
        )
        for item in enrollments
    ]


def get_enrollment_setting(db: Session, user: User) -> EnrollmentSettingOut:
    setting = _get_or_create_setting(db)
    return EnrollmentSettingOut(
        id=setting.id,
        term=setting.term,
        is_open=setting.is_open,
        start_time=setting.start_time,
        end_time=setting.end_time,
        current_week=setting.current_week,
    )


def update_enrollment_setting(db: Session, user: User, payload: EnrollmentSettingUpdate) -> EnrollmentSettingOut:
    if user.role != "admin":
        raise PermissionDenied()
    if payload.end_time <= payload.start_time:
        raise AppError("选课结束时间必须晚于开始时间")
    setting = _get_or_create_setting(db)
    setting.term = payload.term
    setting.is_open = payload.is_open
    setting.start_time = payload.start_time
    setting.end_time = payload.end_time
    setting.current_week = payload.current_week
    log_repository.add_log(db, user.id, "enrollment.setting", "更新选课开放设置")
    db.commit()
    db.refresh(setting)
    return EnrollmentSettingOut(
        id=setting.id,
        term=setting.term,
        is_open=setting.is_open,
        start_time=setting.start_time,
        end_time=setting.end_time,
        current_week=setting.current_week,
    )


def get_weekly_schedule(db: Session, user: User, week: int | None = None, term: str | None = None) -> list[WeeklyScheduleItem]:
    setting = _get_or_create_setting(db)
    current_week = week or setting.current_week
    current_term = term or setting.term
    courses = course_repository.list_courses(db)
    if user.role == "student":
        student_id = _current_student_id(user)
        selected_ids = {item.course_id for item in course_repository.list_student_enrollments(db, student_id)}
        courses = [course for course in courses if course.id in selected_ids]
    elif user.role == "teacher":
        teacher_id = _current_teacher_id(user)
        courses = [course for course in courses if course.teacher_id == teacher_id]
    elif user.role != "admin":
        raise PermissionDenied()

    result: list[WeeklyScheduleItem] = []
    for course in courses:
        for schedule in course.schedules:
            if schedule.term != current_term or current_week not in _weeks_to_set(schedule.weeks):
                continue
            start_section, end_section, start_time, end_time = _section_slot(schedule.start_section)
            result.append(
                WeeklyScheduleItem(
                    course_id=course.id,
                    course_name=course.name,
                    teacher_name=course.teacher.user.real_name,
                    weekday=schedule.weekday,
                    start_section=start_section,
                    end_section=end_section,
                    start_time=start_time,
                    end_time=end_time,
                    classroom=schedule.classroom,
                    weeks=schedule.weeks,
                    term=schedule.term,
                )
            )
    return sorted(result, key=lambda item: (item.weekday, item.start_section))
