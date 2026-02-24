import cv2;
image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is None:
    print("Image not found")
else:
    print("Image loaded successfully")
    cv2.imshow("Joe Goldberg", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()