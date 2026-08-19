"""User registration endpoints for Farmers, Customers, and DeliveryMen."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/farmers",
    response_model=schemas.FarmerResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_farmer(payload: schemas.FarmerCreate, db: Session = Depends(get_db)):
    """Register a new Farmer account, optionally linked to an existing Shop."""
    if payload.ShopID is not None and not db.get(models.Shop, payload.ShopID):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shop not found.")

    farmer = models.Farmer(
        Name=payload.Name,
        Email=payload.Email,
        password=hash_password(payload.password),
        Address=payload.Address,
        Phone=payload.Phone,
        Bio=payload.Bio,
        ShopID=payload.ShopID,
    )
    db.add(farmer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A farmer with this email already exists.",
        )
    db.refresh(farmer)
    return farmer


@router.post(
    "/customers",
    response_model=schemas.CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Register a new Customer account."""
    customer = models.Customer(
        Name=payload.Name,
        Email=payload.Email,
        password=hash_password(payload.password),
        Address=payload.Address,
        Phone=payload.Phone,
    )
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists.",
        )
    db.refresh(customer)
    return customer


@router.post(
    "/delivery-men",
    response_model=schemas.DeliveryManResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_delivery_man(payload: schemas.DeliveryManCreate, db: Session = Depends(get_db)):
    """Register a new DeliveryMan account. Review/TotalDeliveries start at zero."""
    delivery_man = models.DeliveryMan(
        Name=payload.Name,
        Email=payload.Email,
        password=hash_password(payload.password),
        Address=payload.Address,
        Phone=payload.Phone,
        VehicleNo=payload.VehicleNo,
        Review=0.0,
        TotalDeliveries=0,
    )
    db.add(delivery_man)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A delivery person with this email already exists.",
        )
    db.refresh(delivery_man)
    return delivery_man
