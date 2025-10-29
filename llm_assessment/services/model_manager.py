"""
Model Manager for AgentPsy
Based on testLLM/core/model_manager_enhanced.py
"""

import logging
from typing import Dict, List, Any, Optional
from .model_service import create_model_service, ModelService

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages LLM models for AgentPsy"""
    
    def __init__(self):
        """Initialize model manager"""
        self.model_services: Dict[str, ModelService] = {}
        self.current_model: Optional[str] = None
        
    def load_model(self, model_identifier: str) -> bool:
        """
        Load a specific model
        
        Args:
            model_identifier: Model identifier (e.g., "ollama/llama3", "together/meta-llama/Llama-3-8b-chat")
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            # Create model service if it doesn't exist
            if model_identifier not in self.model_services:
                service = create_model_service(model_identifier)
                self.model_services[model_identifier] = service
                
            # Check if service is available
            if not self.model_services[model_identifier].is_available():
                logger.error(f"Model service for {model_identifier} is not available")
                return False
                
            self.current_model = model_identifier
            logger.info(f"Model loaded successfully: {model_identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_identifier}: {e}")
            return False
            
    def generate_response(self, messages: List[Dict[str, str]], 
                         model_identifier: Optional[str] = None,
                         options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate response from model
        
        Args:
            messages: List of messages in OpenAI format
            model_identifier: Model identifier (uses current model if not specified)
            options: Generation options
            
        Returns:
            Model response or None if failed
        """
        target_model = model_identifier or self.current_model
        
        if not target_model:
            logger.error("No model specified and no current model set")
            return None
            
        if target_model not in self.model_services:
            logger.error(f"Model {target_model} not loaded")
            return None
            
        try:
            service = self.model_services[target_model]
            response = service.generate_response(target_model, messages, options)
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed for model {target_model}: {e}")
            return None
            
    def get_available_models(self) -> List[str]:
        """
        Get list of available models
        For now, we return a static list. In a more advanced implementation,
        this could query services for available models.
        """
        # This would be dynamically populated in a more advanced implementation
        return [
            "ollama/llama3",
            "ollama/gemma3",
            "together/mistralai/Mixtral-8x7B-Instruct-v0.1",
            "openrouter/google/gemma-2-9b-it",
            "gemini/gemini-1.5-flash",
            "gemini/gemini-2.0-flash-exp",
            "ppinfra/qwen/qwen3-235b-a22b-fp8",
            "ppinfra/minimaxai/minimax-m1-80k",
            "glm/glm-4-plus",
            "glm/glm-4-air",
            "glm/glm-4-airx",
            "glm/glm-4-flash"
        ]
        
    def is_model_ready(self, model_identifier: str) -> bool:
        """
        Check if model is ready for inference
        
        Args:
            model_identifier: Model identifier
            
        Returns:
            True if model is ready, False otherwise
        """
        return (model_identifier in self.model_services and 
                self.model_services[model_identifier].is_available())