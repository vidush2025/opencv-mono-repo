import json
import socket
import time
import os
from pathlib import Path

def _load_config_defaults():
    # config.json is at project root: ../.. from vision/communication
    try:
        cfg_path = Path(__file__).resolve().parents[2] / "config.json"
        if cfg_path.exists():
            with cfg_path.open("r", encoding="utf-8") as f:
                cfg = json.load(f)
            socket_cfg = cfg.get("socket", {})
            host = socket_cfg.get("host", "127.0.0.1")
            port = int(socket_cfg.get("port", 8888))
            reconnect = float(socket_cfg.get("reconnectIntervalSeconds", 2.0))
            return host, port, reconnect
    except Exception:
        pass
    return "127.0.0.1", 8888, 2.0

class JavaGestureSender:
    def __init__(self, host=None, port=None, reconnect_interval_seconds=None):
        cfg_host, cfg_port, cfg_reconnect = _load_config_defaults()
        self.host = cfg_host if host is None else host
        self.port = cfg_port if port is None else port
        self.reconnect_interval_seconds = cfg_reconnect if reconnect_interval_seconds is None else reconnect_interval_seconds

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