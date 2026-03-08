import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
# mp.num_hands = 2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

prev_gesture = None

while True:
    ret, frame = cap.read()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            lm_list = []

            for id, lm in enumerate(hand_landmarks.landmark):

                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                lm_list.append((cx, cy))

                cv2.putText(frame, str(id), (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            if len(lm_list) != 0:

                index_up = lm_list[8][1] < lm_list[6][1]
                middle_up = lm_list[12][1] < lm_list[10][1]
                ring_up = lm_list[16][1] < lm_list[14][1]
                little_up = lm_list[20][1] < lm_list[18][1]


                gesture = "NONE"

                if index_up and middle_up:
                    gesture = "TWO_FINGERS"
                elif index_up:
                    gesture = "1 number bencho"
                elif middle_up:
                    gesture = "FUCK YOU NIGGA"
                elif ring_up:
                    gesture = "This is unnecessary"
                elif little_up:
                    gesture = "KATTIIIIIIII"


                if gesture != prev_gesture:
                    print("Gesture:", gesture)
                    prev_gesture = gesture

    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
