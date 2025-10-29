"""
验证A/T维度是否已正确集成到评估系统
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 测试直接导入和使用
from at_dimension import neuroticism_to_at_type, get_at_description

print("=== A/T维度功能测试 ===")
print(f"高神经质分数(9.0) -> A/T类型: {neuroticism_to_at_type(9.0)} ({get_at_description(neuroticism_to_at_type(9.0))})")
print(f"低神经质分数(3.0) -> A/T类型: {neuroticism_to_at_type(3.0)} ({get_at_description(neuroticism_to_at_type(3.0))})")
print(f"边界分数(5.0) -> A/T类型: {neuroticism_to_at_type(5.0)} ({get_at_description(neuroticism_to_at_type(5.0))})")

# 测试与现有评估结果的集成
sample_result = {
    'big_five': {
        'openness_to_experience': {'score': 8.2},
        'conscientiousness': {'score': 9.4},
        'extraversion': {'score': 7.0},
        'agreeableness': {'score': 8.7},
        'neuroticism': {'score': 9.0}  # 高神经质 -> T (Turbulent)
    },
    'mbti': {'type': 'INFJ', 'confidence': 0.56},
    'belbin': {'primary_role': 'RI', 'secondary_role': 'CF'}
}

from at_dimension import add_at_dimension_to_result
enhanced_result = add_at_dimension_to_result(sample_result)

print("\n=== 集成测试 ===")
print("原始结果包含的键:", list(sample_result.keys()))
print("增强结果包含的键:", list(enhanced_result.keys()))
print("A/T类型:", enhanced_result.get('at_type'))
print("A/T描述:", enhanced_result.get('at_description'))

# 验证A/T维度正确添加
assert 'at_type' in enhanced_result, "A/T类型未正确添加到结果中"
assert 'at_description' in enhanced_result, "A/T描述未正确添加到结果中"
assert enhanced_result['at_type'] == 'T', f"期望A/T类型为T，实际为{enhanced_result['at_type']}"
assert enhanced_result['at_description'] == 'Turbulent', f"期望A/T描述为Turbulent，实际为{enhanced_result['at_description']}"

print("\n✓ 所有测试通过！A/T维度已成功集成到评估系统中")
print("✓ 现在评估系统将提供Big Five + MBTI + Belbin + A/T的完整人格分析")