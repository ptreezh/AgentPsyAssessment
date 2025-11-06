# OpenRouter 集成设置指南

本指南将帮助您配置和使用 OpenRouter 集成，为您的便携式心理评估系统提供强大的云模型支持。

## 🎯 OpenRouter 简介

OpenRouter 是一个AI模型聚合平台，提供以下优势：

- **统一接口**: 访问多种顶级AI模型（Claude、GPT-4、Gemini等）
- **成本优化**: 竞争性定价和智能模型路由
- **高可用性**: 99.9%的正常运行时间保证
- **灵活配置**: 支持不同任务的最佳模型选择

## 📋 前置要求

1. **OpenRouter 账户**: 在 [https://openrouter.ai](https://openrouter.ai) 注册账户
2. **API 密钥**: 获取您的 OpenRouter API 密钥
3. **Python 环境**: Python 3.8+ 和所需依赖包

## 🔧 配置步骤

### 1. 设置环境变量

创建 `.env` 文件（基于 `.env.example`）：

```bash
# 复制环境变量模板
cp .env.example .env
```

编辑 `.env` 文件，添加您的 OpenRouter API 密钥：

```env
# OpenRouter配置 (推荐)
OPENROUTER_API_KEY=your_actual_openrouter_api_key_here
```

### 2. 验证安装

运行集成测试：

```bash
python test_openrouter_integration.py
```

预期输出：
```
🧪 OpenRouter集成测试
============================================================
测试时间: 2025-11-06 21:30:03

🔐 检查环境配置...
✅ OPENROUTER_API_KEY 已设置
   密钥预览: ...sk-or-v1-your-key-end

🔗 测试统一API客户端
============================================================
✅ 统一API客户端创建成功

📡 测试连接状态...
  openrouter: ✅ 连接正常
  ollama: ✅ 连接正常
```

### 3. 查看可用模型

```python
from unified_api_client import create_unified_client

client = create_unified_client()
models = client.get_available_models()

print("OpenRouter 可用模型:")
for model in models["openrouter"][:5]:
    print(f"- {model['id']}: {model['name']}")
```

## 🚀 使用方法

### 基本用法

```python
from unified_api_client import create_unified_client

# 创建客户端
client = create_unified_client()

# 发送聊天请求
messages = [
    {"role": "system", "content": "你是一个专业的心理评估助手。"},
    {"role": "user", "content": "请分析这个人的性格特质"}
]

response = client.chat_completion(
    model="anthropic/claude-3.5-sonnet",  # 使用 Claude 3.5 Sonnet
    messages=messages,
    temperature=0.7,
    max_tokens=1000
)

# 提取响应内容
content = response["choices"][0]["message"]["content"]
print(content)
```

### 模型推荐

系统为不同任务提供模型推荐：

```python
# 获取评估任务推荐模型
evaluation_models = client.get_recommended_models("evaluation")
for model in evaluation_models:
    print(f"{model['model']}: {model['reason']}")

# 输出示例:
# anthropic/claude-3.5-sonnet: 高质量评估，精确分析
# openai/gpt-4o: 平衡性能与速度
# anthropic/claude-3-opus: 顶级推理能力
```

### 成本计算

```python
# 计算API调用成本
model = "anthropic/claude-3.5-sonnet"
input_tokens = 1000
output_tokens = 500

cost = client.calculate_cost(model, input_tokens, output_tokens)
print(f"调用成本: ${cost:.6f}")
```

## 🎛️ 支持的模型

### 高质量模型（推荐用于评估）

| 模型 | 描述 | 优势 |
|------|------|------|
| `anthropic/claude-3.5-sonnet` | Claude 3.5 Sonnet | 最强大的评估模型，精确分析 |
| `openai/gpt-4o` | GPT-4o | 快速准确，性价比高 |
| `anthropic/claude-3-opus` | Claude 3 Opus | 顶级推理，适合复杂分析 |

### 经济模型

| 模型 | 描述 | 优势 |
|------|------|------|
| `anthropic/claude-3-haiku` | Claude 3 Haiku | 快速响应，成本低 |
| `meta-llama/llama-3.1-70b-instruct` | Llama 3.1 70B | 开源模型，性价比高 |
| `qwen/qwen-2.5-72b-instruct` | Qwen 2.5 72B | 中文优势，成本低 |

## 🔧 配置选项

### 模型配置文件

在 `config/models_config.json` 中可以调整模型参数：

```json
{
  "evaluation_configs": {
    "high_quality": {
      "temperature": 0.1,
      "max_tokens": 4096,
      "top_p": 0.9
    },
    "creative": {
      "temperature": 0.8,
      "max_tokens": 4096
    }
  }
}
```

### 环境变量

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 | ✅ |
| `OLLAMA_HOST` | Ollama 服务地址 | ❌ (可选) |

## 💡 最佳实践

### 1. 模型选择策略

- **心理评估**: 使用 `anthropic/claude-3.5-sonnet` 获得最高精度
- **批量分析**: 使用 `openai/gpt-4o` 平衡速度和质量
- **成本敏感**: 使用 `anthropic/claude-3-haiku` 或开源模型

### 2. 成本控制

```python
# 设置合理的token限制
response = client.chat_completion(
    model="anthropic/claude-3.5-sonnet",
    messages=messages,
    max_tokens=2000  # 限制输出长度
)

# 监控使用情况
usage = response.get("usage", {})
input_tokens = usage.get("prompt_tokens", 0)
output_tokens = usage.get("completion_tokens", 0)
cost = client.calculate_cost(model, input_tokens, output_tokens)
```

### 3. 错误处理

```python
try:
    response = client.chat_completion(
        model="anthropic/claude-3.5-sonnet",
        messages=messages
    )
except Exception as e:
    # 降级到本地Ollama模型
    response = client.chat_completion(
        model="llama3.1",
        messages=messages,
        provider="ollama"
    )
```

## 🔍 故障排除

### 常见问题

**Q: 测试显示 "OPENROUTER_API_KEY 未设置"**
```
A: 确保 .env 文件存在且包含正确的 API 密钥
```

**Q: 连接失败或超时**
```
A: 检查网络连接和 API 密钥有效性
```

**Q: 模型不可用**
```
A: 某些模型可能需要特定权限，尝试使用推荐模型
```

### 调试技巧

1. **启用详细日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **测试连接状态**:
```python
connections = client.test_connection()
print(connections)
```

3. **检查模型可用性**:
```python
models = client.get_available_models()
print(f"可用OpenRouter模型: {len(models['openrouter'])}")
```

## 📊 性能对比

| 任务类型 | 推荐模型 | 平均响应时间 | 成本/1K tokens |
|----------|----------|--------------|----------------|
| 心理评估 | Claude 3.5 Sonnet | 2-3秒 | $0.015 |
| 批量分析 | GPT-4o | 1-2秒 | $0.015 |
| 快速测试 | Claude 3 Haiku | <1秒 | $0.00125 |
| 本地处理 | Llama 3.1 | 3-5秒 | $0 |

## 🔗 相关链接

- [OpenRouter 官方文档](https://openrouter.ai/docs)
- [OpenRouter 模型列表](https://openrouter.ai/models)
- [OpenRouter 定价页面](https://openrouter.ai/pricing)
- [API 密钥管理](https://openrouter.ai/keys)

## 📞 技术支持

如果您在配置或使用过程中遇到问题：

1. 查看本指南的故障排除部分
2. 运行 `python test_openrouter_integration.py` 进行诊断
3. 检查项目的 GitHub Issues

---

**注意**: OpenRouter 是付费服务，请根据使用量合理配置预算。建议设置使用限制和监控。