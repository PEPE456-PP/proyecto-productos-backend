"""
Script de migración y actualización para transformar el catálogo de Supabase
hacia una Tienda de Bicicletas, E-Bikes, Cascos, Guantes, Lentes y Accesorios.
"""
from database import SessionLocal
import models

def seed():
    db = SessionLocal()
    try:
        print("1. Limpiando catálogo antiguo de tecnología...")
        # Eliminar pedidos de prueba antiguos si existen
        db.query(models.Order).delete()
        # Eliminar productos antiguos
        db.query(models.Product).delete()
        # Eliminar categorías antiguas
        db.query(models.Category).delete()
        db.commit()

        print("2. Registrando categorías de ciclismo...")
        categories_data = [
            {
                "id": 1,
                "name": "Bicicletas de Montaña & Ruta",
                "slug": "bicicletas-montana-ruta",
                "description": "Bicicletas profesionales MTB, gravel y carretera",
                "is_active": True,
                "icon": "bike",
            },
            {
                "id": 2,
                "name": "Bicicletas Eléctricas (E-Bikes)",
                "slug": "bicicletas-electricas",
                "description": "E-bikes urbanas y de montaña con asistencia eléctrica y batería de litio",
                "is_active": True,
                "icon": "zap",
            },
            {
                "id": 3,
                "name": "Cascos & Protección",
                "slug": "cascos-proteccion",
                "description": "Cascos aerodinámicos, integrales y de montaña con tecnología MIPS",
                "is_active": True,
                "icon": "shield",
            },
            {
                "id": 4,
                "name": "Guantes & Indumentaria",
                "slug": "guantes-indumentaria",
                "description": "Guantes con amortiguación de gel, maillots y ropa técnica",
                "is_active": True,
                "icon": "hand",
            },
            {
                "id": 5,
                "name": "Lentes & Gafas Deportivas",
                "slug": "lentes-gafas-deportivas",
                "description": "Gafas de sol de ciclismo con protección UV400 y lentes fotocromáticas",
                "is_active": True,
                "icon": "glasses",
            },
            {
                "id": 6,
                "name": "Accesorios & Componentes",
                "slug": "accesorios-componentes",
                "description": "Luces LED potentes, candados U-Lock, infladores y herramientas",
                "is_active": True,
                "icon": "tool",
            },
        ]

        for cat in categories_data:
            db.add(models.Category(**cat))
        db.commit()

        print("3. Registrando productos de ciclismo en Supabase...")
        products_data = [
            {
                "name": "Bicicleta de Montaña Trek Marlin 7 Gen 3",
                "price": 1150.0,
                "stock": 8,
                "sku": "BIKE-MTB-01",
                "description": "Cuadro de aluminio Alpha Silver, suspensión delantera RockShox Judy con bloqueo, transmisión 1x10 Shimano Deore y frenos de disco hidráulicos.",
                "cost_price": 920.0,
                "min_stock": 2,
                "rating": 4.9,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=800&q=80",
                "category_id": 1,
            },
            {
                "name": "Bicicleta de Ruta Specialized Allez Sport",
                "price": 1400.0,
                "stock": 5,
                "sku": "BIKE-ROAD-02",
                "description": "Cuadro ligero de aleación E5 premium, horquilla de carbono FACT, grupo Shimano Tiagra 2x10 y neumáticos de alta velocidad.",
                "cost_price": 1100.0,
                "min_stock": 2,
                "rating": 4.8,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?auto=format&fit=crop&w=800&q=80",
                "category_id": 1,
            },
            {
                "name": "E-Bike Urbana Cannondale Quick Neo SL 2",
                "price": 2850.0,
                "stock": 6,
                "sku": "EBIKE-URB-01",
                "description": "Motor Mahle ebikemotion de 250W en el buje, batería oculta en el cuadro de 250Wh con 75km de autonomía y pantalla de control en el manillar.",
                "cost_price": 2250.0,
                "min_stock": 2,
                "rating": 4.9,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=800&q=80",
                "category_id": 2,
            },
            {
                "name": "E-Bike Todoterreno Specialized Turbo Levo Alloy",
                "price": 5200.0,
                "stock": 4,
                "sku": "EBIKE-MTB-02",
                "description": "Motor Turbo Full Power 2.2 con 90Nm de torque, batería de 700Wh para rutas extremas y suspensión completa Fox de 160mm.",
                "cost_price": 4200.0,
                "min_stock": 1,
                "rating": 5.0,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?auto=format&fit=crop&w=800&q=80",
                "category_id": 2,
            },
            {
                "name": "Casco de Ciclismo Giro Aether Spherical MIPS",
                "price": 280.0,
                "stock": 16,
                "sku": "HELM-GIRO-01",
                "description": "Sistema de protección multidireccional Spherical MIPS, 21 aberturas de ventilación Wind Tunnel y ajuste micrométrico Roc Loc 5 Air.",
                "cost_price": 190.0,
                "min_stock": 4,
                "rating": 4.9,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1559348349-86f1f65817fe?auto=format&fit=crop&w=800&q=80",
                "category_id": 3,
            },
            {
                "name": "Casco Integral MTB Bell Super Air R MIPS",
                "price": 320.0,
                "stock": 10,
                "sku": "HELM-BELL-02",
                "description": "Mentonera desmontable envolvente para descenso, tecnología Flex Spherical + MIPS y visera ajustable compatible con antiparras.",
                "cost_price": 230.0,
                "min_stock": 3,
                "rating": 4.8,
                "is_featured": False,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1596707328905-2e6b20625902?auto=format&fit=crop&w=800&q=80",
                "category_id": 3,
            },
            {
                "name": "Guantes de Ciclismo Fox Racing Ranger Gel",
                "price": 45.0,
                "stock": 25,
                "sku": "GLOV-FOX-01",
                "description": "Inserciones de gel TruGel en la palma para absorber impactos del terreno, puño de neopreno con cierre de velcro e hilos táctiles para móvil.",
                "cost_price": 28.0,
                "min_stock": 5,
                "rating": 4.7,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80",
                "category_id": 4,
            },
            {
                "name": "Guantes Cortos Castelli Arenberg Gel 2",
                "price": 55.0,
                "stock": 18,
                "sku": "GLOV-CAST-02",
                "description": "Sistema de amortiguación Castelli Damping System (CDS) para aliviar la presión en las manos y dorso de micromalla altamente transpirable.",
                "cost_price": 35.0,
                "min_stock": 4,
                "rating": 4.8,
                "is_featured": False,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=800&q=80",
                "category_id": 4,
            },
            {
                "name": "Lentes Deportivos Oakley Radar EV Path Prizm Road",
                "price": 220.0,
                "stock": 14,
                "sku": "LENS-OAK-01",
                "description": "Lente envolvente Prizm Road para maximizar el contraste y visibilidad del asfalto, montura ultraligera O-Matter y gomas de Unobtainium antideslizantes.",
                "cost_price": 150.0,
                "min_stock": 3,
                "rating": 4.9,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=800&q=80",
                "category_id": 5,
            },
            {
                "name": "Lentes Fotocromáticos Rockbros Polarizados UV400",
                "price": 65.0,
                "stock": 22,
                "sku": "LENS-ROCK-02",
                "description": "Lentes inteligentes que se oscurecen automáticamente bajo la luz solar, puente nasal de goma suave y marco interior para cristales graduados.",
                "cost_price": 40.0,
                "min_stock": 5,
                "rating": 4.6,
                "is_featured": False,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1508296695146-257a814070b4?auto=format&fit=crop&w=800&q=80",
                "category_id": 5,
            },
            {
                "name": "Luz LED Inteligente Garmin Varia UT800",
                "price": 135.0,
                "stock": 12,
                "sku": "ACC-LGT-01",
                "description": "Foco frontal de 800 lúmenes con regulación automática de haz según la velocidad, visible a 1.6km y batería recargable USB de 6h.",
                "cost_price": 95.0,
                "min_stock": 3,
                "rating": 4.8,
                "is_featured": True,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=800&q=80",
                "category_id": 6,
            },
            {
                "name": "Candado U-Lock Kryptonite New York Fahgettaboudit",
                "price": 110.0,
                "stock": 15,
                "sku": "ACC-LOCK-02",
                "description": "Grillete de acero endurecido de 18mm máxima seguridad contra palancas y cizallas, cilindro de disco anti-taladro y soporte para cuadro.",
                "cost_price": 75.0,
                "min_stock": 3,
                "rating": 4.9,
                "is_featured": False,
                "status": "active",
                "image_url": "https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?auto=format&fit=crop&w=800&q=80",
                "category_id": 6,
            },
        ]

        for p in products_data:
            db.add(models.Product(**p))
        db.commit()

        print(f"¡Éxito! Se registraron {len(categories_data)} categorías y {len(products_data)} productos de bicicletas.")
    except Exception as e:
        db.rollback()
        print("Error en el seed:", e)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
