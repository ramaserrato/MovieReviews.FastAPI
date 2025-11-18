from sqlalchemy.orm import Session
from app import crud

def obtener_info_pelicula(db: Session, pelicula_id: int):
    pelicula = crud.get_pelicula(db, pelicula_id)

    if not pelicula:
        return None

    return {
        "titulo": pelicula.tituloPelicula,
        "director": pelicula.directorPelicula,
        "anio": pelicula.añoPelicula,
        "poster": pelicula.poster_url,
        "generos": pelicula.generos
    }
