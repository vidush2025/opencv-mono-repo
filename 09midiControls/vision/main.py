import cv2
import json
from pathlib import Path

from communication.java_sender import JavaGestureSender
from tracking.camera import CameraStream
from tracking.hand_tracker import HandTracker
from tracking import landmarks as hand_landmarks
from utils.math_utils import significant_change
from utils.math_utils import normalize_vertical_to_midi


MAX_CC_VALUE = int(round(127 * 0.8))


class StableValue:
	def __init__(self, frames_required=3):
		self.frames_required = max(1, int(frames_required))
		self._stable = None
		self._candidate = None
		self._count = 0

	def update(self, value):
		if value is None:
			self._candidate = None
			self._count = 0
			return self._stable, False

		if value != self._candidate:
			self._candidate = value
			self._count = 1
		else:
			self._count += 1

		if self._count >= self.frames_required and self._stable != self._candidate:
			self._stable = self._candidate
			return self._stable, True

		return self._stable, False

	def clear(self):
		self._stable = None
		self._candidate = None
		self._count = 0


class EmaSmoother:
	def __init__(self, alpha=0.35):
		self.alpha = float(alpha)
		self._value = None

	def update(self, value):
		if self._value is None:
			self._value = float(value)
		else:
			self._value = (self.alpha * float(value)) + ((1.0 - self.alpha) * self._value)
		return int(round(self._value))

	def clear(self):
		self._value = None


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


def _scale_to_cc_cap(value):
	value = max(0, min(127, int(value)))
	return int(round((value / 127.0) * MAX_CC_VALUE))


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


def _distance(point_a, point_b):
	delta_x = float(point_a[0] - point_b[0])
	delta_y = float(point_a[1] - point_b[1])
	return (delta_x * delta_x + delta_y * delta_y) ** 0.5


def _is_thumb_up(landmarks, handedness):
	thumb_tip = landmarks[hand_landmarks.THUMB_TIP]
	thumb_ip = landmarks[hand_landmarks.THUMB_IP]
	index_mcp = landmarks[hand_landmarks.INDEX_FINGER_MCP]

	return _distance(thumb_tip, index_mcp) > (_distance(thumb_ip, index_mcp) + 8.0)


def _is_fist(landmarks):
	wrist = landmarks[hand_landmarks.WRIST]
	middle_mcp = landmarks[hand_landmarks.MIDDLE_FINGER_MCP]
	index_mcp = landmarks[hand_landmarks.INDEX_FINGER_MCP]
	thumb_tip = landmarks[hand_landmarks.THUMB_TIP]

	palm_size = max(1.0, _distance(wrist, middle_mcp))
	finger_tips = [
		hand_landmarks.INDEX_FINGER_TIP,
		hand_landmarks.MIDDLE_FINGER_TIP,
		hand_landmarks.RING_FINGER_TIP,
		hand_landmarks.PINKY_TIP,
	]
	finger_mcps = [
		hand_landmarks.INDEX_FINGER_MCP,
		hand_landmarks.MIDDLE_FINGER_MCP,
		hand_landmarks.RING_FINGER_MCP,
		hand_landmarks.PINKY_MCP,
	]

	folded_fingers = 0
	for tip_index, mcp_index in zip(finger_tips, finger_mcps):
		tip_distance = _distance(landmarks[tip_index], wrist)
		mcp_distance = _distance(landmarks[mcp_index], wrist)
		if tip_distance < (mcp_distance + (0.25 * palm_size)):
			folded_fingers += 1

	thumb_folded = _distance(thumb_tip, index_mcp) < (0.9 * palm_size)
	return folded_fingers >= 4 and thumb_folded


