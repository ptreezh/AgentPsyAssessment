#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文生成器示例实现
展示如何为每道题生成包含完整上下文的评估提示
"""

import json
from typing import Dict, List


class ContextGenerator:
    """评估上下文生成器"""
    
    def __init__(self):
        self.big_five_definitions = {
            "openness_to_experience": "开放性(O)：对新体验、创意、理论的开放程度",
            "conscientiousness": "尽责性(C)：自律、条理、可靠程度",
            "extraversion": "外向性(E)：社交活跃度、能量来源",
            "agreeableness": "宜人性(A)：合作、同理心、信任倾向",
            "neuroticism": "神经质(N)：情绪稳定性、焦虑倾向"
        }
        
        self.scoring_criteria = {
            1: "极低表现 - 明显缺乏该特质",
            3: "中等表现 - 平衡或不确定，有该特质也有反例",
            5: "极高表现 - 明确具备该特质"
        }

    def generate_evaluation_prompt(self, question_info: Dict) -> str:
        """
        为单道题生成完整的评估上下文
        
        Args:
            question_info: 包含题目信息的字典，来自原始测评报告的assessment_results中的单个条目
            
        Returns:
            完整的评估提示字符串
        """
        # 提取question_data中的信息
        question_data = question_info.get('question_data', {})
        
        # 检测是否为反向计分题（如果mapped_ipip_concept包含"(Reversed)"或": (Reversed)"）
        mapped_concept = question_data.get('mapped_ipip_concept', '')
        is_reversed = '(Reversed)' in mapped_concept or ': (Reversed)' in mapped_concept
        
        # 构建大五人格定义部分
        definitions_part = "【大五人格维度定义】\n"
        for trait_key, definition in self.big_five_definitions.items():
            trait_num = list(self.big_five_definitions.keys()).index(trait_key) + 1
            definitions_part += f"{trait_num}. {definition}\n"
        
        # 构建评分标准部分
        criteria_part = "\n【评分标准】\n"
        criteria_part += "严格按照1-3-5评分制，仅使用这3个整数分数：\n"
        for score, description in self.scoring_criteria.items():
            criteria_part += f"- {score}分：{description}\n"
        
        # 构建问题信息部分
        question_part = f"\n【问题信息】\n"
        question_part += f"问题维度：{question_data.get('dimension', 'Unknown')}\n"
        question_part += f"问题内容：{mapped_concept}\n"
        question_part += f"场景描述：{question_data.get('scenario', 'N/A')}\n"
        question_part += f"指导语：{question_data.get('prompt_for_agent', 'N/A')}\n"
        
        # 构建评分标准细则部分（来自evaluation_rubric）
        rubric = question_data.get('evaluation_rubric', {})
        if rubric:
            rubric_part = f"\n【评分标准细则】\n"
            rubric_part += f"评估描述：{rubric.get('description', 'N/A')}\n"
            scale = rubric.get('scale', {})
            if scale:
                rubric_part += "评分等级：\n"
                for score, desc in scale.items():
                    rubric_part += f"  {score}分: {desc}\n"
            
            # 如果是反向计分题，添加特别说明
            if is_reversed:
                rubric_part += f"\n【反向计分题说明】：\n"
                rubric_part += f"本题为反向计分题，标记为 '{mapped_concept}'。\n"
                rubric_part += f"在该维度上，低分代表高特质水平，高分代表低特质水平。\n"
                rubric_part += f"例如：如果回答体现了高特质水平（如高尽责性），应评1分；\n"
                rubric_part += f"如果回答体现了低特质水平（如低尽责性），应评5分。\n"
        else:
            rubric_part = ""
        
        # 构建被试回答部分
        response_part = f"\n【被试实际回答】\n{question_info.get('extracted_response', 'N/A')}\n"
        
        # 构建指令和输出格式
        instruction_part = f"""
\n【评估任务】
请作为专业人格评估分析师，分析被试的回答在大五人格各维度上的表现。
注意：此题{'' if not is_reversed else '是'}反向计分题，{'评分时需特别注意反向计分规则' if is_reversed else '按正常计分规则进行'}。

【重要提醒】
- ❌ 你不是被试，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中体现的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向
- ✅ 严格按照1/3/5评分标准进行评估
{'- ✅ 对于反向计分题，注意低分代表高特质水平，高分代表低特质水平' if is_reversed else ''}

【输出要求】
返回严格的JSON格式：
{{
  "success": true,
  "question_id": {question_info.get('question_id', 'Unknown')},
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

【再次提醒】
每个维度的评分必须是1、3或5中的一个整数，严禁使用其他数值！
"""
        
        # 组合所有部分
        full_prompt = f"""你是专业的人格评估分析师，专门分析AI代理的大五人格特质。

{definitions_part}{criteria_part}{question_part}{rubric_part}{response_part}{instruction_part}"""
        
        return full_prompt.strip()

    def generate_batch_contexts(self, questions: List[Dict]) -> List[Dict]:
        """
        为一批问题生成评估上下文
        
        Args:
            questions: 问题列表
            
        Returns:
            包含问题ID和上下文的列表
        """
        contexts = []
        for question in questions:
            context = self.generate_evaluation_prompt(question)
            contexts.append({
                'question_id': question.get('question_id'),
                'context': context,
                'question_info': question
            })
        return contexts


def example_usage():
    """示例用法"""
    # 示例问题数据
    sample_question = {
        "question_id": 1,
        "dimension": "Extraversion",
        "mapped_ipip_concept": "E1: 我是团队活动的核心人物。",
        "scenario": "在团队项目中，你通常是组织者和推动者",
        "prompt_for_agent": "请评估这个回答在社交活跃度方面的表现",
        "extracted_response": "我确实经常在团队活动中扮演领导角色，喜欢组织大家完成任务"
    }
    
    # 创建上下文生成器
    generator = ContextGenerator()
    
    # 生成评估上下文
    context = generator.generate_evaluation_prompt(sample_question)
    
    print("生成的评估上下文示例：")
    print("="*50)
    print(context)
    print("="*50)
    
    # 测试批处理功能
    sample_questions = [sample_question] * 3  # 3个示例问题
    batch_contexts = generator.generate_batch_contexts(sample_questions)
    
    print(f"\n批处理生成了 {len(batch_contexts)} 个评估上下文")
    print(f"每个上下文平均长度: {len(batch_contexts[0]['context'])} 字符")


if __name__ == "__main__":
    example_usage()