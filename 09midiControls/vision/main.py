import cv2
import json
from pathlib import Path

from communication.java_sender import JavaGestureSender
from tracking.camera import CameraStream
from tracking.hand_tracker import HandTracker
from tracking import landmarks as hand_landmarks
from utils.math_utils import significant_change
from utils.math_utils import normalize_vertical_to_midi


def load_thresholds():
	default_right_move = 2

	try:
		config_path = Path(__file__).resolve().parents[1] / "config.json"
		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		thresholds = config.get("thresholds", {})
		right_move_threshold = int(thresholds.get("handHeightChange", default_right_move))

		return max(0, right_move_threshold)
	except Exception:
		return default_right_move


def _classify_hands(detected_hands):
	left_hand = None
	right_hand = None
	unknown_hands = []

	for hand in detected_hands:
		handedness = hand.get("handedness", "Unknown")
		if handedness == "Left" and left_hand is None:
			left_hand = hand
		elif handedness == "Right" and right_hand is None:
			right_hand = hand
		else:
			unknown_hands.append(hand)

	if (left_hand is None or right_hand is None) and unknown_hands:
		unknown_hands.sort(key=lambda item: item["landmarks"][hand_landmarks.WRIST][0])
		if left_hand is None:
			left_hand = unknown_hands.pop(0)
		if right_hand is None and unknown_hands:
			right_hand = unknown_hands.pop(-1)

	return left_hand, right_hand


def _count_fingers(landmarks, handedness):
    thumb_tip = landmarks[hand_landmarks.THUMB_TIP]
    thumb_mcp = landmarks[hand_landmarks.THUMB_MCP]

    # Distance from thumb MCP to tip = how extended the thumb is
    dx = thumb_tip[0] - thumb_mcp[0]
    dy = thumb_tip[1] - thumb_mcp[1]
    thumb_extension = (dx**2 + dy**2)**0.5
    
    # Thumb is extended if distance is significant
    thumb_up = thumb_extension > 25  # Adjust this threshold as needed

    finger_pairs = [
        (hand_landmarks.INDEX_FINGER_TIP, hand_landmarks.INDEX_FINGER_PIP),
        (hand_landmarks.MIDDLE_FINGER_TIP, hand_landmarks.MIDDLE_FINGER_PIP),
        (hand_landmarks.RING_FINGER_TIP, hand_landmarks.RING_FINGER_PIP),
        (hand_landmarks.PINKY_TIP, hand_landmarks.PINKY_PIP),
    ]

    fingers_up = 1 if thumb_up else 0
    for tip_index, pip_index in finger_pairs:
        if landmarks[tip_index][1] < landmarks[pip_index][1]:
            fingers_up += 1

    return max(0, min(5, fingers_up))
def draw_status(frame, sender_connected, left_count, right_count, right_value):
    connection_status = "connected" if sender_connected else "waiting"
    left_status = "-" if left_count is None else str(left_count)
    right_status = "-" if right_count is None else str(right_count)
    right_midi = "-" if right_value is None else str(right_value)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.45
    thickness = 1
    y_start = 25
    y_step = 22

    cv2.putText(
        frame,
        f"socket: {connection_status}",
        (10, y_start),
        font,
        font_scale,
        (0, 255, 0) if sender_connected else (0, 165, 255),
        thickness,
    )
    cv2.putText(
        frame,
        f"left: {left_status}",
        (10, y_start + y_step),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
    )
    cv2.putText(
        frame,
        f"right: {right_status}",
        (10, y_start + y_step * 2),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
    )
    cv2.putText(
        frame,
        f"MIDI: {right_midi}",
        (10, y_start + y_step * 3),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
    )

def main():
	right_move_change_threshold = load_thresholds()

	camera = CameraStream()
	hand_tracker = HandTracker(max_num_hands=2)
	sender = JavaGestureSender()

	last_left_count = None
	last_right_count = None
	last_right_move_value = None
	both_fists_active = False
	control_top_ratio = 0.2
	control_bottom_ratio = 0.8

	try:
		while True:
			frame = camera.read()
			frame = cv2.flip(frame, 1) 
			frame, detected_hands = hand_tracker.process(frame, draw=True)
			left_count = None
			right_count = None
			right_move_value = None

			if detected_hands:
				left_hand, right_hand = _classify_hands(detected_hands)

				if left_hand is not None:
					left_count = _count_fingers(left_hand["landmarks"], left_hand.get("handedness", "Left"))
					if left_count != last_left_count:
						sender.send_event("LEFT", "FIST" if left_count == 0 else str(left_count))
						last_left_count = left_count
				else:
					last_left_count = None

				if right_hand is not None:
					right_count = _count_fingers(right_hand["landmarks"], right_hand.get("handedness", "Right"))
					if right_count != last_right_count:
						sender.send_event("RIGHT", str(right_count))
						last_right_count = right_count

					frame_height = frame.shape[0]
					control_top = int(frame_height * control_top_ratio)
					control_bottom = int(frame_height * control_bottom_ratio)
					index_tip_y = right_hand["landmarks"][hand_landmarks.INDEX_FINGER_TIP][1]
					right_move_value = normalize_vertical_to_midi(index_tip_y, control_top, control_bottom)

					if significant_change(last_right_move_value, right_move_value, right_move_change_threshold):
						normalized = right_move_value / 127.0
						sender.send_event("RIGHT_MOVE", f"{normalized:.3f}")
						last_right_move_value = right_move_value
				else:
					last_right_count = None
					last_right_move_value = None

				if left_count == 0 and right_count == 0:
					if not both_fists_active:
						sender.send_event("BOTH", "FIST")
						both_fists_active = True
				elif both_fists_active and left_count is not None and right_count is not None and left_count > 0 and right_count > 0:
					sender.send_event("BOTH", "OPEN")
					both_fists_active = False
			else:
				cv2.putText(
					frame,
					"Show left and right hand",
					(20, 40),
					cv2.FONT_HERSHEY_SIMPLEX,
					0.8,
					(255, 255, 255),
					2,
				)
				last_left_count = None
				last_right_count = None
				last_right_move_value = None

			draw_status(frame, sender.is_connected, left_count, right_count, right_move_value)

			cv2.imshow("AirWaveMini Vision", frame)
			key = cv2.waitKey(1) & 0xFF

			if key == ord("q"):
				break

			if key == ord("r"):
				sender.close()
				sender.connect()

		cv2.destroyAllWindows()
	finally:
		sender.close()
		hand_tracker.close()
		camera.release()
		cv2.destroyAllWindows()


if __name__ == "__main__":
	main()
