import enum
from datetime import datetime
from sqlalchemy import Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from src.database.dbConfig import Base


class ImageType(str, enum.Enum):
    COLLABORATIONS = "collaborations"
    MOUS = "MOUs"
    GENERAL = "general"


class GalleryImage(Base):
    __tablename__ = "gallery_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[ImageType] = mapped_column(
        Enum(ImageType), default=ImageType.GENERAL, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())