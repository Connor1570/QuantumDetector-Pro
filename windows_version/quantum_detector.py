import tkinter as tk
from tkinter import ttk
import psutil
import time
import math
import random
import threading
from collections import deque
import numpy as np
import pynvml

class QuantumDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Anomaly Detector - PRO Edition")
        self.root.geometry("800x600")
        self.root.configure(bg="#121212")

        # Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", background="#121212", foreground="white", font=("Segoe UI", 12))
        self.style.configure("TButton", background="#333333", foreground="white", font=("Segoe UI", 10))
        self.style.configure("Horizontal.TScale", background="#121212")

        # Variables
        self.entropy_var = tk.StringVar(value="0.0000")
        self.anomaly_var = tk.StringVar(value="0.00")
        self.status_var = tk.StringVar(value="Initializing Hardware Sensors...")
        self.gpu_info_var = tk.StringVar(value="GPU: Detecting...")
        self.ram_info_var = tk.StringVar(value="RAM: Detecting...")
        
        self.sensitivity = 5.0
        self.running = True
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
        # Allocate 50MB buffer for jitter testing
        try:
            self.ram_buffer = np.zeros(50 * 1024 * 1024, dtype=np.uint8)
            self.ram_info_var.set("RAM: 64GB System (Latency Jitter Active)")
        except:
            self.ram_info_var.set("RAM: Buffer Alloc Failed")
            self.ram_buffer = None

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Quantum Anomaly Detector", bg="#121212", fg="#BB86FC", font=("Segoe UI", 22, "bold")).pack(pady=10)
        tk.Label(self.root, text="PRO EDITION - HARDWARE ACCELERATED", bg="#121212", fg="#FFD700", font=("Segoe UI", 10, "bold")).pack()
        tk.Label(self.root, textvariable=self.status_var, bg="#121212", fg="#03DAC5", font=("Segoe UI", 12)).pack(pady=5)

        # Hardware Stats
        hw_frame = tk.Frame(self.root, bg="#1E1E1E", padx=10, pady=5)
        hw_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(hw_frame, textvariable=self.gpu_info_var, bg="#1E1E1E", fg="#AAAAAA", font=("Consolas", 10)).pack(anchor="w")
        tk.Label(hw_frame, textvariable=self.ram_info_var, bg="#1E1E1E", fg="#AAAAAA", font=("Consolas", 10)).pack(anchor="w")

        # Canvas for Graph
        self.canvas = tk.Canvas(self.root, width=700, height=250, bg="#000000", highlightthickness=1, highlightbackground="#333333")
        self.canvas.pack(pady=20)

        # Metrics
        frame = tk.Frame(self.root, bg="#121212")
        frame.pack(pady=10)

        tk.Label(frame, text="System Entropy:", bg="#121212", fg="white").grid(row=0, column=0, padx=10)
        tk.Label(frame, textvariable=self.entropy_var, bg="#121212", fg="#00FF00", font=("Consolas", 24, "bold")).grid(row=0, column=1, padx=10)

        tk.Label(frame, text="Anomaly Score:", bg="#121212", fg="white").grid(row=1, column=0, padx=10)
        tk.Label(frame, textvariable=self.anomaly_var, bg="#121212", fg="#00FF00", font=("Consolas", 24, "bold")).grid(row=1, column=1, padx=10)

        # Controls
        control_frame = tk.Frame(self.root, bg="#121212")
        control_frame.pack(pady=20, fill="x", padx=50)

        tk.Label(control_frame, text="Sensitivity", bg="#121212", fg="white").pack(anchor="w")
        self.slider = ttk.Scale(control_frame, from_=1.0, to=10.0, orient="horizontal", command=self.update_sensitivity)
        self.slider.set(5.0)
        self.slider.pack(fill="x", pady=5)

        ttk.Button(self.root, text="Calibrate Zero Point", command=self.calibrate).pack(pady=10)

        # Alert Label
        self.alert_label = tk.Label(self.root, text="ANOMALY DETECTED", bg="#121212", fg="#FF0000", font=("Segoe UI", 32, "bold"))

    def update_sensitivity(self, val):
        self.sensitivity = float(val)

    def calibrate(self):
        self.attractor_history.clear()
        self.history.clear()
        self.canvas.delete("all")

    def get_gpu_entropy(self):
        if not self.gpu_active:
            return 0, 0
        try:
            temp = pynvml.nvmlDeviceGetTemperature(self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle) # in milliwatts
            return temp, power
        except:
            return 0, 0

    def get_ram_jitter(self):
        if self.ram_buffer is None:
            return 0
        
        # Measure time to access random indices
        idx = np.random.randint(0, len(self.ram_buffer), 1000)
        t0 = time.perf_counter_ns()
        _ = self.ram_buffer[idx] # Force read
        t1 = time.perf_counter_ns()
        return (t1 - t0) # Jitter in nanoseconds

    def get_system_vector(self):
        # 1. CPU & RAM Load
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        
        # 2. GPU Thermal/Power
        gpu_temp, gpu_power = self.get_gpu_entropy()
        
        # 3. RAM Access Jitter
        ram_jitter = self.get_ram_jitter()
        
        # 4. Time Jitter
        time_jitter = (time.perf_counter() * 1000000) % 100
        
        return [cpu, ram, gpu_temp, gpu_power / 1000.0, ram_jitter / 1000.0, time_jitter]

    def calculate_shannon_entropy(self, data):
        entropy = 0
        for x in data:
            if x > 0:
                # Normalize roughly
                val = (x % 100) / 100.0
                if val > 0:
                    entropy -= val * math.log(val)
        return abs(entropy)

    def update_attractor(self, vector):
        self.attractor_history.append(vector)
        
        # Calculate Centroid
        n = len(self.attractor_history)
        dim = len(vector)
        centroid = [0] * dim
        
        for v in self.attractor_history:
            for i in range(dim):
                centroid[i] += v[i]
        
        centroid = [x / n for x in centroid]
        
        # Deviation (Euclidean Distance)
        dist_sq = 0
        for i in range(dim):
            dist_sq += (vector[i] - centroid[i])**2
            
        return math.sqrt(dist_sq)

    def draw_waveform(self):
        self.canvas.delete("all")
        if len(self.history) < 2:
            return

        w = 700
        h = 250
        max_val = 20.0 # Higher scale for more metrics
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
        while self.running:
            # 1. Get Data
            vector = self.get_system_vector()
            
            # 2. Entropy
            entropy = self.calculate_shannon_entropy(vector)
            
            # 3. Attractor
            deviation = self.update_attractor(vector)
            
            # 4. Update UI
            self.root.after(0, self.update_ui, entropy, deviation)
            
            time.sleep(0.1)

    def update_ui(self, entropy, deviation):
        self.entropy_var.set(f"{entropy:.4f}")
        self.anomaly_var.set(f"{deviation:.2f}")
        self.status_var.set("Scanning Quantum Field (GPU+RAM Active)...")
        
        self.history.append(deviation)
        self.draw_waveform()

        if deviation > self.sensitivity:
            self.alert_label.place(relx=0.5, rely=0.85, anchor="center")
            self.anomaly_var.set(f"{deviation:.2f} !!!")
        else:
            self.alert_label.place_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumDetectorApp(root)
    root.mainloop()
