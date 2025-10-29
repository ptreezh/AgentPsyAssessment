# Ollama 本地评估器使用指南

## 概述

现在支持使用本地Ollama大模型作为评估器，无需API密钥，完全在本地运行。

## 支持的模型

### 默认配置的模型
1. **ollama_llama3** - `llama3:latest`
   - Meta Llama 3 模型
   - 通用性强，适合大多数评估任务

2. **ollama_qwen3** - `qwen3:8b`
   - 阿里云通义千问3
   - 中文优化，8B参数版本

3. **ollama_mistral** - `mistral-nemo:latest`
   - Mistral NeMo 模型
   - 高性能推理模型

## 安装和设置

### 1. 安装Ollama

**Windows**:
```bash
# 下载并安装Ollama
# 访问 https://ollama.ai/download 下载Windows版本
```

**Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS**:
```bash
# 使用Homebrew
brew install ollama
```

### 2. 启动Ollama服务
```bash
ollama serve
```

### 3. 下载模型
```bash
# 下载Llama3
ollama pull llama3:latest

# 下载Qwen3
ollama pull qwen3:8b

# 下载Mistral NeMo
ollama pull mistral-nemo:latest
```

### 4. 验证安装
```bash
# 检查Ollama服务状态
python shared_analysis/ollama_evaluator.py

# 测试配置
python -c "from shared_analysis.ollama_evaluator import test_ollama_setup; test_ollama_setup()"
```

## 配置文件

配置文件位置: `config/ollama_config.json`

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "timeout": 120,
    "models": {
      "llama3": {
        "name": "llama3:latest",
        "temperature": 0.1,
        "max_tokens": 1024
      },
      "qwen3": {
        "name": "qwen3:8b",
        "temperature": 0.1,
        "max_tokens": 1024
      },
      "mistral": {
        "name": "mistral-nemo:latest",
        "temperature": 0.1,
        "max_tokens": 1024
      }
    }
  },
  "evaluators": {
    "ollama_llama3": {
      "provider": "ollama",
      "model": "llama3",
      "description": "Llama3 本地评估器"
    },
    "ollama_qwen3": {
      "provider": "ollama",
      "model": "qwen3",
      "description": "Qwen3 本地评估器"
    },
    "ollama_mistral": {
      "provider": "ollama",
      "model": "mistral",
      "description": "Mistral NeMo 本地评估器"
    }
  }
}
```

## 使用方法

### 基本使用
```bash
# 使用默认的Llama3评估器
python shared_analysis/analyze_results.py test_file.json

# 使用Qwen3评估器
python shared_analysis/analyze_results.py test_file.json --evaluators ollama_qwen3

# 使用Mistral评估器
python shared_analysis/analyze_results.py test_file.json --evaluators ollama_mistral
```

### 多个评估器对比
```bash
# 使用所有本地评估器
python shared_analysis/analyze_results.py test_file.json --evaluators ollama_llama3 ollama_qwen3 ollama_mistral

# 混合使用本地和云端评估器
python shared_analysis/analyze_results.py test_file.json --evaluators ollama_llama3 gpt
```

### 批量处理
```bash
# 处理多个文件
for file in results/*.json; do
    python shared_analysis/analyze_results.py "$file" --evaluators ollama_llama3
done
```

## 添加新的Ollama模型

### 1. 下载新模型
```bash
# 下载新模型
ollama pull new_model:tag
```

### 2. 更新配置文件
在 `config/ollama_config.json` 中添加：

```json
{
  "ollama": {
    "models": {
      "new_model": {
        "name": "new_model:tag",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "新模型描述"
      }
    }
  },
  "evaluators": {
    "ollama_new_model": {
      "provider": "ollama",
      "model": "new_model",
      "description": "新模型评估器"
    }
  }
}
```

### 3. 更新EVALUATOR_PROVIDERS列表
在 `shared_analysis/analyze_results.py` 中：
```python
EVALUATOR_PROVIDERS = ["gpt", "claude", "gemini", "deepseek", "glm", "qwen", "ollama_llama3", "ollama_qwen3", "ollama_mistral", "ollama_new_model"]
```

## 性能优化

### 1. 模型选择
- **快速评估**: 使用 `qwen3:8b` (8B参数)
- **平衡评估**: 使用 `llama3:latest` (8B参数)
- **高质量评估**: 使用 `mistral-nemo:latest` (12B参数)

### 2. 参数调整
在配置文件中调整：
```json
{
  "temperature": 0.1,    # 降低温度提高一致性
  "max_tokens": 512,    # 减少token数量提高速度
  "timeout": 60          # 减少超时时间
}
```

### 3. 并行处理
```bash
# 使用多个评估器并行处理
python shared_analysis/analyze_results.py test_file.json --evaluators ollama_llama3 ollama_qwen3
```

## 故障排除

### 1. 连接问题
```bash
# 检查Ollama服务状态
ollama ps

# 检查服务是否运行
curl http://localhost:11434/api/tags
```

### 2. 模型问题
```bash
# 列出已下载的模型
ollama list

# 重新下载模型
ollama pull llama3:latest
```

### 3. 配置问题
```bash
# 验证配置文件
python -c "import json; print(json.load(open('config/ollama_config.json')))"

# 测试单个评估器
python -c "
from shared_analysis.ollama_evaluator import create_ollama_evaluator
evaluator = create_ollama_evaluator('ollama_llama3')
print('Evaluator created:', evaluator is not None)
"
```

## 优势

### ✅ 本地评估器优势
1. **完全离线**: 无需网络连接
2. **无成本**: 无API费用
3. **数据安全**: 数据不离开本地
4. **自定义**: 可使用任何本地模型
5. **快速响应**: 本地处理无延迟
6. **可控性**: 完全控制评估过程

### 🔄 与云端评估器对比
| 特性 | 本地Ollama | 云端API |
|------|-----------|--------|
| 成本 | 免费 | 按使用付费 |
| 速度 | 适中 | 依赖网络 |
| 质量 | 依赖模型 | 通常较高 |
| 隐私 | 完全本地 | 数据上传 |
| 可用性 | 依赖本地 | 通常稳定 |

## 最佳实践

1. **首次使用**: 先用 `ollama_llama3` 测试
2. **批量处理**: 使用多个评估器提高准确性
3. **中文内容**: 优先使用 `ollama_qwen3`
4. **复杂分析**: 使用 `ollama_mistral`
5. **定期更新**: 保持模型为最新版本

现在你可以完全在本地进行AI评估，无需依赖外部API服务！