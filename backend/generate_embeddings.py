import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import os

DESCRIPTIONS_PATH = "../data/resultados_arte.csv"

def load_descriptions():
    """
    Carga las descripciones de las obras de arte
    """
    df = pd.read_csv(DESCRIPTIONS_PATH)
    descriptions = df["Descripcion"].tolist()
    desc_paths = df["Ruta_Imagen"].tolist()
    return descriptions, desc_paths

def load_model():
    """
    Carga el modelo de embeddings correpondiente
    """
    model = SentenceTransformer(
        "BAAI/bge-m3", 
        cache_folder=None 
    )
    return model

def generate_embeddings(model, descriptions, filename="embeddings_bge_m3.npy"):
    desc_emb = model.encode(
        descriptions,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=True,
    ).astype("float32")

    output_folder = "../embeddings/"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    save_path = os.path.join(output_folder, filename)
    np.save(save_path, desc_emb)
    
    print(f"Embeddings guardados en: {save_path}")

if __name__ == "__main__":
    descriptions, desc_paths = load_descriptions()
    model = load_model()
    generate_embeddings(model, descriptions)
    



