#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版分段评估器 - 使用1-3-5三档评分标准
"""

import json
import sys
import os
import time

def fix_segmented_analyzer_prompt():
    """修复分段评估器的评分标准"""
    analyzer_file = "batchAnalysizeTools/batch_segmented_analysis.py"
    
    if not os.path.exists(analyzer_file):
        print("错误: 找不到分段分析器文件")
        return False
    
    try:
        # 读取文件内容
        with open(analyzer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换评分标准相关的提示词
        # 原始提示词要求1-10分评分
        old_prompt = '''You are a personality analyst. Analyze {len(segment)} questions and provide Big Five scores (1-10) for each.

For each question, assess all 5 traits:
- openness_to_experience
- conscientiousness
- extraversion
- agreeableness
- neuroticism

Scoring guidelines:
- Direct evidence: Score 1-10 based on explicit behavior
- Limited evidence: Score 5.0-7.0 using professional inference
- No evidence: Score 5.0 using professional judgment

REQUIRED JSON FORMAT:
{{
    "question_scores": [
        {{
            "question_id": "Q1",
            "dimension": "extraversion",
            "big_five_scores": {{
                "openness_to_experience": {{"score": 7, "evidence": "Evidence from response", "quality": "direct"}},
                "conscientiousness": {{"score": 6, "evidence": "Professional inference", "quality": "inferred"}},
                "extraversion": {{"score": 8, "evidence": "Direct evidence", "quality": "direct"}},
                "agreeableness": {{"score": 7, "evidence": "Inference from response", "quality": "inferred"}},
                "neuroticism": {{"score": 4, "evidence": "Evidence from response", "quality": "direct"}}
            }}
        }}
    ]
}}

Return ONLY valid JSON. All traits must have scores 1-10 with evidence. No null values.'''
        
        # 新的提示词使用1-3-5三档评分标准
        new_prompt = '''You are a personality analyst. Analyze {len(segment)} questions and provide Big Five scores (1, 3, or 5) for each, matching the original assessment scale.

For each question, assess all 5 traits using ONLY the 1-3-5 scale:
- 1: Low/Minimal expression of the trait
- 3: Moderate/Average expression of the trait  
- 5: High/Strong expression of the trait

Scoring guidelines based on evidence quality:
- Direct evidence: Score 1, 3, or 5 based on explicit behavior in the response
- Limited evidence: Score 3 using professional inference when direct evidence is weak
- No evidence: Score 3 using professional judgment when no clear evidence exists

REQUIRED JSON FORMAT:
{{
    "question_scores": [
        {{
            "question_id": "Q1",
            "dimension": "extraversion",
            "big_five_scores": {{
                "openness_to_experience": {{"score": 3, "evidence": "Evidence from response", "quality": "direct"}},
                "conscientiousness": {{"score": 3, "evidence": "Professional inference", "quality": "inferred"}},
                "extraversion": {{"score": 5, "evidence": "Direct evidence", "quality": "direct"}},
                "agreeableness": {{"score": 3, "evidence": "Inference from response", "quality": "inferred"}},
                "neuroticism": {{"score": 1, "evidence": "Evidence from response", "quality": "direct"}}
            }}
        }}
    ]
}}

Return ONLY valid JSON. All traits must have scores 1, 3, or 5 with evidence. No null values.'''
        
        # 替换提示词
        if old_prompt in content:
            content = content.replace(old_prompt, new_prompt)
            print("成功找到并替换评分标准提示词")
        else:
            print("警告: 未找到预期的提示词模式")
            return False
        
        # 保存修改后的文件
        with open(analyzer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("成功更新分段评估器的评分标准为1-3-5三档评分")
        return True
        
    except Exception as e:
        print(f"修改分段评估器时出错: {e}")
        return False

if __name__ == "__main__":
    fix_segmented_analyzer_prompt()