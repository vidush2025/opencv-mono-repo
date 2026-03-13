package config;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.IOException;
import java.util.Map;

public class Config {
    private int port = 8888;
    private String preferredDeviceName = "";
    private int defaultChannel = 0;
    private final Map<String, MappingConfig> mappings = new HashMap<String, MappingConfig>();

    public Config() {
        mappings.put("pinch", new MappingConfig(defaultChannel, 1, false));
        mappings.put("hand_height", new MappingConfig(defaultChannel, 2, true));
        mappings.put("toggle", new MappingConfig(defaultChannel, 3, true));
    }

    public int getPort() { return port; }
    public String getPreferredDeviceName() { return preferredDeviceName; }
    public int getDefaultChannel() { return defaultChannel; }

    public MappingConfig getMapping(String gestureName) {
        return mappings.get(gestureName);
    }

    public static class MappingConfig {
        private final int channel;
        private final int controllerNumber;
        private final boolean sendWhenInactive;

        public MappingConfig(int channel, int controllerNumber, boolean sendWhenInactive) {
            this.channel = channel;
            this.controllerNumber = controllerNumber;
            this.sendWhenInactive = sendWhenInactive;
        }

        public int getChannel() {
            return channel;
        }

        public int getControllerNumber() {
            return controllerNumber;
        }

        public boolean isSendWhenInactive() {
            return sendWhenInactive;
        }
    }

    public static Config load() {
        Config cfg = new Config();
        Path path = Paths.get("..", "config.json"); // running from midi/ per your batch file
        if (!Files.exists(path)) {
            return cfg;
        }
        try {
            String text = new String(Files.readAllBytes(path), StandardCharsets.UTF_8);
            Pattern portPattern = Pattern.compile("\"socket\"\\s*:\\s*\\{[\\s\\S]*?\"port\"\\s*:\\s*(\\d+)", Pattern.DOTALL);
            Matcher m = portPattern.matcher(text);
            if (m.find()) {
                cfg.port = Integer.parseInt(m.group(1));
            }

            Pattern devicePattern = Pattern.compile("\"midi\"\\s*:\\s*\\{[\\s\\S]*?\"preferredDeviceName\"\\s*:\\s*\"([^\"]*)\"", Pattern.DOTALL);
            m = devicePattern.matcher(text);
            if (m.find()) {
                cfg.preferredDeviceName = m.group(1);
            }

            Pattern defaultChannelPattern = Pattern.compile("\"midi\"\\s*:\\s*\\{[\\s\\S]*?\"defaultChannel\"\\s*:\\s*(-?\\d+)", Pattern.DOTALL);
            m = defaultChannelPattern.matcher(text);
            if (m.find()) {
                cfg.defaultChannel = clamp(Integer.parseInt(m.group(1)), 0, 15);
            }

            cfg.loadMapping(text, "pinch", 1, false);
            cfg.loadMapping(text, "hand_height", 2, true);
            cfg.loadMapping(text, "toggle", 3, true);
        } catch (IOException e) {
            // fall back to defaults
        }
        return cfg;
    }

    private void loadMapping(String rawConfig, String gestureName, int defaultCc, boolean defaultSendWhenInactive) {
        MappingConfig defaultMapping = new MappingConfig(defaultChannel, defaultCc, defaultSendWhenInactive);
        String escapedGesture = Pattern.quote(gestureName);
        Pattern mappingPattern = Pattern.compile("\"" + escapedGesture + "\"\\s*:\\s*\\{([\\s\\S]*?)\\}", Pattern.DOTALL);
        Matcher mappingMatcher = mappingPattern.matcher(rawConfig);
        if (!mappingMatcher.find()) {
            mappings.put(gestureName, defaultMapping);
            return;
        }

        String body = mappingMatcher.group(1);
        int channel = extractInt(body, "channel", defaultChannel);
        int cc = extractInt(body, "cc", defaultCc);
        boolean sendWhenInactive = extractBoolean(body, "sendWhenInactive", defaultSendWhenInactive);

        mappings.put(
            gestureName,
            new MappingConfig(
                clamp(channel, 0, 15),
                clamp(cc, 0, 127),
                sendWhenInactive
            )
        );
    }

    private int extractInt(String section, String key, int fallbackValue) {
        Pattern pattern = Pattern.compile("\"" + Pattern.quote(key) + "\"\\s*:\\s*(-?\\d+)");
        Matcher matcher = pattern.matcher(section);
        if (matcher.find()) {
            return Integer.parseInt(matcher.group(1));
        }
        return fallbackValue;
    }

    private boolean extractBoolean(String section, String key, boolean fallbackValue) {
        Pattern pattern = Pattern.compile("\"" + Pattern.quote(key) + "\"\\s*:\\s*(true|false)");
        Matcher matcher = pattern.matcher(section);
        if (matcher.find()) {
            return Boolean.parseBoolean(matcher.group(1));
        }
        return fallbackValue;
    }

    private static int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }
}