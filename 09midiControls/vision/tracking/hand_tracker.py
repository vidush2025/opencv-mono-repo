import cv2
import mediapipe as mp


class HandTracker:
	def __init__(
		self,
		max_num_hands=1,
		min_detection_confidence=0.6,
		min_tracking_confidence=0.6,
	):
		self._mp_hands = mp.solutions.hands
		self._drawer = mp.solutions.drawing_utils
		self._hands = self._mp_hands.Hands(
			max_num_hands=max_num_hands,
			min_detection_confidence=min_detection_confidence,
			min_tracking_confidence=min_tracking_confidence,
		)

	def process(self, frame, draw=True):
		rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		results = self._hands.process(rgb_frame)
		frame_height, frame_width, _ = frame.shape
		detected_hands = []

		if not results.multi_hand_landmarks:
			return frame, detected_hands

		handedness_list = results.multi_handedness or []

		for index, hand_landmarks in enumerate(results.multi_hand_landmarks):
			if draw:
				self._drawer.draw_landmarks(
					frame,
					hand_landmarks,
					self._mp_hands.HAND_CONNECTIONS,
				)

			handedness_label = "Unknown"
			if index < len(handedness_list):
				handedness_label = handedness_list[index].classification[0].label

			landmarks = []
			for landmark in hand_landmarks.landmark:
				x_position = int(landmark.x * frame_width)
				y_position = int(landmark.y * frame_height)
				landmarks.append((x_position, y_position))

			detected_hands.append(
				{
					"landmarks": landmarks,
					"handedness": handedness_label,
				}
			)

		return frame, detected_hands

	def close(self):
		self._hands.close()
