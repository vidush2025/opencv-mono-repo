package mapping;

import java.util.HashMap;
import java.util.Map;

import midiController.MidiController;

public class MidiMapper {
	private final Map<String, Mapping> mappings;

	public MidiMapper() {
		mappings = new HashMap<String, Mapping>();
		mappings.put("pinch", new Mapping(0, 1, false));
		mappings.put("hand_height", new Mapping(0, 2, true));
		mappings.put("toggle", new Mapping(0, 3, true));
	}

	public void handleGesture(String gesture, int value, boolean active, MidiController midiController) {
		Mapping mapping = mappings.get(gesture);
		if (mapping == null) {
			return;
		}

		if (!mapping.sendWhenInactive && !active) {
			return;
		}

		int outgoingValue = value;
		if ("toggle".equals(gesture)) {
			outgoingValue = active ? 127 : 0;
		}

		midiController.sendControlChange(mapping.channel, mapping.controllerNumber, outgoingValue);
		System.out.println(
			"Mapped gesture " + gesture
				+ " -> CC " + mapping.controllerNumber
				+ " value " + outgoingValue
		);
	}

	private static class Mapping {
		private final int channel;
		private final int controllerNumber;
		private final boolean sendWhenInactive;

		private Mapping(int channel, int controllerNumber, boolean sendWhenInactive) {
			this.channel = channel;
			this.controllerNumber = controllerNumber;
			this.sendWhenInactive = sendWhenInactive;
		}
	}
}
