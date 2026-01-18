import pyaudio
import numpy as np
import time
import logging
from audio_utils import no_alsa_error

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for audio stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
THRESHOLD = 3000  # Adjust based on mic sensitivity
CLAP_GAP = 0.5    # Max time between two claps (seconds)

def detect_claps(required_claps=2, timeout=5):
    """
    Listens for a sequence of loud noises (claps).
    """
    
    p = pyaudio.PyAudio()
    
    with no_alsa_error():
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    
    logger.info(f"Listening for {required_claps} claps within {timeout} seconds...")
    
    claps = 0
    start_time = time.time()
    last_clap_time = 0
    
    try:
        while time.time() - start_time < timeout:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            peak = np.average(np.abs(audio_data))
            
            if peak > THRESHOLD:
                current_time = time.time()
                # Debounce: ignore noise detected immediately after a clap
                if current_time - last_clap_time > 0.2: 
                    claps += 1
                    last_clap_time = current_time
                    logger.info(f"Clap {claps} detected! (Peak: {peak})")
                
                if claps >= required_claps:
                    return True
            
            # Small sleep to prevent CPU hogging - though reading stream blocks usually
            # time.sleep(0.01) 
            
    except Exception as e:
        logger.error(f"Error in clap detection: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    return False

if __name__ == "__main__":
    if detect_claps():
        print("Double clap confirmed!")
    else:
        print("Clap detection timed out.")
