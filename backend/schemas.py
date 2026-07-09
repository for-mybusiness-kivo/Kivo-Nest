from pydantic import BaseModel
from typing import Optional


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    group_key: str
    tier: str
    price: int
    image_urls: list[str]
    why_recommend: list[str]
    not_for_you: list[str]
    models_considered: int
    price_quality_score: float
    build_score: float
    design_score: float
    durability_score: float
    kivo_score: float
    is_choice: bool
    is_featured: bool
    in_stock: bool

    class Config:
        from_attributes = True


class ProductCard(BaseModel):
    id: int
    name: str
    tier: str
    price: int
    image_urls: list[str]
    kivo_score: float
    in_stock: bool

    class Config:
        from_attributes = True


class CartAddIn(BaseModel):
    product_id: int
    qty: int = 1


class CheckoutIn(BaseModel):
    name: str
    phone: str
    address: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    comment: Optional[str] = None
    promo_code: Optional[str] = None


class SearchIn(BaseModel):
    q: str
