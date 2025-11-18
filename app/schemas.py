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
    generos: Optional[str] = None
    poster_url: Optional[str] = None

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
    resultado_review: Optional[str] = None
    porcentaje_review: Optional[float] = None


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

class ResultadoReview(BaseModel):
    idReview: int
    nombre: str
    apellido: str
    textReview: str
    sentimiento: str
    porcentaje: float
    pelicula_titulo: str
    pelicula_poster: str | None = None
    pelicula_anio: int | None = None
    pelicula_director: str | None = None
    pelicula_generos: str | None = None

    class Config:
        orm_mode = True
