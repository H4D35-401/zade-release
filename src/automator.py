import subprocess
import os
import logging
import time

import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_system_volume(level):
    """
    Sets the system volume using amixer (ALSA).
    Level should be an integer between 0 and 100.
    """
    try:
        logger.info(f"Setting system volume to {level}%...")
        subprocess.run(["amixer", "sset", "Master", f"{level}%"], check=True)
    except Exception as e:
        logger.warning(f"Failed to set volume: {e}")

def get_time_string():
    """
    Returns a string representation of the current time, e.g. "It is 8:30 PM".
    """
    now = datetime.now()
    return now.strftime("It is %I:%M %p")

def system_shutdown():
    """
    Initiates system shutdown.
    """
    try:
        logger.info("Initiating Shutdown...")
        subprocess.run(["sudo", "systemctl", "poweroff"], check=True)
    except Exception as e:
        logger.error(f"Shutdown failed: {e}")

def system_reboot():
    """
    Initiates system reboot.
    """
    try:
        logger.info("Initiating Reboot...")
        subprocess.run(["sudo", "systemctl", "reboot"], check=True)
    except Exception as e:
        logger.error(f"Reboot failed: {e}")

def system_sleep():
    """
    Put system to sleep/suspend.
    """
    try:
        logger.info("Initiating Sleep Mode...")
        subprocess.run(["sudo", "systemctl", "suspend"], check=True)
    except Exception as e:
        logger.error(f"Sleep failed: {e}")

def close_app(app_name):
    """
    Closes an application by name.
    """
    try:
        logger.info(f"Closing {app_name}...")
        # Mapping for common names to process names
        valid_name = app_name.lower().strip()
        if "code" in valid_name: valid_name = "code"
        elif "firefox" in valid_name: valid_name = "firefox"
        elif "chrome" in valid_name: valid_name = "chrome"
        elif "terminal" in valid_name: 
            # Check for common terminal process names
            for term in ["xfce4-terminal", "kitty", "gnome-terminal", "konsole", "alacritty"]:
                subprocess.run(["pkill", "-f", term], check=False)
            return True
        elif "spotify" in valid_name: valid_name = "spotify"
        
        subprocess.run(["pkill", "-f", valid_name], check=False)
        return True
    except Exception as e:
        logger.error(f"Failed to close {app_name}: {e}")
        return False

def open_apps(app_list):
    """
    Opens the list of applications provided.
    """
    for app in app_list:
        try:
            logger.info(f"Opening {app}...")
            # Use setsid to detach process so they don't depend on this script
            subprocess.Popen(app, shell=True, start_new_session=True)
        except FileNotFoundError:
            logger.error(f"App not found: {app}")
        except Exception as e:
            logger.error(f"Failed to open {app}: {e}")

def play_music(music_path):
    """
    Plays music from the given path using xdg-open or a specific player.
    """
    if not music_path:
        return

    logger.info(f"Playing music: {music_path}")
    try:
        # Check if file exists
        if not os.path.exists(music_path) and not music_path.startswith("http"):
            logger.warning(f"Music file not found: {music_path}")
            return
            
        if os.name == 'posix': # Linux/Mac
            subprocess.Popen(['xdg-open', music_path], start_new_session=True)
            # OR specific player: subprocess.Popen(['vlc', music_path])
        else:
            os.startfile(music_path)
    except Exception as e:
        logger.error(f"Failed to play music: {e}")

def run_sequence(config):
    """
    Executes the automation sequence defined in config.
    """
    apps = config.get("apps", [])
    music_path = config.get("music_path")
    
    # Open apps
    open_apps(apps)
    
    # Wait a moment for things to initialize?
    time.sleep(1)
    
    # Play music
    play_music(music_path)
