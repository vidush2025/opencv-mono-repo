"""
1. cv2.bitwise_and(img1, img2)
2. cv2.bitwise_or(img1, img2)
3. cv2.bitwise_not(img1)

"""

import cv2
import numpy as np

img1 = np.zeros((300, 300), dtype="uint8")
img2 = np.zeros((300, 300), dtype="uint8")

cv2.circle(img1, (150, 150), 100, 255, -1) #draw circle on img1

cv2.rectangle(img2, (100, 100), (250, 250), 255, -1) #draw rectangle on img2

bitwiseAnd = cv2.bitwise_and(img1, img2)
bitwiseOr = cv2.bitwise_or(img1, img2)
bitwiseNot = cv2.bitwise_not(img1)


cv2.imshow("Circle", img1)
cv2.imshow("Rectangle", img2)
cv2.imshow("Bit-AND", bitwiseAnd)
cv2.imshow("Bit-OR", bitwiseOr)
cv2.imshow("Bit-NOT", bitwiseNot)

cv2.waitKey(0)
cv2.destroyAllWindows()
