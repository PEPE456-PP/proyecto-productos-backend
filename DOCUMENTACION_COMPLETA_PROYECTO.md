# Documentación Técnica: Backend FastAPI con Supabase PostgreSQL

**Proyecto:** Catálogo de Productos y Sistema de Ventas  
**Módulo:** Desarrollo Backend y Bases de Datos Cloud  
**Tecnologías:** Python 3.12, FastAPI, SQLAlchemy ORM, PostgreSQL (Supabase), Pydantic V2, Uvicorn

---

## 1. Arquitectura del Sistema

El sistema implementa una arquitectura desacoplada donde el backend en **FastAPI** actúa como capa de lógica de negocio y validación, conectándose a una base de datos relacional **PostgreSQL** alojada en la nube mediante **Supabase**.

```mermaid
flowchart TD
    subgraph Cliente["Capa Cliente / Presentación"]
        Swagger["Swagger UI / OpenAPI<br/>(http://localhost:8000/docs)"]
        Frontend["Frontend Web (React + Tailwind)<br/>(Vercel / Local)"]
    end

    subgraph Backend["Capa de Lógica y Servicios (FastAPI)"]
        Main["main.py<br/>Controladores & CORS"]
        Schemas["schemas.py<br/>Validación Pydantic"]
        Models["models.py<br/>Mapeo ORM SQLAlchemy"]
        DB["database.py<br/>Motor de Sesión & Pool"]
        Env[".env<br/>Variables de Entorno"]
    end

    subgraph Cloud["Capa de Persistencia (Supabase Cloud)"]
        Pooler["Connection Pooler (Supavisor)<br/>aws-0-us-east-1.pooler.supabase.com:5432"]
        PG[("PostgreSQL Database<br/>(Tablas: categories, products, orders)")]
    end

    Cliente -->|Peticiones HTTP JSON| Main
    Main --> Schemas
    Main --> Models
    Models --> DB
    Env --> DB
    DB -->|TCP IPv4 / psycopg2| Pooler
    Pooler -->|Sesión interna| PG
```

---

## 2. Diagnóstico y Configuración de Conexión a Supabase

### 2.1. Problema Encontrado con la Conexión Directa
Al utilizar la cadena por defecto generada por Supabase:
```text
postgresql://postgres:[PASSWORD]@db.jjqsiorpgzidwkhovdxx.supabase.co:5432/postgres
```
Se presentaron dos fallos críticos:
1. **Incompatibilidad de Red (IPv6 vs IPv4):** Supabase asigna únicamente direcciones **IPv6** a sus hosts de conexión directa (`db.<ref>.supabase.co`). La mayoría de proveedores residenciales de internet operan exclusivamente con **IPv4**, lo que provocaba el error:
   ```text
   psycopg2.OperationalError: connection to server at "db.jjqsiorpgzidwkhovdxx.supabase.co", port 5432 failed: Connection refused
   ```
2. **Marcador de Posición de Contraseña:** Supabase muestra `[YOUR-PASSWORD]`. Al colocar los corchetes literalmente en la contraseña (`[Liam102509.pepe]`), PostgreSQL los interpreta como caracteres reales, generando:
   ```text
   FATAL: password authentication failed for user "postgres"
   ```
3. **Driver en SQLAlchemy 2+:** SQLAlchemy requiere que se declare explícitamente el driver `psycopg2` mediante el prefijo `postgresql+psycopg2://`.

### 2.2. Solución Definitiva (Supabase Connection Pooler)
Se sustituyó la conexión directa por el **Connection Pooler oficial de Supabase (Supavisor)**, el cual cuenta con resolución IPv4 pública y gratuita:

* **Host:** `aws-0-us-east-1.pooler.supabase.com`
* **Puerto:** `5432` (Modo Sesión)
* **Usuario:** `postgres.jjqsiorpgzidwkhovdxx` (Usuario de BD + Referencia del Proyecto)
* **Base de Datos:** `postgres`

