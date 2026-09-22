import enum
from datetime import datetime
from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.dbConfig import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.STUDENT, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="user"
    )
    enrollments: Mapped[list["Course"]] = relationship(
        "Course", secondary="course_enrollments", back_populates="students"
    )