#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型置信度分析器
通过比较多个独立模型的评估结果来计算置信度
"""

import json
import sys
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from enhanced_cloud_analyzer import EnhancedCloudAnalyzer

class MultiModelConfidenceAnalyzer:
    """多模型置信度分析器"""

    def __init__(self, models: List[str] = None, api_key: str = None):
        # 默认使用实际可用的模型（暂时移除有问题的Claude API）
        self.models = models or ["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        self.api_key = api_key
        self.results = {}

    def analyze_with_multiple_models(self, input_file: Path, output_dir: Path) -> Dict:
        """使用多个模型分析同一份测评报告"""
        print(f"🤖 开始多模型分析: {input_file.name}")
        print(f"📊 使用模型: {', '.join(self.models)}")

        # 创建模型特定的输出目录
        model_output_dir = output_dir / "multi_model_results"
        model_output_dir.mkdir(parents=True, exist_ok=True)

        multi_model_results = {}

        # 使用多个模型进行分析
        for model in self.models:
            print(f"\n🔍 正在使用模型 {model} 分析...")

            try:
                analyzer = EnhancedCloudAnalyzer(
                    model=model,
                    api_key=self.api_key
                )

                if not analyzer.api_available:
                    print(f"❌ 模型 {model} API不可用，跳过")
                    continue

                # 为每个模型创建独立的输出目录
                model_dir = model_output_dir / model
                model_dir.mkdir(exist_ok=True)

                # 执行分析
                result = analyzer.analyze_full_assessment(str(input_file), str(model_dir))

                if result['success']:
                    # 获取最终评分和MBTI结果
                    final_scores = result.get('final_scores', {})
                    mbti_result = result.get('mbti_result', {})

                    multi_model_results[model] = {
                        'success': True,
                        'big5_scores': {trait: data.get('final_score', 3) for trait, data in final_scores.items()},
                        'mbti_type': mbti_result.get('type', 'Unknown'),
                        'final_scores_detailed': final_scores,
                        'mbti_detailed': mbti_result,
                        'summary_file': result.get('summary_file', 'N/A'),
                        'evidence_file': result.get('evidence_file', 'N/A')
                    }

                    big5_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in multi_model_results[model]['big5_scores'].items()])
                    print(f"✅ {model} - Big5: {big5_str} - MBTI: {mbti_result['type']}")
                else:
                    print(f"❌ {model} 分析失败: {result.get('error', 'Unknown error')}")
                    multi_model_results[model] = {
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }

            except Exception as e:
                print(f"💥 {model} 分析异常: {e}")
                multi_model_results[model] = {
                    'success': False,
                    'error': str(e)
                }

        # 计算多模型置信度
        confidence_analysis = self.calculate_multi_model_confidence(multi_model_results)

        # 生成多模型汇总报告
        self.save_multi_model_report(
            input_file,
            multi_model_results,
            confidence_analysis,
            model_output_dir
        )

        return {
            'file': str(input_file),
            'multi_model_results': multi_model_results,
            'confidence_analysis': confidence_analysis,
            'success': len(multi_model_results) > 0
        }

    def calculate_multi_model_confidence(self, multi_model_results: Dict) -> Dict:
        """基于多模型比较计算置信度"""
        successful_models = [model for model, result in multi_model_results.items() if result['success']]

        if len(successful_models) < 2:
            return {
                'overall_confidence': 0.0,
                'big5_confidence': {},
                'mbti_confidence': {},
                'note': f'只有 {len(successful_models)} 个模型成功分析，无法计算多模型置信度'
            }

        print(f"\n📈 计算 {len(successful_models)} 个模型之间的置信度...")

        # 收集所有成功模型的评分
        big5_scores_by_model = {}
        mbti_types_by_model = {}

        for model in successful_models:
            result = multi_model_results[model]
            big5_scores_by_model[model] = result['big5_scores']
            mbti_types_by_model[model] = result['mbti_type']

        # 计算Big5每个维度的置信度
        big5_confidence = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        for trait in traits:
            scores = [big5_scores_by_model[model][trait] for model in successful_models]
            confidence = self.calculate_score_agreement(scores)
            big5_confidence[trait] = {
                'confidence_percent': confidence,
                'scores_by_model': {model: big5_scores_by_model[model][trait] for model in successful_models},
                'agreement_level': self.get_agreement_level(confidence)
            }

        # 计算MBTI置信度
        mbti_confidence = self.calculate_mbti_agreement(mbti_types_by_model)

        # 计算总体置信度
        big5_confidences = [conf['confidence_percent'] for conf in big5_confidence.values()]
        overall_confidence = sum(big5_confidences) / len(big5_confidences)

        confidence_analysis = {
            'overall_confidence': round(overall_confidence, 1),
            'big5_confidence': big5_confidence,
            'mbti_confidence': mbti_confidence,
            'successful_models': successful_models,
            'total_models_attempted': len(self.models),
            'analysis_timestamp': datetime.now().isoformat()
        }

        # 打印置信度分析结果
        print(f"🎯 总体置信度: {confidence_analysis.get('overall_confidence', 0)}%")
        print(f"📊 Big5各维度置信度:")
        for trait, conf in big5_confidence.items():
            trait_name = trait.replace('_', ' ').title()
            print(f"  {trait_name}: {conf.get('confidence_percent', 0)}% ({conf.get('agreement_level', 'Unknown')})")
        print(f"🧠 MBTI置信度: {mbti_confidence.get('confidence_percent', 0)}% ({mbti_confidence.get('agreement_level', 'Unknown')})")

        return confidence_analysis

    def calculate_score_agreement(self, scores: List[int]) -> float:
        """计算评分间的一致性（基于完全匹配的比例）"""
        if len(scores) < 2:
            return 0.0

        # 计算评分分布，支持各种可能的评分值
        score_counts = {}
        for score in scores:
            if score not in score_counts:
                score_counts[score] = 0
            score_counts[score] += 1

        # 最常见的评分及其出现次数
        most_common_score = max(score_counts, key=score_counts.get)
        agreement_count = score_counts[most_common_score]

        # 置信度 = 最多评分的数量 / 总评分数量
        confidence = (agreement_count / len(scores)) * 100

        return round(confidence, 1)

    def calculate_mbti_agreement(self, mbti_types: Dict[str, str]) -> Dict:
        """计算MBTI类型间的一致性"""
        if len(mbti_types) < 2:
            return {
                'confidence_percent': 0.0,
                'agreement_level': '无法计算',
                'types_by_model': mbti_types
            }

        # 统计MBTI类型分布
        type_counts = {}
        for model, mbti_type in mbti_types.items():
            if mbti_type not in type_counts:
                type_counts[mbti_type] = []
            type_counts[mbti_type].append(model)

        # 最常见的MBTI类型
        most_common_type = max(type_counts, key=lambda x: len(type_counts[x]))
        agreement_count = len(type_counts[most_common_type])

        # 置信度计算
        confidence = (agreement_count / len(mbti_types)) * 100

        return {
            'confidence_percent': round(confidence, 1),
            'agreement_level': self.get_agreement_level(confidence),
            'most_common_type': most_common_type,
            'types_by_model': mbti_types,
            'type_distribution': {mbti_type: len(models) for mbti_type, models in type_counts.items()}
        }

    def get_agreement_level(self, confidence_percent: float) -> str:
        """根据置信度百分比返回一致性级别"""
        if confidence_percent >= 80:
            return "高度一致"
        elif confidence_percent >= 60:
            return "中等一致"
        elif confidence_percent >= 40:
            return "低度一致"
        else:
            return "不一致"

    def save_multi_model_report(self, input_file: Path, multi_model_results: Dict,
                               confidence_analysis: Dict, output_dir: Path):
        """保存多模型分析报告"""
        filename_base = input_file.stem

        # 保存详细的多模型分析结果
        report_data = {
            'analysis_info': {
                'file_analyzed': str(input_file),
                'filename': input_file.name,
                'analysis_timestamp': datetime.now().isoformat(),
                'models_used': self.models,
                'algorithm': 'multi_model_confidence_v1.0'
            },
            'multi_model_results': multi_model_results,
            'confidence_analysis': confidence_analysis
        }

        # 保存JSON格式的详细报告
        json_report = output_dir / f"{filename_base}_multi_model_confidence.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        # 生成Markdown摘要报告
        self.generate_markdown_summary(report_data, output_dir, filename_base)

        print(f"📋 多模型置信度报告已保存:")
        print(f"   详细报告: {json_report}")
        print(f"   摘要报告: {output_dir / f'{filename_base}_multi_model_summary.md'}")

    def generate_markdown_summary(self, report_data: Dict, output_dir: Path, filename_base: str):
        """生成Markdown格式的多模型分析摘要"""
        confidence = report_data['confidence_analysis']
        successful_models = confidence.get('successful_models', [])

        md_content = f"""# 多模型置信度分析报告

