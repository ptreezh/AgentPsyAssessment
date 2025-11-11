#!/usr/bin/env python3
"""
真实微信公众号发文 MCP 服务器
支持连接真实微信公众号 API 进行自动发布
需要配置真实的微信公众号开发者权限
"""

import asyncio
import json
import sys
import os
import re
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime

class RealWeChatPublisherMCPServer:
    def __init__(self):
        self.name = "real-wechat-publisher"
        self.version = "2.0.0"
        self.config = self.load_config()
        self.access_token = None
        self.token_expires = 0

    def load_config(self):
        """加载配置文件"""
        config_file = Path("wechat_config/config.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 返回模拟配置
            return {
                "wechat": {
                    "appid": "your_appid_here",
                    "appsecret": "your_appsecret_here",
                    "enabled": False
                },
                "publish": {
                    "auto_publish": False,
                    "draft_mode": True
                }
            }

    def get_access_token(self):
        """获取或刷新 Access Token"""
        if not self.config["wechat"]["enabled"]:
            return None

        current_time = time.time()
        if self.access_token and current_time < self.token_expires:
            return self.access_token

        try:
            url = "https://api.weixin.qq.com/cgi-bin/token"
            params = {
                "grant_type": "client_credential",
                "appid": self.config["wechat"]["appid"],
                "secret": self.config["wechat"]["appsecret"]
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "access_token" in data:
                self.access_token = data["access_token"]
                self.token_expires = current_time + data["expires_in"] - 300  # 提前5分钟刷新
                return self.access_token
            else:
                return {"error": f"获取 Access Token 失败: {data}"}

        except Exception as e:
            return {"error": f"获取 Access Token 异常: {str(e)}"}

    def upload_media(self, file_path, media_type="image"):
        """上传媒体文件到微信服务器"""
        if not self.config["wechat"]["enabled"]:
            return {"error": "微信发布功能未启用"}

        access_token = self.get_access_token()
        if not access_token or "error" in str(access_token):
            return {"error": "无法获取有效的 Access Token"}

        try:
            url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={media_type}"

            with open(file_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files, timeout=30)

            return response.json()

        except Exception as e:
            return {"error": f"上传媒体文件失败: {str(e)}"}

    def create_draft(self, title, content, author="", digest="", cover_media_id=""):
        """创建图文消息草稿"""
        if not self.config["wechat"]["enabled"]:
            return {"error": "微信发布功能未启用"}

        access_token = self.get_access_token()
        if not access_token or "error" in str(access_token):
            return {"error": "无法获取有效的 Access Token"}

        try:
            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

            articles = [{
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "content_source_url": "",
                "thumb_media_id": cover_media_id,
                "show_cover_pic": 1 if cover_media_id else 0,
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }]

            data = {"articles": articles}
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=30)

            return response.json()

        except Exception as e:
            return {"error": f"创建草稿失败: {str(e)}"}

    def publish_article(self, media_id):
        """发布图文消息"""
        if not self.config["wechat"]["enabled"] or not self.config["publish"]["auto_publish"]:
            return {"error": "自动发布功能未启用"}

        access_token = self.get_access_token()
        if not access_token or "error" in str(access_token):
            return {"error": "无法获取有效的 Access Token"}

        try:
            url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"

            data = {"media_id": media_id}
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=30)

            return response.json()

        except Exception as e:
            return {"error": f"发布文章失败: {str(e)}"}

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
        timestamp = str(int(time.time()))[-6:]
        return f"{content_hash}{timestamp}"

    async def run_real_wechat_publisher(self, markdown_content="", title="", author="", tags=None, cover_image="", preview=True, auto_publish=False):
        """运行真实微信公众号发文工具"""
        try:
            if not markdown_content:
                return {"error": "缺少 Markdown 内容"}

            # 检查是否启用了微信发布功能
            if not self.config["wechat"]["enabled"]:
                # 返回模拟结果
                html_content = self.markdown_to_wechat_html(markdown_content)
                article_info = {
                    "title": title or self.extract_title_from_markdown(markdown_content),
                    "author": author or "AI Assistant",
                    "content": html_content,
                    "tags": tags or [],
                    "word_count": len(markdown_content),
                    "reading_time": self.calculate_reading_time(markdown_content),
                    "publish_time": datetime.now().isoformat(),
                    "article_id": self.generate_article_id(markdown_content),
                    "preview": preview,
                    "mode": "simulation",
                    "message": "模拟模式：未配置真实微信公众号 API"
                }

                if preview:
                    return {
                        "status": "preview",
                        "article": article_info,
                        "message": "文章预览生成成功（模拟模式）"
                    }
                else:
                    return {
                        "status": "published",
                        "article": article_info,
                        "message": "文章发布成功（模拟模式）",
                        "publish_url": f"https://mp.weixin.qq.com/s?src=11×tamp={int(datetime.now().timestamp())}"
                    }

            # 真实发布流程
            html_content = self.markdown_to_wechat_html(markdown_content)

            # 处理封面图片
            cover_media_id = ""
            if cover_image and Path(cover_image).exists():
                upload_result = self.upload_media(cover_image)
                if "media_id" in upload_result:
                    cover_media_id = upload_result["media_id"]
                elif "error" in upload_result:
                    return {"error": f"封面图片上传失败: {upload_result['error']}"}

            # 创建草稿
            draft_result = self.create_draft(
                title=title or self.extract_title_from_markdown(markdown_content),
                content=html_content,
                author=author,
                cover_media_id=cover_media_id
            )

            if "error" in draft_result:
                return {"error": f"创建草稿失败: {draft_result['error']}"}

            media_id = draft_result.get("media_id")

            article_info = {
                "title": title or self.extract_title_from_markdown(markdown_content),
                "author": author or "AI Assistant",
                "content": html_content,
                "tags": tags or [],
                "word_count": len(markdown_content),
                "reading_time": self.calculate_reading_time(markdown_content),
                "publish_time": datetime.now().isoformat(),
                "article_id": self.generate_article_id(markdown_content),
                "preview": preview,
                "mode": "real",
                "media_id": media_id,
                "cover_media_id": cover_media_id
            }

            if preview:
                return {
                    "status": "preview",
                    "article": article_info,
                    "message": "文章草稿创建成功",
                    "draft_url": f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token={self.access_token}&lang=zh_CN"
                }

            # 自动发布
            if auto_publish and self.config["publish"]["auto_publish"]:
                publish_result = self.publish_article(media_id)
                if "error" in publish_result:
                    return {"error": f"发布失败: {publish_result['error']}"}

                return {
                    "status": "published",
                    "article": article_info,
                    "message": "文章发布成功",
                    "publish_id": publish_result.get("publish_id"),
                    "publish_url": f"https://mp.weixin.qq.com/s?src=11×tamp={int(datetime.now().timestamp())}"
                }
            else:
                return {
                    "status": "drafted",
                    "article": article_info,
                    "message": "文章草稿创建成功，请在微信公众号后台手动发布",
                    "draft_url": f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token={self.access_token}&lang=zh_CN"
                }

        except Exception as e:
            return {"error": f"发布过程异常: {str(e)}"}

    def check_wechat_config(self):
        """检查微信配置状态"""
        return {
            "enabled": self.config["wechat"]["enabled"],
            "appid_configured": bool(self.config["wechat"]["appid"] and self.config["wechat"]["appid"] != "your_appid_here"),
            "appsecret_configured": bool(self.config["wechat"]["appsecret"] and self.config["wechat"]["appsecret"] != "your_appsecret_here"),
            "auto_publish_enabled": self.config["publish"]["auto_publish"],
            "draft_mode": self.config["publish"]["draft_mode"],
            "access_token_valid": bool(self.access_token and time.time() < self.token_expires)
        }

    def list_tools(self):
        """列出可用工具"""
        return {
            "tools": [
                {
                    "name": "run_real_wechat_publisher",
                    "description": "真实微信公众号发文工具 - 支持连接真实微信公众号 API",
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
                            "cover_image": {
                                "type": "string",
                                "description": "封面图片路径（可选）"
                            },
                            "preview": {
                                "type": "boolean",
                                "description": "是否为预览模式",
                                "default": true
                            },
                            "auto_publish": {
                                "type": "boolean",
                                "description": "是否自动发布（需要开启自动发布权限）",
                                "default": false
                            }
                        },
                        "required": ["markdown_content"]
                    }
                },
                {
                    "name": "check_wechat_config",
                    "description": "检查微信公众号配置状态",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }

    async def call_tool(self, name, arguments):
        """调用指定的工具"""
        if name == "run_real_wechat_publisher":
            return await self.run_real_wechat_publisher(
                markdown_content=arguments.get("markdown_content", ""),
                title=arguments.get("title", ""),
                author=arguments.get("author", ""),
                tags=arguments.get("tags", []),
                cover_image=arguments.get("cover_image", ""),
                preview=arguments.get("preview", True),
                auto_publish=arguments.get("auto_publish", False)
            )

        elif name == "check_wechat_config":
            return self.check_wechat_config()

        else:
            return {"error": f"未知工具: {name}"}

async def main():
    """MCP 服务器主循环"""
    server = RealWeChatPublisherMCPServer()

    print(f"真实微信公众号发文 MCP 服务器启动 - v{server.version}", file=sys.stderr)

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