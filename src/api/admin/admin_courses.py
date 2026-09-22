from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas.admin_course_schemas import (
    CourseCreate,
    CourseUpdate,
    LectureCreate,
    LectureUpdate,
)
from src.schemas.course_schemas import CourseDetailResponse
from src.utils.admin_deps import require_admin
from src.database.dbConfig import get_db
from src.modals.courses_models import Course, Lecture
from src.modals.user_models import User

router = APIRouter(
    prefix="/admin/courses",
    tags=["Admin - Courses"],
    dependencies=[Depends(require_admin)],  
)


# --- COURSE ENDPOINTS ---


@router.post(
    "", response_model=CourseDetailResponse, status_code=status.HTTP_201_CREATED
)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    """Add a new course."""
    new_course = Course(
        title=payload.title,
        description=payload.description,
        image_url=payload.image_url,
        price=payload.price,
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.patch("/{course_id}", response_model=CourseDetailResponse)
def update_course(
    course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)
):
    """Update course information dynamically."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_200_OK)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete an existing course and its lectures."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    db.delete(course)
    db.commit()
    return {"message": f"Course '{course.title}' deleted successfully"}


# --- LECTURE ENDPOINTS ---


@router.post("/{course_id}/lectures", status_code=status.HTTP_201_CREATED)
def add_lecture_to_course(
    course_id: int, payload: LectureCreate, db: Session = Depends(get_db)
):
    """Add a private YouTube lecture to a course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    lecture = Lecture(
        course_id=course.id,
        title=payload.title,
        youtube_url=payload.youtube_url,
        order=payload.order,
        duration_minutes=payload.duration_minutes,
    )
    db.add(lecture)
    db.commit()
    db.refresh(lecture)
    return lecture


@router.delete("/lectures/{lecture_id}", status_code=status.HTTP_200_OK)
def delete_lecture(lecture_id: int, db: Session = Depends(get_db)):
    """Delete a specific lecture from a course."""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lecture not found"
        )

    db.delete(lecture)
    db.commit()
    return {"message": "Lecture deleted successfully"}