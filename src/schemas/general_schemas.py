from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.modals.general_models import ImageType


class GalleryImageResponse(BaseModel):
    id: int
    title: str
    image_url: str
    type: ImageType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)