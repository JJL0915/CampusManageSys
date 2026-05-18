from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import secrets

from app.core.config import settings
from app.core.exceptions import AppError


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${base64.urlsafe_b64encode(digest).decode('utf-8')}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, encoded_digest = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    expected = base64.urlsafe_b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, encoded_digest)


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")


def _b64decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def create_access_token(subject: str, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "role": role, "exp": int(expires_at.timestamp())}
    signing_input = ".".join(
        [
            _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, str]:
    try:
        header, body, signature = token.split(".", 2)
        signing_input = f"{header}.{body}"
        expected = hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64encode(expected), signature):
            raise AppError("登录凭证无效", code=401, status_code=401)
        token_header = json.loads(_b64decode(header))
        if token_header.get("alg") != "HS256":
            raise AppError("登录凭证无效", code=401, status_code=401)
        payload = json.loads(_b64decode(body))
    except (ValueError, json.JSONDecodeError):
        raise AppError("登录凭证无效", code=401, status_code=401) from None
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise AppError("登录已过期", code=401, status_code=401)
    return payload
