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
        self.root.title("ZADE IGNITE | ADVANCED TACTICAL HUD v4.0")
        self.root.geometry("850x950")
        self.root.configure(bg='#050505')
        
        # Cybernetic Palette
        self.colors = {
            "bg": "#050505",
            "module_bg": "#0a0a0c",
            "border": "#1a1a25",
            "accent": "#00f3ff", 
            "warning": "#ffb700", 
            "danger": "#ff3344",
            "text_dim": "#556677",
            "text_bright": "#ffffff",
            "grid": "#101520"
        }

        self.red_alert = False
        self.anim_offset = 0
        self.viz_data = [random.randint(0, 50) for _ in range(40)]
        self.scan_y = 0

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        self.config = self.load_config_data()
        self.current_width = 850
        self.current_height = 950
        self.create_widgets()
        self.animate()
        
    def setup_styles(self):
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["accent"], font=("Courier", 10))
        
    def load_config_data(self):
        config = load_secure_config(CONFIG_PATH)
        if config: return config
        
        return {
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

            # Secure Saving
            save_secure_config(CONFIG_PATH, self.config)
            
            self.update_status("PROTOCOLS SECURED", self.colors["accent"])
        except Exception as e:
            messagebox.showerror("SYNC ERROR", f"Encryption failure: {e}")

    def update_status(self, text, color):
        prefix = "SYS_STATUS: " if not self.red_alert else "ALERT_LEVEL: "
        self.status_label.config(text=f"{prefix}{text}", fg=color)
        if not self.red_alert:
            self.root.after(3000, lambda: self.status_label.config(text="SYS_STATUS: STANDBY", fg=self.colors["text_dim"]))

    def toggle_red_alert(self):
        self.red_alert = not self.red_alert
        if self.red_alert:
            self.colors["grid"] = "#300a0a"
            self.colors["accent"] = "#ff3344"
            self.update_status("CRITICAL", self.colors["danger"])
            self.alert_btn.config(text="DISARM_ALERT", fg=self.colors["text_bright"], bg=self.colors["danger"])
        else:
            self.colors["grid"] = "#101520"
            self.colors["accent"] = "#00f3ff"
            self.update_status("STANDBY", self.colors["text_dim"])
            self.alert_btn.config(text="RED_ALERT", fg=self.colors["danger"], bg="#200505")
        
        # Refresh all tactical module colors
        self.draw_grid()

    def test_api_key(self):
        key = self.api_key_var.get()
        if not key:
            messagebox.showwarning("AUTH MISSING", "No key detected.")
            return
        
        self.update_status("POLLING_NEURAL_NODE...", self.colors["warning"])
        
        def run_test():
            try:
                import requests
                headers = {"Authorization": f"Bearer {key}"}
                response = requests.get("https://api.mistral.ai/v1/models", headers=headers, timeout=5)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.update_status("LINK_ACTIVE", "#00ff88"))
                    self.root.after(0, lambda: messagebox.showinfo("LINK ACTIVE", "Neural connection confirmed."))
                else:
                    self.root.after(0, lambda: self.update_status("LINK_FAILED", self.colors["danger"]))
            except Exception as e:
                self.root.after(0, lambda: self.update_status("NODE_OFFLINE", self.colors["danger"]))

        threading.Thread(target=run_test, daemon=True).start()

    def launch_main(self):
        self.save_config()
        script_path = os.path.join(BASE_DIR, "main.py")
        try:
            python_exe = "python3"
            v1 = os.path.join(os.path.dirname(BASE_DIR), "venv", "bin", "python3")
            v2 = os.path.join(BASE_DIR, "venv", "bin", "python3")
            if os.path.exists(v1): python_exe = v1
            elif os.path.exists(v2): python_exe = v2
            
            subprocess.Popen([python_exe, script_path], cwd=BASE_DIR)
            self.update_status("IGNITION_LIVE", self.colors["text_bright"])
        except Exception as e:
            messagebox.showerror("FAILURE", f"Could not ignite: {e}")

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.main_container = tk.Frame(self.canvas, bg=self.colors["bg"])
        self.window_id = self.canvas.create_window(0, 0, window=self.main_container, anchor="nw")
        
        self.root.bind("<Configure>", self.on_resize)
        self.draw_grid()

        # Tactical Header
        header = self.create_tactical_module(self.main_container, "COMMAND_OVERVIEW")
        header.pack(fill=tk.X, pady=(20, 20), padx=40)
        
        tk.Label(header, text="ZADE IGNITE", font=("Courier", 34, "bold"), fg=self.colors["accent"], bg=self.colors["module_bg"]).pack(pady=(10, 0))
        tk.Label(header, text="ENCRYPTED NEURAL HUD [v4.0]", font=("Courier", 9), fg=self.colors["text_dim"], bg=self.colors["module_bg"]).pack()
        
        self.status_label = tk.Label(header, text="SYS_STATUS: STANDBY", font=("Courier", 10, "bold"), fg=self.colors["text_dim"], bg=self.colors["module_bg"])
        self.status_label.pack(pady=10)

        # Control Row
        control = tk.Frame(self.main_container, bg=self.colors["bg"])
        control.pack(fill=tk.X, padx=40, pady=(0, 10))
        
        self.alert_btn = TacticalButton(control, text="RED_ALERT", command=self.toggle_red_alert,
                                        bg="#200505", fg=self.colors["danger"], active_bg=self.colors["danger"],
                                        width=15)
        self.alert_btn.pack(side=tk.RIGHT)

        # Content Grid
        content = tk.Frame(self.main_container, bg=self.colors["bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=40)

        left_col = tk.Frame(content, bg=self.colors["bg"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # System Config
        sys_mod = self.create_tactical_module(left_col, "CORE_PROTOCOLS")
        self.location_var = self.create_tactical_field(sys_mod, "GEO_LOC", self.config.get("location", ""))
        self.volume_var = self.create_tactical_field(sys_mod, "AUDIO_GAIN", self.config.get("startup_volume", 80), spin=True)
        self.tts_var = self.create_tactical_field(sys_mod, "MSG_GREET", self.config.get("tts_response", ""))
        self.music_var = self.create_tactical_field(sys_mod, "SONG_LINK", self.config.get("music_path", ""))

        # Auth Module
        auth_mod = self.create_tactical_module(left_col, "NEURAL_LINK")
        self.api_key_var = self.create_tactical_field(auth_mod, "MISTRAL_ID", self.config.get("MISTRAL_API_KEY", ""), show="*")
        
        TacticalButton(auth_mod, text="VERIFY_LINK", command=self.test_api_key, 
                       bg="#151525", fg=self.colors["warning"], active_bg=self.colors["warning"],
                       width=18, height=1).pack(pady=10)

        right_col = tk.Frame(content, bg=self.colors["bg"])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Seq Module
        seq_mod = self.create_tactical_module(right_col, "AUTO_SEQ_LIST")
        self.apps_text = tk.Text(seq_mod, height=11, width=25, bg="#050505", fg=self.colors["text_bright"], 
                                 insertbackground=self.colors["accent"], font=("Courier", 10), borderwidth=1, 
                                 relief="flat", highlightthickness=1, highlightbackground=self.colors["border"])
        self.apps_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.apps_text.insert(tk.END, "\n".join(self.config.get("apps", [])))

        # Synth Module
        synth_mod = self.create_tactical_module(right_col, "VOICE_SYNTH")
        self.voice_var = self.create_tactical_field(synth_mod, "VOICE_ID", self.config.get("voice_id", "en_US-ChristopherNeural"))
        self.rate_var = self.create_tactical_field(synth_mod, "TEMPO", self.config.get("speech_rate", "+15%"))
        self.pitch_var = self.create_tactical_field(synth_mod, "PITCH", self.config.get("voice_pitch", "-5Hz"))

        # Footer
        footer = tk.Frame(self.main_container, bg=self.colors["bg"])
        footer.pack(fill=tk.X, pady=(30, 20), padx=40)

        TacticalButton(footer, text="SAVE_PROTOCOLS", command=self.save_config, 
                       bg="#0a0a20", fg=self.colors["accent"], active_bg=self.colors["accent"],
                       height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        TacticalButton(footer, text="INIT_IGNITION", command=self.launch_main, 
                       bg="#200505", fg=self.colors["danger"], active_bg=self.colors["danger"],
                       height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def on_resize(self, event):
        if event.widget == self.root:
            self.current_width = event.width
            self.current_height = event.height
            self.draw_grid()
            self.canvas.itemconfig(self.window_id, width=event.width, height=event.height)

    def draw_grid(self):
        self.canvas.delete("grid")
        w = self.current_width
        h = self.current_height
        spacing = 40
        
        # Grid
        color = self.colors["grid"]
        for x in range(0, w, spacing):
            self.canvas.create_line(x, 0, x, h, fill=color, tags="grid")
        for y in range(0, h, spacing):
            self.canvas.create_line(0, y, w, y, fill=color, tags="grid")
            
        # Brackets
        self.canvas.create_line(10, 30, 10, 10, 30, 10, fill=self.colors["accent"], width=2, tags="grid")
        self.canvas.create_line(w-30, 10, w-10, 10, w-10, 30, fill=self.colors["accent"], width=2, tags="grid")
        self.canvas.create_line(10, h-30, 10, h-10, 30, h-10, fill=self.colors["accent"], width=2, tags="grid")
        self.canvas.create_line(w-30, h-10, w-10, h-10, w-10, h-30, fill=self.colors["accent"], width=2, tags="grid")

    def animate(self):
        self.canvas.delete("anim")
        w = self.current_width
        h = self.current_height
        
        # 1. Voice Visualizer (Bottom Wave)
        points = []
        for i, val in enumerate(self.viz_data):
            x = (w / len(self.viz_data)) * i
            # Shift wave data
            self.viz_data[i] = max(5, min(100, val + random.randint(-15, 15)))
            y = h - 20 - self.viz_data[i]
            points.extend([x, y])
        
        if len(points) > 4:
            self.canvas.create_line(points, fill=self.colors["accent"], width=2, smooth=True, tags="anim", stipple="gray50")

        # 2. Scanning Line
        self.scan_y = (self.scan_y + 4) % h
        self.canvas.create_line(0, self.scan_y, w, self.scan_y, fill=self.colors["accent"], width=1, tags="anim", stipple="gray12")

        # 3. Red Alert Pulse
        if self.red_alert:
            alpha = (math.sin(time.time() * 5) + 1) / 2
            pulse_color = f"#{int(50 + 100 * alpha):02x}0505"
            self.canvas.create_rectangle(0, 0, w, h, fill="", outline=pulse_color, width=10, tags="anim")
            if alpha > 0.8:
                self.canvas.create_text(w//2, 50, text="TACTICAL ALERT: CRITICAL STATE", font=("Courier", 20, "bold"), fill="#ff3344", tags="anim")

        self.root.after(50, self.animate)

    def create_tactical_module(self, parent, title):
        mod = tk.Frame(parent, bg=self.colors["module_bg"], highlightthickness=1, highlightbackground=self.colors["border"])
        mod.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(mod, text=f" {title} ", font=("Courier", 8, "bold"), fg=self.colors["accent"], 
                 bg=self.colors["bg"], pady=0).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        tk.Label(mod, text="⌜", font=("Courier", 12), fg=self.colors["accent"], bg=self.colors["module_bg"]).place(x=2, y=2)
        tk.Label(mod, text="⌟", font=("Courier", 12), fg=self.colors["accent"], bg=self.colors["module_bg"]).place(relx=1.0, rely=1.0, x=-12, y=-18)

        return mod

    def create_tactical_field(self, parent, label, default, show=None, spin=False):
        f = tk.Frame(parent, bg=self.colors["module_bg"], padx=15, pady=5)
        f.pack(fill=tk.X)
        
        tk.Label(f, text=f"> {label}:", font=("Courier", 8, "bold"), fg=self.colors["text_dim"], bg=self.colors["module_bg"]).pack(anchor=tk.W)
        var = tk.StringVar(value=str(default))
        
        entry_config = {
            "font": ("Courier", 10), "bg": "#050505", "fg": self.colors["text_bright"], 
            "insertbackground": self.colors["accent"], "borderwidth": 1, 
            "relief": "flat", "highlightthickness": 0
        }
        
        if spin:
            comp = tk.Spinbox(f, from_=0, to=100, textvariable=var, **entry_config, buttonbackground="#1a1a25")
        else:
            comp = tk.Entry(f, textvariable=var, **entry_config)
            if show: comp.config(show=show)
            
        comp.pack(fill=tk.X, pady=(2, 6))
        return var

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
