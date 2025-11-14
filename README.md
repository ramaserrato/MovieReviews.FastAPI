# 🎬 MovieReviews.FastAPI

Una API RESTful para gestión de reviews de películas construida con FastAPI, SQLAlchemy y autenticación JWT.

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.11 o superior
- Git

### Instalación Automática

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd MovieReviews.FastAPI
   ```

2. **Instalar dependencias** (solo primera vez)
   ```bash
   chmod +x install.sh run.sh
   ./install.sh
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

4. **Ejecutar el proyecto**
   ```bash
   ./run.sh
   ```

5. **Abrir en el navegador**
   - 📚 Documentación interactiva: http://localhost:8000/docs
   - 📖 Documentación alternativa: http://localhost:8000/redoc

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
# Base de Datos (elegir una opción)

# Opción 1: MySQL (recomendado para producción)
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/movie_reviews

# Opción 2: SQLite (recomendado para desarrollo)
DATABASE_URL=sqlite:///./movie_reviews.db

# Seguridad
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de la aplicación
DEBUG=True
```

### Configuración de Base de Datos

#### Para SQLite (Más simple):
```python
# En app/database.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./movie_reviews.db"
```

#### Para MySQL:
1. Asegurate de tener MySQL instalado y corriendo
2. Crear una base de datos llamada `movie_reviews`
3. Usar las credenciales correctas en `DATABASE_URL`

## 📁 Estructura del Proyecto

```
MovieReviews.FastAPI/
├── app/                 # Módulos de la aplicación
│   ├── models.py       # Modelos de SQLAlchemy
│   ├── schemas.py      # Esquemas de Pydantic
│   ├── crud.py         # Operaciones de base de datos
│   ├── database.py     # Configuración de DB
│   └── auth.py         # Autenticación JWT
├── main.py             # Punto de entrada
├── requirements.txt    # Dependencias
├── .env.example        # Template de variables
└── README.md          # Este archivo
```

## 🛠️ Scripts Disponibles

### `install.sh`
- Crea entorno virtual
- Instala todas las dependencias
- Configura el proyecto

### `run.sh` 
- Activa el entorno virtual
- Verifica dependencias
- Inicia el servidor de desarrollo

### `start.bat`
- Versión para Windows

## 🎮 Uso de la API

### Endpoints Principales

- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión
- `GET /movies` - Listar películas
- `POST /movies` - Crear película (requiere auth)
- `POST /reviews` - Crear review (requiere auth)
- `GET /reviews/{movie_id}` - Obtener reviews de una película

### Ejemplo de Uso

```bash
# Registrar usuario
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password"}'

# Usar token para acceder a endpoints protegidos
curl -X GET "http://localhost:8000/movies" \
     -H "Authorization: Bearer <tu_token_jwt>"
```

## 🔧 Comandos Manuales

Si preferís no usar los scripts automáticos:

```bash
# Crear y activar entorno virtual
python -m venv venv
source venv/Scripts/activate  # Linux/Mac
# venv\Scripts\activate.bat   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 URLs Importantes

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc  
- **Servidor**: http://localhost:8000

## 🛡️ Seguridad

- Autenticación JWT
- Contraseñas hasheadas con bcrypt
- Validación de datos con Pydantic
- CORS habilitado

## ⚠️ Notas de Desarrollo

- El servidor se reinicia automáticamente con cambios (--reload)
- Para detener: `Ctrl + C`
- Puerto por defecto: 8000
- Modo debug activado en desarrollo

## 🐛 Solución de Problemas

### Error de conexión a base de datos
- Verificar que MySQL esté corriendo (si usás MySQL)
- Revisar credenciales en `.env`
- Para desarrollo, usar SQLite es más simple

### Módulos no encontrados
- Ejecutar `./install.sh` nuevamente
- Verificar que el entorno virtual esté activado

### Puerto en uso
- Cambiar puerto en `run.sh`: `--port 8001`

---
