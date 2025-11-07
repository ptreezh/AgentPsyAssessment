#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESTJ人格问卷生成脚本
专门为ESTJ人格类型生成符合其特征的问卷回答
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

class ESTJPersonalityGenerator:
    """ESTJ人格问卷生成器"""

    def __init__(self):
        self.questionnaire_file = "D:/AIDevelop/portable_psyagent/llm_assessment/test_files/agent-citizenship-test-expanded.json"
        self.output_file = "estj_citizenship_responses.json"
        self.claude_cmd = r'C:\npm_global\claude.cmd'

    def get_estj_system_prompt(self) -> str:
        """获取ESTJ人格系统提示词"""
        return """你是ESTJ（总经理型）人格类型，具有以下核心特征：

**核心认知功能：**
- **主导功能：Te（外向思维）** - 注重效率、组织和客观标准
- **辅助功能：Si（内向感觉）** - 重视传统、经验和既定规则
- **第三功能：Ne（外向直觉）** - 务实的创新和现实可能性
- **弱势功能：Fi（内向情感）** - 内在价值观但不常外露

**ESTJ行为特征：**
- 务实导向，注重实际效果和可行性
- 尊重规则和传统，相信系统化方法
- 强烈的责任感和义务感
- 天生的组织者和管理者
- 决策果断，基于事实和逻辑
- 重视社会秩序和稳定

**回答风格：**
- 回答要有条理性和结构性
- 强调规则、制度和标准的重要性
- 体现责任感和义务感
- 关注实际应用和社会效益
- 使用客观、事实性的语言
- 展现管理思维和组织能力

请根据以上ESTJ人格特征，逐一回答公民知识问卷。每个回答都要体现ESTJ的务实、负责、尊重规则的特点。"""

    def load_questionnaire(self) -> dict:
        """加载问卷文件"""
        try:
            with open(self.questionnaire_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载问卷失败: {e}")
            return {}

    def generate_estj_responses(self) -> bool:
        """生成ESTJ人格回答"""
        print("🧠 生成ESTJ人格问卷回答...")
        print("📋 问卷文件:", self.questionnaire_file)
        print("💾 输出文件:", self.output_file)

        # 加载问卷
        questionnaire = self.load_questionnaire()
        if not questionnaire:
            return False

        questions = questionnaire.get('questions', [])
        if not questions:
            print("❌ 问卷中没有找到问题")
            return False

        print(f"📊 找到 {len(questions)} 个问题")

        # 构建Claude Code命令
        prompt = f"""请以ESTJ人格特征回答以下公民知识问卷。

问卷说明：
{json.dumps(questionnaire.get('description', ''), ensure_ascii=False)}

请按以下JSON格式回答：
{{
    "personality_type": "ESTJ",
    "generation_time": "{datetime.now().isoformat()}",
    "responses": [
        {{
            "question_id": "问题ID",
            "question": "完整问题内容",
            "answer": "你的回答（体现ESTJ特征）",
            "estj_reasoning": "回答背后的ESTJ思维过程",
            "key_traits": ["相关ESTJ特质"],
            "confidence": 0.95
        }}
    ]
}}

ESTJ回答要点：
- 体现务实和责任感
- 尊重规则和制度
- 强调社会秩序和效率
- 展现组织管理思维
- 基于事实和经验判断"""

        try:
            # 使用管道方式调用Claude Code
            process = subprocess.run(
                [self.claude_cmd, 'code', '--print', '--system-prompt', self.get_estj_system_prompt()],
                input=prompt,
                text=True,
                capture_output=True,
                encoding='utf-8'
            )

            if process.returncode != 0:
                print(f"❌ Claude Code调用失败: {process.stderr}")
                return False

            # 解析返回结果
            response_text = process.stdout.strip()
            print("🤖 Claude Code响应获取成功")

            # 尝试提取JSON
            if '{' in response_text:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                json_str = response_text[start_idx:end_idx]

                try:
                    estj_response = json.loads(json_str)

                    # 保存到文件
                    with open(self.output_file, 'w', encoding='utf-8') as f:
                        json.dump(estj_response, f, ensure_ascii=False, indent=2)

                    print(f"✅ ESTJ回答已保存到: {self.output_file}")
                    return True

                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print("📄 原始响应:", response_text[:500])
                    return False
            else:
                print("❌ 响应中没有找到JSON格式")
                print("📄 原始响应:", response_text[:500])
                return False

        except Exception as e:
            print(f"❌ 生成过程失败: {e}")
            return False

    def validate_output(self) -> bool:
        """验证输出文件"""
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 基本验证
            if 'personality_type' not in data or data['personality_type'] != 'ESTJ':
                print("❌ 人格类型验证失败")
                return False

            if 'responses' not in data or not isinstance(data['responses'], list):
                print("❌ 回答格式验证失败")
                return False

            response_count = len(data['responses'])
            if response_count == 0:
                print("❌ 没有找到回答")
                return False

            print(f"✅ 验证通过: {response_count} 个ESTJ回答")
            return True

        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False

    def run(self) -> bool:
        """执行完整生成流程"""
        print("=" * 60)
        print("🏛️  ESTJ（总经理型）人格问卷生成器")
        print("=" * 60)

        # 检查必要文件
        if not Path(self.questionnaire_file).exists():
            print(f"❌ 问卷文件不存在: {self.questionnaire_file}")
            return False

        # 检查Claude Code是否可用
        try:
            subprocess.run([self.claude_cmd, '--version'], capture_output=True, check=True)
            print("✅ Claude Code工具检查通过")
        except Exception as e:
            print(f"❌ Claude Code工具不可用: {e}")
            return False

        # 生成回答
        if not self.generate_estj_responses():
            return False

        # 验证输出
        if not self.validate_output():
            return False

        print("\n🎉 ESTJ人格问卷生成完成！")
        print(f"📁 输出文件: {self.output_file}")
        print(f"📊 可用于后续HTML评估报告生成")
        return True

def main():
    """主函数"""
    generator = ESTJPersonalityGenerator()
    success = generator.run()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()