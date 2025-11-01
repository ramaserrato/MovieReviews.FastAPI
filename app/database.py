from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Obtener variables de entorno
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Crear la URL de conexión (forma correcta)
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@localhost:3306/MovieReviews"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear sesión para interactuar con la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos (tablas)
Base = declarative_base()