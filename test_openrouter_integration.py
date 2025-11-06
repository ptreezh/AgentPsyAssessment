#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenRouter集成测试脚本
验证统一API客户端的OpenRouter功能
"""

import os
import sys
import json
from datetime import datetime

def test_unified_client():
    """测试统一API客户端"""
    print("🔗 测试统一API客户端")
    print("=" * 50)

    try:
        from unified_api_client import create_unified_client

        # 创建客户端
        client = create_unified_client()
        print("✅ 统一API客户端创建成功")

        # 测试连接
        print("\n📡 测试连接状态...")
        connections = client.test_connection()
        for provider, status in connections.items():
            icon = "✅" if status else "❌"
            print(f"  {provider}: {icon} {'连接正常' if status else '连接失败'}")

        # 获取可用模型
        print("\n🤖 获取可用模型...")
        try:
            models = client.get_available_models()
            for provider, model_list in models.items():
                print(f"  {provider}: {len(model_list)} 个模型可用")
                for model in model_list[:3]:  # 只显示前3个
                    name = model.get('name', model.get('id', 'Unknown'))
                    print(f"    - {name}")
        except Exception as e:
            print(f"❌ 获取模型失败: {e}")

        # 测试推荐模型
        print("\n📋 获取推荐模型...")
        recommendations = client.get_recommended_models("evaluation")
        print("评估任务推荐模型:")
        for rec in recommendations[:3]:
            print(f"  - {rec['model']} ({rec['provider']}): {rec['reason']}")

        return client

    except Exception as e:
        print(f"❌ 统一API客户端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_openrouter_chat(client):
    """测试OpenRouter聊天功能"""
    print("\n💬 测试OpenRouter聊天功能")
    print("=" * 50)

    if not client or not client.openrouter_client:
        print("❌ OpenRouter客户端未初始化")
        return False

    # 测试消息
    messages = [
        {"role": "system", "content": "你是一个专业的心理评估助手。"},
        {"role": "user", "content": "请简要解释大五人格模型中的开放性特质。"}
    ]

    # 测试不同模型
    test_models = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "anthropic/claude-3-haiku"
    ]

    results = {}

    for model in test_models:
        print(f"\n🧠 测试模型: {model}")
        try:
            response = client.chat_completion(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )

            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                # 截取前100字符
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"✅ 响应成功: {preview}")

                # 获取使用信息
                usage = response.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                cost = client.calculate_cost(model, input_tokens, output_tokens)

                results[model] = {
                    "success": True,
                    "tokens": {"input": input_tokens, "output": output_tokens},
                    "cost": cost
                }

                print(f"   Tokens: {input_tokens} 输入, {output_tokens} 输出")
                print(f"   成本: ${cost:.6f}")

            else:
                print(f"❌ 响应格式错误")
                results[model] = {"success": False, "error": "响应格式错误"}

        except Exception as e:
            print(f"❌ 请求失败: {e}")
            results[model] = {"success": False, "error": str(e)}

    return results

def test_model_info(client):
    """测试模型信息获取"""
    print("\n📊 测试模型信息获取")
    print("=" * 50)

    test_models = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "llama3.1"  # Ollama模型
    ]

    for model in test_models:
        print(f"\n🔍 获取模型信息: {model}")
        try:
            info = client.get_model_info(model)
            print(f"✅ 模型名称: {info.get('name', 'Unknown')}")
            print(f"   提供商: {info.get('provider', 'Unknown')}")
            print(f"   描述: {info.get('description', 'No description')}")
            print(f"   上下文窗口: {info.get('context_window', 'Unknown')}")

            pricing = info.get('pricing', {})
            print(f"   定价: ${pricing.get('input', 0)}/输入, ${pricing.get('output', 0)}/输出")

        except Exception as e:
            print(f"❌ 获取信息失败: {e}")

def test_cost_calculation(client):
    """测试成本计算"""
    print("\n💰 测试成本计算")
    print("=" * 50)

    test_scenarios = [
        {"model": "anthropic/claude-3.5-sonnet", "input": 1000, "output": 500},
        {"model": "openai/gpt-4o", "input": 2000, "output": 1000},
        {"model": "llama3.1", "input": 5000, "output": 2000}  # 本地模型
    ]

    for scenario in test_scenarios:
        model = scenario["model"]
        input_tokens = scenario["input"]
        output_tokens = scenario["output"]

        try:
            cost = client.calculate_cost(model, input_tokens, output_tokens)
            print(f"📊 {model}:")
            print(f"   {input_tokens} 输入 + {output_tokens} 输出 = ${cost:.6f}")

        except Exception as e:
            print(f"❌ 成本计算失败 ({model}): {e}")

def main():
    """主测试函数"""
    print("🧪 OpenRouter集成测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 检查环境变量
    print("🔐 检查环境配置...")
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if openrouter_key:
        print("✅ OPENROUTER_API_KEY 已设置")
        # 显示部分密钥以确认存在
        print(f"   密钥预览: ...{openrouter_key[-8:]}")
    else:
        print("❌ OPENROUTER_API_KEY 未设置")
        print("   请在 .env 文件中设置 OPENROUTER_API_KEY")
        return

    # 测试统一客户端
    client = test_unified_client()
    if not client:
        print("\n❌ 统一客户端初始化失败，终止测试")
        return

    # 测试模型信息
    test_model_info(client)

    # 测试成本计算
    test_cost_calculation(client)

    # 测试聊天功能（需要API密钥）
    if client.openrouter_client:
        chat_results = test_openrouter_chat(client)

        # 保存测试结果
        if chat_results:
            print(f"\n💾 保存测试结果...")
            results_data = {
                "test_time": datetime.now().isoformat(),
                "openrouter_key_configured": bool(openrouter_key),
                "chat_results": chat_results
            }

            os.makedirs("test_results", exist_ok=True)
            with open("test_results/openrouter_test_results.json", "w", encoding="utf-8") as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print("✅ 测试结果已保存到 test_results/openrouter_test_results.json")

    print("\n🎉 OpenRouter集成测试完成!")

if __name__ == "__main__":
    main()