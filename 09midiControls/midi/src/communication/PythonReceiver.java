package communication;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PythonReceiver {
	private static final Pattern GESTURE_PATTERN = Pattern.compile("\\\"gesture\\\"\\s*:\\s*\\\"([^\\\"]+)\\\"");
	private static final Pattern VALUE_PATTERN = Pattern.compile("\\\"value\\\"\\s*:\\s*(-?\\d+)");
	private static final Pattern ACTIVE_PATTERN = Pattern.compile("\\\"active\\\"\\s*:\\s*(true|false)");

	private final int port;
	private final GestureListener listener;
	private volatile boolean running;
	private ServerSocket serverSocket;

	public PythonReceiver(int port, GestureListener listener) {
		this.port = port;
		this.listener = listener;
	}

	public void start() throws IOException {
		running = true;
		serverSocket = new ServerSocket(port);
		System.out.println("Listening for Python gesture data on port " + port);

		while (running) {
			try (Socket clientSocket = serverSocket.accept();
				 BufferedReader reader = new BufferedReader(
					 new InputStreamReader(clientSocket.getInputStream(), StandardCharsets.UTF_8))) {

				System.out.println("Python vision client connected: " + clientSocket.getRemoteSocketAddress());
				String line;
				while (running && (line = reader.readLine()) != null) {
					GestureMessage message = parseMessage(line);
					if (message != null) {
						listener.onGesture(message);
					}
				}
				System.out.println("Python vision client disconnected");
			} catch (IOException exception) {
				if (running) {
					System.out.println("Communication error: " + exception.getMessage());
				}
			}
		}
	}

	public void stop() {
		running = false;
		if (serverSocket != null && !serverSocket.isClosed()) {
			try {
				serverSocket.close();
			} catch (IOException ignored) {
			}
		}
	}

	private GestureMessage parseMessage(String rawMessage) {
		GestureMessage eventMessage = parseEventMessage(rawMessage);
		if (eventMessage != null) {
			return eventMessage;
		}

		String gesture = extractString(rawMessage, GESTURE_PATTERN);
		Integer value = extractInteger(rawMessage, VALUE_PATTERN);
		Boolean active = extractBoolean(rawMessage, ACTIVE_PATTERN);

		if (gesture == null || value == null || active == null) {
			System.out.println("Skipping malformed message: " + rawMessage);
			return null;
		}

		return new GestureMessage(gesture, value.intValue(), active.booleanValue());
	}

	private GestureMessage parseEventMessage(String rawMessage) {
		if (rawMessage == null) {
			return null;
		}

		String message = rawMessage.trim();
		if (message.isEmpty() || message.startsWith("{")) {
			return null;
		}

		int separatorIndex = message.indexOf(':');
		if (separatorIndex <= 0 || separatorIndex >= message.length() - 1) {
			return null;
		}

		String eventName = message.substring(0, separatorIndex).trim().toUpperCase(Locale.ROOT);
		String eventValue = message.substring(separatorIndex + 1).trim();

		if ("LEFT".equals(eventName)) {
			if ("FIST".equalsIgnoreCase(eventValue)) {
				return new GestureMessage("LEFT", 0, true);
			}
			Integer count = parseIntegerSafe(eventValue);
			if (count != null) {
				return new GestureMessage("LEFT", clamp(count.intValue(), 0, 5), true);
			}
			return null;
		}

		if ("RIGHT".equals(eventName)) {
			Integer count = parseIntegerSafe(eventValue);
			if (count != null) {
				return new GestureMessage("RIGHT", clamp(count.intValue(), 0, 5), true);
			}
			return null;
		}

		if ("RIGHT_MOVE".equals(eventName)) {
			Integer midiValue = parseRightMoveValue(eventValue);
			if (midiValue != null) {
				return new GestureMessage("RIGHT_MOVE", midiValue.intValue(), true);
			}
			return null;
		}

		if ("BOTH".equals(eventName)) {
			if ("FIST".equalsIgnoreCase(eventValue)) {
				return new GestureMessage("BOTH", 0, true);
			}
			if ("OPEN".equalsIgnoreCase(eventValue)) {
				return new GestureMessage("BOTH", 0, false);
			}
		}

		return null;
	}

	private String extractString(String rawMessage, Pattern pattern) {
		Matcher matcher = pattern.matcher(rawMessage);
		if (matcher.find()) {
			return matcher.group(1);
		}
		return null;
	}

	private Integer extractInteger(String rawMessage, Pattern pattern) {
		Matcher matcher = pattern.matcher(rawMessage);
		if (matcher.find()) {
			return Integer.valueOf(matcher.group(1));
		}
		return null;
	}

	private Boolean extractBoolean(String rawMessage, Pattern pattern) {
		Matcher matcher = pattern.matcher(rawMessage);
		if (matcher.find()) {
			return Boolean.valueOf(matcher.group(1));
		}
		return null;
	}

	private Integer parseIntegerSafe(String value) {
		try {
			return Integer.valueOf(Integer.parseInt(value));
		} catch (NumberFormatException exception) {
			return null;
		}
	}

	private Integer parseRightMoveValue(String value) {
		try {
			double parsed = Double.parseDouble(value);
			if (parsed <= 1.0d && parsed >= 0.0d) {
				return Integer.valueOf(clamp((int) Math.round(parsed * 127.0d), 0, 127));
			}
			return Integer.valueOf(clamp((int) Math.round(parsed), 0, 127));
		} catch (NumberFormatException exception) {
			return null;
		}
	}

	private int clamp(int value, int min, int max) {
		return Math.max(min, Math.min(max, value));
	}

	public interface GestureListener {
		void onGesture(GestureMessage message);
	}

	public static class GestureMessage {
		private final String gesture;
		private final int value;
		private final boolean active;

		public GestureMessage(String gesture, int value, boolean active) {
			this.gesture = gesture;
			this.value = value;
			this.active = active;
		}

		public String getGesture() {
			return gesture;
		}

		public int getValue() {
			return value;
		}

		public boolean isActive() {
			return active;
		}
	}
}
