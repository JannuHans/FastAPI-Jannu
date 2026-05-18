from fastapi import FastAPI

from db.database import engine
from db.models import Base
from routers.course_router import router as course_router
from routers.student_router import router as student_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="College Management API")

app.include_router(student_router)
app.include_router(course_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to College Management API",
        "docs": "/docs",
    }
