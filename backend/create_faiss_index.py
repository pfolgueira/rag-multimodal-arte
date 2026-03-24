from sentence_transformers import SentenceTransformer
import numpy as np
import os
import faiss

def load_model():
    """
    Carga el modelo de embeddings correpondiente
    """
    model = SentenceTransformer(
        "BAAI/bge-m3", 
        cache_folder=None 
    )
    return model

def load_embeddings(file_path="../embeddings/embeddings_bge_m3.npy"):
    """
    Carga los embeddings del fichero indicado
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo en: {file_path}")
    
    embeddings = np.load(file_path).astype("float32")

    return embeddings

def create_faiss_index(embeddings, output_folder="../embeddings/vector_index.index"):
    """
    Crea y guarda un índice faiss
    """
    dim = embeddings.shape[1]
    index_desc = faiss.IndexFlatIP(dim)
    index_desc.add(embeddings)

    print(f"Índice FAISS creado | N = {index_desc.ntotal} | Dimensiones = {index_desc.d}")

    faiss.write_index(index_desc, output_folder)
    print(f"Índice FAISS guardado en: {output_folder}")

if __name__ == "__main__":
    model = load_model()
    embeddings = load_embeddings()
    create_faiss_index(embeddings=embeddings, output_folder="../embeddings/vector_index.index")