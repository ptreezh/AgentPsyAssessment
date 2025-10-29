# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Portable PsyAgent is a psychological assessment agent system that supports multiple LLM evaluators and local Ollama models for Big Five personality trait analysis. The system processes assessment responses, generates comprehensive personality reports, and supports batch analysis of multiple model outputs.

## Core Architecture

### Main Components

1. **LLM Assessment Module** (`llm_assessment/`) - Core assessment framework
   - `run_assessment_unified.py` - Main unified assessment runner
   - `services/` - LLM client, model management, prompt building
   - `config/` - Assessment configurations and templates
   - `i18n.py` - Internationalization support

2. **Shared Analysis Module** (`shared_analysis/`) - Analysis and evaluation tools
   - `analyze_results.py` - Primary analysis engine with multi-evaluator support
   - `analyze_big5_results.py` - Big Five personality analysis
   - `analyze_motivation.py` - Motivation analysis (no API required)
   - `ollama_evaluator.py` - Local Ollama model integration

3. **Configuration System**
   - `config/ollama_config.json` - Ollama model configurations
   - `.env` - API keys for cloud services
   - Model-specific settings and evaluators defined in JSON configs

### Data Flow

1. Assessment data (JSON format) → Analysis engines → Personality reports
2. Batch processing supports 294+ result files from multiple model families
3. Local Ollama evaluation provides offline analysis capability

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install Google Gemini support
pip install google-generativeai
```

### Core Analysis Operations
```bash
# Basic personality analysis with default evaluator
python shared_analysis/analyze_results.py data/your_data.json

# Multi-evaluator analysis with cloud models
python shared_analysis/analyze_results.py data/your_data.json --evaluators gpt claude qwen_long qwen3_max

# Local Ollama evaluation
python shared_analysis/analyze_results.py data/your_data.json --evaluators ollama_llama3 ollama_qwen3

# Mixed cloud and local evaluation
python shared_analysis/analyze_results.py data/your_data.json --evaluators qwen_long ollama_llama3

# Big Five specific analysis
python shared_analysis/analyze_big5_results.py data/your_data.json

# Motivation analysis (offline)
python shared_analysis/analyze_motivation.py data/your_data.json --debug
```

### Assessment Generation
```bash
# Run unified assessment system
python llm_assessment/run_assessment_unified.py

# Interactive assessment with configuration
python llm_assessment/interactive_cli_runner.py

# Web-based assessment interface
python llm_assessment/run_web_app.py
```

### Batch Analysis
```bash
# Quick batch test (5 files)
python ultimate_batch_analysis.py --quick

# Filter by model family
python ultimate_batch_analysis.py --filter deepseek

# Full batch processing (294 files)
python ultimate_batch_analysis.py

# Check file statistics
python ultimate_batch_analysis.py --stats
```

### Ollama Local Models
```bash
# Start Ollama service
ollama serve

# Download recommended models
ollama pull llama3:latest
ollama pull qwen3:8b
ollama pull mistral-nemo:latest

# Test Ollama integration
python test_ollama.py
```

## Configuration

### API Keys (.env file)
```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_claude_key

# Google Gemini
GOOGLE_API_KEY=your_gemini_key

# 阿里云通义千问 (Qwen Cloud Models)
DASHSCOPE_API_KEY=your_qwen_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# GLM (智谱AI)
GLM_API_KEY=your_glm_key
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# Moonshot (月之暗面 Kimi)
MOONSHOT_API_KEY=your_moonshot_key
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1

# 示例API密钥配置
DASHSCOPE_API_KEY=sk-ffd03518254b495b8d27e723cd413fc1
```

### Available Cloud Evaluators

**支持多个云服务提供商：**
- **DashScope API** - 阿里云统一访问入口
- **Anthropic API (via BigModel)** - 智谱AI提供的Claude访问

**实际可用的模型列表：**
- ✅ `qwen-long` - Long-context Qwen model for extensive analysis
- ✅ `qwen-max` - Latest Qwen Max model
- ✅ `deepseek-v3.2-exp` - DeepSeek V3.2 Experimental model
- ✅ `Moonshot-Kimi-K2-Instruct` - Moonshot Kimi K2 Instruct model (月之暗面)
- ✅ `claude-3.5-sonnet` - Anthropic Claude 3.5 Sonnet model (via BigModel)
- ✅ `claude-3-opus` - Anthropic Claude 3 Opus model (via BigModel)

**暂不可用的模型：**
- ❌ `deepseek-chat` - 模型名称不存在
- ❌ `GLM-4.5` - GLM模型在DashScope API中不可用
- ❌ `GLM-4.5-AIR` - GLM模型在DashScope API中不可用
- ❌ `glm4.5` - GLM模型在DashScope API中不可用
- ❌ `glm-4.5` - GLM模型在DashScope API中不可用
- ❌ `glm4` - GLM模型在DashScope API中不可用
- ❌ `chatglm4` - GLM模型在DashScope API中不可用
- ❌ `zhipuai-4.5` - GLM模型在DashScope API中不可用

**API配置：**
```bash
# DashScope API (阿里云)
DASHSCOPE_API_KEY=sk-ffd03518254b495b8d27e723cd413fc1

# Anthropic API (via BigModel)
ANTHROPIC_AUTH_TOKEN=488bfcb9b967451c99cb6182ef0156af.BfbJ2NSsEg06S9t2
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
```

**Usage Example:**
```bash
# 配置API密钥
DASHSCOPE_API_KEY=sk-ffd03518254b495b8d27e723cd413fc1

# 使用实际可用的云评估器进行置信度分析
python shared_analysis/analyze_results.py data.json --evaluators qwen-long qwen-max deepseek-v3.2-exp Moonshot-Kimi-K2-Instruct claude-3.5-sonnet claude-3-opus

# 多模型置信度批量分析（使用6个可用模型）
python batch_multi_model_analysis.py results/results --models qwen-long qwen-max deepseek-v3.2-exp Moonshot-Kimi-K2-Instruct claude-3.5-sonnet claude-3-opus

# 使用Claude模型进行快速分析
python multi_model_confidence_analyzer.py your_file.json

# 批量分析前3个文件测试（仅使用Claude模型）
python batch_multi_model_analysis.py results/results --models claude-3.5-sonnet claude-3-opus --sample 3 --delay 20
```

### Ollama Configuration
Edit `config/ollama_config.json` to add models, adjust temperature, and define evaluators. The system supports Mistral, Phi3, Qwen3, and other Ollama-compatible models.

## Testing

### Unit and Integration Tests
```bash
# Test evaluator functionality
python test_evaluators.py

# Test Ollama integration
python test_ollama.py

# Test assessment workflow
python test_assessment_workflow.py

# Test segmented analysis
python test_segmentation.py
```

## Key Features

- **Multi-Evaluator Support**: OpenAI, Claude, Gemini, DeepSeek, GLM, Moonshot Kimi, Qwen Cloud, and local Ollama models
- **Batch Processing**: Handles 294+ assessment files with progress tracking and error recovery
- **Offline Analysis**: Full Ollama support for local processing without API dependencies
- **Big Five Analysis**: Comprehensive personality trait assessment across 5 dimensions
- **Motivation Analysis**: API-free motivational pattern analysis
- **Internationalization**: Multi-language support for assessment content
- **Debug Logging**: Complete conversation logs and debug information in `logs/`

## Output Structure

Analysis results are saved to `output/` directory:
- `analysis_results.json` - Raw analysis data
- `analysis_report.md` - Human-readable report
- `analysis_report.html` - HTML format report
- `evaluation_summary.json` - Assessment summary
- `logs/` - Debug logs and conversation history