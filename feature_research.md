# Feature Research & Recommendations
## Quantum Anomaly Detector Enhancement Ideas

Based on research into anomaly detection best practices, statistical metrics, and similar applications (EMF detectors, Geiger counters), here are recommended features and improvements:

---

## 1. Advanced Visualization Features

### Frequency Spectrum Analyzer
**What:** Add a real-time FFT (Fast Fourier Transform) display showing the frequency components of the anomaly score.
**Why:** Helps identify periodic/cyclic anomalies that might be missed in time-domain analysis. Can detect subtle oscillations in system behavior.
**Display:** A secondary graph panel showing frequency vs. magnitude (like a spectrum analyzer).

### Multiple Time Scale Views
**What:** Add toggleable views for different time scales (1min, 5min, 1hr history).
**Why:** Allows users to zoom out and see long-term patterns or zoom in for detailed analysis.

### Heat Map / 2D Spectrogram
**What:** A scrolling 2D heatmap showing anomaly score over time (Y-axis) vs. time (X-axis), with color representing intensity.
**Why:** Provides an intuitive visual representation of anomaly intensity over extended periods. Commonly used in spectral analysis tools.

### Expected Range Shading
**What:** Display a shaded "normal" band on the waveform graph based on historical data (e.g., mean ± 2 standard deviations).
**Why:** Makes it immediately clear when readings deviate from expected ranges. Industry standard for anomaly visualization.

---

## 2. Statistical Metrics & Analysis

### Rolling Z-Score Display
**What:** Show the Z-score (standard deviations from mean) alongside the raw anomaly score.
**Why:** Provides a statistically normalized view of how unusual the current reading is. More meaningful than raw deviation values.

### Multiple Detection Algorithms
**What:** Add options for different detection methods:
- IQR-based (Interquartile Range)
- MAD (Median Absolute Deviation)  
- Rolling Standard Deviation
**Why:** Different algorithms excel at different types of anomalies. Gives users flexibility to tune detection.

### Confidence Intervals
**What:** Display confidence levels for detections (e.g., "95% confidence this is anomalous").
**Why:** Reduces false positives and helps users understand reliability of alerts.

### Entropy Trend Analysis
**What:** Track and display the trend of Shannon Entropy over time (increasing/decreasing/stable).
**Why:** Changes in entropy trend can indicate systemic shifts before anomalies appear.

---

## 3. Data Export & Analysis Tools

### Detailed CSV Export
**What:** Export not just anomalies, but all data points with timestamps, all metrics (GPU, RAM, CPU, etc.), entropy, and scores.
**Why:** Enables offline analysis, correlation with external events, and machine learning training.

### Session Replay
**What:** Save entire sessions and replay them later to review detection performance.
**Why:** Useful for tuning sensitivity and understanding patterns over time.

### Comparative Analysis Mode
**What:** Load two CSV files and overlay their waveforms for comparison.
**Why:** Compare "normal" vs. "anomalous" periods, or before/after system changes.

---

## 4. Enhanced Alerting & Feedback

### Alert History Panel
**What:** A dedicated panel showing the last 10-20 anomalies with timestamps and peak scores.
**Why:** Provides quick access to recent events without scrolling through logs.

### Customizable Audio Alerts
**What:** Different sound patterns for different severity levels (like Geiger counter clicks that get faster with higher readings).
**Why:** Provides hands-free monitoring. Geiger counters are famous for this feature.

### Multi-Threshold Alerts
**What:** Define multiple threshold levels (yellow warning, orange alert, red critical).
**Why:** Provides graduated response instead of binary "ok/anomaly" state.

---

## 5. Hardware-Specific Enhancements

### GPU Utilization Graph
**What:** Real-time mini-graph of GPU utilization, temperature, and power alongside the main detection graph.
**Why:** Helps correlate anomalies with hardware state changes.

### Network Bandwidth Monitor
**What:** Monitor network I/O as an additional entropy source.
**Why:** Network packet timing can provide high-entropy data, and anomalies might correlate with network events.

### Disk I/O Jitter
**What:** Measure disk read/write latency variations as another entropy source.
**Why:** Storage systems exhibit quantum-like jitter at nanosecond scales.

---

## 6. Quality of Life Features

### Dark/Light Theme Toggle
**What:** User-selectable UI themes.
**Why:** Standard feature for applications used in different lighting conditions.

### Always-on-Top Mode
**What:** Pin window to stay above other applications.
**Why:** Useful for continuous monitoring while working on other tasks.

### Minimize to System Tray
**What:** Minimize to taskbar notification area with pop-up alerts.
**Why:** Allows background monitoring without screen space.

### Preset Profiles
**What:** Save/load sensitivity and configuration presets (e.g., "High Sensitivity", "Low Noise", "Balanced").
**Why:** Quick switching between configurations for different use cases.

### Auto-Calibration Mode
**What:** Automatic periodic recalibration every X minutes.
**Why:** Adapts to changing baseline conditions without manual intervention.

---

## 7. Advanced Features

### Correlation Analysis
**What:** Calculate correlation between different entropy sources (GPU vs RAM vs CPU).
**Why:** Identify which sources contribute most to anomalies.

### Machine Learning Mode
**What:** Option to train a simple ML model on "normal" data to improve detection accuracy.
**Why:** Adaptive detection that learns your system's unique baseline.

### Anomaly Prediction
**What:** Use historical patterns to predict likelihood of imminent anomaly.
**Why:** Proactive rather than reactive detection.

### Event Annotations
**What:** Allow users to manually mark and annotate significant events on the timeline.
**Why:** Helps correlate anomalies with known system events for tuning.

---

## Priority Recommendations (Implement First)

Based on impact vs. effort:

1. **Frequency Spectrum Analyzer** - High impact, medium effort
2. **Rolling Z-Score Display** - High impact, low effort  
3. **Multiple Time Scale Views** - Medium impact, low effort
4. **Expected Range Shading** - High impact, low effort
5. **Alert History Panel** - Medium impact, low effort
6. **Customizable Audio Alerts** - Medium impact, medium effort
7. **Preset Profiles** - High impact, low effort
8. **Detailed CSV Export** - Medium impact, low effort

---

## Implementation Notes

- Most statistical features can be added with NumPy/SciPy
- FFT analysis requires scipy.fft or numpy.fft
- Audio feedback can use pythonnet or windows winsound
- Theme support needs conditional styling in Tkinter
