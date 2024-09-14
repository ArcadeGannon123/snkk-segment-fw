import tkinter as tk
from PIL import Image, ImageTk
from utils.get_dicom_images import leer_dicom_magnitud_fase
import numpy as np
import cv2
from utils.func_image_processing import *
from widgets.common.seleccion_roi import SeleccionRoi

class AreaTrabajo(SeleccionRoi):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Propiedades
        self.canvas_res = 512
        self.reproduciendo = False
        self.indice_imagen = 0
        self.largo_secuencia = 0
        self.imagen_canvas = None
        self.imagenes_png_original_size = {}
        self.imagenes_png_resize = {}
        self.timeline_dicom = None
        self.segmentaciones = {}
        self.n_segmentaciones = 0
        self.segmentacion_mag_fase = []
        self.imagenes_dicom = {}
        self.imagenes_png_original = {}
        self.imagenes_png = {}
        self.imagenes_mag_fase = []
        self.animation_delay = 10
        self.pixel_spacing = None
        self.patient_id = ""
        self.timeline = None

    def set_images(self, image_paths):
        """Extrae los valores de los archivos DICOM """

        # Lee los archivos DICOM y extrae los datos
        DICOM_DATA = leer_dicom_magnitud_fase(image_paths)    
        self.imagenes_dicom = DICOM_DATA['imagetypes']
        self.timeline_dicom = DICOM_DATA['timeline']
        self.pixel_spacing = DICOM_DATA['pixel_spacing']
        self.patient_id = DICOM_DATA['patient_id']
        
        # Obtiene las imagenes de magnitud y fase y las normaliza
        imagenes_magnitud = np.array([normalize_image(image,255.) for image in self.imagenes_dicom['magnitud']])
        imagenes_fase = np.array([normalize_image(image,255.) for image in self.imagenes_dicom['fase']])
        imagenes_magfase = np.concatenate((imagenes_magnitud, imagenes_fase), axis=-1) # Concatena en el eje x las imagenes de magnitud y fase

        # Guarda datos relevantes en las propiedades
        self.largo_secuencia = len(imagenes_magfase)
        self.mri_imagen_shape = imagenes_magnitud.shape

        # Guarda en propiedades las imagenes de magnitud y fase
        self.imagenes_png_original_size['magnitud'] = imagenes_magnitud
        self.imagenes_png_original_size['fase'] = imagenes_fase

        # Procesa las imagenes para mostrar en el canvas
        self.imagenes_png_resize['magnitud'] = [ImageTk.PhotoImage(resize_image(Image.fromarray(imagen), self.canvas_res, self.canvas_res)) for imagen in imagenes_magnitud]
        self.imagenes_png_resize['fase'] = [ImageTk.PhotoImage(resize_image(Image.fromarray(imagen), self.canvas_res, self.canvas_res)) for imagen in imagenes_fase]
        self.imagenes_mag_fase = [ImageTk.PhotoImage(resize_image(Image.fromarray(imagen), self.canvas_res*2, self.canvas_res)) for imagen in imagenes_magfase]

        if self.imagenes_mag_fase:
            self.imagen_canvas = self.create_image(0, 0, anchor=tk.NW, image=self.imagenes_mag_fase[0])
            self.config(width=self.imagenes_mag_fase[0].width(), height=self.imagenes_mag_fase[0].height())
        
        # Actualiza el canvas
        self.cambiar_fotograma()

    
    def actualizar_imagen(self):        
        """Actualiza la imagen mostrada en el canvas y el timeline"""

        if self.reproduciendo:
            # Mostrar la imagen actual
            self.cambiar_fotograma()
    
            # Actualizar la posición del slider en el timeline
            self.timeline.set(self.indice_imagen + 1)
    
            # Avanzar al siguiente índice, reiniciar si es el final
            self.indice_imagen = (self.indice_imagen + 1) % self.largo_secuencia
    
            # Volver a llamar esta función después de un retraso
            self.after(self.animation_delay, self.actualizar_imagen)                    
        
    def cambiar_fotograma(self):        
        """Actualiza la imagen mostrada en el canvas y el timeline"""

        # Mostrar la imagen actual
        imagen_principal = self.imagenes_mag_fase[self.indice_imagen]

        self.itemconfig(self.imagen_canvas, image=imagen_principal)

        # Muestra las segmentaciones en el canvas
        for _,segmentacion in self.segmentaciones.items():
            if segmentacion["active"]:
                self.itemconfig(segmentacion["canvas"], image=segmentacion["segmentacion"][self.indice_imagen])

    
    def mover_fotograma(self,val):
        """Mueve manualmente el timeline y actualiza la imagen"""

        self.indice_imagen = (self.indice_imagen + val) % self.largo_secuencia
        self.timeline.set(self.indice_imagen + 1)
        self.cambiar_fotograma()

    def iniciar(self):
        """Inicia la reproducción de la secuencia de imágenes"""

        if not self.reproduciendo:
            self.reproduciendo = True
            self.actualizar_imagen()
    
    def pausar(self):
        """Pausa la reproducción de la secuencia de imágenes"""

        self.reproduciendo = False
    
    def detener(self):
        """Detiene la reproducción y reinicia el índice de la imagen"""

        self.reproduciendo = False
        self.indice_imagen = 0
        
        # Reinicia la imagen al inicio        
        self.cambiar_fotograma()
        
        self.timeline.set(self.indice_imagen + 1)
    
    def mover_timeline(self,val):
        """Mueve manualmente el timeline y actualiza la imagen"""

        self.indice_imagen = int(val) - 1  
              
        self.cambiar_fotograma()

    def set_timeline(self, timeline):
        """Guarda una referencia del timeline"""

        self.timeline = timeline
        self.timeline.config(to=self.largo_secuencia)

    def get_roi(self,image_type):
        """Recorta la ROI de las imagenes"""

        x1,y1,x2,y2 = self.RESHAPE_ROI
        roi_image = recortar_region(self.imagenes_png_original_size[image_type],x1,y1,x2,y2)
        
        return roi_image

    def set_segmentation(self, segmentacion,color,color_hexa,text,roi):
        """Guarda los datos de una segmentación"""

        if segmentacion is not None:       
            # Añade color a la segmentacion
            segmentacion_color = [self.add_color_alpha(imagen,color) for imagen in segmentacion]
            segmentacion_mag_fase = np.concatenate((segmentacion_color, segmentacion_color), axis=2) # concatena la segmentacion en el eje x
            
            # Extrae los datos de la segmentación para los gráficos
            datos = self.set_charts_value(self.pixel_spacing,segmentacion,self.imagenes_dicom['fase'],self.timeline_dicom)
            
            # Crea un objeto con los datos de la segmentación
            segment_object = {
                "active": True,
                "segmentacion_original": segmentacion,
                "segmentacion": [self.to_photoimage(imagen,(self.canvas_res*2,self.canvas_res)) for imagen in segmentacion_mag_fase],
                "canvas": self.create_image(0, 0, anchor=tk.NW, image=self.to_photoimage(segmentacion_mag_fase[0])),
                "thumbnail": self.add_color(segmentacion[0],color),
                "name":text,
                "color_hexa":color_hexa,
                "datos":datos,
                "roi":roi
            }

            self.segmentaciones[self.n_segmentaciones]=segment_object            
            self.n_segmentaciones = self.n_segmentaciones + 1

            # Actualiza el canvas
            self.cambiar_fotograma()
         

    def add_color_alpha(self,imagen,color):
        """Añade color a una imagen en escala de grises con transparencia"""

        color_image = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
        color_image_with_alpha = np.dstack([color_image, np.zeros((color_image.shape[0], color_image.shape[1]), dtype=np.uint8)])
    
        # Asignar el color a los píxeles con valor 255
        color_image_with_alpha[imagen == 255, :3] = [color[0],color[1],color[2]]
        color_image_with_alpha[imagen == 255, 3] = 255  # Canal alfa completamente opaco para los píxeles con valor 255
    
        # Píxeles diferentes de 255 deben ser transparentes
        color_image_with_alpha[imagen != 255, 3] = 0  # Canal alfa completamente transparente para los píxeles diferentes de 255
        return color_image_with_alpha

    def add_color(self,imagen,color):
        """Añade color a una imagen en escala de grises"""

        color_image = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
        color_image[imagen == 255] = [color[0],color[1],color[2]]
  
        return color_image
       
    
    def to_photoimage(self,imagen,reshape=None):
        """Crea una imange PhotoImage desde un array numpy"""
        
        imagen_pil=Image.fromarray(imagen,"RGBA")
        if reshape:
            imagen_pil=imagen_pil.resize((reshape[0], reshape[1]))
        
        return ImageTk.PhotoImage(imagen_pil)

    def del_segmentacion(self,id):       
        """Elimina la segmentqacion según la id"""

        self.itemconfig(self.segmentaciones[id]["canvas"], image=None)
        del self.segmentaciones[id]
        self.cambiar_fotograma()

    def set_visualizacion(self,id,activacion):  
        """Activa o desactiva una segmentacion en el canvas"""

        self.segmentaciones[id]["active"]=activacion
        canvas = self.segmentaciones[id]["canvas"]
        if not activacion:
            self.itemconfig(canvas, state=tk.HIDDEN)
        else:
            self.itemconfig(canvas, state=tk.NORMAL)
        self.cambiar_fotograma()


    def set_charts_value(self,pixel_spacing,segmentacion,dicom,timeline):
        """Extrae los datos para los graficos según el área segmentada"""
    
        area = np.array([self.get_area_from_imagen(imagen) for imagen in segmentacion])* (pixel_spacing[0]/10.)**2
        velocidad = np.array([self.get_velocity_from_imagen(index,imagen,segmentacion) for index,imagen in enumerate(dicom)])
        
        DATA_CHART = {
            "Área":(area,["Tiempo [ms]","Área [cm²]"]) ,
            "Velocidad Media":(velocidad,["Tiempo [ms]","Velocidad Media [cm/s]"]),
            "Flujo": (area * velocidad,["Tiempo [ms]","Flujo [ml/s]"]),
            "Timeline": timeline
        }

        return DATA_CHART
    
    def get_area_from_imagen(self,imagen):  
        """Calcula la cantidad de pixeles segmentados"""

        umbral = 50
        return np.count_nonzero(imagen > umbral)
    
    def get_velocity_from_imagen(self,index,imagen,segmentacion):
        """Calcula la velocidad promedio del área segmentada"""
    
        mascara = segmentacion[index,:,:] > 50

        # Extraer los valores de velocidad en el área segmentada
        velocidades_segmentadas = imagen[mascara]
        
        # Calcular el promedio de las velocidades en el área segmentada
        promedio_velocidad = np.mean(velocidades_segmentadas)
            
        return promedio_velocidad