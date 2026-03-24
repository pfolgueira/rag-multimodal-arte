import os
import faiss
import matplotlib.pyplot as plt
from PIL import Image
from sentence_transformers import SentenceTransformer
from generate_embeddings import load_descriptions
from generate_descriptions import load_dataset


def load_faiss_index(file_path="../embeddings/vector_index.index"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el índice en: {file_path}")
    
    # Leer el índice
    index = faiss.read_index(file_path)
    print(f"Índice FAISS cargado. Total de vectores: {index.ntotal}")
    return index

def load_model():
    """
    Carga el modelo de embeddings correpondiente
    """
    model = SentenceTransformer(
        "BAAI/bge-m3", 
        cache_folder=None 
    )
    return model

def _text_embedding_st(text: str):
    v = model.encode([text], normalize_embeddings=True).astype("float32")
    return v

def buscar_por_texto_descripciones(index, desc_paths, query: str, k: int = 5):
    q = _text_embedding_st(query)
    scores, idxs = index.search(q, k)

    scores = scores[0].tolist()
    idxs = idxs[0].tolist()

    paths = ["."+desc_paths[i] for i in idxs]
    img_ids = [os.path.splitext(os.path.basename(p))[0] for p in paths]
    return scores, paths, img_ids, idxs

def mostrar_resultados_descripciones(df, descriptions, query: str, k: int = 5):
    scores, paths, img_ids, idxs = buscar_por_texto_descripciones(index, desc_paths, query, k=k)

    if "id" in df.columns:
        df["id"] = df["id"].astype(str)

    plt.figure(figsize=(3*k, 3))
    for j, (s, p, img_id, idx) in enumerate(zip(scores, paths, img_ids, idxs), start=1):
        plt.subplot(1, k, j)
        plt.imshow(Image.open(p).convert("RGB"))
        plt.axis("off")

        titulo, autor = "", ""
        if "id" in df.columns and (df["id"] == img_id).any():
            row = df[df["id"] == img_id].iloc[0]
            if "title" in df.columns: titulo = str(row.get("title", ""))
            if "principalOrFirstMaker" in df.columns: autor = str(row.get("principalOrFirstMaker", ""))

        desc_short = (descriptions[idx][:60] + "…") if descriptions else ""
        plt.title(f"{s:.3f}\n{titulo}\n{autor}\n{desc_short}", fontsize=8)

    plt.suptitle(query)
    plt.show()


if __name__ == "__main__":
    model = load_model()
    index = load_faiss_index()
    descriptions, desc_paths = load_descriptions()
    df = load_dataset()
    mostrar_resultados_descripciones(df, descriptions, "A sense of profound loneliness and isolation in a city.", k=5)

