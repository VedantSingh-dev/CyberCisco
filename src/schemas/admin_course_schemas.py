from typing import Optional
from pydantic import BaseModel, ConfigDict


class LectureCreate(BaseModel):
    title: str
    youtube_url: str
    order: int = 1
    duration_minutes: Optional[int] = None


class LectureUpdate(BaseModel):
    title: Optional[str] = None
    youtube_url: Optional[str] = None
    order: Optional[int] = None
    duration_minutes: Optional[int] = None


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: float = 0.0
    exam_link: Optional[str] = None


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None
    exam_link: Optional[str] = None