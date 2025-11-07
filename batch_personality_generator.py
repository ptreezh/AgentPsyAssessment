#!/usr/bin/env python3
"""
16种人格批量问卷生成和评估系统
使用Claude Code为每个人格类型生成独立的问卷回答，然后评估分析
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any

# 16种MBTI人格类型定义
PERSONALITY_TYPES = {
    "INTJ": {
        "name": "建筑师型",
        "traits": "内向(I)、直觉(N)、思考(T)、判断(J)",
        "description": "战略思维、分析能力、独立思考、效率至上、系统化思考",
        "prompt_prefix": "你是INTJ人格类型（建筑师型）：内向(I)、直觉(N)、思考(T)、判断(J)。你具有强烈的战略思维能力、分析能力、独立思考、效率至上、善于系统化思考。"
    },
    "ENTJ": {
        "name": "指挥官型",
        "traits": "外向(E)、直觉(N)、思考(T)、判断(J)",
        "description": "天生领导力、战略思维、果断决策、目标导向、效率至上",
        "prompt_prefix": "你是ENTJ人格类型（指挥官型）：外向(E)、直觉(N)、思考(T)、判断(J)。你具有天生的领导能力、战略思维、果断决策、目标导向、效率至上、善于组织和规划。"
    },
    "INTP": {
        "name": "逻辑学家型",
        "traits": "内向(I)、直觉(N)、思考(T)、感知(P)",
        "description": "逻辑分析、理论思维、创新能力、求知欲强、善于思考",
        "prompt_prefix": "你是INTP人格类型（逻辑学家型）：内向(I)、直觉(N)、思考(T)、感知(P)。你具有强大的逻辑分析能力、理论思维、创新能力、强烈的求知欲、善于深度思考。"
    },
    "ENTP": {
        "name": "辩论家型",
        "traits": "外向(E)、直觉(N)、思考(T)、感知(P)",
        "description": "善于辩论、创新思维、适应性强、思维敏捷、喜欢挑战",
        "prompt_prefix": "你是ENTP人格类型（辩论家型）：外向(E)、直觉(N)、思考(T)、感知(P)。你善于辩论、创新思维、适应性强、思维敏捷、喜欢挑战常规。"
    },
    "ISTJ": {
        "name": "物流师型",
        "traits": "内向(I)、感觉(S)、思考(T)、判断(J)",
        "description": "注重细节、责任感强、传统价值观、组织能力、执行力",
        "prompt_prefix": "你是ISTJ人格类型（物流师型）：内向(I)、感觉(S)、思考(T)、判断(J)。你注重细节、责任感强、坚持传统价值观、组织能力强、执行力出色。"
    },
    "ESTJ": {
        "name": "总经理型",
        "traits": "外向(E)、感觉(S)、思考(T)、判断(J)",
        "description": "管理能力、组织能力、责任感、效率导向、传统价值观",
        "prompt_prefix": "你是ESTJ人格类型（总经理型）：外向(E)、感觉(S)、思考(T)、判断(J)。你具有出色的管理能力、组织能力、强烈的责任感、效率导向、坚持传统价值观。"
    },
    "ISFJ": {
        "name": "守护者型",
        "traits": "内向(I)、感觉(S)、情感(F)、判断(J)",
        "description": "关怀他人、责任感强、注重细节、忠诚可靠、传统价值",
        "prompt_prefix": "你是ISFJ人格类型（守护者型）：内向(I)、感觉(S)、情感(F)、判断(J)。你关怀他人、责任感强、注重细节、忠诚可靠、坚持传统价值。"
    },
    "ESFJ": {
        "name": "执政官型",
        "traits": "外向(E)、感觉(S)、情感(F)、判断(J)",
        "description": "社交能力、关怀他人、组织能力、责任感、和谐导向",
        "prompt_prefix": "你是ESFJ人格类型（执政官型）：外向(E)、感觉(S)、情感(F)、判断(J)。你具有出色的社交能力、关怀他人、组织能力强、责任感强、注重和谐。"
    },
    "ISTP": {
        "name": "鉴赏家型",
        "traits": "内向(I)、感觉(S)、思考(T)、感知(P)",
        "description": "实用主义、动手能力、逻辑分析、适应性强、独立自主",
        "prompt_prefix": "你是ISTP人格类型（鉴赏家型）：内向(I)、感觉(S)、思考(T)、感知(P)。你注重实用主义、动手能力强、逻辑分析清晰、适应性强、独立自主。"
    },
    "ESTP": {
        "name": "企业家型",
        "traits": "外向(E)、感觉(S)、思考(T)、感知(P)",
        "description": "行动导向、冒险精神、适应性强、社交能力、实用主义",
        "prompt_prefix": "你是ESTP人格类型（企业家型）：外向(E)、感觉(S)、思考(T)、感知(P)。你行动导向、具有冒险精神、适应性强、社交能力出色、注重实用主义。"
    },
    "ISFP": {
        "name": "探险家型",
        "traits": "内向(I)、感觉(S)、情感(F)、感知(P)",
        "description": "艺术天赋、敏感细腻、价值观驱动、适应性强、个人主义",
        "prompt_prefix": "你是ISFP人格类型（探险家型）：内向(I)、感觉(S)、情感(F)、感知(P)。你具有艺术天赋、敏感细腻、价值观驱动、适应性强、注重个人表达。"
    },
    "ESFP": {
        "name": "娱乐家型",
        "traits": "外向(E)、感觉(S)、情感(F)、感知(P)",
        "description": "社交活跃、乐观开朗、表演天赋、关怀他人、享受当下",
        "prompt_prefix": "你是ESFP人格类型（娱乐家型）：外向(E)、感觉(S)、情感(F)、感知(P)。你社交活跃、乐观开朗、具有表演天赋、关怀他人、享受当下。"
    },
    "INFJ": {
        "name": "提倡者型",
        "traits": "内向(I)、直觉(N)、情感(F)、判断(J)",
        "description": "理想主义、深度思考、洞察力强、价值观驱动、关怀他人",
        "prompt_prefix": "你是INFJ人格类型（提倡者型）：内向(I)、直觉(N)、情感(F)、判断(J)。你具有理想主义、深度思考能力、洞察力强、价值观驱动、真诚关怀他人。"
    },
    "INFP": {
        "name": "调停者型",
        "traits": "内向(I)、直觉(N)、情感(F)、感知(P)",
        "description": "理想主义、价值观驱动、创造力强、同理心强、适应性强",
        "prompt_prefix": "你是INFP人格类型（调停者型）：内向(I)、直觉(N)、情感(F)、感知(P)。你具有理想主义、价值观驱动、创造力强、同理心强、适应性强。"
    },
    "ENFJ": {
        "name": "主人公型",
        "traits": "外向(E)、直觉(N)、情感(F)、判断(J)",
        "description": "领导能力、同理心强、理想主义、社交能力、激励他人",
        "prompt_prefix": "你是ENFJ人格类型（主人公型）：外向(E)、直觉(N)、情感(F)、判断(J)。你具有出色的领导能力、同理心强、理想主义、社交能力出色、善于激励他人。"
    },
    "ENFP": {
        "name": "竞选者型",
        "traits": "外向(E)、直觉(N)、情感(F)、感知(P)",
        "description": "热情洋溢、创造力强、社交能力、理想主义、适应性强",
        "prompt_prefix": "你是ENFP人格类型（竞选者型）：外向(E)、直觉(N)、情感(F)、感知(P)。你热情洋溢、创造力强、社交能力出色、理想主义、适应性强。"
    }
}

class PersonalityQuestionnaireGenerator:
    """16种人格问卷生成和评估系统"""

    def __init__(self, questionnaire_file: str, output_dir: str = "personality_results"):
        self.questionnaire_file = questionnaire_file
        self.output_dir = output_dir
        self.html_dir = os.path.join(output_dir, "html")

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.html_dir, exist_ok=True)

        # 检查问卷文件是否存在
        if not os.path.exists(questionnaire_file):
            raise FileNotFoundError(f"问卷文件不存在: {questionnaire_file}")

    def generate_personality_responses(self, personality_type: str) -> str:
        """为指定人格类型生成问卷回答"""
        if personality_type not in PERSONALITY_TYPES:
            raise ValueError(f"不支持的人格类型: {personality_type}")

        personality_info = PERSONALITY_TYPES[personality_type]
        output_file = os.path.join(self.output_dir, f"{personality_type.lower()}_citizenship_responses.json")

        # 检查是否已经存在回答文件
        if os.path.exists(output_file):
            print(f"✅ {personality_type} 回答文件已存在，跳过生成")
            return output_file

        print(f"🧠 正在生成 {personality_type} ({personality_info['name']}) 问卷回答...")

        # 构建系统提示
        system_prompt = f"""{personality_info['prompt_prefix']}
请以{personality_type}人格特征回答以下中国国籍知识测试问卷，每个回答要体现{personality_type}的特质：{personality_info['description']}。

请按照以下格式回答，输出JSON格式：
{{
  "response_metadata": {{
    "persona": "{personality_type} ({personality_info['name']})",
    "traits": "{personality_info['traits']}",
    "response_style": "体现{personality_info['description']}",
    "timestamp": "{datetime.now().isoformat()}"
  }},
  "test_responses": [
    {{
      "question_id": "题目ID",
      "question": "题目内容",
      "dimension": "维度",
      "response": "你的回答，体现{personality_type}人格特征",
      "{personality_type.lower()}_reasoning": "解释你为什么这样回答，体现{personality_type}的思维特点",
      "keywords_matched": ["关键词1", "关键词2"]
    }}
  ]
}}"""

        try:
            # 读取问卷文件内容
            with open(self.questionnaire_file, 'r', encoding='utf-8') as f:
                questionnaire_content = f.read()

            # 构建完整的问题请求
            full_prompt = f"""请基于上述{personality_type}人格特征，回答以下问卷：

{questionnaire_content}

请严格按照指定的JSON格式回答，确保每个回答都体现{personality_type}人格的典型特征和思维模式。"""

            # 使用Claude Code生成回答
            cmd = [
                r'C:\npm_global\claude.cmd', 'code', '--print',
                '--system-prompt', system_prompt,
                '--output-format', 'json'
            ]

            result = subprocess.run(
                cmd,
                input=full_prompt,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )

            if result.returncode == 0:
                # 保存生成的回答
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                print(f"✅ {personality_type} 问卷回答生成完成: {output_file}")
                return output_file
            else:
                print(f"❌ {personality_type} 生成失败: {result.stderr}")
                return None

        except Exception as e:
            print(f"❌ 生成 {personality_type} 回答时出错: {e}")
            return None

    def generate_evaluation_report(self, personality_type: str, responses_file: str) -> str:
        """为指定人格类型生成评估HTML报告"""
        personality_info = PERSONALITY_TYPES[personality_type]
        html_file = os.path.join(self.html_dir, f"{personality_type.lower()}_citizenship_assessment.html")

        # 检查是否已经存在HTML报告
        if os.path.exists(html_file):
            print(f"✅ {personality_type} HTML报告已存在，跳过生成")
            return html_file

        print(f"📊 正在生成 {personality_type} 评估HTML报告...")

        evaluation_prompt = f"""请基于{personality_type}人格特征对以下问卷回答进行专业评估分析，并生成HTML格式的评估报告。

{personality_type}人格特征：{personality_info['traits']}
描述：{personality_info['description']}

请读取回答文件：{responses_file}

生成一个包含以下内容的专业HTML评估报告：
1. 评测概览 - 总体评分和关键指标
2. 人格特征分析 - {personality_type}特征在回答中的体现
3. 详细评分 - 各维度得分和分析
4. 问答分析 - 重点问题和回答质量
5. 优势分析 - {personality_type}的优势体现
6. 改进建议 - 针对{personality_type}的发展建议
7. 结论总结 - 综合评估和建议

HTML报告要求：
- 使用现代化的CSS样式
- 包含交互式标签页
- 响应式设计
- 包含AI人格实验室页脚链接：https://cn.agentpsy.com
- 专业的数据可视化
- 适合在html目录下保存为.html文件"""

        try:
            with open(responses_file, 'r', encoding='utf-8') as f:
                responses_content = f.read()

            full_prompt = f"""{evaluation_prompt}

问卷回答内容：
{responses_content}"""

            cmd = [
                r'C:\npm_global\claude.cmd', 'code', '--print',
                '--system-prompt', '你是专业的心理评估专家，擅长生成HTML格式的评估报告',
                '--output-format', 'text'
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

    def generate_all_personalities(self) -> Dict[str, Dict[str, str]]:
        """为所有16种人格生成回答和评估报告"""
        results = {}

        print("🚀 开始为16种人格批量生成问卷回答和评估报告...")
        print("=" * 60)

        for personality_type in PERSONALITY_TYPES.keys():
            print(f"\n📋 处理 {personality_type} ({PERSONALITY_TYPES[personality_type]['name']})")

            # 生成问卷回答
            responses_file = self.generate_personality_responses(personality_type)

            if responses_file:
                # 生成HTML评估报告
                html_file = self.generate_evaluation_report(personality_type, responses_file)

                results[personality_type] = {
                    'responses_file': responses_file,
                    'html_file': html_file,
                    'status': 'completed' if html_file else 'partial'
                }
            else:
                results[personality_type] = {
                    'responses_file': None,
                    'html_file': None,
                    'status': 'failed'
                }

        return results

    def generate_comparison_report(self, results: Dict[str, Dict[str, str]]) -> str:
        """生成16种人格对比分析报告"""
        comparison_file = os.path.join(self.html_dir, "16_personalities_comparison.html")

        print("\n📈 正在生成16种人格对比分析报告...")

        comparison_prompt = f"""请基于以下16种人格的问卷回答结果，生成一个综合对比分析HTML报告。

已完成的人格类型：
{json.dumps(results, indent=2, ensure_ascii=False)}

请生成包含以下内容的对比分析报告：
1. 总体对比概览 - 16种人格的整体表现对比
2. 各维度得分对比 - 历史、地理、政治、文化、综合分析维度
3. 人格特征对比 - 不同人格在回答中的典型特征体现
4. 优势能力对比 - 各人格类型的独特优势
5. 适合场景分析 - 各人格在不同任务中的适合度
6. 数据可视化 - 使用图表展示对比结果
7. 总结和建议 - 综合分析和应用建议

HTML要求：
- 使用现代化CSS样式
- 包含数据图表（可用CSS或JavaScript实现）
- 响应式设计
- 交互式元素
- AI人格实验室页脚链接：https://cn.agentpsy.com
- 专业的布局和设计"""

        try:
            # 收集所有已完成的回答文件内容用于对比分析
            all_responses = {}
            for personality_type, result in results.items():
                if result.get('responses_file') and os.path.exists(result['responses_file']):
                    with open(result['responses_file'], 'r', encoding='utf-8') as f:
                        all_responses[personality_type] = json.load(f)

            full_prompt = f"""{comparison_prompt}

已收集的人格回答数据：
{json.dumps(all_responses, indent=2, ensure_ascii=False)}"""

            cmd = [
                r'C:\npm_global\claude.cmd', 'code', '--print',
                '--system-prompt', '你是专业的心理对比分析专家，擅长生成综合对比分析报告',
                '--output-format', 'text'
            ]

            result = subprocess.run(
                cmd,
                input=full_prompt,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )

            if result.returncode == 0:
                with open(comparison_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                print(f"✅ 16种人格对比分析报告生成完成: {comparison_file}")
                return comparison_file
            else:
                print(f"❌ 对比分析报告生成失败: {result.stderr}")
                return None

        except Exception as e:
            print(f"❌ 生成对比分析报告时出错: {e}")
            return None

def main():
    """主函数"""
    questionnaire_file = "llm_assessment/test_files/agent-citizenship-test-expanded.json"

    try:
        generator = PersonalityQuestionnaireGenerator(questionnaire_file)

        print("🎯 16种人格问卷生成和评估系统")
        print("=" * 50)
        print(f"问卷文件: {questionnaire_file}")
        print(f"输出目录: {generator.output_dir}")
        print()

        # 生成所有人格的回答和评估
        results = generator.generate_all_personalities()

        # 生成对比分析报告
        comparison_file = generator.generate_comparison_report(results)

        print("\n" + "=" * 60)
        print("📊 批量生成完成统计")
        print("=" * 60)

        completed_count = sum(1 for r in results.values() if r['status'] == 'completed')
        partial_count = sum(1 for r in results.values() if r['status'] == 'partial')
        failed_count = sum(1 for r in results.values() if r['status'] == 'failed')

        print(f"✅ 完全完成: {completed_count} 个人格类型")
        print(f"⚠️  部分完成: {partial_count} 个人格类型")
        print(f"❌ 生成失败: {failed_count} 个人格类型")
        print(f"📄 对比报告: {comparison_file if comparison_file else '未生成'}")

        print("\n📁 输出文件:")
        for personality_type, result in results.items():
            if result['responses_file']:
                print(f"  {personality_type}: {result['responses_file']}")
            if result['html_file']:
                print(f"  {personality_type} HTML: {result['html_file']}")

        return results

    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        return None

if __name__ == "__main__":
    main()