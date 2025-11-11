#!/usr/bin/env python3
"""
微信公众号配置向导
帮助用户逐步配置微信公众号开发者权限和API设置
"""

import json
import os
from pathlib import Path

class WeChatConfigWizard:
    def __init__(self):
        self.config_file = Path("wechat_config/config.json")
        self.config = self.load_existing_config()

    def load_existing_config(self):
        """加载现有配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.get_default_config()

    def get_default_config(self):
        """获取默认配置"""
        return {
            "wechat": {
                "appid": "",
                "appsecret": "",
                "enabled": False,
                "server_url": "",
                "token": "",
                "encoding_aes_key": ""
            },
            "publish": {
                "auto_publish": False,
                "draft_mode": True,
                "cover_image": "",
                "default_author": "AI Assistant",
                "open_comment": False,
                "only_fans_comment": False
            },
            "api": {
                "timeout": 30,
                "retry_times": 3,
                "token_refresh_buffer": 300
            }
        }

    def save_config(self):
        """保存配置"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def run_wizard(self):
        """运行配置向导"""
        print("🔧 微信公众号配置向导")
        print("=" * 50)
        print("此向导将帮助您配置微信公众号开发者权限")
        print("请按照提示输入您的微信公众号配置信息\n")

        # 步骤 1: 确认账号类型
        print("📋 步骤 1: 确认公众号类型")
        print("请确保您有以下类型的微信公众号:")
        print("✅ 企业号")
        print("✅ 政府号")
        print("✅ 媒体号")
        print("❌ 个人号（无法获取开发者权限）")

        confirm = input("\n您的公众号是否为企业/政府/媒体类型？(y/n): ").lower().strip()
        if confirm != 'y':
            print("❌ 抱歉，只有企业/政府/媒体类型的公众号才能获取开发者权限")
            print("请先升级您的公众号类型后再进行配置")
            return

        # 步骤 2: 基本配置
        print("\n📋 步骤 2: 输入基本配置信息")
        print("请登录微信公众平台 (mp.weixin.qq.com) 获取以下信息:")

        appid = input("请输入 AppID: ").strip()
        if not appid:
            print("❌ AppID 不能为空")
            return

        appsecret = input("请输入 AppSecret: ").strip()
        if not appsecret:
            print("❌ AppSecret 不能为空")
            return

        # 步骤 3: 服务器配置
        print("\n📋 步骤 3: 服务器配置（可选）")
        print("如果您有服务器，可以配置以下信息，否则请留空")

        server_url = input("服务器 URL (例如: https://your-domain.com/wechat): ").strip()
        token = input("自定义 Token: ").strip()
        encoding_key = input("EncodingAESKey: ").strip()

        # 步骤 4: 发布配置
        print("\n📋 步骤 4: 发布行为配置")

        auto_publish = input("是否启用自动发布？(y/n，默认 n): ").lower().strip() == 'y'
        draft_mode = not input("是否跳过草稿直接发布？(y/n，默认 n): ").lower().strip() == 'y'

        default_author = input("默认作者名称 (默认: AI Assistant): ").strip() or "AI Assistant"

        open_comment = input("是否开启评论？(y/n，默认 n): ").lower().strip() == 'y'
        only_fans_comment = False
        if open_comment:
            only_fans_comment = input("是否只允许粉丝评论？(y/n，默认 n): ").lower().strip() == 'y'

        # 步骤 5: 确认配置
        print("\n📋 步骤 5: 确认配置信息")
        print("=" * 50)

        # 更新配置
        self.config["wechat"]["appid"] = appid
        self.config["wechat"]["appsecret"] = appsecret
        self.config["wechat"]["enabled"] = True
        self.config["wechat"]["server_url"] = server_url
        self.config["wechat"]["token"] = token
        self.config["wechat"]["encoding_aes_key"] = encoding_key

        self.config["publish"]["auto_publish"] = auto_publish
        self.config["publish"]["draft_mode"] = draft_mode
        self.config["publish"]["default_author"] = default_author
        self.config["publish"]["open_comment"] = open_comment
        self.config["publish"]["only_fans_comment"] = only_fans_comment

        self.print_config_summary()

        confirm_save = input("\n确认保存配置？(y/n): ").lower().strip()
        if confirm_save == 'y':
            self.save_config()
            print("\n✅ 配置已保存到 wechat_config/config.json")
            print("\n📝 后续步骤:")
            print("1. 确保您的公众号已通过微信认证")
            print("2. 在微信公众平台申请以下API权限:")
            print("   - 素材管理权限")
            print("   - 图文消息管理权限")
            print("   - 用户管理权限")
            print("3. 如果配置了服务器，确保服务器可公网访问并配置了SSL证书")
            print("4. 运行测试: python test_real_wechat_publisher.py")
        else:
            print("❌ 配置未保存")

    def print_config_summary(self):
        """打印配置摘要"""
        print(f"AppID: {self.config['wechat']['appid'][:10]}...")
        print(f"AppSecret: {'*' * 10}{self.config['wechat']['appsecret'][-4:] if self.config['wechat']['appsecret'] else ''}")
        print(f"启用状态: {'✅ 已启用' if self.config['wechat']['enabled'] else '❌ 未启用'}")
        print(f"自动发布: {'✅ 已启用' if self.config['publish']['auto_publish'] else '❌ 未启用'}")
        print(f"草稿模式: {'✅ 启用' if self.config['publish']['draft_mode'] else '❌ 禁用'}")
        print(f"默认作者: {self.config['publish']['default_author']}")

    def check_config_status(self):
        """检查配置状态"""
        print("🔍 微信公众号配置状态检查")
        print("=" * 50)

        if not self.config_file.exists():
            print("❌ 配置文件不存在")
            print("请运行: python wechat_config_wizard.py")
            return

        config = self.config
        wechat_config = config.get("wechat", {})
        publish_config = config.get("publish", {})

        # 检查基础配置
        print("📋 基础配置:")
        print(f"AppID: {'✅ 已配置' if wechat_config.get('appid') else '❌ 未配置'}")
        print(f"AppSecret: {'✅ 已配置' if wechat_config.get('appsecret') else '❌ 未配置'}")
        print(f"启用状态: {'✅ 已启用' if wechat_config.get('enabled') else '❌ 未启用'}")

        # 检查服务器配置
        print("\n🌐 服务器配置:")
        print(f"服务器URL: {'✅ 已配置' if wechat_config.get('server_url') else '⚠️ 未配置（可选）'}")
        print(f"Token: {'✅ 已配置' if wechat_config.get('token') else '⚠️ 未配置（可选）'}")

        # 检查发布配置
        print("\n📤 发布配置:")
        print(f"自动发布: {'✅ 已启用' if publish_config.get('auto_publish') else '⚠️ 草稿模式'}")
        print(f"默认作者: {publish_config.get('default_author', 'AI Assistant')}")

        # 总体状态
        print("\n📊 总体状态:")
        if wechat_config.get('enabled') and wechat_config.get('appid') and wechat_config.get('appsecret'):
            print("✅ 配置完整，可以进行发布测试")
            print("运行: python test_real_wechat_publisher.py")
        else:
            print("⚠️ 配置不完整，请运行配置向导")
            print("运行: python wechat_config_wizard.py")

    def reset_config(self):
        """重置配置"""
        print("⚠️  重置配置")
        print("这将删除当前所有配置并恢复默认设置")

        confirm = input("确认重置配置？(y/n): ").lower().strip()
        if confirm == 'y':
            if self.config_file.exists():
                self.config_file.unlink()
            print("✅ 配置已重置")
        else:
            print("❌ 操作已取消")

def main():
    wizard = WeChatConfigWizard()

    if len(os.sys.argv) > 1:
        command = os.sys.argv[1]

        if command == "check":
            wizard.check_config_status()
        elif command == "reset":
            wizard.reset_config()
        elif command == "wizard":
            wizard.run_wizard()
        else:
            print("用法:")
            print("  python wechat_config_wizard.py wizard  # 运行配置向导")
            print("  python wechat_config_wizard.py check   # 检查配置状态")
            print("  python wechat_config_wizard.py reset   # 重置配置")
    else:
        wizard.run_wizard()

if __name__ == "__main__":
    main()