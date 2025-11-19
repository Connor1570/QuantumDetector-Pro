import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
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

class QuantumDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Anomaly Detector - PRO Edition v2.2")
        self.root.geometry("1000x750")
        self.root.configure(bg="#121212")

        # Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#121212", foreground="white", font=("Segoe UI", 10))
        self.style.configure("TButton", background="#333333", foreground="white", font=("Segoe UI", 9))
        self.style.configure("TLabelframe", background="#121212", foreground="#BB86FC")
        self.style.configure("TLabelframe.Label", background="#121212", foreground="#BB86FC", font=("Segoe UI", 10, "bold"))
        self.style.configure("Horizontal.TScale", background="#121212")
        self.style.configure("TCheckbutton", background="#121212", foreground="white", font=("Segoe UI", 10))

        # Variables
        self.entropy_var = tk.StringVar(value="0.0000")
        self.anomaly_var = tk.StringVar(value="0.00")
        self.status_var = tk.StringVar(value="Initializing...")
        self.gpu_info_var = tk.StringVar(value="GPU: Detecting...")
        self.ram_info_var = tk.StringVar(value="RAM: Detecting...")
        self.sensitivity_label_var = tk.StringVar(value="Sensitivity Threshold: 5.00")
        
        self.sensitivity = 5.0
        self.running = True
        self.logging_enabled = tk.BooleanVar(value=False)
        self.history = deque(maxlen=100)
        self.attractor_history = deque(maxlen=50)
        
        # Hardware Init
        self.init_gpu()
        self.init_ram_buffer()

        # UI Components
        self.create_widgets()

        # Start Thread
        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()
        
        self.log_message("System Initialized. Quantum Field Scanning...", "info")

    def init_gpu(self):
        try:
            pynvml.nvmlInit()
            self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(self.gpu_handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            self.gpu_info_var.set(f"GPU: {name} (Thermal Entropy Active)")
            self.gpu_active = True
        except Exception as e:
            self.gpu_info_var.set(f"GPU: Error ({str(e)})")
            self.gpu_active = False

    def init_ram_buffer(self):
        try:
            self.ram_buffer = np.zeros(50 * 1024 * 1024, dtype=np.uint8)
            self.ram_info_var.set("RAM: 64GB System (Latency Jitter Active)")
        except:
            self.ram_info_var.set("RAM: Buffer Alloc Failed")
            self.ram_buffer = None

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#121212")
        header_frame.pack(fill="x", pady=10)
        tk.Label(header_frame, text="Quantum Anomaly Detector", bg="#121212", fg="#BB86FC", font=("Segoe UI", 24, "bold")).pack()
        tk.Label(header_frame, text="PRO EDITION v2.2", bg="#121212", fg="#FFD700", font=("Segoe UI", 10, "bold")).pack()

        # Main Content Area
        main_frame = tk.Frame(self.root, bg="#121212")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Column: Status, Metrics, Log
        left_col = tk.Frame(main_frame, bg="#121212", width=300)
        left_col.pack(side="left", fill="both", expand=False, padx=10)

        # Sensor Status Group
        sensor_group = ttk.LabelFrame(left_col, text="Hardware Sensors")
        sensor_group.pack(fill="x", pady=5, ipadx=10, ipady=5)
        
        tk.Label(sensor_group, textvariable=self.status_var, bg="#121212", fg="#03DAC5").pack(anchor="w")
        tk.Label(sensor_group, textvariable=self.gpu_info_var, bg="#121212", fg="#AAAAAA", font=("Consolas", 9)).pack(anchor="w")
        tk.Label(sensor_group, textvariable=self.ram_info_var, bg="#121212", fg="#AAAAAA", font=("Consolas", 9)).pack(anchor="w")

        # Metrics Group
        metrics_group = ttk.LabelFrame(left_col, text="Real-time Metrics")
        metrics_group.pack(fill="x", pady=10, ipadx=10, ipady=10)

        tk.Label(metrics_group, text="System Entropy", bg="#121212", fg="white").pack(anchor="w")
        tk.Label(metrics_group, textvariable=self.entropy_var, bg="#121212", fg="#00FF00", font=("Consolas", 20, "bold")).pack(anchor="w")
        
        tk.Label(metrics_group, text="Anomaly Score", bg="#121212", fg="white").pack(anchor="w", pady=(10, 0))
        tk.Label(metrics_group, textvariable=self.anomaly_var, bg="#121212", fg="#00FF00", font=("Consolas", 20, "bold")).pack(anchor="w")

        # Log Feed Group (New)
        log_group = ttk.LabelFrame(left_col, text="Event Log")
        log_group.pack(fill="both", expand=True, pady=10, ipadx=5, ipady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_group, bg="#000000", fg="#00FF00", font=("Consolas", 9), height=10)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("info", foreground="#00FF00")
        self.log_text.tag_config("alert", foreground="#FF0000")
        self.log_text.tag_config("warn", foreground="#FFA500")

        # Right Column: Visualization & Controls
        right_col = tk.Frame(main_frame, bg="#121212")
        right_col.pack(side="right", fill="both", expand=True, padx=10)

        # Graph
        self.canvas = tk.Canvas(right_col, bg="#000000", height=350, highlightthickness=1, highlightbackground="#333333")
        self.canvas.pack(fill="both", expand=True, pady=10)

        # Controls Group
        controls_group = ttk.LabelFrame(right_col, text="Controls & Tuning")
        controls_group.pack(fill="x", pady=10, ipadx=10, ipady=10)

        # Sensitivity Slider
        tk.Label(controls_group, textvariable=self.sensitivity_label_var, bg="#121212", fg="white").pack(anchor="w")
        self.slider = ttk.Scale(controls_group, from_=1.0, to=10.0, orient="horizontal", command=self.update_sensitivity)
        self.slider.set(5.0)
        self.slider.pack(fill="x", pady=5)

        # Buttons Row
        btn_frame = tk.Frame(controls_group, bg="#121212")
        btn_frame.pack(fill="x", pady=10)

        self.toggle_btn = ttk.Button(btn_frame, text="Pause Scanning", command=self.toggle_scanning)
        self.toggle_btn.pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Calibrate Zero Point", command=self.calibrate).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Help / Info", command=self.show_help).pack(side="right", padx=5)

        # Logging Checkbox
        ttk.Checkbutton(controls_group, text="Log Anomalies to CSV", variable=self.logging_enabled, onvalue=True, offvalue=False).pack(anchor="w", padx=5)

        # Alert Overlay (Hidden by default)
        self.alert_label = tk.Label(self.root, text="ANOMALY DETECTED", bg="#121212", fg="#FF0000", font=("Segoe UI", 36, "bold"))

    def log_message(self, message, tag="info"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, full_msg, tag)
        self.log_text.see(tk.END)

    def update_sensitivity(self, val):
        self.sensitivity = float(val)
        self.sensitivity_label_var.set(f"Sensitivity Threshold: {self.sensitivity:.2f}")

    def toggle_scanning(self):
        self.running = not self.running
        if self.running:
            self.toggle_btn.config(text="Pause Scanning")
            self.status_var.set("Scanning Quantum Field...")
            self.log_message("Scanning Resumed.", "info")
            if not self.thread.is_alive():
                self.thread = threading.Thread(target=self.update_loop, daemon=True)
                self.thread.start()
        else:
            self.toggle_btn.config(text="Resume Scanning")
            self.status_var.set("PAUSED")
            self.log_message("Scanning Paused.", "warn")

    def calibrate(self):
        self.attractor_history.clear()
        self.history.clear()
        self.canvas.delete("all")
        self.status_var.set("Calibrated Zero Point")
        self.log_message("Zero Point Calibrated.", "warn")

    def show_help(self):
        msg = (
            "Quantum Anomaly Detector v2.2\n\n"
            "Features:\n"
            "- GPU Thermal Entropy: Uses RTX 3050 Ti thermal noise.\n"
            "- RAM Jitter: Uses 64GB RAM access latency.\n"
            "- Attractor Analysis: Detects deviations in system state.\n\n"
            "Controls:\n"
            "- Sensitivity: Adjust trigger threshold.\n"
            "- Calibrate: Reset baseline if stuck in 'Anomaly'.\n"
            "- Log to CSV: Saves detections to 'anomalies.csv'."
        )
        messagebox.showinfo("About", msg)

    def log_anomaly_csv(self, deviation, vector):
        if not self.logging_enabled.get():
            return
        
        file_exists = os.path.isfile("anomalies.csv")
        with open("anomalies.csv", "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Deviation", "Vector"])
            writer.writerow([datetime.datetime.now(), deviation, str(vector)])

    # ... (Hardware methods) ...
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

    def update_attractor(self, vector):
        self.attractor_history.append(vector)
        n = len(self.attractor_history)
        dim = len(vector)
        centroid = [0] * dim
        for v in self.attractor_history:
            for i in range(dim):
                centroid[i] += v[i]
        centroid = [x / n for x in centroid]
        dist_sq = 0
        for i in range(dim):
            dist_sq += (vector[i] - centroid[i])**2
        return math.sqrt(dist_sq)

    def draw_waveform(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Grid Lines
        self.canvas.create_line(0, h/2, w, h/2, fill="#333333", dash=(2, 4))
        self.canvas.create_line(0, h*0.25, w, h*0.25, fill="#222222", dash=(2, 4))
        self.canvas.create_line(0, h*0.75, w, h*0.75, fill="#222222", dash=(2, 4))

        if len(self.history) < 2:
            return

        max_val = 20.0
        step = w / 100

        points = []
        for i, val in enumerate(self.history):
            x = i * step
            y = h - (min(val, max_val) / max_val) * h
            points.append(x)
            points.append(y)

        color = "#00FF00"
        if self.history[-1] > self.sensitivity:
            color = "#FF0000"

        self.canvas.create_line(points, fill=color, width=2)

    def update_loop(self):
        while True:
            if self.running:
                vector = self.get_system_vector()
                entropy = self.calculate_shannon_entropy(vector)
                deviation = self.update_attractor(vector)
                
                self.root.after(0, self.update_ui, entropy, deviation, vector)
            
            time.sleep(0.1)

    def update_ui(self, entropy, deviation, vector):
        self.entropy_var.set(f"{entropy:.4f}")
        self.anomaly_var.set(f"{deviation:.2f}")
        
        self.history.append(deviation)
        self.draw_waveform()

        if deviation > self.sensitivity:
            self.alert_label.place(relx=0.5, rely=0.5, anchor="center")
            self.anomaly_var.set(f"{deviation:.2f} !!!")
            
            # Log to GUI
            self.log_message(f"ANOMALY! Score: {deviation:.2f} > {self.sensitivity:.2f}", "alert")
            
            # Log to CSV
            self.log_anomaly_csv(deviation, vector)
        else:
            self.alert_label.place_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumDetectorApp(root)
    root.mainloop()
