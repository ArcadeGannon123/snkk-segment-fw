import tkinter as tk
from utils.func_image_processing import cargar_icono
from tkinter import filedialog
from widgets.common.hover_button import HoverButton
from tkinter import ttk
from utils.segment_model import KerasModelLoader
from tkinter import messagebox 

class BarraSuperior(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configuración
        self.config(bg="#1E1E1E", relief='raised', borderwidth=2)
        
        # Iconos
        self.icono_carpeta = cargar_icono("./icons/carpeta.png")
        self.icono_guardar = cargar_icono("./icons/sav.png")
        self.icono_cargar = cargar_icono("./icons/neural.png")

        # Propiedades
        self.base = None
        self.barra_lateral = None
        self.modelo = None
        
        # Widgets
        boton_seleccionar = HoverButton(self, image=self.icono_carpeta, text="Importar DICOM", 
                                           compound="left", command=self.seleccionar_imagen, 
                                           bg="#2D2D30", bd=0, fg="white")
        boton_seleccionar.pack(side="left", padx=10, pady=10)

        boton_cargar = HoverButton(self, image=self.icono_cargar, text="Cargar Modelo", 
                                           compound="left", command=self.cargar_modelo_window, 
                                           bg="#2D2D30", bd=0, fg="white")
        boton_cargar.pack(side="left", padx=10, pady=10)

    def seleccionar_imagen(self):
        """Función para abrir el cuadro de diálogo y seleccionar los archivos DICOM"""

        ruta_imagenes = filedialog.askopenfilenames()
        if ruta_imagenes:
            self.base.ingresar_secuencia_mri(ruta_imagenes)
            self.barra_lateral.clean_sidebar()
    
    
    def set_base(self,base):
        """Guarda una referencia al widget base"""
        self.base = base

    def set_barra_lateral(self,barra_lateral):
        """Guarda una referencia al widget barra lateral"""
        self.barra_lateral = barra_lateral
        

    def cargar_modelo_window(self):
        """Abre una ventana para cargar el modelo 3D Unet"""
        # Crear una nueva ventana
        new_window = tk.Toplevel(self)
        new_window.title("Cargar Modelo 3D Unet")        
        new_window.attributes("-topmost", True)    
        new_window.config(bg="#1E1E1E")

        # Sección de selección o ingreso manual de archivo
        def select_file():
            file_path = filedialog.askopenfilename(title="Seleccionar archivo", parent=new_window)
            if file_path:
                file_entry.delete(0, tk.END)
                file_entry.insert(0, file_path)       
        
        file_button = ttk.Button(new_window, text="Seleccionar archivo", command=select_file)
        file_button.grid(row=0, column=0, padx=10, pady=10)

        file_entry = tk.Entry(new_window, width=40)
        file_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # label_dimx = tk.Label(new_window, text=f"dimX")
        # label_dimx.grid(row=2, column=0, padx=10, pady=10)
        # entry_dimx = tk.Entry(new_window, state='readonly')
        # entry_dimx.grid(row=2, column=1, padx=10, pady=10)
        # entry_dimx.insert(0, "32")

        # label_dimy = tk.Label(new_window, text=f"dimY")
        # label_dimy.grid(row=3, column=0, padx=10, pady=10)
        # entry_dimy = tk.Entry(new_window, state='readonly')
        # entry_dimy.grid(row=3, column=1, padx=10, pady=10)
        # entry_dimy.insert(0, "32")

        # label_dimz = tk.Label(new_window, text=f"dimZ")
        # label_dimz.grid(row=4, column=0, padx=10, pady=10)
        # entry_dimz = tk.Entry(new_window, state='readonly')
        # entry_dimz.grid(row=4, column=1, padx=10, pady=10)
        # entry_dimz.insert(0, "128")

        # Botón de aplicar funcionalidad
        def apply_function():
            # Obtener la ruta del archivo desde el campo de entrada
            file_path = file_entry.get()                       
            try:                  
                print(f"Cargando modelo: {file_path}")
                self.modelo = KerasModelLoader(file_path)
                self.base.modelo_no_cargado_label.pack_forget()
                self.base.modelo_cargado_label.pack(anchor='n', padx=10, pady=10, side='top', fill='x')
                new_window.destroy() 
            except Exception:
                messagebox.showerror("Error al cargar modelo", "El archivo no es válido")  
        
        apply_button = HoverButton(new_window, text="Aplicar", command=apply_function, 
                                font=("Arial", 12), bg="#569CD6", fg="white", padx=10, pady=5, cursor="hand2")
        apply_button.grid(row=5, column=0, columnspan=2, padx=10, pady=20)



