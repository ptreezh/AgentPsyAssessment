#!/usr/bin/env python3
"""
微信公众号服务器验证和消息处理脚本
放置于: https://agentpsy.com/wechat
"""

import json
import hashlib
import web
import logging
from urllib.parse import parse_qs

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 微信公众号配置
WECHAT_TOKEN = "your_custom_token"  # 替换为你在config.json中设置的token

# Web.py配置
urls = (
    '/wechat', 'WeChatHandler',
    '/wechat/', 'WeChatHandler',
)

app = web.application(urls, globals())

class WeChatHandler:
    def GET(self):
        """处理微信服务器验证请求"""
        try:
            data = web.input()

            # 获取微信服务器发送的验证参数
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr

            logger.info(f"收到验证请求: signature={signature}, timestamp={timestamp}, nonce={nonce}")

            # 验证服务器
            if self.verify_signature(signature, timestamp, nonce):
                logger.info("验证成功，返回echostr")
                return echostr
            else:
                logger.error("验证失败")
                return "验证失败", 403

        except Exception as e:
            logger.error(f"验证过程出错: {e}")
            return "服务器错误", 500

    def POST(self):
        """处理微信消息推送"""
        try:
            # 获取原始数据
            data = web.data()
            logger.info(f"收到微信消息: {data}")

            # 解析XML消息
            xml_data = self.parse_xml(data)

            if xml_data:
                # 处理不同类型的消息
                msg_type = xml_data.get('MsgType', '')

                if msg_type == 'text':
                    response = self.handle_text_message(xml_data)
                elif msg_type == 'event':
                    response = self.handle_event_message(xml_data)
                else:
                    response = "success"  # 其他消息类型返回success

                logger.info(f"响应消息: {response}")
                return response
            else:
                return "success"

        except Exception as e:
            logger.error(f"处理消息出错: {e}")
            return "success"

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
            logger.error(f"签名验证出错: {e}")
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
            logger.error(f"XML解析出错: {e}")
            return {}

    def handle_text_message(self, xml_data):
        """处理文本消息"""
        try:
            # 获取消息内容
            user_openid = xml_data.get('FromUserName', '')
            my_openid = xml_data.get('ToUserName', '')
            content = xml_data.get('Content', '')
            create_time = xml_data.get('CreateTime', '')

            logger.info(f"收到文本消息: {content} from {user_openid}")

            # 构建回复消息
            reply_content = self.get_auto_reply(content)

            # 创建回复XML
            reply_xml = f"""
            <xml>
                <ToUserName><![CDATA[{user_openid}]]></ToUserName>
                <FromUserName><![CDATA[{my_openid}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{reply_content}]]></Content>
            </xml>
            """

            return reply_xml.strip()

        except Exception as e:
            logger.error(f"处理文本消息出错: {e}")
            return "success"

    def handle_event_message(self, xml_data):
        """处理事件消息"""
        try:
            event = xml_data.get('Event', '')
            user_openid = xml_data.get('FromUserName', '')

            logger.info(f"收到事件消息: {event} from {user_openid}")

            if event == 'subscribe':
                # 用户关注事件
                reply_content = "感谢关注AgentPsy心理评估平台！\n\n我们可以为您提供专业的心理评估服务。\n\n回复关键词了解详情：\n- 评估：开始心理评估\n- 报告：查看评估报告\n- 帮助：获取帮助信息"

                return self.create_text_reply(xml_data, reply_content)

            return "success"

        except Exception as e:
            logger.error(f"处理事件消息出错: {e}")
            return "success"

    def create_text_reply(self, xml_data, content):
        """创建文本回复消息"""
        try:
            user_openid = xml_data.get('FromUserName', '')
            my_openid = xml_data.get('ToUserName', '')
            create_time = xml_data.get('CreateTime', '')

            reply_xml = f"""
            <xml>
                <ToUserName><![CDATA[{user_openid}]]></ToUserName>
                <FromUserName><![CDATA[{my_openid}]]></FromUserName>
                <CreateTime>{create_time}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{content}]]></Content>
            </xml>
            """

            return reply_xml.strip()

        except Exception as e:
            logger.error(f"创建回复消息出错: {e}")
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

# 健康检查接口
class HealthCheck:
    def GET(self):
        return json.dumps({
            "status": "ok",
            "service": "wechat-server",
            "version": "1.0.0"
        }, ensure_ascii=False)

# 添加健康检查路由
urls += ('/health', 'HealthCheck')
urls += ('/health/', 'HealthCheck')

if __name__ == "__main__":
    logger.info("微信公众号服务器启动中...")
    logger.info(f"Token: {WECHAT_TOKEN}")
    logger.info("服务器运行在端口 8080")

    # 启动Web服务器
    app.run(host='0.0.0.0', port=8080)