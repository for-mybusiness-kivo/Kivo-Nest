from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, Boolean, ForeignKey, Text, JSON, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, index=True)  # e.g. "workspace"
    group_key: Mapped[str] = mapped_column(String, index=True)  # links tiers of one product line, e.g. "laptop_stand"
    tier: Mapped[str] = mapped_column(String)  # essential | recommended | premium
    price: Mapped[int] = mapped_column(Integer)  # so'm
    image_urls: Mapped[list] = mapped_column(JSON, default=list)
    why_recommend: Mapped[list] = mapped_column(JSON, default=list)   # list[str] checkmarks
    not_for_you: Mapped[list] = mapped_column(JSON, default=list)     # list[str] crosses
    tags: Mapped[str] = mapped_column(Text, default="")  # free text for search matching

    models_considered: Mapped[int] = mapped_column(Integer, default=0)
    price_quality_score: Mapped[float] = mapped_column(Float, default=0)
    build_score: Mapped[float] = mapped_column(Float, default=0)
    design_score: Mapped[float] = mapped_column(Float, default=0)
    durability_score: Mapped[float] = mapped_column(Float, default=0)
    kivo_score: Mapped[float] = mapped_column(Float, default=0)

    is_choice: Mapped[bool] = mapped_column(Boolean, default=False)  # "KIVO Choice" of the week
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[int] = mapped_column(Integer, default=1)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, default="pending")
    # pending -> confirmed -> packed -> shipped -> delivered

    name: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    location_lat: Mapped[float] = mapped_column(Float, nullable=True)
    location_lng: Mapped[float] = mapped_column(Float, nullable=True)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    promo_code: Mapped[str] = mapped_column(String, nullable=True)

    total: Mapped[int] = mapped_column(Integer, default=0)
    admin_message_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    qty: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship(back_populates="items")
