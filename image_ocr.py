import pytesseract as tess
from PIL import Image
import cv2

tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Path to the tesseract executable

#my_image = Image.open('F:\\Mis Proyectos\\git\\python_pdf\\ocr_python\\ines.png') # Load the image
my_image = cv2.imread('F:\\Mis Proyectos\\git\\python_pdf\\ocr_python\\ines.png') # Load the image
txt = tess.image_to_string(my_image) # Perform OCR
print(txt) # Print the text
