# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# Schemas para Usuario
class UsuarioBase(BaseModel):
    nombreUsuario: str
    apellidoUsuario: str
    correoUsuario: EmailStr
    sexoUsuario: Optional[str] = None
    generoFavUsuario: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    idUsuario: int

    class Config:
        orm_mode = True

# Schemas para Pelicula
class PeliculaBase(BaseModel):
    tituloPelicula: str
    directorPelicula: Optional[str] = None
    añoPelicula: Optional[int] = None

class PeliculaCreate(PeliculaBase):
    pass

class Pelicula(PeliculaBase):
    idPelicula: int

    class Config:
        orm_mode = True

# Schemas para Review
class ReviewBase(BaseModel):
    textReview: str
    numPersonaReview: int
    numPeliculareview: int

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    idReview: int

    class Config:
        orm_mode = True

# Schema para Review con relaciones
class ReviewWithRelations(Review):
    usuario: Usuario
    pelicula: Pelicula