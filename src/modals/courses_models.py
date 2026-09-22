from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy import Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.dbConfig import Base

# Association Table for Many-to-Many relationship between Users (Students) and Courses
course_enrollments = Table(
    "course_enrollments",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
    Column("enrolled_at", String, default=datetime.utcnow().isoformat),
)


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    exam_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Relationships
    lectures: Mapped[list["Lecture"]] = relationship(
        "Lecture", back_populates="course", cascade="all, delete-orphan"
    )
    students: Mapped[list["User"]] = relationship(
        "User", secondary=course_enrollments, back_populates="enrollments"
    )


class Lecture(Base):
    __tablename__ = "lectures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    # Store YouTube unlisted/private link or video ID here
    youtube_url: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="lectures")