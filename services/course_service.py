from sqlalchemy.orm import Session

from db.models import Course
from schemas.college_schema import CourseSchema


def create_course_service(course: CourseSchema, db: Session):
    existing_course = db.query(Course).filter(Course.name == course.name).first()

    if existing_course:
        return None

    new_course = Course(
        name=course.name,
        description=course.description,
        duration=course.duration,
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


def get_courses_service(db: Session):
    return db.query(Course).all()


def get_paginated_courses_service(page: int, page_size: int, db: Session):
    total_items = db.query(Course).count()
    offset = (page - 1) * page_size
    courses = db.query(Course).offset(offset).limit(page_size).all()

    return {
        "items": courses,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": (total_items + page_size - 1) // page_size,
    }


def update_course_service(course_id: int, course: CourseSchema, db: Session):
    db_course = db.query(Course).filter(Course.id == course_id).first()

    if db_course is None:
        return None

    duplicate_course = (
        db.query(Course)
        .filter(Course.name == course.name, Course.id != course_id)
        .first()
    )

    if duplicate_course:
        return "duplicate"

    db_course.name = course.name
    db_course.description = course.description
    db_course.duration = course.duration

    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course_service(course_id: int, db: Session):
    db_course = db.query(Course).filter(Course.id == course_id).first()

    if db_course is None:
        return None

    db.delete(db_course)
    db.commit()
    return db_course
