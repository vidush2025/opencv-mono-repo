from dataclasses import dataclass

from tracking import landmarks as hand_landmarks
from utils.math_utils import distance, normalize_distance_to_midi


@dataclass
class PinchReading:
	active: bool
	midi_value: int
	distance_px: float


class PinchDetector:
	def __init__(self, pinch_threshold=45, minimum_distance=20, maximum_distance=200):
		self.pinch_threshold = pinch_threshold
		self.minimum_distance = minimum_distance
		self.maximum_distance = maximum_distance

	def detect(self, landmarks):
		thumb_tip = landmarks[hand_landmarks.THUMB_TIP]
		index_tip = landmarks[hand_landmarks.INDEX_FINGER_TIP]
		pinch_distance = distance(thumb_tip, index_tip)

		return PinchReading(
			active=pinch_distance <= self.pinch_threshold,
			midi_value=normalize_distance_to_midi(
				pinch_distance,
				self.minimum_distance,
				self.maximum_distance,
			),
			distance_px=pinch_distance,
		)
