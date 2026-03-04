import cv2
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cv2.CAP_DSHOW helps to force-open camera (DirectShow backend)
print("Camera open:", camera.isOpened())

wid = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
hei = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

codec = cv2.VideoWriter_fourcc(*'XVID')
recorder = cv2.VideoWriter("myVideo.avi", codec, 20, (wid, hei))

while True:
    success, image = camera.read()
    if not success:
        print("Something went wrong")
        break

    recorder.write(image)
    cv2.imshow("Video", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        #pressing q quits the webcam
        print("Quitting")
        break

camera.release()
cv2.destroyAllWindows()


