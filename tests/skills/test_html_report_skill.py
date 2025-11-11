#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join('.claude', 'skills', 'html-report-generator'))
from skill import HtmlReportGeneratorSkill

def main():
    print('🎨 使用HTML报告生成器技能创建专业认知压力测评报告')
    print('=' * 70)

    # 创建技能实例
    html_skill = HtmlReportGeneratorSkill()

    # 读取所有四种条件的50题认知压力测评数据
    data_files = [
        {
            'file': 'results/complete_50_基线条件_20251110_165354.json',
            'name': '基线条件',
            'description': '基线条件，无任何认知干扰，使用完整IPIP-FFM-50量表'
        },
        {
            'file': 'results/complete_50_语义谬误干扰_20251110_165610.json',
            'name': '语义谬误干扰',
            'description': '语义谬误干扰 + 中等上下文'
        },
        {
            'file': 'results/complete_50_悖论陷阱干扰_20251110_165838.json',
            'name': '悖论陷阱干扰',
            'description': '悖论陷阱干扰 + 中等上下文'
        },
        {
            'file': 'results/complete_50_循环论证干扰_20251110_170107.json',
            'name': '循环论证干扰',
            'description': '循环论证干扰 + 高上下文'
        }
    ]

    # 读取所有数据
    all_data = []
    missing_files = []

    for data_info in data_files:
        if os.path.exists(data_info['file']):
            with open(data_info['file'], 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.append({
                    'condition': data['condition'],
                    'performance_metrics': data['performance_metrics'],
                    'questionnaire_result': data['questionnaire_result'],
                    'condition_name': data_info['name'],
                    'condition_description': data_info['description']
                })
            print(f'✅ 已读取: {data_info["name"]} ({data_info["file"]})')
        else:
            missing_files.append(data_info['file'])
            print(f'❌ 文件不存在: {data_info["file"]}')

    if missing_files:
        print(f'\n⚠️ 发现 {len(missing_files)} 个缺失文件，将使用现有数据生成报告')
        print(f'缺失文件: {missing_files}')

    if not all_data:
        print('❌ 没有找到任何有效数据文件')
        return

    print(f'\n📊 成功读取 {len(all_data)} 个条件的测评数据')
    print('-' * 70)

    # 使用人格评估器技能分析所有条件
    sys.path.append(os.path.join('.claude', 'skills', 'personality-assessor'))
    from skill import PersonalityAssessor

    print('🧠 使用人格评估器技能分析各条件下的人格表现...')
    personality_assessor = PersonalityAssessor()

    for i, data in enumerate(all_data):
        condition_name = data['condition_name']
        print(f'\n🔹 分析条件 {i+1}/4: {condition_name}')

        try:
            # 使用人格评估器技能分析
            personality_result = personality_assessor.evaluate_personality(
                responses=data['questionnaire_result']['answers']
            )

            if personality_result['success']:
                data['personality_analysis'] = personality_result['personality_analysis']
                print(f'✅ {condition_name} 人格分析成功')
                print(f'   大五人格: O={data["personality_analysis"]["big_five_scores"]["Openness"]:.1f}, C={data["personality_analysis"]["big_five_scores"]["Conscientiousness"]:.1f}, E={data["personality_analysis"]["big_five_scores"]["Extraversion"]:.1f}, A={data["personality_analysis"]["big_five_scores"]["Agreeableness"]:.1f}, N={data["personality_analysis"]["big_five_scores"]["Neuroticism"]:.1f}')
                print(f'   MBTI类型: {data["personality_analysis"]["mbti_type"]}')
                print(f'   Belbin角色: {data["personality_analysis"]["belbin_role"]}')
            else:
                print(f'❌ {condition_name} 人格分析失败: {personality_result.get("error", "未知错误")}')
                data['personality_analysis'] = None

        except Exception as e:
            print(f'❌ {condition_name} 人格分析出错: {e}')
            data['personality_analysis'] = None

    # 准备综合报告数据
    comprehensive_report_data = {
        'title': '完整50题IPIP-FFM认知压力测评专业报告',
        'subtitle': '四种认知干扰条件下的人格表现对比分析',
        'test_info': {
            'scale': 'IPIP-FFM-50 完整量表',
            'total_questions': 50,
            'dimensions': ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'],
            'test_date': datetime.now().strftime('%Y-%m-%d'),
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'conditions': all_data,
        'summary_analysis': {
            'total_conditions': len(all_data),
            'successful_analyses': sum(1 for data in all_data if data['personality_analysis'] is not None),
            'data_completeness': f'{len(all_data)}/4 条件数据完整'
        },
        'brand_info': {
            'company_name': 'AI人格实验室',
            'website': 'https://cn.agentpsy.com',
            'report_title': '认知压力测评专业报告',
            'report_id': f'COMPREHENSIVE_50_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
    }

    print('\n🔹 开始生成综合HTML报告...')

    # 生成HTML报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'html/comprehensive_50_cognitive_stress_report_{timestamp}.html'

    result = html_skill.generate_html_report(
        report_data=comprehensive_report_data,
        output_filename=output_filename,
        report_title='完整50题IPIP-FFM认知压力测评专业报告'
    )

    if result['success']:
        print(f'\n🎉 综合HTML报告生成成功!')
        print(f'📄 输出文件: {result["output_file"]}')
        print(f'📏 文件大小: {result["file_size"]:,} 字符')
        print(f'⏰ 生成时间: {result["generation_time"]}')

        # 检查文件是否存在并验证内容
        if os.path.exists(result['output_file']):
            actual_size = os.path.getsize(result['output_file'])
            print(f'💾 实际文件大小: {actual_size:,} 字节')

            # 验证HTML内容
            with open(result['output_file'], 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 关键内容检查
            key_elements = {
                '报告标题': comprehensive_report_data['title'] in html_content,
                '品牌标识': 'AI人格实验室' in html_content,
                '官网链接': 'cn.agentpsy.com' in html_content,
                '条件数量': f'{len(all_data)}' in html_content,
                '量表信息': 'IPIP-FFM-50' in html_content,
                '专业CSS': '<style>' in html_content,
                '响应式设计': 'media' in html_content.lower(),
                '数据表格': '<table>' in html_content,
                '分析图表': 'chart' in html_content.lower() or 'visualization' in html_content.lower()
            }

            print('\n🔍 关键内容验证:')
            passed_checks = 0
            for element_name, passed in key_elements.items():
                status = '✅' if passed else '❌'
                print(f'   {status} {element_name}')
                if passed:
                    passed_checks += 1

            print(f'\n📊 内容验证通过率: {passed_checks}/{len(key_elements)} ({passed_checks/len(key_elements)*100:.1f}%)')

            # 统计条件信息
            successful_conditions = [data for data in all_data if data['personality_analysis'] is not None]
            if successful_conditions:
                print(f'\n📈 成功分析的条件数: {len(successful_conditions)}/{len(all_data)}')
                print('🧠 各条件下的人格表现:')
                for data in successful_conditions:
                    analysis = data['personality_analysis']
                    big_five = analysis['big_five_scores']
                    print(f'   🔸 {data["condition_name"]}: MBTI={analysis["mbti_type"]}, Belbin={analysis["belbin_role"]}')
                    print(f'      O={big_five["Openness"]:.1f}, C={big_five["Conscientiousness"]:.1f}, E={big_five["Extraversion"]:.1f}, A={big_five["Agreeableness"]:.1f}, N={big_five["Neuroticism"]:.1f}')

            if passed_checks >= len(key_elements) * 0.8:  # 80%通过率
                print('\n🎉 HTML报告生成器技能表现优秀！')
                print('✨ 专业报告生成完成，包含品牌标识和完整数据分析')
            else:
                print('\n⚠️ 报告生成基本成功，但部分内容需要完善')

        else:
            print('\n❌ 报告文件未成功生成')
    else:
        print(f'\n❌ HTML报告生成失败: {result.get("error", "未知错误")}')

if __name__ == '__main__':
    main()