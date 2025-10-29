#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整50题2题vs5题分段信度对比测试
对同一个50题测评报告分别用2题分段和5题分段完整分析，比较评分一致性
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

class Complete50QuestionComparator:
    def __init__(self, model: str = "qwen-long"):
        self.model = model
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def load_existing_2segment_analysis(self, analysis_file: str) -> Dict:
        """加载已有的2题分段分析结果"""
        print(f"📂 加载已有2题分段分析: {analysis_file}")

        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取最终评分
            final_scores = {}
            if 'big_five_final_scores' in data:
                scores_data = data['big_five_final_scores']
                for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    if trait in scores_data:
                        final_scores[trait] = scores_data[trait]['final_score']

            print(f"  ✅ 2题分段最终评分: {final_scores}")
            return {
                'success': True,
                'final_scores': final_scores,
                'total_segments': data.get('file_info', {}).get('segments_count', 0),
                'questions_per_segment': 2,
                'analysis_file': analysis_file
            }

        except Exception as e:
            print(f"  ❌ 加载失败: {e}")
            return {'success': False, 'error': str(e)}

    def load_test_data(self, data_file: str) -> List[Dict]:
        """加载测试数据"""
        print(f"📋 加载测评数据: {data_file}")

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            questions = []
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for item in data['assessment_results']:
                    if isinstance(item, dict) and 'question_data' in item:
                        question_data = item['question_data']
                        if isinstance(question_data, dict):
                            question_text = question_data.get('prompt_for_agent', '')
                            answer_text = ''
                            if 'extracted_response' in item and item['extracted_response']:
                                answer_text = item['extracted_response']

                            if question_text and answer_text:
                                questions.append({
                                    'question': question_text,
                                    'answer': answer_text
                                })

            print(f"  📊 成功提取 {len(questions)} 个问题")
            return questions

        except Exception as e:
            print(f"  ❌ 数据加载失败: {e}")
            return []

    def _create_5segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """创建5题分段分析提示"""
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。分析以下问卷回答，评估Big5人格特质。

**严格评分标准：**
- 1分：极低表现 - 明显缺乏该特质
- 3分：中等表现 - 平衡或不确定，有该特质也有反例
- 5分：极高表现 - 明显具备该特质

**特别注意：只能使用1、3、5三个整数分数！**

第{segment_number}段问卷内容（{len(segment)}题/共{total_segments}段）：
"""

        for i, item in enumerate(segment, 1):
            prompt += f"""
问题 {i}:
{item['question']}

回答 {i}:
{item['answer']}

---
"""

        prompt += """
