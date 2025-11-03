#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复分段评分评估器的编码问题
"""

import re


def fix_segmented_scoring_evaluator():
    """修复segmented_scoring_evaluator.py文件的编码问题"""
    
    # 完整的正确函数定义
    new_function_code = '''    def _create_segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """
        创建分段评分提示
        """
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**以下问卷回答，评估回答者展现的Big5人格特质。

**关键提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**严格评分标准：**
- **1分**：极低表现 - 明显缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **5分**：极高表现 - 明确具备该特质

**特别注意：只能使用1、3、5三个整数分数，严禁使用2、4等其他数值！**

**第{segment_number}段问卷内容（{len(segment)}题/共{total_segments}段）：**
"""

        for i, item in enumerate(segment, 1):
            question_data = item.get('question_data', {})
            prompt += f"""
**问题 {i}:**
{question_data.get('mapped_ipip_concept', '')}

**场景 {i}:**
{question_data.get('scenario', '')}

**指令 {i}:**
{question_data.get('prompt_for_agent', '')}

**AI回答 {i}:**
{item.get('extracted_response', '')}

---
"""

        prompt += """
**请返回严格的JSON格式：**
```json
{
  "success": true,
  "segment_number": {segment_number},
  "analysis_summary": "简要分析总结",
  "scores": {
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  },
  "evidence": {
    "openness_to_experience": "具体证据引用",
    "conscientiousness": "具体证据引用",
    "extraversion": "具体证据引用",
    "agreeableness": "具体证据引用",
    "neuroticism": "具体证据引用"
  },
  "confidence": "high/medium/low"
}
```

**再次提醒：每个评分必须是1、3或5，不能使用其他数值！**
"""

        return prompt

    def _create_question_by_question_prompt(self, question: Dict, question_number: int, total_questions: int) -> str:
        """
        创建单题评分提示 - 针对单题进行分析
        """
        question_data = question.get('question_data', {})
        
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**单个问卷回答，评估回答者在该问题上展现的Big5人格特质。

**关键提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**严格评分标准：**
- **1分**：极低表现 - 明显缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **5分**：极高表现 - 明确具备该特质

**特别注意：只能使用1、3、5三个整数分数，严禁使用2、4等其他数值！**

**第{question_number}道问卷内容（共{total_questions}道题）：**

**问题:**
{question_data.get('mapped_ipip_concept', '')}

**场景:**
{question_data.get('scenario', '')}

**指令:**
{question_data.get('prompt_for_agent', '')}

**AI回答:**
{question.get('extracted_response', '')}

**请返回严格的JSON格式：**
```json
{{
  "success": true,
  "question_number": {question_number},
  "analysis_summary": "简要分析总结",
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }},
  "evidence": {{
    "openness_to_experience": "具体证据引用",
    "conscientiousness": "具体证据引用",
    "extraversion": "具体证据引用",
    "agreeableness": "具体证据引用",
    "neuroticism": "具体证据引用"
  }},
  "confidence": "high/medium/low"
}}
```

**再次提醒：每个评分必须是1、3或5，不能使用其他数值！**
"""

        return prompt
'''

    # 读取原始文件
    with open('segmented_scoring_evaluator.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 替换有问题的函数定义
    # 找到函数开始位置
    start_pos = content.find('def _create_segment_prompt')
    if start_pos == -1:
        print("错误：未找到 _create_segment_prompt 函数")
        return False
    
    # 找到下一个函数定义的开始作为结束位置
    next_def_pos = content.find('def _validate_scores', start_pos)
    if next_def_pos == -1:
        print("错误：未找到下一个函数定义")
        return False
    
    # 替换整个函数定义部分
    new_content = content[:start_pos] + new_function_code + content[next_def_pos:]
    
    # 写回文件
    with open('segmented_scoring_evaluator.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 函数代码已修复")
    return True


if __name__ == "__main__":
    fix_segmented_scoring_evaluator()
    print("修复完成")