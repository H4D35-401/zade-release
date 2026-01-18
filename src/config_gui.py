import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import time
import math
import random
from secure_io import load_secure_config, save_secure_config

# Configuration Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

class TacticalButton(tk.Button):
    def __init__(self, master, **kwargs):
        self.active_bg = kwargs.pop('active_bg', '#00f3ff')
        self.active_fg = kwargs.pop('active_fg', '#000000')
        self.default_bg = kwargs.get('bg', '#0a0a1a')
        self.default_fg = kwargs.get('fg', '#00f3ff')
        
        super().__init__(master, **kwargs)
        self.config(
            relief="flat",
            borderwidth=1,
            highlightthickness=0,
            activebackground=self.active_bg,
            activeforeground=self.active_fg,
            font=("Courier", 10, "bold")
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self.active_bg
        self['foreground'] = self.active_fg

    def on_leave(self, e):
        self['background'] = self.default_bg
        self['foreground'] = self.default_fg

class ConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ZADE IGNITE | QUANTUM TACTICAL HUD v5.0")
        self.root.geometry("1000x900")
        self.root.configure(bg='#020205')
        
        self.colors = {
            "bg": "#020205",
            "module_bg": "#0a0a12",
            "border": "#1a1a2b",
            "accent": "#00f3ff", 
            "warning": "#ffb700", 
            "danger": "#ff3344",
            "text_dim": "#556677",
            "text_bright": "#ffffff",
            "grid": "#0d111a"
        }

        self.red_alert = False
        self.shake_offset = (0, 0)
        self.scan_y = 0
        self.viz_data = [random.randint(5, 40) for _ in range(50)]
        self.pulse_alpha = 0

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        self.config = self.load_config_data()
        
        # UI Elements storage for canvas placement
        self.modules = []
        
        self.create_widgets()
        self.animate()
        
    def setup_styles(self):
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["accent"], font=("Courier", 10))
        
    def load_config_data(self):
        config = load_secure_config(CONFIG_PATH)
        return config if config else {
            "location": "Global Node",
            "startup_volume": 80,
            "tts_response": "Tactical link established.",
            "music_path": "",
            "MISTRAL_API_KEY": "",
            "voice_id": "en_US-ChristopherNeural",
            "speech_rate": "+15%",
            "voice_pitch": "-5Hz",
            "apps": ["google-chrome", "spotify"]
        }

    def save_config(self):
        try:
            self.config["location"] = self.location_var.get()
            self.config["startup_volume"] = int(self.volume_var.get())
            self.config["tts_response"] = self.tts_var.get()
            self.config["music_path"] = self.music_var.get()
            self.config["MISTRAL_API_KEY"] = self.api_key_var.get()
            self.config["voice_id"] = self.voice_var.get()
            self.config["speech_rate"] = self.rate_var.get()
            self.config["voice_pitch"] = self.pitch_var.get()
            
            apps_text = self.apps_text.get("1.0", tk.END).strip()
            self.config["apps"] = [app.strip() for app in apps_text.split("\n") if app.strip()]

            save_secure_config(CONFIG_PATH, self.config)
            self.update_status("QUANTUM ENCRYPTION SYNCED", self.colors["accent"])
        except Exception as e:
            messagebox.showerror("SYNC ERROR", f"Protocol failure: {e}")

    def update_status(self, text, color):
        self.status_label.config(text=f"STATE: {text}", fg=color)
        if not self.red_alert:
            self.root.after(3000, lambda: self.status_label.config(text="STATE: STANDBY", fg=self.colors["text_dim"]))

    def toggle_red_alert(self):
        self.red_alert = not self.red_alert
        if self.red_alert:
            self.colors["accent"] = self.colors["danger"]
            self.colors["grid"] = "#200505"
            self.update_status("CRITICAL_ALERT", self.colors["danger"])
            self.alert_btn.config(text="DISARM_ALERT", bg=self.colors["danger"], fg="#ffffff")
        else:
            self.colors["accent"] = "#00f3ff"
            self.colors["grid"] = "#0d111a"
            self.update_status("STANDBY", self.colors["text_dim"])
            self.alert_btn.config(text="RED_ALERT", bg="#150505", fg=self.colors["danger"])
        
        # Propagate color change to static elements
        self.title_label.config(fg=self.colors["accent"])
        self.draw_grid()

    def launch_main(self):
        self.save_config()
        script_path = os.path.join(BASE_DIR, "main.py")
        try:
            python_exe = os.path.join(BASE_DIR, "venv", "bin", "python3")
            if not os.path.exists(python_exe): python_exe = "python3"
            subprocess.Popen([python_exe, script_path], cwd=BASE_DIR)
            self.update_status("IGNITION_LIVE", "#00ff88")
        except Exception as e:
            messagebox.showerror("FAILURE", f"Could not ignite: {e}")

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.bind("<Configure>", self.on_resize)

        # 1. Header Module
        header = self.create_tactical_module("SYSTEM COMMAND", width=600, height=120)
        self.title_label = tk.Label(header, text="ZADE IGNITE", font=("Courier", 38, "bold"), fg=self.colors["accent"], bg=self.colors["module_bg"])
        self.title_label.pack(pady=(10, 0))
        self.status_label = tk.Label(header, text="STATE: STANDBY", font=("Courier", 10), fg=self.colors["text_dim"], bg=self.colors["module_bg"])
        self.status_label.pack()

        # 2. Protocol Module (Left)
        proto = self.create_tactical_module("CORE_PROTOCOLS", width=420, height=280)
        self.location_var = self.create_field(proto, "GEO_LOC", self.config.get("location", ""))
        self.volume_var = self.create_field(proto, "GAIN", self.config.get("startup_volume", 80), spin=True)
        self.tts_var = self.create_field(proto, "GREET", self.config.get("tts_response", ""))
        self.music_var = self.create_field(proto, "SONG", self.config.get("music_path", ""))

        # 3. Neural Module (Bottom Left)
        neural = self.create_tactical_module("NEURAL_LINK", width=420, height=150)
        self.api_key_var = self.create_field(neural, "MISTRAL_ID", self.config.get("MISTRAL_API_KEY", ""), show="*")
        TacticalButton(neural, text="VERIFY_LINK", command=lambda: self.update_status("POLLING...", "#ffb700"), bg="#10101a", width=15).pack(pady=10)

        # 4. Seq Module (Right)
        seq = self.create_tactical_module("AUTO_SEQUENCE", width=420, height=250)
        self.apps_text = tk.Text(seq, height=8, bg="#050510", fg="#ffffff", font=("Courier", 10), borderwidth=0, highlightthickness=1, highlightbackground=self.colors["border"])
        self.apps_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.apps_text.insert("1.0", "\n".join(self.config.get("apps", [])))

        # 5. Synth Module (Bottom Right)
        synth = self.create_tactical_module("VOICE_SYNTH", width=420, height=180)
        self.voice_var = self.create_field(synth, "ID", self.config.get("voice_id", ""))
        self.rate_var = self.create_field(synth, "RATE", self.config.get("speech_rate", ""))
        self.pitch_var = self.create_field(synth, "PITCH", self.config.get("voice_pitch", ""))

        # 6. Controls
        self.alert_btn = TacticalButton(self.root, text="RED_ALERT", command=self.toggle_red_alert, bg="#150505", fg=self.colors["danger"], height=2)
        save_btn = TacticalButton(self.root, text="SAVE_PROTOCOLS", command=self.save_config, bg="#051510", fg="#00ff88", height=2)
        ignite_btn = TacticalButton(self.root, text="INIT_IGNITION", command=self.launch_main, bg="#200505", fg="#ff3344", height=2)
        
        # Store as canvas items for dynamic layout
        self.header_win = self.canvas.create_window(500, 80, window=header, width=600)
        self.proto_win = self.canvas.create_window(260, 310, window=proto, width=420)
        self.neural_win = self.canvas.create_window(260, 540, window=neural, width=420)
        self.seq_win = self.canvas.create_window(740, 295, window=seq, width=420)
        self.synth_win = self.canvas.create_window(740, 525, window=synth, width=420)
        
        self.alert_win = self.canvas.create_window(500, 680, window=self.alert_btn, width=200)
        self.save_win = self.canvas.create_window(350, 750, window=save_btn, width=300)
        self.ignite_win = self.canvas.create_window(650, 750, window=ignite_btn, width=300)

    def create_tactical_module(self, title, width, height):
        f = tk.Frame(self.canvas, bg=self.colors["module_bg"], highlightthickness=1, highlightbackground=self.colors["border"])
        tk.Label(f, text=f" {title} ", font=("Courier", 8, "bold"), fg=self.colors["accent"], bg=self.colors["bg"]).pack(anchor=tk.W, padx=10, pady=(5, 0))
        # Decorative brackets
        tk.Label(f, text="⌜", font=("Courier", 14), fg=self.colors["accent"], bg=self.colors["module_bg"]).place(x=0, y=0)
        tk.Label(f, text="⌝", font=("Courier", 14), fg=self.colors["accent"], bg=self.colors["module_bg"]).place(relx=1.0, x=-14, y=0)
        tk.Label(f, text="⌞", font=("Courier", 14), fg=self.colors["accent"], bg=self.colors["module_bg"]).place(x=0, rely=1.0, y=-22)
        tk.Label(f, text="⌟", font=("Courier", 14), fg=self.colors["accent"], bg=self.colors["module_bg"]).place(relx=1.0, x=-14, rely=1.0, y=-22)
        return f

    def create_field(self, parent, label, default, show=None, spin=False):
        f = tk.Frame(parent, bg=self.colors["module_bg"], padx=10, pady=2)
        f.pack(fill=tk.X)
        tk.Label(f, text=f"> {label}:", font=("Courier", 8), fg=self.colors["text_dim"], bg=self.colors["module_bg"]).pack(anchor=tk.W)
        var = tk.StringVar(value=str(default))
        cfg = {"font": ("Courier", 10), "bg": "#050510", "fg": "#f0f0f0", "relief": "flat", "insertbackground": "#00f3ff"}
        comp = tk.Spinbox(f, from_=0, to=100, textvariable=var, **cfg) if spin else tk.Entry(f, textvariable=var, **cfg)
        if show: comp.config(show=show)
        comp.pack(fill=tk.X, pady=(0, 5))
        return var

    def on_resize(self, event):
        if event.widget == self.root:
            w, h = event.width, event.height
            self.canvas.coords(self.header_win, w/2, 80)
            self.canvas.coords(self.proto_win, w/2 - 240, 310)
            self.canvas.coords(self.neural_win, w/2 - 240, 540)
            self.canvas.coords(self.seq_win, w/2 + 240, 295)
            self.canvas.coords(self.synth_win, w/2 + 240, 525)
            self.canvas.coords(self.alert_win, w/2, 680)
            self.canvas.coords(self.save_win, w/2 - 160, 750)
            self.canvas.coords(self.ignite_win, w/2 + 160, 750)
            self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("grid")
        w, h = self.root.winfo_width(), self.root.winfo_height()
        gap = 50
        for x in range(0, w, gap):
            self.canvas.create_line(x, 0, x, h, fill=self.colors["grid"], tags="grid")
        for y in range(0, h, gap):
            self.canvas.create_line(0, y, w, y, fill=self.colors["grid"], tags="grid")

    def animate(self):
        self.canvas.delete("fx")
        w, h = self.root.winfo_width(), self.root.winfo_height()
        
        # 1. Scanning Line
        self.scan_y = (self.scan_y + 3) % h
        self.canvas.create_line(0, self.scan_y, w, self.scan_y, fill=self.colors["accent"], width=1, tags="fx", stipple="gray25")
        
        # 2. Voice Wave (Neural Flux)
        pts = []
        for i, v in enumerate(self.viz_data):
            x = (w / len(self.viz_data)) * i
            self.viz_data[i] = max(2, min(80, v + random.randint(-10, 10)))
            pts.extend([x, h - 10 - self.viz_data[i]])
        if len(pts) > 4:
            self.canvas.create_line(pts, fill=self.colors["accent"], width=2, smooth=True, tags="fx")

        # 3. Red Alert Shaker
        if self.red_alert:
            self.pulse_alpha = (math.sin(time.time()*10) + 1) / 2
            self.canvas.create_rectangle(0,0,w,h, outline=self.colors["danger"], width=10*self.pulse_alpha, tags="fx")
            self.canvas.create_text(w/2, h-50, text="CRITICAL STATUS OVERRIDE", font=("Courier", 20, "bold"), fill=self.colors["danger"], tags="fx")
            # Subtle shake
            dx, dy = random.randint(-2, 2), random.randint(-2, 2)
            self.canvas.move("all", dx, dy)
            self.root.after(50, lambda: self.canvas.move("all", -dx, -dy))

        self.root.after(40, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    ConfigGUI(root)
    root.mainloop()
