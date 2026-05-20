from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.college_schema import CourseResponse, CourseSchema
from services.auth_service import get_current_user, require_admin
from services.course_service import (
    create_course_service,
    delete_course_service,
    get_courses_service,
    update_course_service,
)

router = APIRouter()


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    result = create_course_service(course, db)

    if result is None:
        raise HTTPException(status_code=409, detail="Course name already exists")

    return result


@router.get("/courses", response_model=list[CourseResponse])
def get_courses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_courses_service(db)


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course: CourseSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    result = update_course_service(course_id, course, db)

    if result is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if result == "duplicate":
        raise HTTPException(status_code=409, detail="Course name already exists")

    return result


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    result = delete_course_service(course_id, db)

    if result is None:
        raise HTTPException(status_code=404, detail="Course not found")

    return {"message": "Course deleted successfully"}
