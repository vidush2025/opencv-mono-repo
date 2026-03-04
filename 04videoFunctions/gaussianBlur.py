import cv2
image = cv2.imread("testmedia\joeGoldberg.jpg")

blurred = cv2.GaussianBlur(image, (9, 9), 10)

# here (9,9) is kernel_size
# (3,3) = light blur
# (9,9) = strong blur
# (21,21) = super blur
# kernel_size MUST be odd

# here 10 is blur strenth
# can be any number >= 0


cv2.imshow("Joe Goldberg:", image)
cv2.imshow("Joe Blurred-berg:", blurred)

cv2.waitKey(0)
cv2.destroyAllWindows()