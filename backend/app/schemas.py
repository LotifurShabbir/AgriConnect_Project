"""
Pydantic schemas for request validation and response serialization.

Convention: `<Entity>Base` holds shared fields, `<Entity>Create` is the
request body accepted by POST endpoints, and `<Entity>Response` is what's
returned to clients (built from ORM objects via `from_attributes=True`).
Passwords are accepted in Create schemas but deliberately excluded from
Response schemas — they are hashed before storage (see security.py) and
must never be echoed back to a client.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# --------------------------------------------------------------------------
# Farmer
# --------------------------------------------------------------------------
class FarmerBase(BaseModel):
    Name: str
    Email: EmailStr
    Address: Optional[str] = None
    Phone: Optional[str] = None
    Bio: Optional[str] = None
    ShopID: Optional[int] = None


class FarmerCreate(FarmerBase):
    password: str


class FarmerResponse(FarmerBase):
    model_config = ConfigDict(from_attributes=True)

    UserFarmerID: int


# --------------------------------------------------------------------------
# Customer
# --------------------------------------------------------------------------
class CustomerBase(BaseModel):
    Name: str
    Email: EmailStr
    Address: Optional[str] = None
    Phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    password: str


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    UserCustomerID: int


# --------------------------------------------------------------------------
# DeliveryMan
# --------------------------------------------------------------------------
class DeliveryManBase(BaseModel):
    Name: str
    Email: EmailStr
    Address: Optional[str] = None
    Phone: Optional[str] = None
    VehicleNo: Optional[str] = None


class DeliveryManCreate(DeliveryManBase):
    password: str


class DeliveryManResponse(DeliveryManBase):
    model_config = ConfigDict(from_attributes=True)

    UserDeliveryManID: int
    Review: float
    TotalDeliveries: int


# --------------------------------------------------------------------------
# Shop
# --------------------------------------------------------------------------
class ShopBase(BaseModel):
    ShopName: str


class ShopCreate(ShopBase):
    Review: float = 0.0
    # Not a Shop column — if given, the router links this farmer to the new
    # shop by setting Farmer.ShopID, per the schema's existing FK.
    FarmerID: Optional[int] = None


class ShopResponse(ShopBase):
    model_config = ConfigDict(from_attributes=True)

    ShopID: int
    Review: float


# --------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------
# The Items table stores category as three booleans (FruitsAndVegetables,
# Grains, Meat). The API surface instead exposes a single `Category` field
# for a saner client experience — routers/shops.py converts between the two.
CATEGORY_LABELS = ("Fruits & Vegetables", "Grains", "Meat")


class ItemBase(BaseModel):
    Name: str
    Price: float
    Stock: int = 0


class ItemCreate(ItemBase):
    Category: str  # one of CATEGORY_LABELS


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    ItemID: int
    ShopID: int
    OrderID: Optional[int] = None
    Category: str  # derived from the Items model's `Category` property


# --------------------------------------------------------------------------
# Order
# --------------------------------------------------------------------------
class OrderCreate(BaseModel):
    """Request body for placing an order.

    `item_ids` are the ItemID's of existing shop inventory rows being
    purchased. TotalAmount, dates, invoice ID, and statuses are computed
    server-side (see routers/orders.py) rather than accepted from the client.
    """

    UserCustomerID: int
    PaymentMethod: str
    CouponCode: Optional[str] = None
    item_ids: List[int]


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    OrderID: int
    TotalAmount: float
    CouponCode: Optional[str] = None
    InvoiceDate: Optional[datetime] = None
    InvoiceID: Optional[str] = None
    PaymentStatus: Optional[str] = None
    OrderDate: Optional[datetime] = None
    PaymentMethod: Optional[str] = None
    Status: Optional[str] = None
    UserCustomerID: int


# --------------------------------------------------------------------------
# PreOrderRequest
# --------------------------------------------------------------------------
class PreOrderRequestBase(BaseModel):
    ProposedPrice: float
    Quantity: int
    UserFarmerID: int
    UserCustomerID: int
    ItemID: int


class PreOrderRequestCreate(PreOrderRequestBase):
    pass


class PreOrderRequestResponse(PreOrderRequestBase):
    model_config = ConfigDict(from_attributes=True)

    PreOrderID: int
    Status: Optional[str] = None
    RequestDate: Optional[datetime] = None


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserSession(BaseModel):
    """Returned on successful login.

    Farmer, Customer, and DeliveryMan are separate tables with no shared
    primary key space, so `id` is only unique within `role` — always treat
    (role, id) as the identity, not `id` alone.
    """

    id: int
    name: str
    email: EmailStr
    role: str  # "Admin" | "Farmer" | "Customer" | "DeliveryMan"
    address: Optional[str] = None
    phone: Optional[str] = None
    shop_id: Optional[int] = None
