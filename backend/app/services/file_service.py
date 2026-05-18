from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import AppError

MAX_FILE_SIZE = 20 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".zip",
    ".rar",
    ".7z",
    ".txt",
    ".md",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@dataclass(frozen=True)
class StoredUpload:
    original_name: str
    stored_name: str
    file_path: str
    url: str
    content_type: str | None
    size: int
    is_image: bool


def _safe_original_name(filename: str | None) -> str:
    name = Path(filename or "").name.strip()
    return name or "未命名文件"


def save_upload_file(upload: UploadFile, category: str) -> StoredUpload:
    original_name = _safe_original_name(upload.filename)
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise AppError("仅支持 PDF、Word、PPT、Excel、压缩包、文本和常见图片格式")

    target_dir = settings.upload_dir / category
    target_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid4().hex}{suffix}"
    target_path = target_dir / stored_name
    total_size = 0

    try:
        with target_path.open("wb") as output:
            while True:
                chunk = upload.file.read(CHUNK_SIZE)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    raise AppError("单个附件不能超过20MB")
                output.write(chunk)
    except Exception:
        if target_path.exists():
            target_path.unlink()
        raise

    if total_size == 0:
        target_path.unlink(missing_ok=True)
        raise AppError("不能上传空文件")

    relative_path = f"{category}/{stored_name}"
    content_type = upload.content_type
    is_image = bool(content_type and content_type.startswith("image/")) or suffix in IMAGE_EXTENSIONS
    return StoredUpload(
        original_name=original_name,
        stored_name=stored_name,
        file_path=relative_path,
        url=f"/uploads/{relative_path}",
        content_type=content_type,
        size=total_size,
        is_image=is_image,
    )


def save_upload_files(files: list[UploadFile] | None, category: str) -> list[StoredUpload]:
    stored: list[StoredUpload] = []
    for upload in files or []:
        if not upload.filename:
            continue
        stored.append(save_upload_file(upload, category))
    return stored


def delete_stored_file(relative_path: str) -> None:
    upload_root = settings.upload_dir.resolve()
    target_path = (upload_root / relative_path).resolve()
    if target_path == upload_root or upload_root not in target_path.parents:
        return
    target_path.unlink(missing_ok=True)
