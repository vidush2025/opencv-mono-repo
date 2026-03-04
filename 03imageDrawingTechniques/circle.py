import cv2

image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is not None:
    print("Image loaded.")
    center = (200, 500)
    rad = 100

    color = (0,0,255)

    cv2. circle(image, center, rad,color, -1)
    cv2.imshow("CircleBerg", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not load image.")