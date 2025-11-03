#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断API服务连接状态
检查OpenRouter和Ollama服务是否正常运行
"""
import os
import requests
import json
from datetime import datetime


def diagnose_openrouter_api():
    """诊断OpenRouter API连接状态"""
    print("📡 诊断OpenRouter API...")
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ 未设置OPENROUTER_API_KEY环境变量")
        return False
    
    print(f"🔑 API密钥: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 测试简单的聊天请求
        payload = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [
                {"role": "user", "content": "Hello, this is a connection test."}
            ],
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions", 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ OpenRouter API连接成功")
            print(f"   模型: {result['model']}")
            print(f"   回复: {result['choices'][0]['message']['content'][:100]}...")
            return True
        else:
            print(f"   ❌ OpenRouter API连接失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ OpenRouter API请求异常: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ OpenRouter API测试失败: {str(e)}")
        return False


def diagnose_ollama_service():
    """诊断Ollama服务状态"""
    print("\n🦙 诊断Ollama服务...")
    
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    print(f"🌐 基础URL: {base_url}")
    
    try:
        # 检查服务是否运行
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()['models']
            print("   ✅ Ollama服务运行中")
            print(f"   可用模型数量: {len(models)}")
            
            # 显示前几个模型
            for i, model in enumerate(models[:5]):
                print(f"     {i+1}. {model['name']}")
            
            # 测试聊天API
            test_model = models[0]['name'] if models else 'qwen3:4b'
            print(f"\n💬 测试 {test_model} 模型聊天API...")
            
            payload = {
                "model": test_model,
                "messages": [
                    {"role": "user", "content": "Hello, this is a connection test."}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100
                }
            }
            
            chat_response = requests.post(f"{base_url}/api/chat", json=payload, timeout=30)
            print(f"   状态码: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                print("   ✅ Ollama聊天API测试成功")
                print(f"   模型: {result.get('model', 'Unknown')}")
                print(f"   回复: {result.get('message', {}).get('content', '')[:100]}...")
                return True
            else:
                print(f"   ❌ Ollama聊天API测试失败: {chat_response.status_code}")
                print(f"   错误信息: {chat_response.text}")
                return False
                
        else:
            print(f"   ❌ Ollama服务响应异常: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ollama服务请求异常: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Ollama服务诊断失败: {str(e)}")
        return False


def diagnose_services():
    """诊断所有服务"""
    print("="*60)
    print("🔍 API服务诊断工具")
    print("="*60)
    print(f"🕐 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 诊断OpenRouter API
    openrouter_ok = diagnose_openrouter_api()
    
    # 诊断Ollama服务
    ollama_ok = diagnose_ollama_service()
    
    print(f"\n" + "="*60)
    print("📊 诊断结果汇总:")
    print(f"   OpenRouter API: {'✅ 正常' if openrouter_ok else '❌ 异常'}")
    print(f"   Ollama服务: {'✅ 正常' if ollama_ok else '❌ 异常'}")
    
    if openrouter_ok:
        print("   🚀 系统将优先使用OpenRouter云模型")
    elif ollama_ok:
        print("   🚀 系统将使用Ollama本地模型作为备选")
    else:
        print("   ⚠️  所有API服务都不可用，请检查配置")
    
    print("="*60)


if __name__ == "__main__":
    diagnose_services()