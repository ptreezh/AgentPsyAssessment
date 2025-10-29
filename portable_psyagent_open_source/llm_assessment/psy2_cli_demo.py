#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random

def demo_psy2_cli():
    """演示Psy2 CLI工具"""
    print("=" * 60)
    print("           Psy2心理评估CLI工具 - 演示")
    print("=" * 60)
    print()
    print("欢迎使用Psy2心理评估CLI工具演示！")
    print()
    
    # 1. 创建会话
    print("1. 创建新的心理评估会话")
    print("   命令: python human_assessment/cli/main.py create-session")
    print("   输出: Session created with UUID: SESSION-ABC123DEF456")
    print()
    
    # 2. 查看可用测试
    print("2. 查看可用的心理测试")
    print("   命令: python human_assessment/cli/main.py list-assessments")
    print("   输出:")
    print("     Available Assessments:")
    print("       big5: IPIP-FFM-50 大五人格测试")
    print("       dass: DASS-42 抑郁-焦虑-压力量表")
    print()
    
    # 3. 开始测试
    print("3. 开始Big Five人格测试")
    print("   命令: python human_assessment/cli/main.py start-assessment big5")
    print("   输出:")
    print("     Question 1: 我是团队活动的核心人物。")
    print("     Options: 1, 2, 3, 4, 5")
    print()
    
    # 4. 回答问题
    print("4. 回答问题")
    print("   命令: python human_assessment/cli/main.py answer 4")
    print("   输出:")
    print("     Question 2: 我喜欢与人交往。")
    print("     Options: 1, 2, 3, 4, 5")
    print()
    
    print("   命令: python human_assessment/cli/main.py answer 3")
    print("   输出:")
    print("     Trial period ended. Please upgrade for full report.")
    print()
    
    # 5. 生成免费报告
    print("5. 生成免费报告")
    print("   命令: python human_assessment/cli/main.py get-free-report")
    print("   输出:")
    print("     ## Big Five Personality Test - Free Report")
    print("     ### 您的人格特质得分 (满分5分)")
    print("     - Extraversion: 3.2")
    print("     - Agreeableness: 3.8")
    print("     - Conscientiousness: 4.1")
    print("     - Neuroticism: 2.5")
    print("     - Openness to Experience: 3.6")
    print()
    
    # 6. 升级会话
    print("6. 升级会话")
    print("   命令: python human_assessment/cli/main.py upgrade-session")
    print("   输出:")
    print("     Session upgraded to paid status successfully.")
    print()
    
    # 7. 生成完整报告
    print("7. 生成完整报告")
    print("   命令: python human_assessment/cli/main.py get-full-report")
    print("   输出:")
    print("     ## Big Five Personality Test - 完整报告")
    print("     ### 您的人格特质得分 (满分5分)")
    print("     - Extraversion: 3.2")
    print("     - Agreeableness: 3.8")
    print("     - Conscientiousness: 4.1")
    print("     - Neuroticism: 2.5")
    print("     - Openness to Experience: 3.6")
    print("     ...")
    print()
    
    # 8. 生成专业分析报告
    print("8. 生成专业分析报告")
    print("   命令: python human_assessment/cli/main.py get-analyzed-report")
    print("   输出:")
    print("     ## Big Five Personality Test - 专业分析报告")
    print("     ### 综合评估")
    print("     基于深度心理分析模型，您的Big Five人格特质评估如下：")
    print("     ...")
    print()
    
    # 9. 生成MBTI映射报告
    print("9. 生成MBTI映射报告")
    print("   命令: python human_assessment/cli/main.py get-mbti-report")
    print("   输出:")
    print("     ## Big Five Personality Test - MBTI映射分析报告")
    print("     ### MBTI类型映射")
    print("     根据您的Big Five人格特质得分，您的映射MBTI类型为：ENFJ-A")
    print("     ...")
    print()
    
    print("=" * 60)
    print("                   演示结束")
    print("=" * 60)
    print()
    print("要实际使用CLI工具，请在命令行中运行以下命令：")
    print("  cd D:\\AIDevelop\\psy2")
    print("  python human_assessment/cli/main.py --help")

if __name__ == '__main__':
    demo_psy2_cli()