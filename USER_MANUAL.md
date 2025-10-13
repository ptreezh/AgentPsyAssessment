# Portable PsyAgent User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Batch Processing](#batch-processing)
7. [Troubleshooting](#troubleshooting)

## Introduction

Portable PsyAgent is a psychological assessment system designed to evaluate AI agent personality traits using standardized psychological frameworks. The system supports multiple evaluation models and provides detailed personality analysis reports.

## Installation

### System Requirements
- Python 3.7 or higher
- pip package manager
- For local evaluation: Ollama service installed and running

### Installation Steps

1. Clone or download the repository:
   ```bash
   git clone <repository-url>
   cd portable_psyagent_open_source
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For local model evaluation, install Ollama:
   - Windows: Download from https://ollama.ai/download
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - macOS: `brew install ollama`

4. Download recommended models:
   ```bash
   ollama pull mistral:instruct
   ollama pull phi3:mini
   ollama pull qwen3:4b
   ```

## Configuration

### API Keys Configuration
Create a `.env` file in the project root directory with your API keys:

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

### Ollama Configuration
The `config/ollama_config.json` file contains the default configuration for local models:

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
        "description": "Mistral Instruct - Stable reasoning model"
      },
      "phi3_mini": {
        "name": "phi3:mini",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Phi3 Mini - Fast lightweight model"
      },
      "qwen3_4b": {
        "name": "qwen3:4b",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Qwen3 4B - Lightweight model"
      }
    }
  },
  "evaluators": {
    "ollama_mistral": {
      "provider": "ollama",
      "model": "mistral",
      "description": "Mistral Instruct Local Evaluator (Main Evaluator)"
    },
    "phi3_mini": {
      "provider": "ollama",
      "model": "phi3_mini",
      "description": "Phi3 Mini Local Evaluator (Fast)"
    },
    "qwen3_4b": {
      "provider": "ollama",
      "model": "qwen3_4b",
      "description": "Qwen3 4B Local Evaluator (Lightweight)"
    }
  },
  "default_evaluators": [
    "phi3_mini",
    "qwen3_4b"
  ]
}
```

## Basic Usage

### Running a Single Assessment

To analyze a single assessment file:

```bash
python shared_analysis/analyze_results.py path/to/your_assessment.json
```

### Using Specific Evaluators

To use specific evaluators:

```bash
# Use cloud evaluators
python shared_analysis/analyze_results.py data/your_data.json --evaluators gpt claude

# Use local Ollama evaluators
python shared_analysis/analyze_results.py data/your_data.json --evaluators ollama_mistral phi3_mini
```

### Motivation Analysis

To run motivation analysis without API keys:

```bash
python shared_analysis/analyze_motivation.py data/your_data.json --debug
```

### Big Five Personality Analysis

To run Big Five personality analysis:

```bash
python shared_analysis/analyze_big5_results.py data/your_data.json
```

## Advanced Features

### Segmented Analysis

For long assessment reports, the system automatically segments the content to avoid context window limitations:

```bash
python segmented_analysis.py path/to/your_assessment.json
```

### Role-based Personality Testing

The system includes 18 predefined personality roles that can be used to test how AI agents behave under different personality constraints. Role files are located in `llm_assessment/roles/`.

### Pressure Testing

The system includes targeted pressure tests designed to create internal conflicts between different personality traits. These tests help evaluate personality stability under stress.

## Batch Processing

### Batch Analysis Tool

The `batchAnalysizeTools` directory contains a standalone batch analysis tool that can be used on other servers without dependencies on the main project.

To run batch analysis:

```bash
# Analyze a single file
python batch_segmented_analysis.py path/to/input_file.json

# Batch analyze a directory
python batch_segmented_analysis.py batch path/to/input_directory path/to/output_directory
```

### Custom Batch Analysis

For custom batch processing, you can use the comprehensive batch analysis script:

```bash
python comprehensive_batch_analysis.py path/to/input_directory path/to/output_directory
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama service is running: `ollama serve`
   - Check connection: `curl http://localhost:11434/api/tags`
   - Verify models are downloaded: `ollama list`

2. **Module Not Found**
   - Install missing dependencies: `pip install -r requirements.txt`
   - For Google Gemini support: `pip install google-generativeai`

3. **Memory Issues**
   - Reduce batch size for large assessments
   - Use lighter models for local evaluation

4. **API Key Errors**
   - Check `.env` file for correct API key configuration
   - Verify API keys have sufficient permissions

### Debug Mode

Enable debug output for detailed logging:

```bash
python shared_analysis/analyze_results.py data.json --evaluators ollama_mistral --debug
```

Log files are created in the `logs/` directory.

## Assessment Data Format

### Input Format

The system accepts assessment data in JSON format with the following structure:

```json
{
  "assessment_results": [
    {
      "question_id": "Q1",
      "dimension": "extraversion",
      "scenario": "Describe the scenario...",
      "agent_response": "Agent's response...",
      "evaluation_rubric": {
        "description": "Evaluation objective",
        "scale": {
          "1": "Low trait expression",
          "3": "Moderate trait expression", 
          "5": "High trait expression"
        }
      }
    }
  ]
}
```

### Output Format

The analysis produces several output files:

- `analysis_results.json`: Raw analysis results with detailed scores
- `analysis_report.md`: Human-readable report in Markdown format
- `analysis_report.html`: HTML formatted report
- Log files in the `logs/` directory

## Supported Assessment Types

The system includes several predefined assessment types:

1. **Big Five Personality Assessment** (`agent-big-five-50-complete2.json`)
   - 50 questions covering all five personality dimensions
   - Based on the IPIP-FFM-50 framework

2. **Customer Service Skills Assessment** (`Agent-Customer-Service-50.json`)
   - 50 scenarios testing customer service skills

3. **Citizenship Knowledge Assessment** (`agent-citizenship-test.json`)
   - Tests knowledge of national history, geography, politics, and culture

4. **Pressure Tests** (`pressure_test_bank.json`)
   - Scenarios designed to create internal conflicts between personality traits

## Adding New Models

### Adding New Ollama Models

1. Download the model:
   ```bash
   ollama pull new_model:tag
   ```

2. Update `config/ollama_config.json`:
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

### Adding New Cloud Models

To add support for new cloud models, modify the evaluator creation functions in `shared_analysis/ollama_evaluator.py` and add the appropriate API client libraries.

## Contributing

We welcome contributions to improve Portable PsyAgent. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Contact

For questions, issues, or feedback, please contact:
- Website: agentpsy.com
- Email: contact@agentpsy.com, 3061176@qq.com, zhangshuren@hznu.edu.cn