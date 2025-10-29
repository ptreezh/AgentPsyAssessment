#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型差异验证分析
重点检查差异最大的题目在三个云评估器之间的一致性
对比2题分段vs5题分段方案的评分依据
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

class MultiModelDifferenceValidator:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # 三个模型配置
        self.models = [
            {"name": "qwen-long", "description": "通义千问长文本模型"},
            {"name": "qwen-max", "description": "通义千问最强模型"},
            {"name": "qwen-turbo", "description": "通义千问快速模型"}
        ]

        # 从逐题分析中识别的差异最大的题目
        self.most_different_questions = [25, 9, 1, 10, 3, 4, 15, 18, 20, 36]  # 前10个最不一致的题目

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

    def create_analysis_prompt(self, question: Dict, segment_size: int, segment_context: str = "") -> str:
        """创建分析提示"""
        context_info = ""
        if segment_context:
            context_info = f"\n**分段上下文信息：**\n{segment_context}"

        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。分析以下{segment_size}题分段的问卷回答，评估Big5人格特质。

**严格评分标准：**
- 1分：极低表现 - 明显缺乏该特质
- 3分：中等表现 - 平衡或不确定，有该特质也有反例
- 5分：极高表现 - 明显具备该特质

**特别注意：只能使用1、3、5三个整数分数！**

{context_info}

问题 {question['question_index']}:
{question['question']}

回答:
{question['answer']}

