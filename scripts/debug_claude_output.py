#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code输出调试脚本
用于调试Claude Code的输出格式问题
"""

import subprocess
import json
import sys
from pathlib import Path

def test_simple_prompt():
    """测试简单提示词"""
    prompt = """请生成一个简单的JSON响应，格式如下：
{
  "test": "success",
  "message": "这是一个测试响应"
}

严格按照上述JSON格式回答，不要添加任何解释。"""

    claude_cmd = r'C:\npm_global\claude.cmd'

    try:
        print("🔄 测试Claude Code输出...")
        process = subprocess.run(
            [claude_cmd, 'code', '--print'],
            input=prompt,
            text=True,
            capture_output=True,
            encoding='utf-8',
            timeout=30
        )

        print(f"📊 返回码: {process.returncode}")
        print(f"📤 标准输出长度: {len(process.stdout)}")
        print(f"📥 标准错误长度: {len(process.stderr)}")

        if process.stderr:
            print(f"❌ 错误输出:\n{process.stderr}")

        print(f"📄 原始输出:\n{repr(process.stdout[:500])}")

        # 尝试查找JSON
        if '{' in process.stdout:
            json_start = process.stdout.find('{')
            json_end = process.stdout.rfind('}') + 1
            json_content = process.stdout[json_start:json_end]

            print(f"\n🔍 提取的JSON:\n{json_content}")

            try:
                data = json.loads(json_content)
                print(f"✅ JSON解析成功: {data}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                return False
        else:
            print("❌ 输出中未找到JSON结构")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_estj_prompt():
    """测试ESTJ人格提示词"""
    simple_prompt = """你是ESTJ人格类型，请回答这个问题："你的组织管理风格是什么？"

请以以下JSON格式回答：
{
  "personality": "ESTJ",
  "response": "你的回答",
  "reasoning": "推理过程"
}

严格按照JSON格式，不要添加任何解释。"""

    claude_cmd = r'C:\npm_global\claude.cmd'

    try:
        print("\n🔄 测试ESTJ人格输出...")
        process = subprocess.run(
            [claude_cmd, 'code', '--print'],
            input=simple_prompt,
            text=True,
            capture_output=True,
            encoding='utf-8',
            timeout=30
        )

        print(f"📄 ESTJ原始输出:\n{repr(process.stdout)}")

        # 查找JSON
        if '{' in process.stdout:
            json_start = process.stdout.find('{')
            json_end = process.stdout.rfind('}') + 1
            json_content = process.stdout[json_start:json_end]

            print(f"\n🔍 提取的ESTJ JSON:\n{json_content}")

            try:
                data = json.loads(json_content)
                print(f"✅ ESTJ JSON解析成功: {data}")
                return data
            except json.JSONDecodeError as e:
                print(f"❌ ESTJ JSON解析失败: {e}")
                return {}
        else:
            print("❌ ESTJ输出中未找到JSON结构")
            return {}

    except Exception as e:
        print(f"❌ ESTJ测试失败: {e}")
        return {}

def main():
    """主函数"""
    print("🧠 Portable PsyAgent - Claude Code输出调试")
    print("=" * 50)

    # 测试简单提示词
    simple_success = test_simple_prompt()

    # 测试ESTJ提示词
    estj_result = test_estj_prompt()

    print(f"\n🎉 调试完成!")
    print(f"- 简单JSON测试: {'✅' if simple_success else '❌'}")
    print(f"- ESTJ人格测试: {'✅' if estj_result else '❌'}")

if __name__ == "__main__":
    main()