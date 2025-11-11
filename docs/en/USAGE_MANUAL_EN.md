# 📖 AgentPsyAssessment Usage Manual

## 🎯 Quick Start

### 1️⃣ Download Project
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2️⃣ Install Ollama (Local Models)
```bash
# Windows
choco install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Start service
ollama serve

# Download models (new terminal)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
```

### 3️⃣ Configure API Keys (Cloud Models)
```bash
# Alibaba Cloud Qwen
export DASHSCOPE_API_KEY=sk-your-api-key

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-api-key

# OpenAI GPT
export OPENAI_API_KEY=sk-openai-key
```

## 🚀 Core Usage Workflow

### Step 1: Generate Psychological Questionnaire Responses (Assessment System)
```bash
# Basic usage (local models)
python llm_assessment/run_assessment_unified.py

# Specify role
python llm_assessment/run_assessment_unified.py --role_name enfj

# Use Chinese questionnaire
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

### Step 2: Scientific Scoring Analysis (Evaluation System)
```python
# Create evaluate.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

# Initialize evaluation system
pipeline = TransparentPipeline(use_cloud=True)  # Cloud models + adaptive consensus
parser = InputParser()

# Parse and evaluate
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Score: {result['final_adjusted_scores']}")
print(f"🎯 Reliability: {result['confidence_metrics']['overall_reliability']:.3f}")
```

Run evaluation:
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../evaluate.py
```

## 📋 Common Commands Quick Reference

### Local Model Assessment
```bash
# Generate responses
python llm_assessment/run_assessment_unified.py --model_name qwen3:8b --role_name enfj

# Batch role assessment
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
```

### Cloud Model Assessment
```bash
# Set cloud models
export PROVIDER=cloud

# Use cloud models to generate responses
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj

# Run end-to-end test
python test_end_to_end_complete.py
```

### Batch Processing
```bash
# Batch analyze existing results
python production_pipelines/local_batch_production/cli.py analyze --input results/

# Performance test
python adaptive_consensus_performance_test.py

# Integration test
python test_adaptive_consensus_integration.py
```

## 🔧 Configuration Files

### Model Configuration: `llm_assessment/config/ollama_config.json`
```json
{
  "models": {
    "qwen3:8b": {"provider": "ollama", "temperature": 0.7},
    "deepseek-r1:8b": {"provider": "ollama", "temperature": 0.7}
  }
}
```

### Role Configuration: `llm_assessment/roles/enfj.json`
```json
{
  "name": "ENFJ - Protagonist",
  "description": "Warm, idealistic, empathetic",
  "traits": {"extraversion": 0.7, "intuition": 0.8}
}
```

## 📊 Result Interpretation

### Evaluation Output Example
```json
{
  "final_adjusted_scores": {
    "openness": 4.2,
    "conscientiousness": 3.8,
    "extraversion": 2.9,
    "agreeableness": 4.1,
    "neuroticism": 2.3
  },
  "confidence_metrics": {
    "overall_reliability": 0.856,
    "consensus_method": "minor_consensus",
    "quality_metrics": {
      "consensus_strength": 0.823,
      "agreement_level": "high"
    }
  }
}
```

### Reliability Metric Guide
- **0.8-1.0**: High reliability, results trustworthy
- **0.6-0.8**: Medium reliability, reference use
- **0.0-0.6**: Low reliability, recommend re-evaluation

## 🆘 Troubleshooting

### Ollama Issues
```bash
# Check service
ollama list

# Restart
ollama serve

# Check port
netstat -an | grep 11434
```

### API Issues
```bash
# Check keys
echo $DASHSCOPE_API_KEY

# Test connection
python -c "import requests; print('API OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'API Failed')"
```

### Import Errors
```bash
# Correct working directory
cd production_pipelines/local_batch_production/single_report_pipeline

# Or set Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 Extended Features

### 1. Custom Roles
Create `llm_assessment/roles/custom.json`:
```json
{
  "name": "Custom Role",
  "description": "Your role description",
  "traits": {"extraversion": 0.5, "openness": 0.6}
}
```

### 2. Batch Processing Scripts
```bash
# Create batch script
cat > batch_run.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj")
for role in "${ROLES[@]}"; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
EOF

chmod +x batch_run.sh
./batch_run.sh
```

### 3. Result Visualization
```python
import matplotlib.pyplot as plt
import json

# Read results
with open('results/evaluation_result.json') as f:
    data = json.load(f)

# Draw Big Five personality radar chart
# ... plotting code ...

plt.savefig('personality_profile.png')
```

## 🎯 Best Practices

### 1. Choose Appropriate Models
- **Beginners**: Use local Ollama models
- **Professional**: Use cloud GPT-4/Claude-3.5
- **Research**: Use multi-model evaluation with adaptive consensus

### 2. Role Selection Guidelines
- **ENFJ**: Suitable for consulting, education scenarios
- **INTJ**: Suitable for analysis, strategy scenarios
- **ESTP**: Suitable for practice, operations scenarios
- **ISTJ**: Suitable for management, execution scenarios

### 3. Reliability Optimization
- Use cloud models to improve accuracy
- Enable adaptive consensus algorithm
- Set appropriate temperature (0.3-0.7)
- Take average of multiple evaluations

## 📞 Technical Support

- **Project URL**: https://github.com/ptreezh/AgentPsyAssessment
- **Issue Feedback**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **System Separation Guide**: `README_SYSTEM_SEPARATION.md`

---
🎉 You can now start using AgentPsyAssessment for professional psychological assessment!