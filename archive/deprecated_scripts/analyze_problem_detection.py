#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析问题报告检测逻辑
Analyze problem report detection logic
"""

import json
import re
from pathlib import Path

def analyze_assessment_file(file_path):
    """分析测评报告文件，找出被误识别的原因"""

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

        print(f"📁 分析文件: {file_path.name}")
        print(f"📄 文件大小: {len(content)} 字符")
        print()

        # 统计基本信息
        answer_count = content.count('"answer":')
        question_count = content.count('"question_id"')

        print(f"📊 基本统计:")
        print(f"   问题数量: {question_count}")
        print(f"   回答数量: {answer_count}")

        # 检查问题模式匹配
        matched_patterns = []
        matched_examples = []

        for pattern in problem_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                matched_patterns.append(pattern)
                # 收集前几个匹配的示例
                for match in matches[:3]:
                    start_pos = max(0, match.start() - 50)
                    end_pos = min(len(content), match.end() + 50)
                    context = content[start_pos:end_pos]
                    matched_examples.append((pattern, context))

        if matched_patterns:
            print(f"❌ 匹配到 {len(matched_patterns)} 个问题模式:")
            for i, (pattern, context) in enumerate(matched_examples[:5]):  # 只显示前5个
                print(f"   {i+1}. 模式: {pattern}")
                print(f"      上下文: ...{context}...")
                print()
        else:
            print("✅ 没有匹配到问题模式")

        # 检查文件结构
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                if 'assessment_metadata' in data and 'assessment_results' in data:
                    print("✅ 文件结构正确：包含assessment_metadata和assessment_results")

                    # 检查具体数据
                    metadata = data.get('assessment_metadata', {})
                    results = data.get('assessment_results', [])

                    print(f"   📋 模型ID: {metadata.get('model_id', 'N/A')}")
                    print(f"   📋 测试名称: {metadata.get('test_name', 'N/A')}")
                    print(f"   📋 评估结果数量: {len(results)}")

                    # 检查第一个结果的结构
                    if results:
                        first_result = results[0]
                        if 'question_id' in first_result and 'answer' in first_result:
                            print("✅ 评估结果结构正确：包含question_id和answer")
                        else:
                            print("❌ 评估结果结构异常")
                            print(f"   实际键: {list(first_result.keys())}")
                else:
                    print("❌ 文件结构异常：缺少必要的字段")
                    print(f"   实际键: {list(data.keys())}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")

        # 最终判断
        print()
        print("🔍 诊断结果:")
        is_problem = len(matched_patterns) > 0 or answer_count < 45
        if is_problem:
            if matched_patterns:
                print("   ❌ 被识别为问题报告（匹配到问题模式）")
            if answer_count < 45:
                print(f"   ❌ 被识别为问题报告（回答数量不足：{answer_count}/50）")
        else:
            print("   ✅ 应该是正常报告")

        return is_problem, matched_patterns[:3]  # 返回是否为问题报告和前3个匹配的模式

    except Exception as e:
        print(f"❌ 文件分析错误: {e}")
        return True, [f"文件读取错误: {str(e)}"]

def main():
    """主函数"""
    # 检查readonly-original目录中的文件
    readonly_dir = Path("results/readonly-original")

    if not readonly_dir.exists():
        print(f"❌ 目录不存在: {readonly_dir}")
        return

    json_files = list(readonly_dir.glob("*.json"))

    if not json_files:
        print("❌ 没有找到JSON文件")
        return

    print("🔍 分析问题报告检测逻辑")
    print("=" * 80)
    print(f"📁 找到 {len(json_files)} 个JSON文件")
    print()

    # 分析前5个文件
    problem_files = 0
    normal_files = 0

    for i, file_path in enumerate(json_files[:5]):
        is_problem, reasons = analyze_assessment_file(file_path)

        if is_problem:
            problem_files += 1
        else:
            normal_files += 1

        print("=" * 80)
        print()

    print("📊 分析总结:")
    print(f"   ✅ 正常报告: {normal_files}")
    print(f"   ❌ 问题报告: {problem_files}")
    print(f"   📈 问题率: {problem_files/(normal_files+problem_files)*100:.1f}%")

    if problem_files > 0:
        print()
        print("🚨 发现问题！")
        print("💡 建议：检查问题模式匹配是否过于严格")
        print("💡 特别是 'role: system' 和 '\"role\": \"system\"' 模式可能误匹配正常JSON结构")

if __name__ == "__main__":
    main()