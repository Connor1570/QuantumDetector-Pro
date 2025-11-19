package com.antigravity.quantumdetector;

import java.util.LinkedList;

public class AttractorAnalyzer {

    private static final int HISTORY_SIZE = 50;
    private LinkedList<float[]> history = new LinkedList<>();
    private float[] centroid = new float[3];

    /**
     * Updates the attractor state with a new 3D vector (e.g., Accel X, Y, Z).
     * Returns a deviation score (Euclidean distance from the running centroid).
     */
    public double updateAndGetDeviation(float[] vector) {
        history.add(vector.clone());
        if (history.size() > HISTORY_SIZE) {
            history.removeFirst();
        }

        // Recalculate centroid (The "Attractor")
        float sumX = 0, sumY = 0, sumZ = 0;
        for (float[] v : history) {
            sumX += v[0];
            sumY += v[1];
            sumZ += v[2];
        }
        int size = history.size();
        centroid[0] = sumX / size;
        centroid[1] = sumY / size;
        centroid[2] = sumZ / size;

        // Calculate distance of current vector from centroid
        double dist = Math.sqrt(
            Math.pow(vector[0] - centroid[0], 2) +
            Math.pow(vector[1] - centroid[1], 2) +
            Math.pow(vector[2] - centroid[2], 2)
        );

        return dist;
    }
}
