# 🚀 AgentPsyAssessment - Quick Start Guide v1.0

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Environment Setup](#environment-setup)
- [Quick Installation](#quick-installation)
- [5-Minute Experience](#5-minute-experience)
- [Unified Assessment Skills System](#unified-assessment-skills-system)
- [Basic Usage](#basic-usage)
- [API Configuration](#api-configuration)
- [Supported Assessment Types](#supported-assessment-types)
- [Common Issues](#common-issues)
- [Troubleshooting](#troubleshooting)

## 🎯 System Overview

AgentPsyAssessment is a portable, comprehensive psychological assessment framework that combines multiple psychometric models (Big Five, MBTI, cognitive functions) with AI-driven analysis capabilities.

### ⚠️ Important: Assessment vs Evaluation System Separation

- **📝 Assessment System** (`llm_assessment/`): AI-generated psychological questionnaire responses
- **🎯 Evaluation System** (`production_pipelines/`): Scientific scoring and analysis of responses
- **🧠 Unified Skills System** (`.claude/skills/unified-assessment-system/`): Configuration-driven assessment framework

### 🆕 New Features (v1.0)
- ✨ **Unified Assessment Skills System**: Configuration-driven architecture supporting 6 professional assessment types
- 🤖 **Intelligent Type Detection**: Automatic assessment type identification without manual configuration
- 📊 **Visualization Reports**: Interactive HTML reports with Chart.js data visualization
- 🌍 **Multi-language Support**: Bilingual interface and content (Chinese/English)
- 🎭 **16 MBTI Personalities**: Detailed personality type analysis and mapping

## 🔧 Environment Setup

### System Requirements
- **Python**: 3.8+
- **Memory**: 4GB+ (8GB+ recommended)
- **Storage**: 2GB+ available space
- **System**: Windows 10/11, macOS 10.15+, Linux

## ⚡ Quick Installation

### 1. Clone Project
```bash
# Clone the project
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2. Python Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Install dependencies
pip install -r requirements.txt  # if exists
pip install ollama requests numpy pandas
```

### 3. Configure Environment Variables
```bash
# Set provider (local or cloud)
export PROVIDER="local"  # or "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 4. Verify Installation
```bash
# Run unified assessment system tests
cd .claude/skills/unified-assessment-system
python test_runner.py

# Expected output: 🎉 ALL TESTS PASSED!
```

## 🎯 5-Minute Experience

### Method 1: Quick Test Experience
```bash
# 1. Experience questionnaire generation
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. Experience batch analysis
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. View results
ls results/
```

### Method 2: Local Model Experience
```bash
# Start Ollama (if using local models)
ollama serve

# Download model
ollama pull llama3.1

# Run local assessment
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### Method 3: Skills Demo Experience
```bash
# Run skills demo
python skills_demo_chinese_questionnaire.py

# View generated HTML reports
ls html/
```

## 🧠 Unified Assessment Skills System

### System Architecture
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # Configuration validator
├── 🔍 assessment_detector.py        # Assessment type detector
├── 🏗️ skill_base.py                 # Skills base architecture
├── 📝 unified_questionnaire_responder.py    # Unified questionnaire responder skill
├── 📊 unified_psychological_analyzer.py    # Unified psychological analyzer skill
├── 📄 unified_report_generator.py          # Unified report generator skill
└── 📁 configs/                       # Configuration files directory
    ├── big_five_personality.json     # Big Five personality assessment
    ├── citizenship_knowledge.json   # Citizenship knowledge assessment
    ├── financial_professional.json  # Financial professional assessment
    ├── legal_knowledge.json         # Legal knowledge assessment
    ├── motivation_psychology.json   # Motivation psychology assessment
    └── political_literacy.json      # Political literacy assessment
```

### Supported Assessment Types
1. **Big Five Personality Assessment** - OCEAN five dimensions + MBTI mapping
2. **Citizenship Knowledge Assessment** - Civil rights & obligations, political system awareness
3. **Financial Professional Assessment** - Financial expertise, risk identification capabilities
4. **Legal Knowledge Assessment** - Legal fundamentals, practical operation abilities
5. **Motivation Psychology Assessment** - Achievement motivation, power motivation, affiliative motivation
6. **Political Literacy Assessment** - Political system awareness, critical thinking

### Using Unified Skills System
```bash
# Test unified assessment system
cd .claude/skills/unified-assessment-system
python test_runner.py

# Expected output:
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

## 🌐 Deployment

### Option 1: Local Deployment (Recommended for Beginners)

#### 1. Install Ollama
```bash
# Windows (recommended using Chocolatey)
choco install ollama

# Linux (using curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (using Homebrew)
brew install ollama
```

#### 2. Start Ollama Service
```bash
# Start Ollama service
ollama serve

# Open a new terminal, download recommended models
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### Option 2: Cloud Deployment (Recommended for Professional Users)

#### 1. Get API Keys

**Alibaba Cloud Tongyi Qianwen (DashScope)**
```bash
# Register: https://bailian.console.aliyun.com/
# Get API Key
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Anthropic Claude**
```bash
# Register: https://console.anthropic.com/
# Get API Key
export ANTHROPIC_API_KEY=sk-ant-api-key-here
```

**OpenAI GPT**
```bash
# Register: https://platform.openai.com/
# Get API Key
export OPENAI_API_KEY=sk-openai-key-here
```

#### 2. Environment Variable Configuration
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"
$env:ANTHROPIC_API_KEY="sk-ant-api-key"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-your-api-key"
export ANTHROPIC_API_KEY="sk-ant-api-key"
export OPENAI_API_KEY="sk-openai-key"
```

## 🚀 Quick Usage

### 1. Single Assessment
```bash
# Basic assessment
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfj \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json

# Output file location
# results/assessment_<timestamp>_<model>_<role>.json
```

### 2. Batch Assessment
```bash
# Batch process multiple roles
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles a1,a2,b1

# View batch results
python production_pipelines/local_batch_production/cli.py analyze \
    --input results/latest_batch.json
```

### 3. Advanced Configuration
```bash
# Set temperature and parameters
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --temperature 0.2 \
    --max_tokens 1000

# Use specific configuration file
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --config_path configs/custom_assessment.json
```

## 🎨 Supported Assessment Types

### 1. Big Five Personality
```bash
# File pattern matching: *big_five*, *personality*, *ocean*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json
```

### 2. Citizenship Knowledge
```bash
# File pattern matching: *citizenship*, *公民*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-citizenship-test.json
```

### 3. Financial Professional
```bash
# File pattern matching: *financial*, *金融*, *bank*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-fund-management-test.json
```

### 4. Legal Knowledge
```bash
# File pattern matching: *legal*, *law*, *法律*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-legal-test.json
```

### 5. Motivation Psychology
```bash
# File pattern matching: *motivation*, *动机*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-motivation-test.json
```

### 6. Political Literacy
```bash
# File pattern matching: *political*, *政治*
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-political-test.json
```

## 🔧 Common Commands Quick Reference

### Basic Commands
```bash
# Check system status
python test_end_to_end_complete.py

# Run quick test
python run_local_batch.py --quick

# View available models
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py
```

### Report Generation
```bash
# Generate HTML reports
python generate_all_html_reports.py

# View latest reports
ls html/ | tail -1
```

### Troubleshooting
```bash
# Check dependencies
pip check

# Verify configuration
python -c "import llm_assessment; print('✅ Import successful')"

# Test API connection
python quick_cloud_test.py
```

## ❓ Common Questions

### Q1: How to choose the right model?
**A**:
- **Local models**: `llama3.1`, `mistral` - Fast, free, suitable for testing
- **Cloud models**: `gpt-4o`, `claude-3-5-sonnet` - High quality, requires API keys
- **Recommendation**: Use local models for development, cloud models for production

### Q2: Where are assessment results saved?
**A**:
- Raw results: `results/readonly-original/`
- Processed results: `results/ok/evaluated/`
- HTML reports: `html/`
- Batch analysis: `results/final-*-batch-analysis/`

### Q3: How to add new assessment types?
**A**:
1. Add new JSON configuration in `.claude/skills/questionnaire-responder/configs/`
2. Run `python test_runner.py` to verify configuration
3. The system will automatically detect new assessment types

### Q4: What to do with insufficient memory?
**A**:
```bash
# Limit concurrent requests
export MAX_CONCURRENT_REQUESTS=1

# Use smaller models
python llm_assessment/run_assessment_unified.py --model mistral

# Process in batches
python final_batch_processor.py --limit 5
```

### Q5: API call failure handling?
**A**:
```bash
# Check API keys
echo $OPENAI_API_KEY

# Test connection
python quick_cloud_test.py

# Use local backup
export PROVIDER=local
```

## 🎯 Next Steps

### 📚 Deep Learning
- 📖 [Complete User Manual](../../USER_MANUAL.md)
- 🏗️ [System Architecture Documentation](ARCHITECTURE.md)
- 🔧 [API Reference Documentation](API_REFERENCE.md)

### 🚀 Advanced Features
- 🔌 [Plugin Development Guide](PLUGIN_DEVELOPMENT.md)
- 📊 [Batch Processing Tutorial](BATCH_PROCESSING.md)
- 🌐 [Cloud Deployment Guide](CLOUD_DEPLOYMENT.md)

### 🤝 Community Support
- 🐛 [Issue Feedback](https://github.com/your-repo/issues)
- 💬 [Discussion Area](https://github.com/your-repo/discussions)
- 📧 [Email Support](mailto:support@example.com)

## 🎉 Success Checklist

Complete the following steps to indicate successful setup:

- [ ] ✅ Environment setup complete (Python 3.8+)
- [ ] ✅ Project dependencies installed successfully
- [ ] ✅ Environment variables configured correctly
- [ ] ✅ Test run passed (`python test_runner.py`)
- [ ] ✅ Generated first assessment result
- [ ] ✅ Viewed HTML report
- [ ] ✅ Tried different assessment types

**🎊 Congratulations! You have successfully mastered the basic use of AgentPsyAssessment!**

---

**Version**: v1.0.0
**Update Date**: 2025-01-08
**Author**: AgentPsyAssessment Team