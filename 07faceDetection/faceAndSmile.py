import cv2

faceCascade = cv2.CascadeClassifier("07faceDetection/resources/haarcascade_frontalface_default.xml")
smileCascade = cv2.CascadeClassifier("07faceDetection/resources/haarcascade_smile.xml")
eyeCascade = cv2.CascadeClassifier("07faceDetection/resources/haarcascade_eye.xml")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    faces = faceCascade.detectMultiScale(gray, 1.1, 8)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)

    regionGray = gray[y:y+h, x:x+w]  
    regionColor = frame[y:y+h, x:x+w]  

    """
    look for smile and eyes in ONLY the face frame and NOT in the whole frame
    """
    eyes = eyeCascade.detectMultiScale(regionGray, 1.1, 10)

    if len(eyes) > 0:
        cv2.putText(frame, "Eyes Detected", (x, y-30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.6, (0, 0, 255), 2)

    smile = smileCascade.detectMultiScale(regionGray, 1.7, 20)

    if len(smile) > 0:
        cv2.putText(frame, "Smiling", (x, y-20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.6, (255, 0, 0), 2)

    
    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()