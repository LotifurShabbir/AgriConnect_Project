"""Login endpoint.

There is no single `users` table in the schema — Farmer, Customer, and
DeliveryMan are separate tables — so login tries each in turn and reports
back which one matched via `role`. A hardcoded admin account is checked
first since there's no `Admin` table to back it.
"""

import hmac

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..security import verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"


@router.post("/login", response_model=schemas.UserSession)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate against the hardcoded admin account, then Farmer,
    Customer, and DeliveryMan tables, in that order."""

    if payload.email == ADMIN_EMAIL and hmac.compare_digest(payload.password, ADMIN_PASSWORD):
        return schemas.UserSession(id=0, name="Administrator", email=ADMIN_EMAIL, role="Admin")

    farmer = db.query(models.Farmer).filter(models.Farmer.Email == payload.email).first()
    if farmer and verify_password(payload.password, farmer.password):
        return schemas.UserSession(
            id=farmer.UserFarmerID,
            name=farmer.Name,
            email=farmer.Email,
            role="Farmer",
            address=farmer.Address,
            phone=farmer.Phone,
            shop_id=farmer.ShopID,
        )

    customer = db.query(models.Customer).filter(models.Customer.Email == payload.email).first()
    if customer and verify_password(payload.password, customer.password):
        return schemas.UserSession(
            id=customer.UserCustomerID,
            name=customer.Name,
            email=customer.Email,
            role="Customer",
            address=customer.Address,
            phone=customer.Phone,
        )

    delivery_man = db.query(models.DeliveryMan).filter(models.DeliveryMan.Email == payload.email).first()
    if delivery_man and verify_password(payload.password, delivery_man.password):
        return schemas.UserSession(
            id=delivery_man.UserDeliveryManID,
            name=delivery_man.Name,
            email=delivery_man.Email,
            role="DeliveryMan",
            address=delivery_man.Address,
            phone=delivery_man.Phone,
        )

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
