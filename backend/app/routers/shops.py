"""Shop creation and shop-inventory (Items) endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/shops", tags=["Shops"])

# Maps the API's single `Category` field to the Items table's three
# boolean columns (see schemas.CATEGORY_LABELS / models.Items.Category).
_CATEGORY_TO_FLAGS = {
    "Fruits & Vegetables": {"FruitsAndVegetables": True, "Grains": False, "Meat": False},
    "Grains": {"FruitsAndVegetables": False, "Grains": True, "Meat": False},
    "Meat": {"FruitsAndVegetables": False, "Grains": False, "Meat": True},
}


@router.post("", response_model=schemas.ShopResponse, status_code=status.HTTP_201_CREATED)
def create_shop(payload: schemas.ShopCreate, db: Session = Depends(get_db)):
    """Create a new Shop. If FarmerID is given, that farmer is linked to
    the new shop via the existing Farmer.ShopID foreign key."""
    farmer = None
    if payload.FarmerID is not None:
        farmer = db.get(models.Farmer, payload.FarmerID)
        if not farmer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found.")

    shop = models.Shop(ShopName=payload.ShopName, Review=payload.Review)
    db.add(shop)
    db.flush()  # assign shop.ShopID before linking the farmer to it

    if farmer:
        farmer.ShopID = shop.ShopID

    db.commit()
    db.refresh(shop)
    return shop


@router.get("", response_model=List[schemas.ShopResponse])
def list_shops(db: Session = Depends(get_db)):
    """List all shops."""
    return db.query(models.Shop).all()


@router.get("/{shop_id}", response_model=schemas.ShopResponse)
def get_shop(shop_id: int, db: Session = Depends(get_db)):
    """Retrieve a single shop by ID."""
    shop = db.get(models.Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found.")
    return shop


@router.post(
    "/{shop_id}/items",
    response_model=schemas.ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_item_to_shop(shop_id: int, payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Add a new catalog item to a shop's inventory."""
    shop = db.get(models.Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found.")

    flags = _CATEGORY_TO_FLAGS.get(payload.Category)
    if flags is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category must be one of: {', '.join(schemas.CATEGORY_LABELS)}",
        )

    item = models.Items(
        Name=payload.Name,
        Price=payload.Price,
        Stock=payload.Stock,
        ShopID=shop_id,
        **flags,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{shop_id}/items", response_model=List[schemas.ItemResponse])
def list_shop_items(shop_id: int, db: Session = Depends(get_db)):
    """List all items belonging to a shop."""
    if not db.get(models.Shop, shop_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found.")
    return db.query(models.Items).filter(models.Items.ShopID == shop_id).all()
