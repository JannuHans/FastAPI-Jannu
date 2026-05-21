from sqlalchemy.orm import Session

from db.models import Course, Student
from schemas.college_schema import EnrollmentSchema, StudentSchema


def create_student_service(student: StudentSchema, db: Session):
    existing_student = db.query(Student).filter(Student.email == student.email).first()

    if existing_student:
        return None

    new_student = Student(
        name=student.name,
        email=student.email,
        age=student.age,
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


def get_students_service(db: Session):
    return db.query(Student).all()


def get_paginated_students_service(page: int, page_size: int, db: Session):
    total_items = db.query(Student).count()
    offset = (page - 1) * page_size
    students = db.query(Student).offset(offset).limit(page_size).all()

    return {
        "items": students,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": (total_items + page_size - 1) // page_size,
    }


def update_student_service(student_id: int, student: StudentSchema, db: Session):
    db_student = db.query(Student).filter(Student.id == student_id).first()

    if db_student is None:
        return None

    duplicate_student = (
        db.query(Student)
        .filter(Student.email == student.email, Student.id != student_id)
        .first()
    )

    if duplicate_student:
        return "duplicate"

    db_student.name = student.name
    db_student.email = student.email
    db_student.age = student.age

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student_service(student_id: int, db: Session):
    db_student = db.query(Student).filter(Student.id == student_id).first()

    if db_student is None:
        return None

    db.delete(db_student)
    db.commit()
    return db_student


def enroll_student_service(enrollment: EnrollmentSchema, db: Session):
    student = db.query(Student).filter(Student.id == enrollment.student_id).first()
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()

    if student is None or course is None:
        return None

    if course not in student.courses:
        student.courses.append(course)
        db.commit()
        db.refresh(student)

    return {
        "student_id": student.id,
        "course_ids": [course.id for course in student.courses],
    }


def get_enrollments_service(db: Session):
    students = db.query(Student).all()

    result = []
    for student in students:
        result.append(
            {
                "student_id": student.id,
                "course_ids": [course.id for course in student.courses],
            }
        )

    return result
