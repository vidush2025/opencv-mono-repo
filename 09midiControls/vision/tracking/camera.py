import cv2


class CameraStream:
	def __init__(self, camera_index=0):
		api_preference = cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else 0
		self.capture = cv2.VideoCapture(camera_index, api_preference)

		if not self.capture.isOpened():
			self.capture.release()
			self.capture = cv2.VideoCapture(camera_index)

		if not self.capture.isOpened():
			raise RuntimeError("Unable to open webcam")

	def read(self):
		ok, frame = self.capture.read()
		if not ok:
			raise RuntimeError("Unable to read frame from webcam")

		return frame

	def release(self):
		if self.capture is not None:
			self.capture.release()
