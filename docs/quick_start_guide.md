# Portable PsyAgent 快速上手指南

## 1. 简介

Portable PsyAgent 是一个便携式心理评估代理系统，支持对AI代理进行多维度人格测评、分析评估和压力测试。本指南将帮助您快速开始使用该系统。

## 2. 系统要求

- Python 3.8 或更高版本
- Windows、Linux 或 macOS 操作系统
- Ollama（推荐用于本地模型）

## 3. 安装步骤

### 3.1 克隆项目

```bash
git clone <repository_url>
cd portable_psyagent
```

### 3.2 安装依赖

```bash
pip install -r requirements.txt
```

### 3.3 安装Ollama（推荐）

#### Windows
从 https://ollama.ai/download 下载安装

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

### 3.4 下载推荐模型

```bash
# 启动Ollama服务
ollama serve

# 在新终端窗口中下载模型
ollama pull llama3:latest
ollama pull qwen3:8b
```

## 4. 快速测评

### 4.1 运行基础测评

```bash
python llm_assessment/run_assessment_unified.py --model_name llama3:latest --test_file big5 --role_name a1
```

### 4.2 查看测评结果

测评结果将保存在 `llm_assessment/results/` 目录中。

## 5. 快速分析

### 5.1 运行人格分析

```bash
python shared_analysis/analyze_results.py llm_assessment/results/your_result_file.json
```

### 5.2 查看分析报告

分析报告将生成在 `analysis_reports/` 目录中，包含JSON和Markdown格式。

## 6. 压力测试示例

### 6.1 运行带压力测试的测评

```bash
python llm_assessment/run_assessment_unified.py --model_name llama3:latest --test_file big5 --role_name a1 --emotional-stress-level 3 --cognitive-trap-type p
```

### 6.2 参数说明

- `--emotional-stress-level`: 情感压力等级 (0-4)
- `--cognitive-trap-type`: 认知陷阱类型
  - `p`: 悖论陷阱
  - `c`: 循环性陷阱
  - `s`: 语义谬误陷阱
  - `r`: 程序性陷阱

## 7. 批量处理

### 7.1 快速批量分析

```bash
python ultimate_batch_analysis.py --quick
```

### 7.2 完整批量分析

```bash
python ultimate_batch_analysis.py
```

## 8. 常见问题

### 8.1 Ollama连接失败

检查Ollama服务是否运行：
```bash
ollama ps
```

### 8.2 模型未找到

确保模型已下载：
```bash
ollama list
```

### 8.3 内存不足

减少批量处理大小：
```bash
python ultimate_batch_analysis.py --sample 5
```

## 9. 获取帮助

如需更多帮助，请查看完整用户手册或提交Issue。