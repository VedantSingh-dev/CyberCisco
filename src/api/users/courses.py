from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.utils.auth_deps import get_current_user
from src.schemas.course_schemas import (
    CourseDetailResponse,
    CourseListResponse,
    EnrolledCourseResponse,
    LectureDetailResponse,
    LecturePublicResponse,
)
from src.database.dbConfig import get_db
from src.modals.courses_models import Course
from src.modals.user_models import User

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=list[CourseListResponse])
def get_all_courses(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
):
    """Browse public courses catalog with total lecture count."""
    courses = db.query(Course).offset(skip).limit(limit).all()

    result = []
    for course in courses:
        data = CourseListResponse.model_validate(course)
        data.total_lectures = len(course.lectures)
        result.append(data)

    return result


@router.get("/my-courses", response_model=list[EnrolledCourseResponse])
def get_my_courses(current_user: User = Depends(get_current_user)):
    """Fetch courses the logged-in user is currently enrolled in."""
    return current_user.enrollments


@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course_details(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user),
):
    """View single course.

    Hides YouTube URLs unless the user is enrolled.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    is_enrolled = False
    if current_user:
        is_enrolled = any(c.id == course_id for c in current_user.enrollments)
    
    sorted_lectures = sorted(course.lectures, key=lambda x: x.order)

    if is_enrolled or current_user.role == 'admin':
        lectures_data = [
            LectureDetailResponse.model_validate(lec)
            for lec in sorted_lectures
        ]
    else:
        lectures_data = [
            LecturePublicResponse.model_validate(lec)
            for lec in sorted_lectures
        ]

    return CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        image_url=course.image_url,
        price=course.price,
        created_at=course.created_at,
        total_lectures=len(sorted_lectures),
        is_enrolled=is_enrolled,
        lectures=lectures_data,
    )