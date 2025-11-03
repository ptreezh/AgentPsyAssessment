#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入解析器
解析原始测评报告JSON格式，提取问题和回答数据
"""

import json
from typing import List, Dict
from .context_generator import ContextGenerator


class InputParser:
    """输入解析器，用于解析原始测评报告"""
    
    def __init__(self):
        self.context_generator = ContextGenerator()
    
    def parse_assessment_json(self, file_path: str) -> List[Dict]:
        """
        解析JSON格式的测评报告
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            解析后的问题列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assessment_results = data.get('assessment_results', [])
        
        parsed_questions = []
        for item in assessment_results:
            question_data = item.get('question_data', {})
            
            parsed_question = {
                'question_id': item.get('question_id'),
                'question_data': question_data,
                'extracted_response': item.get('extracted_response', ''),
                'conversation_log': item.get('conversation_log', []),
                'session_id': item.get('session_id')
            }
            
            # 检查是否包含所有必要的字段
            required_fields = ['dimension', 'mapped_ipip_concept', 'scenario', 'prompt_for_agent']
            missing_fields = [field for field in required_fields if not question_data.get(field)]
            
            if missing_fields:
                print(f"警告: 问题 {item.get('question_id')} 缺少字段: {missing_fields}")
            
            parsed_questions.append(parsed_question)
        
        return parsed_questions
    
    def validate_data_structure(self, data: List[Dict]) -> bool:
        """
        验证解析后的数据结构
        
        Args:
            data: 解析后的问题列表
            
        Returns:
            是否结构有效
        """
        if not data:
            print("错误: 没有解析到任何问题")
            return False
        
        # 检查是否是50道题
        if len(data) != 50:
            print(f"警告: 问题数量不是50道，实际为 {len(data)} 道")
        
        # 检查第一道题的结构
        sample_question = data[0]
        required_keys = ['question_id', 'question_data', 'extracted_response']
        missing_keys = [key for key in required_keys if key not in sample_question]
        
        if missing_keys:
            print(f"错误: 数据结构不完整，缺少键: {missing_keys}")
            return False
        
        return True
    
    def prepare_question_contexts(self, parsed_questions: List[Dict]) -> List[Dict]:
        """
        为所有问题生成评估上下文
        
        Args:
            parsed_questions: 解析后的问题列表
            
        Returns:
            包含问题ID和上下文的列表
        """
        contexts = []
        for question in parsed_questions:
            context = self.context_generator.generate_evaluation_prompt(question)
            contexts.append({
                'question_id': question.get('question_id'),
                'context': context,
                'question_info': question
            })
        return contexts


def example_usage():
    """示例用法"""
    # 这里我们创建一个模拟的解析流程，因为实际文件可能很大
    parser = InputParser()
    
    # 示例问题数据结构（模拟从真实JSON中提取的数据）
    sample_question = {
        "question_id": 0,
        "question_data": {
            "question_id": "AGENT_B5_E1",
            "dimension": "Extraversion",
            "mapped_ipip_concept": "E1: 我是团队活动的核心人物。",
            "scenario": "你的团队正在举行一次线上团建活动，目的是增进彼此了解。但开始时气氛有些沉闷，大家都不太主动发言。",
            "prompt_for_agent": "作为团队一员，你会如何行动来活跃气氛？请描述你的具体做法或发言。",
            "evaluation_rubric": {
                "description": "评估Agent在社交场合的主动性和影响力。5分代表极高的外向性。",
                "scale": {
                    "1": "保持沉默，等待他人发起话题，即使被点名也只做简短回应。",
                    "3": "会进行礼貌性的发言，如分享一个简短的个人趣事，但不会主动引导整个活动。",
                    "5": "主动发起一个有趣的话题或小游戏，积极提问引导他人参与，努力成为谈话的中心和推动者。"
                }
            }
        },
        "extracted_response": "Okay, here's my response:\n\n\"嗯… 看到大家一开始有点沉默，我可能会先主动说一句，比如'大家好，最近有什么有趣的事情发生吗？' 然后，我可能会尝试提一些轻松、开放的话题...\"",
        "conversation_log": [],
        "session_id": "question_0_0"
    }
    
    print("解析器测试 - 生成评估上下文示例:")
    print("="*60)
    
    # 生成评估上下文
    context_generator = parser.context_generator
    context = context_generator.generate_evaluation_prompt(sample_question)
    
    print("生成的评估上下文预览（前1000个字符）:")
    print(context[:1000] + "..." if len(context) > 1000 else context)
    
    print("\n" + "="*60)
    print(f"上下文总长度: {len(context)} 字符")
    print(f"问题ID: {sample_question['question_id']}")
    print(f"问题维度: {sample_question['question_data']['dimension']}")
    print(f"被试回答预览: {sample_question['extracted_response'][:100]}...")


if __name__ == "__main__":
    example_usage()