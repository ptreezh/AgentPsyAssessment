#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试问题报告识别模式
Debug problem report identification patterns
"""

import re
import json
from pathlib import Path

def test_problem_patterns(file_path):
    """测试文件匹配哪个问题模式"""

    # 问题模式列表（从cloud_fallback_batch_processor.py复制）
    problem_patterns = [
        # 英文问题模式
        r'please provide me with the prompt',
        r'please provide me with a prompt',
        r'please provide me with a prompt so I can assist you',
        r'as an ai language model',
        r'i don\'t have personal information',
        r'i cannot answer',
        r'i\'m not able to',
        r'i am not able to',
        r'i\'m not sure what',
        r'i cannot provide',
        r'i don\'t have access to',
        r'i don\'t have enough information',
        r'i don\'t have enough context',
        r'i don\'t understand the question',
        r'i don\'t know what',
        r'i\'m not sure what you mean',
        r'i\'m not sure i understand',
        r'as an ai assistant',
        r'as a language model',
        r'i am an ai',
        r'i\'m an ai',
        r'i\'m not human',
        r'i don\'t have personal experiences',
        r'i cannot answer from personal experience',
        r'i don\'t have access to real-time information',
        r'i don\'t have access to current information',
        r'i don\'t have access to external information',
        r'i cannot browse the internet',
        r'i don\'t have access to the internet',
        r'i don\'t have access to external data',
        r'i don\'t have access to external sources',
        r'i don\'t have access to external resources',
        r'i don\'t have access to any external information',
        r'i don\'t have access to any external data',
        r'i don\'t have access to any external sources',
        r'i don\'t have access to any external resources',

        # 中文问题模式
        r'请提供给我提示词',
        r'请提供给我提示',
        r'请提供提示词',
        r'作为一个人工智能语言模型',
        r'作为一个人工智能助手',
        r'我没有个人信息',
        r'我无法回答',
        r'我不能回答',
        r'我不能提供',
        r'我没有访问权限',
        r'我没有足够的信息',
        r'我没有足够的上下文',
        r'我不理解这个问题',
        r'我不知道什么',
        r'我不确定你的意思',
        r'我不确定我理解',
        r'我是一个人工智能',
        r'我不是人类',
        r'我没有个人经历',
        r'我无法从个人经历回答',
        r'我没有实时信息访问权限',
        r'我没有当前信息访问权限',
        r'我没有外部信息访问权限',
        r'我无法浏览互联网',
        r'我没有互联网访问权限',
        r'我没有外部数据访问权限',
        r'我没有外部来源访问权限',
        r'我没有外部资源访问权限',

        # 拒绝回答模式
        r'i cannot answer questions',
        r'i cannot provide information',
        r'i cannot provide details',
        r'i cannot provide specific information',
        r'i cannot provide personal information',
        r'i cannot provide medical advice',
        r'i cannot provide legal advice',
        r'i cannot provide financial advice',
        r'我无法回答问题',
        r'我无法提供信息',
        r'我无法提供详细信息',
        r'我无法提供具体信息',
        r'我无法提供个人信息',
        r'我无法提供医疗建议',
        r'我无法提供法律建议',
        r'我无法提供金融建议',
        r'我无法提供专业建议',

        # 系统消息模式
        r'system message',
        r'system prompt',
        r'role: system',
        r'"role": "system"',
        r'\\[system\\]',
        r'\\[system prompt\\]',
        r'系统消息',
        r'系统提示',
        r'角色: 系统',
        r'"角色": "系统"',

        # 无效回答模式
        r'the question is incomplete',
        r'the question is unclear',
        r'the question is ambiguous',
        r'这个问题不完整',
        r'这个问题不清楚',
        r'这个问题模糊',
        r'answer the question',
        r'回答这个问题',
        r'please answer',
        r'请回答',

        # 错误消息模式
        r'an error occurred',
        r'something went wrong',
        r'there was an error',
        r'发生错误',
        r'出现了问题',
        r'发生了错误',
        r'处理失败',
        r'evaluation failed',
        r'评估失败'
    ]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        print(f"📁 测试文件: {file_path.name}")
        print(f"📄 文件大小: {len(content)} 字符")
        print()

        matched_patterns = []

        # 检查每个模式
        for pattern in problem_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                matched_patterns.append(pattern)

        if matched_patterns:
            print(f"❌ 匹配到 {len(matched_patterns)} 个问题模式:")
            for i, pattern in enumerate(matched_patterns[:10]):  # 只显示前10个
                print(f"   {i+1}. {pattern}")
            if len(matched_patterns) > 10:
                print(f"   ... 还有 {len(matched_patterns) - 10} 个模式")
        else:
            print("✅ 没有匹配到问题模式")

        # 检查回答数量
        answer_count = content.count('"answer":')
        question_count = content.count('"question_id"')

        print()
        print(f"📊 统计信息:")
        print(f"   问题数量: {question_count}")
        print(f"   回答数量: {answer_count}")

        if question_count == 50:  # 50题文件
            if answer_count < 45:  # 允许最多缺失5个答案
                print(f"   ❌ 回答数量不足: {answer_count}/50")
            else:
                print(f"   ✅ 回答数量充足: {answer_count}/50")
        elif question_count == 240:  # 240题文件
            if answer_count < 220:  # 允许最多缺失20个答案
                print(f"   ❌ 回答数量不足: {answer_count}/240")
            else:
                print(f"   ✅ 回答数量充足: {answer_count}/240")
        else:
            print(f"   ℹ️  其他格式文件: {answer_count} 个回答")

        # 显示文件开头的一些内容用于调试
        print()
        print("📝 文件开头内容:")
        lines = content.split('\n')
        for i, line in enumerate(lines[:15]):
            print(f"   {i+1:2d}: {line[:80]}...")

        return len(matched_patterns) > 0

    except Exception as e:
        print(f"❌ 文件读取错误: {e}")
        return True

def main():
    """主函数"""
    # 测试文件
    test_files = [
        "results/readonly-original/asses_deepseek_r1_70b_agent_big_five_50_complete2_a1_e0_t0_0_09271.json",
        "results/readonly-original/asses_Yinr_Smegmma_9b_agent_big_five_50_complete2_a1_e0_t0_0_09081.json"
    ]

    print("🔍 调试问题报告识别模式")
    print("=" * 80)

    for file_path in test_files:
        path = Path(file_path)
        if path.exists():
            test_problem_patterns(path)
        else:
            print(f"❌ 文件不存在: {file_path}")

        print()
        print("=" * 80)
        print()

if __name__ == "__main__":
    main()