import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Carga las variables del archivo .env (sobrescribiendo variables residuales de la terminal)
load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")


# Motor de conexión hacia PostgreSQL en Supabase
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Inyector de sesión para los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
