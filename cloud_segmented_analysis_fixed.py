#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版云评估器分段式心理评估分析器
修复评分逻辑、置信度计算、错误处理和文件输出结构
"""

import json
import sys
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import openai

class FixedCloudSegmentedPersonalityAnalyzer:
    """修复版云评估器分段式人格分析器"""

    def __init__(self, model: str = "qwen-long", api_key: str = None, max_questions_per_segment: int = 2):
        self.model = model
        self.api_key = api_key or "sk-ffd03518254b495b8d27e723cd413fc1"
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.max_questions_per_segment = max_questions_per_segment

        # 初始化Big5评分累积器
        self.big_five_traits = {
            'openness_to_experience': {'scores': [], 'evidence': [], 'weight': 0},
            'conscientiousness': {'scores': [], 'evidence': [], 'weight': 0},
            'extraversion': {'scores': [], 'evidence': [], 'weight': 0},
            'agreeableness': {'scores': [], 'evidence': [], 'weight': 0},
            'neuroticism': {'scores': [], 'evidence': [], 'weight': 0}
        }

        self.analysis_log = []
        self.per_question_scores = []
        self.segment_results = []

        # 初始化云评估器客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 检查API连接
        self.api_available = self._check_api_connection()

    def _check_api_connection(self) -> bool:
        """检查API连接是否可用"""
        try:
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            print(f"✅ API连接成功: {self.model}")
            return True
        except Exception as e:
            print(f"❌ API连接失败: {self.model} - {e}")
            return False

    def extract_questions(self, assessment_data: Dict) -> List[Dict]:
        """从评估数据中提取问题列表"""
        if 'assessment_results' in assessment_data:
            assessment_results = assessment_data['assessment_results']

            if isinstance(assessment_results, list):
                if len(assessment_results) > 0 and isinstance(assessment_results[0], dict):
                    if 'question_data' in assessment_results[0]:
                        questions = []
                        for result in assessment_results:
                            if 'question_data' in result:
                                question_data = result['question_data'].copy()
                                if 'conversation_log' in result:
                                    for msg in result['conversation_log']:
                                        if msg.get('role') == 'assistant':
                                            question_data['agent_response'] = msg['content']
                                            break
                                questions.append(question_data)
                        return questions

        if 'questions' in assessment_data:
            return assessment_data['questions']

        print(f"警告: 无法从数据中提取问题，可用键: {list(assessment_data.keys())}")
        return []

    def create_segments(self, questions: List[Dict]) -> List[List[Dict]]:
        """创建分段，每段包含指定数量的问题"""
        segments = []
        for i in range(0, len(questions), self.max_questions_per_segment):
            segment = questions[i:i + self.max_questions_per_segment]
            if segment:
                segments.append(segment)

        print(f"创建 {len(segments)} 个分段，每段最多 {self.max_questions_per_segment} 个问题")
        return segments

    def analyze_segment(self, segment: List[Dict], segment_number: int) -> Dict:
        """分析单个分段，使用严格的1-3-5评分标准"""

        system_prompt = f"""You are a personality analyst specialized in Big Five assessment. Analyze {len(segment)} questions and provide Big Five scores using ONLY the 1-3-5 scale.

For each question, assess all 5 traits using EXCLUSIVELY:
- 1: Low/Minimal expression of the trait
- 3: Moderate/Average expression of the trait
- 5: High/Strong expression of the trait

CRITICAL: Your scores must be EXACTLY 1, 3, or 5 - no other values are acceptable!

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

