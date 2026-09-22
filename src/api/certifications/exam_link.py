from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.utils.auth_utils import send_exam_link_email
from src.utils.auth_deps import get_current_user
from src.database.dbConfig import get_db
from src.modals.courses_models import Course
from src.modals.user_models import User

router = APIRouter(prefix="/exams", tags=["Exams & Certification"])


@router.post("/request-link/{course_id}")
async def request_exam_link(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Protected endpoint: Verify user enrollment and email the course exam link."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    is_enrolled = any(c.id == course_id for c in current_user.enrollments)
    if not is_enrolled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to request an exam link.",
        )

    if not course.exam_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No exam link is currently available for this course. Please contact support.",
        )

    await send_exam_link_email(
        email=current_user.email,
        course_title=course.title,
        exam_link=course.exam_link,
    )

    return {
        "message": f"Exam link for '{course.title}' sent successfully to {current_user.email}."
    }