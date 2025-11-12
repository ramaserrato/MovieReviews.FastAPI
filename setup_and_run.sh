#!/bin/bash
echo "🎯 INSTALACIÓN Y EJECUCIÓN AUTOMÁTICA"
echo "======================================"

# Si no existe el entorno, instalar
if [ ! -d "venv" ]; then
    echo "📦 Instalando dependencias..."
    ./install.sh
fi

# Ejecutar
echo "🚀 Iniciando servidor..."
./run.sh