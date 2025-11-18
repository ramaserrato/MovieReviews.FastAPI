#!/usr/bin/env python3
import joblib
import re
import nltk
import os
from nltk.corpus import stopwords

# Encontrar y cargar el modelo
def cargar_modelo():
    posibles_rutas = [
        'machine-learning/sentimiento_pipeline.pkl',
        'sentimiento_pipeline.pkl', 
        '../machine-learning/sentimiento_pipeline.pkl'
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            modelo = joblib.load(ruta)
            print(f"✅ Modelo cargado desde: {ruta}")
            return modelo
    
    raise FileNotFoundError("No se encontró el archivo del modelo")

# Cargar stopwords
def cargar_stopwords():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("📥 Descargando stopwords...")
        nltk.download('stopwords')
    
    stop_words = set(stopwords.words('english'))
    negaciones = {'no', 'nor', 'not', 'don', "don't", 'ain', 'aren', "aren't"}
    return stop_words - negaciones

# Preprocesar texto
def preprocesar_texto(texto, stop_words):
    texto = texto.lower()
    texto = re.sub(r'[^a-zA-Z\s]', '', texto)
    palabras = [p for p in texto.split() if p not in stop_words]
    return ' '.join(palabras)

# Analizar sentimiento
def analizar_sentimiento(texto, modelo, stop_words):
    texto_procesado = preprocesar_texto(texto, stop_words)
    probabilidades = modelo.predict_proba([texto_procesado])
    prob_positiva = probabilidades[0][1]
    
    if prob_positiva > 0.65:
        sentimiento = "POSITIVO"
    elif prob_positiva < 0.15:
        sentimiento = "NEGATIVO"
    else:
        sentimiento = "NEUTRO"
    
    return {
        'resultado': sentimiento,
        'porcentaje': prob_positiva,
        'texto_procesado': texto_procesado
    }

# Programa principal
def main():
    print("🎬 ANALIZADOR DE SENTIMIENTOS PARA RESEÑAS DE PELÍCULAS")
    print("=" * 55)
    print("Escribe tus reseñas y la IA te dirá si son positivas, negativas o neutras")
    print("Escribe 'salir' para terminar\n")
    
    try:
        modelo = cargar_modelo()
        stop_words = cargar_stopwords()
        print("✅ Sistema listo para analizar reseñas!\n")
        
        while True:
            # Leer reseña del usuario
            reseña = input("📝 Escribe tu reseña: ").strip()
            
            if reseña.lower() in ['salir', 'exit', 'quit', 'q']:
                print("👋 ¡Hasta luego!")
                break
            
            if not reseña:
                print("⚠️  Por favor, escribe una reseña\n")
                continue
            
            # Analizar la reseña
            resultado = analizar_sentimiento(reseña, modelo, stop_words)
            
            # Mostrar resultados
            print(f"\n🎯 RESULTADO:")
            print(f"   {resultado['emoji']} Sentimiento: {resultado['sentimiento']}")
            print(f"   📊 Confianza: {resultado['confianza']:.2%}")
            print(f"   🔍 Texto procesado: '{resultado['texto_procesado']}'")
            print("-" * 50 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegurate de estar en la carpeta correcta del proyecto")

if __name__ == "__main__":
    main()