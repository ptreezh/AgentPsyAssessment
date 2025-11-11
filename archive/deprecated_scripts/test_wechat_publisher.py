#!/usr/bin/env python3
"""
测试微信公众号发文 MCP 工具
"""

import json
import sys
import time
from pathlib import Path

# 导入 CLI 包装器
import importlib.util
spec = importlib.util.spec_from_file_location("cli_wrapper", "cli-wrapper.py")
cli_wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli_wrapper)
CLIWrapper = cli_wrapper.CLIWrapper

class WeChatPublisherTest:
    def __init__(self):
        self.wrapper = CLIWrapper()

    def test_basic_functionality(self):
        """测试基础功能"""
        print("🚀 测试微信公众号发文基础功能")
        print("=" * 50)

        # 测试 Markdown 内容
        test_markdown = """# 测试文章标题

这是一个用于测试微信公众号发文功能的示例文章。

## 功能特性

- **Markdown 转 HTML**: 支持完整的 Markdown 语法转换
- **格式美化**: 适配微信公众号的样式要求
- **预览功能**: 支持发布前预览

### 使用方法

1. 编写 Markdown 格式的文章
2. 使用工具转换为 HTML 格式
3. 发布到微信公众号

> 这是一个引用块，用于测试特殊格式的转换效果。

**粗体文本** 和 *斜体文本* 的展示效果。

`inline code` 行内代码示例。

```python
# 代码块示例
def hello_wechat():
    print("Hello, WeChat!")
    return "success"
```

---

感谢使用微信公众号发文工具！
"""

        try:
            print("📝 测试预览功能...")
            result = self.wrapper.run_wechat_publisher(
                markdown_content=test_markdown,
                title="微信公众号发文测试",
                author="AI Assistant",
                tags=["测试", "微信公众号", "MCP"],
                preview=True
            )

            if 'error' in result:
                print(f"❌ 预览测试失败: {result['error']}")
                return False
            else:
                print("✅ 预览测试成功")
                print(f"📊 文章信息: {result['article']['title']}")
                print(f"📝 字数统计: {result['article']['word_count']}")
                print(f"⏱️ 阅读时间: {result['article']['reading_time']} 分钟")

            print("\n" + "=" * 50)
            print("📝 测试模拟发布功能...")

            # 测试发布功能
            result = self.wrapper.run_wechat_publisher(
                markdown_content=test_markdown,
                title="微信公众号发文测试",
                author="AI Assistant",
                tags=["测试", "微信公众号", "MCP"],
                preview=False
            )

            if 'error' in result:
                print(f"❌ 发布测试失败: {result['error']}")
                return False
            else:
                print("✅ 发布测试成功（模拟）")
                print(f"🔗 文章链接: {result.get('publish_url', 'N/A')}")

            return True

        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False

    def test_formatting(self):
        """测试格式转换功能"""
        print("\n🎨 测试格式转换功能")
        print("=" * 50)

        test_cases = [
            {
                "name": "纯文本格式",
                "content": "这是一段纯文本内容，用于测试基本的段落转换功能。"
            },
            {
                "name": "列表格式",
                "content": """# 列表测试

## 无序列表
- 项目一
- 项目二
- 项目三

## 有序列表
1. 第一步
2. 第二步
3. 第三步"""
            },
            {
                "name": "复杂格式",
                "content": """# 复杂格式测试

包含**粗体**、*斜体*、`代码`的文本。

![测试图片](https://example.com/image.jpg)

[链接文本](https://example.com)

> 这是引用内容
> 支持多行引用"""
            }
        ]

        success_count = 0

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试用例 {i}: {test_case['name']}")

            try:
                result = self.wrapper.run_wechat_publisher(
                    markdown_content=test_case['content'],
                    preview=True
                )

                if 'error' in result:
                    print(f"❌ {test_case['name']} 失败: {result['error']}")
                else:
                    print(f"✅ {test_case['name']} 成功")
                    print(f"   转换长度: {len(result['article']['content'])} 字符")
                    success_count += 1

            except Exception as e:
                print(f"❌ {test_case['name']} 异常: {e}")

        print(f"\n📊 格式转换测试结果: {success_count}/{len(test_cases)} 通过")
        return success_count == len(test_cases)

    def save_test_results(self, results):
        """保存测试结果"""
        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)

        timestamp = int(time.time())
        result_file = output_dir / f"wechat_publisher_test_{timestamp}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_info": {
                    "timestamp": timestamp,
                    "total_tests": len(results),
                    "successful_tests": sum(1 for r in results if r['success']),
                    "tool": "wechat_publisher"
                },
                "results": results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 测试结果已保存到: {result_file}")

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 微信公众号发文 MCP 工具完整测试")
        print("=" * 60)

        results = []

        # 1. 基础功能测试
        print("\n1️⃣ 基础功能测试")
        basic_success = self.test_basic_functionality()
        results.append({
            "test_name": "basic_functionality",
            "success": basic_success,
            "description": "基础预览和发布功能测试"
        })

        # 2. 格式转换测试
        print("\n2️⃣ 格式转换测试")
        format_success = self.test_formatting()
        results.append({
            "test_name": "format_conversion",
            "success": format_success,
            "description": "各种 Markdown 格式转换测试"
        })

        # 总结
        successful_tests = sum(1 for r in results if r['success'])
        total_tests = len(results)

        print(f"\n🎉 测试完成！")
        print(f"📊 测试结果: {successful_tests}/{total_tests} 通过")

        if successful_tests == total_tests:
            print("🎊 所有测试通过！微信公众号发文 MCP 工具配置成功！")
        else:
            print("⚠️ 部分测试失败，请检查配置和依赖。")

        # 保存测试结果
        self.save_test_results(results)

        return successful_tests == total_tests

def main():
    tester = WeChatPublisherTest()

    if len(sys.argv) > 1:
        test_type = sys.argv[1]

        if test_type == "basic":
            tester.test_basic_functionality()
        elif test_type == "format":
            tester.test_formatting()
        else:
            print("用法: python test_wechat_publisher.py [basic|format]")
    else:
        tester.run_all_tests()

if __name__ == "__main__":
    main()