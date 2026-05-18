from datetime import datetime

from pydantic import BaseModel


class AttachmentOut(BaseModel):
    id: int
    original_name: str
    url: str
    content_type: str | None
    size: int
    is_image: bool
    created_at: datetime
