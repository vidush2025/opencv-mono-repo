import json
import socket
import time


class JavaGestureSender:
	def __init__(self, host="127.0.0.1", port=8888, reconnect_interval_seconds=2.0):
		self.host = host
		self.port = port
		self.reconnect_interval_seconds = reconnect_interval_seconds
		self._socket = None
		self._last_attempt_time = 0.0

	@property
	def is_connected(self):
		return self._socket is not None

	def connect(self):
		now = time.time()
		if self._socket is not None:
			return True

		if now - self._last_attempt_time < self.reconnect_interval_seconds:
			return False

		self._last_attempt_time = now

		try:
			connection = socket.create_connection((self.host, self.port), timeout=2.0)
			connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			self._socket = connection
			return True
		except OSError:
			self._socket = None
			return False

	def send_gesture(self, gesture_name, value, active, metadata=None):
		if self._socket is None and not self.connect():
			return False

		payload = {
			"gesture": gesture_name,
			"value": int(value),
			"active": bool(active),
		}

		if metadata:
			payload["metadata"] = metadata

		try:
			message = json.dumps(payload, separators=(",", ":")) + "\n"
			self._socket.sendall(message.encode("utf-8"))
			return True
		except OSError:
			self.close()
			return False

	def close(self):
		if self._socket is not None:
			try:
				self._socket.close()
			finally:
				self._socket = None
