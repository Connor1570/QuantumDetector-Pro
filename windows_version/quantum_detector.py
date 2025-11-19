import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import psutil
import time
import math
import random
import threading
from collections import deque
import numpy as np
import pynvml
import csv
import datetime
import os
import json
import winsound
from scipy import fft, stats

class QuantumDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Anomaly Detector - PRO Edition v3.0")
        self.root.geometry("1400x900")
        
        # Variables
        self.entropy_var = tk.StringVar(value="0.0000")
        self.anomaly_var = tk.StringVar(value="0.00")
        self.zscore_var = tk.StringVar(value="0.00")
        self.status_var = tk.StringVar(value="Initializing...")
        self.gpu_info_var = tk.StringVar(value="GPU: Detecting...")
        self.ram_info_var = tk.StringVar(value="RAM: Detecting...")
        self.sensitivity_label_var = tk.StringVar(value="Sensitivity: 5.00")
        self.timescale_var = tk.StringVar(value="5min")
        self.detection_method_var = tk.StringVar(value="Attractor")
        self.theme_var = tk.StringVar(value="Dark")
        
        self.sensitivity = 5.0
        self.running = True
        self.logging_enabled = tk.BooleanVar(value=False)
        self.audio_enabled = tk.BooleanVar(value=True)
        self.always_on_top = tk.BooleanVar(value=False)
        self.auto_calibrate = tk.BooleanVar(value=False)
        
        # Thresholds for multi-level alerts
        self.threshold_yellow = 3.0
        self.threshold_orange = 5.0
        self.threshold_red = 8.0
        
        # Data storage
        self.history = deque(maxlen=600)  # 10 min at 10Hz
        self.attractor_history = deque(maxlen=50)
        self.alert_history = deque(maxlen=20)
        self.full_data_log = []
        
        # Themes
        self.themes = {
            "Dark": {"bg": "#121212", "fg": "white", "canvas_bg": "#000000", "accent": "#BB86FC"},
            "Light": {"bg": "#F5F5F5", "fg": "black", "canvas_bg": "#FFFFFF", "accent": "#6200EE"}
        }
        self.current_theme = self.themes["Dark"]
        
        # Hardware Init
        self.init_gpu()
        self.init_ram_buffer()
        
        # UI
        self.apply_theme()
        self.create_widgets()
        
        # Start Thread
        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()
        
        self.log_message("System Initialized. All sensors active.", "info")
        
        # Auto-calibration timer
        self.last_calibration = time.time()

    def init_gpu(self):
        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(self.gpu_handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            self.gpu_info_var.set(f"GPU: {name}")
            self.gpu_active = True
        except Exception as e:
            self.gpu_info_var.set(f"GPU: Error")
            self.gpu_active = False

    def init_ram_buffer(self):
        try:
            self.ram_buffer = np.zeros(50 * 1024 * 1024, dtype=np.uint8)
            self.ram_info_var.set("RAM: 64GB System")
        except:
            self.ram_info_var.set("RAM: Buffer Failed")
            self.ram_buffer = None

    def apply_theme(self):
        theme = self.themes[self.theme_var.get()]
        self.root.configure(bg=theme["bg"])
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"], font=("Segoe UI", 10))
        style.configure("TButton", background="#333333", foreground="white")
        style.configure("TLabelframe", background=theme["bg"], foreground=theme["accent"])
        style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["accent"], font=("Segoe UI", 10, "bold"))
        style.configure("Horizontal.TScale", background=theme["bg"])
        style.configure("TCheckbutton", background=theme["bg"], foreground=theme["fg"])
        style.configure("TCombobox", fieldbackground=theme["bg"], background=theme["bg"], foreground=theme["fg"])

    def create_widgets(self):
        theme = self.current_theme
        
        # Header
        header = tk.Frame(self.root, bg=theme["bg"])
        header.pack(fill="x", pady=5)
        tk.Label(header, text="Quantum Anomaly Detector", bg=theme["bg"], fg=theme["accent"], font=("Segoe UI", 20, "bold")).pack()
        tk.Label(header, text="PRO EDITION v3.0 - ULTIMATE", bg=theme["bg"], fg="#FFD700", font=("Segoe UI", 9, "bold")).pack()

        # Main container
        main = tk.Frame(self.root, bg=theme["bg"])
        main.pack(fill="both", expand=True, padx=10, pady=5)

        # LEFT COLUMN
        left = tk.Frame(main, bg=theme["bg"], width=350)
        left.pack(side="left", fill="both", padx=5)

        # Sensors
        sensors = ttk.LabelFrame(left, text="Hardware Sensors")
        sensors.pack(fill="x", pady=3, ipadx=5, ipady=3)
        tk.Label(sensors, textvariable=self.status_var, bg=theme["bg"], fg="#03DAC5", font=("Consolas", 9)).pack(anchor="w")
        tk.Label(sensors, textvariable=self.gpu_info_var, bg=theme["bg"], fg="#AAA", font=("Consolas", 8)).pack(anchor="w")
        tk.Label(sensors, textvariable=self.ram_info_var, bg=theme["bg"], fg="#AAA", font=("Consolas", 8)).pack(anchor="w")

        # Metrics
        metrics = ttk.LabelFrame(left, text="Real-time Metrics")
        metrics.pack(fill="x", pady=3, ipadx=5, ipady=3)
        tk.Label(metrics, text="Entropy", bg=theme["bg"], fg=theme["fg"], font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(metrics, textvariable=self.entropy_var, bg=theme["bg"], fg="#00FF00", font=("Consolas", 16, "bold")).pack(anchor="w")
        tk.Label(metrics, text="Anomaly Score", bg=theme["bg"], fg=theme["fg"], font=("Segoe UI", 9)).pack(anchor="w", pady=(5,0))
        tk.Label(metrics, textvariable=self.anomaly_var, bg=theme["bg"], fg="#00FF00", font=("Consolas", 16, "bold")).pack(anchor="w")
        tk.Label(metrics, text="Z-Score", bg=theme["bg"], fg=theme["fg"], font=("Segoe UI", 9)).pack(anchor="w", pady=(5,0))
        tk.Label(metrics, textvariable=self.zscore_var, bg=theme["bg"], fg="#00FF00", font=("Consolas", 16, "bold")).pack(anchor="w")

        # Alert History
        alerts = ttk.LabelFrame(left, text="Alert History")
        alerts.pack(fill="both", expand=True, pady=3, ipadx=5, ipady=3)
        self.alert_list = tk.Listbox(alerts, bg=theme["canvas_bg"], fg="#FF0000", font=("Consolas", 8), height=8)
        self.alert_list.pack(fill="both", expand=True)

        # Log
        log = ttk.LabelFrame(left, text="Event Log")
        log.pack(fill="both", expand=True, pady=3, ipadx=3, ipady=3)
        self.log_text = scrolledtext.ScrolledText(log, bg=theme["canvas_bg"], fg="#00FF00", font=("Consolas", 8), height=8)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("info", foreground="#00FF00")
        self.log_text.tag_config("alert", foreground="#FF0000")
        self.log_text.tag_config("warn", foreground="#FFA500")

        # RIGHT COLUMN
        right = tk.Frame(main, bg=theme["bg"])
        right.pack(side="right", fill="both", expand=True, padx=5)

        # Waveform
        wave_frame = ttk.LabelFrame(right, text="Anomaly Waveform")
        wave_frame.pack(fill="both", expand=True, pady=3)
        self.canvas = tk.Canvas(wave_frame, bg=theme["canvas_bg"], height=250, highlightthickness=1, highlightbackground="#333")
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # FFT Spectrum
        fft_frame = ttk.LabelFrame(right, text="Frequency Spectrum (FFT)")
        fft_frame.pack(fill="both", expand=True, pady=3)
        self.fft_canvas = tk.Canvas(fft_frame, bg=theme["canvas_bg"], height=200, highlightthickness=1, highlightbackground="#333")
        self.fft_canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Controls
        controls = ttk.LabelFrame(right, text="Controls & Configuration")
        controls.pack(fill="x", pady=3, ipadx=5, ipady=5)

        # Detection Method
        tk.Label(controls, text="Detection Method:", bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=0, sticky="w", padx=5)
        method_combo = ttk.Combobox(controls, textvariable=self.detection_method_var, values=["Attractor", "Z-Score", "IQR", "MAD"], state="readonly", width=12)
        method_combo.grid(row=0, column=1, sticky="w", padx=5)

        # Time Scale
        tk.Label(controls, text="Time Scale:", bg=theme["bg"], fg=theme["fg"]).grid(row=0, column=2, sticky="w", padx=5)
        scale_combo = ttk.Combobox(controls, textvariable=self.timescale_var, values=["1min", "5min", "15min", "1hr"], state="readonly", width=8)
        scale_combo.grid(row=0, column=3, sticky="w", padx=5)
        scale_combo.bind("<<ComboboxSelected>>", self.change_timescale)

        # Sensitivity
        tk.Label(controls, textvariable=self.sensitivity_label_var, bg=theme["bg"], fg=theme["fg"]).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(5,0))
        self.slider = ttk.Scale(controls, from_=1.0, to=15.0, orient="horizontal", command=self.update_sensitivity)
        self.slider.set(5.0)
        self.slider.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=2)

        # Buttons
        btn_frame = tk.Frame(controls, bg=theme["bg"])
        btn_frame.grid(row=3, column=0, columnspan=4, pady=5)
        
        self.toggle_btn = ttk.Button(btn_frame, text="Pause", command=self.toggle_scanning, width=10)
        self.toggle_btn.pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Calibrate", command=self.calibrate, width=10).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Save Session", command=self.save_session, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Load Session", command=self.load_session, width=12).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Presets", command=self.show_presets, width=10).pack(side="left", padx=2)

        # Options
        opt_frame = tk.Frame(controls, bg=theme["bg"])
        opt_frame.grid(row=4, column=0, columnspan=4, sticky="w", padx=5)
        ttk.Checkbutton(opt_frame, text="Log to CSV", variable=self.logging_enabled).pack(side="left", padx=3)
        ttk.Checkbutton(opt_frame, text="Audio Alerts", variable=self.audio_enabled).pack(side="left", padx=3)
        ttk.Checkbutton(opt_frame, text="Always On Top", variable=self.always_on_top, command=self.toggle_always_on_top).pack(side="left", padx=3)
        ttk.Checkbutton(opt_frame, text="Auto-Cal (5min)", variable=self.auto_calibrate).pack(side="left", padx=3)
        ttk.Button(opt_frame, text="Theme", command=self.toggle_theme, width=8).pack(side="left", padx=3)

        # Alert overlay
        self.alert_label = tk.Label(self.root, text="ANOMALY DETECTED", bg=theme["bg"], fg="#FF0000", font=("Segoe UI", 32, "bold"))

    def log_message(self, message, tag="info"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)

    def add_alert(self, score, level="RED"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        alert_text = f"[{timestamp}] {level}: {score:.2f}"
        self.alert_list.insert(0, alert_text)
        if self.alert_list.size() > 20:
            self.alert_list.delete(20, tk.END)
        self.alert_history.append({"time": timestamp, "score": score, "level": level})

    def update_sensitivity(self, val):
        self.sensitivity = float(val)
        self.threshold_orange = self.sensitivity
        self.threshold_yellow = self.sensitivity * 0.6
        self.threshold_red = self.sensitivity * 1.6
        self.sensitivity_label_var.set(f"Sensitivity: {self.sensitivity:.2f}")

    def change_timescale(self, event=None):
        scales = {"1min": 60, "5min": 300, "15min": 900, "1hr": 3600}
        maxlen = scales[self.timescale_var.get()] // 0.1  # 10Hz sampling
        self.history = deque(list(self.history)[-int(maxlen):], maxlen=int(maxlen))

    def toggle_scanning(self):
        self.running = not self.running
        self.toggle_btn.config(text="Resume" if not self.running else "Pause")
        self.log_message("Scanning " + ("Paused" if not self.running else "Resumed"), "warn")

    def calibrate(self):
        self.attractor_history.clear()
        self.history.clear()
        self.canvas.delete("all")
        self.fft_canvas.delete("all")
        self.last_calibration = time.time()
        self.log_message("Zero Point Calibrated", "warn")

    def toggle_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top.get())

    def toggle_theme(self):
        self.theme_var.set("Light" if self.theme_var.get() == "Dark" else "Dark")
        self.current_theme = self.themes[self.theme_var.get()]
        self.apply_theme()
        self.root.destroy()
        self.__init__(tk.Tk())

    def save_session(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            data = {
                "history": list(self.history),
                "alerts": list(self.alert_history),
                "config": {
                    "sensitivity": self.sensitivity,
                    "method": self.detection_method_var.get(),
                    "timescale": self.timescale_var.get()
                }
            }
            with open(filename, 'w') as f:
                json.dump(data, f)
            self.log_message(f"Session saved: {os.path.basename(filename)}", "info")

    def load_session(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.history = deque(data["history"], maxlen=self.history.maxlen)
            self.alert_history = deque(data["alerts"], maxlen=20)
            self.sensitivity = data["config"]["sensitivity"]
            self.slider.set(self.sensitivity)
            self.log_message(f"Session loaded: {os.path.basename(filename)}", "info")

    def show_presets(self):
        preset_win = tk.Toplevel(self.root)
        preset_win.title("Preset Profiles")
        preset_win.geometry("300x200")
        
        presets = {
            "High Sensitivity": 2.0,
            "Balanced": 5.0,
            "Low Noise": 10.0
        }
        
        for name, value in presets.items():
            btn = ttk.Button(preset_win, text=name, command=lambda v=value: self.apply_preset(v, preset_win))
            btn.pack(pady=5, padx=20, fill="x")

    def apply_preset(self, value, window):
        self.slider.set(value)
        self.log_message(f"Preset applied: Sensitivity={value:.1f}", "info")
        window.destroy()

    # Hardware methods
    def get_gpu_entropy(self):
        if not self.gpu_active:
            return 0, 0
        try:
            temp = pynvml.nvmlDeviceGetTemperature(self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle)
            return temp, power
        except:
            return 0, 0

    def get_ram_jitter(self):
        if self.ram_buffer is None:
            return 0
        idx = np.random.randint(0, len(self.ram_buffer), 1000)
        t0 = time.perf_counter_ns()
        _ = self.ram_buffer[idx]
        t1 = time.perf_counter_ns()
        return (t1 - t0)

    def get_system_vector(self):
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        gpu_temp, gpu_power = self.get_gpu_entropy()
        ram_jitter = self.get_ram_jitter()
        time_jitter = (time.perf_counter() * 1000000) % 100
        return [cpu, ram, gpu_temp, gpu_power / 1000.0, ram_jitter / 1000.0, time_jitter]

    def calculate_shannon_entropy(self, data):
        entropy = 0
        for x in data:
            if x > 0:
                val = (x % 100) / 100.0
                if val > 0:
                    entropy -= val * math.log(val)
        return abs(entropy)

    def calculate_anomaly_score(self, vector):
        method = self.detection_method_var.get()
        
        if method == "Attractor":
            self.attractor_history.append(vector)
            if len(self.attractor_history) < 2:
                return 0
            centroid = np.mean(self.attractor_history, axis=0)
            return np.linalg.norm(np.array(vector) - centroid)
        
        elif method == "Z-Score":
            if len(self.history) < 10:
                return 0
            recent = list(self.history)[-30:]
            mean = np.mean(recent)
            std = np.std(recent)
            if std == 0:
                return 0
            current = np.linalg.norm(vector)
            return abs((current - mean) / std)
        
        elif method == "IQR":
            if len(self.history) < 10:
                return 0
            recent = list(self.history)[-50:]
            q1, q3 = np.percentile(recent, [25, 75])
            iqr = q3 - q1
            current = np.linalg.norm(vector)
            if current < q1 - 1.5 * iqr or current > q3 + 1.5 * iqr:
                return abs(current - np.median(recent))
            return 0
        
        elif method == "MAD":
            if len(self.history) < 10:
                return 0
            recent = list(self.history)[-50:]
            median = np.median(recent)
            mad = np.median([abs(x - median) for x in recent])
            current = np.linalg.norm(vector)
            if mad == 0:
                return 0
            return abs((current - median) / (1.4826 * mad))
        
        return 0

    def calculate_zscore(self):
        if len(self.history) < 10:
            return 0
        recent = list(self.history)[-50:]
        mean = np.mean(recent)
        std = np.std(recent)
        if std == 0:
            return 0
        return (self.history[-1] - mean) / std

    def draw_waveform(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        if len(self.history) < 2:
            return

        # Expected range shading
        if len(self.history) > 20:
            recent = list(self.history)
            mean = np.mean(recent)
            std = np.std(recent)
            upper = mean + 2 * std
            lower = mean - 2 * std
            max_val = 20.0
            
            y_upper = h - (min(upper, max_val) / max_val) * h
            y_lower = h - (min(lower, max_val) / max_val) * h
            self.canvas.create_rectangle(0, y_upper, w, y_lower, fill="#004400", outline="")

        # Grid
        self.canvas.create_line(0, h/2, w, h/2, fill="#333", dash=(2, 4))
        
        # Waveform
        max_val = 20.0
        step = w / len(self.history)
        points = []
        for i, val in enumerate(self.history):
            x = i * step
            y = h - (min(val, max_val) / max_val) * h
            points.extend([x, y])

        if len(points) >= 4:
            color = "#00FF00"
            if self.history[-1] > self.threshold_red:
                color = "#FF0000"
            elif self.history[-1] > self.threshold_orange:
                color = "#FF8800"
            elif self.history[-1] > self.threshold_yellow:
                color = "#FFFF00"
            
            self.canvas.create_line(points, fill=color, width=2)

    def draw_fft(self):
        self.fft_canvas.delete("all")
        w = self.fft_canvas.winfo_width()
        h = self.fft_canvas.winfo_height()
        
        if len(self.history) < 32:
            return

        # Perform FFT
        data = np.array(list(self.history))
        fft_result = np.abs(fft.rfft(data))
        freqs = fft.rfftfreq(len(data), d=0.1)  # 10Hz sampling
        
        # Draw bars
        n_bins = min(50, len(fft_result))
        bar_width = w / n_bins
        max_magnitude = np.max(fft_result[1:]) if len(fft_result) > 1 else 1
        
        for i in range(1, n_bins):
            if i >= len(fft_result):
                break
            magnitude = fft_result[i]
            bar_height = (magnitude / max_magnitude) * h * 0.9
            x = i * bar_width
            y = h - bar_height
            
            color = "#00FF00" if magnitude < max_magnitude * 0.7 else "#FFFF00"
            self.fft_canvas.create_rectangle(x, y, x + bar_width - 1, h, fill=color, outline="")

    def play_alert_sound(self, level):
        if not self.audio_enabled.get():
            return
        
        try:
            if level == "RED":
                winsound.Beep(1000, 200)
            elif level == "ORANGE":
                winsound.Beep(800, 150)
            elif level == "YELLOW":
                winsound.Beep(600, 100)
        except:
            pass

    def log_anomaly_csv(self, deviation, vector):
        if not self.logging_enabled.get():
            return
        
        file_exists = os.path.isfile("anomalies.csv")
        with open("anomalies.csv", "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Deviation", "Z-Score", "Vector"])
            zscore = self.calculate_zscore()
            writer.writerow([datetime.datetime.now(), deviation, zscore, str(vector)])

    def update_loop(self):
        while True:
            if self.running:
                # Auto-calibration
                if self.auto_calibrate.get() and (time.time() - self.last_calibration) > 300:
                    self.root.after(0, self.calibrate)
                
                vector = self.get_system_vector()
                entropy = self.calculate_shannon_entropy(vector)
                deviation = self.calculate_anomaly_score(vector)
                
                self.root.after(0, self.update_ui, entropy, deviation, vector)
            
            time.sleep(0.1)

    def update_ui(self, entropy, deviation, vector):
        self.entropy_var.set(f"{entropy:.4f}")
        self.anomaly_var.set(f"{deviation:.2f}")
        
        zscore = self.calculate_zscore()
        self.zscore_var.set(f"{zscore:.2f}")
        
        self.history.append(deviation)
        self.full_data_log.append({
            "time": datetime.datetime.now().isoformat(),
            "entropy": entropy,
            "deviation": deviation,
            "zscore": zscore,
            "vector": vector
        })
        
        self.draw_waveform()
        self.draw_fft()

        # Multi-threshold alerts
        level = None
        if deviation > self.threshold_red:
            level = "RED"
            self.alert_label.place(relx=0.5, rely=0.5, anchor="center")
            self.anomaly_var.set(f"{deviation:.2f} !!!")
        elif deviation > self.threshold_orange:
            level = "ORANGE"
            self.alert_label.place_forget()
        elif deviation > self.threshold_yellow:
            level = "YELLOW"
            self.alert_label.place_forget()
        else:
            self.alert_label.place_forget()
        
        if level:
            self.add_alert(deviation, level)
            self.log_message(f"{level} ALERT! Score: {deviation:.2f}", "alert")
            self.log_anomaly_csv(deviation, vector)
            threading.Thread(target=self.play_alert_sound, args=(level,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumDetectorApp(root)
    root.mainloop()
