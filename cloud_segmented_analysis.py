#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云评估器分段式心理评估分析器
使用Qwen云模型进行分段处理，逐步累积评分，确保分析完整性和准确性
严格遵循1-3-5评分标准
"""

import json
import sys
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
import openai

class CloudSegmentedPersonalityAnalyzer:
    """云评估器分段式人格分析器"""

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

        # 初始化云评估器客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

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
                                # 添加agent_response从conversation_log中提取
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
            if segment:  # 确保段不为空
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

                # 累积每个特质的评分
                for trait, score_data in big_five_scores.items():
                    if trait in self.big_five_traits:
                        score = score_data.get('score', 3)  # 默认3分
                        evidence = score_data.get('evidence', '')
                        quality = score_data.get('quality', 'inferred')

                        # 验证评分是否为1、3、5
                        if score not in [1, 3, 5]:
                            print(f"  警告: {trait} 评分 {score} 不是1、3、5，已修正为3")
                            score = 3

                        self.big_five_traits[trait]['scores'].append(score)
                        self.big_five_traits[trait]['evidence'].append(evidence)
                        self.big_five_traits[trait]['weight'] += 1

                # 记录每个问题的评分
                self.per_question_scores.append({
                    'question_id': question_id,
                    'big_five_scores': big_five_scores.copy(),
                    'segment_number': segment_result['segment_number']
                })

            print(f"  成功累积分段 {segment_result['segment_number']} 的评分")

        except Exception as e:
            print(f"  解析分段 {segment_result.get('segment_number', 'Unknown')} 结果失败: {e}")

    def calculate_final_scores(self) -> Dict:
        """计算最终的Big5评分"""
        final_scores = {}

        for trait, data in self.big_five_traits.items():
            scores = data['scores']
            weight = data['weight']

            if weight > 0:
                # 计算平均分，然后四舍五入到1、3、5
                avg_score = sum(scores) / len(scores)

                # 四舍五入到最接近的1、3、5
                if avg_score <= 2:
                    final_score = 1
                elif avg_score <= 4:
                    final_score = 3
                else:
                    final_score = 5

                final_scores[trait] = {
                    'final_score': final_score,
                    'average_score': round(avg_score, 2),
                    'raw_scores': scores.copy(),
                    'evidence_count': len(data['evidence']),
                    'weight': weight,
                    'evidence_samples': data['evidence'][:3]  # 前3个证据样本
                }
            else:
                final_scores[trait] = {
                    'final_score': 3,  # 默认中等分数
                    'average_score': 3.0,
                    'raw_scores': [],
                    'evidence_count': 0,
                    'weight': 0,
                    'evidence_samples': []
                }

        return final_scores

    def generate_mbti_type(self, final_scores: Dict) -> Dict:
        """基于Big5评分生成MBTI类型"""
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

        # S/N: 感觉 vs 直觉 (基于开放性)
        S_preference = 'S' if O <= 3 else 'N'

        # T/F: 思考 vs 情感 (基于宜人性)
        T_preference = 'T' if A <= 3 else 'F'

        # J/P: 判断 vs 感知 (基于尽责性)
        J_preference = 'J' if C > 3 else 'P'

        mbti_type = f"{E_preference}{S_preference}{T_preference}{J_preference}"

        return {
            'type': mbti_type,
            'scores': {'E/I': e_score, 'S/N': O, 'T/F': A, 'J/P': C},
            'preferences': {
                'extraversion_introversion': E_preference,
                'sensing_intuition': S_preference,
                'thinking_feeling': T_preference,
                'judging_perceiving': J_preference
            }
        }

    def analyze_full_assessment(self, assessment_file: str) -> Dict:
        """分析完整的评估文件"""
        print(f"🔍 开始分析: {assessment_file}")

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
        segment_results = []
        for i, segment in enumerate(segments, 1):
            print(f"📝 分析分段 {i}/{len(segments)}...")
            result = self.analyze_segment(segment, i)
            segment_results.append(result)

            # 累积评分
            self.accumulate_scores(result)

            # 添加延迟避免API限制
            time.sleep(1)

        # 计算最终评分
        final_scores = self.calculate_final_scores()
        mbti_result = self.generate_mbti_type(final_scores)

        # 生成完整分析报告
        analysis_report = {
            'file_info': {
                'filename': Path(assessment_file).name,
                'total_questions': len(questions),
                'segments_count': len(segments),
                'questions_per_segment': self.max_questions_per_segment,
                'model_used': self.model
            },
            'big_five_final_scores': final_scores,
            'mbti_assessment': mbti_result,
            'detailed_analysis': {
                'per_question_scores': self.per_question_scores,
                'segment_results': segment_results,
                'analysis_log': self.analysis_log
            },
            'metadata': {
                'analysis_timestamp': datetime.now().isoformat(),
                'scoring_standard': '1-3-5 scale (1=Low, 3=Moderate, 5=High)',
                'analysis_method': 'Segmented cumulative analysis'
            }
        }

        print(f"✅ 分析完成: {Path(assessment_file).name}")
        return analysis_report

def main():
    """主函数 - 测试云评估器分段分析"""
    import argparse

    parser = argparse.ArgumentParser(description='云评估器分段式Big5分析')
    parser.add_argument('input_file', help='输入评估文件路径')
    parser.add_argument('--model', default='qwen-long', choices=['qwen-long', 'qwen-max'],
                       help='使用的云模型')
    parser.add_argument('--output', help='输出文件路径')

    args = parser.parse_args()

    # 创建分析器
    analyzer = CloudSegmentedPersonalityAnalyzer(model=args.model)

    try:
        # 执行分析
        result = analyzer.analyze_full_assessment(args.input_file)

        # 保存结果
        output_file = args.output or f"{Path(args.input_file).stem}_{args.model}_segmented_analysis.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"📄 分析报告已保存: {output_file}")

        # 显示摘要
        print("\n🎯 Big5最终评分 (1-3-5制):")
        for trait, data in result['big_five_final_scores'].items():
            score = data['final_score']
            weight = data['weight']
            print(f"  {trait}: {score}/5 (基于{weight}个证据)")

        print(f"\n🧠 MBTI类型: {result['mbti_assessment']['type']}")

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()