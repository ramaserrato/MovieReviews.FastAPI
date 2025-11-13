#!/usr/bin/env python3
import sys
import os

# Ejecutar el archivo modelo-final.py directamente
script_path = os.path.join(os.path.dirname(__file__), 'machine-learning', 'modelo-final.py')

try:
    # Ejecutar el script directamente
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Ejecutar el código
    exec(code)
    print("✅ Script modelo-final.py ejecutado correctamente")
    
except Exception as e:
    print(f"❌ Error ejecutando el script: {e}")