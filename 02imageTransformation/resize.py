import cv2
image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is None:
    print("Image not found.")
else:
    print("Image loaded.")

    #variable = cv2.resize(src, (width, height))
    resized = cv2.resize(image, (300, 300)) 

    cv2.imshow("Original Goldberg",image)
    cv2.imshow("Shorter Golderg",resized)

    cv2.imwrite("Resized.jpg", resized)
    print("image resized")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
