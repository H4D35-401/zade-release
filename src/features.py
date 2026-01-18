import requests
import psutil
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_greeting():
    """
    Returns a time-based greeting.
    """
    # Use astimezone() to ensure we get the local machine's hourly time, 
    # even if the environment defaults to UTC.
    hour = datetime.now().astimezone().hour
    if hour < 12:
        return "Good morning"
    elif 12 <= hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

def get_date_string():
    """
    Returns a string representation of the current date, e.g. "Sunday, January 18, 2026".
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y")

def get_battery_status():
    """
    Returns a string describing battery percentage and status.
    """
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = int(battery.percent)
            plugged = battery.power_plugged
            status = "charging" if plugged else "running on battery"
            return f"Battery is at {percent} percent and {status}"
    except Exception as e:
        logger.warning(f"Battery check failed: {e}")
    return ""

def get_weather(location_name="Nagpur"):
    """
    Fetches weather for the given location using OpenMeteo (requires geocoding first).
    For simplicity, we'll use a direct geocoding lookup or default to a known location if it fails.
    """
    try:
        # 1. Geocoding
        # Using open-meteo geocoding API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_name}&count=1&language=en&format=json"
        
        logger.info(f"Fetching weather location for: {location_name}")
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get("results"):
            return f"Could not find weather for {location_name}"
            
        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        
        # 2. Weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(weather_url, timeout=5).json()
        
        if "current_weather" in w_res:
            temp = w_res["current_weather"]["temperature"]
            return f"Current temperature in {location_name} is {temp} degrees Celsius"
            
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        
    return "Unable to fetch weather data"

def get_system_stats():
    """
    Returns a string describing CPU and Memory usage.
    """
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        return f"CPU load is at {cpu} percent. Memory usage is at {mem} percent"
    except Exception:
        return ""

def get_network_status():
    """
    Checks connectivity to Google DNS and returns latency.
    """
    try:
        start = time.time()
        requests.get("http://8.8.8.8", timeout=2) # Using HTTP to just check reachability
        latency = int((time.time() - start) * 1000)
        return f"Systems are online. Network latency is {latency} milliseconds"
    except Exception:
        return "Network appears to be offline"

def get_quote():
    """
    Fetches a random quote from ZenQuotes (free tier).
    """
    try:
        # ZenQuotes free API
        res = requests.get("https://zenquotes.io/api/random", timeout=3).json()
        if res and isinstance(res, list):
            quote = res[0]['q']
            author = res[0]['a']
            return f"Quote of the day: {quote} by {author}"
    except Exception as e:
        logger.error(f"Quote fetch failed: {e}")
        
    return ""
