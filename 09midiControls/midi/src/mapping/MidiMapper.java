package mapping;

import config.Config;
import java.util.Arrays;

import midiController.MidiController;

public class MidiMapper {
	private static final int GESTURE_SLOTS = 5;
	private final int defaultChannel;
	private final int[] controllerNumbers;
	private final int[] faderValues;
	private final int[] previousValues;
	private final int[] lastSentValues;
	private final int resetValue;
	private final int muteValue;
	private final int faderCount;
	private int selectedLeftControl;
	private int selectedRightControl;
	private boolean muteState;

	public MidiMapper(Config config) {
		defaultChannel = config.getDefaultChannel();
		int[] loadedControllers = config.getFaderControllerNumbers();
		if (loadedControllers.length == 0) {
			loadedControllers = new int[] {1, 2, 3, 4, 5};
		}
		controllerNumbers = loadedControllers;
		faderCount = controllerNumbers.length;
		resetValue = clamp(config.getResetValue(), 0, 127);
		muteValue = clamp(config.getMuteValue(), 0, 127);
		faderValues = new int[faderCount];
		previousValues = new int[faderCount];
		lastSentValues = new int[faderCount];
		Arrays.fill(faderValues, resetValue);
		Arrays.fill(previousValues, resetValue);
		Arrays.fill(lastSentValues, -1);
		selectedLeftControl = 1;
		// selectedRightControl = 1;
		muteState = false;
	}

	public void handleGesture(String gesture, int value, boolean active, MidiController midiController) {
		if (gesture == null) {
			return;
		}

		if ("LEFT".equals(gesture)) {
			handleLeftGesture(value, midiController);
			return;
		}

		if ("RIGHT".equals(gesture)) {
			// handleRightSelection(value);
			return;
		}

		if ("RIGHT_MOVE".equals(gesture)) {
			handleRightMove(value, midiController);
			return;
		}

		if ("BOTH".equals(gesture)) {
			if (active) {
				activateMute(midiController);
			} else {
				restoreFromMute(midiController);
			}
		}
	}

	private void handleLeftGesture(int value, MidiController midiController) {
		int normalized = clamp(value, 0, GESTURE_SLOTS);
		if (normalized == 0) {
			resetAllFaders(midiController);
			return;
		}

		selectedLeftControl = normalized;
		if (selectedLeftControl <= faderCount) {
			sendFaderIfChanged(selectedLeftControl - 1, faderValues[selectedLeftControl - 1], midiController);
		}
	}

	// private void handleRightSelection(int value) {
	// 	selectedRightControl = clamp(value, 1, GESTURE_SLOTS);
	// }

	private void handleRightMove(int value, MidiController midiController) {
		if (muteState) {
			return;
		}

		int midiValue = clamp(value, 0, 127);

		// Left hand selection decides target fader(s)
		if (selectedLeftControl == GESTURE_SLOTS) {
			for (int index = 0; index < faderCount; index++) {
				setFaderValue(index, midiValue, midiController);
			}
			return;
		}

		if (selectedLeftControl <= faderCount) {
			setFaderValue(selectedLeftControl - 1, midiValue, midiController);
		}
	}
	private void activateMute(MidiController midiController) {
		if (muteState) {
			return;
		}

		for (int index = 0; index < faderCount; index++) {
			previousValues[index] = faderValues[index];
			setFaderValue(index, muteValue, midiController);
		}
		muteState = true;
	}

	private void restoreFromMute(MidiController midiController) {
		if (!muteState) {
			return;
		}

		for (int index = 0; index < faderCount; index++) {
			setFaderValue(index, previousValues[index], midiController);
		}
		muteState = false;
	}

	private void resetAllFaders(MidiController midiController) {
		for (int index = 0; index < faderCount; index++) {
			setFaderValue(index, resetValue, midiController);
		}
	}

	private void setFaderValue(int index, int value, MidiController midiController) {
		int safeValue = clamp(value, 0, 127);
		faderValues[index] = safeValue;
		sendFaderIfChanged(index, safeValue, midiController);
	}

	private void sendFaderIfChanged(int index, int value, MidiController midiController) {
		if (lastSentValues[index] == value) {
			return;
		}

		midiController.sendControlChange(defaultChannel, controllerNumbers[index], value);
		lastSentValues[index] = value;
		System.out.println("Fader " + (index + 1) + " -> CC " + controllerNumbers[index] + " value " + value);
	}

	private int clamp(int value, int min, int max) {
		return Math.max(min, Math.min(max, value));
	}
}
