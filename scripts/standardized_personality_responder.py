#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准化人格问卷回答器
严格按照Claude Code技能规范生成人格问卷回答，确保输出格式一致性
"""

import json
import subprocess
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class StandardizedPersonalityResponder:
    """标准化人格问卷回答器"""

    def __init__(self):
        self.questionnaire_file = "llm_assessment/test_files/agent-citizenship-test-expanded.json"
        self.claude_cmd = r'C:\npm_global\claude.cmd'
        self.output_dir = Path("html/exam")

        # MBTI人格类型的标准化配置
        self.mbti_config = {
            "INTJ": {
                "name": "建筑师",
                "description": "内向、直觉、思考、判断 - 战略性、系统性、逻辑严密的思考者",
                "cognitive_functions": "主导功能Te（外向思维）、辅助功能Ni（内向直觉）",
                "key_traits": ["系统性思维", "战略分析", "独立思考", "目标导向", "逻辑推理"]
            },
            "ESTJ": {
                "name": "总经理",
                "description": "外向、感觉、思考、判断 - 务实、组织性强、负责任的管理者",
                "cognitive_functions": "主导功能Te（外向思维）、辅助功能Si（内向感觉）",
                "key_traits": ["务实导向", "组织能力", "责任感强", "规则尊重", "决策果断"]
            }
            # 可以扩展其他MBTI类型
        }

    def get_personality_system_prompt(self, personality_type: str) -> str:
        """获取人格类型系统提示词"""
        config = self.mbti_config.get(personality_type, {})

        return f"""你是{personality_type}人格类型（{config.get('name', '未知类型')}），具有以下核心特征：

{config.get('description', '')}

**认知功能：**
{config.get('cognitive_functions', '')}

**核心特质：**
{', '.join(config.get('key_traits', []))}

**回答要求：**
1. 严格按照{personality_type}人格特征回答每个问题
2. 体现该人格类型的思维模式和价值取向
3. 回答要连贯、一致，展现人格的完整性
4. 每个回答都要有{personality_type}特征的合理推理过程

**输出格式要求：**
必须严格遵循以下JSON格式，不允许任何额外的文字说明：

```json
{{
  "response_info": {{
    "persona": "{personality_type}",
    "context": "standard",
    "timestamp": "{datetime.now().isoformat()}",
    "personality_name": "{config.get('name', '')}",
    "total_questions": 42
  }},
  "responses": [
    {{
      "question_id": "唯一标识符",
      "question": "完整问题内容",
      "response": "具体回答内容",
      "reasoning": "基于{personality_type}特征的推理过程",
      "key_traits_demonstrated": ["体现的核心特质"],
      "confidence": 0.95
    }}
  ]
}}
```

请严格按照上述格式生成JSON回答，不要添加任何解释性文字。"""

    def load_questionnaire(self) -> Dict:
        """加载问卷文件"""
        try:
            with open(self.questionnaire_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载问卷失败: {e}")
            return {}

    def generate_personality_response(self, personality_type: str) -> Dict:
        """生成人格问卷回答"""
        print(f"🧠 生成 {personality_type} 人格问卷回答...")

        # 验证人格类型
        if personality_type not in self.mbti_config:
            print(f"❌ 不支持的人格类型: {personality_type}")
            return {}

        # 加载问卷
        questionnaire = self.load_questionnaire()
        if not questionnaire:
            print("❌ 问卷加载失败")
            return {}

        # 构建生成提示
        prompt = f"""请以{personality_type}人格特征回答以下公民知识问卷。

问卷信息：
标题：{questionnaire.get('title', '公民知识测试')}
说明：{questionnaire.get('description', '')}
题目数量：{len(questionnaire.get('questions', []))}

{self.get_personality_system_prompt(personality_type)}

