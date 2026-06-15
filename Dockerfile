# Use an official lightweight Python image
FROM python:3.12-slim

# Copy the uv binary from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for building certain Python packages (like ChromaDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt-get/lists/*

# Copy the dependencies file first to leverage Docker's caching mechanism
COPY pyproject.toml .

# Install dependencies using uv instead of pip
# --system tells uv to install into the global container Python environment rather than a virtualenv
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy the rest of the application code into the container
COPY backend/ ./backend
COPY data/ ./data
COPY embeddings/ ./embeddings

# Expose the port FastAPI will run on
EXPOSE 8000

# Set the default environment variable for the images directory
ENV IMAGE_DIR="/app/dataset/selected_images"

# Start FastAPI using Uvicorn
CMD ["uvicorn", "backend.api_chroma:app", "--host", "0.0.0.0", "--port", "8000"]