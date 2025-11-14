# --- Inicio: Contenido de modelo-final.py ---
import joblib
import re
import nltk
from nltk.corpus import stopwords
import sys
import logging
from typing import Literal, Optional, Set
from deep_translator import GoogleTranslator  # <-- 1. IMPORTAR LA LIBRERÍA

# --- Configuración del Logging ---
logging.basicConfig(
    level=logging.INFO, 
    format='[%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

# --- Constantes ---
PIPELINE_PATH = "sentimiento_pipeline.pkl"
SENTIMIENTO_POSITIVO = "Positivo"
SENTIMIENTO_NEGATIVO = "Negativo"
SENTIMIENTO_NEUTRO = "Neutro"

# Umbrales para clasificación
NEUTRAL_THRESHOLD_HIGH = 0.65
NEUTRAL_THRESHOLD_LOW = 0.15

# --- Funciones de Carga (se ejecutan solo una vez) ---

def _cargar_stopwords() -> Set[str]:
    """
    Carga stopwords de NLTK y elimina las palabras de negación.
    Se ejecuta una vez cuando se importa el módulo.
    """
    try:
        stop_words_original = set(stopwords.words('english'))
    except LookupError:
        log.info("Recursos de NLTK 'stopwords' no encontrados. Descargando...")
        nltk.download('stopwords')
        stop_words_original = set(stopwords.words('english'))

    negaciones = {
        'no', 'nor', 'not', 'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't",
        'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 
        'havn', "haven't", 'isn', "isn't", 'mightn', "mightn't", 'mustn', "mustn't",
        'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
        'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
    }
    
    stop_words_modificadas = stop_words_original - negaciones
    log.info(f"Stopwords cargadas (se mantienen {len(negaciones)} palabras de negación).")
    return stop_words_modificadas

def _cargar_pipeline(filepath: str) -> Optional[object]:
    """
    Carga el pipeline de sentimiento desde el archivo .pkl.
    Se ejecuta una vez cuando se importa el módulo.
    """
    try:
        # Asumimos que el .pkl está en la misma carpeta que este script
        pipeline = joblib.load(filepath)
        log.info(f"Pipeline de sentimiento cargado desde '{filepath}'")
        return pipeline
    except FileNotFoundError:
        log.error(f"¡ERROR! Archivo del pipeline no encontrado: '{filepath}'")
        log.error("Asegúrate de que 'sentimiento_pipeline.pkl' esté en la misma carpeta.")
        return None
    except Exception as e:
        log.error(f"¡ERROR! No se pudo cargar el pipeline: {e}", exc_info=True)
        return None

# --- Inicialización Global ---
STOP_WORDS_MODIFICADAS = _cargar_stopwords()
PIPELINE = _cargar_pipeline(PIPELINE_PATH)

# --- Funciones Principales ---

def normalizar_texto(texto: str) -> str:
    """
    Limpia el texto. Esta función AHORA SÓLO debe procesar inglés,
    ya que la traducción se hace antes.
    """
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = re.sub(r'<br\s*/?>', ' ', texto) # Eliminar HTML
    texto = re.sub(r'[^a-zA-Z\s]', '', texto) # Eliminar no-alfabéticos
    
    palabras = [
        palabra for palabra in texto.split() 
        if palabra not in STOP_WORDS_MODIFICADAS
    ]
    
    return ' '.join(palabras) 

def clasificar_sentimiento(
    texto_resena: str,
    debug: bool = False
) -> Literal["Positivo", "Negativo", "Neutro", None]:
    """
    Traduce (si es necesario) y clasifica una reseña como
    Positiva, Negativa o Neutra.
    """
    if PIPELINE is None:
        log.warning("El pipeline no está cargado. Saltando clasificación.")
        return None

    if not isinstance(texto_resena, str) or not texto_resena.strip():
        return None # No clasificar texto vacío

    # --- 2. PASO DE TRADUCCIÓN ---
    texto_para_normalizar = texto_resena
    try:
        # Traducir de 'auto' (detecta idioma) a inglés ('en')
        # Poner un timeout corto para que la API no se cuelgue si el traductor falla
        # NOTA: deep-translator maneja internamente la rotación de IPs/APIs de Google
        texto_traducido = GoogleTranslator(source='auto', target='en').translate(text=texto_resena, timeout=5)
        
        # A veces deep-translator devuelve None si falla o el texto es idéntico
        if texto_traducido:
            texto_para_normalizar = texto_traducido
            if debug:
                log.info(f"Debug: Texto Original = {texto_resena[:60]}...")
                log.info(f"Debug: Texto Traducido (EN) = {texto_traducido[:60]}...")
        else:
             if debug:
                log.info(f"Debug: Traducción devolvió None o es idéntico. Usando texto original.")

    except Exception as e:
        # No mostrar el traceback completo en producción, solo el error.
        # Es común que falle si el texto es muy corto o incomprensible.
        log.warning(f"Error durante la traducción: {e}. Se usará el texto original.")
        # Fallback: si la traducción falla, intenta clasificar el texto original
        texto_para_normalizar = texto_resena
    # --- FIN DEL PASO DE TRADUCCIÓN ---

    # 3. Normalizar el texto (que ahora está en inglés)
    texto_normalizado = normalizar_texto(texto_para_normalizar)
    
    if not texto_normalizado.strip():
        # Esto puede pasar si la reseña solo contenía stopwords
        return None # No clasificar si la normalización lo deja vacío

    # 4. Obtener probabilidades
    try:
        probabilidades = PIPELINE.predict_proba([texto_normalizado])
        prob_positiva = probabilidades[0][1] # Probabilidad de ser 'positivo' (clase 1)

        if debug:
            log.info(f"Debug: Prob Positiva = {prob_positiva:.4f} | Texto: '{texto_normalizado[:50]}...'")

        # 5. Aplicar lógica de 3 clases
        if prob_positiva > NEUTRAL_THRESHOLD_HIGH:
            return SENTIMIENTO_POSITIVO
        elif prob_positiva < NEUTRAL_THRESHOLD_LOW:
            return SENTIMIENTO_NEGATIVO
        else:
            return SENTIMIENTO_NEUTRO

    except Exception as e:
        log.error(f"Falla al predecir probabilidad: {e}", exc_info=True)
        return None

# --- Pruebas rápidas al ejecutar el archivo ---
if __name__ == "__main__":
    if PIPELINE:
        print("\n--- Realizando pruebas de clasificación (con lógica neutra) ---")

        # Configurar el logger para que muestre mensajes DEBUG solo durante la prueba
        logging.getLogger().setLevel(logging.INFO) # Cambiado a INFO para ver los logs de debug

        resenas_prueba = [
            # --- Casos en Inglés (como antes) ---
            "I absolutely loved this film. One of the best I've seen!",
            "A complete waste of time. The plot was boring and the acting was terrible.",
            "The movie was okay. Not great, but not terrible either. Some parts were interesting.",
            "I didn't hate it, but I also didn't love it. It was just average.",
            
            # --- NUEVOS Casos en Español ---
            "Esta película fue una absoluta maravilla. De las mejores que he visto.",
            "Una completa pérdida de tiempo. La trama era aburrida y las actuaciones terribles.",
            "La película estuvo bien. No fue genial, pero tampoco fue terrible. Algunas partes fueron interesantes.",
            "No la odié, pero tampoco me encantó. Simplemente pasable."
        ]
        
        for resena in resenas_prueba:
            # Pasamos debug=True para ver las probabilidades y la traducción
            resultado = clasificar_sentimiento(resena, debug=True)
            print(f"'{resena[:60]}...' -> {resultado}\n")

    else:
        print("\n[INFO] No se pueden ejecutar pruebas porque el pipeline no está cargado.")
# --- Fin: Contenido de modelo-final.py ---