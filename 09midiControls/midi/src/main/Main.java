package main;

import communication.PythonReceiver;
import mapping.MidiMapper;
import midiController.MidiController;
import config.Config;

public class Main {
    public static void main(String[] args) {
        Config cfg = Config.load();
        final String preferredDeviceName = args.length > 0 ? args[0] : cfg.getPreferredDeviceName();
        final MidiController midiController = new MidiController();
        final MidiMapper midiMapper = new MidiMapper(cfg);

        midiController.printAvailableOutputDevices();
        midiController.connect(preferredDeviceName);

        final PythonReceiver receiver = new PythonReceiver(
            cfg.getPort(),
            new PythonReceiver.GestureListener() {
                @Override
                public void onGesture(PythonReceiver.GestureMessage message) {
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