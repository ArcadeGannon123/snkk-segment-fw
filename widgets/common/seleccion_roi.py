import tkinter as tk
import numpy as np
from utils.func_image_processing import *

class SeleccionRoi(tk.Canvas):
    """Programa el comportamiento del rectangulo en el canvas"""
    def __init__(self, master=None, **kwargs):
        self.image = tk.PhotoImage() 
        super().__init__(master, **kwargs)

        # Configuración
        self.config(bd=0, highlightthickness=0, relief='raised', borderwidth=1)
        self.bind_events()

        # Propiedades
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.ORIGINAL_ROI = None
        self.RESHAPE_ROI = None

        self.max_res = 512

        self.mri_imagen_shape = (0,0,0)
        self.rect_selected = False
        self.edge_selected = None 
        self.rect_x_offset = 0
        self.rect_y_offset = 0
        self.rect_x2_offset = 0
        self.rect_y2_offset = 0

        self.imagenes_png_original = {}
        self.imagenes_png = {}

    def bind_events(self):
        self.bind("<Button-1>", self.on_press)
        self.bind("<Button-3>", self.remover_rectangulo)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Motion>", self.change_cursor)

    def on_press(self, event):
        # Detectar si se hace clic dentro del rectángulo para moverlo
        if self.rect:
            x1, y1, x2, y2 = self.coords(self.rect)

             # Detectar si se hizo clic en los bordes para ajustarlos
            if self.is_near_edge(event.x, event.y, x1, y1, x2, y2):
                self.edge_selected = self.get_edge_or_corner(event.x, event.y, x1, y1, x2, y2)
            elif x1 <= event.x <= x2 and y1 <= event.y <= y2:
                # Si se hizo clic dentro del rectángulo, se prepara para mover
                self.rect_selected = True
                self.rect_x_offset = event.x - x1
                self.rect_y_offset = event.y - y1
                self.rect_x2_offset = event.x - x2
                self.rect_y2_offset = event.y - y2
            else:
                # Si no se hace clic dentro, eliminar y empezar uno nuevo
                self.delete(self.rect)
                self.start_x = event.x
                self.start_y = event.y
                self.rect = self.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="#46eb34")
        else:
            # Crear un nuevo rectángulo si no hay uno
            self.start_x = event.x
            self.start_y = event.y
            self.rect = self.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="#46eb34")
    

    def on_drag(self, event):
        if self.rect_selected:
            # Mover el rectángulo
            new_x1 = event.x - self.rect_x_offset
            new_y1 = event.y - self.rect_y_offset
            new_x2 = event.x - self.rect_x2_offset
            new_y2 = event.y - self.rect_y2_offset

            # Restringir las coordenadas dentro del canvas
            new_x1 = min(max(new_x1, 0), self.max_res)
            new_y1 = min(max(new_y1, 0), self.max_res)
            new_x2 = min(max(new_x2, 0), self.max_res)
            new_y2 = min(max(new_y2, 0), self.max_res)

            self.coords(self.rect, new_x1, new_y1, new_x2, new_y2)
        elif self.edge_selected:
            # Ajustar el borde o esquina seleccionado
            x1, y1, x2, y2 = self.coords(self.rect)
            event_x = min(max(event.x, 0), self.max_res)
            event_y = min(max(event.y, 0), self.max_res)

            if self.edge_selected == "left":
                self.coords(self.rect, event_x, y1, x2, y2)
            elif self.edge_selected == "right":
                self.coords(self.rect, x1, y1, event_x, y2)
            elif self.edge_selected == "top":
                self.coords(self.rect, x1, event_y, x2, y2)
            elif self.edge_selected == "bottom":
                self.coords(self.rect, x1, y1, x2, event_y)
            elif self.edge_selected == "top-left":
                self.coords(self.rect, event_x, event_y, x2, y2)
            elif self.edge_selected == "top-right":
                self.coords(self.rect, x1, event_y, event_x, y2)
            elif self.edge_selected == "bottom-left":
                self.coords(self.rect, event_x, y1, x2, event_y)
            elif self.edge_selected == "bottom-right":
                self.coords(self.rect, x1, y1, event_x, event_y)
        else:
            # Continuar dibujando el rectángulo si no está seleccionado
            start_x = min(max(self.start_x, 0), self.max_res)
            start_y = min(max(self.start_y, 0), self.max_res)
            current_x = min(max(event.x, 0), self.max_res)
            current_y = min(max(event.y, 0), self.max_res)
            self.coords(self.rect, start_x, start_y, current_x, current_y)

    def on_release(self, event):
        self.rect_selected = False  # Deseleccionar el rectángulo
        self.edge_selected = None

        if self.rect:
            x1, y1, x2, y2 = self.coords(self.rect)
            x1 = min(max(x1, 0), self.max_res)
            y1 = min(max(y1, 0), self.max_res)
            x2 = min(max(x2, 0), self.max_res)
            y2 = min(max(y2, 0), self.max_res)
            self.ORIGINAL_ROI = np.array([x1, y1, x2, y2])
            original_shape = self.mri_imagen_shape
            self.RESHAPE_ROI = (np.array([x1, y1, x2, y2]) * (max(original_shape[1], original_shape[2]) / self.max_res)).round().astype(int)

    def change_cursor(self, event):
        if self.rect:
            x1, y1, x2, y2 = self.coords(self.rect)
            if self.is_near_edge(event.x, event.y, x1, y1, x2, y2):
                edge = self.get_edge_or_corner(event.x, event.y, x1, y1, x2, y2)
                if edge in ["left", "right"]:
                    self.config(cursor="sb_h_double_arrow")  # Flecha horizontal
                elif edge in ["top", "bottom"]:
                    self.config(cursor="sb_v_double_arrow")  # Flecha vertical
                elif edge in ["top-left", "bottom-right"]:
                    self.config(cursor="size_nw_se")  # Diagonal superior izquierda a inferior derecha
                elif edge in ["top-right", "bottom-left"]:
                    self.config(cursor="size_ne_sw")  # Diagonal superior derecha a inferior izquierda
            elif x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.config(cursor="hand2")  # Cambiar a cursor de mano cuando esté sobre el rectángulo
            else:
                self.config(cursor="")  # Restaurar el cursor por defecto cuando no esté sobre el rectángulo

    def is_near_edge(self, x, y, x1, y1, x2, y2, threshold=5):
        """Detectar si el cursor está cerca de un borde o esquina del rectángulo."""
        near_left_edge = x1 - threshold < x < x1 + threshold and y1 < y < y2
        near_right_edge = x2 - threshold < x < x2 + threshold and y1 < y < y2
        near_top_edge = y1 - threshold < y < y1 + threshold and x1 < x < x2
        near_bottom_edge = y2 - threshold < y < y2 + threshold and x1 < x < x2
        near_corner = self.is_near_corner(x, y, x1, y1, x2, y2, threshold)
        
        return near_left_edge or near_right_edge or near_top_edge or near_bottom_edge or near_corner

    def is_near_corner(self, x, y, x1, y1, x2, y2, threshold):
        """Detectar si el cursor está cerca de una de las cuatro esquinas."""
        return (
            (abs(x - x1) < threshold and abs(y - y1) < threshold) or  # Esquina superior izquierda
            (abs(x - x2) < threshold and abs(y - y1) < threshold) or  # Esquina superior derecha
            (abs(x - x1) < threshold and abs(y - y2) < threshold) or  # Esquina inferior izquierda
            (abs(x - x2) < threshold and abs(y - y2) < threshold)     # Esquina inferior derecha
        )

    def get_edge_or_corner(self, x, y, x1, y1, x2, y2, threshold=5):
        """Determinar qué borde o esquina está cerca del cursor."""
        if abs(x - x1) < threshold and abs(y - y1) < threshold:
            return "top-left"
        elif abs(x - x2) < threshold and abs(y - y1) < threshold:
            return "top-right"
        elif abs(x - x1) < threshold and abs(y - y2) < threshold:
            return "bottom-left"
        elif abs(x - x2) < threshold and abs(y - y2) < threshold:
            return "bottom-right"
        elif abs(x - x1) < threshold:
            return "left"
        elif abs(x - x2) < threshold:
            return "right"
        elif abs(y - y1) < threshold:
            return "top"
        elif abs(y - y2) < threshold:
            return "bottom"
        return None

    def get_roi(self,type_key):
        x1,y1,x2,y2 = self.ROI

        roi_image = recortar_region(self.imagenes_png[type_key],x1,y1,x2,y2)

        return roi_image

    def get_original_roi(self,type_key):
        x1,y1,x2,y2 = self.ORIGINAL_ROI
        roi_image = recortar_region(self.imagenes_png_original[type_key],x1,y1,x2,y2)
        
        return roi_image
    
    def posicionar_rectangulo(self, roi):
        x1, y1, x2, y2 = roi
        # Eliminar el rectángulo existente si hay uno
        if self.rect:
            self.delete(self.rect)

        # Crear un nuevo rectángulo con las coordenadas y colores especificados
        self.rect = self.create_rectangle(x1, y1, x2, y2, outline="#46eb34")
        
        self.ORIGINAL_ROI = np.array([x1, y1, x2, y2])
        original_shape = self.mri_imagen_shape
        self.RESHAPE_ROI = (np.array([x1, y1, x2, y2]) * (max(original_shape[1], original_shape[2]) / self.max_res)).round().astype(int)

    def remover_rectangulo(self,event):
        # Eliminar el rectángulo si existe
        if self.rect:
            self.delete(self.rect)
            self.rect = None  # Restablecer la referencia para indicar que no hay rectángulo

        self.ORIGINAL_ROI = None
        self.RESHAPE_ROI = None



