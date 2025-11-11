#!/usr/bin/env python3
"""
适配Vercel Serverless Functions的微信公众号处理接口
部署方式：将整个vercel目录推送到Vercel平台
"""

import json
import hashlib
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

# 微信公众号配置
WECHAT_TOKEN = os.environ.get("WECHAT_TOKEN", "your_custom_token")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理微信服务器验证请求"""
        try:
            # 获取查询参数
            path_parts = self.path.split('?')
            if len(path_parts) < 2:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Bad Request")
                return

            query_string = path_parts[1]
            params = parse_qs(query_string)

            signature = params.get('signature', [''])[0]
            timestamp = params.get('timestamp', [''])[0]
            nonce = params.get('nonce', [''])[0]
            echostr = params.get('echostr', [''])[0]

            print(f"收到验证请求: signature={signature}, timestamp={timestamp}, nonce={nonce}")

            # 验证服务器
            if self.verify_signature(signature, timestamp, nonce):
                print("验证成功，返回echostr")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(echostr.encode('utf-8'))
            else:
                print("验证失败")
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"验证失败")

        except Exception as e:
            print(f"验证过程出错: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"服务器错误")

    def do_POST(self):
        """处理微信消息推送"""
        try:
            # 获取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            print(f"收到微信消息: {post_data.decode('utf-8')}")

            # 解析XML消息
            xml_data = self.parse_xml(post_data.decode('utf-8'))

            if xml_data:
                # 处理不同类型的消息
                msg_type = xml_data.get('MsgType', '')

                if msg_type == 'text':
                    response = self.handle_text_message(xml_data)
                elif msg_type == 'event':
                    response = self.handle_event_message(xml_data)
                else:
                    response = "success"  # 其他消息类型返回success

                print(f"响应消息: {response}")

                if response != "success":
                    self.send_response(200)
                    self.send_header('Content-type', 'application/xml')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"success")
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"success")

        except Exception as e:
            print(f"处理消息出错: {e}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"success")

    def verify_signature(self, signature, timestamp, nonce):
        """验证微信服务器签名"""
        try:
            # 将token、timestamp、nonce按字典序排序
            tmp_list = [WECHAT_TOKEN, timestamp, nonce]
            tmp_list.sort()
            tmp_str = ''.join(tmp_list)

            # 对排序后的字符串进行SHA1加密
            tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()

            # 比较加密结果与signature
            return tmp_str == signature

        except Exception as e:
            print(f"签名验证出错: {e}")
            return False

    def parse_xml(self, xml_data):
        """解析XML消息"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_data)

            result = {}
            for child in root:
                result[child.tag] = child.text

            return result

        except Exception as e:
            print(f"XML解析出错: {e}")
            return {}

    def handle_text_message(self, xml_data):
        """处理文本消息"""
        try:
            # 获取消息内容
            user_openid = xml_data.get('FromUserName', '')
            my_openid = xml_data.get('ToUserName', '')
            content = xml_data.get('Content', '')
            create_time = xml_data.get('CreateTime', '')

            print(f"收到文本消息: {content} from {user_openid}")

            # 构建回复消息
            reply_content = self.get_auto_reply(content)

            # 创建回复XML
            reply_xml = f"""<xml>
                <ToUserName><![CDATA[{user_openid}]]></ToUserName>
                <FromUserName><![CDATA[{my_openid}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{reply_content}]]></Content>
            </xml>"""

            return reply_xml

        except Exception as e:
            print(f"处理文本消息出错: {e}")
            return "success"

    def handle_event_message(self, xml_data):
        """处理事件消息"""
        try:
            event = xml_data.get('Event', '')
            user_openid = xml_data.get('FromUserName', '')

            print(f"收到事件消息: {event} from {user_openid}")

            if event == 'subscribe':
                # 用户关注事件
                reply_content = "感谢关注AgentPsy心理评估平台！\n\n我们可以为您提供专业的心理评估服务。\n\n回复关键词了解详情：\n- 评估：开始心理评估\n- 报告：查看评估报告\n- 帮助：获取帮助信息"

                return self.create_text_reply(xml_data, reply_content)

            return "success"

        except Exception as e:
            print(f"处理事件消息出错: {e}")
            return "success"

    def create_text_reply(self, xml_data, content):
        """创建文本回复消息"""
        try:
            user_openid = xml_data.get('FromUserName', '')
            my_openid = xml_data.get('ToUserName', '')
            create_time = xml_data.get('CreateTime', '')

            reply_xml = f"""<xml>
                <ToUserName><![CDATA[{user_openid}]]></ToUserName>
                <FromUserName><![CDATA[{my_openid}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{content}]]></Content>
            </xml>"""

            return reply_xml

        except Exception as e:
            print(f"创建回复消息出错: {e}")
            return "success"

    def get_auto_reply(self, user_message):
        """获取自动回复内容"""
        user_message = user_message.lower().strip()

        # 简单的关键词回复
        if '评估' in user_message or 'test' in user_message:
            return "请访问我们的网站进行专业心理评估：https://agentpsy.com"
        elif '报告' in user_message or 'report' in user_message:
            return "您可以在我们的个人中心查看评估报告。"
        elif '帮助' in user_message or 'help' in user_message:
            return "您可以回复以下关键词：\n- 评估：开始心理评估\n- 报告：查看评估报告\n- 联系：获取联系方式"
        elif '联系' in user_message or 'contact' in user_message:
            return "客服邮箱：support@agentpsy.com\n客服微信：AgentPsy"
        else:
            return "感谢您的消息！回复【帮助】获取更多信息。"