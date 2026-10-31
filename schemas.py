from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# ==================== CATEGORÍAS ====================
class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== PRODUCTOS ====================
class ProductBase(BaseModel):
    name: str
    price: float
    stock: int = 0
    sku: Optional[str] = None
    description: Optional[str] = None
    cost_price: Optional[float] = None
    min_stock: Optional[int] = 5
    rating: Optional[float] = 5.0
    is_featured: Optional[bool] = False
    status: Optional[str] = "active"
    image_url: Optional[str] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ==================== PEDIDOS / VENTAS ====================
class OrderBase(BaseModel):
    product_id: int
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_city: Optional[str] = "La Paz"
    quantity: int = 1
    unit_price: Optional[float] = None
    discount: Optional[float] = 0.0
    total_price: float
    payment_method: Optional[str] = "qr"
    status: Optional[str] = "completed"

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    order_number: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
