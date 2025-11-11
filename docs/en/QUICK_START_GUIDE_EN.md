# 🚀 AgentPsyAssessment Quick Start Guide

## 📋 Table of Contents
- [System Overview](#system-overview)
- [Environment Setup](#environment-setup)
- [Installation & Deployment](#installation--deployment)
- [Quick Usage](#quick-usage)
- [API Configuration](#api-configuration)
- [Complete Examples](#complete-examples)
- [Troubleshooting](#troubleshooting)

## 🎯 System Overview

AgentPsyAssessment is a portable psychological assessment framework that uses AI large language models for personality assessment analysis.

### ⚠️ Important: Assessment vs Evaluation System Separation

- **📝 Assessment System** (`llm_assessment/`): AI generates psychological questionnaire responses
- **🎯 Evaluation System** (`production_pipelines/.../transparent_pipeline.py`): Scientific scoring of responses

## 🔧 Environment Setup

### System Requirements
- **Python**: 3.8+
- **Memory**: 8GB+ (16GB+ recommended)
- **System**: Windows/Linux/macOS

### 1. Clone Project
```bash
# Use Git to clone project
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# Or download ZIP package directly
# Visit: https://github.com/ptreezh/AgentPsyAssessment
# Click "Code" → "Download ZIP"
```

### 2. Python Environment Management
```bash
# Recommend using virtual environment
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Install dependencies
pip install -r requirements.txt  # if exists
pip install ollama requests numpy pandas
```

## 🌐 Installation & Deployment

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

# Open new terminal, download recommended models
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### Option 2: Cloud Deployment (Recommended for Professional Users)

#### 1. Get API Keys

**Alibaba Cloud Qwen (DashScope)**
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

### Step 1: Generate Psychological Questionnaire Responses (Assessment System)

```bash
# Basic usage - use default model
python llm_assessment/run_assessment_unified.py

# Specify model and role
python llm_assessment/run_assessment_unified.py \
    --model_name deepseek-r1:8b \
    --role_name enfj \
    --tmpr 0.7

# Use Chinese questionnaire
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name def \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

**Output Example**:
```
🎯 AI Assessment Complete!
Model: deepseek-r1:8b
Role: enfj
Output file: results/assessment_result_20250108_123456.json
```

### Step 2: Scientific Scoring Analysis (Evaluation System)

```python
# Create evaluation script evaluate_result.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser
import json

# Initialize evaluation pipeline (use cloud models + adaptive consensus algorithm)
pipeline = TransparentPipeline(use_cloud=True)

# Parse responses
parser = InputParser()
questions = parser.parse_assessment_json('results/assessment_result_20250108_123456.json')

# Evaluate first question
question = questions[0]
result = pipeline.process_single_question(question, 0)

# Output results
print(f"✅ Evaluation Complete!")
print(f"Final Score: {result['final_adjusted_scores']}")
print(f"Overall Reliability: {result['confidence_metrics']['overall_reliability']:.3f}")
print(f"Models Used: {len(result['models_used'])}")
print(f"Consensus Method: {result['confidence_metrics']['consensus_method']}")
```

Run evaluation:
```bash
python evaluate_result.py
```

## 🔑 API Configuration Details

### Model Configuration File
Edit `llm_assessment/config/ollama_config.json`:

```json
{
  "models": {
    "deepseek-r1:8b": {
      "provider": "ollama",
      "api_base": "http://localhost:11434",
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "qwen3:8b": {
      "provider": "ollama",
      "api_base": "http://localhost:11434",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  },
  "evaluators": {
    "primary": ["deepseek-r1:8b", "qwen3:8b"],
    "dispute": ["mistral-nemo:latest"]
  }
}
```

### Cloud Model Configuration
Edit `production_pipelines/local_batch_production/single_report_pipeline/config.yaml`:

```yaml
cloud_models:
  primary:
    - deepseek-v3.1:671b-cloud
    - gpt-oss:120b-cloud
    - qwen3-vl:235b-cloud

  dispute:
    - qwen3-vl:235b-cloud
    - gpt-oss:120b-cloud

api_keys:
  dashscope: "${DASHSCOPE_API_KEY}"
  anthropic: "${ANTHROPIC_API_KEY}"
  openai: "${OPENAI_API_KEY}"
```

## 📚 Complete Examples

### Example 1: Complete Evaluation Workflow

```bash
# 1. Generate responses
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name enfj \
    --tmpr 0.7

# 2. Create evaluation script
cat > complete_evaluation.py << 'EOF'
from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

# Initialize cloud evaluation system
pipeline = TransparentPipeline(use_cloud=True)
parser = InputParser()

# Parse responses
questions = parser.parse_assessment_json('results/latest_assessment.json')

# Batch evaluation
all_results = []
for i, question in enumerate(questions):
    print(f"Evaluating question {i+1}/{len(questions)}: {question.get('question_id', 'Unknown')}")
    result = pipeline.process_single_question(question, i)
    all_results.append(result)

# Generate summary report
print("\n🎉 Evaluation Complete!")
print(f"Total questions: {len(all_results)}")
print(f"Average reliability: {sum(r['confidence_metrics']['overall_reliability'] for r in all_results) / len(all_results):.3f}")

# Save results
import json
with open('evaluation_results.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
EOF

# 3. Run evaluation
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../../../complete_evaluation.py
```

### Example 2: Batch Processing Multiple Roles

```bash
# Generate responses for multiple roles
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py \
        --model_name qwen3:8b \
        --role_name $role \
        --tmpr 0.7
    echo "✅ Completed $role role assessment"
done

# Batch evaluation
python batch_evaluation.py
```

## 🛠️ Advanced Features

### 1. Custom Role Configuration
Edit `llm_assessment/roles/enfj.json`:
```json
{
  "name": "ENFJ - Protagonist",
  "description": "Warm, idealistic, empathetic personality type",
  "traits": {
    "extraversion": 0.7,
    "intuition": 0.8,
    "feeling": 0.9,
    "judging": 0.8
  },
  "communication_style": "Warm, encouraging, insightful"
}
```

### 2. Batch Processing Scripts
```bash
# Create batch script
cat > batch_assess.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj" "infp" "entj")
MODEL="qwen3:8b"

for role in "${ROLES[@]}"; do
    echo "🎯 Processing role: $role"
    python llm_assessment/run_assessment_unified.py \
        --model_name $MODEL \
        --role_name $role \
        --tmpr 0.7
    sleep 2  # Avoid API limits
done

echo "✅ Batch assessment complete!"
EOF

chmod +x batch_assess.sh
./batch_assess.sh
```

### 3. Result Visualization
```python
# Create visualization script
import matplotlib.pyplot as plt
import json

# Read evaluation results
with open('evaluation_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Extract Big Five scores
dimensions = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
scores = {dim: [] for dim in dimensions}

for result in results:
    for dim, score in result['final_adjusted_scores'].items():
        if dim in scores:
            scores[dim].append(score)

# Draw radar chart
angles = [n / float(len(dimensions)) * 2 * 3.14159 for n in range(len(dimensions))]
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)

for dim in dimensions:
    values = scores[dim]
    avg_value = sum(values) / len(values)
    # Drawing logic...

plt.title('Personality Trait Analysis', size=16, weight='bold')
plt.savefig('personality_radar.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Ollama Connection Failed
```bash
# Check Ollama service status
ollama list

# If service not started
ollama serve

# Check port
netstat -an | grep 11434
```

#### 2. Model Download Failed
```bash
# Manually download model
ollama pull qwen3:8b

# Check model list
ollama list

# Delete corrupted model and re-download
ollama rm qwen3:8b
ollama pull qwen3:8b
```

#### 3. API Key Error
```bash
# Check environment variables
echo $DASHSCOPE_API_KEY
echo $ANTHROPIC_API_KEY

# Test API connection
python -c "
import requests
response = requests.get('https://dashscope.aliyuncs.com/api/v1/models',
    headers={'Authorization': f'Bearer {os.environ.get(\"DASHSCOPE_API_KEY\")}'})
print('API status code:', response.status_code)
"
```

#### 4. Insufficient Memory
```bash
# Monitor memory usage
htop  # Linux/macOS
tasklist  # Windows

# Reduce concurrency
export OLLAMA_MAX_LOADED_MODELS=1

# Use smaller models
ollama pull qwen3:1.8b  # 1.8B parameter version
```

#### 5. Relative Import Error
```bash
# Ensure running in correct directory
cd production_pipelines/local_batch_production/single_report_pipeline
python -m transparent_pipeline

# Or use PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python your_script.py
```

## 📖 Extended Learning

### Official Documentation
- **Project URL**: https://github.com/ptreezh/AgentPsyAssessment
- **System Separation Guide**: `README_SYSTEM_SEPARATION.md`
- **Assessment System Documentation**: `llm_assessment/README.md`
- **Evaluation System Documentation**: `production_pipelines/local_batch_production/single_report_pipeline/README.md`

### Technical Documentation
- **Adaptive Consensus Algorithm**: `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py`
- **API Configuration**: `CLAUDE.md`
- **Batch Processing**: `production_pipelines/local_batch_production/cli.py`

### Community Resources
- **Issues**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Discussions**: https://github.com/ptreezh/AgentPsyAssessment/discussions
- **Wiki**: https://github.com/ptreezh/AgentPsyAssessment/wiki

## 🎉 Congratulations!

You have successfully deployed the AgentPsyAssessment system!

🔥 **Next Steps Recommendations**:
1. Try running example scripts
2. Explore different role configurations
3. Use cloud models for more accurate evaluation
4. Check generated detailed reports

If you have questions, please check the troubleshooting section or submit an Issue!