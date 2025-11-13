from fastapi import FastAPI, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas, crud
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.ai_service import sentiment_analyzer  

app = FastAPI(title="MovieReviews", version="1.0.0")

# Crear tablas
models.Base.metadata.create_all(bind=engine)

# Dependency para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Bienvenido a MovieReviews API"}

# Endpoints para Usuarios
@app.post("/usuarios/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_email(db, email=usuario.correoUsuario)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return crud.create_usuario(db=db, usuario=usuario)

@app.get("/usuarios/", response_model=list[schemas.Usuario])
def leer_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = crud.get_usuarios(db, skip=skip, limit=limit)
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def leer_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

# Endpoints para Películas
@app.post("/peliculas/", response_model=schemas.Pelicula)
def crear_pelicula(pelicula: schemas.PeliculaCreate, db: Session = Depends(get_db)):
    db_pelicula = crud.get_pelicula_by_titulo(db, titulo=pelicula.tituloPelicula)
    if db_pelicula:
        raise HTTPException(status_code=400, detail="Película ya existe")
    return crud.create_pelicula(db=db, pelicula=pelicula)

@app.get("/peliculas/", response_model=list[schemas.Pelicula])
def leer_peliculas(
    skip: int = 0, 
    limit: int = 100, 
    titulo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    peliculas = crud.get_peliculas(db, skip=skip, limit=limit, titulo=titulo) 
    return peliculas

@app.get("/peliculas/{pelicula_id}", response_model=schemas.Pelicula)
def leer_pelicula(pelicula_id: int, db: Session = Depends(get_db)):
    db_pelicula = crud.get_pelicula(db, pelicula_id=pelicula_id)
    if db_pelicula is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_pelicula

# Endpoints para Reviews
@app.post("/reviews/", response_model=schemas.Review)
def crear_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Verificar que el usuario existe
    usuario = crud.get_usuario(db, usuario_id=review.numPersonaReview)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que la película existe
    pelicula = crud.get_pelicula(db, pelicula_id=review.numPeliculareview)
    if not pelicula:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    return crud.create_review(db=db, review=review)

@app.get("/reviews/", response_model=list[schemas.Review])
def leer_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = crud.get_reviews(db, skip=skip, limit=limit)
    return reviews

@app.get("/reviews/{review_id}", response_model=schemas.Review)
def leer_review(review_id: int, db: Session = Depends(get_db)):
    db_review = crud.get_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review no encontrada")
    return db_review

@app.get("/usuarios/{usuario_id}/reviews/", response_model=list[schemas.Review])
def leer_reviews_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return crud.get_reviews_by_usuario(db, usuario_id=usuario_id)

@app.get("/peliculas/{pelicula_id}/reviews/", response_model=list[schemas.Review])
def leer_reviews_pelicula(pelicula_id: int, db: Session = Depends(get_db)):
    return crud.get_reviews_by_pelicula(db, pelicula_id=pelicula_id)

# Agregar CORS para permitir requests desde Svelte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de desarrollo de Svelte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint para crear reseña desde el formulario
# Endpoint para crear reseña desde el formulario CON ANÁLISIS DE IA
@app.post("/crear-resena/")
async def crear_resena_completa(
    nombre: str = Form(...),
    apellido: str = Form(...), 
    pelicula: str = Form(...),
    reseña: str = Form(...),  # <-- Con ñ
    db: Session = Depends(get_db)
):
    try:
        print(f"Datos recibidos: {nombre}, {apellido}, {pelicula}, {reseña}")  # Debug
        
        # 1. Buscar o crear usuario (usando email temporal)
        email_temp = f"{nombre}.{apellido}@temp.com"
        usuario = crud.get_usuario_by_email(db, email_temp)
        
        if not usuario:
            # Crear usuario temporal
            usuario_data = schemas.UsuarioCreate(
                nombreUsuario=nombre,
                apellidoUsuario=apellido,
                correoUsuario=email_temp,
                sexoUsuario="No especificado",
                generoFavUsuario="No especificado"
            )
            usuario = crud.create_usuario(db, usuario_data)
            print(f"Usuario creado: {usuario.idUsuario}")
        
        # 2. Buscar película por título
        pelicula_db = crud.get_pelicula_by_titulo(db, pelicula)
        if not pelicula_db:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        # 3. ANALIZAR LA RESEÑA CON IA
        print("🤖 Analizando reseña con IA...")
        analisis_ia = sentiment_analyzer.analyze_sentiment(reseña)
        print(f"✅ Resultado IA: {analisis_ia}")
        
        # 4. Crear la reseña
        review_data = schemas.ReviewCreate(
            textReview=reseña,
            numPersonaReview=usuario.idUsuario,
            numPeliculareview=pelicula_db.idPelicula
        )
        
        review = crud.create_review(db, review_data)
        print(f"Reseña creada: {review.idReview}")
        
        # 5. Devolver respuesta con análisis de IA
        return {
            "mensaje": "Reseña creada y analizada exitosamente",
            "usuario_id": usuario.idUsuario,
            "pelicula_id": pelicula_db.idPelicula,
            "review_id": review.idReview,
            "analisis_ia": analisis_ia  # ← NUEVO: resultado de la IA
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completo: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear reseña: {str(e)}")