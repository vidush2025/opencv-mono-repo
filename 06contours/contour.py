import cv2

img = cv2.imread("testmedia\joeGoldberg.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

_, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

cv2.drawContours(img, contours, -1, (0, 255, 0), 4)

for contour in contours:

    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

    corners = len(approx)

    if corners == 3:
        shape = "triangle"
    elif corners == 4:
        shape = "rectangle"
    elif corners == 5:
        shape = "pentagon"
    else:
        shape = "unknown"

    cv2.drawContours(img, [approx], 0, (0, 255, 0), 3)

    x = approx.ravel()[0]
    y = approx.ravel()[1] - 10

    cv2.putText(img, shape, (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)

cv2.imshow("Contours", img)
cv2.waitKey(0)
cv2.destroyAllWindows()