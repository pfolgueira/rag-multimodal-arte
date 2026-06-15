import chromadb
import os
from dotenv import load_dotenv
from pathlib import Path

# Load variables from the .env file into the system environment
load_dotenv()

"""Script para comprobar si la conexión con ChromaDB funciona correctamente."""

# --- BULLETPROOF PATH RESOLUTION ---
# 1. Find the absolute path of the directory this script is in (backend/)
SCRIPT_DIR = Path(__file__).resolve().parent
# 2. Go up one level to the root, then into embeddings/chroma_db
DEFAULT_DB_PATH = SCRIPT_DIR.parent / "embeddings" / "chroma_db"

# 3. Read the env var, fallback to the absolute path
chroma_path = os.getenv("CHROMA_DB_PATH", str(DEFAULT_DB_PATH))

print(f"🔍 Intentando conectar a la base de datos en: {chroma_path}")

# --- DIAGNOSTIC CHECK ---
sqlite_file = Path(chroma_path) / "chroma.sqlite3"
if sqlite_file.exists():
    size_kb = sqlite_file.stat().st_size / 1024
    print(f"✅ Archivo chroma.sqlite3 encontrado. Tamaño: {size_kb:.2f} KB")
    if size_kb == 0:
        print("⚠️ ¡CUIDADO! El archivo SQLite pesa 0 bytes. Está vacío en GitHub.")
else:
    print("❌ El archivo chroma.sqlite3 NO EXISTE en esta ruta.")

client = chromadb.PersistentClient(path=chroma_path)

collection = client.get_collection(name="rag_obras_arte")

total_registros = collection.count()
print(f"Total de registros en la colección: {total_registros}")

# Extraer 5 primeras obras con sus datos y los mostramos
inspeccion = collection.get(
    limit=5,
    include=["documents", "metadatas"]
)

print("\n--- Muestra de los primeros 5 registros ---")
for i in range(len(inspeccion['ids'])):
    print(f"\nID: {inspeccion['ids'][i]}")
    print(f"Título: {inspeccion['metadatas'][i]['title']}")
    print(f"Artista: {inspeccion['metadatas'][i]['artist']}")
    print(f"Tipo: {inspeccion['metadatas'][i]['type']}")
    print(f"Fecha: {inspeccion['metadatas'][i]['date']}")
    print(f"Descripción (primeros 100 caracteres): {inspeccion['documents'][i][:100]}...")