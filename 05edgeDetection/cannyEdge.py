import cv2

# For cannyedge detection, image MUST BE grayScaled
image = cv2.imread("testmedia\joeGoldberg.jpg", cv2.IMREAD_GRAYSCALE)

threshold1 = 50
threshold2 = 250

edged = cv2.Canny(image, threshold1, threshold2)
cv2.imshow("Goldberg", image)
cv2.imshow("Edgeberg", edged)

cv2.waitKey(0)
cv2.destroyAllWindows()