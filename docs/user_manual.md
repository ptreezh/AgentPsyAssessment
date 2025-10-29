# Portable PsyAgent 用户手册

## 目录
1. [项目概述](#项目概述)
2. [功能特性](#功能特性)
3. [系统要求](#系统要求)
4. [安装指南](#安装指南)
5. [快速开始](#快速开始)
6. [详细使用说明](#详细使用说明)
7. [测评模块](#测评模块)
8. [分析评估模块](#分析评估模块)
9. [压力测试模块](#压力测试模块)
10. [配置文件说明](#配置文件说明)
11. [批量处理](#批量处理)
12. [故障排除](#故障排除)
13. [API参考](#api参考)
14. [许可证](#许可证)

## 项目概述

Portable PsyAgent 是一个便携式心理评估代理系统，支持多种大模型评估器和本地Ollama模型。该系统能够对AI代理进行多维度人格测评，生成详细的分析报告，并支持定向加强压力测试。

## 功能特性

- 🧠 **多维度人格评估** - 支持Big Five人格特质分析
- 🤖 **多评估器支持** - 支持OpenAI、Claude、Gemini、DeepSeek、GLM、Qwen和本地Ollama
- 🔧 **配置驱动** - 通过配置文件轻松切换模型和参数
- 📊 **详细分析报告** - 生成包含动机分析、人格特质和行为模式的综合报告
- 🛡️ **本地评估** - 支持完全本地化的Ollama模型评估
- 🔍 **调试日志** - 完整的对话日志和调试信息
- 🚀 **批量分析** - 自动处理大量测评报告，支持智能批处理和进度跟踪
- 💪 **压力测试** - 支持情感压力、认知陷阱和上下文负载等多种压力测试

## 系统要求

- Python 3.8 或更高版本
- Windows、Linux 或 macOS 操作系统
- 至少 4GB RAM（推荐 8GB 或更高）
- 硬盘空间：至少 10GB 可用空间

## 安装指南

### 1. 克隆项目

```bash
git clone <repository_url>
cd portable_psyagent
```

### 2. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 可选：安装Google Gemini支持
pip install google-generativeai
```

### 3. 配置环境变量

创建`.env`文件或设置环境变量：

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic Claude  
ANTHROPIC_API_KEY=your_claude_key

# Google Gemini
GOOGLE_API_KEY=your_gemini_key

# 阿里云Qwen
DASHSCOPE_API_KEY=your_qwen_key

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key

# GLM
GLM_API_KEY=your_glm_key
```

## 快速开始

### 使用Ollama本地模型（推荐）

#### 安装Ollama

```bash
# Windows
# 从 https://ollama.ai/download 下载安装

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama
```

#### 下载模型

```bash
# 启动Ollama服务
ollama serve

# 下载推荐模型
ollama pull llama3:latest
ollama pull qwen3:8b
ollama pull mistral-nemo:latest
```

### 基础评估

```bash
# 使用默认评估器
python shared_analysis/analyze_results.py data/your_data.json

# 使用特定评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators gpt claude

# 使用本地Ollama评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators ollama_llama3 ollama_qwen3
```

## 详细使用说明

### 项目结构

```
portable_psyagent/
├── llm_assessment/          # 测评模块
│   ├── run_assessment_unified.py  # 统一测评入口
│   ├── roles/               # 角色定义文件
│   ├── test_files/          # 测试题库
│   ├── results/             # 测评结果
│   └── services/            # 核心服务
├── shared_analysis/         # 分析评估模块
│   ├── analyze_results.py   # 结果分析主程序
│   ├── analyze_big5_results.py  # Big Five分析
│   ├── analyze_motivation.py    # 动机分析
│   └── ollama_evaluator.py  # Ollama评估器
├── interference_materials/  # 干扰材料（压力测试）
├── config/                  # 配置文件
├── batch_analysis_output/   # 批量分析输出
└── docs/                    # 文档
```

## 测评模块

### 运行测评

```bash
# 基础测评
python llm_assessment/run_assessment_unified.py --model_name gemma3:latest --test_file big5 --role_name a1

# 带压力测试的测评
python llm_assessment/run_assessment_unified.py --model_name gemma3:latest --test_file big5 --role_name a1 --emotional-stress-level 3 --cognitive-trap-type p

# 设置温度参数
python llm_assessment/run_assessment_unified.py --model_name gemma3:latest --test_file big5 --role_name a1 --tmpr 0.7

# 设置上下文长度
python llm_assessment/run_assessment_unified.py --model_name gemma3:latest --test_file big5 --role_name a1 --context-length-mode static --context-length-static 4
```

### 测评参数说明

- `--model_name`: 模型标识符（如 ollama/gemma3:latest）
- `--test_file`: 测试文件名或路径
- `--role_name`: 角色名称
- `--emotional-stress-level`: 情感压力等级（0-4）
- `--cognitive-trap-type`: 认知陷阱类型（p, c, s, r）
- `--tmpr`: 模型温度设置
- `--context-length-mode`: 上下文长度模式（auto, static, dynamic, none）
- `--timeout`: 模型响应超时时间（秒）

## 分析评估模块

### 动机分析

```bash
# 运行动机分析（无需API）
python shared_analysis/analyze_motivation.py data/your_data.json --debug
```

### Big Five人格分析

```bash
# Big Five基础分析
python shared_analysis/analyze_big5_results.py data/your_data.json
```

### 综合分析

```bash
# 使用默认评估器
python shared_analysis/analyze_results.py data/your_data.json

# 使用特定评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators gpt claude

# 使用本地Ollama评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators ollama_llama3 ollama_qwen3
```

## 压力测试模块

### 支持的压力测试类型

1. **情感压力测试** - 通过不同等级的情感压力影响模型表现
2. **认知陷阱测试** - 引入悖论、循环性、语义谬误和程序性陷阱
3. **上下文负载测试** - 通过增加上下文长度测试模型处理能力

### 压力测试参数

- `-esL, --emotional-stress-level`: 情感压力等级（0-4）
- `-ct, --cognitive-trap-type`: 认知陷阱类型
  - `p`: 悖论陷阱
  - `c`: 循环性陷阱
  - `s`: 语义谬误陷阱
  - `r`: 程序性陷阱
- `--context-length-mode`: 上下文长度模式
  - `auto`: 自动检测
  - `static`: 固定长度
  - `dynamic`: 动态比例
  - `none`: 禁用上下文注入

## 配置文件说明

### Ollama配置 (`config/ollama_config.json`)

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "timeout": 120,
    "models": {
      "llama3": {
        "name": "llama3:latest",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Meta Llama 3 - 通用大模型"
      },
      "qwen3": {
        "name": "qwen3:8b",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "阿里云通义千问3 - 8B参数版本"
      },
      "mistral": {
        "name": "mistral-nemo:latest",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Mistral NeMo - 高性能推理模型"
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

## 批量处理

### 批量分析

```bash
# 查看文件统计
python ultimate_batch_analysis.py --stats

# 快速测试 (5个文件)
python ultimate_batch_analysis.py --quick

# 分析特定模型 (如deepseek)
python ultimate_batch_analysis.py --filter deepseek

# 完整批量分析 (所有294个文件)
python ultimate_batch_analysis.py

# Windows用户一键启动
start_batch_analysis.bat
```

### 支持的测评数据

系统支持自动分析 `results/results` 目录中的测评报告，包含多个模型系列的测试数据。

### 批量分析特性

- 🔄 **自动格式转换** - 支持原始测评数据格式
- 📊 **智能批处理** - 支持断点续传和错误恢复
- ⏱️ **进度跟踪** - 实时显示分析进度和预计时间
- 📋 **详细报告** - 生成JSON和Markdown格式摘要
- 🎯 **灵活过滤** - 按模型、样本数量等条件过滤

## 故障排除

### 常见问题

1. **Ollama连接失败**
   ```bash
   # 检查Ollama服务
   ollama ps
   curl http://localhost:11434/api/tags
   ```

2. **批量分析中断**
   ```bash
   # 检查输出目录
   ls -la batch_analysis_results/
   
   # 重新运行（会自动跳过已完成的文件）
   python ultimate_batch_analysis.py --filter deepseek
   ```

3. **内存不足**
   ```bash
   # 减少批量大小
   python ultimate_batch_analysis.py --sample 10
   ```

4. **API密钥问题**
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   ```

5. **模块缺失**
   ```bash
   # 安装缺失的依赖
   pip install google-generativeai
   ```

### 调试模式

```bash
# 启用详细调试输出
python shared_analysis/analyze_results.py data.json --evaluators ollama_llama3
```

查看日志文件：
- `logs/evaluator_conversation_log.txt` - 对话记录
- `logs/debug_info.json` - 调试信息

## API参考

### 测评API

#### run_assessment_unified.py

主要参数：
- `--model_name` (必需): 模型标识符
- `--test_file` (必需): 测试文件
- `--role_name`: 角色名称
- `--debug`: 启用调试模式
- `--test_connection`: 仅测试模型连接性

压力测试参数：
- `--emotional-stress-level`: 情感压力等级 (0-4)
- `--cognitive-trap-type`: 认知陷阱类型 (p, c, s, r)
- `--tmpr`: 模型温度设置
- `--context-length-mode`: 上下文长度模式
- `--timeout`: 响应超时时间

### 分析API

#### analyze_results.py

主要功能：
- 对测评结果进行综合分析
- 生成Big Five和MBTI人格评估
- 支持多种评估器

#### analyze_motivation.py

主要功能：
- 对测评结果进行动机分析
- 生成动机测试报告
- 支持Markdown格式输出

#### analyze_big5_results.py

主要功能：
- 专门针对Big Five人格特质进行分析
- 生成详细的Big Five评分报告

## 许可证

本项目仅用于研究和教育目的。