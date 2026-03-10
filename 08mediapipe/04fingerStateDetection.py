import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


def get_finger_states(lm_list):

    # check x-axis for thumb
    thumb = lm_list[4][0] > lm_list[3][0] #this is for right hand only
    
    # check y-axis for others
    index = lm_list[8][1] < lm_list[6][1]
    middle = lm_list[12][1] < lm_list[10][1]
    ring = lm_list[16][1] < lm_list[14][1]
    pinky = lm_list[20][1] < lm_list[18][1]

    return [thumb, index,middle,ring,pinky]


while True: 
    ret, frame = cap.read()
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            lm_list = []

            for id, lm in enumerate(hand_landmarks.landmark):

                cx = int(lm.x * w)
                cy = int(lm.y * h)

                lm_list.append((cx, cy))

                cv2.putText(frame, str(id), (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
                
            state = get_finger_states(lm_list)
            print(state)
                

    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
