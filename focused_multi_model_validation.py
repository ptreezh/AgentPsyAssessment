#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聚焦多模型差异验证 - 重点验证最关键的差异题目
只验证题25、题9、题1这三个差异最大的题目
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

class FocusedMultiModelValidator:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # 三个模型配置
        self.models = [
            {"name": "qwen-long", "description": "通义千问长文本模型"},
            {"name": "qwen-max", "description": "通义千问最强模型"},
            {"name": "qwen-turbo", "description": "通义千问快速模型"}
        ]

        # 重点验证的差异最大的3个题目
        self.critical_questions = [25, 9, 1]

    def load_test_data(self, data_file: str) -> Dict:
        """加载测试数据"""
        print(f"📋 加载测评数据: {data_file}")

        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            questions = {}
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
                                questions[i + 1] = {  # 1-based indexing
                                    'question': question_text,
                                    'answer': answer_text,
                                    'question_index': i + 1,
                                    'original_segment_2': (i // 2) + 1,
                                    'original_segment_5': (i // 5) + 1
                                }

            print(f"  📊 成功提取 {len(questions)} 个问题")
            return questions

        except Exception as e:
            print(f"  ❌ 数据加载失败: {e}")
            return {}

    def create_focused_prompt(self, question: Dict, segment_size: int) -> str:
        """创建聚焦分析提示"""

        prompt = f"""你是专业的心理评估分析师。分析以下{segment_size}题分段的问卷回答，评估Big5人格特质。

**严格评分标准：**
- 1分：极低表现 - 明显缺乏该特质
- 3分：中等表现 - 平衡或不确定，有该特质也有反例
- 5分：极高表现 - 明显具备该特质

**特别注意：只能使用1、3、5三个整数分数！**

问题 {question['question_index']}:
{question['question']}

回答:
{question['answer']}

请返回JSON格式：
{{
  "success": true,
  "analysis_summary": "简要分析说明和关键评分依据",
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }},
  "key_evidence": "具体评分的关键证据",
  "confidence": "high/medium/low"
}}
"""
        return prompt

    def analyze_with_model(self, model_config: Dict, question: Dict, segment_size: int) -> Dict:
        """使用指定模型分析"""
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            prompt = self.create_focused_prompt(question, segment_size)

            response = client.chat.completions.create(
                model=model_config['name'],
                messages=[
                    {"role": "system", "content": "你是专业的心理评估分析师。必须严格使用1-3-5评分标准，并提供关键证据说明。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
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
                    'model': model_config['name'],
                    'error': 'JSON解析失败',
                    'raw_response': content[:300]
                }

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

            result['model'] = model_config['name']
            result['question_index'] = question['question_index']
            result['segment_size'] = segment_size

            return result

        except Exception as e:
            return {
                'success': False,
                'model': model_config['name'],
                'error': str(e),
                'question_index': question['question_index']
            }

    def run_focused_validation(self, data_file: str) -> Dict:
        """运行聚焦验证"""
        print("🚀 开始聚焦多模型差异验证")
        print("=" * 60)
        print(f"🎯 验证题目: {self.critical_questions} (差异最大的3题)")
        print(f"🤖 使用模型: {[m['name'] for m in self.models]}")

        # 加载数据
        questions = self.load_test_data(data_file)
        if not questions:
            return {'success': False, 'error': '数据加载失败'}

        validation_results = {}

        # 验证每个关键题目
        for question_index in self.critical_questions:
            if question_index not in questions:
                print(f"  ❌ 题{question_index} 数据不存在")
                continue

            question = questions[question_index]
            print(f"\n📋 验证题 {question_index} (差异最大题目之一)")
            print(f"📝 问题: {question['question'][:100]}...")

            question_results = {
                'question_index': question_index,
                'question_preview': question['question'][:100] + "...",
                'answer_preview': question['answer'][:100] + "...",
                'models_2segment': {},
                'models_5segment': {}
            }

            # 2题分段分析
            print(f"  🔍 2题分段分析...")
            for model_config in self.models:
                print(f"    模型: {model_config['name']}...")
                result = self.analyze_with_model(model_config, question, 2)
                question_results['models_2segment'][model_config['name']] = result
                if result['success']:
                    print(f"      ✅ 评分: {result['scores']}")
                else:
                    print(f"      ❌ 失败: {result.get('error', 'Unknown error')}")
                time.sleep(2)

            # 5题分段分析
            print(f"  🔍 5题分段分析...")
            for model_config in self.models:
                print(f"    模型: {model_config['name']}...")
                result = self.analyze_with_model(model_config, question, 5)
                question_results['models_5segment'][model_config['name']] = result
                if result['success']:
                    print(f"      ✅ 评分: {result['scores']}")
                else:
                    print(f"      ❌ 失败: {result.get('error', 'Unknown error')}")
                time.sleep(2)

            validation_results[question_index] = question_results

            print(f"  ✅ 题{question_index}验证完成")

        # 分析结果
        print(f"\n📊 验证结果分析:")
        print("=" * 50)

        for question_index, results in validation_results.items():
            print(f"\n📋 题{question_index} 模型对比:")

            # 收集2题分段结果
            seg_2_scores = {}
            for model_name, result in results['models_2segment'].items():
                if result['success'] and 'scores' in result:
                    seg_2_scores[model_name] = result['scores']
                    evidence = result.get('key_evidence', '无')
                    print(f"   {model_name} (2题): {result['scores']}")
                    print(f"    证据: {evidence[:50]}...")

            # 收集5题分段结果
            seg_5_scores = {}
            for model_name, result in results['models_5segment'].items():
                if result['success'] and 'scores' in result:
                    seg_5_scores[model_name] = result['scores']
                    evidence = result.get('key_evidence', '无')
                    print(f"  {model_name} (5题): {result['scores']}")
                    print(f"    证据: {evidence[:50]}...")

            # 计算模型一致性
            print(f"\n  🔍 模型一致性分析:")
            self._analyze_model_consistency(seg_2_scores, seg_5_scores, question_index)

        return validation_results

    def _analyze_model_consistency(self, seg_2_scores: Dict, seg_5_scores: Dict, question_index: int):
        """分析模型一致性"""
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        print(f"    📊 特质一致性:")

        for trait in traits:
            seg_2_values = []
            seg_5_values = []

            for model, scores in seg_2_scores.items():
                if trait in scores:
                    seg_2_values.append(scores[trait])

            for model, scores in seg_5_scores.items():
                if trait in scores:
                    seg_5_values.append(scores[trait])

            if seg_2_values and seg_5_values:
                avg_2 = statistics.mean(seg_2_values)
                avg_5 = statistics.mean(seg_5_values)
                diff = abs(avg_2 - avg_5)

                consistency = "✅ 一致" if diff < 1 else "⚠️ 有差异"
                print(f"      {trait}: 2题={avg_2:.1f}, 5题={avg_5:.1f}, 差异={diff:.1f} {consistency}")

    def save_results(self, validation_results: Dict):
        """保存验证结果"""
        output_file = f"focused_multi_model_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 验证结果已保存: {output_file}")
        return output_file

def main():
    """主函数"""
    validator = FocusedMultiModelValidator()

    # 选择测试文件
    data_file = "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"

    print(f"🎯 选择测试文件:")
    print(f"  数据文件: {data_file}")

    # 执行聚焦验证
    result = validator.run_focused_validation(data_file)

    if result['success']:
        output_file = validator.save_results(result)
        print(f"\n🎉 聚焦多模型验证完成!")
        print(f"  📄 结果文件: {output_file}")
    else:
        print(f"\n❌ 验证失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()