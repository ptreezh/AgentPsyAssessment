#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分段式心理评估分析器
将完整数据分段处理，逐步累积评分，确保分析完整性和准确性
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

class SegmentedPersonalityAnalyzer:
    """分段式人格分析器"""

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
        self.per_question_scores = []
        
        # 初始化评估器
        if OLLAMA_AVAILABLE:
            self.evaluator = create_ollama_evaluator(evaluator_name)
            if self.evaluator:
                print(f"成功初始化评估器: {evaluator_name}")
            else:
                print(f"无法初始化评估器: {evaluator_name}，将使用模拟模式")
        else:
            print("Ollama评估器不可用，将使用模拟模式")

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
                print(f"  段 {segment_number} 分析失败: {result['error']}")
                # 不再使用模拟数据，而是抛出异常
                raise Exception(f"评估器调用失败: {result['error']}")
        else:
            print(f"  评估器不可用，无法分析段 {segment_number}")
            # 不再使用模拟数据，而是抛出异常
            raise Exception("评估器不可用，无法进行真实分析")
    
    def _create_mock_response(self, segment: List[Dict], segment_number: int, segment_analysis: Dict) -> Dict:
        """创建模拟响应"""
        # 创建模拟的LLM响应
        mock_question_scores = []
        for i, question in enumerate(segment):
            mock_scores = {
                "openness_to_experience": {"score": 5.0 + (i % 3), "evidence": f"Mock evidence for openness in question {i+1}", "quality": "inferred"},
                "conscientiousness": {"score": 6.0 + (i % 2), "evidence": f"Mock evidence for conscientiousness in question {i+1}", "quality": "direct"},
                "extraversion": {"score": 4.0 + (i % 4), "evidence": f"Mock evidence for extraversion in question {i+1}", "quality": "inferred"},
                "agreeableness": {"score": 7.0 + (i % 2), "evidence": f"Mock evidence for agreeableness in question {i+1}", "quality": "direct"},
                "neuroticism": {"score": 3.0 + (i % 3), "evidence": f"Mock evidence for neuroticism in question {i+1}", "quality": "inferred"}
            }
            mock_question_scores.append({
                "question_id": question.get("question_id", f"Q{i+1}"),
                "dimension": question.get("dimension", "Unknown"),
                "big_five_scores": mock_scores
            })
        
        mock_response = {
            "question_scores": mock_question_scores
        }
        
        return {
            'system_prompt': "Mock system prompt",
            'user_prompt': "Mock user prompt",
            'segment_info': segment_analysis,
            'llm_response': mock_response,
            'raw_response': json.dumps(mock_response, ensure_ascii=False)
        }

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
                    return
            else:
                return

        # 累积每个问题的Big Five分数
        for i, question_score in enumerate(question_scores):
            # 处理question_score为字符串的情况
            if isinstance(question_score, str):
                try:
                    import json
                    question_score = json.loads(question_score)
                    print(f"成功解析question_score[{i}]字符串为JSON")
                except:
                    print(f"无法解析question_score[{i}]字符串: {question_score[:100]}...")
                    continue

            if not isinstance(question_score, dict):
                print(f"警告: question_scores[{i}]不是字典类型: {type(question_score)}")
                continue

            question_id = question_score.get('question_id', f'Q{i+1}')
            big_five_scores = question_score.get('big_five_scores', {})

            if not isinstance(big_five_scores, dict):
                print(f"警告: question {question_id}的'big_five_scores'不是字典类型: {type(big_five_scores)}")
                continue

            for trait, score_data in big_five_scores.items():
                if trait in self.big_five_traits:
                    if not isinstance(score_data, dict):
                        print(f"警告: question {question_id}的trait '{trait}'数据不是字典类型: {type(score_data)}")
                        continue

                    score = score_data.get('score')
                    evidence = score_data.get('evidence', f"Question {question_id}")
                    quality = score_data.get('quality', 'direct')  # 默认为直接证据

                    # 分层处理null值策略
                    if score is None:
                        print(f"警告: question {question_id}的trait '{trait}'分数为null，使用智能默认值")
                        score = 5.0  # 中性默认分数
                        evidence = f"Professional inference for {trait} - insufficient direct evidence in Question {question_id}"
                        quality = 'inferred'
                    else:
                        try:
                            score = float(score)
                        except (ValueError, TypeError):
                            print(f"警告: question {question_id}的trait '{trait}'分数类型错误: {score}，使用默认值")
                            score = 5.0
                            evidence = f"Professional inference for {trait} - invalid score format in Question {question_id}"
                            quality = 'inferred'

                    # 确保分数在有效范围内
                    score = max(1.0, min(10.0, score))

                    self.big_five_traits[trait]['score'] += score
                    self.big_five_traits[trait]['evidence'].append({
                        'text': evidence,
                        'quality': quality,
                        'question_id': question_id
                    })
                    self.big_five_traits[trait]['weight'] += 1

            # 记录问题级别的分析日志
            self.analysis_log.append({
                'type': 'question_score',
                'question_id': question_id,
                'big_five_scores': big_five_scores,
                'dimension': question_score.get('dimension', 'Unknown')
            })

            normalized_scores = {}
            for trait, data in big_five_scores.items():
                s = data.get('score')
                try:
                    s = float(s)
                except (ValueError, TypeError):
                    s = 5.0
                s = max(1.0, min(10.0, s))
                normalized_scores[trait] = {'score': s, 'evidence': data.get('evidence', ''), 'quality': data.get('quality', 'direct')}
            self.per_question_scores.append({'question_id': question_id, 'dimension': question_score.get('dimension', 'Unknown'), 'big_five_scores': normalized_scores})

    def calculate_final_scores(self) -> Dict:
        """计算最终分数"""
        final_scores = {
            'big_five': {},
            'mbti': {},
            'belbin': {},
            'per_question_scores': [],
            'analysis_summary': {
                'total_segments': 0,
                'total_questions': 0,
                'trait_coverage': {},
                'evidence_quality': {}
            }
        }

        # 计算Big Five最终分数（加权平均）
        for trait, data in self.big_five_traits.items():
            if data['weight'] > 0:
                # 将累积分数转换为1-10分制
                raw_score = data['score'] / data['weight']
                # 标准化到1-10范围
                normalized_score = max(1, min(10, 5 + raw_score))

                # 分析证据质量
                evidence_items = data['evidence']
                direct_evidence = [item for item in evidence_items if isinstance(item, dict) and item.get('quality') == 'direct']
                inferred_evidence = [item for item in evidence_items if isinstance(item, dict) and item.get('quality') == 'inferred']

                # 处理旧格式的证据（字符串）
                legacy_evidence = [item for item in evidence_items if isinstance(item, str)]

                evidence_quality = {
                    'direct_count': len(direct_evidence),
                    'inferred_count': len(inferred_evidence),
                    'legacy_count': len(legacy_evidence),
                    'direct_ratio': round(len(direct_evidence) / len(evidence_items), 2) if evidence_items else 0,
                    'quality_score': round((len(direct_evidence) + 0.5 * len(inferred_evidence)) / len(evidence_items), 2) if evidence_items else 0
                }

                final_scores['big_five'][trait] = {
                    'score': round(normalized_score, 1),
                    'raw_score': round(raw_score, 2),
                    'evidence_count': len(evidence_items),
                    'weight': data['weight'],
                    'evidence_quality': evidence_quality,
                    'key_evidence': evidence_items[:3]  # 前3个证据
                }

                # 添加到总体证据质量统计
                final_scores['analysis_summary']['evidence_quality'][trait] = evidence_quality
            else:
                final_scores['big_five'][trait] = {
                    'score': 5.0,
                    'raw_score': 0.0,
                    'evidence_count': 0,
                    'weight': 0,
                    'evidence_quality': {
                        'direct_count': 0,
                        'inferred_count': 0,
                        'legacy_count': 0,
                        'direct_ratio': 0,
                        'quality_score': 0
                    },
                    'key_evidence': []
                }

        # 基于Big Five分数计算MBTI类型
        mbti_type = self.convert_big_five_to_mbti(final_scores['big_five'])

        final_scores['mbti'] = {
            'type': mbti_type['type'],
            'confidence': mbti_type['confidence'],
            'big_five_basis': mbti_type['big_five_basis']
        }

        belbin = self.convert_big_five_to_belbin(final_scores['big_five'])
        final_scores['belbin'] = belbin
        
        # 添加A/T维度 (Assertive/Turbulent)
        neuroticism_score = final_scores['big_five']['neuroticism']['score']
        from at_dimension import neuroticism_to_at_type, get_at_description
        at_type = neuroticism_to_at_type(neuroticism_score)
        at_description = get_at_description(at_type)
        
        final_scores['at_type'] = {
            'type': at_type,
            'description': at_description,
            'neuroticism_score': neuroticism_score
        }
        
        final_scores['per_question_scores'] = self.per_question_scores
        final_scores['analysis_summary']['total_questions'] = len(self.per_question_scores)

        return final_scores

    def convert_big_five_to_mbti(self, big_five_scores: Dict) -> Dict:
        """基于Big Five分数转换为MBTI类型"""

        # 获取Big Five分数
        openness = big_five_scores.get('openness_to_experience', {}).get('score', 5.0)
        conscientiousness = big_five_scores.get('conscientiousness', {}).get('score', 5.0)
        extraversion = big_five_scores.get('extraversion', {}).get('score', 5.0)
        agreeableness = big_five_scores.get('agreeableness', {}).get('score', 5.0)
        neuroticism = big_five_scores.get('neuroticism', {}).get('score', 5.0)

        # E/I: 基于Extraversion和Neuroticism
        e_score = extraversion + (10 - neuroticism) / 2  # 高外向性+低神经质=更外向
        i_score = (10 - extraversion) + neuroticism / 2
        e_pref = 'E' if e_score > i_score else 'I'
        e_confidence = abs(e_score - i_score) / 10

        # S/N: 基于Openness
        s_score = 10 - openness
        n_score = openness
        s_pref = 'N' if n_score > s_score else 'S'
        n_confidence = abs(n_score - s_score) / 10

        # T/F: 基于Agreeableness
        t_score = 10 - agreeableness
        f_score = agreeableness
        t_pref = 'F' if f_score > t_score else 'T'
        t_confidence = abs(f_score - t_score) / 10

        # J/P: 基于Conscientiousness
        j_score = conscientiousness
        p_score = 10 - conscientiousness
        j_pref = 'J' if j_score > p_score else 'P'
        j_confidence = abs(j_score - p_score) / 10

        mbti_type = e_pref + s_pref + t_pref + j_pref
        overall_confidence = (e_confidence + n_confidence + t_confidence + j_confidence) / 4

        return {
            'type': mbti_type,
            'confidence': round(overall_confidence, 2),
            'big_five_basis': {
                'E/I': {'score': e_score, 'preference': e_pref, 'confidence': e_confidence},
                'S/N': {'score': n_score, 'preference': s_pref, 'confidence': n_confidence},
                'T/F': {'score': f_score, 'preference': t_pref, 'confidence': t_confidence},
                'J/P': {'score': j_score, 'preference': j_pref, 'confidence': j_confidence}
            }
        }

    def convert_big_five_to_belbin(self, big_five_scores: Dict) -> Dict:
        O = big_five_scores.get('openness_to_experience', {}).get('score', 5.0)
        C = big_five_scores.get('conscientiousness', {}).get('score', 5.0)
        E = big_five_scores.get('extraversion', {}).get('score', 5.0)
        A = big_five_scores.get('agreeableness', {}).get('score', 5.0)
        N = big_five_scores.get('neuroticism', {}).get('score', 5.0)
        roles = {
            'PL': O*0.5 + A*0.2 + (-C)*0.3,
            'RI': E*0.5 + O*0.4,
            'CO': E*0.4 + A*0.4,
            'SH': E*0.4 + (-A)*0.3 + (10-N)*0.2,
            'ME': C*0.5 + (-E)*0.3 + (10-N)*0.2,
            'TW': A*0.5 + E*0.2,
            'IMP': C*0.5 + (-O)*0.3,
            'CF': C*0.4 + N*0.3,
            'SP': C*0.3 + O*0.3
        }
        sorted_roles = sorted(roles.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_roles[0][0]
        secondary = sorted_roles[1][0]
        rationale = {'top_traits': {'O': O, 'C': C, 'E': E, 'A': A, 'N': N}, 'role_scores': roles}
        return {'primary_role': primary, 'secondary_role': secondary, 'rationale': rationale}

def test_segmented_analysis(input_file: str = None, evaluator_name: str = "ollama_mistral"):
    """测试分段分析"""
    if input_file is None:
        if len(sys.argv) > 1:
            input_file = sys.argv[1]
        else:
            print("错误: 请提供输入文件路径")
            print("用法: python segmented_analysis.py <input_file> [evaluator_name]")
            sys.exit(1)
    
    # 检查是否有指定评估器
    if len(sys.argv) > 2:
        evaluator_name = sys.argv[2]
    
    # 检查文件是否存在
    if not Path(input_file).exists():
        print(f"错误: 文件不存在 - {input_file}")
        sys.exit(1)

    # 使用指定的评估器初始化分析器
    analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=2, evaluator_name=evaluator_name)

    # 加载测试数据，尝试多种编码方式
    assessment_data = None
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                assessment_data = json.load(f)
            print(f"成功使用 {encoding} 编码读取文件")
            break
        except UnicodeDecodeError:
            print(f"使用 {encoding} 编码读取文件失败，尝试其他编码...")
            continue
        except json.JSONDecodeError as e:
            print(f"使用 {encoding} 编码读取文件成功但JSON解析失败: {e}")
            continue
    
    if assessment_data is None:
        print("错误: 无法使用任何编码方式读取文件")
        sys.exit(1)

    print("数据结构:", list(assessment_data.keys()))

    # 提取问题
    questions = analyzer.extract_questions(assessment_data)
    print(f"总问题数: {len(questions)}")

    # 创建分段
    segments = analyzer.create_segments(questions)
    print(f"分段数: {len(segments)}")

    # 分析每个段并累积结果
    for i, segment in enumerate(segments):
        print(f"分析段 {i+1}/{len(segments)}: {len(segment)} 个问题")
        dimensions = list(set(q.get('dimension', 'Unknown') for q in segment))
        print(f"  涵盖维度: {dimensions}")

        # 分析段
        segment_analysis = analyzer.analyze_segment(segment, i+1)
        
        # 累积分数
        if 'llm_response' in segment_analysis:
            analyzer.accumulate_scores(segment_analysis['llm_response'])
            print(f"  段 {i+1} 分析完成并累积分数")
        else:
            print(f"  警告: 段 {i+1} 缺少分析结果")

    # 计算最终分数
    final_scores = analyzer.calculate_final_scores()
    
    # 输出结果
    print("\n=== 最终分析结果 ===")
    print("Big Five 分数:")
    for trait, data in final_scores['big_five'].items():
        print(f"  {trait}: {data['score']}/10.0 (基于 {data['weight']} 个问题)")
    
    print(f"\nMBTI 类型: {final_scores['mbti']['type']} (置信度: {final_scores['mbti']['confidence']})")
    
    # 保存结果到文件
    output_file = input_file.replace(".json", "_segmented_analysis.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_scores, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到: {output_file}")

if __name__ == "__main__":
    test_segmented_analysis()