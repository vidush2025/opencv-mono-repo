import cv2
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cv2.CAP_DSHOW helps to force-open camera (DirectShow backend)
print(cap.isOpened())

while True:
    flag, frame = cap.read() #flag: boolean, fram: image
    if not flag:
        print("Could not read frame")
        break
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        #pressing q quits the webcam
        print("Quitting")
        break

cap.release()
cv2.destroyAllWindows()