问卷问题：
{json.dumps(questionnaire.get('questions', []), ensure_ascii=False, indent=2)}"""

        try:
            # 调用Claude Code
            process = subprocess.run(
                [self.claude_cmd, 'code', '--print'],
                input=prompt,
                text=True,
                capture_output=True,
                encoding='utf-8',
                timeout=300  # 5分钟超时
            )

            if process.returncode != 0:
                print(f"❌ Claude Code调用失败: {process.stderr}")
                return {}

            # 提取并解析JSON响应
            response_text = process.stdout.strip()
            print(f"📄 Claude输出长度: {len(response_text)}")
            print(f"📄 原始输出前200字符: {repr(response_text[:200])}")

            return self._parse_and_validate_response(response_text, personality_type)

        except subprocess.TimeoutExpired:
            print(f"❌ {personality_type} 生成超时")
            return {}
        except Exception as e:
            print(f"❌ {personality_type} 生成失败: {e}")
            return {}

    def _parse_and_validate_response(self, response_text: str, personality_type: str) -> Dict:
        """解析和验证响应"""
        try:
            # 处理可能存在的markdown代码块标记
            # 移除开头的 ```json
            if response_text.strip().startswith('```json'):
                lines = response_text.split('\n')
                # 找到代码块结束位置
                end_marker = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '```':
                        end_marker = i
                        break

                if end_marker > 0:
                    response_text = '\n'.join(lines[1:end_marker])
                    print(f"✅ 移除了markdown代码块标记")

            # 查找JSON开始和结束位置
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                print(f"❌ {personality_type}: 未找到有效JSON结构")
                return {}

            json_content = response_text[json_start:json_end]
            response_data = json.loads(json_content)

            # 验证必要字段
            if 'response_info' not in response_data or 'responses' not in response_data:
                print(f"❌ {personality_type}: 缺少必要字段")
                return {}

            # 验证response_info
            response_info = response_data['response_info']
            if response_info.get('persona') != personality_type:
                print(f"❌ {personality_type}: 人格类型不匹配")
                return {}

            # 验证responses
            responses = response_data['responses']
            if not isinstance(responses, list) or len(responses) == 0:
                print(f"❌ {personality_type}: responses格式错误")
                return {}

            # 验证每个response的必要字段
            required_fields = ['question_id', 'question', 'response', 'reasoning']
            for i, resp in enumerate(responses):
                for field in required_fields:
                    if field not in resp:
                        print(f"❌ {personality_type}: response[{i}]缺少字段{field}")
                        return {}

            print(f"✅ {personality_type}: JSON验证通过，{len(responses)}个回答")
            return response_data

        except json.JSONDecodeError as e:
            print(f"❌ {personality_type}: JSON解析失败 - {e}")
            return {}
        except Exception as e:
            print(f"❌ {personality_type}: 验证失败 - {e}")
            return {}

    def save_response(self, personality_type: str, response_data: Dict) -> bool:
        """保存回答数据"""
        if not response_data:
            return False

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        filename = f"{personality_type.lower()}_citizenship_responses.json"
        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)

            print(f"✅ {personality_type} 回答已保存: {filepath}")
            return True

        except Exception as e:
            print(f"❌ 保存 {personality_type} 回答失败: {e}")
            return False

    def generate_response_format_summary(self, personality_type: str, response_data: Dict) -> str:
        """生成回答格式摘要"""
        if not response_data:
            return f"❌ {personality_type} 生成失败"

        responses = response_data.get('responses', [])
        response_info = response_data.get('response_info', {})

        summary = f"""
# {personality_type}人格问卷回答摘要

## 基本信息
- **人格类型**: {personality_type}
- **生成时间**: {response_info.get('timestamp', '未知')}
- **上下文**: {response_info.get('context', '标准')}
- **回答数量**: {len(responses)}

## 回答统计
- **总问题数**: {response_info.get('total_questions', 0)}
- **实际回答**: {len(responses)}
- **格式正确**: ✅

## 特质体现
{personality_type}人格特征在回答中得到了充分体现，展现了：
{', '.join(self.mbti_config.get(personality_type, {}).get('key_traits', []))}

## 文件信息
- **保存位置**: html/exam/{personality_type.lower()}_citizenship_responses.json
- **JSON格式**: 标准化技能格式
- **数据质量**: 已验证
"""
        return summary

    def run(self, personality_type: str) -> bool:
        """执行完整生成流程"""
        print(f"🎯 开始生成 {personality_type} 人格问卷回答")
        print("=" * 60)

        # 检查必要文件
        if not Path(self.questionnaire_file).exists():
            print(f"❌ 问卷文件不存在: {self.questionnaire_file}")
            return False

        # 检查Claude Code
        try:
            subprocess.run([self.claude_cmd, '--version'],
                         capture_output=True, check=True, timeout=10)
            print("✅ Claude Code工具检查通过")
        except Exception as e:
            print(f"❌ Claude Code工具不可用: {e}")
            return False

        # 生成回答
        response_data = self.generate_personality_response(personality_type)
        if not response_data:
            return False

        # 保存回答
        if not self.save_response(personality_type, response_data):
            return False

        # 生成摘要
        summary = self.generate_response_format_summary(personality_type, response_data)
        print(summary)

        print(f"\n🎉 {personality_type} 人格问卷回答生成完成！")
        return True

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='标准化人格问卷回答生成器')
    parser.add_argument('personality', help='MBTI人格类型 (如: INTJ, ESTJ)')

    args = parser.parse_args()

    personality_type = args.personality.upper()

    responder = StandardizedPersonalityResponder()
    success = responder.run(personality_type)

    exit(0 if success else 1)

if __name__ == "__main__":
    main()