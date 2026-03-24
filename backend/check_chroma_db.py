import chromadb

"""Script para comprobar si la conexión con ChromaDB funciona correctamente."""

client = chromadb.PersistentClient(path="../embeddings/chroma_db")

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