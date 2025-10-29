#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama云模型JSON解析诊断工具
基于TDD方法，逐步诊断和修复JSON解析问题
"""

import sys
import os
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class OllamaJSONDiagnostic:
    def __init__(self):
        self.models = [
            "deepseek-v3.1:671b-cloud",
            "gpt-oss:120b-cloud",
            "qwen3-coder:480b-cloud"
        ]

    def test_basic_ollama_response(self, model_name):
        """测试基础Ollama响应格式"""
        print(f"\n🔍 测试模型: {model_name}")

        # 使用最简单的提示测试响应
        simple_prompt = "请返回一个包含数字1到5的JSON格式评分，格式：{\"score\": 3}"

        cmd = ['ollama', 'run', model_name, simple_prompt, '--format', 'json']

        try:
            print(f"  发送简单提示: {simple_prompt}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            print(f"  返回码: {result.returncode}")
            print(f"  标准输出长度: {len(result.stdout)} 字符")
            print(f"  标准错误长度: {len(result.stderr)} 字符")

            if result.stdout:
                print(f"  原始响应前500字符:")
                print(f"    {repr(result.stdout[:500])}")

                # 尝试不同的解析方法
                print(f"  🔧 尝试解析方法:")

                # 方法1: 直接解析
                try:
                    if result.stdout.strip().startswith('{') and result.stdout.strip().endswith('}'):
                        parsed = json.loads(result.stdout.strip())
                        print(f"    ✅ 直接解析成功: {parsed}")
                        return {"success": True, "method": "direct", "result": parsed}
                    else:
                        print(f"    ❌ 直接解析失败: 不是标准JSON格式")
                except Exception as e:
                    print(f"    ❌ 直接解析失败: {e}")

                # 方法2: 提取JSON对象
                try:
                    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                    matches = re.findall(json_pattern, result.stdout, re.DOTALL)
                    print(f"    找到 {len(matches)} 个可能的JSON对象")

                    for i, match in enumerate(matches):
                        try:
                            parsed = json.loads(match)
                            print(f"    ✅ 正则提取#{i+1}成功: {parsed}")
                            return {"success": True, "method": "regex", "result": parsed}
                        except Exception as e:
                            print(f"    ❌ 正则提取#{i+1}失败: {e}")
                except Exception as e:
                    print(f"    ❌ 正则提取失败: {e}")

                # 方法3: 寻找JSON代码块
                try:
                    codeblock_pattern = r'```(?:json)?\s*\n?(\{.*?\})\s*```'
                    matches = re.findall(codeblock_pattern, result.stdout, re.DOTALL)
                    print(f"    找到 {len(matches)} 个JSON代码块")

                    for i, match in enumerate(matches):
                        try:
                            parsed = json.loads(match.strip())
                            print(f"    ✅ 代码块提取#{i+1}成功: {parsed}")
                            return {"success": True, "method": "codeblock", "result": parsed}
                        except Exception as e:
                            print(f"    ❌ 代码块提取#{i+1}失败: {e}")
                except Exception as e:
                    print(f"    ❌ 代码块提取失败: {e}")

                # 方法4: 智能修复常见JSON问题
                try:
                    fixed_json = self.fix_common_json_issues(result.stdout)
                    parsed = json.loads(fixed_json)
                    print(f"    ✅ 智能修复成功: {parsed}")
                    return {"success": True, "method": "smart_fix", "result": parsed}
                except Exception as e:
                    print(f"    ❌ 智能修复失败: {e}")

            if result.stderr:
                print(f"  错误输出前200字符:")
                print(f"    {repr(result.stderr[:200])}")

            return {"success": False, "error": "所有解析方法都失败"}

        except subprocess.TimeoutExpired:
            print(f"  ❌ 请求超时")
            return {"success": False, "error": "timeout"}
        except Exception as e:
            print(f"  ❌ 其他错误: {e}")
            return {"success": False, "error": str(e)}

    def fix_common_json_issues(self, json_str):
        """智能修复常见JSON格式问题"""
        # 移除BOM和其他不可见字符
        json_str = json_str.strip().lstrip('\ufeff')

        # 尝试找到JSON对象
        if '{' in json_str and '}' in json_str:
            start = json_str.find('{')
            # 找到最后一个匹配的右括号
            brace_count = 0
            end = start
            for i, char in enumerate(json_str[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break

            json_str = json_str[start:end]

        # 修复常见的引号问题
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)  # 键加引号
        json_str = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)', r': "\1"', json_str)  # 值加引号

        # 移除注释
        json_str = re.sub(r'//.*?\n', '', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)

        # 移除尾部逗号
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        return json_str

    def test_big5_prompt_format(self, model_name):
        """测试Big5分析提示格式"""
        print(f"\n🧪 测试Big5提示格式: {model_name}")

        # 创建一个简化的Big5测试提示
        big5_prompt = """你是心理评估分析师。分析以下回答并返回JSON格式评分。

问题1：我喜欢尝试新事物
回答：是的，我经常尝试新的餐厅和活动

问题2：我做事很有条理
回答：我总是制定详细计划

