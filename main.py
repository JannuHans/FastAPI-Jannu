import time

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from db.database import engine
from db.models import Base
from routers.auth_router import router as auth_router
from routers.course_router import router as course_router
from routers.student_router import router as student_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="College Management API")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    print(f"Incoming request: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    print(
        f"Outgoing response: {response.status_code} "
        f"completed in {process_time:.4f} seconds"
    )

    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Invalid request data",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    print(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
        },
    )


app.include_router(auth_router)
app.include_router(student_router)
app.include_router(course_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to College Management API",
        "docs": "/docs",
    }
