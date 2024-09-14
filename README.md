# Framework Segment 3D Unet

## Descripción

Framework de segmentación de imagenes de resonancia magnética por contraste de fase qué utiliza un modelo 3D Unet

## Requisitos del sistema

- Python 3.9

## Dependencias

La aplicación utiliza las siguientes librerías de Python:

- `tensorflow`
- `keras`
- `matplotlib`
- `pydicom`
- `scipy`
- `opencv-python`
- `pillow`
- `tkinter`
- `Modelo 3D Unet entrenado`

## Instalación

Para la instalacion se deben seguir los siguientes pasos:

1. Clonar repositorio en la máquina local.

2. Crear un entorno virtual con Python 3.9.
    ```bash
    python -m venv venv
3. Activar el entorno.
    ```bash
    # Windows
    .\venv\script\activate
    # Linux
    source venv/bin/activate
4. Instalar dependencias.
    ```bash
    pip install -r requirements.txt
5. Ejecutar la aplicación
    ```bash
    python app.py
## Instrucciones de uso

### Interfaz principal
<img src="./tutorial/main_interfaz.png" alt="imagen" width="900" height="auto" />

### 1. Cargar Modelo
El botón <b>Cargar Modelo</b> se utiliza para cargar el modelo 3D Unet en el framework.<br/><br/>
<img src="./tutorial/cargar_modelo.png" alt="imagen" width="512" height="auto" /><br/><br/>
Se debe seleccionar la ubicación del archivo para luego aplicar. Si todo salio bien el mensaje en la interfaz cambiará.<br/><br/>
<img src="./tutorial/mensaje_modelo.png" alt="imagen" width="128" height="auto" /><br/><br/>

### 2. Importar DICOM
El botón <b>Importar DICOM</b> sirve para cargar las imagenes de resonsancia magnética por contraste de fase en formato dicom.<br/><br/>
<img src="./tutorial/importacion_dicom.png" alt="imagen" width="512" height="auto" /><br/><br/>
Si la importación es exitosa se verán las imagenes de magnitud y fase en el <b>Panel</b>.<br/><br/>

### 3. Panel
En el Panel se podrá ver las imagenes de magnitud y fase de los archivos Dicom.<br/><br/>
<img src="./tutorial/visor_mri.png" alt="imagen" width="512" height="auto" /><br/><br/>
En esta interfaz se debe <b>enmarcar</b> la <b>Región de Interés</b> que se quiera <b>segmentar</b> utilizando el mouse y dibujando un rectangulo cubriendo lo mejor posible el área de interés.<br/><br/>
<img src="./tutorial/roi.png" alt="imagen" width="512" height="auto" /><br/><br/>

### 4. Linea de Tiempo
La <b>Linea de Tiempo</b> permite manipular la reproducción de la secuencia de imagenes en pantalla.<br/><br/>
<img src="./tutorial/linea_de_tiempo.png" alt="imagen" width="512" height="auto" /><br/><br/>
En ella de podrá <b>iniciar</b>, <b>pausar</b>, <b>detener</b> y mover la animación <b>fotograma</b> a <b>fotograma</b>.<br/><br/>

### 5. Segmentar ROI
El botón <b>Segmentar ROI</b> sive para segmentar la <b>Región de Interés</b> enmarcada en el <b>Panel</b>. Para realizar esta acción el <b>modelo 3D Unet</b> debe estar cargado y la Región de interés enmarcada en el Panel<br/><br/>
<img src="./tutorial/segmentar_roi.png" alt="imagen" width="256" height="auto" /><br/><br/>
En la Ventana Emergente se debe ingresar un <b>nombre</b> para la segmentación y un <b>color</b>. Si todo sale bien la segmentación se verá en el Panel y un bloque con la información se verá en la barra lateral<br/><br/>
<img src="./tutorial/segmentacion.png" alt="imagen" width="900" height="auto" /><br/><br/>
El bloque en la barra lateral permite realizar diversas acciones<br/><br/>
<img src="./tutorial/bloque.png" alt="imagen" width="256" height="auto" /><br/><br/>

1. El icono de <b>ojo</b> permite activar u ocultar la segmentación en el Panel.<br/>
2. El icono de <b>Gráficos</b> abre una ventana con los gráficos de <b>área</b>, <b>velocidad media</b> y <b>flujo</b> calculados a partir de la segmentación.<br/><br/>
<img src="./tutorial/graficos.png" alt="imagen" width="512" height="auto" /><br/>

3. El icono de <b>Basurero</b> sirve para eliminar la segmentación.<br/>
4. El icono de <b>Exportar</b> permite exportar los datos de dicha segmentación, como la máscara y los datos de los gráficos.<br/>

### 6. Exportar a .mat

El botón <b>Exportar a .mat</b> permite exportar todas las segmentaciones realizadas en la interfaz en un único archivo .mat. Para el caso de que se hayan realizado multiples segmentaciones.<br/><br/>
<img src="./tutorial/multiples_segmentaciones.png" alt="imagen" width="720" height="auto" /><br/>