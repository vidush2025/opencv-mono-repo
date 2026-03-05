import cv2

image = cv2.imread("testmedia\joeGoldberg.jpg", cv2.IMREAD_GRAYSCALE)

flag, thresholded = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY)  

cv2.imshow("Goldberg", image)
cv2.imshow("Edgeberg", thresholded)

cv2.waitKey(0)
cv2.destroyAllWindows()