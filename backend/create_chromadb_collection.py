import numpy as np
import os
import pandas as pd
import chromadb

def load_embeddings(file_path="../embeddings/embeddings_bge_m3.npy"):
    """
    Carga los embeddings del fichero indicado.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo de embeddings en: {file_path}")
    
    return np.load(file_path).astype("float32")

def prepare_data(metadata_path, resultados_path):
    """
    Lee los CSV, extrae el ID de la ruta de la imagen y une los metadatos
    con las descripciones generadas.
    """

    df_meta = pd.read_csv(metadata_path)
    df_res = pd.read_csv(resultados_path)

    df_res['id'] = df_res['Ruta_Imagen'].apply(lambda x: os.path.splitext(os.path.basename(x))[0])

    df_final = pd.merge(df_res, df_meta, on='id', how='inner')

    df_final = df_final.fillna("Desconocido")

    return df_final

def create_chroma_collection_with_metadata(embeddings, df_data, output_folder="../embeddings/chroma_db", collection_name="rag_obras_arte"):
    """
    Crea la colección en ChromaDB insertando vectores, documentos y metadatos.
    """

    if len(embeddings) != len(df_data):
        print(f"⚠️ ADVERTENCIA: Tienes {len(embeddings)} embeddings pero {len(df_data)} filas en el dataframe unificado.")
        print("Asegúrate de que el archivo .npy se generó exactamente para las mismas filas de resultados_arte.csv")
    
    # Inicializar cliente de ChromaDB
    client = chromadb.PersistentClient(path=output_folder)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "ip"} # Producto interno para mayor eficiencia
    )

    # Preparar los datos que queremos incluir en la BD
    embeddings_list = embeddings.tolist()
    documents = df_data['Descripcion'].tolist()
    ids = df_data['id'].astype(str).tolist()
    
    metadatas = []
    for _, row in df_data.iterrows():
        meta_dict = {
            "title": str(row['title']),
            "artist": str(row['artist']),
            "date": str(row['date']),
            "type": str(row['type']),
            "ruta_imagen": str(row['Ruta_Imagen'])
        }
        metadatas.append(meta_dict)

    # Añadir datos a ChromaDB por lotes
    batch_size = 1000
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        
        collection.add(
            embeddings=embeddings_list[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
        print(f"Añadidos a ChromaDB registros del {i} al {end_idx - 1}")

    print(f"\nBase de datos vectorial creada correctamente.")
    print(f"Total de obras almacenadas: {collection.count()}")

if __name__ == "__main__":
    PATH_METADATA = "../dataset/rijksmuseum/rijksmuseum/metadata.csv"
    PATH_RESULTADOS = "../data/resultados_arte.csv"
    PATH_EMBEDDINGS = "../embeddings/embeddings_arte_bge_m3.npy"

    embeddings = load_embeddings(PATH_EMBEDDINGS)

    df_data = prepare_data(PATH_METADATA, PATH_RESULTADOS)

    create_chroma_collection_with_metadata(embeddings=embeddings, df_data=df_data)