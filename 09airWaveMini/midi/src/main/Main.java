package main;

import communication.PythonReciever;
import mapping.MidiMapper;
import midiController.MidiController;

public class Main {
	public static void main(String[] args) {
		final String preferredDeviceName = args.length > 0 ? args[0] : "";
		final MidiController midiController = new MidiController();
		final MidiMapper midiMapper = new MidiMapper();

		midiController.printAvailableOutputDevices();
		midiController.connect(preferredDeviceName);

		final PythonReciever receiver = new PythonReciever(
			8888,
			new PythonReciever.GestureListener() {
				@Override
				public void onGesture(PythonReciever.GestureMessage message) {
					midiMapper.handleGesture(
						message.getGesture(),
						message.getValue(),
						message.isActive(),
						midiController
					);
				}
			}
		);

		Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {
			@Override
			public void run() {
				receiver.stop();
				midiController.close();
			}
		}));

		try {
			receiver.start();
		} catch (Exception exception) {
			System.out.println("Failed to start receiver: " + exception.getMessage());
		} finally {
			receiver.stop();
			midiController.close();
		}
	}
}
