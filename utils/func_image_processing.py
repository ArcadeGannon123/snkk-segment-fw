import numpy as np
from PIL import Image, ImageTk

def resize_image(image, max_width, max_height):
    # Obtener las dimensiones originales de la imagen
    original_width, original_height = image.size

    scale = max_width/original_width if original_width > original_height else max_height/original_height

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    return image.resize((new_width, new_height))

def normalize_image(image,max_value):
    imagen_normalized = ((image.astype(np.float32)-np.min(image)) / (np.max(image)-np.min(image))) * max_value
    imagen_normalized = imagen_normalized.astype(np.uint8)
    return imagen_normalized

def recortar_region(imagenes, x_inicio, y_inicio, x_final, y_final):
    imagenes_recortadas = []
    for imagen in imagenes:
        imagen_recortada = imagen[y_inicio:y_final, x_inicio:x_final]
        imagenes_recortadas.append(imagen_recortada)
    return np.array(imagenes_recortadas)

def cargar_icono(path):
    icono_chart = Image.open(path)  # Asegúrate de tener un archivo icono.png
    icono_chart = icono_chart.resize((30, 30))
    icono_chart = ImageTk.PhotoImage(icono_chart)
    return icono_chart