#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新修复分段评分评估器的缩进问题
"""

def fix_indentation():
    """修复缩进问题"""
    with open('segmented_scoring_evaluator.py', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # 找到出错的位置 - 需要移除错误添加的缩进
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # 检查是否是函数定义行缩进了错误的空格
        if line.strip().startswith('def _create_segment_prompt') and line.startswith('        '):
            # 这一行的缩进是错误的，需要重新格式化
            print(f"修复第 {i+1} 行的缩进问题")
            # 找到这个函数的完整定义
            func_start = i
            # 找到下一个正确缩进的def或类结束
            func_end = i
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith('def ') and not lines[j].startswith('        '):
                    func_end = j
                    break
                elif lines[j].startswith('    def ') or lines[j].startswith('class ') or (lines[j].strip() == '' and j > i+10):
                    # 一些明显的标记
                    next_line = j
                    while next_line < len(lines) and lines[next_line].strip() == '':
                        next_line += 1
                    if next_line < len(lines) and (lines[next_line].startswith('    def ') or lines[next_line].startswith('class ')):
                        func_end = next_line
                        break
            # 修复这些行的缩进
            for k in range(func_start, func_end):
                orig_line = lines[k]
                if orig_line.startswith('        '):
                    fixed_line = orig_line[4:]  # 移除4个空格
                else:
                    fixed_line = orig_line
                fixed_lines.append(fixed_line)
            i = func_end
        else:
            fixed_lines.append(line)
            i += 1

    # 写回文件
    with open('segmented_scoring_evaluator.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ 缩进问题已修复")


def add_new_function():
    """添加新的函数定义"""
    with open('segmented_scoring_evaluator.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 _validate_scores 函数的位置，然后在其后添加新函数
    pos = content.find('def _validate_scores')
    if pos == -1:
        print("错误：未找到 _validate_scores 函数")
        return False
    
    # 找到这个函数定义的结束位置（下一个def的位置）
    next_pos = content.find('def _analyze_segment_with_model', pos)
    if next_pos == -1:
        print("错误：未找到下一个函数")
        return False
    
    # 创建正确缩进的新函数
    new_function_code = '''
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
    
    # 在找到的位置插入新函数
    new_content = content[:next_pos] + new_function_code + content[next_pos:]
    
    with open('segmented_scoring_evaluator.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 新函数已添加")
    return True


if __name__ == "__main__":
    fix_indentation()
    add_new_function()
    print("修复完成")