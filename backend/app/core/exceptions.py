from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, code: int = 400, status_code: int = 400) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code


class PermissionDenied(AppError):
    def __init__(self, message: str = "无权执行该操作") -> None:
        super().__init__(message=message, code=403, status_code=403)


class NotFound(AppError):
    def __init__(self, message: str = "资源不存在") -> None:
        super().__init__(message=message, code=404, status_code=404)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


async def generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": f"服务器内部错误：{exc}", "data": None},
    )

