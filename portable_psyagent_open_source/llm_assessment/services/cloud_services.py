"""
Cloud Service Configuration and Unified Calling Interface
Based on testLLM/scripts/utils/cloud_services.py
"""

import os
import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# All cloud service configurations
CLOUD_SERVICES = {
    "together": {
        "name": "Together.ai",
        "api_url": "https://api.together.xyz/v1/chat/completions",
        "api_key_env": "TOGETHER_API_KEY",
        "models": ["mistralai/Mixtral-8x7B-Instruct-v0.1"],
        "test_prompt": "Hello",
        "type": "openai_compatible"
    },
    "openrouter": {
        "name": "OpenRouter",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key_env": "OPENROUTER_API_KEY",
        "models": ["google/gemma-2-9b-it"],
        "test_prompt": "Hello",
        "type": "openai_compatible"
    },
    "ppinfra": {
        "name": "PPInfra",
        "api_url": "https://api.ppinfra.com/v3/openai/chat/completions",
        "api_key_env": "PPINFRA_API_KEY",
        "models": ["qwen/qwen3-235b-a22b-fp8", "minimaxai/minimax-m1-80k"],
        "test_prompt": "Hello",
        "type": "openai_compatible"
    },
    "gemini": {
        "name": "Google Gemini",
        "api_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "api_key_env": "GEMINI_API_KEY",
        "models": ["gemini-1.5-flash", "gemini-2.0-flash-exp"],
        "test_prompt": "Hello",
        "type": "gemini"
    },
    "dashscope": {
        "name": "阿里云DashScope",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "api_key_env": "DASHSCOPE_API_KEY",
        "models": ["qwen-plus", "qwen-max", "qwen-turbo"],
        "test_prompt": "你好",
        "type": "openai_compatible"
    },
    "glm": {
        "name": "智谱AI GLM",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "api_key_env": "GLM_API_KEY",
        "models": ["glm-4-plus", "glm-4-air", "glm-4-airx", "glm-4-flash"],
        "test_prompt": "你好",
        "type": "openai_compatible"
    }
}

def _call_openai_compatible(config: Dict, model_name: str, messages: List) -> str:
    """Call OpenAI compatible API"""
    api_key = os.getenv(config["api_key_env"])
    if not api_key:
        raise ValueError(f"API key not set: {config['api_key_env']}")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"model": model_name, "messages": messages, "max_tokens": 1024}

    # Increase timeout to 120 seconds
    logger.debug(f"Calling {config["name"]} API with 120s timeout")
    start_time = time.time()
    try:
        response = requests.post(config["api_url"], headers=headers, json=payload, timeout=120)
        elapsed_time = time.time() - start_time
        logger.debug(f"{config["name"]} API response received in {elapsed_time:.2f}s")
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"{config["name"]} API call failed after {elapsed_time:.2f}s: {e}")
        raise
    
    # Better error handling
    if response.status_code == 404:
        raise ValueError(f"Model {model_name} not found. API response: {response.text}")
    elif response.status_code != 200:
        raise ValueError(f"API request failed with status {response.status_code}. Response: {response.text}")
    
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def _call_gemini(config: Dict, model_name: str, messages: List) -> str:
    """Call Google Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(f"API key not set: {config['api_key_env']}")

    url = f"{config['api_url']}/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Gemini needs different format
    gemini_contents = []
    for msg in messages:
        if msg['role'] == 'system': # Gemini uses system instructions
            continue
        gemini_contents.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}]
        })

    payload = {"contents": gemini_contents}
    
    # Increase timeout to 120 seconds
    logger.debug(f"Calling {config["name"]} API with 120s timeout")
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        elapsed_time = time.time() - start_time
        logger.debug(f"{config["name"]} API response received in {elapsed_time:.2f}s")
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"{config["name"]} API call failed after {elapsed_time:.2f}s: {e}")
        raise
    
    # Better error handling
    if response.status_code == 404:
        raise ValueError(f"Model {model_name} not found. API response: {response.text}")
    elif response.status_code != 200:
        raise ValueError(f"API request failed with status {response.status_code}. Response: {response.text}")
    
    response.raise_for_status()
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']

def call_cloud_service(service_name: str, model_name: str, prompt: str, system_prompt: Optional[str] = None) -> str:
    """Call cloud service (unified entry)"""
    if service_name not in CLOUD_SERVICES:
        raise ValueError(f"Unknown service: {service_name}")

    config = CLOUD_SERVICES[service_name]
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    service_type = config.get("type", "openai_compatible")

    try:
        if service_type == "openai_compatible":
            return _call_openai_compatible(config, model_name, messages)
        elif service_type == "gemini":
            return _call_gemini(config, model_name, messages)
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    except Exception as e:
        print(f"Failed to call {service_name}/{model_name}: {e}")
        raise  # Re-raise exception for caller to handle

def get_available_services() -> List[str]:
    """Get list of all available service names"""
    return list(CLOUD_SERVICES.keys())

def get_all_models() -> List[Dict[str, str]]:
    """Get information for all models"""
    models = []
    for service_name, config in CLOUD_SERVICES.items():
        for model in config["models"]:
            models.append({
                "service": service_name,
                "model": model,
                "key": f"{model}-{service_name}"
            })
    return models