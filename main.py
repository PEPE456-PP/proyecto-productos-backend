from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
from database import engine, get_db

# Asegurar que las tablas existan en Supabase
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API PEPEBIKE - Catálogo de Bicicletas, E-Bikes y Accesorios",
    version="1.0.0",
    description="Servicio Backend conectado a PostgreSQL en Supabase con Bicicletas de Montaña, E-Bikes, Cascos, Guantes, Lentes y Accesorios de Ciclismo"
)

# Habilitar CORS para permitir llamadas desde Vercel o desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ENDPOINTS DE CATEGORÍAS ====================
@app.get("/api/v1/categories", response_model=List[schemas.CategoryResponse], tags=["Categorías"])
def list_categories(db: Session = Depends(get_db)):
    """Obtiene la lista de todas las categorías disponibles."""
    return db.query(models.Category).all()

@app.post("/api/v1/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED, tags=["Categorías"])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Registra una nueva categoría."""
    nueva = models.Category(**category.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# ==================== ENDPOINTS DE PRODUCTOS ====================
@app.get("/api/v1/products", response_model=List[schemas.ProductResponse], tags=["Productos"])
def list_products(
    category_id: Optional[int] = None,
    is_featured: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Obtiene todos los productos con soporte opcional de filtro por categoría o destacados."""
    query = db.query(models.Product)
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)
    if is_featured is not None:
        query = query.filter(models.Product.is_featured == is_featured)
    return query.all()

@app.get("/api/v1/products/{product_id}", response_model=schemas.ProductResponse, tags=["Productos"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtiene un producto específico por su ID."""
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return prod

@app.post("/api/v1/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Registra un nuevo producto en el catálogo."""
    nuevo = models.Product(**product.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.patch("/api/v1/products/{product_id}", response_model=schemas.ProductResponse, tags=["Productos"])
def update_product_partial(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """Actualiza parcialmente un producto (ej. descontar o modificar stock)."""
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prod, field, value)
    db.commit()
    db.refresh(prod)
    return prod

@app.put("/api/v1/products/{product_id}", response_model=schemas.ProductResponse, tags=["Productos"])
def update_product_full(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Actualiza completamente un producto."""
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    for field, value in product_update.model_dump().items():
        setattr(prod, field, value)
    db.commit()
    db.refresh(prod)
    return prod


# ==================== ENDPOINTS DE PEDIDOS / VENTAS ====================
@app.get("/api/v1/orders", response_model=List[schemas.OrderResponse], tags=["Pedidos"])
def list_orders(db: Session = Depends(get_db)):
    """Lista todos los pedidos registrados en el sistema."""
    return db.query(models.Order).order_by(models.Order.id.desc()).all()

@app.post("/api/v1/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Crea un nuevo pedido y descuenta el stock del producto."""
    prod = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto solicitado no existe")
    if prod.stock < order.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Stock insuficiente. Disponible: {prod.stock}")

    # Descontar stock
    prod.stock -= order.quantity

    nuevo_pedido = models.Order(**order.model_dump())
    if not nuevo_pedido.order_number:
        nuevo_pedido.order_number = f"ORD-2026-{db.query(models.Order).count() + 1:03d}"

    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido
