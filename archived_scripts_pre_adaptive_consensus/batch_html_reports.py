#!/usr/bin/env python3
"""
批量为14个人格类型生成独立的HTML评估报告
"""

import json
import os
import subprocess
from datetime import datetime

# 14个人格类型信息
PERSONALITY_INFO = {
    "INTJ": {"name": "建筑师型", "traits": "内向(I)、直觉(N)、思考(T)、判断(J)"},
    "ENTJ": {"name": "指挥官型", "traits": "外向(E)、直觉(N)、思考(T)、判断(J)"},
    "INTP": {"name": "逻辑学家型", "traits": "内向(I)、直觉(N)、思考(T)、感知(P)"},
    "ENTP": {"name": "辩论家型", "traits": "外向(E)、直觉(N)、思考(T)、感知(P)"},
    "ISTJ": {"name": "物流师型", "traits": "内向(I)、感觉(S)、思考(T)、判断(J)"},
    "ISFJ": {"name": "守护者型", "traits": "内向(I)、感觉(S)、情感(F)、判断(J)"},
    "ESFJ": {"name": "执政官型", "traits": "外向(E)、感觉(S)、情感(F)、判断(J)"},
    "ISTP": {"name": "鉴赏家型", "traits": "内向(I)、感觉(S)、思考(T)、感知(P)"},
    "ESTP": {"name": "企业家型", "traits": "外向(E)、感觉(S)、思考(T)、感知(P)"},
    "ISFP": {"name": "探险家型", "traits": "内向(I)、感觉(S)、情感(F)、感知(P)"},
    "ESFP": {"name": "娱乐家型", "traits": "外向(E)、感觉(S)、情感(F)、感知(P)"},
    "INFJ": {"name": "提倡者型", "traits": "内向(I)、直觉(N)、情感(F)、判断(J)"},
    "INFP": {"name": "调停者型", "traits": "内向(I)、直觉(N)、情感(F)、感知(P)"},
    "ENFP": {"name": "竞选者型", "traits": "外向(E)、直觉(N)、情感(F)、感知(P)"}
}

def generate_html_report(personality_type: str, personality_info: dict) -> str:
    """为指定人格类型生成HTML评估报告"""
    responses_file = f"{personality_type.lower()}_citizenship_responses.json"
    html_dir = "html"
    html_file = os.path.join(html_dir, f"{personality_type.lower()}_citizenship_assessment.html")

    print(f"📊 正在生成 {personality_type} ({personality_info['name']}) HTML评估报告...")

    # 确保html目录存在
    os.makedirs(html_dir, exist_ok=True)

    # 检查是否已经存在HTML报告
    if os.path.exists(html_file):
        print(f"✅ {personality_type} HTML报告已存在，跳过生成")
        return html_file

    # 检查回答文件是否存在
    if not os.path.exists(responses_file):
        print(f"❌ {personality_type} 回答文件不存在: {responses_file}")
        return None

    evaluation_prompt = f"""请基于{personality_type}人格特征对以下问卷回答进行专业评估分析，并生成HTML格式的评估报告。

{personality_type}人格特征：{personality_info['traits']}

请读取回答文件：{responses_file}

生成一个包含以下内容的专业HTML评估报告：
1. 评测概览 - 总体评分和关键指标
2. 人格特征分析 - {personality_type}特征在回答中的体现
3. 详细评分 - 各维度得分和分析（历史知识、地理知识、政治知识、文化知识、综合分析）
4. 问答分析 - 重点问题和回答质量，体现{personality_type}思维特点
5. 优势分析 - {personality_type}的优势体现
6. 改进建议 - 针对{personality_type}的发展建议
7. 结论总结 - 综合评估和建议

HTML报告要求：
- 使用现代化的CSS样式，包含渐变背景和动画效果
- 包含交互式标签页，使用JavaScript实现页面切换
- 响应式设计，适配移动设备
- 包含AI人格实验室页脚链接：https://cn.agentpsy.com
- 专业的数据可视化，使用CSS图表
- 适合在html目录下保存为.html文件
- 当前评估时间：{datetime.now().strftime('%Y-%m-%d')}"""

    try:
        with open(responses_file, 'r', encoding='utf-8') as f:
            responses_content = f.read()

        full_prompt = f"""{evaluation_prompt}

问卷回答内容：
{responses_content}

请生成完整的HTML文档，包含DOCTYPE声明、head、body等完整结构。"""

        cmd = [
            r'C:\npm_global\claude.cmd', 'code', '--print',
            '--system-prompt', '你是专业的心理评估专家，擅长生成HTML格式的评估报告。请直接输出完整的HTML代码，不要包含任何解释性文字。'
        ]

        result = subprocess.run(
            cmd,
            input=full_prompt,
            text=True,
            capture_output=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            # 保存HTML报告
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print(f"✅ {personality_type} HTML评估报告生成完成: {html_file}")
            return html_file
        else:
            print(f"❌ {personality_type} HTML报告生成失败: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ 生成 {personality_type} HTML报告时出错: {e}")
        return None

def main():
    """主函数 - 批量生成HTML评估报告"""
    print("🚀 开始为14个人格类型批量生成HTML评估报告...")
    print("=" * 60)

    results = {}
    success_count = 0

    for personality_type, personality_info in PERSONALITY_INFO.items():
        print(f"\n📋 处理 {personality_type} ({personality_info['name']})")

        html_file = generate_html_report(personality_type, personality_info)

        if html_file:
            results[personality_type] = {
                'status': 'completed',
                'file': html_file
            }
            success_count += 1
        else:
            results[personality_type] = {
                'status': 'failed',
                'file': None
            }

    print("\n" + "=" * 60)
    print("📊 HTML报告生成完成统计")
    print("=" * 60)
    print(f"✅ 成功生成: {success_count} 个人格类型")
    print(f"❌ 生成失败: {len(PERSONALITY_INFO) - success_count} 个人格类型")

    print("\n📁 生成的HTML文件:")
    for personality_type, result in results.items():
        if result['file']:
            print(f"  {personality_type}: {result['file']}")

    return results

if __name__ == "__main__":
    main()