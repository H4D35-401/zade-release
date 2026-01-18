# ⚡ ZADE IGNITE | Your Intelligent Command Center

ZADE IGNITE is a high-performance, voice-activated virtual assistant designed for rapid system orchestration and natural language interaction. Inspired by the sophistication of JARVIS, ZADE provides a premium "Command Center" interface to manage your digital environment.

![ZADE GUI Concept](https://img.shields.io/badge/Interface-Premium_Dark-00d4ff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 🚀 Vision
To create a seamless bridge between user intent and system action through advanced voice recognition, neural-link AI (Mistral), and automated task sequences.

## 🖥️ Platform Support
- **Operating System**: Optimized for **Arch Linux** and general Linux distributions.
- **Window Managers**: Fully compatible with Tiling Window Managers (**i3**, **Sway**, **Hyprland**) and Desktop Environments (Knome, Plasma).
- **Environment**: Designed for high-performance terminal and GUI orchestration.

## ✨ Key Features (v6.0 Universal HUD)
- **Universal AI Engine**: Select between **Mistral**, **OpenAI**, and **Google Gemini** directly in the HUD.
- **Cross-Platform Mastery**: Native support for **Arch Linux**, generic Linux distributions, and **Windows 10/11**.
- **Voice Profile Browser**: Choose and preview from a wide range of regional voice profiles.
- **Quantum HUD v5.0+**: Floating interactive modules on a dynamic, animated tactical canvas.
- **Encrypted Security**: Machine-locked encryption for your AI credentials.

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/zade-ignite.git
cd zade-ignite/zade-release
```

### 2. Run Setup Script
This will create a virtual environment and install all necessary neural dependencies.
```bash
./setup_env.sh
```

### 3. Launch the Command Center
```bash
./run_zade.sh
```

## ⚙️ Configuration
1. **Mistral AI Key**: Obtain an API key from [Mistral AI](https://console.mistral.ai/) and input it into the "Neural Interface" section.
2. **Apps**: List the commands for apps you want ZADE to launch upon ignition (one per line).
3. **Voice**: Adjust the Voice ID and Tempo to match your preference.

## 🛠️ Troubleshooting

### 1. `ModuleNotFoundError: No module named 'cryptography'`
This happens if the security library is missing from your environment.
- **Fix**: Run `pip install cryptography` or re-run `./setup_env.sh` to refresh the virtual environment.

### 2. `PermissionError` on Exit
If you see a permission error when trying to "Cancel" or "Deactivate" ZADE, it is usually because you are running it as a background service and it's trying to close the parent terminal.
- **Fix**: This is handled automatically in **v4.1+**. If you encounter it, ensure you are running the latest version from this repository.

### 3. Voice Not Recognized
- **Fix**: Ensure your microphone is calibrated. Stay silent during the "Calibrating" phase at startup. 

### 4. `config.json` Security
Your configuration is **machine-locked**. If you copy your `config.json` to another computer, it will not be readable. This is a security feature to protect your API keys.
- **Fix**: Create a fresh config on the new machine.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Developed with focus on speed, aesthetics, and intelligence.*
