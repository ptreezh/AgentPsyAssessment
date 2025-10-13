# Portable PsyAgent

A portable psychological assessment agent system supporting multiple large model evaluators and local Ollama models.

## Features

- 🧠 **Multi-dimensional Personality Assessment** - Supports Big Five personality trait analysis
- 🤖 **Multi-Evaluator Support** - Supports OpenAI, Claude, Gemini, DeepSeek, GLM, Qwen and local Ollama
- 🔧 **Configuration-Driven** - Easily switch models and parameters through configuration files
- 📊 **Detailed Analysis Reports** - Generates comprehensive reports containing motivation analysis, personality traits and behavioral patterns
- 🛡️ **Local Evaluation** - Supports fully localized Ollama model evaluation
- 🔍 **Debug Logs** - Complete conversation logs and debugging information
- 🚀 **Batch Analysis** - Automatically processes large numbers of assessment reports with intelligent batch processing and progress tracking

## Quick Start

### 1. Install Dependencies

```bash
# Install basic dependencies
pip install requests openai anthropic dashscope

# Optional: Install Google Gemini support
pip install google-generativeai
```

### 2. Configure API Keys

Create `.env` file or set environment variables:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic Claude  
ANTHROPIC_API_KEY=your_claude_key

# Google Gemini
GOOGLE_API_KEY=your_gemini_key

# Alibaba Cloud Qwen
DASHSCOPE_API_KEY=your_qwen_key

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key

# GLM
GLM_API_KEY=your_glm_key
```

### 3. Use Ollama Local Models (Recommended)

#### Install Ollama

```bash
# Windows
# Download from https://ollama.ai/download

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama
```

#### Download Models

```bash
# Start Ollama service
ollama serve

# Download recommended models
ollama pull llama3:latest
ollama pull qwen3:8b
ollama pull mistral-nemo:latest
```

## Usage

### Basic Assessment

```bash
# Use default evaluator
python shared_analysis/analyze_results.py data/your_data.json

# Use specific evaluators
python shared_analysis/analyze_results.py data/your_data.json --evaluators gpt claude

# Use local Ollama evaluators
python shared_analysis/analyze_results.py data/your_data.json --evaluators ollama_llama3 ollama_qwen3
```

### Motivation Analysis

```bash
# Run motivation analysis (no API required)
python shared_analysis/analyze_motivation.py data/your_data.json --debug
```

### Big Five Personality Analysis

```bash
# Basic Big Five analysis
python shared_analysis/analyze_big5_results.py data/your_data.json
```

### Batch Analysis

```bash
# View file statistics
python ultimate_batch_analysis.py --stats

# Quick test (5 files)
python ultimate_batch_analysis.py --quick

# Analyze specific model (e.g. deepseek)
python ultimate_batch_analysis.py --filter deepseek

# Full batch analysis (all 294 files)
python ultimate_batch_analysis.py

# Windows users one-click start
start_batch_analysis.bat
```

## Configuration Files

### Ollama Configuration (`config/ollama_config.json`)

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
        "description": "Meta Llama 3 - General purpose large model"
      },
      "qwen3": {
        "name": "qwen3:8b",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Alibaba Cloud Qwen3 - 8B parameter version"
      },
      "mistral": {
        "name": "mistral-nemo:latest",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Mistral NeMo - High-performance reasoning model"
      }
    }
  },
  "evaluators": {
    "ollama_llama3": {
      "provider": "ollama",
      "model": "llama3",
      "description": "Llama3 Local Evaluator"
    },
    "ollama_qwen3": {
      "provider": "ollama",
      "model": "qwen3",
      "description": "Qwen3 Local Evaluator"
    },
    "ollama_mistral": {
      "provider": "ollama",
      "model": "mistral",
      "description": "Mistral NeMo Local Evaluator"
    }
  }
}
```

## Data Format

### Input Data Format

```json
{
  "user_id": "user_001",
  "session_id": "session_001",
  "responses": [
    {
      "question_id": "q1",
      "scenario": "Describe scenario...",
      "prompt_for_agent": "Instructions for AI...",
      "agent_response": "AI's response...",
      "dimension": "Personality dimension",
      "evaluation_rubric": {
        "description": "Evaluation objective",
        "scale": {
          "1": "1-point description",
          "2": "2-point description",
          "3": "3-point description",
          "4": "4-point description",
          "5": "5-point description"
        }
      }
    }
  ]
}
```

