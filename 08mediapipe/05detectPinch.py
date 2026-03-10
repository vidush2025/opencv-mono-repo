import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

pinch_active = False
PINCH_THRESHOLD = 40

def get_pinch_distance(lm_list):
    x1, y1 = lm_list[4]   # thumb tip
    x2, y2 = lm_list[8]   # index tip

    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    return distance

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
                
            distance = get_pinch_distance(lm_list)

            if distance < PINCH_THRESHOLD:
                if not pinch_active:
                    pinch_active = True
                    print("Pinch Start")
                else:
                    print("Pinch Hold")
            else:
                if pinch_active:
                    pinch_active = False
                    print("Pinch Release")

                
            
            cv2.putText(frame, str(int(distance)), (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            
            cv2.line(frame, lm_list[4], lm_list[8], (255,0,0), 2)
                

    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
