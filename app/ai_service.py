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
    
    # 🔥 MANTENER PALABRAS CLAVE PARA SENTIMIENTOS
    palabras_importantes = {
        'no', 'not', 'nor', 'but', 'very', 'too', 'so', 'really', 'extremely',
        'absolutely', 'definitely', 'never', 'always', 'nothing', 'none',
        'nobody', 'nowhere', 'neither', 'cannot', 'couldn', "couldn't", 
        'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
        'haven', "haven't", 'isn', "isn't", 'mightn', "mightn't", 'mustn', "mustn't",
        'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn',
        "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
    }
    
    return stop_words - palabras_importantes

# 🔥 PREPROCESAMIENTO MEJORADO QUE PRESERVA NEGACIONES
def preprocesar_texto_mejorado(texto, stop_words):
    texto = texto.lower().strip()
    
    # 🔥 CRÍTICO: Manejar negaciones uniéndolas a la siguiente palabra
    texto = re.sub(r"won't", "will_not", texto)
    texto = re.sub(r"can't", "can_not", texto)
    texto = re.sub(r"n't", "_not", texto)
    
    # Reemplazar "not" por "_not_" para unirlo a la siguiente palabra
    texto = re.sub(r"\bnot\b", "_not_", texto)
    texto = re.sub(r"\bno\b", "_no_", texto)
    texto = re.sub(r"\bnever\b", "_never_", texto)
    
    # Mantener signos de exclamación e interrogación
    texto = re.sub(r'[^a-zA-Z\s!?_]', ' ', texto)
    
    # Reducir espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    # 🔥 Filtrar stopwords pero MANTENER NEGACIONES Y PALABRAS CLAVE
    palabras = []
    for palabra in texto.split():
        # Mantener palabras con guiones bajos (negaciones) y palabras importantes
        if '_' in palabra or palabra not in stop_words:
            palabras.append(palabra)
    
    texto_procesado = ' '.join(palabras)
    
    return texto_procesado

def analizar_sentimiento(texto, modelo, stop_words):
    # Preprocesar preservando negaciones
    texto_procesado = preprocesar_texto_mejorado(texto, stop_words)
    
    # 🔥 DETECTAR PATRONES NEGATIVOS EXPLÍCITAMENTE
    patrones_negativos = [
        r'_not', r'_no', r'_never', r'\bnot\b', r'\bno\b', r'\bnever\b',
        r'\bhate\b', r'\bhated\b', r'\bhating\b', r'\bterrible\b', 
        r'\bawful\b', r'\bhorrible\b', r'\bboring\b', r'\bbored\b',
        r'\bdislike\b', r'\bdisliked\b', r'\bworst\b', r'\bbad\b',
        r'\bwaste\b', r'\brubbish\b', r'\bgarbage\b', r'\bstupid\b',
        r'\bdumb\b', r'\bsucks\b', r'\bsucked\b'
    ]
    
    patrones_positivos = [
        r'\blove\b', r'\bloved\b', r'\bloving\b', r'\bgreat\b', 
        r'\bamazing\b', r'\bawesome\b', r'\bfantastic\b', r'\bexcellent\b',
        r'\bwonderful\b', r'\bbrilliant\b', r'\bperfect\b', r'\bbest\b',
        r'\benjoyed\b', r'\benjoy\b', r'\bfun\b', r'\bfunny\b'
    ]
    
    tiene_negacion = any(re.search(patron, texto_procesado, re.IGNORECASE) for patron in patrones_negativos)
    tiene_positivo = any(re.search(patron, texto_procesado, re.IGNORECASE) for patron in patrones_positivos)
    
    # Debug info
    print(f"🔍 ANALIZANDO: '{texto}'")
    print(f"   Procesado: '{texto_procesado}'")
    print(f"   Tiene negación: {tiene_negacion}")
    print(f"   Tiene positivo: {tiene_positivo}")
    
    try:
        probabilidades = modelo.predict_proba([texto_procesado])
        prob_positiva = probabilidades[0][1]
        
        print(f"   Probabilidad base: {prob_positiva:.3f}")
        
        # 🔥 REGLAS INTELIGENTES - SIEMPRE USAR prob_positiva COMO PORCENTAJE FINAL
        
        # CASO 1: Negación fuerte sin palabras positivas → NEGATIVO (bajamos el porcentaje)
        if tiene_negacion and not tiene_positivo:
            sentimiento = "NEGATIVO"
            porcentaje_final = max(0.0, prob_positiva - 0.3)  # Bajamos el porcentaje
            print("   🎯 Aplicando regla: Negación fuerte -> NEGATIVO")
        
        # CASO 2: Negación pero con palabras positivas (ej: "not bad") 
        elif tiene_negacion and tiene_positivo:
            if prob_positiva > 0.5:
                sentimiento = "POSITIVO"
                porcentaje_final = prob_positiva
                print("   🎯 Aplicando regla: Negación + positivo -> POSITIVO")
            else:
                sentimiento = "NEUTRO"
                porcentaje_final = 0.5  # Forzar neutro
                print("   🎯 Aplicando regla: Negación + positivo -> NEUTRO")
        
        # CASO 3: Palabras positivas sin negación → POSITIVO (subimos el porcentaje)
        elif tiene_positivo and not tiene_negacion:
            if prob_positiva > 0.4:
                sentimiento = "POSITIVO"
                porcentaje_final = min(1.0, prob_positiva + 0.2)  # Subimos el porcentaje
                print("   🎯 Aplicando regla: Positivo claro -> POSITIVO")
            else:
                sentimiento = "NEUTRO"
                porcentaje_final = 0.5
        
        # CASO 4: Comportamiento normal del modelo
        else:
            if prob_positiva > 0.65:
                sentimiento = "POSITIVO"
                porcentaje_final = prob_positiva
            elif prob_positiva < 0.35:
                sentimiento = "NEGATIVO"
                porcentaje_final = prob_positiva  # Mantenemos bajo para negativo
            else:
                sentimiento = "NEUTRO"
                porcentaje_final = 0.5
            print("   🎯 Aplicando regla: Modelo base")
        
        # Asignar emoji
        emoji = "😊" if sentimiento == "POSITIVO" else "😠" if sentimiento == "NEGATIVO" else "😐"
        
        return {
            'resultado': sentimiento,
            'porcentaje': porcentaje_final,  # Siempre representa positividad
            'texto_procesado': texto_procesado,
            'emoji': emoji,
            'confianza': porcentaje_final
        }
        
    except Exception as e:
        print(f"❌ Error en predicción: {e}")
        # Fallback basado en detección de patrones
        if tiene_negacion:
            sentimiento_fallback = "NEGATIVO"
            confianza_fallback = 0.2  # Bajo porque es negativo
            emoji_fallback = "😠"
        elif tiene_positivo:
            sentimiento_fallback = "POSITIVO" 
            confianza_fallback = 0.8  # Alto porque es positivo
            emoji_fallback = "😊"
        else:
            sentimiento_fallback = "NEUTRO"
            confianza_fallback = 0.5  # Medio porque es neutro
            emoji_fallback = "😐"
            
        return {
            'resultado': sentimiento_fallback,
            'porcentaje': confianza_fallback,
            'texto_procesado': texto_procesado,
            'emoji': emoji_fallback,
            'confianza': confianza_fallback
        }




