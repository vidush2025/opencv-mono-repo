package mapping;

import config.Config;
import java.util.HashMap;
import java.util.Map;

import midiController.MidiController;

public class MidiMapper {
	private final Map<String, Mapping> mappings;

	public MidiMapper(Config config) {
		mappings = new HashMap<String, Mapping>();
		addMapping(config, "pinch", 1, false);
		addMapping(config, "hand_height", 2, true);
		addMapping(config, "toggle", 3, true);
	}

	private void addMapping(Config config, String gestureName, int fallbackCc, boolean fallbackSendWhenInactive) {
		Config.MappingConfig loadedMapping = config.getMapping(gestureName);
		if (loadedMapping == null) {
			mappings.put(gestureName, new Mapping(config.getDefaultChannel(), fallbackCc, fallbackSendWhenInactive));
			return;
		}

		mappings.put(
			gestureName,
			new Mapping(
				loadedMapping.getChannel(),
				loadedMapping.getControllerNumber(),
				loadedMapping.isSendWhenInactive()
			)
		);
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
