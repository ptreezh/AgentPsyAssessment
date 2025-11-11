#!/usr/bin/env python3
"""
基于成功ENTJ模板，批量生成其余14种人格的问卷回答
"""

import json
import os
import subprocess
from datetime import datetime

# 14种需要生成的人格类型（INTJ和ENFJ已存在，ENTJ刚刚生成）
REMAINING_PERSONALITIES = {
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
    "ENFP": {
        "name": "竞选者型",
        "traits": "外向(E)、直觉(N)、情感(F)、感知(P)",
        "description": "热情洋溢、创造力强、社交能力、理想主义、适应性强",
        "prompt_prefix": "你是ENFP人格类型（竞选者型）：外向(E)、直觉(N)、情感(F)、感知(P)。你热情洋溢、创造力强、社交能力出色、理想主义、适应性强。"
    }
}

def generate_personality_responses(personality_type: str, personality_info: dict) -> str:
    """为指定人格类型生成问卷回答"""
    questionnaire_file = "llm_assessment/test_files/agent-citizenship-test-expanded.json"
    output_file = f"{personality_type.lower()}_citizenship_responses.json"

    print(f"🧠 正在生成 {personality_type} ({personality_info['name']}) 问卷回答...")

    # 检查是否已经存在回答文件
    if os.path.exists(output_file):
        print(f"✅ {personality_type} 回答文件已存在，跳过生成")
        return output_file

    # 构建系统提示
    system_prompt = f"""{personality_info['prompt_prefix']}
请以{personality_type}人格特征回答以下中国国籍知识测试问卷，每个回答要体现{personality_type}的特质：{personality_info['description']}。

请严格按照以下JSON格式回答：
```json
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
}}
```"""

    try:
        # 读取问卷文件内容
        with open(questionnaire_file, 'r', encoding='utf-8') as f:
            questionnaire_content = f.read()

        # 构建完整的问题请求
        full_prompt = f"""请基于上述{personality_type}人格特征，回答以下问卷：

{questionnaire_content}

请严格按照指定的JSON格式回答，确保每个回答都体现{personality_type}人格的典型特征和思维模式。输出格式必须是有效的JSON。"""

        # 使用Claude Code生成回答
        cmd = [
            r'C:\npm_global\claude.cmd', 'code', '--print',
            '--system-prompt', system_prompt
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

def main():
    """主函数 - 批量生成剩余14种人格的回答"""
    print("🚀 开始批量生成剩余14种人格的问卷回答...")
    print("=" * 60)

    results = {}
    success_count = 0

    for personality_type, personality_info in REMAINING_PERSONALITIES.items():
        print(f"\n📋 处理 {personality_type} ({personality_info['name']})")

        output_file = generate_personality_responses(personality_type, personality_info)

        if output_file:
            results[personality_type] = {
                'status': 'completed',
                'file': output_file
            }
            success_count += 1
        else:
            results[personality_type] = {
                'status': 'failed',
                'file': None
            }

    print("\n" + "=" * 60)
    print("📊 批量生成完成统计")
    print("=" * 60)
    print(f"✅ 成功生成: {success_count} 个人格类型")
    print(f"❌ 生成失败: {len(REMAINING_PERSONALITIES) - success_count} 个人格类型")

    print("\n📁 生成的文件:")
    for personality_type, result in results.items():
        if result['file']:
            print(f"  {personality_type}: {result['file']}")

    return results

if __name__ == "__main__":
    main()