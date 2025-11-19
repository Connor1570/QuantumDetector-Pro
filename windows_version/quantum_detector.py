import tkinter as tk
from tkinter import ttk
import psutil
import time
import math
import random
import threading
from collections import deque

class QuantumDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Anomaly Detector")
        self.root.geometry("600x500")
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
        self.status_var = tk.StringVar(value="Scanning Quantum Field...")
        self.sensitivity = 5.0
        self.running = True
        self.history = deque(maxlen=100)
        self.attractor_history = deque(maxlen=50)
        self.centroid = [0, 0, 0]

        # UI Components
        self.create_widgets()

        # Start Thread
        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="Quantum Anomaly Detector", bg="#121212", fg="#BB86FC", font=("Segoe UI", 18, "bold")).pack(pady=10)
        tk.Label(self.root, textvariable=self.status_var, bg="#121212", fg="#03DAC5", font=("Segoe UI", 12)).pack()

        # Canvas for Graph
        self.canvas = tk.Canvas(self.root, width=500, height=200, bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Metrics
        frame = tk.Frame(self.root, bg="#121212")
        frame.pack(pady=10)

        tk.Label(frame, text="Entropy:", bg="#121212", fg="white").grid(row=0, column=0, padx=10)
        tk.Label(frame, textvariable=self.entropy_var, bg="#121212", fg="#00FF00", font=("Consolas", 20, "bold")).grid(row=0, column=1, padx=10)

        tk.Label(frame, text="Anomaly Score:", bg="#121212", fg="white").grid(row=1, column=0, padx=10)
        tk.Label(frame, textvariable=self.anomaly_var, bg="#121212", fg="#00FF00", font=("Consolas", 20, "bold")).grid(row=1, column=1, padx=10)

        # Controls
        control_frame = tk.Frame(self.root, bg="#121212")
        control_frame.pack(pady=20, fill="x", padx=50)

        tk.Label(control_frame, text="Sensitivity", bg="#121212", fg="white").pack(anchor="w")
        self.slider = ttk.Scale(control_frame, from_=1.0, to=10.0, orient="horizontal", command=self.update_sensitivity)
        self.slider.set(5.0)
        self.slider.pack(fill="x", pady=5)

        ttk.Button(self.root, text="Calibrate Zero Point", command=self.calibrate).pack(pady=10)

        # Alert Label
        self.alert_label = tk.Label(self.root, text="ANOMALY DETECTED", bg="#121212", fg="#FF0000", font=("Segoe UI", 24, "bold"))

    def update_sensitivity(self, val):
        self.sensitivity = float(val)

    def calibrate(self):
        self.attractor_history.clear()
        self.history.clear()
        self.canvas.delete("all")

    def get_system_entropy(self):
        # Combine CPU, RAM, and Time Jitter for "Quantum" noise
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        jitter = (time.perf_counter() * 1000000) % 100
        return [cpu, ram, jitter]

    def calculate_shannon_entropy(self, data):
        # Simplified entropy calculation
        entropy = 0
        for x in data:
            if x > 0:
                p = (x % 10) / 10.0 # Normalize to 0-1 roughly
                if p > 0:
                    entropy -= p * math.log(p)
        return abs(entropy)

    def update_attractor(self, vector):
        self.attractor_history.append(vector)
        
        # Calculate Centroid
        sum_x, sum_y, sum_z = 0, 0, 0
        for v in self.attractor_history:
            sum_x += v[0]
            sum_y += v[1]
            sum_z += v[2]
        
        n = len(self.attractor_history)
        cx, cy, cz = sum_x/n, sum_y/n, sum_z/n
        
        # Deviation
        dist = math.sqrt((vector[0]-cx)**2 + (vector[1]-cy)**2 + (vector[2]-cz)**2)
        return dist

    def draw_waveform(self):
        self.canvas.delete("all")
        if len(self.history) < 2:
            return

        w = 500
        h = 200
        max_val = 10.0
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
            vector = self.get_system_entropy()
            
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
        self.history.append(deviation)
        self.draw_waveform()

        if deviation > self.sensitivity:
            self.alert_label.place(relx=0.5, rely=0.9, anchor="center")
            self.anomaly_var.set(f"{deviation:.2f} !!!")
        else:
            self.alert_label.place_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuantumDetectorApp(root)
    root.mainloop()
