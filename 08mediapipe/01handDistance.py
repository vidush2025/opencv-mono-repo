import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
# mp.num_hands = 2


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

prev_value = -1
threshold = 3

while True: 
    ret, frame = cap.read()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #convert from cv2's BGR to RGB 
    results = hands.process(rgb_frame)

    x1, y1 = 0, 0
    x2, y2 = 0, 0

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h) 

                if id == 4:
                    #thumb tip
                    x1, y1 = cx, cy
                if id == 8:
                    x2, y2 = cx, cy
                
                cv2.putText(frame, str(id), (cx, cy),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
            

            cv2.circle(frame, (x1, y1), 8, (255,0,255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 8, (255,0,255), cv2.FILLED)
            
            cv2.line(frame, (x1,y1), (x2,y2), (255,0,255), 2)
            distance = np.hypot(x2-x1, y2-y1)
            minDist = 20
            maxDist = 200

            #normalizing the distance by linear interpolation
            # [0-127] are the only valid inputs for a midi
            midi_value = int(np.interp(distance, [minDist, maxDist], [0, 127]))
            
            #compressing the value to stay between [0-127]
            midi_value = max(0, min(127, midi_value))

            # print only if significant change
            if abs(midi_value - prev_value) > threshold:
                print("distance:", distance, "midi_value:", midi_value)
                prev_value = midi_value

    cv2.imshow("Webcam", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
