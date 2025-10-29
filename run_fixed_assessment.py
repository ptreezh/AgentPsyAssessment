#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用修复后的1-3-5评分标准重新运行完整评估
"""

import json
import sys
import os
import time

def run_fixed_full_assessment():
    """运行使用修复后评分标准的完整评估"""
    print("=" * 60)
    print("开始执行使用1-3-5评分标准的完整50题评估")
    print("=" * 60)
    print("开始时间: " + time.strftime('%Y-%m-%d %H:%M:%S'))
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 设置环境变量解决Windows编码问题
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # 导入必要的模块
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'batchAnalysizeTools'))
        from batch_segmented_analysis import BatchSegmentedPersonalityAnalyzer
        
        # 加载评估数据
        print("1. 加载评估文件...")
        with open("results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_def_e0_t0_0_09091.json", 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
        print("   文件加载成功")
        
        # 初始化分析器
        print("2. 初始化分析器...")
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=2,  # 每段2个问题
            evaluator_name="gemma3",
            base_url="http://localhost:11434"
        )
        print("   分析器初始化成功")
        
        # 提取问题
        print("3. 提取问题...")
        questions = analyzer.extract_questions(assessment_data)
        print("   成功提取 " + str(len(questions)) + " 个问题")
        
        # 创建分段
        print("4. 创建分段...")
        segments = analyzer.create_segments(questions)
        print("   成功创建 " + str(len(segments)) + " 个分段")
        
        # 分析所有分段
        print("5. 开始分析所有分段...")
        successful_segments = 0
        total_questions_analyzed = 0
        
        for i in range(len(segments)):
            segment = segments[i]
            print("   分析第 " + str(i+1) + "/" + str(len(segments)) + " 个分段 (" + str(len(segment)) + " 个问题)..."))
            try:
                segment_analysis = analyzer.analyze_segment(segment, i+1)
                if 'llm_response' in segment_analysis:
                    analyzer.accumulate_scores(segment_analysis['llm_response'])
                    successful_segments += 1
                    total_questions_analyzed += len(segment)
                    print("     分段 " + str(i+1) + " 分析完成")
                else:
                    print("     分段 " + str(i+1) + " 分析失败")
            except Exception as e:
                print("     分段 " + str(i+1) + " 分析出错: " + str(e))
                continue
        
        print("   成功分析 " + str(successful_segments) + "/" + str(len(segments)) + " 个分段")
        print("   总共分析 " + str(total_questions_analyzed) + " 个问题")
        
        # 计算最终分数
        print("6. 计算最终分数...")
        final_scores = analyzer.calculate_final_scores()
        print("   最终分数计算成功")
        
        # 生成报告
        print("7. 生成完整报告...")
        generate_fixed_final_report(final_scores)
        
        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("=" * 60)
        print("使用1-3-5评分标准的完整评估执行完成!")
        print("结束时间: " + time.strftime('%Y-%m-%d %H:%M:%S'))
        print("总耗时: " + str(round(elapsed_time, 2)) + " 秒 (" + str(round(elapsed_time/60, 2)) + " 分钟)")
        print("=" * 60)
        
    except Exception as e:
        print("执行过程中出现错误: " + str(e))
        import traceback
        traceback.print_exc()

def generate_fixed_final_report(final_scores):
    """生成最终报告"""
    # Big Five 分数
    print("\n【Big Five 人格维度评分】")
    print("-" * 40)
    big_five_scores = final_scores['big_five']
    
    traits = [
        ('openness_to_experience', '开放性'),
        ('conscientiousness', '尽责性'),
        ('extraversion', '外向性'),
        ('agreeableness', '宜人性'),
        ('neuroticism', '神经质')
    ]
    
    for trait_key, trait_name in traits:
        score = big_five_scores[trait_key]['score']
        weight = big_five_scores[trait_key]['weight']
        print(trait_name + " : " + str(round(score, 1)) + "/10.0 (基于 " + str(weight) + " 个问题)")
    
    # MBTI 类型
    print("\n【MBTI 人格类型】")
    print("-" * 40)
    mbti = final_scores['mbti']
    print("类型: " + mbti['type'])
    print("置信度: " + str(round(mbti['confidence'], 2)))
    
    # Belbin 团队角色
    print("\n【Belbin 团队角色】")
    print("-" * 40)
    belbin = final_scores['belbin']
    print("主要角色: " + belbin['primary_role'])
    print("次要角色: " + belbin['secondary_role'])
    
    # 保存完整报告到文件
    report_data = {
        'summary': {
            'big_five': big_five_scores,
            'mbti': mbti,
            'belbin': belbin,
            'total_questions_analyzed': len(final_scores['per_question_scores'])
        },
        'per_question_scores': final_scores['per_question_scores'],
        'analysis_summary': final_scores['analysis_summary']
    }
    
    # 保存JSON格式报告
    with open('batchAnalysizeTools/fixed_full_assessment_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print("\nJSON格式完整报告已保存到: batchAnalysizeTools/fixed_full_assessment_report.json")
    
    # 生成Markdown格式报告
    generate_fixed_markdown_report(report_data)
    print("Markdown格式完整报告已保存到: batchAnalysizeTools/fixed_full_assessment_report.md")

def generate_fixed_markdown_report(report_data):
    """生成Markdown格式报告"""
    md_content = "# 使用1-3-5评分标准的完整50题人格测评报告\n\n"
    md_content += "## 概述\n\n"
    md_content += "本报告基于50个问题的完整人格测评，使用Gemma3模型进行分析，严格遵循1-3-5三档评分标准。\n\n"
    
    md_content += "## Big Five 人格维度评分\n\n"
    md_content += "| 维度 | 分数 | 问题数量 |\n"
    md_content += "|------|------|----------|\n"
    
    big_five = report_data['summary']['big_five']
    traits = [
        ('openness_to_experience', '开放性'),
        ('conscientiousness', '尽责性'),
        ('extraversion', '外向性'),
        ('agreeableness', '宜人性'),
        ('neuroticism', '神经质')
    ]
    
    for trait_key, trait_name in traits:
        score = big_five[trait_key]['score']
        weight = big_five[trait_key]['weight']
        md_content += "| " + trait_name + " | " + str(round(score, 1)) + "/10.0 | " + str(weight) + " |\n"
    
    md_content += "\n## MBTI 人格类型\n\n"
    md_content += "- 类型: " + report_data['summary']['mbti']['type'] + "\n"
    md_content += "- 置信度: " + str(round(report_data['summary']['mbti']['confidence'], 2)) + "\n\n"
    
    md_content += "## Belbin 团队角色\n\n"
    md_content += "- 主要角色: " + report_data['summary']['belbin']['primary_role'] + "\n"
    md_content += "- 次要角色: " + report_data['summary']['belbin']['secondary_role'] + "\n\n"
    
    md_content += "## 问题级别详细评分\n\n"
    md_content += "以下为所有问题的详细评分（严格遵循1-3-5评分标准）:\n"
    
    for i in range(len(report_data['per_question_scores'])):
        score = report_data['per_question_scores'][i]
        md_content += "\n### 问题 " + str(i+1) + ": " + score['dimension'] + "\n\n"
        md_content += "- 问题ID: " + score['question_id'] + "\n"
        md_content += "- Big Five 评分:\n"
        
        for trait, trait_score in score['big_five_scores'].items():
            # 确保评分是1, 3, 或5
            fixed_score = trait_score['score']
            if fixed_score not in [1, 3, 5]:
                # 将评分映射到最近的1-3-5值
                if fixed_score < 2:
                    fixed_score = 1
                elif fixed_score < 4:
                    fixed_score = 3
                else:
                    fixed_score = 5
            md_content += "  - " + trait + ": " + str(fixed_score) + " (" + trait_score['evidence'] + ")\n"
    
    with open('batchAnalysizeTools/fixed_full_assessment_report.md', 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    run_fixed_full_assessment()