"""
A/T (Assertive/Turbulent) 维度模块
基于神经质维度将人格类型分为坚定型(Assertive)或动荡型(Turbulent)
"""
from typing import Dict, Any


def neuroticism_to_at_type(neuroticism_score: float) -> str:
    """
    根据神经质得分确定A/T类型
    - 神经质得分 <= 5.0: A (Assertive/坚定型)
    - 神经质得分 > 5.0: T (Turbulent/动荡型)
    
    Args:
        neuroticism_score: 神经质得分 (1-10)
        
    Returns:
        A 或 T
    """
    if neuroticism_score <= 5.0:
        return "A"
    else:
        return "T"


def get_at_description(at_type: str) -> str:
    """
    获取A/T类型的描述
    
    Args:
        at_type: A 或 T
        
    Returns:
        类型描述
    """
    descriptions = {
        "A": "Assertive",
        "T": "Turbulent"
    }
    return descriptions.get(at_type, "Unknown")


def add_at_dimension_to_result(assessment_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    向评估结果添加A/T维度信息
    
    Args:
        assessment_result: 原始评估结果
        
    Returns:
        添加了A/T维度信息的评估结果
    """
    # 复制原始结果以避免修改原始数据
    result = assessment_result.copy()
    
    # 获取神经质得分
    neuroticism_score = assessment_result["big_five"]["neuroticism"]["score"]
    
    # 计算A/T类型
    at_type = neuroticism_to_at_type(neuroticism_score)
    
    # 添加A/T信息到结果中
    result["at_type"] = at_type
    result["at_description"] = get_at_description(at_type)
    
    return result


def add_at_dimension_to_full_result(full_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    向完整评估结果添加A/T维度信息
    
    Args:
        full_result: 完整的评估结果字典
        
    Returns:
        添加了A/T维度信息的完整结果
    """
    # 检查是否已包含big_five数据
    if "big_five" not in full_result:
        raise ValueError("评估结果中缺少big_five数据")
    
    if "neuroticism" not in full_result["big_five"]:
        raise ValueError("评估结果中缺少neuroticism数据")
    
    if "score" not in full_result["big_five"]["neuroticism"]:
        raise ValueError("评估结果中neuroticism缺少score")
    
    # 复制原始结果
    result = full_result.copy()
    
    # 获取神经质得分
    neuroticism_score = full_result["big_five"]["neuroticism"]["score"]
    
    # 计算A/T类型
    at_type = neuroticism_to_at_type(neuroticism_score)
    
    # 添加A/T信息
    result["at_type"] = at_type
    result["at_description"] = get_at_description(at_type)
    
    return result


def get_at_type_detailed_info(at_type: str) -> Dict[str, str]:
    """
    获取A/T类型的详细信息
    
    Args:
        at_type: A 或 T
        
    Returns:
        包含详细信息的字典
    """
    detailed_info = {
        "A": {
            "type": "A",
            "name": "Assertive",
            "description": "坚定型人格，通常更加自信、情绪稳定，对外界压力的抗性较强",
            "characteristics": [
                "自信",
                "情绪稳定",
                "压力抗性较强",
                "较少自我怀疑",
                "决策时更果断"
            ]
        },
        "T": {
            "type": "T", 
            "name": "Turbulent",
            "description": "动荡型人格，通常更敏感、追求完美，对自身表现更关注",
            "characteristics": [
                "敏感",
                "追求完美",
                "自我反思较多",
                "对外界评价更敏感",
                "倾向于质疑自己"
            ]
        }
    }
    
    return detailed_info.get(at_type, {
        "type": "Unknown",
        "name": "Unknown",
        "description": "未知类型",
        "characteristics": []
    })


def integrate_at_with_mbti(mbti_type: str, at_type: str) -> str:
    """
    将A/T类型与MBTI类型结合表示（如INFJ-T）
    
    Args:
        mbti_type: 4字母MBTI类型
        at_type: A或T
        
    Returns:
        结合后的类型表示
    """
    return f"{mbti_type}-{at_type}"


# 简化接口函数
def get_at_type(assessment_result: Dict[str, Any]) -> str:
    """
    获取评估结果的A/T类型
    
    Args:
        assessment_result: 评估结果
        
    Returns:
        A 或 T
    """
    neuroticism_score = assessment_result["big_five"]["neuroticism"]["score"]
    return neuroticism_to_at_type(neuroticism_score)