"""
API client for OpenRouter Claude 3 Sonnet integration
"""

import os
import random
import requests
import json
from typing import List, Optional, Dict, Any
import streamlit as st


def load_api_keys() -> List[str]:
    """
    Loads API keys from environment variables.

    Returns:
        List[str]: List of API keys
    """
    #load_dotenv()

    api_keys = []
    for i in range(1, 5):  # Load 4 API keys
        key = os.getenv(f"OPENROUTER_API_KEY_{i}")
        if key:
            api_keys.append(key)

    return api_keys


def validate_api_keys(api_keys: List[str]) -> bool:
    """
    Validates that API keys are properly loaded.

    Args:
        api_keys (List[str]): List of API keys to validate

    Returns:
        bool: True if keys are valid, False otherwise
    """
    if not api_keys:
        return False

    # Check that all keys start with expected prefix
    for key in api_keys:
        if not key.startswith("sk-or-v1-"):
            return False

    # Accept any number of valid API keys (at least one)
    return len(api_keys) > 0


def get_random_api_key(api_keys: List[str]) -> Optional[str]:
    """
    Returns a randomly selected API key from the available keys.

    Args:
        api_keys (List[str]): List of available API keys

    Returns:
        Optional[str]: Randomly selected API key or None if no keys available
    """
    if not api_keys:
        return None

    return random.choice(api_keys)


def get_model_for_api_key(api_key: str) -> str:
    """
    Returns the appropriate model based on the API key.

    Args:
        api_key (str): The API key

    Returns:
        str: The model name to use
    """
    # Map API keys to their respective models
    # Based on your API keys: DeepSeek, Kimi K2, Qwen
    api_keys = load_api_keys()

    if not api_keys:
        return "deepseek/deepseek-chat"  # Default fallback

    key_index = None
    try:
        key_index = api_keys.index(api_key)
    except ValueError:
        return "deepseek/deepseek-chat"  # Default fallback

    # Map each API key to its corresponding model
    models = [
        "deepseek/deepseek-chat",  # API Key 1 - DeepSeek
        "google/gemini-2.0-flash-exp:free",  # API Key 2 - Gemini 2.5 Pro
        "01-ai/yi-large",  # API Key 3 - Kimi K2 (Yi model)
        "qwen/qwen-2.5-72b-instruct",  # API Key 4 - Qwen
    ]

    return models[key_index] if key_index < len(models) else models[0]


def generate_response(
    prompt: str, 
    api_key: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    streaming: bool = False
) -> Dict[str, Any]:
    """
    Sends a request to the appropriate AI model via OpenRouter API.
    
    Args:
        prompt (str): The user's prompt
        api_key (str): The API key to use for the request
        conversation_history (Optional[List[Dict[str, str]]]): Previous conversation messages
        system_prompt (Optional[str]): System prompt for AI behavior
        streaming (bool): Whether to stream the response
        
    Returns:
        Dict[str, Any]: Response containing success status, content, and error info
    """
    # Always use non-streaming mode to avoid generator issues
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit-claude-app.com",  # Optional
        "X-Title": "Streamlit Claude App"  # Optional
    }
    
    # Get the appropriate model for this API key
    selected_model = get_model_for_api_key(api_key)
    
    # Build messages array
    messages = []
    
    # Add system message if provided
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current prompt
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    data = {
        "model": selected_model,
        "messages": messages,
        "max_tokens": 4000,
        "temperature": 0.9,
        "stream": False  # Always set to False to avoid generator issues
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            return {"success": True, "content": content, "error": None}
        else:
            return {
                "success": False,
                "content": None,
                "error": "No response content received"
            }
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "content": None, "error": f"Request error: {str(e)}"}
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": f"Unexpected error: {str(e)}"
        }


def initialize_api_keys() -> bool:
    """
    Initializes API keys in session state.

    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        api_keys = load_api_keys()

        if not validate_api_keys(api_keys):
            st.error("❌ Invalid or missing API keys. Please chcek your streamlit secrets.")
            return False

        st.session_state.api_keys = api_keys
        return True

    except Exception as e:
        st.error(f"❌ Error loading API keys: {str(e)}")
        return False


def test_api_connection(api_key: str) -> bool:
    """
    Tests API connection with a simple request.

    Args:
        api_key (str): API key to test

    Returns:
        bool: True if connection successful, False otherwise
    """
    test_prompt = "Hello, please respond with 'API connection successful'"
    result = generate_response(test_prompt, api_key)
    return result["success"]