def _count_fingers(landmarks, handedness):
	finger_pairs = [
		(hand_landmarks.INDEX_FINGER_TIP, hand_landmarks.INDEX_FINGER_PIP),
		(hand_landmarks.MIDDLE_FINGER_TIP, hand_landmarks.MIDDLE_FINGER_PIP),
		(hand_landmarks.RING_FINGER_TIP, hand_landmarks.RING_FINGER_PIP),
		(hand_landmarks.PINKY_TIP, hand_landmarks.PINKY_PIP),
	]

	fingers_up = 1 if _is_thumb_up(landmarks, handedness) else 0
	for tip_index, pip_index in finger_pairs:
		if landmarks[tip_index][1] < (landmarks[pip_index][1] - 8):
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
	hand_tracker = HandTracker(
		max_num_hands=2,
		min_detection_confidence=0.75,
		min_tracking_confidence=0.75,
	)
	sender = JavaGestureSender()

	last_left_count = None
	last_right_fist = None
	last_right_move_value = None
	both_state = None
	control_top_ratio = 0.2
	control_bottom_ratio = 0.8
	left_count_stable = StableValue(frames_required=3)
	right_count_stable = StableValue(frames_required=3)
	right_fist_stable = StableValue(frames_required=4)
	both_state_stable = StableValue(frames_required=3)
	right_move_smoother = EmaSmoother(alpha=0.35)

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
					raw_left_count = _count_fingers(left_hand["landmarks"], left_hand.get("handedness", "Left"))
					left_count, left_changed = left_count_stable.update(raw_left_count)
					if left_count is not None and left_changed and left_count != last_left_count:
						sender.send_event("LEFT", "FIST" if left_count == 0 else str(left_count))
						last_left_count = left_count
				else:
					left_count_stable.clear()
					last_left_count = None

				if right_hand is not None:
					raw_right_count = _count_fingers(right_hand["landmarks"], right_hand.get("handedness", "Right"))
					right_count, _ = right_count_stable.update(raw_right_count)

					raw_right_fist = _is_fist(right_hand["landmarks"])
					right_fist, right_fist_changed = right_fist_stable.update(raw_right_fist)
					if right_fist is not None and right_fist_changed and right_fist != last_right_fist:
						sender.send_event("RIGHT", "FIST" if right_fist else "OPEN")
						last_right_fist = right_fist

					frame_height = frame.shape[0]
					control_top = int(frame_height * control_top_ratio)
					control_bottom = int(frame_height * control_bottom_ratio)
					index_tip_y = right_hand["landmarks"][hand_landmarks.INDEX_FINGER_TIP][1]
					middle_tip_y = right_hand["landmarks"][hand_landmarks.MIDDLE_FINGER_TIP][1]
					control_y = int(round((index_tip_y + middle_tip_y) / 2.0))
					raw_right_move_value = normalize_vertical_to_midi(control_y, control_top, control_bottom)
					smoothed_value = right_move_smoother.update(raw_right_move_value)
					right_move_value = _scale_to_cc_cap(smoothed_value)

					if significant_change(last_right_move_value, right_move_value, right_move_change_threshold):
						sender.send_event("RIGHT_MOVE", str(right_move_value))
						last_right_move_value = right_move_value
				else:
					right_count_stable.clear()
					right_fist_stable.clear()
					right_move_smoother.clear()
					last_right_move_value = None
					if last_right_fist is not None:
						sender.send_event("RIGHT", "OPEN")
						last_right_fist = None

				if left_count is not None and right_count is not None:
					raw_both_state = None
					if left_count == 0 and right_count == 0:
						raw_both_state = "FIST"
					elif left_count >= 4 and right_count >= 4:
						raw_both_state = "OPEN"

					stable_both_state, both_changed = both_state_stable.update(raw_both_state)
					if stable_both_state is not None and both_changed and stable_both_state != both_state:
						sender.send_event("BOTH", stable_both_state)
						both_state = stable_both_state
				else:
					both_state_stable.clear()
					both_state = None
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
				if last_right_fist is not None:
					sender.send_event("RIGHT", "OPEN")
				last_left_count = None
				last_right_fist = None
				last_right_move_value = None
				left_count_stable.clear()
				right_count_stable.clear()
				right_fist_stable.clear()
				both_state_stable.clear()
				both_state = None
				right_move_smoother.clear()

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