## 基本信息

- **分析文件:** {report_data['analysis_info']['filename']}
- **分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **使用模型:** {', '.join(report_data['analysis_info']['models_used'])}
- **成功模型:** {', '.join(successful_models)} ({len(successful_models)}/{len(self.models)})
- **算法版本:** multi_model_confidence_v1.0

## 总体置信度

**{confidence['overall_confidence']}%** - {self.get_agreement_level(confidence['overall_confidence'])}

## Big5各维度置信度

| 维度 | 置信度 | 一致性级别 | 各模型评分 |
|------|--------|------------|------------|
"""

        traits_display = {
            'openness_to_experience': '开放性 (O)',
            'conscientiousness': '尽责性 (C)',
            'extraversion': '外向性 (E)',
            'agreeableness': '宜人性 (A)',
            'neuroticism': '神经质 (N)'
        }

        for trait, conf in confidence['big5_confidence'].items():
            trait_display = traits_display.get(trait, trait)
            scores_str = ", ".join([f"{model}:{score}" for model, score in conf['scores_by_model'].items()])
            md_content += f"| {trait_display} | {conf['confidence_percent']}% | {conf['agreement_level']} | {scores_str} |\n"

        md_content += f"""
## MBTI置信度

**{confidence['mbti_confidence']['confidence_percent']}%** - {confidence['mbti_confidence']['agreement_level']}

