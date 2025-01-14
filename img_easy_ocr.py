import cv2
import easyocr
import re
import os
import datetime
import shutil
import traceback
import gc
from contextlib import contextmanager

def write_log(mensaje, tipo="INFO"):
    """
    Escribe mensajes de log en un archivo
    """
    log_file = os.path.join('imagenes', 'proceso.log')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f"{timestamp} - {tipo}: {mensaje}\n")

@contextmanager
def timer(descripcion):
    """
    Contexto para medir tiempo de ejecución
    """
    inicio = datetime.datetime.now()
    yield
    tiempo = datetime.datetime.now() - inicio
    write_log(f"{descripcion}: {tiempo.total_seconds():.2f} segundos")

def log_error(error_msg, seccion):
    """
    Registra errores en el archivo errores.txt
    """
    error_file = os.path.join('imagenes', 'errores.txt')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(error_file, 'a', encoding='utf-8') as file:
        file.write(f"\n{'='*50}\n")
        file.write(f"Fecha y hora: {timestamp}\n")
        file.write(f"Carpeta: {seccion}\n")
        file.write(f"Error: {error_msg}\n")
        file.write(f"{'='*50}\n")
    write_log(f"Error en {seccion}: {error_msg}", "ERROR")

def liberar_recursos():
    """
    Libera recursos del sistema
    """
    gc.collect()
    cv2.destroyAllWindows()

def read_text(seccion, image_name, reader):
    try:
        guardar_resultado = True
        num_lineas = 0

        path = os.path.join('imagenes', seccion, image_name)
        image = cv2.imread(path)
        
        if image is None:
            raise Exception(f"No se pudo leer la imagen: {image_name}")

        # Mantener solo la región de interés
        image_roi = image[250:, :]
        
        # Procesar la imagen
        result = reader.readtext(image_roi, paragraph=True)
        
        todo_el_texto = []
        for res in result:
            pt0 = res[0][0]
            pt1 = res[0][1]
            pt2 = res[0][2]
            pt3 = res[0][3]

            if guardar_resultado:
                cv2.putText(image_roi, res[1], (pt0[0], pt0[1] - 3), 2, 0.8, (166,56,242), 2)
                cv2.rectangle(image_roi, pt0, pt2, (0, 255, 0), 2)

            linea = res[1].upper()
            linea = re.sub(r'\d+', '', linea)
            linea = re.sub(r'[^A-ZÁÉÍÓÚÜÑÀÈÌÒÙÂÊÎÔÛÄËÏÖÜa-záéíóúüñàèìòùâêîôûäëïöü\s]', '', linea)
            linea = linea.strip()
            
            if not re.search(r'EMISIÓN|VOTÓ|NUM.|PÁGINA|ELECTORAL', linea):
                if len(linea) > 11:
                    todo_el_texto.append(linea)
                    num_lineas += 1

        # Guardar imagen procesada
        if guardar_resultado:
            resultado_dir = os.path.join('imagenes', seccion, 'resultado')
            os.makedirs(resultado_dir, exist_ok=True)
            image[250:, :] = image_roi
            cv2.imwrite(os.path.join(resultado_dir, 'res_' + image_name), image)

        # Liberar memoria
        del image
        del image_roi
        del result
        gc.collect()

        return "\n".join(todo_el_texto), num_lineas, False

    except Exception as e:
        error_msg = f"Error procesando imagen {image_name}: {str(e)}"
        log_error(error_msg, seccion)
        return "", 0, True
    finally:
        liberar_recursos()

