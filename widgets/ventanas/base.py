import tkinter as tk
from widgets.common.area_trabajo import AreaTrabajo
from utils.func_image_processing import cargar_icono
from tkinter import ttk
from scipy.io import savemat
from tkinter import filedialog
from tkinter import messagebox 

class Base(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Configuración
        self.config(width=1600, height=900)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # Iconos
        self.play_imagen = cargar_icono("./icons/play.png")
        self.pause_imagen = cargar_icono("./icons/pausa.png")
        self.stop_imagen = cargar_icono("./icons/stop.png")
        self.next_imagen = cargar_icono("./icons/proximo.png")
        self.back_imagen = cargar_icono("./icons/atras.png")

        # Propiedades
        self.area_trabajo = None


        # Widgets
        self.base_visor = tk.Frame(self)
        self.base_visor.grid(row=0, column=1, sticky="nsew")

        self.visor = tk.Frame(self.base_visor,bg="#2D2D30")
        self.visor.pack_propagate(False) 
        self.visor.pack(fill=tk.BOTH,expand=True)

        self.mri_sequence = AreaTrabajo(self.visor, bg="#D4D4D4", width=1024, height=512, relief='raised', borderwidth=2)
        self.mri_sequence.pack_propagate(False) 
        self.mri_sequence.place(relx=0.5, rely=0.5, anchor=tk.CENTER)



        self.base_reproductor = tk.Frame(self.base_visor, height=256)
        self.base_reproductor.pack(side=tk.BOTTOM, fill=tk.X)

        self.base_timeline = tk.Frame(self.base_reproductor)
        self.base_timeline.pack(fill=tk.X)           

        # Barra de timeline
        self.timeline = tk.Scale(self.base_timeline, from_=1, to=1, orient="horizontal", command=self.mover_timeline)
        self.timeline.pack(side=tk.TOP, fill=tk.X, expand=True)


        # Crear un frame para las etiquetas
        self.frame_etiquetas = tk.Frame(self.base_reproductor)
        self.frame_etiquetas.pack(fill=tk.X, pady=0)      

        

        # Etiqueta para el valor mínimo
        self.label_min = tk.Label(self.frame_etiquetas, text="0.0 [ms]", font=("Courier", 10))
        self.label_min.pack(side=tk.LEFT, padx=5)

        # Etiqueta para el valor actual 
        self.time = tk.Label(self.frame_etiquetas, text="--", font=("Courier", 10))
        self.time.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Etiqueta para el valor máximo
        self.label_max = tk.Label(self.frame_etiquetas, text="1.0 [ms]", font=("Courier", 10))
        self.label_max.pack(side=tk.RIGHT, padx=5)

        self.base_controles = tk.Frame(self.base_reproductor)
        self.base_controles.pack(fill=tk.X)        

        # Botones de control
        self.frame_controles = tk.Frame(self.base_controles)
        self.frame_controles.pack(expand=True, padx=10, pady=10)

        self.base_playpause = tk.Frame(self.frame_controles)
        self.base_playpause.pack(side=tk.LEFT)

        self.btn_iniciar = ttk.Button(self.base_playpause, image=self.play_imagen,command=self.iniciar)
        self.btn_iniciar.pack(side=tk.LEFT)

        self.btn_pausar = ttk.Button(self.base_playpause, image=self.pause_imagen,command=self.pausar)
        self.btn_pausar.pack(side=tk.LEFT)
        self.btn_pausar.pack_forget()

        self.btn_atras = ttk.Button(self.frame_controles, image=self.back_imagen,command=self.mover_fotograma_izq)
        self.btn_atras.pack(side=tk.LEFT)

        self.btn_detener = ttk.Button(self.frame_controles, image=self.stop_imagen,command=self.detener)
        self.btn_detener.pack(side=tk.LEFT)

        self.btn_adelante = ttk.Button(self.frame_controles, image=self.next_imagen,command=self.mover_fotograma_der)
        self.btn_adelante.pack(side=tk.LEFT)

        # Label de estado del modelo 3D Unet
        self.modelo_no_cargado_label = tk.Label(self.visor, text="Se necesita cargar el modelo 3D Unet", fg="#ffe5ec",bg="#2D2D30")
        self.modelo_no_cargado_label.pack(anchor='n', padx=10, pady=10, side='top', fill='x')
        
        self.modelo_cargado_label = tk.Label(self.visor, text="Modelo 3D Unet Operativo", fg="lightblue",bg="#2D2D30")
        self.modelo_cargado_label.pack(anchor='n', padx=10, pady=10, side='top', fill='x')
        self.modelo_cargado_label.pack_forget()

    def iniciar(self):
        """Inicia la reproducción y actualiza el estado de los botones"""

        self.area_trabajo.iniciar()
        self.btn_iniciar.pack_forget()
        self.btn_pausar.pack(side=tk.LEFT)

    def pausar(self):
        """Pausa la reproducción y actualiza el estado de los botones"""

        self.area_trabajo.pausar()
        self.btn_pausar.pack_forget()
        self.btn_iniciar.pack(side=tk.LEFT)

    def detener(self):
        """Detiene la reproducción y actualiza el estado de los botones"""

        self.area_trabajo.detener()
        self.btn_iniciar.pack(side=tk.LEFT)
        self.btn_pausar.pack_forget()

    def mover_timeline(self,val):
        """Mueve manualmente el timeline y actualiza el tiempo actual"""

        self.time.config(text=str(self.area_trabajo.timeline_dicom[int(val)-1])+"[ms]")
        self.area_trabajo.mover_timeline(val)

    def mover_fotograma_izq(self):
        """Mueve un fotograma a la izquierda"""
        self.area_trabajo.mover_fotograma(-1)

    def mover_fotograma_der(self):
        """Mueve un fotograma a la derecha"""
        self.area_trabajo.mover_fotograma(1)

    def export_to_mat(self, id):
        """Exporta los datos de una segmentacion a un archivo .mat"""
        datos = self.area_trabajo.segmentaciones[id]

        # Pide al usuario expecificar el destino de la exportación
        default_name = f"{self.area_trabajo.patient_id}({datos['name']})"
        output_file = filedialog.asksaveasfilename(defaultextension=".mat", filetypes=[("MAT files", "*.mat")], initialfile=default_name)

        # Crea un objeto que almacenará los datos de la segmentación
        data = {
            "nombre":datos["name"],
            "segmentacion_mascara":datos["segmentacion_original"],
            "img":self.area_trabajo.imagenes_png_original_size,
            "datos":{
                "area":datos["datos"]["Área"][0],
                "flujo":datos["datos"]["Flujo"][0],
                "velocidad":datos["datos"]["Velocidad Media"][0],
                "timeline":datos["datos"]["Timeline"]
            }
        }
        # Guardar los datos de las segmentaciones en .mat
        savemat(output_file, {'segmentacion': [data]})
    
    def export_to_mat_all(self):
        """Exporta los datos de todas las segmentaciones a un archivo .mat"""

        # Pide al usuario expecificar el destino de la exportación
        default_name = self.area_trabajo.patient_id
        output_file = filedialog.asksaveasfilename(defaultextension=".mat", filetypes=[("MAT files", "*.mat")], initialfile=default_name)
   
        # Crea un objeto que almacenará todos los datos de las segmentaciones
        segmentaciones = []
        for _,datos in self.area_trabajo.segmentaciones.items():
            data = {
                "nombre":datos["name"],
                "segmentacion_mascara":datos["segmentacion_original"],
                "img":self.area_trabajo.imagenes_png_original_size,
                "datos":{
                    "area":datos["datos"]["Área"][0],
                    "flujo":datos["datos"]["Flujo"][0],
                    "velocidad":datos["datos"]["Velocidad Media"][0],
                    "timeline":datos["datos"]["Timeline"]
                }
            }
            segmentaciones.append(data)

        # Guardar los datos de las segmentaciones en .mat
        savemat(output_file, {'segmentacion': segmentaciones})

    def ingresar_secuencia_mri(self,ruta_imagenes):
        """Muestra las imagenes extraidas de los archivos DICOM en el canvas"""
        
        if self.area_trabajo is not None:
            # Si existe, destruirlo para eliminarlo de la interfaz
            self.area_trabajo.destroy()        
        
        self.area_trabajo = AreaTrabajo(self.mri_sequence)
        self.area_trabajo.pack(fill=tk.BOTH, expand=True) 
        try:
            self.area_trabajo.set_images(ruta_imagenes)            
        except  Exception:
            messagebox.showerror("Error", "El formato de las imagenes no es válido.")
            return
        self.area_trabajo.set_timeline(self.timeline)
        self.label_min.config(text=str(self.area_trabajo.timeline_dicom[0])+" [ms]")
        self.label_max.config(text=str(self.area_trabajo.timeline_dicom[-1])+" [ms]")
        self.time.config(text=str(self.area_trabajo.timeline_dicom[int(self.timeline.get())])+"[ms]")

