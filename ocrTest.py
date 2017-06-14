from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import os


pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'

image = cv2.imread("Phthalo Green Text.jpg")
text = pytesseract.image_to_string(Image.open('Phthalo Green Text.jpg'),
                                        config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")
print(text+'\n')

gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imwrite('temp1.jpg', gray_image)

blurred = cv2.GaussianBlur(gray_image, (5,5), 0)
cv2.imwrite('temp2.jpg', blurred)

high_thresh, thresh_im = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
lowThresh = 0.5*high_thresh
edged = cv2.Canny(blurred, 50, 200)
cv2.imwrite('temp3.jpg', edged)

text_gray = pytesseract.image_to_string(Image.open('temp1.jpg'),
                                        config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")

text_blurred = pytesseract.image_to_string(Image.open('temp2.jpg'),
                                           config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")
text_canny = pytesseract.image_to_string(Image.open('temp3.jpg'),
                                         config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")
print('Gray Scale ' + text_gray +"\n With Gaussian Blur: " +text_blurred +'\n After Canny Edge Detection: ' + text_canny)



#vd brown

image = cv2.imread("Van Dyke Brown Text.jpg")
text = pytesseract.image_to_string(Image.open('Van Dyke Brown Text.jpg'),
                                        config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")
print(text+'\n')

gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imwrite('temp1.jpg', gray_image)

blurred = cv2.GaussianBlur(gray_image, (5,5), 0)
cv2.imwrite('temp2.jpg', blurred)

high_thresh, thresh_im = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
lowThresh = 0.5*high_thresh
edged = cv2.Canny(blurred, 50, 200)
cv2.imwrite('temp3.jpg', edged)

text_gray = pytesseract.image_to_string(Image.open('temp1.jpg'),
                                        config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")

text_blurred = pytesseract.image_to_string(Image.open('temp2.jpg'),
                                           config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")
text_canny = pytesseract.image_to_string(Image.open('temp3.jpg'),
                                         config="-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ -psm 6")
print('Gray Scale ' + text_gray +"\n With Gaussian Blur: " +text_blurred +'\n After Canny Edge Detection: ' + text_canny)


#print(pytesseract.image_to_string(Image.open('test.png')))
#print(pytesseract.image_to_string(Image.open('Phthalo Green Text.jpg')))


