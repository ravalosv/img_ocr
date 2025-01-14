import cv2
import easyocr
import re
import os
import datetime
import shutil
import traceback

def log_error(error_msg, seccion):
    """
    Función para registrar errores en el archivo errores.txt
    """
    error_file = os.path.join('imagenes', 'errores.txt')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(error_file, 'a', encoding='utf-8') as file:
        file.write(f"\n{'='*50}\n")
        file.write(f"Fecha y hora: {timestamp}\n")
        file.write(f"Carpeta: {seccion}\n")
        file.write(f"Error: {error_msg}\n")
        file.write(f"{'='*50}\n")

def read_text(seccion, image_name):
    try:
        guardar_resultado = True
        num_lineas = 0

        print("Leyendo imagen: ", image_name)
        path = r'imagenes/' + seccion + '/'
        image = cv2.imread(path + image_name)
        
        if image is None:
            raise Exception(f"No se pudo leer la imagen: {image_name}")

        image = image[250:, :]
        result = reader.readtext(image,paragraph=True)

        todo_el_texto = ""
        linea = ""
        for res in result:
            pt0 = res[0][0]
            pt1 = res[0][1]
            pt2 = res[0][2]
            pt3 = res[0][3]

            if guardar_resultado:
                cv2.putText(image, res[1], (pt0[0], pt0[1] - 3), 2, 0.8, (166,56,242), 2)
                cv2.rectangle(image, pt0, pt2, (0, 255, 0), 2)

            linea = res[1].upper()
            linea = re.sub(r'\d+', '', linea)
            linea = re.sub(r'[^A-ZÁÉÍÓÚÜÑÀÈÌÒÙÂÊÎÔÛÄËÏÖÜa-záéíóúüñàèìòùâêîôûäëïöü\s]', '', linea)
            linea = linea.strip()
            
            if not re.search(r'EMISIÓN|VOTÓ|NUM.|PÁGINA|ELECTORAL', linea):
                if len(linea) > 10:
                    todo_el_texto += linea + "\n"
                    num_lineas += 1

        resultado_dir = os.path.join('imagenes', seccion, 'resultado')
        os.makedirs(resultado_dir, exist_ok=True)
        
        if guardar_resultado:
            path = os.path.join(resultado_dir, 'res_' + image_name)
            cv2.imwrite(path, image)

        todo_el_texto = todo_el_texto.upper()
        return todo_el_texto, num_lineas, False  # False indica que no hubo error
    except Exception as e:
        error_msg = f"Error procesando imagen {image_name}: {str(e)}\n{traceback.format_exc()}"
        log_error(error_msg, seccion)
        return "", 0, True  # True indica que hubo error

print("Hora de inicio: ", datetime.datetime.now())

try:
    reader = easyocr.Reader(['es'], gpu=False)
    procesados_dir = os.path.join('imagenes', 'procesados')
    os.makedirs(procesados_dir, exist_ok=True)

    directorio_base = 'imagenes'
    carpetas = [d for d in os.listdir(directorio_base) 
               if os.path.isdir(os.path.join(directorio_base, d)) 
               and d != 'procesados']

    # Procesar cada carpeta
    for seccion in carpetas:
        try:
            carpeta_con_errores = False  # Flag para controlar si hubo errores en la carpeta
            tiempo_inicio_carpeta = datetime.datetime.now()
            print(f"\nProcesando carpeta: {seccion}")
            directorio_seccion = os.path.join('imagenes', seccion)
            
            nombres_imagenes = [f for f in os.listdir(directorio_seccion) 
                              if os.path.isfile(os.path.join(directorio_seccion, f)) 
                              and f.lower().endswith('.jpg')]
            
            if not nombres_imagenes:
                print(f"No se encontraron imágenes JPG en la carpeta {seccion}")
                continue
            
            resultado_dir = os.path.join(directorio_seccion)
            os.makedirs(resultado_dir, exist_ok=True)
            
            conteo_lineas = {}
            todo_el_texto = ""
            for image_name in nombres_imagenes:
                texto_imagen, num_lineas, hubo_error = read_text(seccion, image_name)
                if hubo_error:
                    carpeta_con_errores = True
                todo_el_texto += '***' + image_name + "\n"
                todo_el_texto += texto_imagen + "\n"
                conteo_lineas[image_name] = num_lineas

            # Guardar el archivo de texto principal
            file_name = os.path.join(resultado_dir, seccion + '.txt')
            print("Guardando el archivo: ", file_name)
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(todo_el_texto)
            
            tiempo_fin_carpeta = datetime.datetime.now()
            duracion = tiempo_fin_carpeta - tiempo_inicio_carpeta
            duracion_minutos = duracion.total_seconds() / 60.0

            # Guardar el archivo de líneas procesadas
            lineas_file = os.path.join(resultado_dir, 'lineas_procesadas.txt')
            with open(lineas_file, 'w', encoding='utf-8') as file:
                file.write(f"Fecha y hora de inicio: {tiempo_inicio_carpeta.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"Fecha y hora de fin: {tiempo_fin_carpeta.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"Tiempo de procesamiento: {duracion_minutos:.2f} minutos\n")
                file.write(f"Estado: {'Con errores' if carpeta_con_errores else 'Procesado correctamente'}\n")
                file.write("\nDetalle de líneas procesadas por archivo:\n")
                file.write("-" * 60 + "\n\n")
                
                for imagen, num_lineas in conteo_lineas.items():
                    file.write(f"{imagen:<40} ->\t\t{num_lineas}\n")
            
            # Solo mover la carpeta si no hubo errores
            if not carpeta_con_errores:
                destino = os.path.join(procesados_dir, seccion)
                print(f"Moviendo carpeta {seccion} a procesados...")
                
                if os.path.exists(destino):
                    shutil.rmtree(destino)
                
                shutil.move(directorio_seccion, destino)
                print(f"Carpeta {seccion} movida exitosamente a procesados")
            else:
                print(f"La carpeta {seccion} contiene errores y no será movida a procesados")

        except Exception as e:
            error_msg = f"Error procesando carpeta {seccion}: {str(e)}\n{traceback.format_exc()}"
            log_error(error_msg, seccion)
            print(f"Error en carpeta {seccion}. Continuando con la siguiente...")
            continue

    print("\nHora de fin: ", datetime.datetime.now())

except Exception as e:
    error_msg = f"Error general del programa: {str(e)}\n{traceback.format_exc()}"
    log_error(error_msg, "ERROR_GENERAL")
    print("Se ha producido un error general en el programa")
