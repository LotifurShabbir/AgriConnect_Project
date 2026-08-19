"""Order placement and retrieval endpoints.

Each `Items` row is a single unit of shop inventory (there is no
separate order-line-item table with quantities in the schema), so
"placing an order" means: take a set of not-yet-ordered ItemID's,
attach them to a new Order, and total their price.
"""

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Place an order for one or more existing, unordered shop items."""
    if not db.get(models.Customer, payload.UserCustomerID):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    if not payload.item_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="item_ids must not be empty.")

    items = db.query(models.Items).filter(models.Items.ItemID.in_(payload.item_ids)).all()
    found_ids = {item.ItemID for item in items}
    missing_ids = set(payload.item_ids) - found_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item(s) not found: {sorted(missing_ids)}",
        )

    already_ordered_ids = [item.ItemID for item in items if item.OrderID is not None]
    if already_ordered_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item(s) already attached to another order: {already_ordered_ids}",
        )

    now = datetime.now(timezone.utc)
    order = models.Order(
        TotalAmount=sum(item.Price for item in items),
        CouponCode=payload.CouponCode,
        InvoiceDate=now,
        InvoiceID=str(uuid.uuid4()),
        PaymentStatus="Unpaid",
        OrderDate=now,
        PaymentMethod=payload.PaymentMethod,
        Status="Pending",
        UserCustomerID=payload.UserCustomerID,
    )
    db.add(order)
    db.flush()  # assign order.OrderID before linking items to it

    for item in items:
        item.OrderID = order.OrderID

    db.commit()
    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Retrieve a single order by ID."""
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    return order


@router.get("/customer/{customer_id}", response_model=List[schemas.OrderResponse])
def list_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    """List all orders placed by a given customer, most recent first."""
    if not db.get(models.Customer, customer_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return (
        db.query(models.Order)
        .filter(models.Order.UserCustomerID == customer_id)
        .order_by(models.Order.OrderDate.desc())
        .all()
    )
