import joblib
import re
import nltk
from nltk.corpus import stopwords
import sys
import logging
from typing import Literal, Optional, Set

# --- Configuración del Logging ---
# Usar logging es más profesional que print()
# Los logs irán a la consola (stderr por defecto)
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
        pipeline = joblib.load(filepath)
        log.info(f"Pipeline de sentimiento cargado desde '{filepath}'")
        return pipeline
    except FileNotFoundError:
        log.error(f"¡ERROR! Archivo del pipeline no encontrado: '{filepath}'")
        log.error("Asegúrate de ejecutar 'entrenar_modelo.py' primero.")
        return None
    except Exception as e:
        log.error(f"¡ERROR! No se pudo cargar el pipeline: {e}", exc_info=True)
        return None

# --- Inicialización Global ---
# Estas variables se crean UNA VEZ cuando FastAPI inicia e importa este archivo.
# Esto es mucho más eficiente que cargarlas en cada llamada a la API.
STOP_WORDS_MODIFICADAS = _cargar_stopwords()
PIPELINE = _cargar_pipeline(PIPELINE_PATH)

# --- Funciones Principales ---

def normalizar_texto(texto: str) -> str:
    """
    Limpia el texto. 
    
    ADVERTENCIA: Esta función es una copia de la que está en 'entrenar_modelo.py'.
    Si la cambias aquí, ¡debes cambiarla allí también y re-entrenar!
    Lo ideal es tener esta función en un 'utils.py' e importarla en ambos scripts.
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
    Clasifica una reseña como Positiva, Negativa o Neutra usando probabilidades.
    """
    if PIPELINE is None:
        log.warning("El pipeline no está cargado. Saltando clasificación.")
        return None

    if not isinstance(texto_resena, str) or not texto_resena.strip():
        return None # No clasificar texto vacío

    # 1. Normalizar el texto de entrada
    texto_normalizado = normalizar_texto(texto_resena)
    
    if not texto_normalizado.strip():
        return None # No clasificar si la normalización lo deja vacío

    # 2. Obtener probabilidades
    try:
        # El pipeline se encarga de la vectorización automáticamente
        probabilidades = PIPELINE.predict_proba([texto_normalizado])
        prob_positiva = probabilidades[0][1] # Probabilidad de ser 'positivo' (clase 1)

        if debug:
            # log.debug no se mostrará a menos que configures level=logging.DEBUG
            # Usamos info por ahora para que sea visible
            log.info(f"Debug: Prob Positiva = {prob_positiva:.4f} | Texto: '{texto_normalizado[:50]}...'")

        # 3. Aplicar lógica de 3 clases
        if prob_positiva > NEUTRAL_THRESHOLD_HIGH:
            return SENTIMIENTO_POSITIVO
        elif prob_positiva < NEUTRAL_THRESHOLD_LOW:
            return SENTIMIENTO_NEGATIVO
        else:
            return SENTIMIENTO_NEUTRO

    except Exception as e:
        # log.error con exc_info=True imprimirá el error completo (traceback)
        log.error(f"Falla al predecir probabilidad: {e}", exc_info=True)
        return None

# --- Pruebas rápidas al ejecutar el archivo ---
if __name__ == "__main__":
    if PIPELINE:
        print("\n--- Realizando pruebas de clasificación (con lógica neutra) ---")

        # Configurar el logger para que muestre mensajes DEBUG solo durante la prueba
        logging.getLogger().setLevel(logging.DEBUG)

        resenas_prueba = [
            "I absolutely loved this film. One of the best I've seen!",
            "A complete waste of time. The plot was boring and the acting was terrible.",
            "The movie was okay. Not great, but not terrible either. Some parts were interesting.",
            "I didn't hate it, but I also didn't love it. It was just average."
        ]
        
        for resena in resenas_prueba:
            # Pasamos debug=True para ver las probabilidades
            resultado = clasificar_sentimiento(resena, debug=True)
            print(f"'{resena[:60]}...' -> {resultado}\n")

    else:
        print("\n[INFO] No se pueden ejecutar pruebas porque el pipeline no está cargado.")