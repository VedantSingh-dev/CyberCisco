from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.schemas.general_schemas import GalleryImageResponse
from src.database.dbConfig import get_db
from src.modals.general_models import GalleryImage, ImageType

router = APIRouter(prefix="/general", tags=["General & Public"])


@router.get("/gallery", response_model=list[GalleryImageResponse])
def get_gallery_images(
    image_type: Optional[ImageType] = Query(
        None,
        alias="type",
        description="Filter by image type: collaborations, MOUs, or general",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Unprotected endpoint returning image URLs, titles, and types."""
    query = db.query(GalleryImage)

    if image_type:
        query = query.filter(GalleryImage.type == image_type)

    images = query.offset(skip).limit(limit).all()
    return images