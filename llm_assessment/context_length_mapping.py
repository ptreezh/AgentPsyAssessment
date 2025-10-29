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