from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.college_schema import (
    EnrollmentResponse,
    EnrollmentSchema,
    PaginatedStudentsResponse,
    StudentResponse,
    StudentSchema,
)
from services.auth_service import get_current_user, require_admin
from services.student_service import (
    create_student_service,
    delete_student_service,
    enroll_student_service,
    get_enrollments_service,
    get_paginated_students_service,
    get_students_service,
    update_student_service,
)

router = APIRouter()


@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    result = create_student_service(student, db)

    if result is None:
        raise HTTPException(status_code=409, detail="Student email already exists")

    return result


@router.get("/students", response_model=list[StudentResponse])
def get_students(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_students_service(db)


@router.get("/admin/students", response_model=PaginatedStudentsResponse)
def get_paginated_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return get_paginated_students_service(page, page_size, db)


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    result = update_student_service(student_id, student, db)

    if result is None:
        raise HTTPException(status_code=404, detail="Student not found")

    if result == "duplicate":
        raise HTTPException(status_code=409, detail="Student email already exists")

    return result


@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    result = delete_student_service(student_id, db)

    if result is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}


@router.post(
    "/enrollments",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def enroll_student(
    enrollment: EnrollmentSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    result = enroll_student_service(enrollment, db)

    if result is None:
        raise HTTPException(status_code=404, detail="Student or course not found")

    return result


@router.get("/enrollments", response_model=list[EnrollmentResponse])
def get_enrollments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_enrollments_service(db)
