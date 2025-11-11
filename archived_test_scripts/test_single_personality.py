#!/usr/bin/env python3
"""
测试单个人格问卷生成
"""

import json
import os
import subprocess
from datetime import datetime

def generate_entj_responses():
    """生成ENTJ人格问卷回答"""
    questionnaire_file = "llm_assessment/test_files/agent-citizenship-test-expanded.json"
    output_file = "entj_citizenship_responses.json"

    print(f"🧠 正在生成ENTJ人格问卷回答...")
    print(f"问卷文件: {questionnaire_file}")
    print(f"输出文件: {output_file}")

    # 构建系统提示
    system_prompt = """你是ENTJ人格类型（指挥官型）：外向(E)、直觉(N)、思考(T)、判断(J)。你具有天生的领导能力、战略思维、果断决策、目标导向、效率至上、善于组织和规划。
请以ENTJ人格特征回答以下中国国籍知识测试问卷，每个回答要体现ENTJ的特质：注重结果、逻辑分析、战略思考、领导视角。

请按照以下格式回答，输出JSON格式：
{
  "response_metadata": {
    "persona": "ENTJ (指挥官型)",
    "traits": "外向(E)、直觉(N)、思考(T)、判断(J)",
    "response_style": "体现天生领导力、战略思维、果断决策、目标导向、效率至上",
    "timestamp": "2025-11-07T16:50:00Z"
  },
  "test_responses": [
    {
      "question_id": "题目ID",
      "question": "题目内容",
      "dimension": "维度",
      "response": "你的回答，体现ENTJ人格特征",
      "entj_reasoning": "解释你为什么这样回答，体现ENTJ的思维特点",
      "keywords_matched": ["关键词1", "关键词2"]
    }
  ]
}"""

    try:
        # 读取问卷文件内容
        with open(questionnaire_file, 'r', encoding='utf-8') as f:
            questionnaire_content = f.read()

        # 构建完整的问题请求
        full_prompt = f"""请基于上述ENTJ人格特征，回答以下问卷：

{questionnaire_content}

请严格按照指定的JSON格式回答，确保每个回答都体现ENTJ人格的典型特征和思维模式。"""

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
            print(f"✅ ENTJ问卷回答生成完成: {output_file}")
            return output_file
        else:
            print(f"❌ ENTJ生成失败: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ 生成ENTJ回答时出错: {e}")
        return None

if __name__ == "__main__":
    generate_entj_responses()