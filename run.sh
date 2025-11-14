#!/bin/bash
echo "🎬 INICIANDO MOVIE REVIEWS FASTAPI"
echo "==================================="

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecutá: ./install.sh"
    exit 1
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/Scripts/activate

# Verificar dependencias
echo "🔍 Verificando dependencias..."
python -c "import fastapi, uvicorn, sqlalchemy, pymysql" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Faltan dependencias. Ejecutá: ./install.sh"
    exit 1
fi

echo "✅ Dependencias verificadas"

# Ejecutar servidor
echo "🚀 Iniciando servidor FastAPI..."
echo "📡 Servidor disponible en:"
echo "   🌐 http://localhost:8000"
echo "   📚 http://localhost:8000/docs"
echo "   📖 http://localhost:8000/redoc"
echo ""
echo "🛑 Presiona Ctrl+C para detener el servidor"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000