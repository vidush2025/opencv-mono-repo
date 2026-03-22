package mapping;

import config.Config;
import java.util.Arrays;

import midiController.MidiController;

public class MidiMapper {
	private static final int GESTURE_SLOTS = 5;
	private static final int MAX_CC_VALUE = (int) Math.round(127.0d * 0.8d);
	private static final double RIGHT_MOVE_SMOOTHING_ALPHA = 0.35d;
	private final int defaultChannel;
	private final int[] controllerNumbers;
	private final int[] faderValues;
	private final int[] lastSentValues;
	private final double[] smoothedMoveValues;
	private final int resetValue;
	private final int muteValue;
	private final int openValue;
	private final int faderCount;
	private int selectedLeftControl;
	private boolean muteState;
	private boolean rightFistActive;

	public MidiMapper(Config config) {
		defaultChannel = config.getDefaultChannel();
		int[] loadedControllers = config.getFaderControllerNumbers();
		if (loadedControllers.length == 0) {
			loadedControllers = new int[] {1, 2, 3, 4, 5};
		}
		controllerNumbers = loadedControllers;
		faderCount = controllerNumbers.length;
		resetValue = clamp(config.getResetValue(), 0, MAX_CC_VALUE);
		muteValue = clamp(config.getMuteValue(), 0, MAX_CC_VALUE);
		openValue = MAX_CC_VALUE;
		faderValues = new int[faderCount];
		lastSentValues = new int[faderCount];
		smoothedMoveValues = new double[faderCount];
		Arrays.fill(faderValues, clamp(resetValue, 0, MAX_CC_VALUE));
		Arrays.fill(smoothedMoveValues, -1.0d);
		Arrays.fill(lastSentValues, -1);
		selectedLeftControl = 1;
		muteState = false;
		rightFistActive = false;
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
			handleRightGesture(value, active, midiController);
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
				releaseToOpenLevel(midiController);
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

	private void handleRightMove(int value, MidiController midiController) {
		if (muteState || rightFistActive) {
			return;
		}

		int midiValue = clamp(value, 0, MAX_CC_VALUE);

		if (selectedLeftControl <= faderCount) {
			int targetIndex = selectedLeftControl - 1;
			setFaderValue(targetIndex, smoothMoveValue(targetIndex, midiValue), midiController);
		}
	}

	private void handleRightGesture(int value, boolean active, MidiController midiController) {
		boolean isFist = active && value == 0;
		if (isFist) {
			if (!rightFistActive) {
				rightFistActive = true;
				muteSelectedFader(midiController);
			}
			return;
		}

		rightFistActive = false;
	}

	private void muteSelectedFader(MidiController midiController) {
		if (muteState) {
			return;
		}

		if (selectedLeftControl <= 0 || selectedLeftControl > faderCount) {
			return;
		}

		setFaderValue(selectedLeftControl - 1, muteValue, midiController);
	}

	private void activateMute(MidiController midiController) {
		if (muteState) {
			return;
		}

		rightFistActive = false;

		for (int index = 0; index < faderCount; index++) {
			setFaderValue(index, muteValue, midiController);
		}
		muteState = true;
	}

	private void releaseToOpenLevel(MidiController midiController) {
		if (!muteState) {
			return;
		}

		for (int index = 0; index < faderCount; index++) {
			setFaderValue(index, openValue, midiController);
		}
		muteState = false;
	}

	private void resetAllFaders(MidiController midiController) {
		for (int index = 0; index < faderCount; index++) {
			setFaderValue(index, resetValue, midiController);
		}
	}

	private void setFaderValue(int index, int value, MidiController midiController) {
		int safeValue = clamp(value, 0, MAX_CC_VALUE);
		faderValues[index] = safeValue;
		smoothedMoveValues[index] = safeValue;
		sendFaderIfChanged(index, safeValue, midiController);
	}

	private int smoothMoveValue(int index, int targetValue) {
		double previous = smoothedMoveValues[index];
		double smoothed;

		if (previous < 0.0d) {
			smoothed = targetValue;
		} else {
			smoothed = (RIGHT_MOVE_SMOOTHING_ALPHA * targetValue)
				+ ((1.0d - RIGHT_MOVE_SMOOTHING_ALPHA) * previous);
		}

		smoothedMoveValues[index] = smoothed;
		return clamp((int) Math.round(smoothed), 0, MAX_CC_VALUE);
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
