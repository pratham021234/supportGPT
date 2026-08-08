from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

class BaseAppException(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST", data: dict = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data or {}

class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Could not validate credentials", data: dict = None):
        super().__init__(message=message, status_code=401, error_code="UNAUTHORIZED", data=data)

class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "Not enough permissions", data: dict = None):
        super().__init__(message=message, status_code=403, error_code="FORBIDDEN", data=data)

class NotFoundException(BaseAppException):
    def __init__(self, message: str = "Resource not found", data: dict = None):
        super().__init__(message=message, status_code=404, error_code="NOT_FOUND", data=data)

class BadRequestException(BaseAppException):
    def __init__(self, message: str = "Bad request", data: dict = None):
        super().__init__(message=message, status_code=400, error_code="BAD_REQUEST", data=data)

def setup_exception_handlers(app):
    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code,
                "errors": exc.data
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error_code": "HTTP_ERROR",
                "errors": {}
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Validation Error",
                "error_code": "UNPROCESSABLE_ENTITY",
                "errors": exc.errors()
            },
        )
