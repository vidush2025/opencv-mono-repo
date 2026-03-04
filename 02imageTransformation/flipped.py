import cv2;
image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is None:
    print("Image not found")
else:
    vertical = cv2.flip(image, 0)
    horizontal = cv2.flip(image, 1)
    horizAndVer = cv2.flip(image, -1)
    
    cv2.imshow("Org Joe:", image)
    cv2.imshow("Vertical Joe:", vertical)
    cv2.imshow("Horizontal Joe:", horizontal)
    cv2.imshow("Nashedi Joe:", horizAndVer)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
