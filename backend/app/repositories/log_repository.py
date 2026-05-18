from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.log import OperationLog


def add_log(db: Session, user_id: int | None, action: str, detail: str | None = None) -> OperationLog:
    log = OperationLog(user_id=user_id, action=action, detail=detail)
    db.add(log)
    db.flush()
    return log


def list_recent_logs(db: Session, limit: int = 8) -> list[OperationLog]:
    return list(db.scalars(select(OperationLog).order_by(OperationLog.created_at.desc()).limit(limit)).all())

