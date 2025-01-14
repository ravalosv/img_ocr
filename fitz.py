

import cv2
import pytesseract as tess
from pytesseract import Output


tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Path to the tesseract executable


myconfig = r"--psm 11 --oem 3"

img = cv2.imread("666c2_page-0019.jpg")
height, width, _ = img.shape


data = tess.image_to_data(img, config=myconfig, output_type=Output.DICT)

amount_boxes = len(data['text'])

print(amount_boxes)
 
for i in range(amount_boxes):
    if float(data['conf'][i]) >= 70:
        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        #img = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        img = cv2.putText(img, data['text'][i], (x+100, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0, 255), 2, cv2.LINE_AA)

cv2.imshow("Result", img)
cv2.waitKey(0) 


""" boxes = tess.image_to_boxes(img, config=myconfig)

for box in boxes.splitlines():
    box = box.split(" ")
    x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
    img = cv2.rectangle(img, (x, height - y), (w, height - h), (0, 255, 0), 3)
cv2.imshow("Result", img)
cv2.waitKey(0) """

