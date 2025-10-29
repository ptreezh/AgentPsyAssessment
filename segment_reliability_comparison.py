#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2题分段 vs 5题分段信度对比测试
对同一个测评报告分别用两种分段方案分析，比较评分一致性
"""

import sys
import os
import json
import time
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import statistics

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-ded837735b3c44599a9bc138da561c27'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class SegmentReliabilityComparator:
    def __init__(self, model: str = "qwen-long"):
        self.model = model
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def _create_2segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """创建2题分段分析提示"""
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

    def _analyze_segment(self, segment: List[Dict], prompt_func: callable, segment_number: int, total_segments: int) -> Dict:
        """分析单个分段"""
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            prompt = prompt_func(segment, segment_number, total_segments)

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
                return {
                    'success': False,
                    'error': 'JSON解析失败',
                    'raw_response': content[:200]
                }

            # 验证评分标准
            if 'scores' in result:
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
                    print(f"    ⚠️ 发现并修正无效评分: {invalid_scores}")

            result['segment_number'] = segment_number
            result['model'] = self.model

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'segment_number': segment_number
            }

    def _analyze_with_segmentation(self, questions: List[Dict], segment_size: int) -> Dict:
        """用指定分段大小分析"""
        print(f"  🔍 使用{segment_size}题分段分析...")

        # 分段处理
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i+segment_size]
            if len(segment) == segment_size:
                segments.append(segment)

        total_segments = len(segments)
        print(f"  📊 分成{total_segments}个{segment_size}题分段")

        # 选择提示函数
        prompt_func = self._create_2segment_prompt if segment_size == 2 else self._create_5segment_prompt

        # 分析每个分段
        segment_results = []
        for i, segment in enumerate(segments, 1):
            print(f"    分析分段{i}...")
            result = self._analyze_segment(segment, prompt_func, i, total_segments)

            if result['success']:
                segment_results.append(result)
                print(f"      ✅ 评分: {result['scores']}")
            else:
                print(f"      ❌ 失败: {result.get('error', 'Unknown error')}")

            time.sleep(2)  # API限制

        if segment_results:
            # 计算最终评分
            final_scores = {}
            for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                all_scores = [result['scores'][trait] for result in segment_results]
                final_scores[trait] = int(statistics.median(all_scores))

            return {
                'success': True,
                'segment_size': segment_size,
                'total_segments': total_segments,
                'segment_results': segment_results,
                'final_scores': final_scores
            }
        else:
            return {
                'success': False,
                'segment_size': segment_size,
                'error': '没有成功的分段结果'
            }

    def _calculate_score_consistency(self, scores_2segment: Dict, scores_5segment: Dict) -> Dict:
        """计算评分一致性"""
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        consistency_results = {}
        exact_matches = 0
        close_matches = 0  # 相差不超过2分

        for trait in traits:
            score_2 = scores_2segment.get(trait, 0)
            score_5 = scores_5segment.get(trait, 0)

            exact_match = score_2 == score_5
            close_match = abs(score_2 - score_5) <= 2

            consistency_results[trait] = {
                'score_2segment': score_2,
                'score_5segment': score_5,
                'difference': abs(score_2 - score_5),
                'exact_match': exact_match,
                'close_match': close_match
            }

            if exact_match:
                exact_matches += 1
            if close_match:
                close_matches += 1

        # 计算一致性指标
        total_traits = len(traits)
        exact_match_rate = (exact_matches / total_traits) * 100
        close_match_rate = (close_matches / total_traits) * 100

        return {
            'trait_details': consistency_results,
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'total_traits': total_traits,
            'exact_match_rate': exact_match_rate,
            'close_match_rate': close_match_rate,
            'consistency_score': (exact_match_rate * 0.7 + close_match_rate * 0.3)
        }

    def analyze_file_comparison(self, file_path: str) -> Dict:
        """对单个文件进行2题vs5题分段对比分析"""
        print(f"\n📊 对比分析文件: {Path(file_path).name}")
        print("=" * 60)

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取问题
            questions = []
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for item in data['assessment_results'][:20]:  # 取前20题，保证够用
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

            if len(questions) < 10:
                print(f"❌ 问题数量不足：{len(questions)}")
                return {'success': False, 'error': '问题数量不足'}

            print(f"📋 提取了 {len(questions)} 个问题")

            # 2题分段分析
            print(f"\n🔬 2题分段分析:")
            result_2segment = self._analyze_with_segmentation(questions[:10], 2)  # 用前10题

            # 5题分段分析
            print(f"\n🔬 5题分段分析:")
            result_5segment = self._analyze_with_segmentation(questions[:10], 5)  # 用前10题

            if result_2segment['success'] and result_5segment['success']:
                # 计算一致性
                consistency = self._calculate_score_consistency(
                    result_2segment['final_scores'],
                    result_5segment['final_scores']
                )

                print(f"\n🎯 一致性分析结果:")
                print(f"  ✅ 完全匹配: {consistency['exact_matches']}/{consistency['total_traits']} ({consistency['exact_match_rate']:.1f}%)")
                print(f"  ✅ 接近匹配: {consistency['close_matches']}/{consistency['total_traits']} ({consistency['close_match_rate']:.1f}%)")
                print(f"  📊 一致性分数: {consistency['consistency_score']:.1f}/100")

                print(f"\n📈 详细对比:")
                for trait, detail in consistency['trait_details'].items():
                    print(f"  {trait}: 2题={detail['score_2segment']}, 5题={detail['score_5segment']}, 差异={detail['difference']}")

                # 保存对比结果
                comparison_result = {
                    "file_info": {
                        "filename": Path(file_path).name,
                        "total_questions": len(questions),
                        "analysis_date": datetime.now().isoformat(),
                        "model_used": self.model
                    },
                    "analysis_2segment": result_2segment,
                    "analysis_5segment": result_5segment,
                    "consistency_analysis": consistency,
                    "reliability_assessment": {
                        "high_reliability": consistency['consistency_score'] >= 80,
                        "medium_reliability": consistency['consistency_score'] >= 60,
                        "recommendation": "高信度" if consistency['consistency_score'] >= 80 else "中等信度" if consistency['consistency_score'] >= 60 else "低信度"
                    }
                }

                output_filename = f"{Path(file_path).stem}_segment_comparison.json"
                output_path = os.path.join("segment_comparison_results", output_filename)

                os.makedirs("segment_comparison_results", exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(comparison_result, f, ensure_ascii=False, indent=2)

                print(f"\n💾 对比结果已保存: {output_filename}")

                return {
                    'success': True,
                    'file_path': file_path,
                    'consistency_score': consistency['consistency_score'],
                    'exact_match_rate': consistency['exact_match_rate'],
                    'comparison_result': comparison_result
                }
            else:
                print(f"❌ 其中一种分段分析失败")
                return {
                    'success': False,
                    'error': '分段分析失败',
                    'result_2segment': result_2segment,
                    'result_5segment': result_5segment
                }

        except Exception as e:
            print(f"❌ 文件处理失败: {e}")
            return {'success': False, 'error': str(e)}

    def batch_comparison_test(self, input_dir: str = "results/results", max_files: int = 5):
        """批量对比测试"""
        print("🚀 开始2题vs5题分段信度对比测试")
        print("=" * 60)

        # 查找文件
        files = glob.glob(os.path.join(input_dir, "*.json"))
        files = files[:max_files]

        print(f"📊 选择 {len(files)} 个文件进行对比测试")

        if not files:
            print("❌ 未找到文件")
            return

        # 批量处理
        comparison_results = []
        consistency_scores = []

        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] 开始对比分析...")
            result = self.analyze_file_comparison(file_path)

            if result['success']:
                comparison_results.append(result)
                consistency_scores.append(result['consistency_score'])
                print(f"   ✅ 一致性分数: {result['consistency_score']:.1f}")
            else:
                print(f"   ❌ 分析失败: {result.get('error', 'Unknown error')}")

        # 总体统计
        if comparison_results:
            avg_consistency = sum(consistency_scores) / len(consistency_scores)
            high_reliability_count = sum(1 for score in consistency_scores if score >= 80)
            medium_reliability_count = sum(1 for score in consistency_scores if 60 <= score < 80)

            print(f"\n🎯 总体信度评估:")
            print(f"  📊 平均一致性分数: {avg_consistency:.1f}/100")
            print(f"  ✅ 高信度文件: {high_reliability_count}/{len(comparison_results)}")
            print(f"  ⚠️ 中等信度文件: {medium_reliability_count}/{len(comparison_results)}")
            print(f"  ❌ 低信度文件: {len(comparison_results) - high_reliability_count - medium_reliability_count}/{len(comparison_results)}")

            # 最终评估
            if avg_consistency >= 80:
                overall_rating = "优秀"
                recommendation = "✅ 5题分段方案信度优秀，可以替代2题分段"
            elif avg_consistency >= 70:
                overall_rating = "良好"
                recommendation = "⚠️ 5题分段方案信度良好，建议结合使用"
            elif avg_consistency >= 60:
                overall_rating = "中等"
                recommendation = "⚠️ 5题分段方案信度中等，需要优化"
            else:
                overall_rating = "需要改进"
                recommendation = "❌ 5题分段方案信度不足，建议继续使用2题分段"

            print(f"\n🏆 总体评级: {overall_rating}")
            print(f"💡 建议: {recommendation}")

            # 保存总体报告
            overall_report = {
                "test_info": {
                    "test_type": "2题vs5题分段信度对比",
                    "test_date": datetime.now().isoformat(),
                    "model_used": self.model,
                    "files_tested": len(files),
                    "files_successful": len(comparison_results)
                },
                "consistency_stats": {
                    "average_consistency": avg_consistency,
                    "high_reliability_count": high_reliability_count,
                    "medium_reliability_count": medium_reliability_count,
                    "low_reliability_count": len(comparison_results) - high_reliability_count - medium_reliability_count
                },
                "overall_assessment": {
                    "rating": overall_rating,
                    "recommendation": recommendation,
                    "reliable": avg_consistency >= 70
                },
                "individual_results": comparison_results
            }

            with open("segment_comparison_overall_report.json", 'w', encoding='utf-8') as f:
                json.dump(overall_report, f, ensure_ascii=False, indent=2)

            print(f"\n📄 总体报告已保存: segment_comparison_overall_report.json")

            return overall_report
        else:
            print("❌ 没有成功的对比分析结果")
            return None

def main():
    """主函数"""
    comparator = SegmentReliabilityComparator(model="qwen-long")
    comparator.batch_comparison_test(max_files=3)  # 测试3个文件

if __name__ == "__main__":
    main()