- **最常见的MBTI类型:** {confidence['mbti_confidence']['most_common_type']}
- **各模型结果:** {', '.join([f"{model}:{mbti}" for model, mbti in confidence['mbti_confidence']['types_by_model'].items()])}

## 详细评分对比

| 模型 | O | C | E | A | N | MBTI |
|------|---|---|---|---|---|------|
"""

        for model in successful_models:
            if model in report_data['multi_model_results'] and report_data['multi_model_results'][model]['success']:
                result = report_data['multi_model_results'][model]
                scores = result['big5_scores']
                mbti = result['mbti_type']
                md_content += f"| {model} | {scores['openness_to_experience']} | {scores['conscientiousness']} | {scores['extraversion']} | {scores['agreeableness']} | {scores['neuroticism']} | {mbti} |\n"

        # 保存Markdown文件
        md_file = output_dir / f"{filename_base}_multi_model_summary.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

def main():
    """测试多模型置信度分析"""
    if len(sys.argv) < 2:
        print("用法: python multi_model_confidence_analyzer.py <input_file> [output_dir]")
        return

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"❌ 文件不存在: {input_file}")
        return

    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("multi_model_confidence_results")

    # 创建多模型分析器
    analyzer = MultiModelConfidenceAnalyzer()

    # 执行分析
    result = analyzer.analyze_with_multiple_models(input_file, output_dir)

    if result['success']:
        print(f"\n🎉 多模型置信度分析完成!")
        confidence = result['confidence_analysis']['overall_confidence']
        print(f"📊 总体置信度: {confidence}%")
        print(f"📁 结果保存在: {output_dir}")
    else:
        print(f"\n❌ 多模型分析失败")

if __name__ == "__main__":
    main()