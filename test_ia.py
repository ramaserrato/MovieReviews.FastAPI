#!/usr/bin/env python3
"""
TEST IA INTERACTIVO - Escribe reseñas y la IA las analiza
"""
import joblib
import re
import nltk
from nltk.corpus import stopwords

def main():
    print("🎬 ANALIZADOR INTERACTIVO DE SENTIMIENTOS")
    print("=" * 50)
    print("Escribe reseñas y la IA te dirá si son positivas, negativas o neutras")
    print("Escribe 'salir' para terminar\n")
    
    try:
        # Cargar modelo
        modelo = joblib.load('machine-learning/sentimiento_pipeline.pkl')
        print("✅ Modelo cargado")
        
        # Cargar stopwords
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("📥 Descargando stopwords...")
            nltk.download('stopwords')
        
        stop_words = set(stopwords.words('english'))
        negaciones = {'no', 'nor', 'not', 'don', "don't"}
        stop_words_modificadas = stop_words - negaciones
        print("✅ Stopwords cargadas")
        
        def preprocesar(texto):
            texto = texto.lower()
            texto = re.sub(r'[^a-zA-Z\s]', '', texto)
            palabras = [p for p in texto.split() if p not in stop_words_modificadas]
            return ' '.join(palabras)
        
        def analizar_resena(reseña):
            texto_procesado = preprocesar(reseña)
            probabilidades = modelo.predict_proba([texto_procesado])
            prob_positiva = probabilidades[0][1]
            
            if prob_positiva > 0.65:
                return "👍 POSITIVO", prob_positiva, texto_procesado
            elif prob_positiva < 0.15:
                return "👎 NEGATIVO", prob_positiva, texto_procesado
            else:
                return "😐 NEUTRO", prob_positiva, texto_procesado
        
        print("💡 Ejemplos para probar:")
        print("   - 'I loved this movie! Amazing acting!'")
        print("   - 'Terrible film, boring and bad acting'")
        print("   - 'It was okay, nothing special'")
        print("   - 'This is the worst movie ever made'")
        print("   - 'Brilliant cinematography and great performances'")
        print()
        
        # Bucle interactivo
        while True:
            try:
                # Pedir input al usuario
                reseña = input("📝 Escribe tu reseña: ").strip()
                
                # Verificar si quiere salir
                if reseña.lower() in ['salir', 'exit', 'quit', 'q']:
                    print("👋 ¡Hasta luego!")
                    break
                
                # Verificar que no esté vacío
                if not reseña:
                    print("⚠️  Por favor, escribe una reseña\n")
                    continue
                
                # Analizar la reseña
                resultado, confianza, texto_procesado = analizar_resena(reseña)
                
                # Mostrar resultados
                print(f"\n🎯 RESULTADO:")
                print(f"   {resultado}")
                print(f"   📊 Confianza: {confianza:.2%}")
                print(f"   🔍 Texto procesado: '{texto_procesado}'")
                print("-" * 50)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error analizando la reseña: {e}")
                print()
        
    except Exception as e:
        print(f"❌ Error inicializando: {e}")
        print("💡 Asegurate de que:")
        print("   - Estés en la carpeta correcta del proyecto")
        print("   - El archivo sentimiento_pipeline.pkl esté en machine-learning/")
        print("   - Tengas todas las dependencias instaladas")

if __name__ == "__main__":
    main()