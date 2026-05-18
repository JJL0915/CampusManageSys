from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserProfile(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    profile_id: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

