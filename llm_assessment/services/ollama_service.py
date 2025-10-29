"""
Ollama Service for Local Models
Based on testLLM/independence/utils.py and testLLM/scripts/utils/utils.py
"""

import logging
import time
from typing import Dict, List, Any, Optional
import ollama

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for local Ollama models"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize Ollama service"""
        self.host = host
        self.client = ollama.Client(host=host)
        
    def generate_response(self, model: str, messages: List[Dict[str, str]], 
                         options: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate response from Ollama model
        
        Args:
            model: Model name
            messages: List of messages in OpenAI format
            options: Ollama options (tmpr, top_p, etc.)
            
        Returns:
            Model response content
        """
        start_time = time.time()
        try:
            # Set default options
            ollama_options = {
                "tmpr": 0.7,
                "top_p": 0.9
            }
            
            # Update with provided options
            if options:
                ollama_options.update(options)
                
            # Call model
            logger.debug(f"Calling Ollama model {model} with options {ollama_options}")
            response = self.client.chat(
                model=model,
                messages=messages,
                options=ollama_options
            )
            elapsed_time = time.time() - start_time
            logger.debug(f"Ollama model {model} response received in {elapsed_time:.2f}s")
            
            return response['message']['content']
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Ollama model {model} call failed after {elapsed_time:.2f}s: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
            
    def list_models(self) -> List[str]:
        """
        List available models

        Returns:
            List of model names
        """
        try:
            models_response = self.client.list()
            # The structure is a ListResponse with a 'models' field containing a list of Model objects
            all_models = [model.model for model in models_response.models]
            # Filter out embedding models
            embedding_models = ['nomic-embed-text:latest', 'all-minilm:latest', 'mxbai-embed-large:latest']
            return [model for model in all_models if model not in embedding_models]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
            
    def is_available(self) -> bool:
        """
        Check if Ollama service is available
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama service not available: {e}")
            return False