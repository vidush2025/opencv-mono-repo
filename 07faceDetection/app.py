import cv2
faceCascade = cv2.CascadeClassifier(
    "07faceDetection/resources/haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    faces = faceCascade.detectMultiScale(gray, 1.1, 8)

    """
    detectMultiScale(...): detect and scan objects (here faces)

    1.1: scale factor/zoom level to check while finding object(1.1 meins 10% smaller every iteration)

    5: minimum neighbours, here 5 means we will test 5 times for strict checking for correct output
    """

    for(x, y, wid, hei) in faces:
        cv2.rectangle(frame, (x,y), (x + wid, y + hei), (0, 255, 0), 2) #draw the rectangle around the face


    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


