import cv2
from PIL import Image
import pytesseract

im_file = 'data/page_01.png'

im = Image.open(im_file)
print(im)
im.show()
im.save('temp/page_01.png')
