"""
Retry Manager Service
Handles retry logic with incremental delays for robust assessment execution.
"""

import time
import traceback
from typing import Callable, Any, Optional
from datetime import datetime


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(self, max_retries: int = 3, delays: list = None):
        self.max_retries = max_retries
        # Default delays: 60s, 120s, 180s
        self.delays = delays or [60, 120, 180]


class RetryManager:
    """Manages retry logic with incremental delays"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Optional[Any]:
        """
        Execute an operation with retry logic and incremental delays.
        
        Args:
            operation: The callable to execute
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            The result of the operation if successful, otherwise None
        """
        last_exception = None
        
        # Try up to max_retries + 1 times (initial attempt + retries)
        for attempt in range(self.config.max_retries + 1):
            try:
                print(f"Attempt {attempt + 1}/{self.config.max_retries + 1}", flush=True)
                result = operation(*args, **kwargs)
                print(f"Operation completed successfully on attempt {attempt + 1}", flush=True)
                return result
            except Exception as e:
                last_exception = e
                print(f"Exception occurred on attempt {attempt + 1}: {e}", flush=True)
                traceback.print_exc()
                
                # If we haven't exhausted retries, wait before retrying
                if attempt < self.config.max_retries:
                    delay = self.config.delays[attempt] if attempt < len(self.config.delays) else self.config.delays[-1]
                    print(f"Retrying in {delay} seconds...", flush=True)
                    time.sleep(delay)
        
        # All attempts failed
        print(f"All {self.config.max_retries + 1} attempts failed", flush=True)
        return None


# Example usage:
# config = RetryConfig(max_retries=3, delays=[60, 120, 180])
# manager = RetryManager(config)
# 
# def my_operation():
#     # Some operation that might fail
#     pass
# 
# result = manager.execute_with_retry(my_operation)