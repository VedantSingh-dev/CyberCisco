from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StudentSummaryResponse(BaseModel):
    id: int
    full_name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseStudentsResponse(BaseModel):
    course_id: int
    course_title: str
    total_enrolled_students: int
    students: list[StudentSummaryResponse]

    model_config = ConfigDict(from_attributes=True)