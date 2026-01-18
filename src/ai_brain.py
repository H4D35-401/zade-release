import logging
import os
from mistralai import Mistral
import openai
from google import genai
from memory_system import load_memory, get_identity_context
from features import get_system_stats, get_battery_status

logger = logging.getLogger(__name__)

_client = None
_engine_type = "mistral" # default

def init_ai(config):
    """
    Initializes the AI brain based on config.
    Supports: 'mistral', 'openai', 'gemini'
    """
    global _client, _engine_type
    
    _engine_type = config.get("ai_engine", "mistral").lower()
    api_key = config.get(f"{_engine_type.upper()}_API_KEY", "")
    
    if not api_key:
        logger.warning(f"No API key found for {_engine_type}. AI interactions disabled.")
        return

    try:
        if _engine_type == "mistral":
            _client = Mistral(api_key=api_key)
            logger.info("Mistral Neural Link initialized.")
        
        elif _engine_type == "openai":
            openai.api_key = api_key
            _client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI Neural Link initialized.")
            
        elif _engine_type == "gemini":
            _client = genai.Client(api_key=api_key)
            logger.info("Gemini Neural Link (v1 SDK) initialized.")
            
    except Exception as e:
        logger.error(f"Neural linkage failure: {e}")

def ask_ai(prompt):
    """Queries the active AI engine with full situational awareness."""
    global _client, _engine_type
    if not _client:
        return "System error: No active neural link. Please check your API keys."

    # v7.0 Neural Context
    identity = get_identity_context()
    stats = get_system_stats()
    battery = get_battery_status()
    
    system_instruction = (
        f"{identity} "
        f"SITUATIONAL_AWARENESS: {stats}. {battery}. "
        "Your responses should be tactical, efficient, and formatted for a HUD. "
        "Keep them under 50 words unless asked for technical detail."
    )

    try:
        full_prompt = f"[SYSTEM_INT: {system_instruction}]\nUSER: {prompt}"

        if _engine_type == "mistral":
            response = _client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": full_prompt}]
            )
            return response.choices[0].message.content

        elif _engine_type == "openai":
            response = _client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": full_prompt}]
            )
            return response.choices[0].message.content

        elif _engine_type == "gemini":
            response = _client.models.generate_content(
                model="gemini-pro",
                contents=full_prompt
            )
            return response.text

    except Exception as e:
        logger.error(f"AI Query failed: {e}")
        return "I'm having trouble connecting to my neural network right now."
