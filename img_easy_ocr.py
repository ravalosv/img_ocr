import cv2
import easyocr
import re
import os
import datetime


def read_text(seccion, image_name):
    print("Leyendo imagen: ", image_name)
    path = r'imagenes/' + seccion + '/'
    image = cv2.imread(path + image_name)

    image = image[400:, :]

    result = reader.readtext(image,paragraph=True)

    todo_el_texto = ""
    linea = ""
    for res in result:
        pt0 = res[0][0]
        pt1 = res[0][1]
        pt2 = res[0][2]
        pt3 = res[0][3]

        #cv2.rectangle(image, pt0, (pt1[0], pt1[1] - 23), (166,56,242), -1)
        cv2.putText(image, res[1], (pt0[0], pt0[1] - 3), 2, 0.8, (166,56,242), 2)

        cv2.rectangle(image, pt0, pt2, (0, 255, 0), 2)

        linea = res[1].upper()

    # Eliminar cualquier número de la línea
        linea = re.sub(r'\d+', '', linea)
        linea = linea.strip()
        
        if not re.search(r'EMISIÓN|VOTÓ|NUM.|PÁGINA|ELECTORAL', linea):
            if len(linea) > 10:
                todo_el_texto += linea + "\n"


    path = r'imagenes/' + seccion + '/res_' + image_name
    cv2.imwrite(path, image)
    #cv2.imshow("Result", image)

    todo_el_texto = todo_el_texto.upper()

    return todo_el_texto


print("Hora de inicio: ", datetime.datetime.now())

seccion = "666c2"
reader = easyocr.Reader(['es'], gpu=False)

# leer el directorio de la sección y obtener el nombre de las imágenes
directorio_seccion = os.path.join('imagenes', seccion)

# Obtener la lista de nombres de las imágenes en el directorio
nombres_imagenes = [f for f in os.listdir(directorio_seccion) if os.path.isfile(os.path.join(directorio_seccion, f)) and f.lower().endswith('.jpg')]

todo_el_texto = ""
for image_name in nombres_imagenes:
    todo_el_texto = todo_el_texto + '***' + image_name + "\n"
    todo_el_texto = todo_el_texto + read_text(seccion, image_name) + "\n"

file_name = os.path.join(directorio_seccion, seccion + '.txt')

print("Guardando el archivo: ", file_name)
# Guardar el contenido de todo_el_texto en un archivo de texto
with open(file_name, 'w', encoding='utf-8') as file:
    file.write(todo_el_texto)

print("Hora de fin: ", datetime.datetime.now())

cv2.waitKey(0)
cv2.destroyAllWindows()

