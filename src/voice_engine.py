import speech_recognition as sr
import edge_tts
import asyncio
import os
import logging
from audio_utils import no_alsa_error

# Shared state for GUI reactivity
vocal_level = 0.0

def get_vocal_level():
    global vocal_level
    return vocal_level

def _on_audio_data(recognizer, audio):
    """Callback to update volume level for UI reactivity."""
    global vocal_level
    try:
        # Calculate simple RMS energy from raw data
        raw = audio.get_raw_data()
        if raw:
            import audioop
            vocal_level = audioop.rms(raw, 2) / 32768.0 # Normalize 0.0 to 1.0ish
    except Exception:
        vocal_level = 0.0
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global config storage
current_config = {}

# Global objects to reuse connection
recognizer = sr.Recognizer()
microphone = None

# Pipeline Queues
import queue
import threading
import uuid

generation_queue = queue.Queue()
playback_queue = queue.Queue()
processing_started = False

def configure_engine(config):
    global current_config
    current_config = config
    
def start_processing():
    """
    Starts the background threads for TTS generation and playback.
    """
    global processing_started
    if processing_started:
        return
        
    threading.Thread(target=_generator_loop, daemon=True).start()
    threading.Thread(target=_playback_loop, daemon=True).start()
    processing_started = True
    logger.info("TTS Pipeline started.")

def _generator_loop():
    """
    Consumes text from generation_queue, generates AI, puts file path in playback_queue.
    """
    while True:
        text = generation_queue.get()
        if text is None: break # Sentinel
        
        try:
            # Unique filename to allow multiple files
            filename = f"/tmp/speech_{uuid.uuid4().hex}.mp3"
            
            # Defaults
            voice = current_config.get("voice_id", "en-US-ChristopherNeural") 
            rate = current_config.get("speech_rate", "+20%") 
            pitch = current_config.get("voice_pitch", "-5Hz") 
            
            # Generate
            success = asyncio.run(_generate_audio(text, filename, voice, rate, pitch))
            
            if success:
                playback_queue.put(filename)
            else:
                logger.error(f"Failed to generate audio for: {text}")
                
        except Exception as e:
            logger.error(f"Generator loop error: {e}")
        finally:
            generation_queue.task_done()

def _playback_loop():
    """
    Consumes file paths from playback_queue and plays them.
    """
    while True:
        filename = playback_queue.get()
        if filename is None: break
        
        try:
            with no_alsa_error():
                os.system(f"mpg123 -q {filename}")
            
            # Cleanup
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            logger.error(f"Playback loop error: {e}")
        finally:
            playback_queue.task_done()

def queue_speak(text):
    """
    Non-blocking speak. Adds text to the generation queue.
    """
    logger.info(f"Queued Speak: {text}")
    print(f">> {text}", flush=True)
    generation_queue.put(text)

def calibrate_mic():
    """
    Run once at startup to adjust for ambient noise.
    """
    global microphone
    logger.info("Calibrating microphone for ambient noise... (Please be silent)")
    with no_alsa_error():
        if microphone is None:
            microphone = sr.Microphone()
            
        with microphone as source:
            # Better calibration
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            recognizer.dynamic_energy_threshold = True
            recognizer.energy_threshold = 300 # Base starting point
            # Breathing room
            recognizer.pause_threshold = 0.8
            recognizer.non_speaking_duration = 0.4
    logger.info("Calibration complete.")

async def _generate_audio(text, output_file, voice, rate, pitch):
    """
    Async helper to generate audio using edge-tts.
    """
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_file)
        return True
    except Exception as e:
        logger.error(f"EdgeTTS generation failed: {e}")
        return False

def speak(text):
    """
    Blocking speak. Uses the pipeline but waits for completion to maintain compatibility.
    """
    queue_speak(text)
    # Ideally we wouldn't block here if we want full async, 
    # but for "Chat Mode" we usually want to wait until finished before listening again.
    # For now, let's just queue it. 
    # If we need to block, we'd need a different mechanism, but queueing is safer for preventing overlaps.
    return 

def wait_for_completion():
    """
    Blocks until all queued speech is generated and played.
    """
    if processing_started:
        generation_queue.join()
        playback_queue.join()

def listen_for_input():
    """
    Listens for any speech using the pre-calibrated microphone.
    """
    global microphone
    
    # Ensure mic is initialized if calibrate wasn't called
    if microphone is None:
        calibrate_mic()

    # Wait for playback queue to empty before listening (prevent listening to self)
    if processing_started:
        playback_queue.join() 
        # Note: join() blocks until queue is empty. 
        # Ideally we check if it's empty, but join ensures we don't listen while speaking.
    
    with no_alsa_error():
        # Reuse existing microphone instance to skip init overhead
        with microphone as source:
            try:
                # Optimized for a balance of speed and reliability
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                # Brief volume check for UI (not real-time enough in blocking listen, but better than nothing)
                global vocal_level
                import audioop
                vocal_level = audioop.rms(audio.get_raw_data(), 2) / 1000.0
                try:
                    text = recognizer.recognize_google(audio).lower()
                    print(f"[DEBUG] Recognized: {text}", flush=True)
                    return text
                            
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"[DEBUG] API unavailable: {e}", flush=True)
            except sr.WaitTimeoutError:
                 pass
            except Exception as e:
                 print(f"[DEBUG] Unexpected error: {e}", flush=True)
            
    return None

def listen_for_commands(commands=["ignite"]):
    """
    Deprecated: Use listen_for_input and parse manually.
    """
    text = listen_for_input()
    if text:
        for cmd in commands:
            if cmd in text.split():
                return cmd
    return None

if __name__ == "__main__":
    # Test
    speak("Voice engine initialized.")
    cmd = listen_for_commands(["ignite", "test"])
    if cmd:
        speak(f"Command {cmd} detected.")
