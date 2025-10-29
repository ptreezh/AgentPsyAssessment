# Portable PsyAgent

一个便携式心理评估代理系统，支持多种大模型评估器和本地Ollama模型。

## 功能特性

- 🧠 **多维度人格评估** - 支持Big Five人格特质分析
- 🤖 **多评估器支持** - 支持OpenAI、Claude、Gemini、DeepSeek、GLM、Qwen和本地Ollama
- 🔧 **配置驱动** - 通过配置文件轻松切换模型和参数
- 📊 **详细分析报告** - 生成包含动机分析、人格特质和行为模式的综合报告
- 🛡️ **本地评估** - 支持完全本地化的Ollama模型评估
- 🔍 **调试日志** - 完整的对话日志和调试信息
- 🚀 **批量分析** - 自动处理大量测评报告，支持智能批处理和进度跟踪

## 快速开始

### 1. 安装依赖

```bash
# 安装基础依赖
pip install requests openai anthropic dashscope

# 可选：安装Google Gemini支持
pip install google-generativeai
```

### 2. 配置API密钥

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

### 3. 使用Ollama本地模型（推荐）

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

## 使用方法

### 基础评估

```bash
# 使用默认评估器
python shared_analysis/analyze_results.py data/your_data.json

# 使用特定评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators gpt claude

# 使用本地Ollama评估器
python shared_analysis/analyze_results.py data/your_data.json --evaluators ollama_llama3 ollama_qwen3
```

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

## 配置文件

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

## 数据格式

### 输入数据格式

```json
{
  "user_id": "user_001",
  "session_id": "session_001",
  "responses": [
    {
      "question_id": "q1",
      "scenario": "描述场景...",
      "prompt_for_agent": "给AI的指令...",
      "agent_response": "AI的回答...",
      "dimension": "人格维度",
      "evaluation_rubric": {
        "description": "评估目标",
        "scale": {
          "1": "1分描述",
          "2": "2分描述",
          "3": "3分描述",
          "4": "4分描述",
          "5": "5分描述"
        }
      }
    }
  ]
}
```

### 输出报告格式

评估完成后会生成以下文件：

```
output/
├── analysis_results.json          # 原始分析结果
├── analysis_report.md            # 人类可读报告
├── analysis_report.html          # HTML格式报告
├── evaluation_summary.json       # 评估摘要
└── logs/                         # 调试日志
    ├── evaluator_conversation_log.txt  # 对话日志
    └── debug_info.json           # 调试信息
```

## 可用评估器

### 云端评估器

| 评估器 | 提供商 | 描述 | 状态 |
|--------|--------|------|------|
| gpt | OpenAI | GPT-4/GPT-3.5 | ✅ |
| claude | Anthropic | Claude 3 | ⚠️ |
| gemini | Google | Gemini Pro | ⚠️ |
| qwen | 阿里云 | 通义千问 | ⚠️ |
| deepseek | DeepSeek | DeepSeek Chat | ❌ |
| glm | 智谱AI | GLM-4 | ❌ |

### 本地Ollama评估器

| 评估器 | 模型 | 描述 | 状态 |
|--------|------|------|------|
| ollama_llama3 | llama3:latest | Meta Llama 3 | ✅ |
| ollama_qwen3 | qwen3:8b | 通义千问3 8B | ✅ |
| ollama_mistral | mistral-nemo:latest | Mistral NeMo | ✅ |

## 批量分析

### 支持的测评数据

系统支持自动分析 `results/results` 目录中的测评报告，包含：

| 模型系列 | 文件数量 | 说明 |
|----------|----------|------|
| deepseek | 65 | DeepSeek R1系列 |
| orca | 96 | Orca Mini系列 |
| llama3.2 | 23 | Llama 3.2系列 |
| Yinr | 63 | Yinr模型系列 |
| wizardlm2 | 21 | WizardLM 2系列 |
| qwen2 | 21 | Qwen 2系列 |
| llama3.1 | 2 | Llama 3.1系列 |
| qwen3 | 2 | Qwen 3系列 |
| qwen2.5 | 1 | Qwen 2.5系列 |
| **总计** | **294** | **涵盖10个模型系列** |

### 批量分析特性

- 🔄 **自动格式转换** - 支持原始测评数据格式
- 📊 **智能批处理** - 支持断点续传和错误恢复
- ⏱️ **进度跟踪** - 实时显示分析进度和预计时间
- 📋 **详细报告** - 生成JSON和Markdown格式摘要
- 🎯 **灵活过滤** - 按模型、样本数量等条件过滤

### 性能指标

| 文件数量 | 预计耗时 | 内存使用 | 建议评估器 |
|----------|----------|----------|------------|
| 5 | ~10分钟 | <2GB | 单个 |
| 20 | ~40分钟 | <4GB | 单个 |
| 50 | ~1.5小时 | <6GB | 单个 |
| 100 | ~3小时 | <8GB | 单个 |
| 294 | ~10小时 | <12GB | 单个 |

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

## 添加新的Ollama模型

1. 下载新模型：
   ```bash
   ollama pull new_model:tag
   ```

2. 更新配置文件 `config/ollama_config.json`：
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

### 如何添加新的云模型进行测评

本系统支持通过修改配置文件，无缝接入新的云模型（如通义千问、DeepSeek、月之暗面等）作为“考生”参与测评，无需修改任何代码。

核心原理是：系统通过模型ID的**前缀**来识别服务商，并自动加载对应的API密钥。

以下为三步配置法（以接入通义千问`qwen-long`为例）：

#### 第一步：在 `.env` 文件中配置API密钥

1.  打开项目根目录下的 `.env` 文件。
2.  为您的云服务商添加API密钥，变量名必须遵循 `服务商名大写_API_KEY` 的格式。

    ```
    # .env

    # 阿里云通义千问
    DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"

    # DeepSeek
    DEEPSEEK_API_KEY="your-deepseek-api-key"

    # 月之暗面 (Kimi) - 使用OpenAI兼容接口，服务商名为OPENAI
    OPENAI_API_KEY="your-kimi-api-key"
    OPENAI_API_BASE="https://api.moonshot.cn/v1"
    ```

#### 第二步：在 `batch_config.json` 中添加云模型

1.  打开 `llm_assessment/batch_config.json` 文件。
2.  在 `"models"` 列表中，添加一个新的模型对象。
    -   `"name"`: 您自定义的显示名称。
    -   `"path"`: **核心字段**，必须使用 `服务商名小写/模型ID` 的格式。

    ```json
    // llm_assessment/batch_config.json

    "models": [
        {
            "name": "Ollama Llama 3",
            "path": "ollama/llama3"
        },
        {
            "name": "Qwen Long",
            "path": "dashscope/qwen-long"
        }
    ],
    ```

3.  在 `"test_suites"` 中，将您刚添加的模型的 `"name"` 加入到想运行的测试套件的 `"models_to_run"` 数组中。

    ```json
    // llm_assessment/batch_config.json

    "test_suites": [
        {
            "suite_name": "Standard Big5 Test",
            "models_to_run": [
                "Ollama Llama 3",
                "Qwen Long"
            ],
            "tasks": [
                // ...
            ]
        }
    ]
    ```

#### 第三步：运行批量测评

回到项目根目录 `D:\AIDevelop\portable_psyagent\`，执行以下命令：

```shell
python -m llm_assessment.run_batch_suite
```

系统将自动识别到`Qwen Long`，加载对应的`DASHSCOPE_API_KEY`，并调用其API开始测评。

## 许可证

本项目仅用于研究和教育目的。

## 贡献

欢迎提交Issue和Pull Request来改进此项目。