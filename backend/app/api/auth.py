from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.responses import success
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth_schema import LoginRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, payload.username, payload.password)
    return success(result.model_dump())


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return success(auth_service.build_user_profile(user).model_dump())

