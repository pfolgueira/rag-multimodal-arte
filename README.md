# 🎨 Buscador de Arte Semántico

![Interfaz del buscador](imgs/interface_example.png)

## 🗂️ Estructura del proyecto

```text
.
├── pyproject.toml
├── README.md
├── backend/
│   ├── api_chroma.py
│   ├── create_chromadb_collection.py
│   ├── create_faiss_index.py
│   ├── generate_descriptions.py
│   ├── generate_embeddings.py
│   ├── retrieve_results.py
│   └── test_semantic_search.py
├── data/
│   └── resultados_arte.csv
├── embeddings/
│   ├── arte_rijksmuseum.index
│   ├── embeddings_arte_bge_m3.npy
│   └── chroma_db/
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
└── notebooks/
	├── analisis_dataset.ipynb
	└── MS_Challenge_Sesion_Formativa.ipynb
```

Este proyecto está organizado en bloques funcionales para separar claramente el procesamiento de datos, la API y la interfaz web:

- `backend/`: contiene la lógica principal de búsqueda semántica y los scripts para generar descripciones, embeddings e índices (`FAISS` y `ChromaDB`), además de la API en FastAPI.
- `data/`: incluye el fichero con las descripciones generadas por el VLM.
- `dataset/`: carpeta que debe contener las imágenes fuente del proyecto, divididas en `selected_images/` y `test_dataset/`.
- `embeddings/`: almacena los artefactos generados para la búsqueda semántica (indices vectoriales, matrices de embeddings y base de datos de Chroma).
- `frontend/`: aplicacián React (Vite) que se comunica con el backend y permite realizar consultas desde una interfaz visual.
- `notebooks/`: notebooks de exploración y análisis del dataset.
- `pyproject.toml`: define dependencias y configuración del proyecto Python.
- `README.md`: documentación principal de instalación y uso.

## 📥 Descarga del dataset de imagenes

Las imágenes utilizadas en este proyecto no se han incluido en el repositorio.

Puedes descargarlas desde los siguientes enlaces:

- `selected_images`: https://drive.google.com/file/d/1BpIQK04vqM0vkOShM9gd4Byb1YbO-L1Z/view?usp=sharing
- `test_dataset`: https://drive.google.com/file/d/1hNLfZ6celhMptZNT4wK6wGMnFu82aFLF/view?usp=sharing

Para utilizarlas y ejecutar el proyecto correctamente, crea una carpeta `dataset/` en la raíz del proyecto e incluye dentro ambas carpetas descomprimidas:

```text
dataset/
├── selected_images/
└── test_dataset/
```

## ⚙️ Dependencias gestionadas con `uv`

Este proyecto gestiona las dependencias de Python con `uv`, definidas en `pyproject.toml`.

Pasos recomendados:

1. Instalar `uv` si no lo tienes.
2. Desde la raíz del proyecto, sincronizar dependencias:

```bash
uv sync
```

3. Ejecutar scripts y servidor con `uv run` para usar el entorno del proyecto.

4. Arrancar el servidor de desarrollo

```bash
cd backend
uv run uvicorn api_chroma:app --reload
```

## 🐍 Dependencias con `pip` (alternativa directa)

Si prefieres no usar `uv`, puedes gestionar dependencias con `pip` usando un entorno virtual.

1. Crear entorno virtual en la raíz del proyecto:

```bash
python -m venv .venv
```

2. Activar entorno virtual:

```bash
source .venv/bin/activate
```

3. Actualizar `pip` e instalar dependencias desde `pyproject.toml`:

```bash
python -m pip install --upgrade pip
pip install .
```

4. Arrancar backend con el entorno activo:

```bash
cd backend
uvicorn api_chroma:app --reload
```

## 💻 Ejecucion del frontend

```bash
npm install
cd frontend
npm run dev
```
