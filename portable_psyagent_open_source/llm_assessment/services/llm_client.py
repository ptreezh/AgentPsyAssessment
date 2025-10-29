"""
LLM Client for AgentPsy
Based on testLLM/TestLLM.py and testLLM/scripts/utils/utils.py
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

from .model_manager import ModelManager

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    """LLM client for AgentPsy"""
    
    def __init__(self, mock_mode=False):
        """Initialize LLM client"""
        self.mock_mode = mock_mode
        self.model_manager = ModelManager()
        self.provider = os.getenv("PROVIDER", "")  # '' for both, 'local' for Ollama or 'cloud' for cloud services
        
        # Initialize based on provider
        if self.provider == "local":
            self.local_api_base = os.getenv("LOCAL_API_BASE", "http://localhost:11434")
            self.local_api_key = os.getenv("LOCAL_API_KEY", "ollama")
            self.local_model_id = os.getenv("LOCAL_MODEL_ID")
        elif self.provider == "cloud":
            # Cloud models are handled by the model manager
            pass
        elif self.provider == "":
            # When provider is empty, we will try to get both local and cloud models
            self.local_api_base = os.getenv("LOCAL_API_BASE", "http://localhost:11434")
            self.local_api_key = os.getenv("LOCAL_API_KEY", "ollama")
            self.local_model_id = os.getenv("LOCAL_MODEL_ID")
        else:
            raise ValueError(f"Invalid PROVIDER in .env: {self.provider}")

        # --- DIAGNOSTIC PRINT --- #
        print("\n--- LLMClient Initialized with following config ---", flush=True)
        print(f"  PROVIDER: {self.provider}", flush=True)
        print(f"  LOCAL_API_BASE: {self.local_api_base}", flush=True)
        print(f"  LOCAL_API_KEY: {self.local_api_key}", flush=True)
        print("----------------------------------------------------\n", flush=True)
            
    def get_model_id(self) -> str:
        """
        Get current model ID
        
        Returns:
            Model identifier
        """
        if self.provider == "local":
            return self.local_model_id
        else:
            # For cloud provider, we would need to get this from the model manager
            # For now, we'll just return a placeholder
            return "cloud/model"
            
    def generate_response(self, messages: List[Dict[str, str]], 
                         model_identifier: Optional[str] = None,
                         options: Optional[Dict[str, Any]] = None,
                         timeout: int = 0) -> Optional[str]:
        """
        Generate response from LLM
        
        Args:
            messages: List of messages in OpenAI format
            model_identifier: Specific model to use (optional)
            options: Generation options (tmpr, max_tokens, etc.)
            
        Returns:
            Model response or None if failed
        """
        if self.mock_mode:
            return "This is a mock response."
        try:
            # Determine if we're using a cloud model (has slash and not starting with ollama/)
            # For Ollama models, the identifier starts with "ollama/" or is in format "namespace/model:tag"
            is_cloud_model = (model_identifier and 
                             "/" in model_identifier and 
                             not model_identifier.startswith("ollama/") and
                             not (":" in model_identifier and len(model_identifier.split("/")) == 2))
            
            if (self.provider == "local" or self.provider == "") and not is_cloud_model:
                # Use OpenAI client for local models (Ollama)
                # Robustly construct the final URL for the OpenAI client
                final_url = self.local_api_base.rstrip('/')
                if final_url.endswith('/v1'):
                    final_url = final_url[:-3]
                final_url += '/v1'
                
                client = OpenAI(base_url=final_url, api_key=self.local_api_key)
                model_id = model_identifier or self.local_model_id

                # For Ollama, we should use the full model identifier as it appears in Ollama
                # The previous approach of stripping prefix was incorrect
                actual_model_id = model_id
                
                # Convert options to OpenAI format
                openai_options = {}
                if options:
                    if "tmpr" in options:
                        openai_options["temperature"] = options["tmpr"]
                    if "max_tokens" in options:
                        openai_options["max_tokens"] = options["max_tokens"]
                        
                # 如果timeout为0，则不设置超时限制
                start_time = time.time()
                try:
                    if timeout > 0:
                        logger.debug(f"Calling local model {actual_model_id} with timeout {timeout}s")
                        response = client.chat.completions.create(
                            model=actual_model_id, # Use the corrected model ID
                            messages=messages,
                            timeout=timeout,
                            **openai_options
                        )
                    else:
                        logger.debug(f"Calling local model {actual_model_id} with no timeout")
                        response = client.chat.completions.create(
                            model=actual_model_id, # Use the corrected model ID
                            messages=messages,
                            **openai_options
                        )
                    elapsed_time = time.time() - start_time
                    logger.debug(f"Local model {actual_model_id} response received in {elapsed_time:.2f}s")
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    logger.error(f"Local model {actual_model_id} call failed after {elapsed_time:.2f}s: {e}")
                    raise
                return response.choices[0].message.content
                
            else:
                # Use model manager for cloud models or when provider is not explicitly local
                model_id = model_identifier or self.get_model_id()
                # For cloud models, we need to ensure the model is loaded
                if is_cloud_model:
                    # Check if model is already loaded, if not, load it
                    if not self.model_manager.is_model_ready(model_id):
                        if not self.model_manager.load_model(model_id):
                            logger.error(f"Failed to load cloud model: {model_id}")
                            return None
                start_time = time.time()
                try:
                    logger.debug(f"Calling cloud model {model_id}")
                    response = self.model_manager.generate_response(messages, model_id, options)
                    elapsed_time = time.time() - start_time
                    logger.debug(f"Cloud model {model_id} response received in {elapsed_time:.2f}s")
                    return response
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    logger.error(f"Cloud model {model_id} call failed after {elapsed_time:.2f}s: {e}")
                    raise
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # 在调试模式下重新抛出异常以获取完整的堆栈跟踪
            if os.getenv("DEBUG", "").lower() in ("1", "true"):
                raise
            return None
            
    def list_models(self) -> List[str]:
        """
        List available models from both local and cloud providers
        
        Returns:
            List of model identifiers
        """
        all_models = []
        
        # Add local models if provider is local
        if self.provider == "local":
            # For local provider, query Ollama directly
            from .ollama_service import OllamaService
            # Remove /v1 suffix if present
            host = self.local_api_base.rstrip('/v1')
            service = OllamaService(host)
            local_models = service.list_models()
            all_models.extend(local_models)
        
        # Add cloud models if provider is cloud
        if self.provider == "cloud":
            cloud_models = self.model_manager.get_available_models()
            all_models.extend(cloud_models)
            
        # If provider is not set or is neither local nor cloud, try both
        if self.provider not in ["local", "cloud"]:
            # Try to get local models
            try:
                from .ollama_service import OllamaService
                host = self.local_api_base.rstrip('/v1') if self.local_api_base else "http://localhost:11434"
                service = OllamaService(host)
                local_models = service.list_models()
                all_models.extend(local_models)
            except Exception as e:
                logger.warning(f"Could not get local models: {e}")
            
            # Try to get cloud models
            try:
                cloud_models = self.model_manager.get_available_models()
                all_models.extend(cloud_models)
            except Exception as e:
                logger.warning(f"Could not get cloud models: {e}")
        
        return all_models
            
    def is_model_available(self, model_identifier: str) -> bool:
        """
        Check if a model is available
        
        Args:
            model_identifier: Model identifier to check
            
        Returns:
            True if model is available, False otherwise
        """
        if self.provider == "local":
            # For local provider, check if it's the configured model
            return model_identifier == self.local_model_id
        else:
            # For cloud provider, use model manager
            return self.model_manager.is_model_ready(model_identifier)