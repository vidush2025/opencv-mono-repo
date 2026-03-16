package communication;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
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
		String gesture = extractString(rawMessage, GESTURE_PATTERN);
		Integer value = extractInteger(rawMessage, VALUE_PATTERN);
		Boolean active = extractBoolean(rawMessage, ACTIVE_PATTERN);

		if (gesture == null || value == null || active == null) {
			System.out.println("Skipping malformed message: " + rawMessage);
			return null;
		}

		return new GestureMessage(gesture, value.intValue(), active.booleanValue());
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
