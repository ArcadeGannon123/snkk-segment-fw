import pydicom
import numpy as np

def leer_dicom_magnitud_fase(ruta_archivos):
    """Extrae la informacion de los archivos DICOM"""
    datos = {
        'pixel_spacing':[1,1],
        'timeline':[],
        'patient_id':"ANON",
        'imagetypes':{
            'magnitud':[],
            'fase':[]
        }
    }
    for ruta_archivo in ruta_archivos:
        dataset = pydicom.dcmread(ruta_archivo)
        type = list(dataset.ImageType)
        datos['pixel_spacing'] = dataset.PixelSpacing
        datos['patient_id'] = dataset.PatientID
        if type[3] == 'P' and type[4] == 'PCA':
            # IM X RS + INTER
            # pixelSpacing mm
            # rescale slope = dataset.RescaleSlope
            # rescale intersept = dataset.intersept
            datos['imagetypes']['fase'].append([int(dataset.InstanceNumber), np.array(dataset.pixel_array) * dataset.RescaleSlope + dataset.RescaleIntercept])
            datos['timeline'].append(dataset.TriggerTime)
        elif type[3] == 'M' and type[4] == 'FFE':
            datos['imagetypes']['magnitud'].append([int(dataset.InstanceNumber), dataset.pixel_array])

    

    for key_type in datos['imagetypes'].keys():
        datos['imagetypes'][key_type] = np.array([tupla[1] for tupla in sorted(datos['imagetypes'][key_type], key=lambda x: x[0])])
    datos['timeline'].sort()
    return datos