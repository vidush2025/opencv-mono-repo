from dataclasses import dataclass

from tracking import landmarks as hand_landmarks
from utils.math_utils import normalize_vertical_to_midi


@dataclass
class HandPositionReading:
	midi_value: int
	control_y: int
	control_top: int
	control_bottom: int
	toggle_triggered: bool
	two_fingers_up: bool


class HandPositionDetector:
	def __init__(self, top_ratio=0.2, bottom_ratio=0.8):
		self.top_ratio = top_ratio
		self.bottom_ratio = bottom_ratio
		self._previous_two_fingers_up = False

	def detect(self, landmarks, frame_height):
		control_top = int(frame_height * self.top_ratio)
		control_bottom = int(frame_height * self.bottom_ratio)

		index_tip = landmarks[hand_landmarks.INDEX_FINGER_TIP]
		index_pip = landmarks[hand_landmarks.INDEX_FINGER_PIP]
		middle_tip = landmarks[hand_landmarks.MIDDLE_FINGER_TIP]
		middle_pip = landmarks[hand_landmarks.MIDDLE_FINGER_PIP]

		index_up = index_tip[1] < index_pip[1]
		middle_up = middle_tip[1] < middle_pip[1]
		two_fingers_up = index_up and middle_up

		toggle_triggered = two_fingers_up and not self._previous_two_fingers_up
		self._previous_two_fingers_up = two_fingers_up

		return HandPositionReading(
			midi_value=normalize_vertical_to_midi(index_tip[1], control_top, control_bottom),
			control_y=index_tip[1],
			control_top=control_top,
			control_bottom=control_bottom,
			toggle_triggered=toggle_triggered,
			two_fingers_up=two_fingers_up,
		)
