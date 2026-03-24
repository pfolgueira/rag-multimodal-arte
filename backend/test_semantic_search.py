import requests
import time

evaluacion = [
    # 1. NG-2007-5-94.jpg (Grupo de soldados)
    {"query": "A vintage black and white historical photograph capturing a candid, relaxed moment outdoors, conveying a strong documentary and archival mood.", "expected_id": "NG-2007-5-94"},
    {"query": "Un grupo de soldados con uniformes militares, botas altas y gorras, sentados juntos descansando en la ladera de una colina de hierba, con el texto manuscrito 'Den Brielle' en la parte inferior.", "expected_id": "NG-2007-5-94"},

    # 2. SK-A-3236.jpg (Retrato femenino con perlas)
    {"query": "A classical portrait of a woman with a serene and elegant atmosphere, featuring a soft color palette with delicate pink and white tones against a dark background.", "expected_id": "SK-A-3236"},
    {"query": "Un retrato de medio cuerpo de una joven con cabello oscuro y rizado adornado con perlas, vistiendo un escote amplio con lazos rosados.", "expected_id": "SK-A-3236"},

    # 3. SK-A-2566.jpg (Bodegón con langosta)
    {"query": "Un bodegón oscuro y tenebrista con un fuerte contraste de iluminación que resalta los tonos rojos y amarillos vibrantes sobre un fondo sumido en la sombra.", "expected_id": "SK-A-2566"},
    {"query": "A highly detailed still life featuring a large red lobster in the center, a sliced lemon, a piece of bread, oysters, and a glass goblet on a table.", "expected_id": "SK-A-2566"},

    # 4. SK-A-2343.jpg (Paisaje pastoral)
    {"query": "A peaceful pastoral landscape bathed in soft daylight, conveying a tranquil and idyllic rural mood with earthy colors and a clear blue sky.", "expected_id": "SK-A-2343"},
    {"query": "Una escena campestre con una mujer amamantando a un bebé junto a un pastor, rodeados de animales como un caballo blanco, vacas descansando y ovejas cerca de unas ruinas.", "expected_id": "SK-A-2343"},

    # 5. SK-A-2316.jpg (Marina con barcos)
    {"query": "Una marina dinámica bajo un cielo intensamente nublado y amenazante, capturando la bruma del mar agitado y una paleta de grises, azules apagados y ocres.", "expected_id": "SK-A-2316"},
    {"query": "A seascape showing a sailboat with reddish-brown sails navigating choppy waters, a smaller boat moored to the left, and a figure wading in the sea in the foreground.", "expected_id": "SK-A-2316"},

    # 6. NG-2007-5-154.jpg (Escena de piscina)
    {"query": "Una fotografía histórica en blanco y negro que transmite una atmósfera de ocio y relajación al aire libre, mostrando una escena clásica y refrescante en el agua.", "expected_id": "NG-2007-5-154"},
    {"query": "A vintage photograph featuring a group of people wearing retro swimsuits, gathered in and around a swimming pool enjoying a sunny day.", "expected_id": "NG-2007-5-154"},

    # 7. NG-2007-5-175.jpg (Piscina concurrida)
    {"query": "An archival black and white image capturing a lively, bustling, and crowded aquatic environment, reflecting a highly active day at a public pool", "expected_id": "NG-2007-5-175"},
    {"query": "Una vista amplia de unas instalaciones acuáticas muy concurridas, con un gran número de personas en bañador interactuando tanto dentro del agua como en los bordes de la piscina.", "expected_id": "NG-2007-5-175"},

    # 8. RP-T-00-633.jpg (La Natividad)
    {"query": "A humble and sacred scene of the Nativity in a stable, with a soft, spiritual atmosphere conveyed through delicate ink and wash on aged paper.", "expected_id": "RP-T-00-633"},
    {"query": "El nacimiento de Jesús en el pesebre, con la Virgen María y San José adorando al niño, rodeados por un buey y un asno en un entorno arquitectónico rústico.", "expected_id": "RP-T-00-633"},

    # 9. RP-T-00-546.jpg (Jinete heroico en caballo encabritado)
    {"query": "Un grabado o dibujo clásico que transmite una atmósfera heroica y de gran dinamismo, resaltando la tensión y el poder a través de un vigoroso sombreado de líneas cruzadas.", "expected_id": "RP-T-00-546"},
    {"query": "A muscular warrior wearing a plumed helmet and a cape, riding a rearing horse, holding a baton in his raised hand, with city buildings and smaller figures in the background.", "expected_id": "RP-T-00-546"},

    # 10. RP-T-00-10.jpg (Dos figuras caminando)
    {"query": "A monochromatic ink drawing with a somewhat melancholic and quiet atmosphere, utilizing visible cross-hatching techniques to define the shadows and forms of the walking children.", "expected_id": "RP-T-00-10"},
    {"query": "Dos niños caminando en la misma dirección; el niño de la izquierda va descalzo, lleva un sombrero, una caja rectangular bajo el brazo y una cesta, mientras que la segunda figura camina detrás con los brazos cruzados.", "expected_id": "RP-T-00-10"},

    # 11. RP-F-2001-7-564B-24.jpg (Libro abierto con el Palazzo Vecchio)
    {"query": "Una imagen con un tono documental e histórico que muestra un libro antiguo abierto; la página exhibe una fotografía arquitectónica clásica o impresión en blanco y negro de un imponente edificio gubernamental renacentista.", "expected_id": "RP-F-2001-7-564B-24"},
    {"query": "A two-page spread of an open book; the left side has a protective tissue paper with the text 'Palazzo Vecchio.' printed in red, while the right side features a large, rusticated stone building with battlements, statues at the entrance, and a prominent tall clock tower.", "expected_id": "RP-F-2001-7-564B-24"},

    # 12. RP-F-2001-7-749B-32.jpg (Libro abierto con ilustraciones de peces)
    {"query": "Una doble página de un libro antiguo o enciclopedia natural con una atmósfera académica, formal y científica, mostrando ilustraciones zoológicas monocromáticas muy precisas.", "expected_id": "RP-F-2001-7-749B-32"},
    {"query": "A spread of an open book featuring four highly detailed illustrations of fish with visible scales and fins, arranged with two fish on the left page and two on the right, accompanied by paragraphs of printed text.", "expected_id": "RP-F-2001-7-749B-32"},

    # 13. RP-F-2001-7-749B-19.jpg (Libro abierto con ilustraciones de ganado)
    {"query": "An antique agricultural or zoological reference book spread, presenting a formal and educational atmosphere with precise, monochromatic engravings of livestock.", "expected_id": "RP-F-2001-7-749B-19"},
    {"query": "Una doble página de un libro impreso que muestra tres ilustraciones detalladas de toros o vacas de aspecto robusto; dos vacas más pequeñas en la página izquierda y un toro más grande en la página derecha, rodeados de densos bloques de texto.", "expected_id": "RP-F-2001-7-749B-19"}
]

