package midiController;

import javax.sound.midi.InvalidMidiDataException;
import javax.sound.midi.MidiDevice;
import javax.sound.midi.MidiMessage;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.Receiver;
import javax.sound.midi.ShortMessage;

public class MidiController {
	private MidiDevice currentDevice;
	private Receiver receiver;

	public void printAvailableOutputDevices() {
		MidiDevice.Info[] deviceInfos = MidiSystem.getMidiDeviceInfo();

		System.out.println("Available MIDI output devices:");
		for (MidiDevice.Info deviceInfo : deviceInfos) {
			try {
				MidiDevice device = MidiSystem.getMidiDevice(deviceInfo);
				if (device.getMaxReceivers() != 0) {
					System.out.println("- " + deviceInfo.getName() + " | " + deviceInfo.getDescription());
				}
			} catch (Exception exception) {
				System.out.println("- Unable to inspect device: " + deviceInfo.getName());
			}
		}
	}

	public boolean connect(String preferredDeviceName) {
		close();

		MidiDevice.Info[] deviceInfos = MidiSystem.getMidiDeviceInfo();
		for (MidiDevice.Info deviceInfo : deviceInfos) {
			try {
				MidiDevice device = MidiSystem.getMidiDevice(deviceInfo);
				if (device.getMaxReceivers() == 0) {
					continue;
				}

				if (preferredDeviceName != null
					&& !preferredDeviceName.trim().isEmpty()
					&& !deviceInfo.getName().toLowerCase().contains(preferredDeviceName.toLowerCase())) {
					continue;
				}

				device.open();
				receiver = device.getReceiver();
				currentDevice = device;
				System.out.println("Connected to MIDI device: " + deviceInfo.getName());
				return true;
			} catch (Exception exception) {
				System.out.println("Failed to connect to device: " + deviceInfo.getName());
			}
		}

		try {
			receiver = MidiSystem.getReceiver();
			currentDevice = null;
			System.out.println("Connected to default system MIDI receiver");
			return true;
		} catch (Exception exception) {
			System.out.println("No MIDI output receiver available");
			return false;
		}
	}

	public void sendControlChange(int channel, int controllerNumber, int value) {
		if (receiver == null) {
			return;
		}

		int safeChannel = Math.max(0, Math.min(15, channel));
		int safeControllerNumber = Math.max(0, Math.min(127, controllerNumber));
		int safeValue = Math.max(0, Math.min(127, value));

		try {
			ShortMessage message = new ShortMessage();
			message.setMessage(
				ShortMessage.CONTROL_CHANGE,
				safeChannel,
				safeControllerNumber,
				safeValue
			);
			send(message);
		} catch (InvalidMidiDataException exception) {
			System.out.println("Invalid MIDI data: " + exception.getMessage());
		}
	}

	private void send(MidiMessage message) {
		receiver.send(message, -1L);
	}

	public void close() {
		if (receiver != null) {
			receiver.close();
			receiver = null;
		}

		if (currentDevice != null && currentDevice.isOpen()) {
			currentDevice.close();
			currentDevice = null;
		}
	}
}
