from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, PermissionDenied
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories import user_repository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError("请先登录", code=401, status_code=401)
    payload = decode_access_token(credentials.credentials)
    user = user_repository.get_user_by_id(db, int(payload["sub"]))
    if user is None or not user.is_active:
        raise AppError("用户不存在或已禁用", code=401, status_code=401)
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise PermissionDenied()
        return user

    return dependency

