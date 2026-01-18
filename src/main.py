
import json
import os
import logging
import json
import os
import logging
import time
import signal
import voice_engine
import clap_detector
import automator
import features
import ai_brain
import webbrowser
import subprocess
import concurrent.futures

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Could not load config: {e}")
        return {}

def main():
    config = load_config()
    tts_response = config.get("tts_response", "Welcome home, sir.")
    
    # Configure voice
    voice_engine.configure_engine(config)
    
    logger.info("Initializing Zade Ignite Protocol...")
    
    # Calibrate Audio
    time.sleep(2) # Wait for system audio to settle
    voice_engine.calibrate_mic()
    voice_engine.start_processing()
    
    # Initialize AI
    api_key = config.get("MISTRAL_API_KEY", "")
    ai_brain.init_ai(api_key)
    
    voice_engine.speak("System online. Listening.")
    print("System Ready - Listening...", flush=True)

    while True:
        # 1. Listen for ANY input
        user_text = voice_engine.listen_for_input()
        
        if user_text:
            logger.info(f"User said: {user_text}")
            words = user_text.split()
            
            # --- COMMANDS ---
            
            # 1. IGNITE / STARTUP
            ignite_keywords = ["ignite", "ignited", "ign", "start"]
            if any(k in words for k in ignite_keywords):
                logger.info("Ignite command detected")
                # Immediately set volume to ensure we are heard
                startup_volume = config.get("startup_volume", 80)
                automator.set_system_volume(startup_volume)
                
                # Immediate Response (Greeting & Time)
                greeting = features.get_greeting()
                time_str = automator.get_time_string()
                voice_engine.queue_speak(f"{greeting}. {time_str}.")
                
                # Start parallel fetching immediately
                location = config.get("location", "Nagpur")
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Submit all tasks
                    future_weather = executor.submit(features.get_weather, location)
                    future_battery = executor.submit(features.get_battery_status)
                    future_sys = executor.submit(features.get_system_stats)
                    future_net = executor.submit(features.get_network_status)
                    future_quote = executor.submit(features.get_quote)
                    
                    # Speak quick-available results first
                    voice_engine.queue_speak(future_battery.result())
                    voice_engine.queue_speak(future_sys.result())
                    # Wait for network and weather which might be slower
                    voice_engine.queue_speak(future_net.result())
                    voice_engine.queue_speak(future_weather.result())
                    voice_engine.queue_speak(future_quote.result())

                # Finalize
                voice_engine.queue_speak(tts_response)
                automator.run_sequence(config)
                voice_engine.queue_speak("Startup complete.")
            
            # 2. SHUTDOWN
            elif "shutdown" in words:
                voice_engine.speak("Confirm shutdown?")
                if clap_detector.detect_claps(required_claps=2):
                    voice_engine.speak("Shutting down.")
                    automator.system_shutdown()
                    
            # 3. REBOOT
            elif "reboot" in words or "restart" in words:
                voice_engine.speak("Confirm reboot?")
                if clap_detector.detect_claps(required_claps=2):
                    voice_engine.speak("Rebooting system.")
                    automator.system_reboot()
                    
            # 4. SLEEP
            elif "sleep" in words:
                voice_engine.speak("Entering sleep mode.")
                automator.system_sleep()
                
            # 5. CANCEL / TERMINATE
            elif "terminate" in words or "abort" in words or (("cancel" in words or "stop" in words) and any(w in words for w in ["system", "protocol", "process", "program", "listening"])):
                voice_engine.speak("Goodbye, sir. Deactivating protocols.")
                # Just wait for speech to finish, then exit. Do NOT close apps as per user request.
                voice_engine.wait_for_completion()
                # Kill parent process (the shell) to close terminal
                os.kill(os.getppid(), signal.SIGHUP)
                break
                
            # 6. SMART COMMANDS (Open / Search)
            elif process_smart_commands(user_text):
                pass # Command handled by function

            # 7. CONTINUOUS CHAT MODE
            elif "chat mode" in user_text or "lets chat" in user_text:
                voice_engine.speak("Engaging conversational mode. Say 'exit' to stop.")
                while True:
                    chat_text = voice_engine.listen_for_input()
                    if not chat_text: 
                        continue
                    
                    if "exit" in chat_text or "stop" in chat_text or "cancel" in chat_text:
                        voice_engine.speak("Exiting chat mode.")
                        break
                    
                    # Check for commands within chat (Open / Search)
                    if process_smart_commands(chat_text):
                        continue
                        
                    # Direct conversation
                    response = ai_brain.ask_ai(chat_text)
                    if response:
                        voice_engine.speak(response)

            # --- AI FALLBACK ---
            else:
                # Chat with JARVIS (One-off)
                if "zade" in words or len(words) > 1: # Avoid responding to ambient noise single words
                    response = ai_brain.ask_ai(user_text)
                    if response:
                         voice_engine.speak(response)
        
        time.sleep(0.1)

def process_smart_commands(text):
    """
    Processes 'Open' and 'Search' commands.
    Returns True if a command was executed, False otherwise.
    """
    text = text.lower()
    
    # OPEN APPS
    if "open" in text:
        parts = text.split("open", 1)
        if len(parts) > 1:
            app_name = parts[1].strip()
        else:
            return False
        voice_engine.speak(f"Opening {app_name}")
        if "code" in app_name:
            subprocess.Popen(["code"])
        elif "firefox" in app_name:
            subprocess.Popen(["firefox"])
        elif "terminal" in app_name:
            # Try available terminals
            terminals = ["xfce4-terminal", "kitty", "gnome-terminal", "konsole", "alacritty", "xterm"]
            found = False
            for term in terminals:
                if subprocess.run(["which", term], capture_output=True).returncode == 0:
                    subprocess.Popen([term])
                    found = True
                    break
            if not found:
                voice_engine.speak("I could not find a supported terminal emulator.")
        else:
             try:
                 subprocess.Popen(app_name, shell=True)
             except:
                 voice_engine.speak(f"Could not find application {app_name}")
        return True

    # CLOSE APPS
    elif text.startswith("close") or text.startswith("kill"):
        app_name = text.replace("close", "").replace("kill", "").strip()
        voice_engine.speak(f"Closing {app_name}")
        automator.close_app(app_name)
        return True

    # WEB SEARCH
    elif text.startswith("search for") or text.startswith("look up"):
        query = text.replace("search for", "").replace("look up", "").strip()
        voice_engine.speak(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return True
        
    return False



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutting down.")
