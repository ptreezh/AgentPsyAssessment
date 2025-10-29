#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐题对比分析 - 50道题的详细评分差异分析
对比2题分段和5题分段对每道题的评分差异
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import statistics

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-ded837735b3c44599a9bc138da561c27'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class QuestionByQuestionComparator:
    def __init__(self, model: str = "qwen-long"):
        self.model = model
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def load_2segment_per_question_scores(self, analysis_file: str) -> Dict:
        """加载2题分段的每题评分"""
        print(f"📂 加载2题分段逐题评分: {analysis_file}")

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取每个分段的详细评分
            segment_scores = []
            if 'segment_analyses' in data:
                for segment in data['segment_analyses']:
                    if 'big_five_scores' in segment:
                        segment_scores.append(segment['big_five_scores'])

            print(f"  ✅ 加载了 {len(segment_scores)} 个分段的评分")
            return {
                'success': True,
                'segment_scores': segment_scores,
                'total_segments': len(segment_scores),
                'questions_per_segment': 2
            }

        except Exception as e:
            print(f"  ❌ 加载失败: {e}")
            return {'success': False, 'error': str(e)}

    def load_test_data_with_mapping(self, data_file: str) -> Tuple[List[Dict], Dict]:
        """加载测试数据并建立问题-分段映射关系"""
        print(f"📋 加载测评数据: {data_file}")

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            questions = []
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for i, item in enumerate(data['assessment_results']):
                    if isinstance(item, dict) and 'question_data' in item:
                        question_data = item['question_data']
                        if isinstance(question_data, dict):
                            question_text = question_data.get('prompt_for_agent', '')
                            answer_text = ''
                            if 'extracted_response' in item and item['extracted_response']:
                                answer_text = item['extracted_response']

                            if question_text and answer_text:
                                questions.append({
                                    'index': i + 1,
                                    'question': question_text,
                                    'answer': answer_text,
                                    'original_segment_2': (i // 2) + 1,  # 2题分段索引
                                    'original_segment_5': (i // 5) + 1   # 5题分段索引
                                })

            print(f"  📊 成功提取 {len(questions)} 个问题")

            # 建立分段映射
            segment_2_mapping = {}
            segment_5_mapping = {}

            for q in questions:
                seg_2 = q['original_segment_2']
                seg_5 = q['original_segment_5']

                if seg_2 not in segment_2_mapping:
                    segment_2_mapping[seg_2] = []
                if seg_5 not in segment_5_mapping:
                    segment_5_mapping[seg_5] = []

                segment_2_mapping[seg_2].append(q)
                segment_5_mapping[seg_5].append(q)

            return questions, {
                'segment_2_mapping': segment_2_mapping,
                'segment_5_mapping': segment_5_mapping
            }

        except Exception as e:
            print(f"  ❌ 数据加载失败: {e}")
            return [], {}

    def analyze_5segment_per_question(self, questions: List[Dict], mapping: Dict) -> Dict:
        """分析5题分段的每题评分"""
        print(f"\n🔍 开始5题分段逐题分析")

        segment_5_mapping = mapping['segment_5_mapping']
        all_question_scores = []

        import openai
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 分析每个5题分段
        for segment_num, segment_questions in segment_5_mapping.items():
            print(f"  📝 分析5题分段 {segment_num}/{len(segment_5_mapping)} (题 {segment_questions[0]['index']}-{segment_questions[-1]['index']})")

            # 为分段中的每个题单独分析
            for i, question in enumerate(segment_questions):
                print(f"    🔍 分析题 {question['index']}...")

                prompt = f"""你是专业的心理评估分析师。分析以下单个问题的回答，评估Big5人格特质。

**严格评分标准：**
- 1分：极低表现 - 明显缺乏该特质
- 3分：中等表现 - 平衡或不确定，有该特质也有反例
- 5分：极高表现 - 明显具备该特质

**特别注意：只能使用1、3、5三个整数分数！**

问题 {question['index']}:
{question['question']}

回答:
{question['answer']}

请返回JSON格式：
{{
  "success": true,
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }}
}}
"""

                try:
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "你是专业的心理评估分析师。必须严格使用1-3-5评分标准。"},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.1
                    )

                    content = response.choices[0].message.content

                    # 解析JSON
                    try:
                        import re
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            result = json.loads(json_str)
                        else:
                            result = json.loads(content)
                    except json.JSONDecodeError:
                        print(f"      ❌ JSON解析失败")
                        continue

                    # 验证评分标准
                    if 'scores' in result and result['scores']:
                        invalid_scores = []
                        for trait, score in result['scores'].items():
                            if score not in [1, 3, 5]:
                                invalid_scores.append(f"{trait}:{score}")
                                # 修正无效评分
                                if score < 2:
                                    result['scores'][trait] = 1
                                elif score > 4:
                                    result['scores'][trait] = 5
                                else:
                                    result['scores'][trait] = 3

                        if invalid_scores:
                            print(f"      ⚠️ 修正无效评分: {invalid_scores}")

                        question_score = {
                            'question_index': question['index'],
                            'segment_5': segment_num,
                            'scores': result['scores'],
                            'segment_position': i + 1  # 在分段中的位置
                        }
                        all_question_scores.append(question_score)
                        print(f"      ✅ 题{question['index']}: {result['scores']}")
                    else:
                        print(f"      ❌ 无有效评分")

                except Exception as e:
                    print(f"      ❌ 分析失败: {e}")

                time.sleep(1)  # API限制

        print(f"  📊 完成 {len(all_question_scores)} 道题的5题分段分析")
        return {
            'success': True,
            'question_scores': all_question_scores,
            'total_questions': len(all_question_scores)
        }

    def reconstruct_2segment_per_question_scores(self, questions: List[Dict], segment_2_scores: List[Dict]) -> Dict:
        """重构2题分段的每题评分"""
        print(f"\n🔧 重构2题分段逐题评分")

        question_scores_2segment = []

        for i, question in enumerate(questions):
            segment_2_index = question['original_segment_2'] - 1  # 转换为0-based索引

            if segment_2_index < len(segment_2_scores):
                segment_score = segment_2_scores[segment_2_index]
                question_score = {
                    'question_index': question['index'],
                    'segment_2': question['original_segment_2'],
                    'scores': segment_score.copy(),  # 使用副本避免修改原数据
                    'segment_position': (i % 2) + 1  # 在分段中的位置
                }
                question_scores_2segment.append(question_score)

        print(f"  📊 重构了 {len(question_scores_2segment)} 道题的2题分段评分")
        return {
            'success': True,
            'question_scores': question_scores_2segment,
            'total_questions': len(question_scores_2segment)
        }

    def calculate_question_by_question_differences(self, scores_2segment: List[Dict], scores_5segment: List[Dict]) -> Dict:
        """计算逐题评分差异"""
        print(f"\n📈 计算逐题评分差异分析")

        # 创建问题索引映射
        scores_5_by_index = {q['question_index']: q for q in scores_5segment}
        scores_2_by_index = {q['question_index']: q for q in scores_2segment}

        question_differences = []
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        for question_idx in range(1, 51):  # 1-50题
            if question_idx in scores_2_by_index and question_idx in scores_5_by_index:
                q2_scores = scores_2_by_index[question_idx]['scores']
                q5_scores = scores_5_by_index[question_idx]['scores']

                question_diff = {
                    'question_index': question_idx,
                    'segment_2': scores_2_by_index[question_idx]['segment_2'],
                    'segment_5': scores_5_by_index[question_idx]['segment_5'],
                    'trait_differences': {},
                    'overall_difference': 0,
                    'max_difference': 0,
                    'consistent_traits': 0,
                    'inconsistent_traits': 0
                }

                total_diff = 0
                max_diff = 0
                consistent_count = 0

                for trait in traits:
                    score_2 = q2_scores.get(trait, 3)
                    score_5 = q5_scores.get(trait, 3)
                    difference = abs(score_2 - score_5)

                    question_diff['trait_differences'][trait] = {
                        'score_2segment': score_2,
                        'score_5segment': score_5,
                        'difference': difference,
                        'consistent': difference == 0
                    }

                    total_diff += difference
                    max_diff = max(max_diff, difference)
                    if difference == 0:
                        consistent_count += 1

                question_diff['overall_difference'] = total_diff
                question_diff['max_difference'] = max_diff
                question_diff['consistent_traits'] = consistent_count
                question_diff['inconsistent_traits'] = 5 - consistent_count

                # 分类差异等级
                if max_diff == 0:
                    question_diff['difference_level'] = '完全一致'
                elif max_diff <= 2:
                    question_diff['difference_level'] = '轻微差异'
                elif max_diff <= 4:
                    question_diff['difference_level'] = '中等差异'
                else:
                    question_diff['difference_level'] = '显著差异'

                question_differences.append(question_diff)

        print(f"  📊 分析了 {len(question_differences)} 道题的差异")
        return question_differences

    def generate_detailed_difference_report(self, question_differences: List[Dict]) -> Dict:
        """生成详细差异报告"""
        print(f"\n📋 生成详细差异分析报告")

        # 统计分析
        total_questions = len(question_differences)
        difference_levels = {'完全一致': 0, '轻微差异': 0, '中等差异': 0, '显著差异': 0}
        trait_consistency = {trait: {'consistent': 0, 'total': 0} for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']}

        overall_differences = []
        max_differences = []
        consistent_counts = []

        for q_diff in question_differences:
            difference_levels[q_diff['difference_level']] += 1
            overall_differences.append(q_diff['overall_difference'])
            max_differences.append(q_diff['max_difference'])
            consistent_counts.append(q_diff['consistent_traits'])

            # 统计特质一致性
            for trait, trait_diff in q_diff['trait_differences'].items():
                trait_consistency[trait]['total'] += 1
                if trait_diff['consistent']:
                    trait_consistency[trait]['consistent'] += 1

        # 计算统计指标
        avg_overall_diff = statistics.mean(overall_differences) if overall_differences else 0
        avg_max_diff = statistics.mean(max_differences) if max_differences else 0
        avg_consistent_traits = statistics.mean(consistent_counts) if consistent_counts else 0

        print(f"📊 差异分布:")
        for level, count in difference_levels.items():
            percentage = (count / total_questions) * 100 if total_questions > 0 else 0
            print(f"  {level}: {count}题 ({percentage:.1f}%)")

        print(f"\n🎯 总体统计:")
        print(f"  平均总体差异: {avg_overall_diff:.2f}")
        print(f"  平均最大差异: {avg_max_diff:.2f}")
        print(f"  平均一致特质数: {avg_consistent_traits:.1f}/5")

        print(f"\n📋 特质一致性分析:")
        for trait, stats in trait_consistency.items():
            consistency_rate = (stats['consistent'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"  {trait}: {stats['consistent']}/{stats['total']} ({consistency_rate:.1f}%)")

        # 找出差异最大的问题
        most_different_questions = sorted(question_differences, key=lambda x: x['max_difference'], reverse=True)[:5]
        most_consistent_questions = sorted(question_differences, key=lambda x: x['consistent_traits'], reverse=True)[:5]

        print(f"\n🔍 差异最大的5题:")
        for i, q in enumerate(most_different_questions, 1):
            print(f"  {i}. 题{q['question_index']}: 最大差异{q['max_difference']}, 一致特质{q['consistent_traits']}/5")

        print(f"\n✅ 最一致的5题:")
        for i, q in enumerate(most_consistent_questions, 1):
            print(f"  {i}. 题{q['question_index']}: {q['consistent_traits']}/5特质一致")

        # 生成详细报告
        detailed_report = {
            "analysis_info": {
                "total_questions_analyzed": total_questions,
                "analysis_date": datetime.now().isoformat(),
                "model_used": self.model
            },
            "difference_distribution": difference_levels,
            "overall_statistics": {
                "average_overall_difference": avg_overall_diff,
                "average_max_difference": avg_max_diff,
                "average_consistent_traits": avg_consistent_traits,
                "perfectly_consistent_questions": difference_levels['完全一致'],
                "perfect_consistency_rate": (difference_levels['完全一致'] / total_questions) * 100
            },
            "trait_consistency": {
                trait: {
                    "consistent_count": stats['consistent'],
                    "total_count": stats['total'],
                    "consistency_rate": (stats['consistent'] / stats['total']) * 100 if stats['total'] > 0 else 0
                }
                for trait, stats in trait_consistency.items()
            },
            "question_level_differences": question_differences,
            "most_different_questions": most_different_questions,
            "most_consistent_questions": most_consistent_questions,
            "conclusions": self._generate_conclusions(avg_overall_diff, avg_consistent_traits, difference_levels)
        }

        return detailed_report

    def _generate_conclusions(self, avg_overall_diff: float, avg_consistent_traits: float, difference_levels: Dict) -> Dict:
        """生成结论"""
        perfect_consistency_rate = (difference_levels['完全一致'] / sum(difference_levels.values())) * 100

        if perfect_consistency_rate >= 80:
            reliability_level = "优秀"
            recommendation = "✅ 5题分段方案与2题分段高度一致，推荐使用"
        elif perfect_consistency_rate >= 60:
            reliability_level = "良好"
            recommendation = "✅ 5题分段方案与2题分段基本一致，可以使用"
        elif perfect_consistency_rate >= 40:
            reliability_level = "中等"
            recommendation = "⚠️ 5题分段方案存在一些差异，需要谨慎使用"
        else:
            reliability_level = "需要改进"
            recommendation = "❌ 5题分段方案差异较大，不建议使用"

        return {
            "reliability_level": reliability_level,
            "recommendation": recommendation,
            "perfect_consistency_rate": perfect_consistency_rate,
            "average_consistency_per_question": avg_consistent_traits,
            "key_finding": f"平均每题有{avg_consistent_traits:.1f}/5个特质评分一致"
        }

    def complete_question_by_question_analysis(self, data_file: str, analysis_2segment_file: str) -> Dict:
        """完整的逐题对比分析"""
        print("🚀 开始完整50题逐题对比分析")
        print("=" * 70)

        # 1. 加载2题分段评分
        result_2segment = self.load_2segment_per_question_scores(analysis_2segment_file)
        if not result_2segment['success']:
            return {'success': False, 'error': '无法加载2题分段评分'}

        # 2. 加载测评数据
        questions, mapping = self.load_test_data_with_mapping(data_file)
        if len(questions) < 50:
            return {'success': False, 'error': f'问题数量不足: {len(questions)} < 50'}

        # 3. 分析5题分段每题评分
        result_5segment = self.analyze_5segment_per_question(questions, mapping)
        if not result_5segment['success']:
            return {'success': False, 'error': '5题分段分析失败'}

        # 4. 重构2题分段每题评分
        result_2segment_reconstructed = self.reconstruct_2segment_per_question_scores(questions, result_2segment['segment_scores'])

        # 5. 计算逐题差异
        question_differences = self.calculate_question_by_question_differences(
            result_2segment_reconstructed['question_scores'],
            result_5segment['question_scores']
        )

        # 6. 生成详细报告
        detailed_report = self.generate_detailed_difference_report(question_differences)

        # 7. 保存结果
        output_filename = f"question_by_question_comparison_{Path(data_file).stem}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 详细对比报告已保存: {output_filename}")

        return {
            'success': True,
            'data_file': data_file,
            'analysis_2segment_file': analysis_2segment_file,
            'detailed_report': detailed_report
        }

def main():
    """主函数"""
    comparator = QuestionByQuestionComparator(model="qwen-long")

    # 选择测试文件
    data_file = "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"
    analysis_2segment_file = "asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271_qwen-long_segmented_analysis.json"

    print(f"🎯 选择测试文件:")
    print(f"  数据文件: {data_file}")
    print(f"  2题分段分析: {analysis_2segment_file}")

    # 执行逐题对比分析
    result = comparator.complete_question_by_question_analysis(data_file, analysis_2segment_file)

    if result['success']:
        report = result['detailed_report']
        print(f"\n🎉 逐题对比分析完成!")
        print(f"  📊 完全一致题数: {report['difference_distribution']['完全一致']}/50")
        print(f"  📈 完美一致性率: {report['overall_statistics']['perfect_consistency_rate']:.1f}%")
        print(f"  🎯 可靠性等级: {report['conclusions']['reliability_level']}")
        print(f"  💡 建议: {report['conclusions']['recommendation']}")
    else:
        print(f"\n❌ 逐题对比分析失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()