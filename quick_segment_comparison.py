#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速单文件2题vs5题分段对比测试
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import statistics

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-ded837735b3c44599a9bc138da561c27'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def quick_comparison_test():
    """快速对比测试"""
    print("🔬 快速2题vs5题分段对比测试")
    print("=" * 50)

    # 选择测试文件
    test_file = "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"

    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return

    # 读取文件
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取前10题
    questions = []
    if 'assessment_results' in data and isinstance(data['assessment_results'], list):
        for item in data['assessment_results'][:10]:
            if isinstance(item, dict) and 'question_data' in item:
                question_data = item['question_data']
                if isinstance(question_data, dict):
                    question_text = question_data.get('prompt_for_agent', '')
                    answer_text = item.get('extracted_response', '')

                    if question_text and answer_text:
                        questions.append({
                            'question': question_text,
                            'answer': answer_text
                        })

    print(f"📋 提取了 {len(questions)} 个问题")

    if len(questions) < 10:
        print("❌ 问题数量不足")
        return

    # 初始化API客户端
    import openai
    client = openai.OpenAI(
        api_key=os.getenv('DASHSCOPE_API_KEY'),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    def analyze_segments(segment_size: int, segment_name: str):
        """分析指定大小的分段"""
        print(f"\n🔍 {segment_name}分段分析:")

        # 分段
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i+segment_size]
            if len(segment) == segment_size:
                segments.append(segment)

        print(f"  📊 分成 {len(segments)} 个{segment_size}题分段")

        # 分析每个分段
        segment_results = []
        for i, segment in enumerate(segments, 1):
            print(f"    分析分段{i}...")

            # 构建提示
            prompt = f"""你是专业的心理评估分析师。分析以下{segment_size}个问题的回答，评估Big5人格特质。

严格评分标准：
- 1分：极低表现
- 3分：中等表现
- 5分：极高表现

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

第{i}段内容：
"""

            for j, item in enumerate(segment, 1):
                prompt += f"\n问题{j}: {item['question'][:100]}..."
                prompt += f"\n回答{j}: {item['answer'][:100]}...\n"

            try:
                response = client.chat.completions.create(
                    model="qwen-long",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )

                content = response.choices[0].message.content

                # 解析JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)

                    if 'scores' in result:
                        scores = result['scores']
                        print(f"      ✅ 评分: {scores}")

                        # 验证评分标准
                        invalid_scores = [s for s in scores.values() if s not in [1, 3, 5]]
                        if invalid_scores:
                            print(f"      ⚠️ 发现无效评分: {invalid_scores}")
                            # 修正无效评分
                            for trait, score in scores.items():
                                if score not in [1, 3, 5]:
                                    if score < 2:
                                        scores[trait] = 1
                                    elif score > 4:
                                        scores[trait] = 5
                                    else:
                                        scores[trait] = 3
                            print(f"      🔧 修正后: {scores}")

                        segment_results.append(result)
                    else:
                        print(f"      ❌ 无scores字段")
                else:
                    print(f"      ❌ JSON解析失败")

            except Exception as e:
                print(f"      ❌ 分析失败: {e}")

            time.sleep(2)  # API限制

        if segment_results:
            # 计算最终评分
            final_scores = {}
            for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                all_scores = []
                for result in segment_results:
                    if result['scores'] and trait in result['scores']:
                        all_scores.append(result['scores'][trait])

                if all_scores:
                    final_scores[trait] = int(statistics.median(all_scores))
                else:
                    final_scores[trait] = 3  # 默认值

            print(f"  📊 最终评分: {final_scores}")
            return final_scores
        else:
            print(f"  ❌ 没有成功的分段结果")
            return None

    # 执行对比分析
    print(f"\n🎯 开始对比分析...")

    # 2题分段分析
    scores_2segment = analyze_segments(2, "2题")

    # 5题分段分析
    scores_5segment = analyze_segments(5, "5题")

    if scores_2segment and scores_5segment:
        # 计算一致性
        print(f"\n📈 一致性分析:")
        print("-" * 40)

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        exact_matches = 0
        close_matches = 0

        for trait in traits:
            score_2 = scores_2segment[trait]
            score_5 = scores_5segment[trait]
            difference = abs(score_2 - score_5)

            exact_match = score_2 == score_5
            close_match = difference <= 2

            if exact_match:
                exact_matches += 1
                status = "✅ 完全一致"
            elif close_match:
                close_matches += 1
                status = "⚠️ 接近一致"
            else:
                status = "❌ 差异较大"

            print(f"  {trait}: 2题={score_2}, 5题={score_5}, 差异={difference} {status}")

        # 计算一致性指标
        total_traits = len(traits)
        exact_match_rate = (exact_matches / total_traits) * 100
        close_match_rate = (close_matches / total_traits) * 100
        consistency_score = (exact_match_rate * 0.7 + close_match_rate * 0.3)

        print(f"\n🎯 一致性统计:")
        print(f"  ✅ 完全匹配: {exact_matches}/{total_traits} ({exact_match_rate:.1f}%)")
        print(f"  ⚠️ 接近匹配: {close_matches}/{total_traits} ({close_match_rate:.1f}%)")
        print(f"  📊 一致性分数: {consistency_score:.1f}/100")

        # 评估结果
        if consistency_score >= 80:
            reliability = "优秀"
            recommendation = "✅ 5题分段信度优秀，可以替代2题分段"
        elif consistency_score >= 70:
            reliability = "良好"
            recommendation = "⚠️ 5题分段信度良好，建议结合使用"
        elif consistency_score >= 60:
            reliability = "中等"
            recommendation = "⚠️ 5题分段信度中等，需要优化"
        else:
            reliability = "需要改进"
            recommendation = "❌ 5题分段信度不足，建议继续使用2题分段"

        print(f"\n🏆 信度评级: {reliability}")
        print(f"💡 建议: {recommendation}")

        # 保存结果
        result_data = {
            "test_info": {
                "test_file": Path(test_file).name,
                "test_date": datetime.now().isoformat(),
                "questions_used": len(questions)
            },
            "scores_2segment": scores_2segment,
            "scores_5segment": scores_5segment,
            "consistency_analysis": {
                "exact_match_rate": exact_match_rate,
                "close_match_rate": close_match_rate,
                "consistency_score": consistency_score,
                "reliability_rating": reliability,
                "recommendation": recommendation
            }
        }

        with open("quick_segment_comparison_result.json", 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存: quick_segment_comparison_result.json")

        return result_data
    else:
        print("❌ 对比分析失败")
        return None

if __name__ == "__main__":
    quick_comparison_test()