### Output Report Format

After evaluation, the following files will be generated:

```
output/
├── analysis_results.json          # Raw analysis results
├── analysis_report.md            # Human-readable report
├── analysis_report.html          # HTML format report
├── evaluation_summary.json       # Evaluation summary
└── logs/                         # Debug logs
    ├── evaluator_conversation_log.txt  # Conversation logs
    └── debug_info.json           # Debug information
```

## Available Evaluators

### Cloud Evaluators

| Evaluator | Provider | Description | Status |
|-----------|----------|-------------|--------|
| gpt | OpenAI | GPT-4/GPT-3.5 | ✅ |
| claude | Anthropic | Claude 3 | ⚠️ |
| gemini | Google | Gemini Pro | ⚠️ |
| qwen | Alibaba Cloud | Tongyi Qianwen | ⚠️ |
| deepseek | DeepSeek | DeepSeek Chat | ❌ |
| glm | Zhipu AI | GLM-4 | ❌ |

### Local Ollama Evaluators

| Evaluator | Model | Description | Status |
|-----------|-------|-------------|--------|
| ollama_llama3 | llama3:latest | Meta Llama 3 | ✅ |
| ollama_qwen3 | qwen3:8b | Tongyi Qwen3 8B | ✅ |
| ollama_mistral | mistral-nemo:latest | Mistral NeMo | ✅ |

## Batch Analysis

### Supported Assessment Data

The system supports automatic analysis of assessment reports in the `results/results` directory, including:

| Model Series | File Count | Description |
|--------------|------------|-------------|
| deepseek | 65 | DeepSeek R1 series |
| orca | 96 | Orca Mini series |
| llama3.2 | 23 | Llama 3.2 series |
| Yinr | 63 | Yinr model series |
| wizardlm2 | 21 | WizardLM 2 series |
| qwen2 | 21 | Qwen 2 series |
| llama3.1 | 2 | Llama 3.1 series |
| qwen3 | 2 | Qwen 3 series |
| qwen2.5 | 1 | Qwen 2.5 series |
| **Total** | **294** | **Covering 10 model series** |

### Batch Analysis Features

- 🔄 **Automatic Format Conversion** - Supports original assessment data format
- 📊 **Intelligent Batch Processing** - Supports resume and error recovery
- ⏱️ **Progress Tracking** - Real-time display of analysis progress and estimated time
- 📋 **Detailed Reports** - Generates JSON and Markdown format summaries
- 🎯 **Flexible Filtering** - Filter by model, sample count, etc.

### Performance Metrics

| File Count | Estimated Time | Memory Usage | Recommended Evaluator |
|------------|----------------|--------------|-----------------------|
| 5 | ~10 minutes | <2GB | Single |
| 20 | ~40 minutes | <4GB | Single |
| 50 | ~1.5 hours | <6GB | Single |
| 100 | ~3 hours | <8GB | Single |
| 294 | ~10 hours | <12GB | Single |

## Troubleshooting

### Common Issues

1. **Ollama Connection Failure**
   ```bash
   # Check Ollama service
   ollama ps
   curl http://localhost:11434/api/tags
   ```

2. **Batch Analysis Interrupted**
   ```bash
   # Check output directory
   ls -la batch_analysis_results/
   
   # Re-run (will automatically skip completed files)
   python ultimate_batch_analysis.py --filter deepseek
   ```

3. **Out of Memory**
   ```bash
   # Reduce batch size
   python ultimate_batch_analysis.py --sample 10
   ```

4. **API Key Issues**
   ```bash
   # Check environment variables
   echo $OPENAI_API_KEY
   ```

5. **Missing Modules**
   ```bash
   # Install missing dependencies
   pip install google-generativeai
   ```

### Debug Mode

```bash
# Enable detailed debug output
python shared_analysis/analyze_results.py data.json --evaluators ollama_llama3
```

Check log files:
- `logs/evaluator_conversation_log.txt` - Conversation records
- `logs/debug_info.json` - Debug information

## Add New Ollama Models

1. Download new model:
   ```bash
   ollama pull new_model:tag
   ```

2. Update configuration file `config/ollama_config.json`:
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
         "description": "New Model Evaluator"
       }
     }
   }
   ```

## License

This project is for research and educational purposes only.

## Contributing

Welcome to submit issues and pull requests to improve this project.