请返回JSON格式：
{
  "success": true,
  "scores": {
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5
  }
}"""

        cmd = ['ollama', 'run', model_name, '--format', 'json', '--prompt', big5_prompt]

        try:
            print(f"  发送Big5测试提示...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            print(f"  响应长度: {len(result.stdout)} 字符")

            if result.stdout:
                print(f"  完整响应:")
                print(f"    {repr(result.stdout)}")

                # 使用改进的解析器
                parsed_result = self.parse_ollama_response(result.stdout)
                return parsed_result

            if result.stderr:
                print(f"  错误信息: {result.stderr[:200]}")

            return {"success": False, "error": "无响应内容"}

        except Exception as e:
            print(f"  ❌ Big5测试失败: {e}")
            return {"success": False, "error": str(e)}

    def parse_ollama_response(self, response_text):
        """改进的Ollama响应解析器"""
        response_text = response_text.strip()

        if not response_text:
            return {"success": False, "error": "响应为空"}

        # 解析策略按优先级排序
        strategies = [
            ("直接解析", lambda: self._direct_parse(response_text)),
            ("代码块提取", lambda: self._extract_codeblock(response_text)),
            ("正则提取", lambda: self._regex_extract(response_text)),
            ("智能修复", lambda: self._smart_parse(response_text)),
            ("模糊匹配", lambda: self._fuzzy_extract(response_text))
        ]

        for strategy_name, strategy_func in strategies:
            try:
                result = strategy_func()
                if result and isinstance(result, dict):
                    print(f"    ✅ {strategy_name}成功: {result}")
                    return {"success": True, "method": strategy_name, "result": result}
            except Exception as e:
                print(f"    ❌ {strategy_name}失败: {e}")
                continue

        return {"success": False, "error": "所有解析策略都失败", "raw_response": response_text[:500]}

    def _direct_parse(self, text):
        """直接解析JSON"""
        if text.startswith('{') and text.endswith('}'):
            return json.loads(text)
        return None

    def _extract_codeblock(self, text):
        """提取代码块中的JSON"""
        patterns = [
            r'```json\s*\n?(\{.*?\})\s*```',
            r'```\s*\n?(\{.*?\})\s*```',
            r'`\{.*?\}`'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except:
                    continue
        return None

    def _regex_extract(self, text):
        """正则表达式提取JSON"""
        # 更精确的JSON匹配模式
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # 标准JSON对象
            r'\{(?:[^{}"]|"[^"]*")*\}',          # 包含字符串的JSON
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        return None

    def _smart_parse(self, text):
        """智能修复并解析"""
        fixed = self.fix_common_json_issues(text)
        return json.loads(fixed)

    def _fuzzy_extract(self, text):
        """模糊提取评分信息"""
        scores = {}

        # 提取评分
        score_patterns = [
            r'openness_to_experience["\s]*:["\s]*([1-5])',
            r'conscientiousness["\s]*:["\s]*([1-5])',
            r'extraversion["\s]*:["\s]*([1-5])',
            r'agreeableness["\s]*:["\s]*([1-5])',
            r'neuroticism["\s]*:["\s]*([1-5])'
        ]

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        for i, pattern in enumerate(score_patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scores[traits[i]] = int(match.group(1))

        if scores:
            return {
                "success": True,
                "scores": scores,
                "extraction_method": "fuzzy"
            }

        return None

    def run_comprehensive_diagnostic(self):
        """运行综合诊断"""
        print("🔬 Ollama云模型JSON解析综合诊断")
        print("=" * 60)

        diagnostic_results = {}

        for model in self.models:
            print(f"\n{'='*20} {model} {'='*20}")

            model_results = {
                "basic_test": self.test_basic_ollama_response(model),
                "big5_test": self.test_big5_prompt_format(model)
            }

            diagnostic_results[model] = model_results

            # 分析结果
            print(f"\n📊 {model} 诊断总结:")
            basic_success = model_results["basic_test"].get("success", False)
            big5_success = model_results["big5_test"].get("success", False)

            print(f"  基础响应测试: {'✅ 通过' if basic_success else '❌ 失败'}")
            print(f"  Big5格式测试: {'✅ 通过' if big5_success else '❌ 失败'}")

            if basic_success and big5_success:
                print(f"  🎉 {model} 完全兼容！")
            elif basic_success or big5_success:
                print(f"  ⚠️ {model} 部分兼容，需要优化")
            else:
                print(f"  ❌ {model} 需要重大修复")

        # 保存诊断报告
        report_file = f"ollama_json_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "diagnostic_time": datetime.now().isoformat(),
                "models_tested": self.models,
                "results": diagnostic_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 诊断报告已保存: {report_file}")

        # 提供修复建议
        print(f"\n🔧 修复建议:")
        successful_models = [m for m in self.models if diagnostic_results[m]["big5_test"].get("success", False)]

        if successful_models:
            print(f"  ✅ 可直接使用: {', '.join(successful_models)}")
            print(f"  💡 建议优先使用这些模型进行批量分析")

        failed_models = [m for m in self.models if m not in successful_models]
        if failed_models:
            print(f"  ⚠️ 需要修复: {', '.join(failed_models)}")
            print(f"  🔧 建议实现模型特定的解析逻辑")

def main():
    """主函数"""
    diagnostic = OllamaJSONDiagnostic()
    diagnostic.run_comprehensive_diagnostic()

if __name__ == "__main__":
    main()