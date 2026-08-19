"""
SQLAlchemy ORM models for AgriConnect.

These map 1:1 to the fixed relational schema provided for the project.
Field names, primary keys, and foreign keys follow the schema exactly.

Two field names in the source schema are not valid Python/SQL identifiers
and were adjusted to the minimum extent required:
  - Order."Total amount"          -> Order.TotalAmount
  - Items."Fruits & Vegetables"   -> Items.FruitsAndVegetables
No other fields, keys, or relationships were altered.
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Shop(Base):
    """A farmer's shop/storefront."""

    __tablename__ = "shops"

    ShopID = Column(Integer, primary_key=True, index=True)
    ShopName = Column(String(150), nullable=False)
    Review = Column(Float, default=0.0)

    farmers = relationship("Farmer", back_populates="shop")
    items = relationship("Items", back_populates="shop")


class Farmer(Base):
    """A farmer user account, optionally linked to a Shop."""

    __tablename__ = "farmers"

    UserFarmerID = Column(Integer, primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    Address = Column(String(255))
    Phone = Column(String(20))
    Name = Column(String(100), nullable=False)
    Email = Column(String(150), unique=True, index=True, nullable=False)
    Bio = Column(Text)
    ShopID = Column(Integer, ForeignKey("shops.ShopID"))

    shop = relationship("Shop", back_populates="farmers")
    pre_order_requests = relationship("PreOrderRequest", back_populates="farmer")


class Customer(Base):
    """A customer user account."""

    __tablename__ = "customers"

    UserCustomerID = Column(Integer, primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    Address = Column(String(255))
    Phone = Column(String(20))
    Name = Column(String(100), nullable=False)
    Email = Column(String(150), unique=True, index=True, nullable=False)

    orders = relationship("Order", back_populates="customer")
    pre_order_requests = relationship("PreOrderRequest", back_populates="customer")


class DeliveryMan(Base):
    """A delivery person user account."""

    __tablename__ = "delivery_men"

    UserDeliveryManID = Column(Integer, primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    Address = Column(String(255))
    Phone = Column(String(20))
    Name = Column(String(100), nullable=False)
    Email = Column(String(150), unique=True, index=True, nullable=False)
    Review = Column(Float, default=0.0)
    TotalDeliveries = Column(Integer, default=0)
    VehicleNo = Column(String(50))

    deliveries = relationship("Delivery", back_populates="delivery_man")


class Order(Base):
    """A customer order. Table is `orders` since ORDER is a reserved SQL keyword."""

    __tablename__ = "orders"

    OrderID = Column(Integer, primary_key=True, index=True)
    TotalAmount = Column(Float, nullable=False)  # source schema: "Total amount"
    CouponCode = Column(String(50))
    InvoiceDate = Column(DateTime)
    InvoiceID = Column(String(50))
    PaymentStatus = Column(String(50))
    OrderDate = Column(DateTime)
    PaymentMethod = Column(String(50))
    Status = Column(String(50))
    UserCustomerID = Column(Integer, ForeignKey("customers.UserCustomerID"))

    customer = relationship("Customer", back_populates="orders")
    items = relationship("Items", back_populates="order")
    deliveries = relationship("Delivery", back_populates="order")


class Delivery(Base):
    """A delivery task linking a DeliveryMan to an Order."""

    __tablename__ = "deliveries"

    DeliveryID = Column(Integer, primary_key=True, index=True)
    PickedUpTime = Column(DateTime)
    Status = Column(String(50))
    UserDeliveryManID = Column(Integer, ForeignKey("delivery_men.UserDeliveryManID"))
    OrderID = Column(Integer, ForeignKey("orders.OrderID"))

    delivery_man = relationship("DeliveryMan", back_populates="deliveries")
    order = relationship("Order", back_populates="deliveries")


class Items(Base):
    """A shop's catalog item, which may also belong to an Order once purchased."""

    __tablename__ = "items"

    ItemID = Column(Integer, primary_key=True, index=True)
    Name = Column(String(150), nullable=False)
    Price = Column(Float, nullable=False)
    Stock = Column(Integer, default=0)
    FruitsAndVegetables = Column(Boolean, default=False)  # source schema: "Fruits & Vegetables"
    Grains = Column(Boolean, default=False)
    Meat = Column(Boolean, default=False)
    ShopID = Column(Integer, ForeignKey("shops.ShopID"))
    OrderID = Column(Integer, ForeignKey("orders.OrderID"))

    shop = relationship("Shop", back_populates="items")
    order = relationship("Order", back_populates="items")
    pre_order_requests = relationship("PreOrderRequest", back_populates="item")

    @property
    def Category(self) -> str:
        """Derives a single display category from the three boolean columns."""
        if self.FruitsAndVegetables:
            return "Fruits & Vegetables"
        if self.Grains:
            return "Grains"
        if self.Meat:
            return "Meat"
        return "Uncategorized"


class PreOrderRequest(Base):
    """A customer's request to a farmer to pre-order an item at a proposed price."""

    __tablename__ = "pre_order_requests"

    PreOrderID = Column(Integer, primary_key=True, index=True)
    ProposedPrice = Column(Float, nullable=False)
    Quantity = Column(Integer, nullable=False)
    Status = Column(String(50))
    RequestDate = Column(DateTime)
    UserFarmerID = Column(Integer, ForeignKey("farmers.UserFarmerID"))
    UserCustomerID = Column(Integer, ForeignKey("customers.UserCustomerID"))
    ItemID = Column(Integer, ForeignKey("items.ItemID"))

    farmer = relationship("Farmer", back_populates="pre_order_requests")
    customer = relationship("Customer", back_populates="pre_order_requests")
    item = relationship("Items", back_populates="pre_order_requests")