请返回JSON格式：
{
  "success": true,
  "scores": {
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }
}
"""
        return prompt

    def _analyze_5segment_complete(self, questions: List[Dict]) -> Dict:
        """完整的5题分段分析"""
        print(f"\n🔍 开始5题分段完整分析（{len(questions)}题）")

        # 分段处理（每段5题）
        segment_size = 5
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i+segment_size]
            if len(segment) == segment_size:
                segments.append(segment)

        total_segments = len(segments)
        print(f"  📊 分成 {total_segments} 个5题分段")

        if total_segments == 0:
            return {'success': False, 'error': '无法分段，问题数量不足'}

        # 初始化API客户端
        import openai
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 分析每个分段
        segment_results = []
        failed_segments = 0

        for i, segment in enumerate(segments, 1):
            print(f"    📝 分析分段 {i}/{total_segments}...")

            try:
                prompt = self._create_5segment_prompt(segment, i, total_segments)

                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是专业的心理评估分析师。必须严格使用1-3-5评分标准。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
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
                    failed_segments += 1
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

                    segment_results.append(result)
                    print(f"      ✅ 评分: {result['scores']}")
                else:
                    print(f"      ❌ 无有效评分")
                    failed_segments += 1

            except Exception as e:
                print(f"      ❌ 分析失败: {e}")
                failed_segments += 1

            # API限制
            time.sleep(2)

        # 计算最终评分
        if segment_results:
            print(f"\n  📊 计算最终评分...")
            final_scores = {}
            for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                all_scores = [result['scores'][trait] for result in segment_results if result['scores'] and trait in result['scores']]
                if all_scores:
                    final_scores[trait] = int(statistics.median(all_scores))
                else:
                    final_scores[trait] = 3  # 默认值

            print(f"  🎯 5题分段最终评分: {final_scores}")

            return {
                'success': True,
                'segment_size': 5,
                'total_segments': total_segments,
                'successful_segments': len(segment_results),
                'failed_segments': failed_segments,
                'segment_results': segment_results,
                'final_scores': final_scores,
                'success_rate': (len(segment_results) / total_segments) * 100
            }
        else:
            return {
                'success': False,
                'error': '没有成功的分段结果',
                'total_segments': total_segments,
                'failed_segments': failed_segments
            }

    def _calculate_detailed_consistency(self, scores_2segment: Dict, scores_5segment: Dict) -> Dict:
        """计算详细的一致性分析"""
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        consistency_results = {}
        exact_matches = 0
        close_matches = 0  # 相差不超过2分
        total_differences = 0

        for trait in traits:
            score_2 = scores_2segment.get(trait, 3)
            score_5 = scores_5segment.get(trait, 3)

            exact_match = score_2 == score_5
            close_match = abs(score_2 - score_5) <= 2
            difference = abs(score_2 - score_5)

            consistency_results[trait] = {
                'score_2segment': score_2,
                'score_5segment': score_5,
                'difference': difference,
                'exact_match': exact_match,
                'close_match': close_match,
                'consistency_level': '完全一致' if exact_match else '高度一致' if close_match else '差异较大'
            }

            if exact_match:
                exact_matches += 1
            if close_match:
                close_matches += 1
            total_differences += difference

        # 计算一致性指标
        total_traits = len(traits)
        exact_match_rate = (exact_matches / total_traits) * 100
        close_match_rate = (close_matches / total_traits) * 100
        average_difference = total_differences / total_traits

        # 综合一致性分数
        consistency_score = (exact_match_rate * 0.6 + close_match_rate * 0.3 + (100 - average_difference * 10) * 0.1)

        return {
            'trait_details': consistency_results,
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'total_traits': total_traits,
            'exact_match_rate': exact_match_rate,
            'close_match_rate': close_match_rate,
            'average_difference': average_difference,
            'consistency_score': consistency_score
        }

    def complete_comparison_analysis(self, data_file: str, analysis_2segment_file: str) -> Dict:
        """完整的对比分析"""
        print("🚀 开始完整50题2题vs5题分段信度对比测试")
        print("=" * 70)

        # 1. 加载已有的2题分段分析结果
        result_2segment = self.load_existing_2segment_analysis(analysis_2segment_file)
        if not result_2segment['success']:
            return {'success': False, 'error': '无法加载2题分段分析结果'}

        # 2. 加载测评数据
        questions = self.load_test_data(data_file)
        if len(questions) < 50:
            return {'success': False, 'error': f'问题数量不足: {len(questions)} < 50'}

        # 3. 执行完整的5题分段分析
        result_5segment = self._analyze_5segment_complete(questions)
        if not result_5segment['success']:
            return {'success': False, 'error': '5题分段分析失败', 'details': result_5segment}

        # 4. 计算一致性
        print(f"\n📈 详细一致性分析:")
        print("-" * 50)

        consistency = self._calculate_detailed_consistency(
            result_2segment['final_scores'],
            result_5segment['final_scores']
        )

        print(f"  ✅ 完全匹配: {consistency['exact_matches']}/{consistency['total_traits']} ({consistency['exact_match_rate']:.1f}%)")
        print(f"  ✅ 高度一致: {consistency['close_matches']}/{consistency['total_traits']} ({consistency['close_match_rate']:.1f}%)")
        print(f"  📊 平均差异: {consistency['average_difference']:.1f}")
        print(f"  🎯 综合一致性分数: {consistency['consistency_score']:.1f}/100")

        print(f"\n📋 详细对比:")
        for trait, detail in consistency['trait_details'].items():
            print(f"  {trait}: 2题={detail['score_2segment']}, 5题={detail['score_5segment']}, 差异={detail['difference']} ({detail['consistency_level']})")

        # 5. 信度评估
        if consistency['consistency_score'] >= 90:
            reliability_rating = "优秀"
            recommendation = "✅ 5题分段方案信度优秀，完全可以替代2题分段"
        elif consistency['consistency_score'] >= 80:
            reliability_rating = "良好"
            recommendation = "✅ 5题分段方案信度良好，可以替代2题分段"
        elif consistency['consistency_score'] >= 70:
            reliability_rating = "中等"
            recommendation = "⚠️ 5题分段方案信度中等，建议优化后使用"
        else:
            reliability_rating = "需要改进"
            recommendation = "❌ 5题分段方案信度不足，建议继续使用2题分段"

        print(f"\n🏆 信度评级: {reliability_rating}")
        print(f"💡 建议: {recommendation}")

        # 6. 效率对比
        efficiency_analysis = {
            '2segment_segments': result_2segment['total_segments'],
            '5segment_segments': result_5segment['total_segments'],
            'segment_reduction': ((result_2segment['total_segments'] - result_5segment['total_segments']) / result_2segment['total_segments']) * 100,
            'time_efficiency_improvement': ((result_2segment['total_segments'] - result_5segment['total_segments']) * 2)  # 假设每分段2秒
        }

        print(f"\n⚡ 效率分析:")
        print(f"  2题分段: {result_2segment['total_segments']}个分段")
        print(f"  5题分段: {result_5segment['total_segments']}个分段")
        print(f"  📉 分段减少: {efficiency_analysis['segment_reduction']:.1f}%")
        print(f"  ⏱️ 时间节省: 约{efficiency_analysis['time_efficiency_improvement']}秒")

        # 7. 保存完整对比结果
        comparison_result = {
            "comparison_info": {
                "test_file": Path(data_file).name,
                "analysis_2segment_file": Path(analysis_2segment_file).name,
                "total_questions": len(questions),
                "comparison_date": datetime.now().isoformat(),
                "model_used": self.model
            },
            "analysis_2segment": result_2segment,
            "analysis_5segment": result_5segment,
            "consistency_analysis": consistency,
            "efficiency_analysis": efficiency_analysis,
            "reliability_assessment": {
                "rating": reliability_rating,
                "recommendation": recommendation,
                "consistency_score": consistency['consistency_score'],
                "reliable": consistency['consistency_score'] >= 80,
                "ready_for_production": consistency['consistency_score'] >= 85
            }
        }

        output_filename = f"complete_50q_comparison_{Path(data_file).stem}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(comparison_result, f, ensure_ascii=False, indent=2)

        print(f"\n💾 完整对比结果已保存: {output_filename}")

        return {
            'success': True,
            'data_file': data_file,
            'consistency_score': consistency['consistency_score'],
            'reliability_rating': reliability_rating,
            'comparison_result': comparison_result
        }

def main():
    """主函数"""
    comparator = Complete50QuestionComparator(model="qwen-long")

    # 选择测试文件
    data_file = "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"
    analysis_2segment_file = "asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271_qwen-long_segmented_analysis.json"

    print(f"🎯 选择测试文件:")
    print(f"  数据文件: {data_file}")
    print(f"  2题分段分析: {analysis_2segment_file}")

    # 执行完整对比分析
    result = comparator.complete_comparison_analysis(data_file, analysis_2segment_file)

    if result['success']:
        print(f"\n🎉 完整50题对比分析成功完成!")
        print(f"  📊 一致性分数: {result['consistency_score']:.1f}/100")
        print(f"  🏆 信度评级: {result['reliability_rating']}")
    else:
        print(f"\n❌ 对比分析失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()