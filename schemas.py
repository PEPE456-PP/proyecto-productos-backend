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

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    cost_price: Optional[float] = None
    min_stock: Optional[int] = None
    rating: Optional[float] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None

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


# ==================== SISTEMA REAL DE VENTAS Y FACTURACIÓN MULTI-ÍTEM ====================
class SaleItemBase(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    product_sku: Optional[str] = None
    quantity: int = 1
    unit_price: float
    subtotal: float

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    model_config = ConfigDict(from_attributes=True)


class SaleCreate(BaseModel):
    customer_name: str
    customer_nit: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    payment_method: Optional[str] = "Efectivo"
    amount_paid: Optional[float] = None
    discount: Optional[float] = 0.0
    items: List[SaleItemCreate]

class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    authorization_code: Optional[str] = None
    control_code: Optional[str] = None
    customer_name: str
    customer_nit: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    payment_method: str
    amount_paid: Optional[float] = None
    change_amount: Optional[float] = None
    subtotal: float
    discount: float
    total: float
    status: str
    created_at: Optional[datetime] = None
    items: List[SaleItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
