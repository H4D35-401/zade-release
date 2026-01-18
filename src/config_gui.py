import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import time

# Configuration Path (Relative to current file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        self.active_bg = kwargs.pop('active_bg', '#00d4ff')
        self.active_fg = kwargs.pop('active_fg', '#0a0a12')
        self.default_bg = kwargs.get('bg', '#1a1a2e')
        self.default_fg = kwargs.get('fg', '#00d4ff')
        
        super().__init__(master, **kwargs)
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
        self.root.title("ZADE IGNITE | COMMAND CENTER")
        self.root.geometry("750x850")
        self.root.configure(bg='#05050a')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # UI Colors
        self.colors = {
            "bg": "#05050a",
            "frame_bg": "#0a0a1a",
            "accent": "#00d4ff",
            "text": "#ffffff",
            "danger": "#ff3333",
            "warning": "#ffcc00",
            "glow": "#005577"
        }

        self.setup_styles()
        self.config = self.load_config()
        self.create_widgets()
        
    def setup_styles(self):
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("Card.TFrame", background=self.colors["frame_bg"], borderwidth=1, relief="flat")
        
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["accent"], font=("Orbitron", 10))
        self.style.configure("Title.TLabel", background=self.colors["bg"], foreground=self.colors["danger"], font=("Orbitron", 22, "bold"))
        self.style.configure("Sub.TLabel", background=self.colors["frame_bg"], foreground=self.colors["accent"], font=("Orbitron", 10, "bold"))
        
        self.style.configure("TEntry", fieldbackground="#151525", foreground="white", insertcolor="white", borderwidth=0)
        self.style.configure("TLabelframe", background=self.colors["bg"], foreground=self.colors["warning"], borderwidth=1)
        self.style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["warning"], font=("Orbitron", 9, "bold"))

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            return {
                "location": "New York",
                "startup_volume": 80,
                "tts_response": "System online. All protocols initiated.",
                "MISTRAL_API_KEY": "",
                "voice_id": "en_US-ChristopherNeural",
                "speech_rate": "+15%",
                "voice_pitch": "-5Hz",
                "apps": ["google-chrome", "spotify"]
            }
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("IO ERROR", f"Failed to access neural link (config.json): {e}")
            return {}

    def save_config(self):
        try:
            self.config["location"] = self.location_var.get()
            self.config["startup_volume"] = int(self.volume_var.get())
            self.config["tts_response"] = self.tts_var.get()
            self.config["MISTRAL_API_KEY"] = self.api_key_var.get()
            self.config["voice_id"] = self.voice_var.get()
            self.config["speech_rate"] = self.rate_var.get()
            self.config["voice_pitch"] = self.pitch_var.get()
            
            apps_text = self.apps_text.get("1.0", tk.END).strip()
            self.config["apps"] = [app.strip() for app in apps_text.split("\n") if app.strip()]

            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.status_label.config(text="STATUS: CONFIG_UPLOADED", fg="#00ff00")
            self.root.after(3000, lambda: self.status_label.config(text="STATUS: READY", fg=self.colors["accent"]))
            
        except Exception as e:
            messagebox.showerror("SYNC ERROR", f"Could not sync protocols: {e}")

    def test_api_key(self):
        key = self.api_key_var.get()
        if not key:
            messagebox.showwarning("AUTH MISSING", "No API key found in the buffer.")
            return
        
        self.status_label.config(text="STATUS: TESTING_LINK...", fg=self.colors["warning"])
        
        def run_test():
            try:
                # Simple check for Mistral API
                import requests
                headers = {"Authorization": f"Bearer {key}"}
                response = requests.get("https://api.mistral.ai/v1/models", headers=headers, timeout=5)
                if response.status_code == 200:
                    self.root.after(0, lambda: messagebox.showinfo("LINK ESTABLISHED", "Neural link with Mistral established successfully."))
                    self.root.after(0, lambda: self.status_label.config(text="STATUS: LINK_ACTIVE", fg="#00ff00"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("LINK FAILED", f"Auth rejected by node: {response.status_code}"))
                    self.root.after(0, lambda: self.status_label.config(text="STATUS: LINK_OFFLINE", fg=self.colors["danger"]))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("TEST ERROR", f"Link error: {e}"))
                self.root.after(0, lambda: self.status_label.config(text="STATUS: ERROR", fg=self.colors["danger"]))

        threading.Thread(target=run_test, daemon=True).start()

    def launch_main(self):
        self.save_config()
        script_path = os.path.join(BASE_DIR, "main.py")
        try:
            # Detect if running in venv
            python_exe = "python3"
            venv_path = os.path.join(os.path.dirname(BASE_DIR), "venv", "bin", "python3")
            if os.path.exists(venv_path):
                python_exe = venv_path
            
            subprocess.Popen([python_exe, script_path], cwd=BASE_DIR)
            messagebox.showinfo("IGNITION", "ZADE IGNITE protocol has been initiated.")
        except Exception as e:
            messagebox.showerror("FAILURE", f"Could not ignite: {e}")

    def create_widgets(self):
        # Background Drawing (Subtle Glow)
        self.canvas = tk.Canvas(self.root, width=750, height=850, bg=self.colors["bg"], highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.canvas.create_oval(-100, -100, 300, 300, fill="#0a0a25", outline="")
        self.canvas.create_oval(500, 600, 900, 1000, fill="#0a0a25", outline="")

        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # Header Section
        header = tk.Frame(main_frame, bg=self.colors["bg"])
        header.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(header, text="ZADE IGNITE", font=("Orbitron", 32, "bold"), fg=self.colors["danger"], bg=self.colors["bg"]).pack()
        tk.Label(header, text="VIRTUAL ASSISTANT COMMAND CENTER", font=("Orbitron", 10), fg=self.colors["accent"], bg=self.colors["bg"]).pack()
        
        self.status_label = tk.Label(header, text="STATUS: READY", font=("Courier", 10, "bold"), fg=self.colors["accent"], bg=self.colors["bg"])
        self.status_label.pack(pady=10)

        # Settings Container
        container = tk.Frame(main_frame, bg=self.colors["bg"])
        container.pack(fill=tk.BOTH, expand=True)

        # LEFT COLUMN (General)
        left_col = tk.Frame(container, bg=self.colors["bg"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Core Settings Card
        core_card = self.create_card(left_col, "SYSTEM PROTOCOLS")
        
        self.location_var = self.create_entry(core_card, "GEO-LOCATION", self.config.get("location", ""))
        self.volume_var = self.create_spinbox(core_card, "STARTUP VOLUME", self.config.get("startup_volume", 80))
        self.tts_var = self.create_entry(core_card, "GREETING SEQUENCE", self.config.get("tts_response", ""))
        
        # API Card
        api_card = self.create_card(left_col, "NEURAL INTERFACE")
        self.api_key_var = self.create_entry(api_card, "MISTRAL API KEY", self.config.get("MISTRAL_API_KEY", ""), show="*")
        
        test_btn = ModernButton(api_card, text="VERIFY LINK", command=self.test_api_key, font=("Orbitron", 8, "bold"), 
                               bg="#1a1a2e", fg="#ffcc00", relief="flat", padx=10, pady=5)
        test_btn.pack(pady=10)

        # RIGHT COLUMN (Apps & Voice)
        right_col = tk.Frame(container, bg=self.colors["bg"])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Apps Card
        apps_card = self.create_card(right_col, "AUTO-IGNITE APPS")
        tk.Label(apps_card, text="(One per line)", font=("Orbitron", 7), bg=self.colors["frame_bg"], fg="#555577").pack(anchor=tk.W)
        self.apps_text = tk.Text(apps_card, height=10, width=25, bg="#050510", fg="white", 
                                 insertbackground="white", font=("Courier", 10), borderwidth=0)
        self.apps_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.apps_text.insert(tk.END, "\n".join(self.config.get("apps", [])))

        # Voice Modulation Card
        voice_card = self.create_card(right_col, "VOICE SYNTAX")
        self.voice_var = self.create_entry(voice_card, "VOICE IDENT", self.config.get("voice_id", "en_US-ChristopherNeural"))
        self.rate_var = self.create_entry(voice_card, "TEMPO OFFSET", self.config.get("speech_rate", "+15%"))
        self.pitch_var = self.create_entry(voice_card, "PITCH OFFSET", self.config.get("voice_pitch", "-5Hz"))

        # Footer Actions
        footer = tk.Frame(main_frame, bg=self.colors["bg"])
        footer.pack(fill=tk.X, pady=30)

        ModernButton(footer, text="UPLOAD CONFIG", command=self.save_config, font=("Orbitron", 12, "bold"),
                    bg="#1a1a2e", fg=self.colors["accent"], active_bg=self.colors["accent"], active_fg="#05050a",
                    relief="flat", height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        ModernButton(footer, text="IGNITE PROTOCOL", command=self.launch_main, font=("Orbitron", 12, "bold"),
                    bg="#2e1a1a", fg=self.colors["danger"], active_bg=self.colors["danger"], active_fg="#ffffff",
                    relief="flat", height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def create_card(self, parent, title):
        card = tk.Frame(parent, bg=self.colors["frame_bg"], padx=15, pady=15, highlightthickness=1, highlightbackground="#151535")
        card.pack(fill=tk.BOTH, expand=True, pady=10)
        tk.Label(card, text=title, font=("Orbitron", 10, "bold"), fg=self.colors["warning"], bg=self.colors["frame_bg"]).pack(anchor=tk.W, pady=(0, 10))
        return card

    def create_entry(self, parent, label, default, show=None):
        tk.Label(parent, text=label, font=("Orbitron", 8), fg="#00d4ff", bg=self.colors["frame_bg"]).pack(anchor=tk.W)
        var = tk.StringVar(value=default)
        entry = tk.Entry(parent, textvariable=var, font=("Inter", 10), bg="#050510", fg="#ffffff", 
                         insertbackground="white", borderwidth=0, highlightthickness=1, highlightbackground="#151535")
        if show: entry.config(show=show)
        entry.pack(fill=tk.X, pady=(2, 12))
        return var

    def create_spinbox(self, parent, label, default):
        tk.Label(parent, text=label, font=("Orbitron", 8), fg="#00d4ff", bg=self.colors["frame_bg"]).pack(anchor=tk.W)
        var = tk.StringVar(value=str(default))
        sb = tk.Spinbox(parent, from_=0, to=100, textvariable=var, font=("Inter", 10), bg="#050510", fg="#ffffff",
                        buttonbackground="#151535", borderwidth=0, highlightthickness=1, highlightbackground="#151535")
        sb.pack(fill=tk.X, pady=(2, 12))
        return var

if __name__ == "__main__":
    root = tk.Tk()
    # Handle missing fonts gracefully
    try:
        root.option_add("*Font", "Inter 10")
    except:
        pass
    app = ConfigGUI(root)
    root.mainloop()
