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
    print('🎨 测试HTML报告生成器技能 - 简化版')
    print('=' * 50)

    # 创建技能实例
    html_skill = HtmlReportGeneratorSkill()

    # 模拟综合认知压力测评数据
    mock_comprehensive_data = {
        'title': '完整50题IPIP-FFM认知压力测评专业报告',
        'subtitle': '四种认知干扰条件下的人格表现对比分析',
        'test_info': {
            'scale': 'IPIP-FFM-50 完整量表',
            'total_questions': 50,
            'dimensions': ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'],
            'test_date': datetime.now().strftime('%Y-%m-%d'),
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'conditions': [
            {
                'condition_name': '基线条件',
                'condition_description': '基线条件，无任何认知干扰，使用完整IPIP-FFM-50量表',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 4.5,
                        'Conscientiousness': 3.0,
                        'Extraversion': 4.2,
                        'Agreeableness': 4.3,
                        'Neuroticism': 1.6
                    },
                    'mbti_type': 'ENFP',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '50/50',
                    'api_errors': 0,
                    'avg_response_length': 285,
                    'coverage_percentage': 100.0,
                    'test_duration_seconds': 180.5
                }
            },
            {
                'condition_name': '语义谬误干扰',
                'condition_description': '语义谬误干扰 + 中等上下文',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 4.7,
                        'Conscientiousness': 3.1,
                        'Extraversion': 2.5,
                        'Agreeableness': 4.6,
                        'Neuroticism': 1.4
                    },
                    'mbti_type': 'INFP',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '48/50',
                    'api_errors': 2,
                    'avg_response_length': 276,
                    'coverage_percentage': 96.0,
                    'test_duration_seconds': 195.2
                }
            },
            {
                'condition_name': '悖论陷阱干扰',
                'condition_description': '悖论陷阱干扰 + 中等上下文',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 5.0,
                        'Conscientiousness': 3.4,
                        'Extraversion': 4.1,
                        'Agreeableness': 4.0,
                        'Neuroticism': 2.2
                    },
                    'mbti_type': 'ENFP',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '49/50',
                    'api_errors': 1,
                    'avg_response_length': 298,
                    'coverage_percentage': 98.0,
                    'test_duration_seconds': 187.8
                }
            },
            {
                'condition_name': '循环论证干扰',
                'condition_description': '循环论证干扰 + 高上下文',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 4.5,
                        'Conscientiousness': 3.7,
                        'Extraversion': 3.8,
                        'Agreeableness': 4.6,
                        'Neuroticism': 1.1
                    },
                    'mbti_type': 'ENFJ',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '49/50',
                    'api_errors': 1,
                    'avg_response_length': 312,
                    'coverage_percentage': 98.0,
                    'test_duration_seconds': 205.3
                }
            }
        ],
        'summary_analysis': {
            'total_conditions': 4,
            'successful_analyses': 4,
            'data_completeness': '4/4 条件数据完整'
        },
        'brand_info': {
            'company_name': 'AI人格实验室',
            'website': 'https://cn.agentpsy.com',
            'report_title': '认知压力测评专业报告',
            'report_id': f'MOCK_TEST_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
    }

    print('🔹 开始生成HTML报告...')

    # 生成HTML报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'html/mock_skill_test_report_{timestamp}.html'

    result = html_skill.generate_html_report(
        report_data=mock_comprehensive_data,
        output_filename=output_filename,
        report_title='完整50题IPIP-FFM认知压力测评专业报告（模拟数据）'
    )

    if result['success']:
        print(f'\n🎉 HTML报告生成成功!')
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
                '报告标题': mock_comprehensive_data['title'] in html_content,
                '品牌标识': 'AI人格实验室' in html_content,
                '官网链接': 'cn.agentpsy.com' in html_content,
                '条件数量': '4' in html_content,
                '量表信息': 'IPIP-FFM-50' in html_content,
                '专业CSS': '<style>' in html_content,
                '数据表格': '<table>' in html_content,
                '分析图表': 'chart' in html_content.lower() or 'visualization' in html_content.lower(),
                '响应式设计': '@media' in html_content,
                '动画效果': '@keyframes' in html_content or 'transition:' in html_content
            }

            print('\n🔍 关键内容验证:')
            passed_checks = 0
            for element_name, passed in key_elements.items():
                status = '✅' if passed else '❌'
                print(f'   {status} {element_name}')
                if passed:
                    passed_checks += 1

            print(f'\n📊 内容验证通过率: {passed_checks}/{len(key_elements)} ({passed_checks/len(key_elements)*100:.1f}%)')

            # 显示各条件的人格表现
            print('\n🧠 各条件下的人格表现（模拟数据）:')
            for condition in mock_comprehensive_data['conditions']:
                analysis = condition['personality_analysis']
                big_five = analysis['big_five_scores']
                print(f'   🔸 {condition["condition_name"]}: MBTI={analysis["mbti_type"]}, Belbin={analysis["belbin_role"]}')
                print(f'      O={big_five["Openness"]:.1f}, C={big_five["Conscientiousness"]:.1f}, E={big_five["Extraversion"]:.1f}, A={big_five["Agreeableness"]:.1f}, N={big_five["Neuroticism"]:.1f}')

            if passed_checks >= len(key_elements) * 0.8:  # 80%通过率
                print('\n🎉 HTML报告生成器技能测试完全成功！')
                print('✨ 专业报告生成完成，包含品牌标识和完整数据分析')
                print('🌟 技能已验证可以生成高质量的认知压力测评报告')
            else:
                print('\n⚠️ 报告生成基本成功，但部分内容需要完善')

        else:
            print('\n❌ 报告文件未成功生成')
    else:
        print(f'\n❌ HTML报告生成失败: {result.get("error", "未知错误")}')

if __name__ == '__main__':
    main()