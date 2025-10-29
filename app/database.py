from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Crear la URL de conexión
DATABASE_URL = "mysql+pymysql://fastapi_user:1234@localhost:3306/MovieReviews"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear sesión para interactuar con la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos (tablas)
Base = declarative_base()
