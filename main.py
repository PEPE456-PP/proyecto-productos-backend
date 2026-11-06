from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import hashlib
import random
import time

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


# ==================== ENDPOINTS DE VENTAS Y FACTURACIÓN MULTI-ÍTEM ====================
@app.get("/api/v1/sales", response_model=List[schemas.SaleResponse], tags=["Ventas y Facturación"])
def list_sales(db: Session = Depends(get_db)):
    """Lista todas las facturas y ventas multi-ítem registradas en el sistema."""
    return db.query(models.Sale).order_by(models.Sale.id.desc()).all()


@app.get("/api/v1/sales/{sale_id}", response_model=schemas.SaleResponse, tags=["Ventas y Facturación"])
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle completo de una factura por su ID."""
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Factura no encontrada")
    return sale


@app.post("/api/v1/sales", response_model=schemas.SaleResponse, status_code=status.HTTP_201_CREATED, tags=["Ventas y Facturación"])
def create_sale(sale_in: schemas.SaleCreate, db: Session = Depends(get_db)):
    """
    Registra una venta multi-producto con emisión de factura real:
    - Valida y descuenta stock atómicamente en PostgreSQL.
    - Genera N° de Factura correlativo, Código de Autorización y Código de Control.
    - Calcula totales, cambio e IVA.
    """
    if not sale_in.items or len(sale_in.items) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe incluir al menos un producto en la venta.")

    # 1. Validar stock de todos los productos antes de procesar
    for item in sale_in.items:
        if item.product_id:
            prod = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            if not prod:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto '{item.product_name}' no encontrado.")
            if prod.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{prod.name}'. Solicitado: {item.quantity}, Disponible: {prod.stock}"
                )

    # 2. Descontar stock atómicamente
    calculated_subtotal = 0.0
    for item in sale_in.items:
        item_subtotal = round(item.unit_price * item.quantity, 2)
        calculated_subtotal += item_subtotal
        if item.product_id:
            prod = db.query(models.Product).filter(models.Product.id == item.product_id).first()
            prod.stock -= item.quantity

    calculated_subtotal = round(calculated_subtotal, 2)
    discount = round(sale_in.discount or 0.0, 2)
    total = max(0.0, round(calculated_subtotal - discount, 2))

    amount_paid = sale_in.amount_paid if sale_in.amount_paid is not None else total
    change_amount = max(0.0, round(amount_paid - total, 2)) if sale_in.payment_method == "Efectivo" else 0.0

    # 3. Generar número de factura correlativo
    sale_count = db.query(models.Sale).count() + 1
    invoice_number = f"FAC-2026-{sale_count:05d}"
    auth_code = f"4154016000{random.randint(10000, 99999)}"
    raw_control = f"{invoice_number}-{sale_in.customer_nit}-{total}-{time.time()}"
    control_code = "-".join([hashlib.md5(raw_control.encode()).hexdigest()[i:i+2].upper() for i in range(0, 8, 2)])

    nueva_venta = models.Sale(
        invoice_number=invoice_number,
        authorization_code=auth_code,
        control_code=control_code,
        customer_name=sale_in.customer_name.strip() or "Sin Nombre",
        customer_nit=sale_in.customer_nit.strip() or "0",
        customer_email=sale_in.customer_email,
        customer_phone=sale_in.customer_phone,
        payment_method=sale_in.payment_method or "Efectivo",
        amount_paid=amount_paid,
        change_amount=change_amount,
        subtotal=calculated_subtotal,
        discount=discount,
        total=total,
        status="emitida"
    )
    db.add(nueva_venta)
    db.flush()

    # 4. Insertar ítems asociados
    for item in sale_in.items:
        sale_item = models.SaleItem(
            sale_id=nueva_venta.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_sku=item.product_sku,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=round(item.unit_price * item.quantity, 2)
        )
        db.add(sale_item)

    db.commit()
    db.refresh(nueva_venta)
    return nueva_venta
