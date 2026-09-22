from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.schemas.admin_schemas import CourseStudentsResponse, StudentSummaryResponse
from src.utils.admin_deps import require_admin
from src.database.dbConfig import get_db
from src.modals.courses_models import Course

router = APIRouter(
    prefix="/admin",
    tags=["Admin - Management"],
    dependencies=[Depends(require_admin)],  # Protected via admin check
)


@router.get(
    "/course-students",
    response_model=list[CourseStudentsResponse],
    status_code=status.HTTP_200_OK,
)
def get_registered_students_per_course(
    course_id: Optional[int] = Query(
        None, description="Optional: Filter enrolled students by a specific course ID"
    ),
    db: Session = Depends(get_db),
):
    """Retrieve all registered students for courses.

    Returns data grouped by course.
    """
    query = db.query(Course)

    if course_id:
        query = query.filter(Course.id == course_id)
        course = query.first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
            )
        courses = [course]
    else:
        courses = query.all()

    result = []
    for course in courses:
        # course.enrollments accesses all User objects enrolled via the SQLite association
        student_list = [
            StudentSummaryResponse.model_validate(user)
            for user in course.enrollments
        ]

        result.append(
            CourseStudentsResponse(
                course_id=course.id,
                course_title=course.title,
                total_enrolled_students=len(student_list),
                students=student_list,
            )
        )

    return result