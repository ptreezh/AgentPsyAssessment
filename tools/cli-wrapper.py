#!/usr/bin/env python3
"""
本地CLI工具包装器
用于将本地CLI工具暴露为MCP工具
"""

import subprocess
import json
import sys
import os
from pathlib import Path

class CLIWrapper:
    def __init__(self):
        self.cli_tools = {
            'gemini': r"C:\npm_global\gemini.cmd",
            'qwen': r"C:\npm_global\qwen.cmd",
            'qodercli': r"C:\npm_global\qodercli.cmd",
            'copilot': r"C:\npm_global\copilot.cmd",
            'iflow': r"C:\npm_global\iflow.cmd",
            'codebuddy': r"C:\npm_global\codebuddy.cmd",
            'ollama': "ollama",  # 系统命令，不需要完整路径
            'kimi': "kimi",       # 系统命令，不需要完整路径
            'wechat-publisher': "python wechat_publisher_mcp.py"  # 自定义微信公众号发文工具
        }

    def run_command(self, tool_name, args):
        """运行指定的CLI工具"""
        if tool_name not in self.cli_tools:
            return {"error": f"Unknown tool: {tool_name}"}

        cmd_path = self.cli_tools[tool_name]

        # 系统命令和 Python 脚本不需要 PowerShell 包装
        if tool_name in ['ollama', 'kimi', 'wechat-publisher']:
            cmd = [cmd_path] + args
        else:
            # npm 安装的命令需要 PowerShell 包装
            cmd = ['powershell', '-c', f"& '{cmd_path}'"] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            return {
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}

    def run_gemini(self, prompt, model=None, temperature=None):
        """运行gemini CLI"""
        args = [prompt]
        if model:
            args.extend(['-m', model])
        if temperature:
            args.extend(['-t', str(temperature)])
        return self.run_command('gemini', args)

    def run_qwen(self, prompt, model=None, temperature=None):
        """运行qwen CLI"""
        args = [prompt]
        if model:
            args.extend(['--model', model])
        if temperature:
            args.extend(['--temperature', str(temperature)])
        return self.run_command('qwen', args)

    def run_qodercli(self, prompt):
        """运行qodercli CLI"""
        return self.run_command('qodercli', [prompt])

    def run_copilot(self, prompt):
        """运行copilot CLI"""
        return self.run_command('copilot', [prompt])

    def run_iflow(self, prompt, model=None):
        """运行iflow CLI"""
        args = [prompt]
        if model:
            args.extend(['--model', model])
        return self.run_command('iflow', args)

    def run_codebuddy(self, prompt):
        """运行codebuddy CLI"""
        return self.run_command('codebuddy', [prompt])

    def run_ollama(self, prompt, model=None):
        """运行ollama CLI"""
        args = ['run']
        if model:
            args.append(model)
        else:
            args.append('llama3.2')  # 默认模型

        # 对于 ollama，我们需要将 prompt 通过 stdin 传递
        import tempfile
        import os

        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as f:
                f.write(prompt)
                temp_file = f.name

            # 使用 cat 管道传递给 ollama
            cmd = ['cat', temp_file, '|', 'ollama', 'run'] + args[-1:]  # 只取最后一个参数作为模型名

            result = subprocess.run(
                f"cat {temp_file} | ollama run {args[-1:]}",
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            # 清理临时文件
            os.unlink(temp_file)

            return {
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            # 清理临时文件（如果存在）
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file)
            except:
                pass
            return {"error": str(e)}

    def run_kimi(self, prompt, model=None):
        """运行kimi CLI"""
        args = [prompt]
        if model:
            args.extend(['--model', model])
        return self.run_command('kimi', args)

    def run_wechat_publisher(self, markdown_content="", title="", author="", tags=None, preview=False):
        """运行微信公众号发文工具"""
        import json

        # 构建参数
        params = {
            "markdown_content": markdown_content,
            "title": title,
            "author": author,
            "tags": tags or [],
            "preview": preview
        }

        # 通过标准输入传递 JSON 参数
        import tempfile
        import os

        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.json') as f:
                json.dump(params, f, ensure_ascii=False)
                temp_file = f.name

            # 调用微信发文工具
            cmd = ['python', 'wechat_publisher_mcp.py']

            # 创建测试请求
            test_request = {
                "method": "tools/call",
                "params": {
                    "name": "run_wechat_publisher",
                    "arguments": params
                },
                "id": 1
            }

            result = subprocess.run(
                cmd,
                input=json.dumps(test_request, ensure_ascii=False),
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            # 清理临时文件
            os.unlink(temp_file)

            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout.strip())
                    if "result" in response:
                        content = response["result"]["content"][0]["text"]
                        return json.loads(content)
                    else:
                        return {"error": "无效响应格式"}
                except json.JSONDecodeError:
                    return {"output": result.stdout, "error": result.stderr, "returncode": result.returncode}
            else:
                return {"error": result.stderr, "returncode": result.returncode}

        except Exception as e:
            # 清理临时文件（如果存在）
            try:
                if 'temp_file' in locals():
                    os.unlink(temp_file)
            except:
                pass
            return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli-wrapper.py <tool_name> <args...>")
        sys.exit(1)

    wrapper = CLIWrapper()
    tool_name = sys.argv[1]
    args = sys.argv[2:]

    result = wrapper.run_command(tool_name, args)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()