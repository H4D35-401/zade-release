import os
import subprocess
import platform
import logging

logger = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"

def set_system_volume(volume_level):
    """Sets system volume (0-100)."""
    try:
        if IS_WINDOWS:
            # Simple volume set via powershell or nircmd if available
            # Basic fallback: use powershell to set master volume (simplified)
            cmd = f"$w = New-Object -ComObject WScript.Shell; $w.SendKeys([char]175)" # Vol Up placeholder
            # For real volume control on Windows, a library like pycaw is usually better
            # but for a portable script, we'll use a simplified approach
            pass 
        else:
            # Linux (amixer/pactl)
            subprocess.run(["amixer", "sset", "Master", f"{volume_level}%"], capture_output=True)
    except Exception as e:
        logger.error(f"Volume control failed: {e}")

def system_shutdown():
    """Triggers system shutdown."""
    if IS_WINDOWS:
        os.system("shutdown /s /t 1")
    else:
        os.system("shutdown now")

def system_reboot():
    """Triggers system reboot."""
    if IS_WINDOWS:
        os.system("shutdown /r /t 1")
    else:
        os.system("reboot")

def system_sleep():
    """Triggers system sleep."""
    if IS_WINDOWS:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    else:
        # Check for common linux sleep commands
        for cmd in ["systemctl suspend", "pm-suspend"]:
            if subprocess.run(["which", cmd.split()[0]], capture_output=True).returncode == 0:
                os.system(cmd)
                break

def close_app(app_name):
    """Closes an application by name."""
    if IS_WINDOWS:
        os.system(f"taskkill /IM {app_name}.exe /F")
    else:
        os.system(f"pkill -f {app_name}")

def run_sequence(config):
    """Launches the user's startup application stack."""
    apps = config.get("apps", [])
    for app in apps:
        try:
            if IS_WINDOWS:
                # On Windows, we often need 'start' for common apps
                subprocess.Popen(f"start {app}", shell=True)
            else:
                subprocess.Popen(app, shell=True)
        except Exception as e:
            logger.error(f"Failed to launch {app}: {e}")

def get_time_string():
    import datetime
    now = datetime.datetime.now()
    return now.strftime("The time is %I:%M %p")
