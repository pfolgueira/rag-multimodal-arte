from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import uvicorn
import os
from typing import Optional
from dotenv import load_dotenv
import requests
import numpy as np

# Load variables from the .env file into the system environment
load_dotenv()

app = FastAPI()

# 1. Read Environment Variables with local fallbacks
# split(",") allows us to pass multiple URLs separated by commas in the server
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://localhost:8000")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "baai/bge-m3"
)
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "../embeddings/chroma_db")
IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL")

# 2. Apply CORS using the environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_data = {}

@app.on_event("startup")
async def startup_event():
    print("Cargando recursos...")
    
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    app_data["collection"] = client.get_collection(name="rag_obras_arte")
    
    print("Modelo de embeddgins cargado y BD inicializada.")

class ImageResult(BaseModel):
    score: float
    image_id: str
    image_path: str
    title: str
    author: str
    anio: str
    tipo: str
    description: str

def build_where_filter(tipo: Optional[str],
                       year_min: Optional[int],
                       year_max: Optional[int]) -> Optional[dict]:
    filters = []
    if tipo:
        filters.append({"type": {"$eq": tipo}})
    if year_min is not None:
        filters.append({"year_numeric": {"$gte": year_min}})
    if year_max is not None:
        filters.append({"year_numeric": {"$lte": year_max}})

    if not filters:
        return None
    if len(filters) == 1:
        return filters[0]
    return {"$and": filters}


def match_text(value, filter_text):
    if not filter_text:
        return True
    if not value:
        return False
    return filter_text.lower() in str(value).lower()


def get_embedding(text: str):
    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
            "encoding_format": "float"
        },
        timeout=30,
    )

    response.raise_for_status()

    embedding = np.array(
        response.json()["data"][0]["embedding"],
        dtype=np.float32
    )

    # Equivalente a normalize_embeddings=True
    norm = np.linalg.norm(embedding)

    if norm == 0:
        raise ValueError("El embedding recibido tiene norma 0.")

    embedding = embedding / norm

    return embedding.tolist()


@app.get("/search", response_model=list[ImageResult])
async def search_art(
    query: str = Query("", description="Texto de búsqueda semántica"),
    k: int = Query(5, description="Número de resultados"),
    author: Optional[str] = Query(None, description="Filtrar por artista"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de obra"),
    year_min: Optional[int] = Query(None, description="Año mínimo"),
    year_max: Optional[int] = Query(None, description="Año máximo"),
    title: Optional[str] = Query(None, description="Filtrar por título"),
):
    collection = app_data["collection"]

    try:
        where_clause = build_where_filter(tipo, year_min, year_max)

        if query and query.strip():
            # Modo semántico: vector search + filtros en ChromaDB + post-filtro en Python
            q_emb = [get_embedding(query)]
            fetch_k = min(k * 10, 500)
            results = collection.query(
                query_embeddings=q_emb,
                n_results=fetch_k,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )

            resultados = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    if len(resultados) >= k:
                        break
                    img_id = results["ids"][0][i]
                    meta = results["metadatas"][0][i]

                    if not match_text(meta.get("artist"), author):
                        continue
                    if not match_text(meta.get("title"), title):
                        continue

                    distancia_bruta = float(results["distances"][0][i])
                    score_similitud = 1.0 - distancia_bruta

                    web_path = f"{IMAGE_BASE_URL}/{img_id}.jpg"

                    resultados.append(ImageResult(
                        score=score_similitud,
                        image_id=img_id,
                        image_path=web_path,
                        title=str(meta.get("title", "Sin título")),
                        author=str(meta.get("artist", "Anónimo")),
                        anio=str(meta.get("date", "Desconocida")),
                        tipo=str(meta.get("type", "Desconocido")),
                        description=str(results["documents"][0][i])
                    ))
        else:
            # Modo filtros: solo metadatos + post-filtro en Python
            results = collection.get(
                where=where_clause,
                limit=4000,
                include=["documents", "metadatas"]
            )

            resultados = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    if len(resultados) >= k:
                        break
                    img_id = results["ids"][i]
                    meta = results["metadatas"][i]

                    if not match_text(meta.get("artist"), author):
                        continue
                    if not match_text(meta.get("title"), title):
                        continue

                    web_path = f"{IMAGE_BASE_URL}/{img_id}.jpg"

                    resultados.append(ImageResult(
                        score=1.0,
                        image_id=img_id,
                        image_path=web_path,
                        title=str(meta.get("title", "Sin título")),
                        author=str(meta.get("artist", "Anónimo")),
                        anio=str(meta.get("date", "Desconocida")),
                        tipo=str(meta.get("type", "Desconocido")),
                        description=str(results["documents"][i])
                    ))

        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)