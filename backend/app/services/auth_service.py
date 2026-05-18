from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth_schema import TokenResponse, UserProfile


def build_user_profile(user: User) -> UserProfile:
    profile_id = None
    if user.role == "student" and user.student_profile:
        profile_id = user.student_profile.id
    if user.role == "teacher" and user.teacher_profile:
        profile_id = user.teacher_profile.id
    return UserProfile(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        role=user.role,
        profile_id=profile_id,
    )


def login(db: Session, username: str, password: str) -> TokenResponse:
    user = user_repository.get_user_by_username(db, username)
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise AppError("用户名或密码错误", code=401, status_code=401)
    token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(access_token=token, token_type="bearer", user=build_user_profile(user))

