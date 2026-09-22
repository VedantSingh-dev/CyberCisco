from typing import Optional
from pydantic import BaseModel, HttpUrl
from src.modals.general_models import ImageType


class GalleryImageCreate(BaseModel):
    title: str
    image_url: str
    type: ImageType = ImageType.GENERAL


class GalleryImageUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[ImageType] = None