Cadena configurada en el archivo `.env`:
```env
DATABASE_URL=postgresql+psycopg2://postgres.jjqsiorpgzidwkhovdxx:Liam102509.pepe@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

Además, en `database.py` se implementó `load_dotenv(override=True)` para asegurar que las variables del entorno del sistema operativo no sobreescriban los valores actualizados del archivo local.

---

## 3. Modelo Entidad-Relación (DER)

El modelo de datos consta de 3 entidades normalizadas con integridad referencial y relaciones **1 a Muchos (1:N)**:

```mermaid
erDiagram
    CATEGORIES ||--o{ PRODUCTS : "clasifica (1:N)"
    PRODUCTS ||--o{ ORDERS : "registra venta (1:N)"

    CATEGORIES {
        bigint id PK "Identificador único"
        text name "Nombre de la categoría (Único)"
        text slug "Identificador URL amigable"
        text description "Descripción de la categoría"
        boolean is_active "Estado de activación"
        text icon "Nombre de icono UI"
        timestamptz created_at "Fecha de registro"
    }

    PRODUCTS {
        bigint id PK "Identificador único"
        bigint category_id FK "Referencia a categories.id"
        text sku "Código comercial único (SKU)"
        text name "Nombre del producto"
        text description "Ficha técnica o descripción"
        numeric price "Precio unitario de venta"
        numeric cost_price "Costo de adquisición (margen)"
        integer stock "Inventario disponible"
        integer min_stock "Stock mínimo de alerta"
        numeric rating "Calificación (1.0 - 5.0)"
        boolean is_featured "Producto destacado en portada"
        text status "Estado (active, out_of_stock)"
        text image_url "Enlace a imagen del producto"
        timestamptz created_at "Fecha de registro"
    }

    ORDERS {
        bigint id PK "Identificador único"
        text order_number "Código correlativo de pedido"
        bigint product_id FK "Referencia a products.id"
        text customer_name "Nombre completo del cliente"
        text customer_email "Correo electrónico"
        text customer_phone "Teléfono de contacto"
        text customer_city "Ciudad destino de la compra"
        integer quantity "Cantidad de unidades compradas"
        numeric unit_price "Precio unitario aplicado"
        numeric discount "Descuento otorgado en Bs."
        numeric total_price "Total neto cobrado en Bs."
        text payment_method "Forma de pago (qr, tarjeta, transferencia)"
        text status "Estado del pedido (completed, pending)"
        timestamptz created_at "Fecha de registro"
    }
```

---

## 4. Scripts SQL Ejecutados en Supabase

### 4.1. Creación de Tablas (DDL) y Seguridad (RLS)
```sql
-- 1. Tabla de Categorías
create table if not exists categories (
    id bigint generated by default as identity primary key,
    name text not null unique,
    slug text,
    description text,
    is_active boolean default true,
    icon text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Tabla de Productos
create table if not exists products (
    id bigint generated by default as identity primary key,
    category_id bigint references categories(id) on delete set null,
    sku text,
    name text not null,
    description text,
    price numeric not null,
    cost_price numeric,
    stock integer default 0 not null,
    min_stock integer default 5,
    rating numeric default 5.0,
    is_featured boolean default false,
    status text default 'active',
    image_url text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Tabla de Pedidos / Ventas
create table if not exists orders (
    id bigint generated by default as identity primary key,
    order_number text,
    product_id bigint not null references products(id) on delete cascade,
    customer_name text not null,
    customer_email text,
    customer_phone text,
    customer_city text,
    quantity integer not null default 1,
    unit_price numeric,
    discount numeric default 0.00,
    total_price numeric not null,
    payment_method text default 'qr',
    status text default 'completed',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Habilitar Row Level Security (RLS) en todas las tablas
alter table categories enable row level security;
alter table products enable row level security;
alter table orders enable row level security;

-- Políticas de lectura pública
create policy "Cualquiera puede ver categorias" on categories for select to public using (true);
create policy "Cualquiera puede ver los productos" on products for select to public using (true);
create policy "Cualquiera puede ver pedidos" on orders for select to public using (true);

-- Políticas de inserción pública (APIs / Clientes)
create policy "Permitir insertar categorias" on categories for insert to public with check (true);
create policy "Permitir insertar productos" on products for insert to public with check (true);
create policy "Permitir insertar pedidos" on orders for insert to public with check (true);
```

### 4.2. Poblado de Datos Iniciales (Seed Data)
```sql
-- Categorías
INSERT INTO categories (id, name, slug, description, is_active, icon) VALUES
(1, 'Laptops & Computadoras', 'laptops-computadoras', 'Portátiles de trabajo, gaming y estaciones de escritorio', true, 'laptop'),
(2, 'Periféricos & Accesorios', 'perifericos-accesorios', 'Teclados mecánicos, ratones gamer y alfombrillas', true, 'keyboard'),
(3, 'Audio & Sonido', 'audio-sonido', 'Auriculares inalámbricos, altavoces y micrófonos profesionales', true, 'headphones'),
(4, 'Monitores & Pantallas', 'monitores-pantallas', 'Monitores 4K, pantallas curvas y paneles de alta tasa de refresco', true, 'monitor'),
(5, 'Almacenamiento', 'almacenamiento', 'Discos de estado sólido SSD, discos externos y memorias NVMe', true, 'hard-drive');

-- Productos
INSERT INTO products (id, category_id, sku, name, description, price, cost_price, stock, min_stock, rating, is_featured, status, image_url) VALUES
(1, 1, 'LAP-NITRO-01', 'Laptop Gamer Acer Nitro 5', 'Intel Core i7 12th Gen, 16GB RAM, 512GB SSD, RTX 3060', 6850.00, 5600.00, 12, 3, 4.8, true, 'active', 'https://images.unsplash.com/photo-1603302576837-37561b2e2302'),
(2, 1, 'LAP-THINK-02', 'Lenovo ThinkPad E14', 'AMD Ryzen 7 5700U, 16GB RAM, 512GB SSD, ideal para empresas', 5200.00, 4300.00, 8, 2, 4.7, false, 'active', 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed'),
(3, 2, 'KEY-K552-01', 'Teclado Mecánico Redragon Kumara', 'Switches Outemu Blue, retroiluminación RGB, chasis metálico compacto', 340.00, 220.00, 25, 5, 4.6, true, 'active', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3'),
(4, 2, 'MOU-G502-02', 'Mouse Logitech G502 HERO', 'Sensor HERO 25K, 11 botones programables, peso personalizable', 420.00, 290.00, 18, 5, 4.9, true, 'active', 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7'),
(5, 3, 'AUD-SONY-01', 'Auriculares Sony WH-1000XM5', 'Cancelación de ruido líder en la industria, 30h de batería, Bluetooth 5.2', 2450.00, 1950.00, 6, 2, 4.9, true, 'active', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e'),
(6, 3, 'MIC-HYPER-02', 'Micrófono HyperX QuadCast S', 'Micrófono condensador USB con montura anti-vibración e iluminación RGB', 980.00, 750.00, 9, 3, 4.7, false, 'active', 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df'),
(7, 4, 'MON-LG27-01', 'Monitor LG UltraGear 27" IPS', 'Resolución QHD 2K, 165Hz, 1ms GtG, compatible con G-Sync', 2600.00, 2100.00, 5, 2, 4.8, true, 'active', 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf'),
(8, 5, 'SSD-EVO-01', 'SSD NVMe Samsung 980 PRO 1TB', 'PCIe 4.0, velocidades de lectura de hasta 7000 MB/s para gaming', 890.00, 680.00, 30, 8, 4.9, false, 'active', 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b');

-- Pedidos / Ventas
INSERT INTO orders (id, order_number, product_id, customer_name, customer_email, customer_phone, customer_city, quantity, unit_price, discount, total_price, payment_method, status) VALUES
(1, 'ORD-2026-001', 1, 'Carlos Mendoza', 'carlos.m@gmail.com', '77123456', 'La Paz', 1, 6850.00, 150.00, 6700.00, 'tarjeta_credito', 'completed'),
(2, 'ORD-2026-002', 3, 'Andrea Flores', 'andrea.f@hotmail.com', '68987654', 'Santa Cruz', 2, 340.00, 0.00, 680.00, 'qr', 'completed'),
(3, 'ORD-2026-003', 4, 'Jorge Gutierrez', 'jorge.gtz@yahoo.com', '71239845', 'Cochabamba', 1, 420.00, 20.00, 400.00, 'qr', 'completed'),
(4, 'ORD-2026-004', 5, 'Mariana Rojas', 'mariana.r@gmail.com', '76541289', 'La Paz', 1, 2450.00, 100.00, 2350.00, 'transferencia', 'completed'),
(5, 'ORD-2026-005', 7, 'Roberto Arteaga', 'roberto.art@outlook.com', '70112233', 'Santa Cruz', 1, 2600.00, 0.00, 2600.00, 'tarjeta_credito', 'pending'),
(6, 'ORD-2026-006', 8, 'Lucia Morales', 'lucia.m@gmail.com', '72334455', 'Sucre', 3, 890.00, 90.00, 2580.00, 'qr', 'completed'),
(7, 'ORD-2026-007', 2, 'Daniel Vargas', 'daniel.v@empresa.com', '75998877', 'La Paz', 2, 5200.00, 400.00, 10000.00, 'transferencia', 'completed'),
(8, 'ORD-2026-008', 3, 'Fernanda Soliz', 'fer.soliz@gmail.com', '78445566', 'Cochabamba', 1, 340.00, 0.00, 340.00, 'qr', 'completed'),
(9, 'ORD-2026-009', 6, 'Mateo Quiroga', 'mateo.q@gmail.com', '73114422', 'Tarija', 1, 980.00, 50.00, 930.00, 'efectivo', 'completed'),
(10, 'ORD-2026-010', 4, 'Valeria Gomez', 'valeria.g@hotmail.com', '79887766', 'Santa Cruz', 1, 420.00, 0.00, 420.00, 'tarjeta_debito', 'completed');

-- Sincronizar secuencias autonuméricas
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));
```

---

## 5. Implementación del Backend en FastAPI

### 5.1. Estructura de Archivos
```text
backend/
├── .env                  # URL de conexión a Supabase (Pooler)
├── requirements.txt      # Dependencias instaladas
├── database.py           # Conexión SQLAlchemy y get_db()
├── models.py             # Modelos ORM (Category, Product, Order)
├── schemas.py            # Esquemas Pydantic V2 de validación
└── main.py               # Aplicación FastAPI, CORS y Endpoints REST
```

### 5.2. Endpoints Disponibles en la API
| Método | Endpoint | Descripción | Parámetros Opcionales |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/categories` | Lista todas las categorías | Ninguno |
| `POST` | `/api/v1/categories` | Registra una nueva categoría | Body JSON (`CategoryCreate`) |
| `GET` | `/api/v1/products` | Lista catálogo de productos | `category_id`, `is_featured` |
| `GET` | `/api/v1/products/{id}` | Detalle de un producto | `product_id` (Path) |
| `POST` | `/api/v1/products` | Registra un nuevo producto | Body JSON (`ProductCreate`) |
| `GET` | `/api/v1/orders` | Historial de pedidos | Ninguno |
| `POST` | `/api/v1/orders` | Registra pedido y descuenta stock | Body JSON (`OrderCreate`) |

---

## 6. Banco de Consultas SQL para Demostración en Clase

Estas consultas demuestran el poder del modelo relacional en PostgreSQL y pueden ejecutarse directamente en el **SQL Editor** de Supabase:

### Consulta 1: INNER JOIN y Formato Completo de Pedidos
*Muestra cada pedido relacionando el cliente, producto, categoría y método de pago.*
```sql
SELECT 
    o.order_number AS "Nro. Pedido",
    o.customer_name AS "Cliente",
    p.name AS "Producto Adquirido",
    c.name AS "Categoría",
    o.quantity AS "Cant.",
    o.payment_method AS "Método Pago",
    o.discount AS "Descuento (Bs.)",
    o.total_price AS "Total Pagado (Bs.)",
    TO_CHAR(o.created_at, 'DD/MM/YYYY HH24:MI') AS "Fecha"
FROM orders o
JOIN products p ON o.product_id = p.id
JOIN categories c ON p.category_id = c.id
ORDER BY o.id DESC;
```

### Consulta 2: Agregación con GROUP BY por Ciudad
*Calcula el total recaudado y unidades vendidas en cada ciudad de Bolivia.*
```sql
SELECT 
    customer_city AS "Ciudad",
    COUNT(id) AS "Total Transacciones",
    SUM(quantity) AS "Unidades Vendidas",
    ROUND(AVG(total_price), 2) AS "Ticket Promedio (Bs.)",
    SUM(total_price) AS "Total Recaudado (Bs.)"
FROM orders
WHERE status = 'completed'
GROUP BY customer_city
ORDER BY "Total Recaudado (Bs.)" DESC;
```

### Consulta 3: Agregación y Ventas por Categoría (LEFT JOIN)
*Muestra el rendimiento comercial de cada categoría de la tienda.*
```sql
SELECT 
    c.name AS "Categoría",
    COUNT(DISTINCT p.id) AS "Variedad Productos",
    COALESCE(SUM(o.quantity), 0) AS "Unidades Vendidas",
    COALESCE(SUM(o.total_price), 0.00) AS "Ingresos Generados (Bs.)"
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
LEFT JOIN orders o ON p.id = o.product_id
GROUP BY c.id, c.name
ORDER BY "Ingresos Generados (Bs.)" DESC;
```

### Consulta 4: Análisis de Márgenes de Ganancia Comercial
*Compara precio de venta con precio de costo para calcular la utilidad unitaria y porcentaje de rentabilidad.*
```sql
SELECT 
    sku AS "SKU",
    name AS "Producto",
    cost_price AS "Costo (Bs.)",
    price AS "Venta (Bs.)",
    (price - cost_price) AS "Margen Unitario (Bs.)",
    ROUND(((price - cost_price) / cost_price) * 100, 2) AS "% Rentabilidad",
    stock AS "Stock Actual"
FROM products
WHERE cost_price IS NOT NULL
ORDER BY "% Rentabilidad" DESC;
```

### Consulta 5: Alerta de Control de Inventario (Stock Crítico)
*Identifica productos que están por agotarse según su umbral configurado.*
```sql
SELECT 
    sku AS "SKU",
    name AS "Producto",
    stock AS "Stock Actual",
    min_stock AS "Mínimo Requerido",
    CASE 
        WHEN stock = 0 THEN 'AGOTADO'
        WHEN stock <= min_stock THEN 'REORDENAR URGENTE'
        ELSE 'NORMAL'
    END AS "Nivel de Alerta"
FROM products
WHERE stock <= min_stock
ORDER BY stock ASC;
```

---

## 7. Instrucciones para Ejecutar y Presentar

1. **Activar el entorno virtual:**
   ```bash
   source venv/bin/activate
   ```
2. **Iniciar el servidor local:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. **Acceder a la documentación Swagger:**
   * Navegador: [http://localhost:8000/docs](http://localhost:8000/docs)
   * Permite probar visualmente cada método GET y POST con respuestas instantáneas contra la base de datos Supabase.

