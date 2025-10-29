def parse_tmpr_and_context_args(args):
    """
    Parse tmpr and context length arguments from CLI.
    
    Args:
        args: Parsed CLI arguments
        
    Returns:
        dict: Dictionary with tmpr and context length settings
    """
    settings = {
        'tmpr': args.tmpr,
        'context_length_mode': getattr(args, 'context_length_mode', 'auto'),
        'context_length_static': getattr(args, 'context_length_static', 0),
        'context_length_dynamic': getattr(args, 'context_length_dynamic', '1/2')
    }
    
    return settings


def apply_model_settings(client, tmpr=None, context_length=None):
    """
    Apply model settings like tmpr and context length.
    
    Args:
        client: LLMClient instance
        tmpr (float): Model tmpr setting
        context_length (str): Context length setting
        
    Returns:
        dict: Options dictionary for model generation
    """
    options = {}
    
    # Apply tmpr if specified
    if tmpr is not None:
        options['tmpr'] = tmpr
    
    # Apply context length if specified (this would be used in prompt construction)
    if context_length is not None:
        options['context_length'] = context_length
    
    return options


def get_model_max_context_length(model_id):
    """
    Get the maximum context length for a given model.
    This is a placeholder that would need to be implemented based on model info.
    
    Args:
        model_id (str): Model identifier
        
    Returns:
        int: Maximum context length in tokens, or None if unknown
    """
    # This would need to be implemented based on actual model information
    # For now, we'll return some common defaults based on model name
    model_defaults = {
        'gemma': 8192,
        'gemma3': 8192,
        'llama3': 8192,
        'mixtral': 32768,
        'phi': 4096,
        'mistral': 32768,
        'qwen': 32768,
        'qwen3': 32768,
    }
    
    # Try to match model name
    for model_prefix, max_context in model_defaults.items():
        if model_prefix in model_id.lower():
            return max_context
    
    # For unknown models, return None to indicate we don't know the context length
    return None


def calculate_dynamic_context_length(model_id, dynamic_setting):
    """
    Calculate dynamic context length based on model's maximum context length.
    
    Args:
        model_id (str): Model identifier
        dynamic_setting (str): Dynamic setting ('1/4', '1/2', '3/4', '9/10')
        
    Returns:
        int: Calculated context length in K (e.g., 4 for 4K)
    """
    max_context = get_model_max_context_length(model_id)
    
    if max_context is None:
        return 0  # Unknown model, no context injection
    
    ratios = {
        '1/4': 0.25,
        '1/2': 0.5,
        '3/4': 0.75,
        '9/10': 0.9
    }
    
    ratio = ratios.get(dynamic_setting, 0)
    calculated_length = int(max_context * ratio)
    
    # Convert to K and return
    return calculated_length // 1024


def map_static_context_length(static_param):
    """
    Map static parameter to context length in K.
    
    Args:
        static_param (int): Static parameter (0-64)
        
    Returns:
        int: Context length in K
    """
    # Direct mapping from parameter to K value
    static_mapping = {
        0: 0,     # 0K
        1: 1,     # 1K
        2: 2,     # 2K
        4: 4,     # 4K
        8: 8,     # 8K
        16: 16,   # 16K
        32: 32,   # 32K
        64: 64    # 64K
    }
    
    # If the parameter is directly in the mapping, return it
    if static_param in static_mapping:
        return static_mapping[static_param]
    
    # For values not in the mapping, return 0
    return 0


def determine_context_length(model_id, mode='auto', static_param=0, dynamic_ratio='1/2'):
    """
    Determine context length based on mode and parameters.
    
    Args:
        model_id (str): Model identifier
        mode (str): Context length mode ('auto', 'static', 'dynamic', 'none')
        static_param (int): Static parameter (0-4)
        dynamic_ratio (str): Dynamic ratio ('1/4', '1/2', '3/4', '9/10')
        
    Returns:
        tuple: (context_length_k, source) where context_length_k is in K and source indicates calculation method
    """
    if mode == 'none':
        # Explicitly disable context injection
        return 0, 'none'
    
    elif mode == 'static':
        # Use static mapping
        context_k = map_static_context_length(static_param)
        return context_k, 'static'
    
    elif mode == 'dynamic':
        # Force dynamic calculation
        context_k = calculate_dynamic_context_length(model_id, dynamic_ratio)
        return context_k, 'dynamic'
    
    else:  # auto mode (default)
        # Try to get model max context length
        max_context = get_model_max_context_length(model_id)
        
        if max_context is not None and max_context > 0:
            # Use dynamic calculation
            context_k = calculate_dynamic_context_length(model_id, dynamic_ratio)
            return context_k, 'dynamic_auto'
        else:
            # Fall back to static mapping
            context_k = map_static_context_length(static_param)
            return context_k, 'static_fallback'


if __name__ == "__main__":
    main()