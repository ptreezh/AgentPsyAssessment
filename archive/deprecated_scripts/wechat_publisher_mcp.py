#!/usr/bin/env python3
"""
微信公众号发文 MCP 服务器
支持 Markdown 转 HTML 格式，模拟微信公众号发布功能
"""

import asyncio
import json
import sys
import os
import re
import base64
from pathlib import Path
from datetime import datetime
import hashlib

class WeChatPublisherMCPServer:
    def __init__(self):
        self.name = "wechat-publisher"
        self.version = "1.0.0"

    async def run_wechat_publisher(self, markdown_content="", title="", author="", tags=None, preview=False):
        """运行微信公众号发文工具"""
        try:
            if not markdown_content:
                return {"error": "缺少 Markdown 内容"}

            # 转换 Markdown 为 HTML
            html_content = self.markdown_to_wechat_html(markdown_content)

            # 生成文章信息
            article_info = {
                "title": title or self.extract_title_from_markdown(markdown_content),
                "author": author or "AI Assistant",
                "content": html_content,
                "tags": tags or [],
                "word_count": len(markdown_content),
                "reading_time": self.calculate_reading_time(markdown_content),
                "publish_time": datetime.now().isoformat(),
                "article_id": self.generate_article_id(markdown_content),
                "preview": preview
            }

            # 如果是预览模式，返回预览信息
            if preview:
                return {
                    "status": "preview",
                    "article": article_info,
                    "message": "文章预览生成成功"
                }

            # 模拟发布流程
            return {
                "status": "published",
                "article": article_info,
                "message": "文章发布成功（模拟）",
                "publish_url": f"https://mp.weixin.qq.com/s?src=11×tamp={int(datetime.now().timestamp())}"
            }

        except Exception as e:
            return {"error": f"发布失败: {str(e)}"}

    def markdown_to_wechat_html(self, markdown_text):
        """将 Markdown 转换为微信公众号兼容的 HTML"""
        # 基础 Markdown 转换
        html = markdown_text

        # 标题转换
        html = re.sub(r'^# (.+)$', r'<h1 class="rich_media_title">\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2 class="rich_media_title">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

        # 粗体和斜体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # 链接
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # 图片
        html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1" style="width: 100%; height: auto;">', html)

        # 代码块
        html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

        # 行内代码
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # 段落处理
        paragraphs = html.split('\n\n')
        html_paragraphs = []

        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                # 判断是否是列表项
                if para.startswith(('- ', '* ', '1. ')):
                    # 简单列表处理
                    list_items = re.split(r'^[-*]\s|^\d+\.\s', para, flags=re.MULTILINE)
                    list_items = [item.strip() for item in list_items if item.strip()]
                    if para.startswith(('- ', '* ')):
                        html_para = '<ul class="list-paddingleft-2">' + ''.join([f'<li>{item}</li>' for item in list_items]) + '</ul>'
                    else:
                        html_para = '<ol class="list-paddingleft-2">' + ''.join([f'<li>{item}</li>' for item in list_items]) + '</ol>'
                else:
                    html_para = f'<p class="rich_media_content">{para}</p>'
                html_paragraphs.append(html_para)
            elif para:
                html_paragraphs.append(para)

        return '\n'.join(html_paragraphs)

    def extract_title_from_markdown(self, markdown_text):
        """从 Markdown 中提取标题"""
        lines = markdown_text.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "未命名文章"

    def calculate_reading_time(self, text, words_per_minute=300):
        """计算阅读时间（分钟）"""
        word_count = len(text)
        return max(1, round(word_count / words_per_minute))

    def generate_article_id(self, content):
        """生成文章 ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = str(int(datetime.now().timestamp()))[-6:]
        return f"{content_hash}{timestamp}"

    def list_tools(self):
        """列出可用工具"""
        return {
            "tools": [
                {
                    "name": "run_wechat_publisher",
                    "description": "微信公众号发文工具 - 支持Markdown转HTML并发布",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "markdown_content": {
                                "type": "string",
                                "description": "Markdown格式的文章内容"
                            },
                            "title": {
                                "type": "string",
                                "description": "文章标题（可选）"
                            },
                            "author": {
                                "type": "string",
                                "description": "作者名称（可选）"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "文章标签（可选）"
                            },
                            "preview": {
                                "type": "boolean",
                                "description": "是否为预览模式",
                                "default": false
                            }
                        },
                        "required": ["markdown_content"]
                    }
                },
                {
                    "name": "format_wechat_content",
                    "description": "格式化内容为微信公众号HTML格式",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "需要格式化的内容"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["markdown", "plain"],
                                "default": "markdown",
                                "description": "内容格式类型"
                            }
                        },
                        "required": ["content"]
                    }
                }
            ]
        }

    async def call_tool(self, name, arguments):
        """调用指定的工具"""
        if name == "run_wechat_publisher":
            return await self.run_wechat_publisher(
                markdown_content=arguments.get("markdown_content", ""),
                title=arguments.get("title", ""),
                author=arguments.get("author", ""),
                tags=arguments.get("tags", []),
                preview=arguments.get("preview", False)
            )

        elif name == "format_wechat_content":
            content = arguments.get("content", "")
            format_type = arguments.get("format", "markdown")

            if format_type == "markdown":
                html_content = self.markdown_to_wechat_html(content)
            else:
                # 纯文本处理
                paragraphs = content.split('\n\n')
                html_paragraphs = [f'<p class="rich_media_content">{para.strip()}</p>' for para in paragraphs if para.strip()]
                html_content = '\n'.join(html_paragraphs)

            return {
                "original_content": content,
                "formatted_html": html_content,
                "format": format_type,
                "length": len(content)
            }

        else:
            return {"error": f"未知工具: {name}"}

async def main():
    """MCP 服务器主循环"""
    server = WeChatPublisherMCPServer()

    print(f"微信公众号发文 MCP 服务器启动 - v{server.version}", file=sys.stderr)

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
                    "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]}
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