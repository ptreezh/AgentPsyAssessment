#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于现有结果生成汇总报告
"""

import json
from pathlib import Path
from datetime import datetime

def generate_current_summary():
    print("📊 基于现有结果生成汇总报告...")

    # 结果目录
    results_dir = Path("four_model_results/multi_model_results")
    if not results_dir.exists():
        print("❌ 结果目录不存在")
        return

    # 收集所有成功的结果
    successful_results = []
    failed_results = []

    # 查找所有summary文件
    summary_files = list(results_dir.glob("*/*summary.json"))
    print(f"📁 找到 {len(summary_files)} 个结果文件")

    for summary_file in summary_files:
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查是否成功（基于分析质量）
            analysis_quality = data.get('analysis_quality', {})
            success_rate = analysis_quality.get('success_rate', 0)

            if success_rate > 0:  # 有成功的分段
                big5_scores = data.get('big5_final_scores', {})
                mbti_type = data.get('mbti_type', 'N/A')
                mbti_confidence = data.get('mbti_confidence', 0)
                model_used = data.get('analysis_info', {}).get('model_used', 'Unknown')
                filename = data.get('analysis_info', {}).get('filename', 'Unknown')

                # 提取Big5评分
                big5_simple = {}
                for trait, scores in big5_scores.items():
                    big5_simple[trait] = scores.get('final_score', 3)

                successful_results.append({
                    'filename': filename,
                    'model': model_used,
                    'big5_scores': big5_simple,
                    'mbti_type': mbti_type,
                    'mbti_confidence': mbti_confidence,
                    'success_rate': success_rate,
                    'analysis_time': data.get('analysis_info', {}).get('analysis_timestamp', '')
                })
            else:
                failed_results.append({
                    'filename': data.get('analysis_info', {}).get('filename', 'Unknown'),
                    'model': data.get('analysis_info', {}).get('model_used', 'Unknown'),
                    'error': '分析失败 (成功率0%)'
                })

        except Exception as e:
            failed_results.append({
                'filename': summary_file.name,
                'error': f'读取失败: {e}'
            })

    print(f"✅ 成功结果: {len(successful_results)}")
    print(f"❌ 失败结果: {len(failed_results)}")

    if not successful_results:
        print("❌ 没有成功的结果可以分析")
        return

    # 按文件分组结果
    file_results = {}
    for result in successful_results:
        filename = result['filename']
        if filename not in file_results:
            file_results[filename] = []
        file_results[filename].append(result)

    # 统计分析
    print(f"\n📈 分析统计:")
    print(f"   成功分析的文件数: {len(file_results)}")
    print(f"   使用的模型: {list(set(r['model'] for r in successful_results))}")

    # Big5评分分布
    big5_stats = {}
    mbti_stats = {}

    for filename, results in file_results.items():
        if len(results) >= 2:  # 只统计有多模型结果的文件
            # 统计MBTI
            mbti_types = [r['mbti_type'] for r in results]
            for mbti in mbti_types:
                mbti_stats[mbti] = mbti_stats.get(mbti, 0) + 1

            # 统计Big5 (使用第一个成功模型的结果)
            first_result = results[0]
            for trait, score in first_result['big5_scores'].items():
                if trait not in big5_stats:
                    big5_stats[trait] = {1: 0, 3: 0, 5: 0}
                big5_stats[trait][score] += 1

    print(f"\n🎯 MBTI类型分布:")
    for mbti, count in sorted(mbti_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = count / sum(mbti_stats.values()) * 100
        print(f"   {mbti}: {count} ({percentage:.1f}%)")

    print(f"\n📊 Big5评分分布:")
    trait_names = {
        'openness_to_experience': '开放性 (O)',
        'conscientiousness': '尽责性 (C)',
        'extraversion': '外向性 (E)',
        'agreeableness': '宜人性 (A)',
        'neuroticism': '神经质 (N)'
    }

    for trait, scores in big5_stats.items():
        trait_name = trait_names.get(trait, trait)
        total = sum(scores.values())
        print(f"\n   {trait_name}:")
        for score in [1, 3, 5]:
            if scores[score] > 0:
                percentage = scores[score] / total * 100
                print(f"     {score}分: {scores[score]} ({percentage:.1f}%)")

    # 生成详细报告
    summary_report = {
        'summary': {
            'total_files_analyzed': len(file_results),
            'successful_analyses': len(successful_results),
            'failed_analyses': len(failed_results),
            'models_used': list(set(r['model'] for r in successful_results)),
            'analysis_timestamp': datetime.now().isoformat(),
            'data_source': 'four_model_results/multi_model_results'
        },
        'statistics': {
            'mbti_distribution': mbti_stats,
            'big5_distribution': big5_stats
        },
        'detailed_results': file_results
    }

    # 保存汇总报告
    output_file = Path("current_analysis_summary.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 汇总报告已保存: {output_file}")

    # 生成Markdown报告
    generate_markdown_report(summary_report)

def generate_markdown_report(summary_data):
    """生成Markdown格式报告"""
    summary = summary_data['summary']
    mbti_stats = summary_data['statistics']['mbti_distribution']
    big5_stats = summary_data['statistics']['big5_distribution']
    detailed_results = summary_data['detailed_results']

    trait_names = {
        'openness_to_experience': '开放性 (O)',
        'conscientiousness': '尽责性 (C)',
        'extraversion': '外向性 (E)',
        'agreeableness': '宜人性 (A)',
        'neuroticism': '神经质 (N)'
    }

    md_content = f"""# 心理评估分析汇总报告

