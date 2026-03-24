from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
import uvicorn
import os

app = FastAPI()

# CORS  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir imágenes estáticas para poder mostrarlas en el frontend
IMAGE_PATH = "../dataset/selected_images"
if os.path.exists(IMAGE_PATH):
    app.mount("/images", StaticFiles(directory=IMAGE_PATH), name="images")

app_data = {}

@app.on_event("startup")
async def startup_event():
    print("Cargando recursos...")
    
    app_data["model"] = SentenceTransformer("BAAI/bge-m3", cache_folder=None)
    
    client = chromadb.PersistentClient(path="../embeddings/chroma_db")
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

@app.get("/search", response_model=list[ImageResult])
async def search_art(query: str, k: int = 5):
    model = app_data["model"]
    collection = app_data["collection"]

    try:
        # Embedding de la consulta del usuario
        q_emb = model.encode([query], normalize_embeddings=True).astype("float32").tolist()
        
        # Buscar en la BD vectorial
        results = collection.query(
            query_embeddings=q_emb,
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        resultados = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                img_id = results["ids"][0][i]
                meta = results["metadatas"][0][i]

                distancia_bruta = float(results["distances"][0][i])
                score_similitud = 1.0 - distancia_bruta
                
                web_path = f"http://localhost:8000/images/{img_id}.jpg"
                
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
                
        return resultados
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)