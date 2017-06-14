import numpy
import pytesseract
import cv2
import textdetection
import os

image = cv2.imread("Van Dyke Brown.jpg")
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray_image, (5,5), 0)
high_thresh, thresh_im = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
lowThresh = 0.5*high_thresh

edged = cv2.Canny(blurred, 50, 200)

cv2.imshow("VDB", image)
cv2.imshow("VDB - gray", gray_image)
cv2.imshow("edges", edged)
path_to_edged = "edged.jpg"
cv2.imwrite(path_to_edged, edged)
cv2.imwrite(path_to_edged, blurred)


#textdetection.main(__name__, "C:\Users\Danny\PycharmProjects\BobRoss\edged.jpg")

cv2.waitKey(0)
cv2.destroyAllWindows()