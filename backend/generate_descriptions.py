import os
import pandas as pd
import glob
import numpy as np
import random
import shutil
import csv
from tqdm.asyncio import tqdm
from google import genai
from google.genai import types
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Rutas de directorios
DESIRED_PATH = "../dataset"
DESTINATION_DIR = os.path.join(DESIRED_PATH, "rijksmuseum")
DATASET_ROOT_DIR = os.path.join(DESTINATION_DIR, "rijksmuseum")

# API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
GEMINI_MODEL = os.getenv("VLM_MODEL")

def load_dataset():
    """
    Cargar el dataset
    """
    os.makedirs(DESIRED_PATH, exist_ok=True)
    data_path = os.path.join(DATASET_ROOT_DIR, "metadata.csv")
    df = pd.read_csv(data_path)
    return df


def print_dataset_info(df):
    """
    Mostrar información del dataset para asegurar que se ha cargado correctamente
    """
    print(df.columns)
    folders = [f for f in os.listdir(DATASET_ROOT_DIR) if os.path.isdir(os.path.join(DATASET_ROOT_DIR, f))]
    print("Carpetas en la subcarpeta del dataset ('rijksmuseum'):", folders)
    total_items_in_subfolders = sum(len(os.listdir(os.path.join(DATASET_ROOT_DIR, folder))) for folder in folders)
    print("Número total de elementos en todas las carpetas dentro de 'rijksmuseum':", total_items_in_subfolders)
    print("Número total de entradas en el dataset (metadata.csv):", len(df))


def get_work_subset(df, num_samples=1000, seed=None):
    """
    Toma un dataframe con las obras artísticas del Rijksmuseum y selecciona aleatoriamente 1000 obras de cada tipo. 
    """
    selected_images_path = os.path.join(DESIRED_PATH, "selected_images")
    os.makedirs(selected_images_path, exist_ok=True)

    folders = [f for f in os.listdir(DATASET_ROOT_DIR) if os.path.isdir(os.path.join(DATASET_ROOT_DIR, f))]

    if seed is not None:
        random.seed(seed)

    total_found = 0
    total_selected = 0
    selected_image_paths = []
    for carpeta in folders:
        ruta_carpeta = os.path.join(DATASET_ROOT_DIR, carpeta)
        imagenes = glob.glob(os.path.join(ruta_carpeta, "*.jpg"))
        n_found = len(imagenes)
        total_found += n_found

        if n_found == 0:
            print(f"{carpeta}: no se encontraron archivos .jpg")
            continue

        # Seleccionar aleatoriamente hasta `num_samples` imágenes de esta carpeta
        selected = imagenes if n_found <= num_samples else random.sample(imagenes, num_samples)
        total_selected += len(selected)
        selected_image_paths.extend(selected)


        print(f"{carpeta}: encontrados {n_found}, seleccionadas {len(selected)}")

    # Copiar todas las imágenes seleccionadas al directorio indicado
    for ruta_img in selected_image_paths:
        shutil.copy2(ruta_img, os.path.join(selected_images_path, os.path.basename(ruta_img)))

    print(f"Se copiaron correctamente {len(selected_image_paths)} imágenes en {selected_images_path}")

    # Extraer los IDs de imagen a partir de selected_image_paths
    ids_imagen_copiados = [os.path.splitext(os.path.basename(p))[0] for p in selected_image_paths]

    # Filtrar el DataFrame original para incluir solo las imágenes seleccionadas
    df_subset = df[df["id"].isin(ids_imagen_copiados)].copy()
    print("Longitud del DataFrame:", len(df_subset))

    return df_subset, selected_image_paths

def generate_descriptions_for_images(selected_image_paths):
    """
    Conexión con la API de gemini para generar la descripción de las imágenes seleccionadas
    """

    client = genai.Client(api_key=GEMINI_API_KEY)

    def _get_image_part(image_path: str) -> types.Part:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        return types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )

    async def describe_image_gemini_async(image_path: str) -> str:
        image_part = _get_image_part(image_path)
        prompt = (
            "Act as an art history expert. "
            "Your task is to analyze this image for an artwork information retrieval system. "
            "Begin the first sentence by explicitly identifying whether the work is a painting, a photograph, a photomechanical print, or a picture. Next, fluidly describe the main subject, the spatial composition, and the use of light. Integrate into the narrative details about the color palette, the technique (such as the type of brushstroke or photographic grain), and especially the atmosphere or mood it conveys (e.g., whether it is somber, vibrant, gloomy, or serene). "
            "Use specialized art vocabulary and make sure to mention key objects or symbols. "
            "At the end, add a comma-separated list of keywords including specific objects, symbols, or iconographical details that a user might use to search for this work."
        )

        max_retries = 3
        base_sleep_s = 2.0

        for attempt in range(1, max_retries + 1):
            try:
                resp = await client.aio.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[prompt, image_part],
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=500,
                    ),
                )
                return resp.text.strip()
            except Exception as e:
                if attempt == max_retries:
                    print(f"\nError final en {image_path}: {e}")
                    return None
                await asyncio.sleep(base_sleep_s * (2 ** (attempt - 1)))

    # Generar descripciones respetando el límite de RPM y guardando en un fichero CSV
    async def _run_rate_limited_and_save(image_paths, output_csv="../data/resultados_arte.csv", rpm_limit: int = 100):
        delay_between_requests = (60.0 / rpm_limit) + 0.2

        # Comprobamos si el archivo ya existe para saber si debemos escribir los encabezados
        file_exists = os.path.isfile(output_csv)

        # Abrimos en modo 'a' (append) para añadir filas sin borrar lo que ya existe
        with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Escribimos los encabezados solo si es un archivo nuevo
            if not file_exists:
                writer.writerow(["Ruta_Imagen", "Descripcion"]) 

            pbar = tqdm(total=len(image_paths), desc=f"Procesando ({rpm_limit} RPM)")

            for p in image_paths:
                try:
                    # Llamada a la API
                    d = await describe_image_gemini_async(p)

                    # Si la llamada fue exitosa, guardamos inmediatamente
                    if d is not None:
                        writer.writerow([p, d])
                        f.flush() 

                except Exception as e:
                    print(f"\nNo se pudo procesar la imagen {p}: {e}")
                finally:
                    pbar.update(1)
                    # Pausa para respetar el límite de peticiones por minuto
                    await asyncio.sleep(delay_between_requests)

        pbar.close()
        print(f"\n--- Proceso finalizado. Datos guardados en: {output_csv} ---")

    # Ejecutar el loop asíncrono desde contexto síncrono
    asyncio.run(
        _run_rate_limited_and_save(
            image_paths=selected_image_paths, output_csv="../data/resultados_arte.csv", rpm_limit=150
        )
    )

if __name__ == "__main__":
    # Cargar el dataset y mostrar su información
    df = load_dataset()
    print_dataset_info(df)
    # Obtener un subconjunto de imágenes
    df_subset, selected_image_paths = get_work_subset(df, num_samples=1000, seed=42)
    # Generar descripciones para las imágenes seleccionadas
    generate_descriptions_for_images(selected_image_paths[2500:4000])


