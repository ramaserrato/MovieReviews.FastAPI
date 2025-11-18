from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Usuario(Base):
    __tablename__ = "Usuarios"
    idUsuario = Column(Integer, primary_key=True, index=True)
    nombreUsuario = Column(String(100), nullable=False)
    apellidoUsuario = Column(String(100), nullable=False)
    correoUsuario = Column(String(150), unique=True, nullable=False)
    sexoUsuario = Column(String(50))
    generoFavUsuario = Column(String(255))

    reviews = relationship("Review", back_populates="usuario")

class Pelicula(Base):
    __tablename__ = "Peliculas"
    idPelicula = Column(Integer, primary_key=True, index=True)
    tituloPelicula = Column(String(255), nullable=False, unique=True)
    directorPelicula = Column(String(100))
    añoPelicula = Column(Integer)
    generos = Column(String(100))
    poster_url = Column(String(255))
    
    reviews = relationship("Review", back_populates="pelicula")

class Review(Base):
    __tablename__ = "Reviews"
    
    idReview = Column(Integer, primary_key=True, index=True)
    numPersonaReview = Column(Integer, ForeignKey("Usuarios.idUsuario"))
    numPeliculareview = Column(Integer, ForeignKey("Peliculas.idPelicula"))
    textReview = Column(String(1000))

    resultado_review = Column(String(20))  # POSITIVO / NEGATIVO / NEUTRO
    porcentaje_review = Column(Integer)    # o Double si querés decimal

    usuario = relationship("Usuario", back_populates="reviews")
    pelicula = relationship("Pelicula", back_populates="reviews")
