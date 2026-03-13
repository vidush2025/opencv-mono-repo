import cv2
import json
from pathlib import Path

from communication.java_sender import JavaGestureSender
from gestures.hand_position import HandPositionDetector
from gestures.pinch_detector import PinchDetector
from tracking.camera import CameraStream
from tracking.hand_tracker import HandTracker
from utils.math_utils import significant_change


def load_thresholds():
	default_pinch = 2
	default_hand_height = 2

	try:
		config_path = Path(__file__).resolve().parents[1] / "config.json"
		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		thresholds = config.get("thresholds", {})
		pinch_threshold = int(thresholds.get("pinchChange", default_pinch))
		hand_height_threshold = int(thresholds.get("handHeightChange", default_hand_height))

		return max(0, pinch_threshold), max(0, hand_height_threshold)
	except Exception:
		return default_pinch, default_hand_height


def draw_status(frame, sender_connected, control_enabled, pinch_reading, hand_reading):
	pinch_status = "active" if pinch_reading.active else "idle"
	connection_status = "connected" if sender_connected else "waiting"
	control_status = "enabled" if control_enabled else "disabled"

	cv2.putText(
		frame,
		f"socket: {connection_status}",
		(20, 30),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.7,
		(0, 255, 0) if sender_connected else (0, 165, 255),
		2,
	)
	cv2.putText(
		frame,
		f"control: {control_status}",
		(20, 60),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.7,
		(255, 255, 255),
		2,
	)
	cv2.putText(
		frame,
		f"pinch: {pinch_reading.midi_value} ({pinch_status})",
		(20, 90),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.7,
		(255, 255, 255),
		2,
	)
	cv2.putText(
		frame,
		f"hand height: {hand_reading.midi_value}",
		(20, 120),
		cv2.FONT_HERSHEY_SIMPLEX,
		0.7,
		(255, 255, 255),
		2,
	)

	cv2.rectangle(
		frame,
		(40, hand_reading.control_top),
		(70, hand_reading.control_bottom),
		(255, 255, 255),
		2,
	)
	fill_position = int(
		hand_reading.control_bottom
		- ((hand_reading.midi_value / 127.0) * (hand_reading.control_bottom - hand_reading.control_top))
	)
	cv2.rectangle(
		frame,
		(40, fill_position),
		(70, hand_reading.control_bottom),
		(0, 255, 0),
		cv2.FILLED,
	)


def main():
	pinch_change_threshold, hand_height_change_threshold = load_thresholds()

	camera = CameraStream()
	hand_tracker = HandTracker(max_num_hands=1)
	pinch_detector = PinchDetector()
	hand_position_detector = HandPositionDetector()
	sender = JavaGestureSender()

	last_pinch_value = None
	last_hand_height_value = None
	last_pinch_active = False
	control_enabled = False

	try:
		while True:
			frame = camera.read()
			frame, detected_hands = hand_tracker.process(frame, draw=True)

			if detected_hands:
				primary_hand = detected_hands[0]
				landmarks = primary_hand["landmarks"]

				pinch_reading = pinch_detector.detect(landmarks)
				hand_reading = hand_position_detector.detect(landmarks, frame.shape[0])

				if hand_reading.toggle_triggered:
					control_enabled = not control_enabled
					sender.send_gesture("toggle", 127 if control_enabled else 0, control_enabled)

				if pinch_reading.active != last_pinch_active:
					sender.send_gesture("pinch", pinch_reading.midi_value, pinch_reading.active)
					last_pinch_active = pinch_reading.active
					last_pinch_value = pinch_reading.midi_value

				if control_enabled and pinch_reading.active and significant_change(
					last_pinch_value,
					pinch_reading.midi_value,
					pinch_change_threshold,
				):
					sender.send_gesture("pinch", pinch_reading.midi_value, True)
					last_pinch_value = pinch_reading.midi_value

				if control_enabled and significant_change(
					last_hand_height_value,
					hand_reading.midi_value,
					hand_height_change_threshold,
				):
					sender.send_gesture("hand_height", hand_reading.midi_value, True)
					last_hand_height_value = hand_reading.midi_value

				draw_status(
					frame,
					sender.is_connected,
					control_enabled,
					pinch_reading,
					hand_reading,
				)
			else:
				cv2.putText(
					frame,
					"Show one hand to start",
					(20, 40),
					cv2.FONT_HERSHEY_SIMPLEX,
					0.8,
					(255, 255, 255),
					2,
				)

				if last_pinch_active:
					sender.send_gesture("pinch", 0, False)
					last_pinch_active = False
					last_pinch_value = None

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
