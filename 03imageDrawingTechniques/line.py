import cv2

image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is not None:
    print("Image loaded.")
    p1 = (100, 200)
    p2 = (600, 200)

    color = (255, 0, 0) #blue
    thickness = 3
    cv2.line(image, p1, p2,color, thickness)

    cv2.imshow("Lined Goldberg:", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Image not found.")