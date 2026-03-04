import cv2
image = cv2.imread("testmedia\joeGoldberg.jpg")

blurred = cv2.medianBlur(image, 21)
# blurred = cv2.medianBlur(src_image, kernel_size)
# kernel_size MUST be odd

cv2.imshow("Joe Goldberg:", image)
cv2.imshow("Joe Blurred-berg:", blurred)

cv2.waitKey(0)
cv2.destroyAllWindows()
