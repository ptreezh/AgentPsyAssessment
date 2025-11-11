#!/usr/bin/env python3
"""
MCP Server for local CLI tools
暴露本地 CLI 工具为 MCP 技能工具
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

class MCPCLIToolsServer:
    def __init__(self):
        self.cli_tools = {
            'gemini': r"C:\npm_global\gemini.cmd",
            'qwen': r"C:\npm_global\qwen.cmd",
            'qodercli': r"C:\npm_global\qodercli.cmd",
            'copilot': r"C:\npm_global\copilot.cmd",
            'iflow': r"C:\npm_global\iflow.cmd",
            'codebuddy': r"C:\npm_global\codebuddy.cmd"
        }

    async def run_cli_tool(self, tool_name, args):
        """运行指定的 CLI 工具"""
        if tool_name not in self.cli_tools:
            return {"error": f"Unknown tool: {tool_name}"}

        cmd_path = self.cli_tools[tool_name]
        cmd = ['powershell', '-c', f"& '{cmd_path}'"] + args

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                text=True
            )

            stdout, stderr = await process.communicate()

            return {
                "output": stdout,
                "error": stderr,
                "returncode": process.returncode
            }
        except Exception as e:
            return {"error": str(e)}

    def list_tools(self):
        """列出可用的工具"""
        return {
            "tools": [
                {
                    "name": "run_gemini",
                    "description": "Run Gemini CLI tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "model": {"type": "string"},
                            "temperature": {"type": "number"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "run_qwen",
                    "description": "Run Qwen CLI tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "model": {"type": "string"},
                            "temperature": {"type": "number"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "run_qodercli",
                    "description": "Run Qoder CLI tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "run_copilot",
                    "description": "Run Copilot CLI tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "run_iflow",
                    "description": "Run iFlow CLI tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "model": {"type": "string"}
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "run_codebuddy",
                    "description": "Run CodeBuddy CLI tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"}
                        },
                        "required": ["prompt"]
                    }
                }
            ]
        }

    async def call_tool(self, name, arguments):
        """调用指定的工具"""
        if name == "run_gemini":
            prompt = arguments.get("prompt", "")
            args = [prompt]
            if arguments.get("model"):
                args.extend(["-m", arguments["model"]])
            if arguments.get("temperature"):
                args.extend(["-t", str(arguments["temperature"])])
            return await self.run_cli_tool("gemini", args)

        elif name == "run_qwen":
            prompt = arguments.get("prompt", "")
            args = [prompt]
            if arguments.get("model"):
                args.extend(["--model", arguments["model"]])
            if arguments.get("temperature"):
                args.extend(["--temperature", str(arguments["temperature"])])
            return await self.run_cli_tool("qwen", args)

        elif name == "run_qodercli":
            prompt = arguments.get("prompt", "")
            return await self.run_cli_tool("qodercli", [prompt])

        elif name == "run_copilot":
            prompt = arguments.get("prompt", "")
            return await self.run_cli_tool("copilot", [prompt])

        elif name == "run_iflow":
            prompt = arguments.get("prompt", "")
            args = [prompt]
            if arguments.get("model"):
                args.extend(["--model", arguments["model"]])
            return await self.run_cli_tool("iflow", args)

        elif name == "run_codebuddy":
            prompt = arguments.get("prompt", "")
            return await self.run_cli_tool("codebuddy", [prompt])

        else:
            return {"error": f"Unknown tool: {name}"}

async def main():
    """MCP 服务器主循环"""
    server = MCPCLIToolsServer()

    while True:
        try:
            # 读取 MCP 请求
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )

            if not line:
                break

            request = json.loads(line.strip())

            # 处理请求
            if request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": server.list_tools()
                }

            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                result = await server.call_tool(tool_name, arguments)

                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
                }

            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                }

            # 发送响应
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())