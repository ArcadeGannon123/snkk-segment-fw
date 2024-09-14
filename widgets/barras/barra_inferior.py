import tkinter as tk
from utils.func_image_processing import cargar_icono
from tkinter import colorchooser, Toplevel
import numpy as np
import cv2
from widgets.common.hover_button import HoverButton
from tkinter import messagebox 

class BarraInferior(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        #configuracion
        self.config(bg="#1E1E1E", relief='raised', borderwidth=2)

        # Propiedades
        self.base = None
        self.barra_superior = None
        self.barra_lateral = None
        
        # Iconos
        self.icono_segment = cargar_icono("./icons/elipse.png")
        self.icono_export = cargar_icono("./icons/exportar.png")
        self.export_imagen = cargar_icono("./icons/exportar.png")
        self.icono_app = cargar_icono("./icons/conexiones.png")

        # Widgets        
        self.boton_segmentar = HoverButton(self, image=self.icono_segment, text="Segmentar ROI", 
                                           compound="left", command=self.segmentar_roi, 
                                           bg="#569CD6", bd=0, fg="white")
        self.boton_segmentar.pack(side="left", padx=10, pady=10, ipadx=5,ipady=5)

        self.boton_exportar = HoverButton(self, image=self.export_imagen, text="Exportar a .mat", 
                                           compound="left", command=lambda: self.exportar_segmentacion(), 
                                           bg="#2D2D30", bd=0, fg="white")
        self.boton_exportar.pack(side="left", padx=10, pady=10, ipadx=5,ipady=5)
        
    """ Abre una ventana para obtener un nombre y un color para segmentación una ROI """
    def segmentar_roi(self):

        try:
            if self.base.area_trabajo.RESHAPE_ROI is None: 
                raise Exception
        except Exception:  
            messagebox.showerror("Error", "No existe un área seleccionada.")
            return
        # Crear una nueva ventana
        nueva_ventana = Toplevel(self)
        nueva_ventana.title("Segmentar Región de Interés")
        nueva_ventana.config(bg="#1E1E1E")
        nueva_ventana.attributes("-topmost", True)        
        nueva_ventana.iconphoto(False, self.icono_app)

        # Frame para alinear texto y entrada
        frame_texto = tk.Frame(nueva_ventana,bg="#1E1E1E")
        frame_texto.pack(pady=20, padx=20, anchor="w")

        # Etiqueta para el texto
        tk.Label(frame_texto, text="Ingresa un nombre:", font=("Arial", 12),bg="#1E1E1E",fg="#fff").grid(row=0, column=0, padx=5)
        
        # Entrada de texto
        entrada_texto = tk.Entry(frame_texto, font=("Helvetica", 12), width=20)
        entrada_texto.grid(row=0, column=1, padx=5)
        entrada_texto.insert(0, "Segmentacion #"+str(self.base.area_trabajo.n_segmentaciones+1))
        
        # Frame para alinear el selector de color
        frame_color = tk.Frame(nueva_ventana,bg="#1E1E1E")
        frame_color.pack(pady=10, padx=20, anchor="w")

        # Etiqueta para seleccionar color
        tk.Label(frame_color, text="Seleccionar Color:", font=("Arial", 12),bg="#1E1E1E",fg="#fff").grid(row=0, column=0, padx=5)
        
        # Color por defecto (blanco)
        color_hexa = "#ffffff"
        color_rgb = (255,255,255)

        # Función para elegir color y actualizar el cuadro
        def elegir_color():
            nonlocal color_hexa
            nonlocal color_rgb
            color = colorchooser.askcolor(title="Selecciona un color", parent=nueva_ventana)
            if color:
                color_hexa = color[1]
                color_rgb = color[0]
                cuadro_color.config(bg=color_hexa)

        # Función para comenzar la segmentación
        def segmentar_roi():
            nombre_segmentacion = entrada_texto.get()
            nueva_ventana.destroy() 
            self.segmentar_imagen(nombre_segmentacion ,color_rgb,color_hexa)
        
        # Cuadro de color clicable
        cuadro_color = tk.Label(frame_color, width=3, height=1, bg=color_hexa, bd=2, relief="raised", cursor="hand2")
        cuadro_color.grid(row=0, column=1, padx=5)
        cuadro_color.bind("<Button-1>", lambda e: elegir_color())

        # Botón para confirmar el texto y color        
        btn_confirmar = HoverButton(nueva_ventana, text="Aplicar", command=segmentar_roi, 
                                font=("Arial", 12), bg="#569CD6", fg="white", padx=10, pady=5, cursor="hand2")
        btn_confirmar.pack(pady=20)
    
    """ Función para segmentar la ROI """
    def segmentar_imagen(self,texto,color,color_hexa):

        if self.barra_superior.modelo is None:
            messagebox.showerror("Error", "El modelo 3D Unet no ha sido cargado.")
            return
        
        if self.base.area_trabajo.RESHAPE_ROI is not None:   
            train_dim = self.barra_superior.modelo.dim_train

            # Obtiene la ROI de la secuencia de imagenes
            region_magnitud = self.redimensionar(self.base.area_trabajo.get_roi('magnitud'),(train_dim,train_dim))
            region_fase = self.redimensionar(self.base.area_trabajo.get_roi('fase'),(train_dim,train_dim))

            # Obtiene las coordenadas de la ROI para la imagen en el canvas (ORIGINAL)
            # y para la imagen con resolución original (RESHAPE)
            x1,y1,x2,y2 = self.base.area_trabajo.RESHAPE_ROI
            canvas_roi = self.base.area_trabajo.ORIGINAL_ROI
            
            ancho = x2 - x1
            alto = y2 - y1

            # Entrega la ROI al modelo 3d unet
            self.barra_superior.modelo.coordenadas = {'x1':x1,'y1':y1,'ancho':ancho,'alto':alto}
            self.barra_superior.modelo.imagenes['magnitud'] = self.base.area_trabajo.imagenes_png_original_size['magnitud']
            self.barra_superior.modelo.imagenes['fase'] = self.base.area_trabajo.imagenes_png_original_size['fase']
            self.barra_superior.modelo.input_data(np.array([region_magnitud,region_fase]))

            # Predice la segmentacion para la ROI
            prediccion = self.barra_superior.modelo.predict()
            
            # Guarda los datos de la segmentacion y los muestra en el canvas
            self.base.area_trabajo.set_segmentation(prediccion,color,color_hexa,texto,canvas_roi)
            
            # Crea un bloque de la segmentacion en la barra lateral
            self.barra_lateral.clean_sidebar()
            for id,segmentacion in self.base.area_trabajo.segmentaciones.items():
                self.barra_lateral.crear_bloque(id, segmentacion["name"], segmentacion["datos"], segmentacion["thumbnail"], 90, 90,segmentacion["color_hexa"],segmentacion["active"],segmentacion["roi"])

    """ Funcion para redimensiona una imagen """
    def redimensionar(self,images,new_shape):
        # Inicializar un nuevo array para las imágenes redimensionadas
        new_seq = []
        for frame in images:    
            new_seq.append( cv2.resize(frame, new_shape) )
        return np.array(new_seq)

    """ Guarda una referencia del widget base """
    def set_base(self,base):
        self.base = base

    """ Guarda una referencia del widget barra_superior """
    def set_barra_superior(self,barra_superior):
        self.barra_superior = barra_superior

    """ Guarda una referencia del widget barra lateral """
    def set_barra_lateral(self,barra_lateral):
        self.barra_lateral = barra_lateral
    
    """ Llama a la funcion para exportar todas las segmentaciones a un archivo .mat """
    def exportar_segmentacion(self):
        self.base.export_to_mat_all()