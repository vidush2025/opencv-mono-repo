#load image
#convert to grayScale
#show and save

import cv2;
image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is not None:
    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if grayImage is not None:
        print("Image converted to grayscale.")
        
        cv2.imshow("Gray Goldberg", grayImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        saved = cv2.imwrite("grayberg.jpg", grayImage)
        if saved:
            print("Gray Image saved successfully.")
        else:
            print("Failed to save grayscale-d image")
    else:
        print("Failed to convert to grayscale")

