# Portable PsyAgent 用户手册

## 目录
1. [简介](#简介)
2. [安装](#安装)
3.. [配置](#配置)
4. [基本使用](#基本使用)
5. [高级功能](#高级功能)
6. [批量处理](#批量处理)
7. [故障排除](#故障排除)

## 简介

Portable PsyAgent 是一个心理评估系统，旨在使用标准化的心理学框架评估AI代理的人格特质。该系统支持多种评估模型，并提供详细的人格分析报告。

## 安装

### 系统要求
- Python 3.7 或更高版本
- pip 包管理器
- 本地评估：已安装并运行的 Ollama 服务

### 安装步骤

1. 克隆或下载代码库：
   ```bash
   git clone <repository-url>
   cd portable_psyagent_open_source
   ```

2. 安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 安装 Ollama（用于本地模型评估）：
   - Windows: 从 https://ollama.ai/download 下载
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - macOS: `brew install ollama`

4. 下载推荐模型：
   ```bash
   ollama pull mistral:instruct
   ollama pull phi3:mini
   ollama pull qwen3:4b
   ```

## 配置

### API 密钥配置
在项目根目录创建 `.env` 文件，包含您的 API 密钥：

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic Claude  
ANTHROPIC_API_KEY=your_claude_key

# Google Gemini
GOOGLE_API_KEY=your_gemini_key

# 阿里云 Qwen
DASHSCOPE_API_KEY=your_qwen_key

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key

# GLM
GLM_API_KEY=your_glm_key
```

### Ollama 配置
`config/ollama_config.json` 文件包含本地模型的默认配置：

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "timeout": 300,
    "models": {
      "mistral": {
        "name": "mistral:instruct",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Mistral Instruct - 稳定推理模型"
      },
      "phi3_mini": {
        "name": "phi3:mini",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Phi3 Mini - 快速轻量模型"
      },
      "qwen3_4b": {
        "name": "qwen3:4b",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Qwen3 4B - 轻量级模型"
      }
    }
  },
  "evaluators": {
    "ollama_mistral": {
      "provider": "ollama",
      "model": "mistral",
      "description": "Mistral Instruct 本地评估器 (主评估器)"
    },
    "phi3_mini": {
      "provider": "ollama",
      "model": "phi3_mini",
      "description": "Phi3 Mini 本地评估器 (快速)"
    },
    "qwen3_4b": {
      "provider": "ollama",
      "model": "qwen3_4b",
      "description": "Qwen3 4B 本地评估器 (轻量)"
    }
  },
  "default_evaluators": [
    "phi3_mini",
    "qwen3_4b"
  ]
}
```

## 基本使用

### 运行单个评估

分析单个评估文件：

```bash
python shared_analysis/analyze_results.py path/to/your_assessment.json
```

### 使用特定评估器

使用特定评估器：

```bash
# 使用云端评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators gpt claude

# 使用本地 Ollama 评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators ollama_mistral phi3_mini
```

### 动机分析

运行无需 API 密钥的动机分析：

```bash
python shared_analysis/analyze_motivation.py data/your_data.json --debug
```

### 大五人格分析

运行大五人格分析：

```bash
python shared_analysis/analyze_big5_results.py data/your_data.json
```

## 高级功能

### 分段分析

对于长评估报告，系统会自动分段内容以避免上下文窗口限制：

```bash
python segmented_analysis.py path/to/your_assessment.json
```

### 基于角色的人格测试

系统包含18个预定义的人格角色，可用于测试AI代理在不同人格约束下的行为表现。角色文件位于 `llm_assessment/roles/` 目录。

### 压力测试

系统包含定向压力测试，旨在创造不同人格特质之间的内部冲突。这些测试有助于评估压力下的人格稳定性。

## 批量处理

### 批量分析工具

`batchAnalysizeTools` 目录包含一个独立的批量分析工具，可以在其他服务器上使用，无需依赖主项目。

运行批量分析：

```bash
# 分析单个文件
python batch_segmented_analysis.py path/to/input_file.json

# 批量分析目录
python batch_segmented_analysis.py batch path/to/input_directory path/to/output_directory
```

### 自定义批量分析

对于自定义批量处理，可以使用综合批量分析脚本：

```bash
python comprehensive_batch_analysis.py path/to/input_directory path/to/output_directory
```

## 故障排除

### 常见问题

1. **Ollama 连接失败**
   - 确保 Ollama 服务正在运行：`ollama serve`
   - 检查连接：`curl http://localhost:11434/api/tags`
   - 验证模型已下载：`ollama list`

2. **模块未找到**
   - 安装缺失的依赖：`pip install -r requirements.txt`
   - Google Gemini 支持：`pip install google-generativeai`

3. **内存问题**
   - 减少长评估的批量大小
   - 使用轻量模型进行本地评估

4. **API 密钥错误**
   - 检查 `.env` 文件中的 API 密钥配置
   - 验证 API 密钥具有足够权限

### 调试模式

启用调试输出以获取详细日志：

```bash
python shared_analysis/analyze_results.py data.json --evaluators ollama_mistral --debug
```

日志文件在 `logs/` 目录中创建。

## 评估数据格式

### 输入格式

系统接受以下结构的 JSON 格式评估数据：

```json
{
  "assessment_results": [
    {
      "question_id": "Q1",
      "dimension": "extraversion",
      "scenario": "描述场景...",
      "agent_response": "代理的回应...",
      "evaluation_rubric": {
        "description": "评估目标",
        "scale": {
          "1": "低特质表现",
          "3": "中等特质表现", 
          "5": "高特质表现"
        }
      }
    }
  ]
}
```

### 输出格式

分析会产生几个输出文件：

- `analysis_results.json`：包含详细分数的原始分析结果
- `analysis_report.md`：Markdown 格式的人类可读报告
- `analysis_report.html`：HTML 格式的报告
- `logs/` 目录中的日志文件

## 支持的评估类型

系统包含几种预定义的评估类型：

1. **大五人格评估** (`agent-big-five-50-complete2.json`)
   - 50个问题，涵盖所有五个个性维度
   - 基于 IPIP-FFM-50 框架

2. **客户服务技能评估** (`Agent-Customer-Service-50.json`)
   - 50个场景测试客户服务技能

3. **公民知识评估** (`agent-citizenship-test.json`)
   - 测试国家历史、地理、政治和文化知识

4. **压力测试** (`pressure_test_bank.json`)
   - 旨在创造人格特质之间内部冲突的场景

## 添加新模型

### 添加新 Ollama 模型

1. 下载模型：
   ```bash
   ollama pull new_model:tag
   ```

2. 更新 `config/ollama_config.json`：
   ```json
   {
     "ollama": {
       "models": {
         "new_model": {
           "name": "new_model:tag",
           "temperature": 0.1,
           "max_tokens": 1024
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

### 添加新云端模型

要添加对新云端模型的支持，请修改 `shared_analysis/ollama_evaluator.py` 中的评估器创建函数，并添加适当的 API 客户端库。

## 贡献

我们欢迎对 Portable PsyAgent 的改进贡献。请遵循以下步骤：

1. Fork 代码库
2. 创建功能分支
3. 进行修改
4. 如适用，添加测试
5. 提交 pull request

## 许可证

本项目采用 Apache License 2.0 许可证。详情请见 LICENSE 文件。

## 联系方式

如有问题、建议或反馈，请联系：
- 网站：agentpsy.com
- 邮箱：contact@agentpsy.com, 3061176@qq.com, zhangshuren@hznu.edu.cn