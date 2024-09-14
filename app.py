import tkinter as tk
from utils.segment_model import KerasModelLoader
import tensorflow as tf
from widgets.barras.barra_superior import BarraSuperior
from widgets.barras.barra_inferior import BarraInferior
from widgets.barras.barra_lateral import BarraLateral
from widgets.ventanas.base import Base
from utils.func_image_processing import cargar_icono

# Lista de GPUs disponibles
# gpus = tf.config.list_physical_devices('GPU')
# if gpus:
#     try:
#         # Dejar visible solo el CPU
#         tf.config.set_visible_devices([], 'GPU')
#         print("GPU desactivada, solo CPU en uso.")
#     except RuntimeError as e:
#         print(e)
# if gpus:
#     try:
#         # Establecer una fracción de memoria máxima para cada GPU
#         for gpu in gpus:
#             tf.config.experimental.set_virtual_device_configuration(
#                 gpu,
#                 [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=0)])
#         logical_gpus = tf.config.list_logical_devices('GPU')
#         print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
#     except RuntimeError as e:
#         # Las configuraciones deben ser establecidas antes de que se asigne memoria en GPU
#         print(e)mri_3D_150epochs_128x32x32_0_00001LR_batch4

#MODELO = KerasModelLoader('C:/Users/snkk/Documents/PROYECTO_MEMORIA/3D_CNN/mri_3D_200epochs_64x32x32_0_00001LR_batch4.h5')
#MODELO = KerasModelLoader('C:/Users/snkk/Documents/PROYECTO_MEMORIA/3D_CNN/mri_3D_400epochs_128x32x32_0_000001LR_batch8.h5')
#MODELO = KerasModelLoader('C:/Users/snkk/Documents/PROYECTO_MEMORIA/3D_CNN/mri_3D_400epochs_64x32x32_0_000001LR_batch16.h5')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Segmentación 3D Unet")
        self.geometry("1600x900")
        
        self.icono_carpeta = cargar_icono("./icons/conexiones.png")
        self.iconphoto(False, self.icono_carpeta)
                
        self.barra_superior = BarraSuperior(self)
        self.barra_superior.pack(side=tk.TOP, fill=tk.X)
        
        self.base = Base(self)
        self.base.pack_propagate(False) 
        self.base.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.barra_superior.set_base(self.base)

        self.barra_lateral = BarraLateral(self.base)
        self.barra_lateral.grid(row=0, column=0, sticky="nsew")
        self.barra_superior.set_barra_lateral(self.barra_lateral)

        self.barra_inferior = BarraInferior(self)
        self.barra_inferior.pack(side=tk.BOTTOM, fill=tk.X)
        self.barra_inferior.set_base(self.base)
        self.barra_inferior.set_barra_superior(self.barra_superior)
        self.barra_inferior.set_barra_lateral(self.barra_lateral)

if __name__ == "__main__":
    app = App()
    app.mainloop()