## 基本信息

- **分析时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析文件数:** {summary['total_files_analyzed']}
- **成功分析数:** {summary['successful_analyses']}
- **失败分析数:** {summary['failed_analyses']}
- **使用模型:** {', '.join(summary['models_used'])}
- **数据来源:** {summary['data_source']}

## MBTI类型分布

"""

    total_mbti = sum(mbti_stats.values())
    for mbti, count in sorted(mbti_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = count / total_mbti * 100 if total_mbti > 0 else 0
        md_content += f"- **{mbti}:** {count} ({percentage:.1f}%)\n"

    md_content += "\n## Big5评分分布\n\n"

    for trait, scores in big5_stats.items():
        trait_name = trait_names.get(trait, trait)
        total = sum(scores.values())
        md_content += f"### {trait_name}\n"
        for score in [1, 3, 5]:
            if scores.get(score, 0) > 0:
                percentage = scores[score] / total * 100 if total > 0 else 0
                md_content += f"- **{score}分:** {scores[score]} ({percentage:.1f}%)\n"
        md_content += "\n"

    md_content += "## 详细分析结果\n\n"

    for filename, results in detailed_results.items():
        md_content += f"### {filename}\n\n"

        if len(results) >= 2:
            # 多模型结果对比
            md_content += "**多模型对比:**\n\n"
            md_content += "| 模型 | MBTI | 置信度 | Big5 (O,C,E,A,N) | 成功率 |\n"
            md_content += "|------|------|--------|------------------|--------|\n"

            for result in results:
                big5_str = ",".join(str(result['big5_scores'][t]) for t in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'])
                md_content += f"| {result['model']} | {result['mbti_type']} | {result['mbti_confidence']:.1f}% | {big5_str} | {result['success_rate']:.1f}% |\n"

            # 计算一致性
            mbti_types = [r['mbti_type'] for r in results]
            mbti_agreement = len(set(mbti_types)) == 1
            md_content += f"\n**MBTI一致性:** {'✅ 一致' if mbti_agreement else '❌ 不一致'}\n"
        else:
            # 单模型结果
            result = results[0]
            big5_str = ",".join(str(result['big5_scores'][t]) for t in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'])
            md_content += f"- **模型:** {result['model']}\n"
            md_content += f"- **MBTI:** {result['mbti_type']} (置信度: {result['mbti_confidence']:.1f}%)\n"
            md_content += f"- **Big5:** {big5_str}\n"
            md_content += f"- **成功率:** {result['success_rate']:.1f}%\n"

        md_content += "\n"

    # 保存Markdown报告
    md_file = Path("current_analysis_report.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ Markdown报告已保存: {md_file}")

if __name__ == "__main__":
    generate_current_summary()