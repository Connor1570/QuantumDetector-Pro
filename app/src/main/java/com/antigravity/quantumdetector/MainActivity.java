package com.antigravity.quantumdetector;

import android.content.Context;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.slider.Slider;
import java.util.Locale;

public class MainActivity extends AppCompatActivity implements SensorManagerHelper.SensorCallback {

    private SensorManagerHelper sensorHelper;
    private QuantumEntropySource entropySource;
    private AttractorAnalyzer attractorAnalyzer;

    private TextView entropyValueText;
    private TextView anomalyValueText;
    private TextView alertText;
    private WaveformView waveformView;
    private Slider sensitivitySlider;
    private Button calibrateButton;

    private Vibrator vibrator;
    private double anomalyThreshold = 5.0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize Views
        entropyValueText = findViewById(R.id.entropyValue);
        anomalyValueText = findViewById(R.id.anomalyValue);
        alertText = findViewById(R.id.alertText);
        waveformView = findViewById(R.id.waveformView);
        sensitivitySlider = findViewById(R.id.sensitivitySlider);
        calibrateButton = findViewById(R.id.calibrateButton);

        // Initialize Logic
        sensorHelper = new SensorManagerHelper(this, this);
        entropySource = new QuantumEntropySource();
        attractorAnalyzer = new AttractorAnalyzer();
        vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);

        // Setup Controls
        sensitivitySlider.addOnChangeListener((slider, value, fromUser) -> {
            anomalyThreshold = value;
            // Update graph scale visually if needed, or just logic
        });

        calibrateButton.setOnClickListener(v -> {
            attractorAnalyzer = new AttractorAnalyzer(); // Reset history
            waveformView = findViewById(R.id.waveformView); // Re-binding not needed, just visual reset?
            // Actually, just resetting the analyzer is enough.
            // Maybe clear graph too?
            // waveformView.clear(); // If we implemented clear
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        sensorHelper.start();
    }

    @Override
    protected void onPause() {
        super.onPause();
        sensorHelper.stop();
    }

    @Override
    public void onSensorData(float[] accelerometerValues, float[] magnetometerValues) {
        // 1. Calculate Entropy
        double entropy = entropySource.calculateEntropy(accelerometerValues);
        if (entropy >= 0) {
            entropyValueText.setText(String.format(Locale.US, "%.4f", entropy));
        }

        // 2. Analyze Attractor
        double deviation = attractorAnalyzer.updateAndGetDeviation(accelerometerValues);
        anomalyValueText.setText(String.format(Locale.US, "%.2f", deviation));

        // 3. Update Graph
        waveformView.addPoint((float) deviation);

        // 4. Check Anomalies
        if (deviation > anomalyThreshold) {
            alertText.setVisibility(View.VISIBLE);
            anomalyValueText.setTextColor(getColor(R.color.quantum_red));
            waveformView.setColor(getColor(R.color.quantum_red));
            triggerHapticFeedback();
        } else {
            alertText.setVisibility(View.INVISIBLE);
            anomalyValueText.setTextColor(getColor(R.color.quantum_green));
            waveformView.setColor(getColor(R.color.quantum_green));
        }
    }

    private void triggerHapticFeedback() {
        if (vibrator != null && vibrator.hasVibrator()) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE));
            } else {
                vibrator.vibrate(50);
            }
        }
    }
}
