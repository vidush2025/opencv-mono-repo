import cv2

image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is not None:
    print("Image loaded.")
    p1 = (50,50)
    p2 = (500,500)

    color = (0,0,255) #red
    thickness = 4

    cv2.rectangle(image, p1, p2, color, thickness)
    cv2.imshow("Rectangoldberg", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not load image.")