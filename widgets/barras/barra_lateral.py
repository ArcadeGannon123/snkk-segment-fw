import tkinter as tk
from utils.func_image_processing import cargar_icono
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox 
from widgets.ventanas.graph_window import GraphWindow

class BarraLateral(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Configuración
        self.config(bg='#1E1E1E')
        self.pack_propagate(False) 

        # Iconos
        self.trash_imagen = cargar_icono("./icons/bote-de-basura.png")
        self.chart_imagen = cargar_icono("./icons/chart.png")
        self.export_imagen = cargar_icono("./icons/exportar.png")
        self.eye_open = cargar_icono("./icons/ojo.png")
        self.eye_closed = cargar_icono("./icons/ojo_closed.png")

        # Propiedades
        self.bloques = {}

    def crear_bloque(self,id,texto, datos,img, new_width, new_height,color,activado,roi):
        """Posiciona un bloque con la informacion de una segmentación en la barra lateral"""
        imagen = self.load_image(img, new_width, new_height)
        
        # Frame para cada bloque
        bloque = tk.Frame(self, bg='#D69D85')
        bloque.pack(padx=5, pady=5)
        bloque.grid_columnconfigure(0, weight=1)
        bloque.grid_columnconfigure(1, weight=4)
        bloque.grid_rowconfigure(0, weight=1)

        visible_button = tk.Frame(bloque)
        visible_button.grid_rowconfigure(0, weight=1)
        visible_button.grid_rowconfigure(2, weight=1)
        visible_button.grid_columnconfigure(0, weight=1)
        visible_button.grid(row=0, column=0, sticky="nsew")

        bloque.btn_eye_open = ttk.Button(visible_button, image=self.eye_open,command=lambda: self.activar_segmentacion(id,False,bloque))
        bloque.btn_eye_open.grid(row=1, column=0, sticky="nsew",padx=(5,0)) 
        

        bloque.btn_eye_closed = ttk.Button(visible_button, image=self.eye_closed,command=lambda: self.activar_segmentacion(id,True,bloque))
        bloque.btn_eye_closed.grid(row=1, column=0, sticky="nsew",padx=(5,0)) 

        if activado:
            bloque.btn_eye_closed.grid_forget()
        else:
            bloque.btn_eye_open.grid_forget()

        self.bloques[id]=bloque
    
        # Crear un frame para organizar la imagen y el texto/botones horizontalmente
        horizontal_frame = tk.Frame(bloque)
        horizontal_frame.grid(row=0, column=1, sticky="nsew")
    
        # Añadir la imagen al lado izquierdo
        label_imagen = tk.Label(horizontal_frame, image=imagen, bg=color, cursor="hand2")
        label_imagen.pack(side='left', padx=5)
        label_imagen.image = imagen
        label_imagen.roi = roi
        label_imagen.bind("<Button-1>", lambda event: self.master.area_trabajo.posicionar_rectangulo(label_imagen.roi))
    
        # Crear un frame a la derecha para el texto y los botones
        texto_botones_frame = tk.Frame(horizontal_frame)
        texto_botones_frame.pack(side='left', padx=10, pady=5, expand=True)
    
        # Añadir el texto
        label_texto = tk.Label(texto_botones_frame, text=texto, font=("Helvetica", 10))
        label_texto.pack(anchor='w')
    
        # Crear un frame para los botones
        botones_frame = tk.Frame(texto_botones_frame)
        botones_frame.pack(fill='x', pady=5)
    
        # Añadir botones alineados
        btn1 = ttk.Button(botones_frame, image=self.chart_imagen, command=lambda: self.ventana_graficos(datos))
        btn1.pack(side='left', padx=5)

        btn2 = ttk.Button(botones_frame, image=self.trash_imagen, command=lambda: self.confirm_removal(id,bloque))
        btn2.pack(side='left', padx=5)

        btn3 = ttk.Button(botones_frame, image=self.export_imagen, command=lambda: self.exportar_segmentacion(id))
        btn3.pack(side='left', padx=5)

            
    def load_image(self,array, new_width, new_height):
        """Convierte y redimensiona una imagen en numpy array en un objeto PhotoImage"""
        image = Image.fromarray(array).resize((new_width,new_height))
        return ImageTk.PhotoImage(image)

    def confirm_removal(self, id, frame):
        """Método para confirmar la eliminación de un frame"""
        # Mostrar un cuadro de diálogo para confirmar la eliminación
        confirm = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este Frame?")
        
        if confirm:  # Si el usuario selecciona 'Sí'
            self.remove_frame(id,frame)

    def remove_frame(self, id, frame):
        """Método para eliminar un bloque específico junto con la segmentación asociada"""
        frame.destroy()  # Destruir el frame y sus hijos
        del self.bloques[id]# Removerlo de la lista de frames
        self.master.area_trabajo.del_segmentacion(id)

    def exportar_segmentacion(self, id):
        """Método para exportar los datos de la segmentación a un archivo .mat"""
        self.master.export_to_mat(id)

    def clean_sidebar(self):
        """Limpia la barra lateral"""
        for _,bloque in self.bloques.items():
            bloque.destroy()

    def ventana_graficos(self,datos):
        """Abre una ventana que muestra los gráficos asociados a la segmentación"""
        nueva_ventana = tk.Toplevel(self)
        GraphWindow(nueva_ventana,datos)
    
    
    def activar_segmentacion(self,id,activado,bloque):
        """Método para activar o desactivar una segmentación"""
        if activado:
            self.master.area_trabajo.set_visualizacion(id,True)
            bloque.btn_eye_closed.grid_forget()
            bloque.btn_eye_open.grid(row=1, column=0, sticky="nsew",padx=(5,0))  
        else:
            self.master.area_trabajo.set_visualizacion(id,False)
            bloque.btn_eye_open.grid_forget()
            bloque.btn_eye_closed.grid(row=1, column=0, sticky="nsew",padx=(5,0)) 
