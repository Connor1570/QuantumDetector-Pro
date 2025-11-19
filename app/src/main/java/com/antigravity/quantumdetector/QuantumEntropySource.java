package com.antigravity.quantumdetector;

import java.nio.ByteBuffer;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class QuantumEntropySource {

    private StringBuilder entropyBuffer = new StringBuilder();
    private static final int BUFFER_SIZE = 256;

    /**
     * Extracts the Least Significant Bits (LSB) from sensor float values.
     * These bits are most susceptible to thermal/quantum noise.
     */
    public double calculateEntropy(float[] values) {
        for (float val : values) {
            int rawBits = Float.floatToRawIntBits(val);
            // Extract the last 4 bits
            int lsb = rawBits & 0xF;
            entropyBuffer.append(Integer.toHexString(lsb));
        }

        if (entropyBuffer.length() >= BUFFER_SIZE) {
            String rawEntropy = entropyBuffer.toString();
            entropyBuffer.setLength(0); // Clear buffer
            return calculateShannonEntropy(rawEntropy);
        }

        return -1.0; // Not enough data yet
    }

    private double calculateShannonEntropy(String s) {
        int[] frequencies = new int[16]; // Hex characters 0-F
        for (char c : s.toCharArray()) {
            int val = Character.digit(c, 16);
            if (val >= 0) frequencies[val]++;
        }

        double entropy = 0.0;
        int len = s.length();
        for (int freq : frequencies) {
            if (freq > 0) {
                double p = (double) freq / len;
                entropy -= p * (Math.log(p) / Math.log(2));
            }
        }
        return entropy;
    }
}
