import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# fader variables
fader_value = 0
prev_value = -1

fader_switch = False
prev_two_fingers = False

while True:

    ret, frame = cap.read()
    h, w, _ = frame.shape

    # usable screen range for control
    top = int(h * 0.2)
    bottom = int(h * 0.8)

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

            if len(lm_list) != 0:

                # finger states
                index_up = lm_list[8][1] < lm_list[6][1]
                middle_up = lm_list[12][1] < lm_list[10][1]

                two_fingers = index_up and middle_up

                # toggle for fader
                if two_fingers and not prev_two_fingers:
                    fader_switch = not fader_switch

                prev_two_fingers = two_fingers
                 
                if fader_switch:
                    # read index finger height
                    index_y = lm_list[8][1]

                    top = int(h * 0.2)
                    bottom = int(h * 0.8)

                    # clamp finger position inside control zone
                    index_y = max(top, min(bottom, index_y))

                    # map position → MIDI value
                    # fader_value = int(np.interp(index_y, [bottom, top], [0,127]))
                    fader_value = int(np.interp(index_y, [top, bottom], [127,0]))

                    # print only if value changed enough
                    if abs(fader_value - prev_value) > 2:
                        print("FADER:", fader_value)
                        prev_value = fader_value


    # fader UI
    if fader_switch:
        bar_height = int(np.interp(fader_value, [0,127], [bottom, top]))

        cv2.rectangle(frame, (50, top), (80, bottom), (255,255,255), 2)
        cv2.rectangle(frame, (50, bar_height), (80, bottom), (0,255,0), cv2.FILLED)

        cv2.putText(frame, str(fader_value), (40, bottom + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)


    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()