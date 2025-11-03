# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional

# CRUD para Usuarios
def get_usuario(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.idUsuario == usuario_id).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.correoUsuario == email).first()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    db_usuario = models.Usuario(
        nombreUsuario=usuario.nombreUsuario,
        apellidoUsuario=usuario.apellidoUsuario,
        correoUsuario=usuario.correoUsuario,
        sexoUsuario=usuario.sexoUsuario,
        generoFavUsuario=usuario.generoFavUsuario
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# CRUD para Películas
def get_pelicula(db: Session, pelicula_id: int):
    return db.query(models.Pelicula).filter(models.Pelicula.idPelicula == pelicula_id).first()

def get_peliculas(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    titulo: Optional[str] = None 
):
    query = db.query(models.Pelicula) 
    
    if titulo: 
        query = query.filter(models.Pelicula.tituloPelicula.ilike(f"%{titulo}%"))
        
    return query.offset(skip).limit(limit).all()

def get_pelicula_by_titulo(db: Session, titulo: str):
    return db.query(models.Pelicula).filter(models.Pelicula.tituloPelicula == titulo).first()

def create_pelicula(db: Session, pelicula: schemas.PeliculaCreate):
    db_pelicula = models.Pelicula(
        tituloPelicula=pelicula.tituloPelicula,
        directorPelicula=pelicula.directorPelicula,
        añoPelicula=pelicula.añoPelicula,
        # AGREGA LOS NUEVOS CAMPOS
        generos=pelicula.generos,
        poster_url=pelicula.poster_url
        # Agrega más campos si es necesario
    )
    db.add(db_pelicula)
    db.commit()
    db.refresh(db_pelicula)
    return db_pelicula

# CRUD para Reviews
def get_review(db: Session, review_id: int):
    return db.query(models.Review).filter(models.Review.idReview == review_id).first()

def get_reviews(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Review).offset(skip).limit(limit).all()

def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(
        textReview=review.textReview,
        numPersonaReview=review.numPersonaReview,
        numPeliculareview=review.numPeliculareview
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_by_usuario(db: Session, usuario_id: int):
    return db.query(models.Review).filter(models.Review.numPersonaReview == usuario_id).all()

def get_reviews_by_pelicula(db: Session, pelicula_id: int):
    return db.query(models.Review).filter(models.Review.numPeliculareview == pelicula_id).all()