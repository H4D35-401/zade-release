import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import time
import math
import random
import platform
import psutil
from secure_io import load_secure_config, save_secure_config
import voice_engine

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
            relief="flat", borderwidth=1, highlightthickness=0,
            activebackground=self.active_bg, activeforeground=self.active_fg,
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
        self.root.title(f"ZADE IGNITE | UNIVERSAL HUD v6.0 [{platform.system()}]")
        self.root.geometry("1100x950")
        self.root.configure(bg='#020205')
        
        self.colors = {
            "bg": "#020205", "module_bg": "#0a0a12", "border": "#1a1a2b",
            "accent": "#00f3ff", "warning": "#ffb700", "danger": "#ff3344",
            "text_dim": "#556677", "text_bright": "#ffffff", "grid": "#0d111a"
        }

        self.red_alert = False
        self.scan_y = 0
        self.viz_data = [random.randint(5, 40) for _ in range(50)]
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        self.config = self.load_config_data()
        
        self.create_widgets()
        self.animate()
        
    def setup_styles(self):
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["accent"], font=("Courier", 10))
        self.style.configure("TMenubutton", background="#0a0a20", foreground=self.colors["accent"])
        
    def load_config_data(self):
        config = load_secure_config(CONFIG_PATH)
        return config if config else {
            "location": "Global Node",
            "startup_volume": 80,
            "tts_response": "Universal link established.",
            "ai_engine": "mistral",
            "MISTRAL_API_KEY": "",
            "OPENAI_API_KEY": "",
            "GEMINI_API_KEY": "",
            "voice_id": "en_US-ChristopherNeural",
            "speech_rate": "+15%",
            "voice_pitch": "-5Hz",
            "apps": []
        }

    def save_config(self):
        try:
            self.config["location"] = self.location_var.get()
            self.config["startup_volume"] = int(self.volume_var.get())
            self.config["tts_response"] = self.tts_var.get()
            self.config["ai_engine"] = self.ai_engine_var.get()
            self.config["MISTRAL_API_KEY"] = self.mistral_key_var.get()
            self.config["OPENAI_API_KEY"] = self.openai_key_var.get()
            self.config["GEMINI_API_KEY"] = self.gemini_key_var.get()
            self.config["voice_id"] = self.voice_var.get()
            self.config["speech_rate"] = self.rate_var.get()
            self.config["voice_pitch"] = self.pitch_var.get()
            
            apps_text = self.apps_text.get("1.0", tk.END).strip()
            self.config["apps"] = [app.strip() for app in apps_text.split("\n") if app.strip()]

            save_secure_config(CONFIG_PATH, self.config)
            self.update_status("UNIVERSAL SYNC COMPLETE", self.colors["accent"])
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
        center_x = 550 # Default center
        # Container for scrollable canvas
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.main_frame, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.root.bind("<Configure>", self.on_resize)
        # Mousewheel scrolling
        self.root.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.root.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.root.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        # 1. Header
        header = self.create_tactical_module("SYSTEM COMMAND", 700, 120)
        self.title_label = tk.Label(header, text="ZADE IGNITE", font=("Courier", 38, "bold"), fg=self.colors["accent"], bg=self.colors["module_bg"])
        self.title_label.pack(pady=(10, 0))
        self.status_label = tk.Label(header, text="STATE: STANDBY", font=("Courier", 10), fg=self.colors["text_dim"], bg=self.colors["module_bg"])
        self.status_label.pack()

        # 2. Protocol Module (Left)
        proto = self.create_tactical_module("CORE_PROTOCOLS", 450, 220)
        self.location_var = self.create_field(proto, "GEO_LOC", self.config.get("location", ""))
        self.volume_var = self.create_field(proto, "GAIN", self.config.get("startup_volume", 80), spin=True)
        self.tts_var = self.create_field(proto, "GREET", self.config.get("tts_response", ""))

        # 3. Universal AI Module (Center Right)
        ai_mod = self.create_tactical_module("NEURAL_ENGINE", 450, 320)
        tk.Label(ai_mod, text="> ACTIVE_ENGINE:", font=("Courier", 8), fg=self.colors["text_dim"], bg=self.colors["module_bg"]).pack(anchor=tk.W, padx=10)
        self.ai_engine_var = tk.StringVar(value=self.config.get("ai_engine", "mistral"))
        engine_opt = ttk.OptionMenu(ai_mod, self.ai_engine_var, self.ai_engine_var.get(), "mistral", "openai", "gemini")
        engine_opt.pack(fill=tk.X, padx=10, pady=5)
        
        self.mistral_key_var = self.create_field(ai_mod, "MISTRAL_ID", self.config.get("MISTRAL_API_KEY", ""), show="*")
        self.openai_key_var = self.create_field(ai_mod, "OPENAI_ID", self.config.get("OPENAI_API_KEY", ""), show="*")
        self.gemini_key_var = self.create_field(ai_mod, "GEMINI_ID", self.config.get("GEMINI_API_KEY", ""), show="*")

        # 4. Voice Profiles (Bottom Left)
        voice_mod = self.create_tactical_module("VOICE_PROFILES", 450, 250)
        tk.Label(voice_mod, text="> SELECT_PROFILE:", font=("Courier", 8), fg=self.colors["text_dim"], bg=self.colors["module_bg"]).pack(anchor=tk.W, padx=10)
        self.voice_var = tk.StringVar(value=self.config.get("voice_id", "en_US-ChristopherNeural"))
        
        # Simplified Voice List for v6.0
        voices = [
            "en-US-ChristopherNeural", "en-US-GuyNeural", "en-US-JennyNeural",
            "en-GB-RyanNeural", "en-GB-SoniaNeural", "en-AU-WilliamNeural",
            "hi-IN-MadhurNeural", "hi-IN-SwaraNeural"
        ]
        voice_opt = ttk.OptionMenu(voice_mod, self.voice_var, self.voice_var.get(), *voices)
        voice_opt.pack(fill=tk.X, padx=10, pady=5)
        
        self.rate_var = self.create_field(voice_mod, "TEMPO", self.config.get("speech_rate", ""))
        self.pitch_var = self.create_field(voice_mod, "PITCH", self.config.get("voice_pitch", ""))

        # 5. Apps (Middle Right)
        app_mod = self.create_tactical_module("AUTO_SEQUENCE", 450, 200)
        self.apps_text = tk.Text(app_mod, height=5, bg="#050510", fg="#ffffff", font=("Courier", 10), borderwidth=0)
        self.apps_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.apps_text.insert("1.0", "\n".join(self.config.get("apps", [])))

        # 6. Telemetry (Bottom Center)
        tele_mod = self.create_tactical_module("SYSTEM_TELEMETRY", 900, 150)
        self.tele_canvas = tk.Canvas(tele_mod, bg="#050510", height=80, highlightthickness=0)
        self.tele_canvas.pack(fill=tk.X, padx=10, pady=5)
        
        # Canvas Windows
        self.header_win = self.canvas.create_window( center_x, 80, window=header, width=700)
        self.proto_win = self.canvas.create_window(280, 280, window=proto, width=450)
        self.ai_win = self.canvas.create_window(820, 330, window=ai_mod, width=450)
        self.voice_win = self.canvas.create_window(280, 550, window=voice_mod, width=450)
        self.app_win = self.canvas.create_window(820, 600, window=app_mod, width=450)
        self.tele_win = self.canvas.create_window(550, 800, window=tele_mod, width=900)

        # Footer Actions
        self.alert_btn = TacticalButton(self.root, text="RED_ALERT", command=self.toggle_red_alert, bg="#150505", fg=self.colors["danger"], height=2)
        save_btn = TacticalButton(self.root, text="SAVE_PROTOCOLS", command=self.save_config, bg="#051510", fg="#00ff88", height=2)
        ignite_btn = TacticalButton(self.root, text="INIT_IGNITION", command=self.launch_main, bg="#200505", fg="#ff3344", height=2)
        
        self.alert_win = self.canvas.create_window(550, 950, window=self.alert_btn, width=200)
        self.save_win = self.canvas.create_window(350, 1020, window=save_btn, width=300)
        self.ignite_win = self.canvas.create_window(750, 1020, window=ignite_btn, width=300)

    def create_tactical_module(self, title, width, height):
        f = tk.Frame(self.canvas, bg=self.colors["module_bg"], highlightthickness=1, highlightbackground=self.colors["border"])
        tk.Label(f, text=f" {title} ", font=("Courier", 8, "bold"), fg=self.colors["accent"], bg=self.colors["bg"]).pack(anchor=tk.W, padx=10, pady=(5, 0))
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
            
            # Adaptive Threshold
            vertical_mode = w < 950
            side_margin = 40
            gap = 25
            center_x = w / 2

            if vertical_mode:
                # VERTICAL STACK MODE
                module_w = min(800, w - (side_margin * 2))
                
                # Dynamic Y-Offsets
                y_pos = 80 # Header
                self.canvas.coords(self.header_win, center_x, y_pos)
                self.canvas.itemconfig(self.header_win, width=module_w)
                
                y_pos += 140 # Proto
                self.canvas.coords(self.proto_win, center_x, y_pos)
                self.canvas.itemconfig(self.proto_win, width=module_w)
                
                y_pos += 210 # AI
                self.canvas.coords(self.ai_win, center_x, y_pos)
                self.canvas.itemconfig(self.ai_win, width=module_w)
                
                y_pos += 300 # Voice
                self.canvas.coords(self.voice_win, center_x, y_pos)
                self.canvas.itemconfig(self.voice_win, width=module_w)
                
                y_pos += 220 # Apps
                self.canvas.coords(self.app_win, center_x, y_pos)
                self.canvas.itemconfig(self.app_win, width=module_w)
                
                y_pos += 150 # Telemetry
                self.canvas.coords(self.tele_win, center_x, y_pos)
                self.canvas.itemconfig(self.tele_win, width=module_w)
                
                y_pos += 120 # Alert
                self.canvas.coords(self.alert_win, center_x, y_pos)
                
                y_pos += 80 # Footer Buttons
                btn_w = (module_w - gap) // 2
                self.canvas.itemconfig(self.save_win, width=btn_w)
                self.canvas.coords(self.save_win, center_x - (btn_w/2) - (gap/2), y_pos)
                
                self.canvas.itemconfig(self.ignite_win, width=btn_w)
                self.canvas.coords(self.ignite_win, center_x + (btn_w/2) + (gap/2), y_pos)
                
                final_y = y_pos + 100
            else:
                # 2-COLUMN TACTICAL HUD
                module_w = (w - (side_margin * 2) - gap) // 2
                left_x = side_margin + (module_w / 2)
                right_x = w - side_margin - (module_w / 2)
                
                header_w = min(1000, w - (side_margin * 2))
                self.canvas.itemconfig(self.header_win, width=header_w)
                self.canvas.coords(self.header_win, center_x, 80)
                
                self.canvas.itemconfig(self.proto_win, width=module_w)
                self.canvas.coords(self.proto_win, left_x, 280)
                
                self.canvas.itemconfig(self.voice_win, width=module_w)
                self.canvas.coords(self.voice_win, left_x, 550)
                
                self.canvas.itemconfig(self.ai_win, width=module_w)
                self.canvas.coords(self.ai_win, right_x, 330)
                
                self.canvas.itemconfig(self.app_win, width=module_w)
                self.canvas.coords(self.app_win, right_x, 600)
                
                tele_w = w - (side_margin * 2)
                self.canvas.itemconfig(self.tele_win, width=tele_w)
                self.canvas.coords(self.tele_win, center_x, 800)

                self.canvas.coords(self.alert_win, center_x, 950)
                btn_w = min(300, (w - side_margin*2 - gap) // 2)
                self.canvas.itemconfig(self.save_win, width=btn_w)
                self.canvas.coords(self.save_win, center_x - (btn_w/2) - (gap/2), 1020)
                
                self.canvas.itemconfig(self.ignite_win, width=btn_w)
                self.canvas.coords(self.ignite_win, center_x + (btn_w/2) + (gap/2), 1020)
                
                final_y = 1100

            # Update Scroll Region
            self.canvas.config(scrollregion=(0, 0, w, final_y))
            self.draw_grid(final_y)

    def draw_grid(self, height=None):
        self.canvas.delete("grid")
        w = self.root.winfo_width()
        h = height if height else self.root.winfo_height()
        gap = 50
        for x in range(0, w, gap): self.canvas.create_line(x, 0, x, h, fill=self.colors["grid"], tags="grid")
        for y in range(0, h, gap): self.canvas.create_line(0, y, w, y, fill=self.colors["grid"], tags="grid")

    def animate(self):
        self.canvas.delete("fx")
        w, h = self.root.winfo_width(), self.root.winfo_height()
        
        # 0. Vocal Reactivity
        v_lvl = voice_engine.get_vocal_level()
        pulse_w = 1 + (v_lvl * 5)
        accent_pulse = self.colors["accent"] if v_lvl < 0.3 else self.colors["warning"]
        
        # 1. Scanning Line
        self.scan_y = (self.scan_y + (3 + v_lvl*20)) % 1200 
        self.canvas.create_line(0, self.scan_y, w, self.scan_y, fill=accent_pulse, width=pulse_w, tags="fx", stipple="gray25")
        
        # 2. Voice Visualization (Neural Flux Reactive)
        pts = []
        for i, v in enumerate(self.viz_data):
            x = (w / len(self.viz_data)) * i
            target_v = max(5, v_lvl * 400 * random.random()) if v_lvl > 0.1 else random.randint(5, 40)
            self.viz_data[i] = self.viz_data[i] * 0.7 + target_v * 0.3 # Smooth transition
            pts.extend([x, 1000 - self.viz_data[i]])
        if len(pts) > 4: self.canvas.create_line(pts, fill=accent_pulse, width=pulse_w, smooth=True, tags="fx")
        
        # 3. Telemetry Visualizers
        self.update_telemetry()

        # 4. Red Alert Shaker
        if self.red_alert:
            alpha = (math.sin(time.time()*10) + 1) / 2
            self.canvas.create_rectangle(0,0,w,1200, outline=self.colors["danger"], width=10*alpha, tags="fx")
            self.canvas.create_text(w/2, 100, text="CRITICAL STATUS OVERRIDE", font=("Courier", 20, "bold"), fill=self.colors["danger"], tags="fx")
            dx, dy = random.randint(-2, 2), random.randint(-2, 2)
            self.canvas.move("all", dx, dy)
            self.root.after(50, lambda: self.canvas.move("all", -dx, -dy))

        self.root.after(40, self.animate)

    def update_telemetry(self):
        self.tele_canvas.delete("bar")
        w = self.tele_canvas.winfo_width()
        if w < 100: return # Skip if not initialized
        
        stats = [
            ("CPU", psutil.cpu_percent()),
            ("RAM", psutil.virtual_memory().percent),
            ("BAT", psutil.sensors_battery().percent if psutil.sensors_battery() else 100)
        ]
        
        bar_w = (w - 60) // 3
        for i, (label, val) in enumerate(stats):
            x = 20 + i * (bar_w + 10)
            # Label
            self.tele_canvas.create_text(x + 5, 15, text=f"{label}: {int(val)}%", fill=self.colors["accent"], font=("Courier", 8), anchor=tk.NW, tags="bar")
            # Bg Bar
            self.tele_canvas.create_rectangle(x, 35, x + bar_w, 55, outline=self.colors["border"], fill="#050510", tags="bar")
            # Fill Bar
            fill_color = self.colors["accent"] if val < 80 else (self.colors["warning"] if val < 90 else self.colors["danger"])
            self.tele_canvas.create_rectangle(x, 35, x + (bar_w * val / 100), 55, fill=fill_color, outline="", tags="bar")

if __name__ == "__main__":
    root = tk.Tk()
    ConfigGUI(root)
    root.mainloop()
