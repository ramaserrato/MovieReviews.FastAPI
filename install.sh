#!/bin/bash
echo "🚀 INSTALADOR COMPLETO - MovieReviews.FastAPI"
echo "=============================================="

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Python no encontrado. Instalá Python 3.11+ desde python.org"
    exit 1
fi

echo "✅ Python encontrado: $(python --version)"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python -m venv venv

# Activar entorno
echo "🔧 Activando entorno virtual..."
source venv/Scripts/activate

# Actualizar pip
echo "📚 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv 
pip install python-jose[cryptography] passlib[bcrypt] python-multipart 
pip install cryptography email-validator alembic

# Crear requirements.txt si no existe
if [ ! -f "requirements.txt" ]; then
    echo "📄 Creando requirements.txt..."
    cat > requirements.txt << EOF
fastapi>=0.104.0
uvicorn>=0.24.0
sqlalchemy>=2.0.0
pymysql>=1.0.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.0
python-multipart>=0.0.6
cryptography>=41.0.0
email-validator>=2.0.0
alembic>=1.12.0
EOF
fi

# Instalar desde requirements.txt también
pip install -r requirements.txt

echo ""
echo "✅ ✅ ✅ INSTALACIÓN COMPLETADA ✅ ✅ ✅"
echo ""
echo "🎮 Ahora podés ejecutar: ./run.sh"
echo "🌐 O abrir: http://localhost:8000/docs"
echo ""