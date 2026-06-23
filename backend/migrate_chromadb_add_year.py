import chromadb
import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

SCRIPT_DIR = Path(__file__).resolve().parent
raw_path = os.getenv("CHROMA_DB_PATH", str(SCRIPT_DIR.parent / "embeddings" / "chroma_db"))
CHROMA_DB_PATH = str((SCRIPT_DIR / raw_path).resolve())

def parse_year_range(date_str):
    years = re.findall(r'\b(\d{4})\b', date_str)
    if not years:
        return None
    return int(years[0])

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_collection(name="rag_obras_arte")

all_data = collection.get(include=["metadatas"])
total = len(all_data["ids"])
print(f"Total registros: {total}")

BATCH_SIZE = 100
for i in range(0, total, BATCH_SIZE):
    end = min(i + BATCH_SIZE, total)
    batch_ids = all_data["ids"][i:end]
    batch_metas = all_data["metadatas"][i:end]

    new_metadatas = []
    for meta in batch_metas:
        date_str = meta.get("date", "")
        if isinstance(date_str, dict):
            date_str = str(date_str.get("date", ""))
        year = parse_year_range(str(date_str))
        meta["year_numeric"] = year
        new_metadatas.append(meta)

    collection.update(ids=batch_ids, metadatas=new_metadatas)
    print(f"Actualizados registros {i} a {end - 1}")

print("Migración completada.")
