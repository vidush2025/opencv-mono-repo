import cv2
import numpy as np

image = cv2.imread("testmedia\joeGoldberg.jpg")

kernel = np.array([
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0],
])
# above is the kernel matrix
# a kernel is a 3x3 matrix used the modify the current
# pixels in the image so that we can manipulate the appearance of a certain pixel
# by increasing/decreasing the neighbours

# here, we increase the value of middle pixel of the 3x3 matrix
# by +5, and decrease its horizontal and vertical neighbours by -1

# we keep the corners same so that the middle pixel just appears sharper 

sharpened = cv2.filter2D(image, -1, kernel)
# sharpened = cv2.filter2D(image, depth, kernel_matrix)

cv2.imshow("Joe Goldberg:", image)
cv2.imshow("Joe Sharp-berg:", sharpened)

cv2.waitKey(0)
cv2.destroyAllWindows()
