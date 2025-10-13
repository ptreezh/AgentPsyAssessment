# 批量分段评估工具使用说明

## 概述

本工具是一个独立的批量分段式心理评估分析器，可在其他服务器上独立运行，无需依赖原项目的其他组件。它支持多种Ollama模型进行批量评估分析。

## 环境要求

1. Python 3.7+
2. 安装依赖包：
   ```
   pip install requests
   ```
3. Ollama服务运行在本地或远程服务器上
4. 可用的Ollama模型（如 mistral:instruct, phi3:mini, qwen3:4b, gemma3:latest 等）

## 支持的模型

工具默认支持以下模型：
1. `mistral:instruct` - 稳定推理模型
2. `phi3:mini` - 快速轻量模型
3. `qwen3:4b` - 轻量级模型
4. `gemma3:latest` - Google开源模型

## 使用方法

### 1. 单文件分析

分析单个JSON评估文件：

```bash
python batch_segmented_analysis.py <input_file> [evaluator_name] [base_url]
```

参数说明：
- `input_file`: 输入的JSON评估文件路径
- `evaluator_name`: 评估器名称 (默认: ollama_mistral)
- `base_url`: Ollama服务地址 (默认: http://localhost:11434)

示例：
```bash
# 使用默认模型分析文件
python batch_segmented_analysis.py assessment.json

# 使用Gemma3模型分析文件
python batch_segmented_analysis.py assessment.json gemma3

# 使用远程Ollama服务分析文件
python batch_segmented_analysis.py assessment.json ollama_mistral http://192.168.1.100:11434
```

### 2. 批量分析

批量分析目录中的所有JSON文件：

```bash
python batch_segmented_analysis.py batch <input_directory> <output_directory> [evaluator_name] [base_url]
```

参数说明：
- `input_directory`: 包含JSON文件的输入目录
- `output_directory`: 输出结果的目录
- `evaluator_name`: 评估器名称 (默认: ollama_mistral)
- `base_url`: Ollama服务地址 (默认: http://localhost:11434)

示例：
```bash
# 批量分析目录中的文件
python batch_segmented_analysis.py batch ./input ./output

# 使用Gemma3模型批量分析
python batch_segmented_analysis.py batch ./input ./output gemma3

# 使用远程Ollama服务批量分析
python batch_segmented_analysis.py batch ./input ./output ollama_mistral http://192.168.1.100:11434
```

## 配置说明

### 模型配置

工具通过 `evaluator_config.json` 文件支持自定义模型配置。如果该文件存在，工具将优先从配置文件加载模型设置。

示例配置文件：
```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "timeout": 300,
    "models": {
      "gemma3": {
        "name": "gemma3:latest",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Gemma3 - 谷歌开源模型"
      },
      "mistral": {
        "name": "mistral:instruct",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Mistral Instruct - 稳定推理模型"
      }
    }
  },
  "evaluators": {
    "gemma3": {
      "provider": "ollama",
      "model": "gemma3",
      "description": "Gemma3 本地评估器"
    },
    "ollama_mistral": {
      "provider": "ollama",
      "model": "mistral",
      "description": "Mistral Instruct 本地评估器 (主评估器)"
    }
  },
  "default_evaluator": "gemma3"
}
```

### 自定义模型配置

如果需要使用其他模型，可以在 `evaluator_config.json` 文件中添加新的模型配置，或者直接修改脚本中的 `get_model_config` 方法。

## 输出格式

分析结果将保存为JSON格式，包含以下主要部分：

1. **Big Five 分数**: 开放性、尽责性、外向性、宜人性、神经质五个维度的评分
2. **MBTI 类型**: 基于Big Five分数推导的MBTI人格类型
3. **Belbin 角色**: 基于Big Five分数推导的团队角色
4. **问题级别评分**: 每个问题的具体评分和证据
5. **分析摘要**: 分析过程的统计信息

## 测试验证

工具已通过测试验证，能够正常工作：
- 成功连接到Ollama服务
- 成功调用Gemma3模型进行分析
- 成功解析模型响应并计算人格分数
- 输出结果包括Big Five维度评分和MBTI类型

测试结果示例：
```
Big Five 分数:
  openness_to_experience: 10/10.0
  conscientiousness: 10/10.0
  extraversion: 10/10.0
  agreeableness: 10/10.0
  neuroticism: 9.0/10.0
MBTI 类型: ENFJ
```

## 注意事项

1. 确保Ollama服务正在运行且可访问
2. 确保所需的模型已下载到Ollama中
3. 输入的JSON文件需要符合特定格式（包含评估结果和问题数据）
4. 分析过程可能需要较长时间，取决于模型大小和问题数量
5. 工具会自动处理JSON格式错误和模型响应修复

## 故障排除

1. **连接失败**: 检查Ollama服务是否运行，地址和端口是否正确
2. **模型未找到**: 确认模型已通过 `ollama pull` 命令下载
3. **JSON解析错误**: 检查输入文件格式是否正确
4. **超时错误**: 可以增加模型配置中的timeout值