#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的分段式心理评估分析器
确保在评估器调用失败时正确报告错误而不是使用模拟数据
"""

import json
import sys
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import math
import os

# 确保在Windows上使用UTF-8编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入Ollama评估器
try:
    from shared_analysis.ollama_evaluator import OllamaEvaluator, create_ollama_evaluator, get_ollama_model_config
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("警告: 无法导入Ollama评估器，将使用模拟模式")

class FixedSegmentedPersonalityAnalyzer:
    """修复后的分段式人格分析器"""

    def __init__(self, max_questions_per_segment: int = 2, max_segment_size: int = 50000, 
                 evaluator_name: str = "ollama_mistral"):
        self.max_questions_per_segment = max_questions_per_segment
        self.max_segment_size = max_segment_size  # 50K大小限制，适应128K上下文
        self.evaluator_name = evaluator_name
        self.evaluator = None
        self.big_five_traits = {
            'openness_to_experience': {'score': 0, 'evidence': [], 'weight': 0},
            'conscientiousness': {'score': 0, 'evidence': [], 'weight': 0},
            'extraversion': {'score': 0, 'evidence': [], 'weight': 0},
            'agreeableness': {'score': 0, 'evidence': [], 'weight': 0},
            'neuroticism': {'score': 0, 'evidence': [], 'weight': 0}
        }
        self.analysis_log = []
        
        # 初始化评估器
        if OLLAMA_AVAILABLE:
            self.evaluator = create_ollama_evaluator(evaluator_name)
            if self.evaluator:
                print(f"成功初始化评估器: {evaluator_name}")
            else:
                raise Exception(f"无法初始化评估器: {evaluator_name}")
        else:
            raise Exception("Ollama评估器不可用")

    def extract_questions(self, assessment_data: Dict) -> List[Dict]:
        """从评估数据中提取问题列表"""

        # 处理新的简化格式
        if 'assessment_data' in assessment_data:
            assessment_data = assessment_data['assessment_data']

        if 'assessment_results' in assessment_data:
            assessment_results = assessment_data['assessment_results']

            if isinstance(assessment_results, list):
                # 检查是否是问题对象列表（每个对象包含question_data）
                if len(assessment_results) > 0 and isinstance(assessment_results[0], dict):
                    if 'question_data' in assessment_results[0]:
                        # 从question_data中提取问题
                        questions = []
                        for result in assessment_results:
                            if 'question_data' in result:
                                question_data = result['question_data'].copy()
                                # 添加agent_response从conversation_log中提取
                                if 'conversation_log' in result:
                                    for msg in result['conversation_log']:
                                        if msg.get('role') == 'assistant':
                                            question_data['agent_response'] = msg['content']
                                            break
                                questions.append(question_data)
                        return questions
                    elif 'question_id' in assessment_results[0] and 'agent_response' in assessment_results[0]:
                        # 新的简化格式：直接包含问题字段
                        return assessment_results

            elif isinstance(assessment_results, dict) and 'questions' in assessment_results:
                return assessment_results['questions']

        if 'questions' in assessment_data:
            return assessment_data['questions']

        # 如果都找不到，打印更多信息用于调试
        print(f"调试: assessment_data keys = {list(assessment_data.keys())}")
        if 'assessment_results' in assessment_data:
            results = assessment_data['assessment_results']
            print(f"调试: assessment_results type = {type(results)}")
            if isinstance(results, list):
                print(f"调试: assessment_results length = {len(results)}")
                if len(results) > 0:
                    print(f"调试: first result keys = {list(results[0].keys()) if isinstance(results[0], dict) else 'not dict'}")

        raise ValueError("无法从评估数据中提取问题")

    def create_segments(self, questions: List[Dict]) -> List[List[Dict]]:
        """将问题列表分段，考虑大小限制"""
        segments = []
        remaining_questions = questions.copy()

        while remaining_questions:
            segment = []
            current_size = 0

            # 按顺序添加问题，直到达到数量或大小限制
            while len(segment) < self.max_questions_per_segment and remaining_questions:
                question = remaining_questions[0]

                # 检查添加这个问题是否会超过大小限制
                test_segment = segment + [question]
                segment_size = len(json.dumps(test_segment, ensure_ascii=False).encode('utf-8'))

                if segment_size <= self.max_segment_size:
                    segment.append(question)
                    remaining_questions.pop(0)
                    current_size = segment_size
                else:
                    # 如果单个问题就超过限制，需要截断文本
                    single_question_size = len(json.dumps([question], ensure_ascii=False).encode('utf-8'))
                    if single_question_size > self.max_segment_size:
                        # 截断问题文本
                        truncated_question = self.truncate_question_to_size(question, self.max_segment_size - 1000)  # 留些余量
                        segment.append(truncated_question)
                        remaining_questions.pop(0)
                    break

            if segment:  # 确保段不为空
                segments.append(segment)

        return segments

    def truncate_question_to_size(self, question: Dict, max_size: int) -> Dict:
        """截断问题文本以适应大小限制"""
        truncated = question.copy()

        # 截断场景描述
        if 'scenario' in truncated and len(truncated['scenario']) > 200:
            truncated['scenario'] = truncated['scenario'][:200] + "..."

        # 截断回答
        if 'agent_response' in truncated and len(truncated['agent_response']) > 400:
            truncated['agent_response'] = truncated['agent_response'][:400] + "..."

        # 截断评分标准描述
        if 'evaluation_rubric' in truncated and isinstance(truncated['evaluation_rubric'], dict):
            if 'description' in truncated['evaluation_rubric'] and len(truncated['evaluation_rubric']['description']) > 100:
                truncated['evaluation_rubric']['description'] = truncated['evaluation_rubric']['description'][:100] + "..."

        return truncated

    def analyze_segment(self, segment: List[Dict], segment_number: int) -> Dict:
        """分析单个段并返回该段的评分"""
        segment_analysis = {
            'segment_number': segment_number,
            'question_count': len(segment),
            'dimensions_covered': list(set(q.get('dimension', 'Unknown') for q in segment))
        }

        # 构建段的分析提示 - 简化版本
        system_prompt = f"""You are a personality analyst. Analyze {len(segment)} questions and provide Big Five scores (1-10) for each.

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

