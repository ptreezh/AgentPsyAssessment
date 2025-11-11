#!/usr/bin/env python3
"""
测试真实微信公众号发文功能
"""

import json
import sys
import time
from pathlib import Path

# 导入真实微信发布服务器
import importlib.util
spec = importlib.util.spec_from_file_location("real_wechat_publisher", "wechat_real_publisher_mcp.py")
real_wechat_publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(real_wechat_publisher)
RealWeChatPublisherMCPServer = real_wechat_publisher.RealWeChatPublisherMCPServer

class RealWeChatPublisherTest:
    def __init__(self):
        self.server = RealWeChatPublisherMCPServer()

    def test_config_check(self):
        """测试配置检查"""
        print("🔍 测试微信公众号配置检查")
        print("=" * 50)

        try:
            config_status = self.server.check_wechat_config()

            print("📋 配置状态:")
            for key, value in config_status.items():
                status_icon = "✅" if value else "❌"
                status_text = "已配置" if value else "未配置"
                print(f"  {key}: {status_icon} {status_text}")

            if config_status.get("enabled") and config_status.get("appid_configured") and config_status.get("appsecret_configured"):
                print("\n✅ 基础配置完整，可以进行 API 测试")
                return True
            else:
                print("\n❌ 配置不完整，请运行配置向导")
                return False

        except Exception as e:
            print(f"❌ 配置检查失败: {e}")
            return False

    def test_access_token(self):
        """测试 Access Token 获取"""
        print("\n🔐 测试 Access Token 获取")
        print("=" * 50)

        try:
            access_token = self.server.get_access_token()

            if access_token and "error" not in str(access_token):
                print("✅ Access Token 获取成功")
                print(f"Token 长度: {len(access_token)} 字符")
                print(f"Token 有效期: 2小时")
                return True
            else:
                print("❌ Access Token 获取失败")
                if access_token and "error" in str(access_token):
                    print(f"错误信息: {access_token}")
                return False

        except Exception as e:
            print(f"❌ Access Token 测试异常: {e}")
            return False

    def test_article_creation(self):
        """测试文章创建（草稿模式）"""
        print("\n📝 测试文章创建（草稿模式）")
        print("=" * 50)

        test_markdown = """# 测试文章标题

这是一篇用于测试微信公众号 API 功能的文章。

## 功能测试

- **Markdown 转换**: 测试 Markdown 到 HTML 的转换
- **草稿创建**: 测试创建微信公众号草稿
- **API 连接**: 测试与微信服务器的连接

### 测试内容

1. 标题格式测试
2. 段落格式测试
3. 列表格式测试

> 这是引用块测试
> 用于验证格式转换功能

**粗体文本** 和 *斜体文本* 的展示效果。

`inline code` 行内代码示例。

```python
# 代码块示例
def test_wechat_api():
    print("Testing WeChat API")
    return "success"
```

---

感谢使用微信公众号发文工具！
"""

        try:
            # 调用异步方法
            import asyncio

            async def test_creation():
                result = await self.server.run_real_wechat_publisher(
                    markdown_content=test_markdown,
                    title="微信公众号 API 测试文章",
                    author="AI Assistant",
                    tags=["测试", "API", "微信公众号"],
                    preview=True
                )
                return result

            result = asyncio.run(test_creation())

            if "error" in result:
                print(f"❌ 文章创建失败: {result['error']}")
                return False
            else:
                print("✅ 文章创建成功")
                print(f"文章标题: {result['article']['title']}")
                print(f"文章模式: {result['article']['mode']}")
                print(f"字数统计: {result['article']['word_count']}")
                print(f"阅读时间: {result['article']['reading_time']} 分钟")
                print(f"状态: {result['status']}")

                if result.get('article', {}).get('mode') == 'real':
                    print(f"媒体ID: {result['article'].get('media_id', 'N/A')}")
                    print(f"草稿链接: {result.get('draft_url', 'N/A')}")

                return True

        except Exception as e:
            print(f"❌ 文章创建测试异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 真实微信公众号发文功能完整测试")
        print("=" * 60)

        tests = [
            ("配置检查", self.test_config_check),
            ("Access Token 获取", self.test_access_token),
            ("文章创建测试", self.test_article_creation)
        ]

        results = []
        total_tests = len(tests)

        for i, (test_name, test_func) in enumerate(tests, 1):
            print(f"\n{i}/{total_tests} {test_name}")
            print("-" * 40)

            try:
                success = test_func()
                results.append({
                    "test_name": test_name,
                    "success": success,
                    "error": None
                })
            except Exception as e:
                results.append({
                    "test_name": test_name,
                    "success": False,
                    "error": str(e)
                })

        # 总结
        successful_tests = sum(1 for r in results if r['success'])
        failed_tests = total_tests - successful_tests

        print(f"\n" + "=" * 60)
        print(f"🎉 测试完成！")
        print(f"📊 测试结果: {successful_tests}/{total_tests} 通过")

        if successful_tests == total_tests:
            print("🎊 所有测试通过！微信公众号 API 连接正常！")
            print("\n🚀 你现在可以:")
            print("1. 使用 MCP 技能: mcp__real-wechat-publisher__run_real_wechat_publisher")
            print("2. 使用 CLI 工具进行文章发布")
            print("3. 在微信公众号后台查看创建的草稿")
        else:
            print(f"⚠️ {failed_tests} 个测试失败，请检查配置和网络连接")

            print("\n🔧 故障排查建议:")
            for result in results:
                if not result['success']:
                    print(f"❌ {result['test_name']}: {result.get('error', '未知错误')}")

        # 保存测试结果
        self.save_test_results(results)
        return successful_tests == total_tests

    def save_test_results(self, results):
        """保存测试结果"""
        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)

        timestamp = int(time.time())
        result_file = output_dir / f"real_wechat_publisher_test_{timestamp}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_info": {
                    "timestamp": timestamp,
                    "total_tests": len(results),
                    "successful_tests": sum(1 for r in results if r['success']),
                    "tool": "real_wechat_publisher"
                },
                "results": results,
                "config_status": self.server.check_wechat_config()
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 测试结果已保存到: {result_file}")

def main():
    tester = RealWeChatPublisherTest()

    if len(sys.argv) > 1:
        test_type = sys.argv[1]

        if test_type == "config":
            tester.test_config_check()
        elif test_type == "token":
            tester.test_access_token()
        elif test_type == "article":
            tester.test_article_creation()
        else:
            print("用法: python test_real_wechat_publisher.py [config|token|article]")
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()