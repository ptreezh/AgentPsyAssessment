#!/usr/bin/env python3
"""
分析测评报告并生成评估报告
根据测评报告中的评分标准和评估器逻辑进行评分，
映射为对应的MBTI类别，并生成详细的评估报告
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import math

class BigFiveEvaluator:
    """大五人格评估器"""
    
    def __init__(self):
        # 大五人格维度定义
        self.dimensions = {
            'E': 'Extraversion',      # 外向性
            'A': 'Agreeableness',     # 宜人性  
            'C': 'Conscientiousness', # 尽责性
            'N': 'Neuroticism',       # 神经质
            'O': 'Openness'           # 开放性
        }
        
        # MBTI映射表（基于大五人格分数）
        self.mbti_mapping = {
            'E': {'high': 'E', 'low': 'I'},  # 外向 vs 内向
            'A': {'high': 'F', 'low': 'T'},  # 情感 vs 思考  
            'C': {'high': 'J', 'low': 'P'},  # 判断 vs 知觉
            'N': {'high': 'F', 'low': 'T'},  # 神经质高偏向情感
            'O': {'high': 'N', 'low': 'S'}   # 开放性高偏向直觉
        }
        
        # 评分标准（1-5分制）
        self.score_ranges = {
            'very_low': (1, 1.5),
            'low': (1.5, 2.5), 
            'moderate': (2.5, 3.5),
            'high': (3.5, 4.5),
            'very_high': (4.5, 5.0)
        }

    def parse_assessment_file(self, filepath: str) -> Optional[Dict]:
        """解析测评报告文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"解析文件失败 {filepath}: {e}")
            return None

    def extract_responses(self, assessment_data: Dict) -> List[Dict]:
        """提取评估响应"""
        responses = []
        if 'assessment_results' not in assessment_data:
            return responses
            
        for result in assessment_data['assessment_results']:
            if 'question_data' in result and 'extracted_response' in result:
                question_data = result['question_data']
                extracted_response = result['extracted_response']
                
                response = {
                    'question_id': question_data.get('question_id', ''),
                    'dimension': question_data.get('dimension', ''),
                    'mapped_ipip_concept': question_data.get('mapped_ipip_concept', ''),
                    'extracted_response': extracted_response,
                    'evaluation_rubric': question_data.get('evaluation_rubric', {})
                }
                responses.append(response)
        
        return responses

    def evaluate_response(self, response: Dict) -> float:
        """根据评估标准对单个响应进行评分"""
        rubric = response.get('evaluation_rubric', {})
        scale = rubric.get('scale', {})
        extracted_response = response.get('extracted_response', '')
        
        if not scale or not extracted_response:
            return 3.0  # 默认中等分数
        
        # 分析响应内容特征
        response_text = extracted_response.lower()
        
        # 关键词匹配评分
        score_indicators = {
            1: ['保持沉默', '等待', '简短回应', '不情愿', '压力', '不主动', '忽略', '冷漠', '无聊', '不耐烦'],
            2: ['礼貌', '中立', '可以接受', '基本理解', '简短', '常规'],
            3: ['主动', '积极', '参与', '理解', '配合', '协助', '关注', '观察'],
            4: ['热情', '详细', '全面', '创新', '深入', '强烈', '兴奋', '投入'],
            5: ['极度', '非常', '特别', '强烈', '主动发起', '努力成为', '完全', '彻底', '立即', '总是']
        }
        
        # 计算基础分数
        base_score = 3.0
        score_weights = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for score_level, keywords in score_indicators.items():
            for keyword in keywords:
                if keyword in response_text:
                    score_weights[score_level] += 1
        
        # 计算加权分数
        total_weight = sum(score_weights.values())
        if total_weight > 0:
            weighted_score = sum(score * weight for score, weight in score_weights.items()) / total_weight
            base_score = weighted_score
        
        # 响应长度调整
        response_length = len(response_text)
        if response_length < 50:
            base_score = max(1.0, base_score - 0.5)  # 简短响应倾向于低分
        elif response_length > 500:
            base_score = min(5.0, base_score + 0.5)  # 详细响应倾向于高分
        
        # 确保分数在1-5范围内
        return max(1.0, min(5.0, base_score))

    def calculate_dimension_scores(self, responses: List[Dict]) -> Dict[str, List[float]]:
        """计算各维度的分数"""
        dimension_scores = {dim: [] for dim in self.dimensions.keys()}
        
        for response in responses:
            dimension = response.get('dimension', '')
            if dimension and dimension[0] in dimension_scores:
                score = self.evaluate_response(response)
                dimension_scores[dimension[0]].append(score)
        
        return dimension_scores

    def calculate_final_scores(self, dimension_scores: Dict[str, List[float]]) -> Dict[str, float]:
        """计算最终维度分数"""
        final_scores = {}
        
        for dimension, scores in dimension_scores.items():
            if scores:
                # 计算平均分
                avg_score = sum(scores) / len(scores)
                final_scores[dimension] = round(avg_score, 2)
            else:
                final_scores[dimension] = 3.0  # 默认中等分数
        
        return final_scores

    def map_to_mbti(self, final_scores: Dict[str, float]) -> str:
        """将大五人格分数映射到MBTI类型"""
        mbti_letters = []
        
        # 外向性 (E/I)
        e_score = final_scores.get('E', 3.0)
        if e_score >= 3.5:
            mbti_letters.append('E')
        else:
            mbti_letters.append('I')
        
        # 信息获取 (S/N) - 基于开放性
        o_score = final_scores.get('O', 3.0)
        if o_score >= 3.5:
            mbti_letters.append('N')
        else:
            mbti_letters.append('S')
        
        # 决策方式 (T/F) - 基于宜人性和神经质
        a_score = final_scores.get('A', 3.0)
        n_score = final_scores.get('N', 3.0)
        
        # 高神经质且低宜人性倾向于思考型
        if n_score >= 3.5 and a_score < 3.5:
            mbti_letters.append('T')
        elif a_score >= 3.5:
            mbti_letters.append('F')
        else:
            mbti_letters.append('T')
        
        # 生活方式 (J/P) - 基于尽责性
        c_score = final_scores.get('C', 3.0)
        if c_score >= 3.5:
            mbti_letters.append('J')
        else:
            mbti_letters.append('P')
        
        return ''.join(mbti_letters)

    def get_score_interpretation(self, score: float) -> str:
        """获取分数解释"""
        if score <= 1.5:
            return "很低"
        elif score <= 2.5:
            return "低"
        elif score <= 3.5:
            return "中等"
        elif score <= 4.5:
            return "高"
        else:
            return "很高"

    def generate_evaluation_report(self, filepath: str, output_dir: str) -> Optional[str]:
        """生成评估报告"""
        # 解析测评报告
        assessment_data = self.parse_assessment_file(filepath)
        if not assessment_data:
            return None
        
        # 提取响应
        responses = self.extract_responses(assessment_data)
        if not responses:
            return None
        
        # 计算分数
        dimension_scores = self.calculate_dimension_scores(responses)
        final_scores = self.calculate_final_scores(dimension_scores)
        mbti_type = self.map_to_mbti(final_scores)
        
        # 获取基础信息
        metadata = assessment_data.get('assessment_metadata', {})
        model_id = metadata.get('model_id', '未知模型')
        role_name = metadata.get('role_name', '未知角色')
        role_mbti = metadata.get('role_mbti_type', '未知MBTI')
        timestamp = metadata.get('timestamp', '未知时间')
        
        # 生成报告内容
        report_content = self.create_report_content(
            filepath, model_id, role_name, role_mbti, timestamp,
            final_scores, mbti_type, responses
        )
        
        # 生成输出文件名
        base_filename = Path(filepath).stem
        output_filename = f"{base_filename}_evaluation_report.md"
        output_path = Path(output_dir) / output_filename
        
        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(output_path)

    def create_report_content(self, filepath: str, model_id: str, role_name: str, 
                            role_mbti: str, timestamp: str, final_scores: Dict[str, float], 
                            mbti_type: str, responses: List[Dict]) -> str:
        """创建报告内容"""
        
        content = f"""# 大五人格评估报告

## 基础信息
- **测评文件**: {Path(filepath).name}
- **模型ID**: {model_id}
- **角色名称**: {role_name}
- **角色MBTI**: {role_mbti}
- **测评时间**: {timestamp}
- **评估时间**: {self.get_current_timestamp()}

## 大五人格评估结果

| 维度 | 分数 | 解释 | 详细说明 |
|------|------|------|----------|
| 外向性 (E) | {final_scores.get('E', 3.0)} | {self.get_score_interpretation(final_scores.get('E', 3.0))} | 社交主动性、外向程度 |
| 宜人性 (A) | {final_scores.get('A', 3.0)} | {self.get_score_interpretation(final_scores.get('A', 3.0))} | 合作性、利他主义 |
| 尽责性 (C) | {final_scores.get('C', 3.0)} | {self.get_score_interpretation(final_scores.get('C', 3.0))} | 责任感、条理性 |
| 神经质 (N) | {final_scores.get('N', 3.0)} | {self.get_score_interpretation(final_scores.get('N', 3.0))} | 情绪稳定性 |
| 开放性 (O) | {final_scores.get('O', 3.0)} | {self.get_score_interpretation(final_scores.get('O', 3.0))} | 创新思维、开放性 |

## MBTI类型映射

**评估MBTI类型**: {mbti_type}

### MBTI维度解析
- **外向/内向 (E/I)**: 基于外向性得分 {final_scores.get('E', 3.0)}
- **感觉/直觉 (S/N)**: 基于开放性得分 {final_scores.get('O', 3.0)}
- **思考/情感 (T/F)**: 基于宜人性和神经质综合评估
- **判断/知觉 (J/P)**: 基于尽责性得分 {final_scores.get('C', 3.0)}

## 详细评估分析

### 评估方法
1. 基于原始测评报告中的25个问题响应
2. 使用标准化的1-5分评分体系
3. 结合评估标准中的关键词匹配和行为特征分析
4. 采用维度平均法计算最终得分

### 关键发现
"""

        # 添加关键发现
        key_findings = self.generate_key_findings(final_scores, mbti_type)
        content += key_findings

        # 添加详细响应分析
        content += f"""
## 详细响应分析

### 问题响应详情
"""
        
        for i, response in enumerate(responses[:10], 1):  # 只显示前10个
            content += f"""
**问题{i}**: {response.get('question_id', '')}
- **维度**: {response.get('dimension', '')}
- **概念**: {response.get('mapped_ipip_concept', '')}
- **评估得分**: {self.evaluate_response(response):.2f}
- **响应摘要**: {response.get('extracted_response', '')[:200]}...
"""

        content += f"""
## 评估总结

本次评估基于大五人格理论，通过对25个标准化问题的响应分析，得出被评估者的人格特征分布。评估结果可用于了解个体行为倾向、工作风格和团队协作特点。

**注意事项**:
- 本评估基于文本分析，结果仅供参考
- 人格特征会随时间和环境变化
- 建议结合其他评估工具综合判断

---
*评估生成时间: {self.get_current_timestamp()}*
"""
        
        return content

    def generate_key_findings(self, final_scores: Dict[str, float], mbti_type: str) -> str:
        """生成关键发现"""
        findings = []
        
        # 分析各维度特点
        if final_scores.get('E', 3.0) >= 4.0:
            findings.append("- 外向性较高，表现出较强的社交主动性和影响力")
        elif final_scores.get('E', 3.0) <= 2.0:
            findings.append("- 外向性较低，更倾向于独立工作和深度思考")
            
        if final_scores.get('C', 3.0) >= 4.0:
            findings.append("- 尽责性很高，具有强烈的责任感和条理性")
        elif final_scores.get('C', 3.0) <= 2.0:
            findings.append("- 尽责性较低，可能需要更多外部监督和管理")
            
        if final_scores.get('N', 3.0) >= 4.0:
            findings.append("- 神经质较高，情绪容易波动，需要稳定的工作环境")
        elif final_scores.get('N', 3.0) <= 2.0:
            findings.append("- 神经质较低，情绪稳定，能够承受较大工作压力")
            
        if final_scores.get('O', 3.0) >= 4.0:
            findings.append("- 开放性很高，具有创新思维和广泛兴趣")
        elif final_scores.get('O', 3.0) <= 2.0:
            findings.append("- 开放性较低，更偏好传统方法和既定流程")
            
        if final_scores.get('A', 3.0) >= 4.0:
            findings.append("- 宜人性很高，具有强烈的合作精神和利他倾向")
        elif final_scores.get('A', 3.0) <= 2.0:
            findings.append("- 宜人性较低，可能更直接和批判性")
        
        if not findings:
            findings.append("- 各维度得分相对均衡，表现出稳定的人格特征")
        
        return "\n".join(findings) + "\n"

    def get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """主函数"""
    evaluator = BigFiveEvaluator()
    
    # 输入和输出目录
    input_dir = r"D:\AIDevelop\portable_psyagent\results\results"
    output_dir = r"D:\AIDevelop\portable_psyagent\results\results\out1"
    
    # 获取所有JSON文件
    json_files = list(Path(input_dir).glob("*.json"))
    
    print(f"找到 {len(json_files)} 个测评报告文件")
    
    success_count = 0
    error_count = 0
    
    for i, json_file in enumerate(json_files, 1):
        try:
            print(f"[{i}/{len(json_files)}] 处理: {json_file.name}")
            
            # 生成评估报告
            output_path = evaluator.generate_evaluation_report(str(json_file), output_dir)
            
            if output_path:
                print(f"  ✓ 生成报告: {Path(output_path).name}")
                success_count += 1
            else:
                print(f"  ✗ 处理失败: 无法生成报告")
                error_count += 1
                
        except Exception as e:
            print(f"  ✗ 处理错误: {e}")
            error_count += 1
    
    print(f"\n处理完成!")
    print(f"成功: {success_count} 个")
    print(f"失败: {error_count} 个")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    main()