def guardar_resultados_parciales(seccion, total_texto, conteo_lineas, 
                               tiempo_inicio, carpeta_con_errores):
    """
    Guarda los resultados parciales del procesamiento
    """
    try:
        directorio_seccion = os.path.join('imagenes', seccion)
        
        # Guardar texto principal
        with open(os.path.join(directorio_seccion, f'{seccion}.txt'), 'w', 
                 encoding='utf-8') as file:
            file.write("".join(total_texto))

        # Guardar estadísticas
        tiempo_actual = datetime.datetime.now()
        duracion = tiempo_actual - tiempo_inicio
        
        with open(os.path.join(directorio_seccion, 'lineas_procesadas.txt'), 'w', 
                 encoding='utf-8') as file:
            file.write(f"Fecha inicio: {tiempo_inicio.strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Última actualización: {tiempo_actual.strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Tiempo transcurrido: {duracion.total_seconds() / 60:.2f} minutos\n")
            file.write(f"Estado: {'Con errores' if carpeta_con_errores else 'En proceso'}\n")
            file.write("\nDetalle de líneas procesadas:\n")
            for imagen, num_lineas in conteo_lineas.items():
                file.write(f"{imagen:<40} ->\t\t{num_lineas}\n")

    except Exception as e:
        write_log(f"Error guardando resultados parciales: {str(e)}", "ERROR")

def procesar_carpeta(seccion, reader):
    """
    Procesa una carpeta completa de imágenes
    """
    try:
        carpeta_con_errores = False
        tiempo_inicio_carpeta = datetime.datetime.now()
        write_log(f"Iniciando procesamiento de carpeta: {seccion}")
        
        directorio_seccion = os.path.join('imagenes', seccion)
        nombres_imagenes = [f for f in os.listdir(directorio_seccion) 
                          if f.lower().endswith('.jpg')]

        if not nombres_imagenes:
            write_log(f"No se encontraron imágenes JPG en {seccion}", "WARNING")
            return False

        # Procesar imágenes por lotes
        batch_size = 10
        total_texto = []
        conteo_lineas = {}

        for i in range(0, len(nombres_imagenes), batch_size):
            batch = nombres_imagenes[i:i+batch_size]
            
            for image_name in batch:
                texto_imagen, num_lineas, hubo_error = read_text(seccion, image_name, reader)
                if hubo_error:
                    carpeta_con_errores = True
                total_texto.append(f"***{image_name}\n{texto_imagen}\n")
                conteo_lineas[image_name] = num_lineas

            # Guardar resultados parciales
            guardar_resultados_parciales(seccion, total_texto, conteo_lineas, 
                                      tiempo_inicio_carpeta, carpeta_con_errores)
            
            # Liberar memoria después de cada lote
            gc.collect()

        return carpeta_con_errores

    except Exception as e:
        error_msg = f"Error procesando carpeta {seccion}: {str(e)}"
        log_error(error_msg, seccion)
        return True

def main():
    write_log("Iniciando proceso de OCR")
    print("Hora de inicio: ", datetime.datetime.now())

    try:
        reader = easyocr.Reader(['es'], gpu=False)
        procesados_dir = os.path.join('imagenes', 'procesados')
        os.makedirs(procesados_dir, exist_ok=True)

        directorio_base = 'imagenes'
        carpetas = [d for d in os.listdir(directorio_base) 
                   if os.path.isdir(os.path.join(directorio_base, d)) 
                   and d != 'procesados']

        total_carpetas = len(carpetas)
        for idx, seccion in enumerate(carpetas, 1):
            write_log(f"Procesando carpeta {idx}/{total_carpetas}: {seccion}")
            
            with timer(f"Procesamiento completo de carpeta {seccion}"):
                carpeta_con_errores = procesar_carpeta(seccion, reader)

                if not carpeta_con_errores:
                    destino = os.path.join(procesados_dir, seccion)
                    if os.path.exists(destino):
                        shutil.rmtree(destino)
                    shutil.move(os.path.join('imagenes', seccion), destino)
                    write_log(f"Carpeta {seccion} procesada y movida exitosamente")
                else:
                    write_log(f"Carpeta {seccion} contiene errores y no será movida", "WARNING")

            # Liberar recursos después de cada carpeta
            liberar_recursos()

    except Exception as e:
        error_msg = f"Error general del programa: {str(e)}"
        log_error(error_msg, "ERROR_GENERAL")
        write_log(f"Error general del programa: {str(e)}", "CRITICAL")
    
    finally:
        write_log("Proceso finalizado")
        print("Hora de fin: ", datetime.datetime.now())

if __name__ == "__main__":
    main()
