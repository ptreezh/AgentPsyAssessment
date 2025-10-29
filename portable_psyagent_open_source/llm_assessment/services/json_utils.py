import json
import json5
import os

def load_json_file(filepath, auto_fix=True):
    """
    安全地加载JSON文件，具有多种容错机制
    
    Args:
        filepath (str): JSON文件路径
        auto_fix (bool): 是否自动尝试修复JSON格式错误
    
    Returns:
        dict or None: 解析后的JSON数据，如果失败则返回None
    """
    # 检查文件是否存在
    if not os.path.exists(filepath):
        print(f"Error: File not found - {filepath}")
        return None
    
    # 尝试使用标准JSON解析器
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Standard JSON parsing failed for '{filepath}': {e}")
    except Exception as e:
        print(f"Error: Failed to read file '{filepath}': {e}")
        return None
    
    # 尝试使用JSON5解析器（更宽松的格式）
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json5.load(f)
    except Exception as e:
        print(f"Warning: JSON5 parsing failed for '{filepath}': {e}")
    
    # 如果允许自动修复，尝试修复文件
    if auto_fix:
        try:
            print(f"Attempting to fix JSON format for '{filepath}'...")
            if fix_json_file(filepath):
                # 修复成功后再次尝试加载
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Failed to fix JSON format for '{filepath}'")
        except Exception as e:
            print(f"Error: Failed to fix and load file '{filepath}': {e}")
    
    print(f"Error: Unable to load JSON file '{filepath}' with any method")
    return None

def fix_json_file(file_path):
    """
    尝试修复JSON文件中的常见格式错误
    
    Args:
        file_path (str): JSON文件路径
    
    Returns:
        bool: 修复是否成功
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析原始内容
        try:
            json.loads(content)
            print("File is already valid JSON")
            return True
        except json.JSONDecodeError:
            pass  # 继续修复过程
        
        # 尝试修复常见的格式问题
        import re
        
        # 1. 移除对象或数组最后一个元素后的逗号
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        
        # 2. 确保所有键都用双引号包围（这是一个简化的方法，可能不适用于所有情况）
        # 这个修复比较复杂，需要更精确的处理，这里我们只处理最常见的情况
        
        # 再次尝试解析
        data = json.loads(content)
        
        # 保存修复后的内容
        backup_path = file_path + ".backup"
        os.rename(file_path, backup_path)
        print(f"Original file backed up as: {backup_path}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Fixed file saved to: {file_path}")
        return True
        
    except Exception as e:
        print(f"Failed to fix JSON file: {e}")
        return False

def validate_json_file(file_path):
    """
    验证JSON文件格式
    
    Args:
        file_path (str): JSON文件路径
    
    Returns:
        bool: 文件是否为有效JSON格式
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except Exception as e:
        print(f"JSON validation failed for '{file_path}': {e}")
        return False