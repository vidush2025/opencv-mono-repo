import cv2

image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is not None:
    print("Image loaded.")
    cv2.putText(image, "JOE GOLDBERG", (200, 400),
                cv2.FONT_HERSHEY_PLAIN, 3.0, (0,0,255), thickness=2)
    # cv2.putText(image, text, (x, y), cv2.FONT_HERSHEY_PLAIN,textSize, color, thickness)

    cv2.imshow("Text-Berg", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Could not load image.")