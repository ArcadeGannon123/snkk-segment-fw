from keras.models import load_model
import numpy as np
import cv2

class KerasModelLoader:

    def __init__(self, model_path):
        
        # Propiedades
        self.n_frames = 128
        self.dim_train = 32
        self.model_path = model_path
        self.model = self.load_model()
        self.array_volumenes = []
        self.coordenadas = {}
        self.imagenes = {}
        self.seg_all_frames = []
        self.segmentacion_completa = []

    def load_model(self):
        """Carga el modelo 3D Unet"""
        model = load_model(self.model_path, compile=False)
        print(f"Modelo cargado desde {self.model_path}")
        return model


    def input_data(self,secuencia_magnitud_fase):   
        """Recibe la secuencia de imagenes de magnitud y fase y crea los volumenes para la entrada del modelo 3D Unet"""         
        sequence_slices = []
        for tipo_imagen in secuencia_magnitud_fase:
            segment = self.cortar_array(np.array(tipo_imagen),self.n_frames,len(tipo_imagen))
            sequence_slices.append(segment)
            
        self.array_volumenes = np.array(sequence_slices)

    def recortar_region(self,imagenes, x_inicio, y_inicio, ancho, alto):
        """Recorta la región de interés de la secuencia de imagenes"""    
        imagenes_recortadas = []
        for imagen in imagenes:
            imagen_recortada = imagen[y_inicio:y_inicio+alto, x_inicio:x_inicio+ancho]
            imagenes_recortadas.append(imagen_recortada)
        return imagenes_recortadas

    def completar_array(self,ultimo_volumen, secuencia_imagenes, longitud_deseada, long_secuencia):
        """Completa el último volumen recortado de la secuencia de imagenes con los fotogramas iniciales para llegar a la longitud deseada"""    
        long_actual = len(ultimo_volumen)     
        miss_frames = longitud_deseada - long_actual # Fotogramas faltantes
        init_seq = 0
        for _ in range(miss_frames):
            if init_seq >= long_secuencia:
                init_seq = 0
                
            ultimo_volumen.append(secuencia_imagenes[init_seq]) # Añade los fotogramas faltantes en el volumen    
            init_seq +=1
        return ultimo_volumen
    
    def cortar_array(self,array,n_frames,long_secuencia):
        """Corta la secuencia de imagenes en volumenes de la misma cantidad de fotogramas"""  
        
        elementos_necesarios = n_frames - len(array) % n_frames # Calcula cuántos elementos se necesitan para completar el último trozo
        
        array_cortado = [array[i:i+n_frames] for i in range(0, len(array), n_frames)]
        
        if elementos_necesarios != n_frames: # completa el último trozo con la cantidad de fotogramas deseada
            array_cortado[-1] = self.completar_array(array_cortado[-1].tolist(), array, n_frames,long_secuencia)
        return array_cortado

    def predict(self):
        """Predice la segmentación para los volumenes con el modelo 3D Unet"""

        input_fase_magnitud = np.stack((self.array_volumenes[0],self.array_volumenes[1]), axis=-1)/255. # Combina los volumenes de magnitud y fase en un solo volumen con dos canales
        predictions = self.model.predict(input_fase_magnitud) # Predice la segmentación para los volumenes

        y_pred_reshape = predictions.reshape(self.n_frames*predictions.shape[0], self.dim_train, self.dim_train) # Convierte los volumenes en una secuencia de imagenes

        new_shape = (self.coordenadas['ancho'],self.coordenadas['alto'])
        position = (self.coordenadas['x1'],self.coordenadas['y1'])
        
        y_pred_original_dim = self.redimensionar(y_pred_reshape,new_shape) # restaura la dimensión de las ROIs a su dimension original

        self.seg_all_frames = y_pred_original_dim[:self.imagenes['magnitud'].shape[0],:,:] # Ajusta el largo del array de segmentaciones al largo de la secuencia de imagenes original

        self.segmentacion_completa = self.completar_imagen(self.seg_all_frames,self.imagenes['magnitud'].shape,position) # Posiciona la segmentación de la ROI en la posición original dentro de las imagenes
        
        return self.segmentacion_completa
    
    def redimensionar(self,secuencia_area,new_shape):
        """Redimensiona una secuencia de imagenes en numpy array y normaliza los pixeles a 255"""
        secuencia_resize = []
        for imagen_recortada in secuencia_area:        
            secuencia_resize.append(cv2.resize(imagen_recortada, new_shape))
    
        secuencia_resize = np.array(secuencia_resize)
        secuencia_resize = (secuencia_resize.astype(np.float32) / np.max(secuencia_resize)) * 255.0
        secuencia_resize = secuencia_resize.astype(np.uint8)
        
        return secuencia_resize
    
    def completar_imagen(self,segmentacion,original_shape,coordenadas,bias=200):
        """Posiciona la ROI en una imagen de dimensión más grande según unas coordenadas"""

        # Copia de la imagen grande para no modificar la original
        segmentacion_blank = np.zeros(original_shape, np.uint8)
        
        # Obtener las dimensiones de la imagen grande y pequeña
        _,alto_grande, ancho_grande = segmentacion_blank.shape
        _,alto_pequena, ancho_pequena = segmentacion.shape
    
        # Asegurar que las coordenadas estén dentro de los límites de la imagen grande
        x_inicio = max(0, coordenadas[0])
        y_inicio = max(0, coordenadas[1])
        x_fin = min(ancho_grande, coordenadas[0] + ancho_pequena)
        y_fin = min(alto_grande, coordenadas[1] + alto_pequena)
        
        segmentacion[segmentacion > bias] = 255.
    
        mascara_segmentada = segmentacion > bias
        
        # Superponer la imagen pequeña en la imagen grande
        segmentacion_blank[:,y_inicio:y_fin, x_inicio:x_fin][mascara_segmentada] = segmentacion[:,:,:][mascara_segmentada]
    
        return segmentacion_blank
        
    