def main():
    print("🎬 ANALIZADOR DE SENTIMIENTOS MEJORADO")
    print("=" * 55)
    print("🔍 Ahora con detección inteligente de negaciones")
    print("=" * 55)
    
    try:
        modelo = cargar_modelo()
        stop_words = cargar_stopwords()
        print("✅ Sistema mejorado listo para analizar!\n")
        
        # Probar casos específicos primero
        casos_prueba = [
            "I did not like this movie",
            "This film is not good", 
            "I hate the acting",
            "The movie was great!",
            "It was okay, nothing special",
            "Not bad actually",
            "I loved the performance but hated the ending",
            "This is the worst movie ever",
            "Amazing cinematography"
        ]
        
        print("🧪 PROBANDO CASOS ESPECÍFICOS:")
        print("-" * 50)
        
        for caso in casos_prueba:
            resultado = analizar_sentimiento(caso, modelo, stop_words)
            print(f"📝 '{caso}'")
            print(f"🎯 {resultado['emoji']} {resultado['resultado']} ({resultado['porcentaje']:.1%})")
            print(f"🔍 '{resultado['texto_procesado']}'")
            print("-" * 40)
        
        print("\n💬 Ahora puedes escribir tus propias reseñas:")
        print("   (Escribe 'salir' para terminar)\n")
        
        # Bucle principal interactivo
        while True:
            reseña = input("📝 Escribe tu reseña: ").strip()
            
            if reseña.lower() in ['salir', 'exit', 'quit', 'q']:
                print("👋 ¡Hasta luego!")
                break
                
            if not reseña:
                print("⚠️  Por favor, escribe una reseña\n")
                continue
                
            resultado = analizar_sentimiento(reseña, modelo, stop_words)
            
            print(f"\n🎯 RESULTADO: {resultado['emoji']} {resultado['resultado']}")
            print(f"📊 Confianza: {resultado['confianza']:.1%}")
            print(f"🔍 Texto procesado: '{resultado['texto_procesado']}'")
            print("-" * 50 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de estar en la carpeta correcta del proyecto")

if __name__ == "__main__":
    main()