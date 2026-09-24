from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LecturePublicResponse(BaseModel):
    id: int
    title: str
    order: int
    duration_minutes: int | None

    model_config = ConfigDict(from_attributes=True)


class LectureDetailResponse(LecturePublicResponse):
    youtube_url: str  # Only visible to enrolled users


class CourseListResponse(BaseModel):
    id: int
    title: str
    description: str | None
    image_url: str | None
    price: float
    created_at: datetime
    total_lectures: int 

    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(CourseListResponse):
    is_enrolled: bool = False
    lectures: list[LecturePublicResponse] | list[LectureDetailResponse]


class EnrolledCourseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    image_url: str | None
    price: float

    model_config = ConfigDict(from_attributes=True)