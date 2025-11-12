import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline # Importar Pipeline
import joblib
import sys
import csv # <--- Importamos CSV para lectura manual

# --- Configuración de NLTK (LÓGICA MEJORADA) ---
try:
    stop_words_original = set(stopwords.words('english'))
except LookupError:
    print("Descargando stopwords de NLTK...")
    nltk.download('stopwords')
    stop_words_original = set(stopwords.words('english'))

# Define las negaciones que quieres MANTENER
negaciones = {
    'no', 'nor', 'not', 'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 
    'havn', "haven't", 'isn', "isn't", 'mightn', "mightn't", 'mustn', "mustn't",
    'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
    'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

# Crea tu lista final de stopwords quitando las negaciones
stop_words_modificadas = stop_words_original - negaciones
print(f"[OK] Stopwords cargadas (se mantienen {len(negaciones)} palabras de negación).")


def normalizar_texto(texto):
    """Limpia y normaliza el texto de las reseñas."""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = re.sub(r'<br\s*/?>', ' ', texto) # Eliminar HTML
    texto = re.sub(r'[^a-zA-Z\s]', '', texto) # Eliminar no-alfabéticos
    
    # Usa la nueva lista de stopwords
    palabras = [palabra for palabra in texto.split() if palabra not in stop_words_modificadas] 
    
    return ' '.join(palabras)

def cargar_datos(filepath="IMDB Dataset.csv"):
    """
    Carga y preprocesa el dataset (MODO ROBUSTO).
    Lee el CSV manualmente para evitar errores de parsing.
    """
    print(f"Cargando el dataset de reseñas desde '{filepath}' (Modo Robusto)...")
    
    reviews = []
    sentiments = []
    lineas_saltadas = 0

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Usar csv.reader para manejar correctamente las comillas
            reader = csv.reader(f, quotechar='"', delimiter=',')
            
            # Omitir el encabezado (review,sentiment)
            try:
                next(reader) 
            except StopIteration:
                print("[ERROR] Archivo CSV está vacío.", file=sys.stderr)
                sys.exit(1)
            
            # Iterar línea por línea
            for i, row in enumerate(reader):
                # Una fila válida DEBE tener 2 columnas
                if len(row) == 2:
                    reviews.append(row[0])
                    sentiments.append(row[1])
                else:
                    # Esta línea está rota (tiene más/menos de 2 columnas)
                    lineas_saltadas += 1
                    
    except FileNotFoundError:
        print(f"\n[ERROR] Archivo '{filepath}' no encontrado.", file=sys.stderr)
        print("Por favor, descarga el dataset de Kaggle y colócalo en esta carpeta.", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"\n[ERROR] Problema de codificación. Asegúrate de que el CSV esté en UTF-8.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error inesperado al leer el archivo: {e}", file=sys.stderr)
        sys.exit(1)

    if lineas_saltadas > 0:
        print(f"[INFO] Se saltaron {lineas_saltadas} líneas malformadas.")

    # Crear DataFrame desde las listas
    df = pd.DataFrame({
        'review': reviews,
        'sentiment': sentiments
    })

    # --- Limpieza de datos ---
    df.dropna(subset=['review', 'sentiment'], inplace=True)
    df['sentiment'] = df['sentiment'].astype(str).str.strip().str.strip('"')
    df = df[df['sentiment'].isin(['positive', 'negative'])]
    
    print(f"Se encontraron {len(df)} filas válidas después de filtrar.")

    # Si después de filtrar no queda nada, es un problema
    if df.empty:
        print("[ERROR] El DataFrame está vacío después de limpiar y filtrar.")
        print("Verifica el contenido de tu archivo 'IMDB Dataset.csv'.")
        sys.exit(1)

    print("Normalizando texto... (esto puede tardar unos segundos)")
    df['review_normalizada'] = df['review'].apply(normalizar_texto)

    # Mapeo: 1 para 'positive', 0 para 'negative'
    y = df['sentiment'].map({'positive': 1, 'negative': 0})
    X = df['review_normalizada']

    print("Carga y normalización completadas.")
    return X, y

def entrenar_y_evaluar(X, y):
    """Crea, entrena y evalúa el pipeline."""

    # Dividir datos
    print("Dividiendo datos en conjuntos de entrenamiento y prueba...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # --- CREAR EL PIPELINE ---
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=20000, 
            ngram_range=(1, 2)
        )),
        ('clf', LogisticRegression(solver='liblinear', random_state=42))
    ])

    # Entrenar el pipeline
    print(f"Entrenando el pipeline con {len(y_train)} reseñas y {20000} features...")
    pipeline.fit(X_train, y_train)
    print("Entrenamiento completado.")

    # Evaluar el modelo
    print("\nEvaluando el rendimiento del modelo...")
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    reporte = classification_report(y_test, y_pred, target_names=['Negativo', 'Positivo'])

    print(f"\n----------- RESULTADOS DE LA EVALUACIÓN -----------")
    print(f"Precisión Global (Accuracy): {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("\nReporte de Clasificación:")
    print(reporte)
    print("-------------------------------------------------")

    return pipeline

def guardar_pipeline(pipeline, filepath="sentimiento_pipeline.pkl"):
    """Guarda el pipeline entrenado en un archivo."""
    joblib.dump(pipeline, filepath)
    print(f"\n[ÉXITO] Pipeline guardado exitosamente en '{filepath}'")

# --- Ejecución Principal ---
if __name__ == "__main__":
    X_datos, y_labels = cargar_datos()
    modelo_pipeline = entrenar_y_evaluar(X_datos, y_labels)
    guardar_pipeline(modelo_pipeline)