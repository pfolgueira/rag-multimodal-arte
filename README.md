# Art-RAG: Multimodal Semantic Search for Artwork

[![CI](https://github.com/Pablo/rag-multimodal-arte/actions/workflows/ci.yaml/badge.svg)](https://github.com/Pablo/rag-multimodal-arte/actions/workflows/ci.yaml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Docker](https://img.shields.io/badge/docker-ready-2496ed?logo=docker)](Dockerfile)

> Search for art the way you think about it — by atmosphere, color palette, mood, or composition.

Search the [Rijksmuseum](https://www.rijksmuseum.nl/en) collection using natural language. Instead of filtering by tags or titles, describe what you're looking for: *"A gloomy landscape with bold brushstrokes and a stormy sky"* or *"A serene portrait with soft lighting and pearl details"*.

**[Try the live demo](https://rag-multimodal-arte.vercel.app/)**

![Interface screenshot](imgs/interface_example.png)

---

## Features

- **Semantic search** — query by mood, lighting, technique, or objects using vector embeddings
- **Metadata filters** — narrow results by artist, title, artwork type, or year range
- **Multilingual UI** — English / Spanish with one click
- **Dark mode** — respects system preference, persists your choice
- **Detail modal** — click any result to read the full VLM-generated art analysis
- **VLM-powered descriptions** — Google Gemini generates rich, structured descriptions for each artwork
- **Dual vector indices** — ChromaDB (production API with filters) + FAISS (offline prototyping)

---

## Architecture

```text
┌─────────────┐    ┌──────────────────┐    ┌────────────────┐    ┌──────────────┐
│  Rijksmuseum │    │  Gemini VLM      │    │  BGE-M3        │    │  ChromaDB /  │
│  Images      │───▶│  (generate desc) │───▶│  (embeddings)  │───▶│  FAISS       │
└─────────────┘    └──────────────────┘    └────────────────┘    └──────┬───────┘
                                                                        │
                                                                        ▼
┌──────────────┐    ┌──────────────────┐    ┌─────────────────────────┐ │
│  React UI    │◀───│  FastAPI         │◀───│  /search endpoint       │◀┘
│  (Vite +     │    │  (CORS + static) │    │  (semantic + filters)   │
│   Tailwind)  │    └──────────────────┘    └─────────────────────────┘
└──────────────┘
```

### Pipeline phases

1. **Indexing** — Images are sent to Google Gemini, which generates detailed art-historical descriptions. These descriptions are embedded with `BAAI/bge-m3` (SentenceTransformers) and stored in ChromaDB with metadata (title, artist, date, type).
2. **API** — FastAPI server exposes `GET /search` that accepts a natural language query and optional filters. It encodes the query with the same model, performs vector search in ChromaDB, and returns ranked results.
3. **UI** — React app (Vite + Tailwind) lets users type queries, adjust filters, browse results in a responsive grid, and inspect full descriptions in a modal.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Vector DB | ChromaDB, FAISS |
| Embeddings | SentenceTransformers (`BAAI/bge-m3`) |
| VLM | Google Gemini (`google-genai`) |
| Frontend | React 19, Vite, Tailwind CSS |
| Package mgmt | `uv` (Python), npm (frontend) |
| Container | Docker |
| CI | GitHub Actions |
| Deployment | Oracle Cloud (backend), Vercel (frontend) |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- `uv` (recommended) or `pip`

### 1. Clone & download the dataset

```bash
git clone https://github.com/Pablo/rag-multimodal-arte.git
cd rag-multimodal-arte
```

Download the images from Google Drive and place them in `dataset/`:

- [`selected_images`](https://drive.google.com/file/d/1BpIQK04vqM0vkOShM9gd4Byb1YbO-L1Z/view?usp=sharing)
- [`test_dataset`](https://drive.google.com/file/d/1hNLfZ6celhMptZNT4wK6wGMnFu82aFLF/view?usp=sharing)

```
dataset/
├── selected_images/
└── test_dataset/
```

### 2. Backend

```bash
# Install dependencies
uv sync

# Start the API (development)
cd backend
uv run uvicorn api_chroma:app --reload
```

The API is now running at `http://localhost:8000`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### Alternative: pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
cd backend
uvicorn api_chroma:app --reload
```

---

## Configuration

### Backend (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PUBLIC_URL` | `http://localhost:8000` | Public URL for serving images |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS origins (comma-separated) |
| `CHROMA_DB_PATH` | `../embeddings/chroma_db` | Path to ChromaDB persistent storage |
| `IMAGE_DIR` | `../dataset/selected_images` | Directory with artwork images |

### Frontend (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |

---

## API Reference

### `GET /search`

Perform a semantic search across the artwork collection.

**Query parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | `""` | Natural language search query |
| `k` | int | `5` | Number of results to return |
| `author` | string | — | Filter by artist name (substring match) |
| `tipo` | string | — | Filter by art type (`painting`, `drawing`, `photograph`, `photomechanical print`) |
| `year_min` | int | — | Minimum year |
| `year_max` | int | — | Maximum year |
| `title` | string | — | Filter by title (substring match) |

**Example response:**

```json
[
  {
    "score": 0.723,
    "image_id": "SK-A-3236",
    "image_path": "http://localhost:8000/images/SK-A-3236.jpg",
    "title": "Portrait of a Young Woman",
    "author": "Johannes Vermeer",
    "anio": "1665",
    "tipo": "painting",
    "description": "This painting depicts a young woman..."
  }
]
```

---

## Evaluation

The system is benchmarked with **13 curated queries** spanning paintings, drawings, and photographs. Each query targets a specific artwork by describing its mood, composition, colors, and objects.

```bash
uv run python backend/test_semantic_search.py
```

---

## Project Structure

```text
.
├── backend/
│   ├── api_chroma.py                  # FastAPI server
│   ├── create_chromadb_collection.py  # Build ChromaDB index
│   ├── create_faiss_index.py          # Build FAISS index
│   ├── generate_descriptions.py       # Gemini VLM pipeline
│   ├── generate_embeddings.py         # BGE-M3 embedding generation
│   ├── retrieve_results.py            # FAISS retrieval script
│   └── test_semantic_search.py        # Evaluation benchmark
├── frontend/
│   ├── src/
│   │   ├── App.jsx                    # Main search UI
│   │   └── i18n/                      # English / Spanish translations
│   ├── package.json
│   └── vite.config.js
├── data/
│   └── resultados_arte.csv            # VLM-generated descriptions
├── embeddings/
│   ├── chroma_db/                     # ChromaDB persistent store
│   ├── embeddings_arte_bge_m3.npy     # Pre-computed embeddings
│   └── arte_rijksmuseum.index         # FAISS index
├── imgs/
│   └── interface_example.png          # Screenshot
├── notebooks/                         # EDA and experimentation
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## Dataset

The project uses the [Rijksmuseum](https://www.rijksmuseum.nl/en) art collection. Images come from the museum's public dataset and include paintings, drawings, photographs, and photomechanical prints spanning several centuries.

The dataset is split into two parts:

- **`selected_images/`** — ~4,000 images used for the semantic search index
- **`test_dataset/`** — additional images for evaluation

Both must be downloaded separately (see Quick Start above) as they are not included in the repository.

---

## License

MIT License — feel free to use, modify, and adapt.

---

## Contributing

Issues and pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.