Return ONLY valid JSON. All traits must have scores 1-10 with evidence. No null values."""

        # 构建用户输入
        user_content = []
        for i, question in enumerate(segment):
            user_content.append(f"Question {i+1} ({question.get('dimension', 'Unknown')}):")
            user_content.append(f"Scenario: {question['scenario']}")
            user_content.append(f"Response: {question['agent_response'][:300]}...")
            user_content.append(f"Rubric: {question.get('evaluation_rubric', {}).get('description', 'N/A')}")
            user_content.append("---")

        user_prompt = "\n".join(user_content)

        # 如果评估器可用且已初始化，使用真实的LLM调用
        if self.evaluator and OLLAMA_AVAILABLE:
            print(f"  使用评估器 {self.evaluator_name} 分析段 {segment_number}")
            
            # 获取模型配置
            model_config = get_ollama_model_config(self.evaluator_name.replace("ollama_", ""))
            temperature = model_config.get("temperature", 0.1)
            max_tokens = model_config.get("max_tokens", 1024)
            
            # 调用评估器
            result = self.evaluator.evaluate_json_response(
                model_config.get("name", "mistral:instruct"), 
                system_prompt, 
                user_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if result["success"]:
                print(f"  段 {segment_number} 分析成功")
                return {
                    'system_prompt': system_prompt,
                    'user_prompt': user_prompt,
                    'segment_info': segment_analysis,
                    'llm_response': result["response"],
                    'raw_response': result["raw_response"]
                }
            else:
                # 不再回退到模拟模式，而是抛出异常
                error_msg = f"段 {segment_number} 分析失败: {result['error']}"
                print(f"  {error_msg}")
                raise Exception(error_msg)
        else:
            raise Exception(f"评估器不可用，无法分析段 {segment_number}")

    def accumulate_scores(self, segment_result: Dict) -> None:
        """累积问题级别的评分到总分"""
        if 'question_scores' not in segment_result:
            print(f"警告: segment_result中缺少'question_scores'字段: {list(segment_result.keys())}")
            return

        question_scores = segment_result['question_scores']
        if not isinstance(question_scores, list):
            print(f"警告: 'question_scores'不是列表类型: {type(question_scores)}")
            # 尝试修复：如果question_scores是字符串，尝试解析为JSON
            if isinstance(question_scores, str):
                try:
                    import json
                    question_scores = json.loads(question_scores)
                    print(f"成功解析question_scores字符串为JSON")
                except:
                    print(f"无法解析question_scores字符串: {question_scores[:100]}...")

        # 累积每个问题的评分
        for question_score in question_scores:
            if not isinstance(question_score, dict):
                print(f"警告: question_score不是字典类型: {type(question_score)}")
                continue

            # 累积每个Big Five特质的评分
            big_five_scores = question_score.get('big_five_scores', {})
            for trait, score_data in big_five_scores.items():
                if trait in self.big_five_traits:
                    if isinstance(score_data, dict) and 'score' in score_data:
                        score = score_data['score']
                        evidence = score_data.get('evidence', '')
                        weight = score_data.get('weight', 1.0)
                        
                        # 累积分数和证据
                        self.big_five_traits[trait]['score'] += score * weight
                        self.big_five_traits[trait]['evidence'].append({
                            'question_id': question_score.get('question_id', 'Unknown'),
                            'evidence': evidence,
                            'score': score,
                            'weight': weight
                        })
                        self.big_five_traits[trait]['weight'] += weight
                    else:
                        print(f"警告: {trait}的评分数据格式不正确: {score_data}")

    def calculate_final_scores(self) -> Dict:
        """计算最终的Big Five分数和MBTI类型"""
        final_scores = {
            'big_five': {},
            'mbti': {},
            'analysis_summary': {
                'total_segments': 0,
                'total_questions': 0,
                'trait_coverage': {}
            }
        }

        # 计算Big Five分数
        for trait, data in self.big_five_traits.items():
            if data['weight'] > 0:
                # 计算加权平均分
                avg_score = data['score'] / data['weight']
                # 转换为1-10分制
                normalized_score = max(1, min(10, avg_score))
                
                # 计算证据质量
                direct_count = sum(1 for e in data['evidence'] if e.get('quality') == 'direct')
                inferred_count = sum(1 for e in data['evidence'] if e.get('quality') == 'inferred')
                legacy_count = sum(1 for e in data['evidence'] if e.get('quality') == 'legacy')
                total_evidence = len(data['evidence'])
                direct_ratio = direct_count / total_evidence if total_evidence > 0 else 0
                quality_score = (direct_count * 1.0 + inferred_count * 0.5 + legacy_count * 0.2) / total_evidence if total_evidence > 0 else 0
                
                # 选择关键证据（最多3个）
                key_evidence = sorted(data['evidence'], key=lambda x: x.get('score', 0), reverse=True)[:3]
                
                final_scores['big_five'][trait] = {
                    'score': round(normalized_score, 1),
                    'raw_score': round(avg_score, 2),
                    'evidence_count': total_evidence,
                    'weight': round(data['weight'], 1),
                    'evidence_quality': {
                        'direct_count': direct_count,
                        'inferred_count': inferred_count,
                        'legacy_count': legacy_count,
                        'direct_ratio': round(direct_ratio, 2),
                        'quality_score': round(quality_score, 2)
                    },
                    'key_evidence': key_evidence
                }
            else:
                # 如果没有证据，给出中性分数
                final_scores['big_five'][trait] = {
                    'score': 5.0,
                    'raw_score': 5.0,
                    'evidence_count': 0,
                    'weight': 0,
                    'evidence_quality': {
                        'direct_count': 0,
                        'inferred_count': 0,
                        'legacy_count': 0,
                        'direct_ratio': 0.0,
                        'quality_score': 0.0
                    },
                    'key_evidence': []
                }

        # 计算MBTI类型
        mbti_dimensions = {
            'E/I': 'E' if final_scores['big_five']['extraversion']['score'] > 5 else 'I',
            'S/N': 'N' if final_scores['big_five']['openness_to_experience']['score'] > 5 else 'S',
            'T/F': 'F' if final_scores['big_five']['agreeableness']['score'] > 5 else 'T',
            'J/P': 'J' if final_scores['big_five']['conscientiousness']['score'] > 5 else 'P'
        }
        
        mbti_type = ''.join(mbti_dimensions.values())
        
        # 计算置信度
        confidence_scores = []
        for trait in ['extraversion', 'openness_to_experience', 'agreeableness', 'conscientiousness']:
            score = final_scores['big_five'][trait]['score']
            # 偏离5.0越远，置信度越高
            confidence = abs(score - 5.0) / 5.0
            confidence_scores.append(confidence)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        final_scores['mbti'] = {
            'type': mbti_type,
            'confidence': round(avg_confidence, 2),
            'big_five_basis': mbti_dimensions
        }

        return final_scores

# 测试代码
if __name__ == "__main__":
    # 这里可以添加测试代码
    pass