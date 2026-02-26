import cv2
image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is None:
    print("Image not found.")
else:
    len, bre, col = image.shape #length, bredth, colour channels
    print("Image Loaded")
    print("Length:", len, "Breadth:", bre)

    #variable = cv2.image[yStart : yEnd, xStart : xEnd]
    cropped = image[10 : 500, 550 : 1000]
    cv2.imshow("Joe Goldberg", image)
    cv2.imshow("Sliced Goldberg", cropped)

    cv2.waitKey(0)
    cv2.destroyAllWindows()