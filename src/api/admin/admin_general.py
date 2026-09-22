from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.schemas.admin_general_schemas import GalleryImageCreate, GalleryImageUpdate
from src.utils.admin_deps import require_admin
from src.schemas.general_schemas import GalleryImageResponse
from src.database.dbConfig import get_db
from src.modals.general_models import GalleryImage

router = APIRouter(
    prefix="/admin/general",
    tags=["Admin - General Gallery"],
    dependencies=[Depends(require_admin)], 
)


@router.post(
    "/gallery",
    response_model=GalleryImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_gallery_image(
    payload: GalleryImageCreate, db: Session = Depends(get_db)
):
    """Add a new image to the gallery (Collaborations, MOUs, or General)."""
    new_image = GalleryImage(
        title=payload.title,
        image_url=payload.image_url,
        type=payload.type,
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    return new_image


@router.patch("/gallery/{image_id}", response_model=GalleryImageResponse)
def update_gallery_image(
    image_id: int, payload: GalleryImageUpdate, db: Session = Depends(get_db)
):
    """Update an existing gallery image's title, URL, or category type."""
    image = db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery image not found",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(image, key, value)

    db.commit()
    db.refresh(image)
    return image


@router.delete("/gallery/{image_id}", status_code=status.HTTP_200_OK)
def delete_gallery_image(image_id: int, db: Session = Depends(get_db)):
    """Delete a gallery image by ID."""
    image = db.query(GalleryImage).filter(GalleryImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery image not found",
        )

    db.delete(image)
    db.commit()
    return {"message": f"Gallery image '{image.title}' deleted successfully"}