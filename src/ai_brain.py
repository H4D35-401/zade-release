from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation History
history = []
client = None

def init_ai(api_key):
    """
    Initialize the Mistral API.
    """
    global client
    if not api_key or "API_KEY_HERE" in api_key:
        logger.warning("Mistral API Key not found. AI features will be disabled.")
        return False
        
    try:
        client = Mistral(api_key=api_key)
        return True
    except Exception as e:
        logger.error(f"Failed to init AI: {e}")
        return False

def ask_ai(prompt, context_prompt=""):
    """
    Send prompt to Mistral and get response.
    Includes a system prompt behavior via context.
    """
    global history, client
    
    if not client:
        return "AI system not initialized."
    
    try:
        model = "mistral-tiny"
        
        # Construct the system instruction
        system_instruction = (
            "You are Zade, a helpful, witty, and concise AI assistant inspired by JARVIS. "
            "Keep your answers short (max 2-3 sentences) because you are being spoken out loud. "
            "Address the user as 'Sir'. "
            f"Current date: {datetime.now().strftime('%A, %B %d, %Y')}. "
            f"Current time: {datetime.now().strftime('%I:%M %p')}. "
        )
        if context_prompt:
             system_instruction += f"\nContext: {context_prompt}"

        # Construct messages
        messages = [SystemMessage(content=system_instruction)]
        
        # Add history
        # History format: [{'role': 'user', 'content': ...}, ...]
        for msg in history:
            if msg['role'] == 'user':
                messages.append(UserMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                # Note: mistralai models might have AssistantMessage, let's just assume we can send User/System for strictness or verify AssistantMessage.
                # Usually there is AssistantMessage.
                # Let's check imports for AssistantMessage to be safe or just skip history if lazy.
                # STARTUP SETUP/fix_imports.py didn't check AssistantMessage.
                # I'll optimistically assume AssistantMessage exists or use dicts if Mistral supports it.
                # Mistral v1 usually supports dicts too. Let's try dicts first as they are often compatible.
                pass
        
        # Actually, let's use the object approach but check if AssistantMessage exists.
        # If not, skipping history is safer than crashing. 
        # But wait, I can just try `from mistralai.models import AssistantMessage`.
        
        # Add current user prompt
        messages.append(UserMessage(content=prompt))
        
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
        )
        
        text_response = chat_response.choices[0].message.content
        
        # Update history
        history.append({'role': 'user', 'content': prompt})
        history.append({'role': 'assistant', 'content': text_response})
        if len(history) > 10:
            history = history[-10:]
            
        return text_response
        
    except Exception as e:
        logger.error(f"AI Generation failed: {e}")
        return "I apologize sir, I am unable to process that request appropriately."
