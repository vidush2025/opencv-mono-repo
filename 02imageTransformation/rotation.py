import cv2;
image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is None:
    print("Image not found")
else:
    (hei, wid) = image.shape[:2]
    center = (wid // 2, hei // 2)
    
    # matrix = cv2.getRotationMatrix2D(center, angle, scale)
    matrix = cv2.getRotationMatrix2D(center, 90, 1.0)

    rotated = cv2.warpAffine(image, matrix, (wid, hei))
    cv2.imshow("Org Joe:", image)
    cv2.imshow("Rotated Joe:", rotated)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