请返回JSON格式：
{{
  "success": true,
  "analysis_summary": "简要分析说明和评分依据",
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }},
  "evidence": {{
    "openness_to_experience": "具体评分依据",
    "conscientiousness": "具体评分依据",
    "extraversion": "具体评分依据",
    "agreeableness": "具体评分依据",
    "neuroticism": "具体评分依据"
  }},
  "confidence": "high/medium/low"
}}
"""
        return prompt

    def analyze_question_with_model(self, model_config: Dict, question: Dict, segment_size: int, segment_context: str = "") -> Dict:
        """使用指定模型分析单个问题"""
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            prompt = self.create_analysis_prompt(question, segment_size, segment_context)

            response = client.chat.completions.create(
                model=model_config['name'],
                messages=[
                    {"role": "system", "content": "你是专业的心理评估分析师。必须严格使用1-3-5评分标准，并提供详细的评分依据。"},
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
                    'model': model_config['name'],
                    'error': 'JSON解析失败',
                    'raw_response': content[:500]
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
                    print(f"      ⚠️ 发现并修正无效评分: {invalid_scores}")

            result['model'] = model_config['name']
            result['model_description'] = model_config['description']
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

    def get_segment_context(self, questions: Dict, question_index: int, segment_size: int) -> str:
        """获取分段上下文信息"""
        segment_num = (question_index - 1) // segment_size + 1
        start_idx = (segment_num - 1) * segment_size + 1
        end_idx = min(segment_num * segment_size, len(questions))

        context_questions = []
        for i in range(start_idx, end_idx + 1):
            if i in questions:
                context_questions.append(f"问题{i}: {questions[i]['question'][:100]}...")

        return "\n".join(context_questions)

    def multi_model_validate_differences(self, questions: Dict) -> Dict:
        """多模型验证差异题目"""
        print(f"🔬 多模型差异验证分析")
        print(f"📋 重点验证题目: {self.most_different_questions}")
        print(f"🤖 使用模型: {[m['name'] for m in self.models]}")
        print("=" * 60)

        validation_results = {}

        for question_index in self.most_different_questions:
            if question_index not in questions:
                print(f"  ❌ 题{question_index} 数据不存在，跳过")
                continue

            question = questions[question_index]
            print(f"\n📝 验证题 {question_index} (差异题目)")
            print("-" * 40)

            # 获取2题分段上下文
            context_2seg = self.get_segment_context(questions, question_index, 2)
            # 获取5题分段上下文
            context_5seg = self.get_segment_context(questions, question_index, 5)

            question_results = {
                'question_index': question_index,
                'question_text': question['question'][:100] + "...",
                'answer_preview': question['answer'][:100] + "...",
                'segment_2': question['original_segment_2'],
                'segment_5': question['original_segment_5'],
                'models_2segment': {},
                'models_5segment': {}
            }

            # 2题分段多模型分析
            print(f"  🔍 2题分段多模型分析...")
            for model_config in self.models:
                print(f"    分析模型: {model_config['name']}...")
                result = self.analyze_question_with_model(model_config, question, 2, context_2seg)
                question_results['models_2segment'][model_config['name']] = result
                time.sleep(1)  # API限制

            # 5题分段多模型分析
            print(f"  🔍 5题分段多模型分析...")
            for model_config in self.models:
                print(f"    分析模型: {model_config['name']}...")
                result = self.analyze_question_with_model(model_config, question, 5, context_5seg)
                question_results['models_5segment'][model_config['name']] = result
                time.sleep(1)  # API限制

            validation_results[question_index] = question_results

        return validation_results

    def analyze_model_consistency(self, validation_results: Dict) -> Dict:
        """分析模型间一致性"""
        print(f"\n📊 模型一致性分析")
        print("=" * 50)

        consistency_analysis = {
            'questions': {},
            'segment_2_analysis': {},
            'segment_5_analysis': {},
            'cross_segment_comparison': {}
        }

        # 分析每个题目的模型一致性
        for question_index, results in validation_results.items():
            print(f"\n📋 题{question_index} 一致性分析:")

            # 2题分段模型一致性
            seg_2_models = {}
            for model_name, result in results['models_2segment'].items():
                if result['success'] and 'scores' in result:
                    seg_2_models[model_name] = result['scores']

            # 5题分段模型一致性
            seg_5_models = {}
            for model_name, result in results['models_5segment'].items():
                if result['success'] and 'scores' in result:
                    seg_5_models[model_name] = result['scores']

            question_consistency = {
                'segment_2_models': seg_2_models,
                'segment_5_models': seg_5_models,
                'segment_2_consistency': self._calculate_model_consistency(seg_2_models),
                'segment_5_consistency': self._calculate_model_consistency(seg_5_models),
                'cross_segment_consistency': self._calculate_cross_segment_consistency(seg_2_models, seg_5_models)
            }

            # 显示一致性结果
            print(f"  2题分段一致性: {question_consistency['segment_2_consistency']['consistency_rate']:.1f}%")
            print(f"  5题分段一致性: {question_consistency['segment_5_consistency']['consistency_rate']:.1f}%")
            print(f"  跨分段一致性: {question_consistency['cross_segment_consistency']['consistency_rate']:.1f}%")

            consistency_analysis['questions'][question_index] = question_consistency

        # 计算总体一致性
        all_seg2_consistency = [q['segment_2_consistency']['consistency_rate'] for q in consistency_analysis['questions'].values()]
        all_seg5_consistency = [q['segment_5_consistency']['consistency_rate'] for q in consistency_analysis['questions'].values()]
        all_cross_consistency = [q['cross_segment_consistency']['consistency_rate'] for q in consistency_analysis['questions'].values()]

        consistency_analysis['segment_2_analysis'] = {
            'average_consistency': statistics.mean(all_seg2_consistency),
            'consistency_scores': all_seg2_consistency,
            'min_consistency': min(all_seg2_consistency),
            'max_consistency': max(all_seg2_consistency)
        }

        consistency_analysis['segment_5_analysis'] = {
            'average_consistency': statistics.mean(all_seg5_consistency),
            'consistency_scores': all_seg5_consistency,
            'min_consistency': min(all_seg5_consistency),
            'max_consistency': max(all_seg5_consistency)
        }

        consistency_analysis['cross_segment_comparison'] = {
            'average_consistency': statistics.mean(all_cross_consistency),
            'consistency_scores': all_cross_consistency,
            'min_consistency': min(all_cross_consistency),
            'max_consistency': max(all_cross_consistency)
        }

        print(f"\n🎯 总体一致性统计:")
        print(f"  2题分段模型一致性: {consistency_analysis['segment_2_analysis']['average_consistency']:.1f}%")
        print(f"  5题分段模型一致性: {consistency_analysis['segment_5_analysis']['average_consistency']:.1f}%")
        print(f"  跨分段一致性: {consistency_analysis['cross_segment_comparison']['average_consistency']:.1f}%")

        return consistency_analysis

    def _calculate_model_consistency(self, model_scores: Dict) -> Dict:
        """计算模型间一致性"""
        if len(model_scores) < 2:
            return {'consistency_rate': 0, 'details': {}}

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        model_names = list(model_scores.keys())

        consistency_details = {}
        total_consistency = 0
        total_traits = len(traits)

        for trait in traits:
            scores = [model_scores[model][trait] for model in model_names if trait in model_scores[model]]
            if len(scores) >= 2:
                unique_scores = set(scores)
                consistency_details[trait] = {
                    'scores': scores,
                    'unique_count': len(unique_scores),
                    'all_same': len(unique_scores) == 1,
                    'model_names': model_names
                }
                if consistency_details[trait]['all_same']:
                    total_consistency += 1

        consistency_rate = (total_consistency / total_traits) * 100 if total_traits > 0 else 0

        return {
            'consistency_rate': consistency_rate,
            'details': consistency_details,
            'total_consistent_traits': total_consistency,
            'total_traits': total_traits
        }

    def _calculate_cross_segment_consistency(self, seg_2_models: Dict, seg_5_models: Dict) -> Dict:
        """计算跨分段一致性"""
        # 取各模型在不同分段下的平均值进行对比
        common_models = set(seg_2_models.keys()) & set(seg_5_models.keys())

        if len(common_models) < 1:
            return {'consistency_rate': 0, 'details': {}}

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        cross_consistency = {}
        total_consistency = 0

        for trait in traits:
            seg_2_scores = []
            seg_5_scores = []

            for model in common_models:
                if trait in seg_2_models[model]:
                    seg_2_scores.append(seg_2_models[model][trait])
                if trait in seg_5_models[model]:
                    seg_5_scores.append(seg_5_models[model][trait])

            if seg_2_scores and seg_5_scores:
                avg_2 = statistics.mean(seg_2_scores)
                avg_5 = statistics.mean(seg_5_scores)
                diff = abs(avg_2 - avg_5)

                cross_consistency[trait] = {
                    'segment_2_avg': avg_2,
                    'segment_5_avg': avg_5,
                    'difference': diff,
                    'consistent': diff < 1  # 允许0.5的误差
                }

                if cross_consistency[trait]['consistent']:
                    total_consistency += 1

        consistency_rate = (total_consistency / len(traits)) * 100 if traits else 0

        return {
            'consistency_rate': consistency_rate,
            'details': cross_consistency,
            'total_consistent_traits': total_consistency,
            'total_traits': len(traits)
        }

    def analyze_scoring_rationale(self, validation_results: Dict) -> Dict:
        """分析评分依据"""
        print(f"\n📝 评分依据分析")
        print("=" * 50)

        rationale_analysis = {
            'questions': {},
            'common_rationale_patterns': {},
            'segment_comparison': {}
        }

        # 提取评分依据
        common_evidence = {
            'openness_to_experience': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        }

        for question_index, results in validation_results.items():
            print(f"\n📋 题{question_index} 评分依据:")

            question_rationale = {
                'segment_2_rationales': {},
                'segment_5_rationales': {},
                'rationale_comparison': {}
            }

            # 提取2题分段评分依据
            for model_name, result in results['models_2segment'].items():
                if result['success'] and 'evidence' in result:
                    question_rationale['segment_2_rationales'][model_name] = result['evidence']
                    # 收集证据模式
                    for trait, evidence in result['evidence'].items():
                        if evidence:
                            common_evidence[trait].append(f"题{question_index}-2-{model_name}: {evidence}")

            # 提取5题分段评分依据
            for model_name, result in results['models_5segment'].items():
                if result['success'] and 'evidence' in result:
                    question_rationale['segment_5_rationales'][model_name] = result['evidence']
                    # 收集证据模式
                    for trait, evidence in result['evidence'].items():
                        if evidence:
                            common_evidence[trait].append(f"题{question_index}-5-{model_name}: {evidence}")

            # 分析评分依据差异
            rationale_analysis['questions'][question_index] = question_rationale

        # 分析常见的评分依据模式
        print(f"\n🔍 评分依据模式分析:")
        for trait, evidence_list in common_evidence.items():
            print(f"\n{trait} 特质的评分依据模式:")

            # 统计常见关键词
            evidence_keywords = {}
            for evidence in evidence_list:
                words = evidence.lower().split()
                for word in words:
                    if len(word) > 2:  # 过滤短词
                        evidence_keywords[word] = evidence_keywords.get(word, 0) + 1

            # 显示高频关键词
            top_keywords = sorted(evidence_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
            for word, count in top_keywords:
                print(f"  '{word}': {count}次")

        return rationale_analysis

    def generate_comprehensive_report(self, validation_results: Dict, consistency_analysis: Dict, rationale_analysis: Dict) -> Dict:
        """生成综合报告"""
        print(f"\n📄 生成综合验证报告")
        print("=" * 60)

        # 生成结论
        avg_seg2_consistency = consistency_analysis['segment_2_analysis']['average_consistency']
        avg_seg5_consistency = consistency_analysis['segment_5_analysis']['average_consistency']
        avg_cross_consistency = consistency_analysis['cross_segment_comparison']['average_consistency']

        # 评估哪个方案更可信
        if avg_seg5_consistency > avg_seg2_consistency:
            more_reliable = "5题分段"
            reliability_advantage = (avg_seg5_consistency - avg_seg2_consistency)
            recommendation = f"✅ 5题分段方案更可信，一致性高出{reliability_advantage:.1f}%"
        else:
            more_reliable = "2题分段"
            reliability_advantage = (avg_seg2_consistency - avg_seg5_consistency)
            recommendation = f"✅ 2题分段方案更可信，一致性高出{reliability_advantage:.1f}%"

        print(f"\n🏆 综合评估结论:")
        print(f"  📊 更可信方案: {more_reliable}")
        print(f"  📈 一致性优势: {reliability_advantage:.1f}%")
        print(f"  💡 建议: {recommendation}")

        # 详细评估标准
        if avg_cross_consistency >= 90:
            overall_rating = "优秀"
            overall_recommendation = "✅ 两种方案高度一致，可任意选择"
        elif avg_cross_consistency >= 80:
            overall_rating = "良好"
            overall_recommendation = "✅ 两种方案基本一致，推荐使用更一致方案"
        elif avg_cross_consistency >= 70:
            overall_rating = "中等"
            overall_recommendation = "⚠️ 存在一定差异，需要谨慎选择"
        else:
            overall_rating = "需要改进"
            overall_recommendation = "❌ 差异较大，需要重新评估"

        print(f"\n🎯 总体评级: {overall_rating}")
        print(f"📋 总体建议: {overall_recommendation}")

        # 保存报告
        comprehensive_report = {
            "validation_info": {
                "validation_date": datetime.now().isoformat(),
                "focus_questions": self.most_different_questions,
                "models_tested": [m['name'] for m in self.models],
                "total_questions_analyzed": len(validation_results)
            },
            "model_consistency_analysis": consistency_analysis,
            "rationale_analysis": rationale_analysis,
            "comprehensive_assessment": {
                "more_reliable_approach": more_reliable,
                "reliability_advantage": reliability_advantage,
                "overall_rating": overall_rating,
                "overall_recommendation": overall_recommendation,
                "segment_2_avg_consistency": avg_seg2_consistency,
                "segment_5_avg_consistency": avg_seg5_consistency,
                "cross_segment_avg_consistency": avg_cross_consistency
            },
            "question_details": validation_results
        }

        with open("multi_model_difference_validation_report.json", 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 综合验证报告已保存: multi_model_difference_validation_report.json")

        return comprehensive_report

    def run_multi_model_validation(self, data_file: str) -> Dict:
        """运行多模型差异验证"""
        print("🚀 开始多模型差异验证分析")
        print("=" * 70)
        print(f"📋 目标: 验证差异题目在多个模型间的一致性")
        print(f"🔍 重点: 分析2题vs5题分段方案的评分依据")
        print(f"🤖 模型: {[m['name'] for m in self.models]}")

        # 1. 加载数据
        questions = self.load_test_data(data_file)
        if not questions:
            return {'success': False, 'error': '数据加载失败'}

        # 2. 多模型验证差异题目
        validation_results = self.multi_model_validate_differences(questions)

        # 3. 分析模型一致性
        consistency_analysis = self.analyze_model_consistency(validation_results)

        # 4. 分析评分依据
        rationale_analysis = self.analyze_scoring_rationale(validation_results)

        # 5. 生成综合报告
        comprehensive_report = self.generate_comprehensive_report(
            validation_results, consistency_analysis, rationale_analysis
        )

        return {
            'success': True,
            'comprehensive_report': comprehensive_report
        }

def main():
    """主函数"""
    validator = MultiModelDifferenceValidator()

    # 选择测试文件
    data_file = "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"

    print(f"🎯 选择测试文件:")
    print(f"  数据文件: {data_file}")

    # 执行多模型验证
    result = validator.run_multi_model_validation(data_file)

    if result['success']:
        report = result['comprehensive_report']
        print(f"\n🎉 多模型差异验证完成!")
        print(f"  🏆 更可信方案: {report['comprehensive_assessment']['more_reliable_approach']}")
        print(f"  📊 一致性优势: {report['comprehensive_assessment']['reliability_advantage']:.1f}%")
        print(f"  🎯 总体评级: {report['comprehensive_assessment']['overall_rating']}")
        print(f"  💡 建议: {report['comprehensive_assessment']['overall_recommendation']}")
    else:
        print(f"\n❌ 多模型验证失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()