Return ONLY valid JSON. All traits must have scores 1, 3, or 5 with evidence. No null values."""

        # 构建用户输入
        user_content = []
        for i, question in enumerate(segment):
            user_content.append(f"Question {i+1} ({question.get('dimension', 'Unknown')}):")
            user_content.append(f"Scenario: {question['scenario']}")
            response = question.get('agent_response', '')
            user_content.append(f"Response: {response[:500]}...")
            user_content.append(f"Rubric: {question.get('evaluation_rubric', {}).get('description', 'N/A')}")
            user_content.append("---")

        user_prompt = "\n".join(user_content)

        try:
            print(f"  使用 {self.model} 分析段 {segment_number} ({len(segment)} 题)")

            # 调用云评估器
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )

            response_text = response.choices[0].message.content
            print(f"  段 {segment_number} 分析成功")

            return {
                'system_prompt': system_prompt,
                'user_prompt': user_prompt,
                'segment_number': segment_number,
                'llm_response': response_text,
                'success': True
            }

        except Exception as e:
            print(f"  段 {segment_number} 分析失败: {e}")
            return {
                'system_prompt': system_prompt,
                'user_prompt': user_prompt,
                'segment_number': segment_number,
                'error': str(e),
                'success': False
            }

    def validate_and_fix_score(self, score: Any) -> int:
        """验证并修复评分，确保只能是1、3、5"""
        try:
            score = int(score)
            if score in [1, 3, 5]:
                return score
            elif score <= 2:
                return 1
            elif score <= 4:
                return 3
            else:
                return 5
        except (ValueError, TypeError):
            return 3  # 默认值

    def accumulate_scores(self, segment_result: Dict) -> None:
        """累积分段分析结果到总评分"""
        if not segment_result.get('success'):
            print(f"  跳过失败的分段 {segment_result.get('segment_number', 'Unknown')}")
            return

        try:
            # 解析LLM响应
            response_text = segment_result['llm_response']

            # 尝试提取JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                response_data = json.loads(json_text)
            else:
                response_data = json.loads(response_text)

            if 'question_scores' not in response_data:
                print(f"  警告: 分段 {segment_result['segment_number']} 响应中缺少 question_scores")
                return

            # 处理每个问题的评分
            for question_score in response_data['question_scores']:
                question_id = question_score.get('question_id', f'Q{len(self.per_question_scores)+1}')
                big_five_scores = question_score.get('big_five_scores', {})

                validated_scores = {}
                for trait, score_data in big_five_scores.items():
                    if trait in self.big_five_traits:
                        raw_score = score_data.get('score', 3)
                        score = self.validate_and_fix_score(raw_score)
                        evidence = score_data.get('evidence', '')
                        quality = score_data.get('quality', 'inferred')

                        # 记录修复情况
                        if raw_score != score:
                            print(f"    修复 {trait} 评分: {raw_score} -> {score}")

                        self.big_five_traits[trait]['scores'].append(score)
                        self.big_five_traits[trait]['evidence'].append(evidence)
                        self.big_five_traits[trait]['weight'] += 1

                        validated_scores[trait] = {
                            'original_score': raw_score,
                            'validated_score': score,
                            'evidence': evidence,
                            'quality': quality
                        }

                # 记录每个问题的评分
                self.per_question_scores.append({
                    'question_id': question_id,
                    'segment_number': segment_result['segment_number'],
                    'big_five_scores': validated_scores
                })

            print(f"  成功累积分段 {segment_result['segment_number']} 的评分")

        except Exception as e:
            print(f"  解析分段 {segment_result.get('segment_number', 'Unknown')} 结果失败: {e}")

    def calculate_final_scores(self) -> Dict:
        """计算最终的Big5评分和置信度"""
        final_scores = {}

        for trait, data in self.big_five_traits.items():
            scores = data['scores']
            weight = data['weight']

            if weight > 0:
                # 计算平均分
                avg_score = sum(scores) / len(scores)

                # 四舍五入到最接近的1、3、5
                if avg_score <= 2:
                    final_score = 1
                elif avg_score <= 4:
                    final_score = 3
                else:
                    final_score = 5

                # 计算置信度
                score_distribution = {1: 0, 3: 0, 5: 0}
                for score in scores:
                    score_distribution[score] += 1

                # 置信度计算：基于评分一致性
                max_count = max(score_distribution.values())
                consistency = max_count / len(scores)  # 评分一致性
                confidence = round(consistency * 100, 1)

                final_scores[trait] = {
                    'final_score': final_score,
                    'average_score': round(avg_score, 2),
                    'raw_scores': scores.copy(),
                    'score_distribution': score_distribution,
                    'confidence_percent': confidence,
                    'evidence_count': len(data['evidence']),
                    'weight': weight,
                    'evidence_samples': data['evidence'][:3]
                }
            else:
                final_scores[trait] = {
                    'final_score': 3,  # 默认中等分数
                    'average_score': 3.0,
                    'raw_scores': [],
                    'score_distribution': {1: 0, 3: 0, 5: 0},
                    'confidence_percent': 0.0,  # 无数据时置信度为0
                    'evidence_count': 0,
                    'weight': 0,
                    'evidence_samples': [],
                    'warning': 'No successful segment analysis'
                }

        return final_scores

    def generate_mbti_type(self, final_scores: Dict) -> Dict:
        """基于Big5评分生成MBTI类型和置信度"""
        O = final_scores.get('openness_to_experience', {}).get('final_score', 3)
        C = final_scores.get('conscientiousness', {}).get('final_score', 3)
        E = final_scores.get('extraversion', {}).get('final_score', 3)
        A = final_scores.get('agreeableness', {}).get('final_score', 3)
        N = final_scores.get('neuroticism', {}).get('final_score', 3)

        # MBTI计算逻辑
        # E/I: 外向性 vs 神经质
        e_score = E + (5 - N)  # 高外向性+低神经质=更外向
        i_score = (5 - E) + N
        E_preference = 'E' if e_score > i_score else 'I'
        E_confidence = abs(e_score - i_score) / 8  # 置信度 0-1

        # S/N: 感觉 vs 直觉 (基于开放性)
        S_preference = 'S' if O <= 3 else 'N'
        S_confidence = abs(O - 3) / 2  # 距离中间值的距离

        # T/F: 思考 vs 情感 (基于宜人性)
        T_preference = 'T' if A <= 3 else 'F'
        T_confidence = abs(A - 3) / 2

        # J/P: 判断 vs 感知 (基于尽责性)
        J_preference = 'J' if C > 3 else 'P'
        J_confidence = abs(C - 3) / 2

        mbti_type = f"{E_preference}{S_preference}{T_preference}{J_preference}"

        # 整体MBTI置信度
        overall_confidence = (E_confidence + S_confidence + T_confidence + J_confidence) / 4

        return {
            'type': mbti_type,
            'component_scores': {
                'E/I': {'score': e_score, 'preference': E_preference, 'confidence': round(E_confidence * 100, 1)},
                'S/N': {'score': O, 'preference': S_preference, 'confidence': round(S_confidence * 100, 1)},
                'T/F': {'score': A, 'preference': T_preference, 'confidence': round(T_confidence * 100, 1)},
                'J/P': {'score': C, 'preference': J_preference, 'confidence': round(J_confidence * 100, 1)}
            },
            'overall_confidence': round(overall_confidence * 100, 1),
            'preferences': {
                'extraversion_introversion': E_preference,
                'sensing_intuition': S_preference,
                'thinking_feeling': T_preference,
                'judging_perceiving': J_preference
            }
        }

    def save_separate_files(self, base_filename: str, output_dir: Path,
                           final_scores: Dict, mbti_result: Dict,
                           per_question_scores: List, segment_results: List):
        """分离保存不同类型的输出文件"""

        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. 保存主要摘要文件（最终评分和MBTI）
        summary_file = output_dir / f"{base_filename}_summary.json"
        summary_data = {
            'file_info': {
                'filename': base_filename,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_used': self.model,
                'api_available': self.api_available
            },
            'big_five_final_scores': {
                trait: {
                    'final_score': data['final_score'],
                    'confidence_percent': data['confidence_percent'],
                    'evidence_count': data['evidence_count']
                } for trait, data in final_scores.items()
            },
            'mbti_assessment': {
                'type': mbti_result['type'],
                'overall_confidence': mbti_result['overall_confidence'],
                'component_confidence': {
                    comp: data['confidence']
                    for comp, data in mbti_result['component_scores'].items()
                }
            },
            'analysis_quality': {
                'total_segments_attempted': len(segment_results),
                'successful_segments': sum(1 for r in segment_results if r.get('success', False)),
                'total_questions_analyzed': len(per_question_scores),
                'successful_analysis_rate': sum(1 for r in segment_results if r.get('success', False)) / len(segment_results) * 100 if segment_results else 0
            }
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        # 2. 保存详细评分依据文件
        evidence_file = output_dir / f"{base_filename}_detailed_evidence.json"
        evidence_data = {
            'file_info': summary_data['file_info'],
            'big_five_detailed_scores': final_scores,
            'per_question_analysis': per_question_scores,
            'segment_analysis_log': segment_results
        }

        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence_data, f, ensure_ascii=False, indent=2)

        print(f"📄 摘要文件: {summary_file.name}")
        print(f"📋 详细证据文件: {evidence_file.name}")

        return str(summary_file), str(evidence_file)

    def analyze_full_assessment(self, assessment_file: str, output_dir: str = "fixed_results") -> Dict:
        """分析完整的评估文件"""
        print(f"🔍 开始分析: {assessment_file}")

        # 检查API可用性
        if not self.api_available:
            print(f"❌ API不可用，跳过分析: {assessment_file}")
            return {
                'success': False,
                'error': 'API connection failed',
                'file': assessment_file
            }

        try:
            # 加载评估数据
            with open(assessment_file, 'r', encoding='utf-8') as f:
                assessment_data = json.load(f)

            # 提取问题
            questions = self.extract_questions(assessment_data)
            if not questions:
                raise ValueError("无法从评估文件中提取问题")

            print(f"📊 提取到 {len(questions)} 个问题")

            # 创建分段
            segments = self.create_segments(questions)

            # 分析每个分段
            for i, segment in enumerate(segments, 1):
                print(f"📝 分析分段 {i}/{len(segments)}...")
                result = self.analyze_segment(segment, i)
                self.segment_results.append(result)

                # 累积评分
                self.accumulate_scores(result)

                # 添加延迟避免API限制
                time.sleep(1)

            # 计算最终评分
            final_scores = self.calculate_final_scores()
            mbti_result = self.generate_mbti_type(final_scores)

            # 保存分离的文件
            base_filename = Path(assessment_file).stem
            output_path = Path(output_dir)
            summary_file, evidence_file = self.save_separate_files(
                base_filename, output_path / self.model,
                final_scores, mbti_result, self.per_question_scores, self.segment_results
            )

            print(f"✅ 分析完成: {Path(assessment_file).name}")

            # 显示摘要
            print(f"🎯 Big5最终评分:")
            for trait, data in final_scores.items():
                score = data['final_score']
                confidence = data['confidence_percent']
                weight = data['weight']
                print(f"  {trait}: {score}/5 (置信度: {confidence}%, 基于{weight}个证据)")

            print(f"🧠 MBTI类型: {mbti_result['type']} (置信度: {mbti_result['overall_confidence']}%)")

            # 计算成功率
            successful_segments = sum(1 for r in self.segment_results if r.get('success', False))
            success_rate = successful_segments / len(self.segment_results) * 100

            return {
                'success': True,
                'file': assessment_file,
                'summary_file': summary_file,
                'evidence_file': evidence_file,
                'big_five_scores': {trait: data['final_score'] for trait, data in final_scores.items()},
                'mbti_type': mbti_result['type'],
                'analysis_quality': {
                    'success_rate': success_rate,
                    'successful_segments': successful_segments,
                    'total_segments': len(self.segment_results)
                }
            }

        except Exception as e:
            print(f"❌ 分析失败: {assessment_file} - {e}")
            return {
                'success': False,
                'error': str(e),
                'file': assessment_file
            }

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='修复版云评估器分段式Big5分析')
    parser.add_argument('input_file', help='输入评估文件路径')
    parser.add_argument('--model', default='qwen-long', choices=['qwen-long', 'qwen-max'],
                       help='使用的云模型')
    parser.add_argument('--output', default='fixed_cloud_results', help='输出目录')

    args = parser.parse_args()

    # 创建分析器
    analyzer = FixedCloudSegmentedPersonalityAnalyzer(model=args.model)

    # 执行分析
    result = analyzer.analyze_full_assessment(args.input_file, args.output)

    if result['success']:
        print(f"\n🎉 分析成功完成!")
        print(f"📊 Big5: {result['big_five_scores']}")
        print(f"🧠 MBTI: {result['mbti_type']}")
        print(f"📈 分析质量: {result['analysis_quality']['success_rate']:.1f}% 分段成功")
    else:
        print(f"\n💥 分析失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()