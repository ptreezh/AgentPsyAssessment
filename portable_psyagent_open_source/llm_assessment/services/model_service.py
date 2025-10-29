"""
Unified Model Service Interface
Based on testLLM/core/model_manager_enhanced.py
"""

import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from .ollama_service import OllamaService
from .cloud_services import call_cloud_service, get_available_services

logger = logging.getLogger(__name__)

class ModelService(ABC):
    """Abstract base class for model services"""
    
    @abstractmethod
    def generate_response(self, model: str, messages: List[Dict[str, str]], 
                         options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate response from model
        
        Args:
            model: Model identifier
            messages: List of messages
            options: Generation options
            
        Returns:
            Model response
        """
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if service is available
        
        Returns:
            True if available, False otherwise
        """
        pass

class OllamaModelService(ModelService):
    """Model service for local Ollama models"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize Ollama model service"""
        self.service = OllamaService(host)
        
    def generate_response(self, model: str, messages: List[Dict[str, str]], 
                         options: Optional[Dict[str, Any]] = None) -> str:
        """Generate response from Ollama model"""
        # For Ollama, model identifier is just the model name
        actual_model = model.split('/', 1)[1] if '/' in model else model
        logger.debug(f"Calling Ollama model {actual_model}")
        start_time = time.time()
        try:
            response = self.service.generate_response(actual_model, messages, options)
            elapsed_time = time.time() - start_time
            logger.debug(f"Ollama model {actual_model} response received in {elapsed_time:.2f}s")
            return response
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Ollama model {actual_model} call failed after {elapsed_time:.2f}s: {e}")
            raise
        
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        return self.service.is_available()

class CloudModelService(ModelService):
    """Model service for cloud models"""
    
    def __init__(self):
        """Initialize cloud model service"""
        pass
        
    def generate_response(self, model: str, messages: List[Dict[str, str]], 
                         options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate response from cloud model
        
        Args:
            model: Model identifier in format "service/model-name"
            messages: List of messages
            options: Generation options (not used for cloud services in this implementation)
            
        Returns:
            Model response
        """
        # Parse model identifier
        if '/' not in model:
            raise ValueError("Cloud model identifier must be in format 'service/model-name'")
            
        service_name, model_name = model.split('/', 1)
        
        # Extract prompt and system message
        prompt = ""
        system_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                prompt = msg["content"]
                
        # Call cloud service
        logger.debug(f"Calling cloud model service {service_name}/{model_name}")
        start_time = time.time()
        try:
            response = call_cloud_service(service_name, model_name, prompt, system_prompt)
            elapsed_time = time.time() - start_time
            logger.debug(f"Cloud model service {service_name}/{model_name} response received in {elapsed_time:.2f}s")
            return response
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Cloud model service {service_name}/{model_name} call failed after {elapsed_time:.2f}s: {e}")
            raise
        
    def is_available(self) -> bool:
        """
        Check if cloud services are available
        
        Returns:
            True if available, False otherwise
        """
        try:
            # In this implementation, we assume cloud services are always available
            # In a more robust implementation, we would check connectivity to each service
            # For now, we'll return True as we'll check each model individually during testing
            return True
        except Exception as e:
            logger.error(f"Failed to check cloud service availability: {e}")
            return False

# Factory function to create model service based on model identifier
def create_model_service(model_identifier: str) -> ModelService:
    """
    Create appropriate model service based on model identifier
    
    Args:
        model_identifier: Model identifier (e.g., "ollama/llama3", "together/meta-llama/Llama-3-8b-chat")
        
    Returns:
        Appropriate model service instance
        
    Raises:
        ValueError: If the model identifier format is unsupported or the service is not available.
    """
    if model_identifier.startswith("ollama/"):
        return OllamaModelService()
    elif "/" in model_identifier:
        # Check if it's a known cloud service
        service_name = model_identifier.split("/", 1)[0]
        if service_name in get_available_services():
            return CloudModelService()
        else:
            # If it has a '/' but is not a known service, it's invalid
            raise ValueError(f"Unsupported model identifier: {model_identifier}")
    # For local models without any "/" prefix, treat them as Ollama models
    elif "/" not in model_identifier:
        return OllamaModelService()
    else:
        # This else clause might be redundant, but kept for explicitness
        raise ValueError(f"Unsupported model identifier: {model_identifier}")