API_URL = "http://localhost:8000/search"
K = 10
aciertos = 0
tiempos_respuesta = []

print(f"Iniciando evaluación para {len(evaluacion)} consultas (K={K})...\n")

for i, test in enumerate(evaluacion, 1):
    query = test["query"]
    expected_id = test["expected_id"]
    
    # Medir latencia (inicio)
    start_time = time.time()
    
    try:
        response = requests.get(API_URL, params={"query": query, "k": K})
        response.raise_for_status() # Asegurar que fue un 200 OK
        resultados = response.json()
        
        # Latencia
        end_time = time.time()
        latencia = end_time - start_time
        tiempos_respuesta.append(latencia)
        
        # Extraer ids de los resultados
        ids_recuperados = [res["image_id"].replace(".jpg", "") for res in resultados]
        expected_id_clean = expected_id.replace(".jpg", "")
        
        hit = expected_id_clean in ids_recuperados
        if hit:
            aciertos += 1
            
        print(f"[{i}/{len(evaluacion)}] Query: {query[:30]}... | Latencia: {latencia:.2f}s | Acierto: {hit}")

    except Exception as e:
        print(f"[{i}/{len(evaluacion)}] Error en la consulta: {e}")

    time.sleep(0.5)

recall_at_k = aciertos / len(evaluacion)
latencia_media = sum(tiempos_respuesta) / len(tiempos_respuesta) if tiempos_respuesta else 0

print("\n" + "="*40)
print("RESULTADOS DE LA EVALUACIÓN")
print("="*40)
print(f"Total de consultas: {len(evaluacion)}")
print(f"Aciertos (Hit in top {K}): {aciertos}")
print(f"Recall@{K}: {recall_at_k:.2%} ({recall_at_k})")
print(f"Latencia Media: {latencia_media:.3f} segundos")