# 🚀 AgentPsyAssessment Quick Reference Card

## ⚡ One-Click Startup

### 🔽 Download & Install
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 🔧 Install Ollama
```bash
# Windows
choco install ollama && ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# macOS
brew install ollama && ollama serve

# Download models
ollama pull qwen3:8b deepseek-r1:8b
```

### 🔑 Set API Keys (Cloud Models)
```bash
export DASHSCOPE_API_KEY=sk-your-key
export ANTHROPIC_API_KEY=sk-ant-key
```

## 🎯 Core Commands

### 📝 Generate Responses (Assessment System)
```bash
# Basic
python llm_assessment/run_assessment_unified.py

# Specify role
python llm_assessment/run_assessment_unified.py --role_name enfj

# Cloud models
export PROVIDER=cloud
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj
```

### 📊 Scientific Scoring (Evaluation System + Adaptive Consensus Algorithm)
```python
# Create evaluation script
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

pipeline = TransparentPipeline(use_cloud=True)  # Cloud models + adaptive consensus
parser = InputParser()
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ Score: {result['final_adjusted_scores']}")
print(f"🎯 Reliability: {result['confidence_metrics']['overall_reliability']:.3f}")
```

### 🚀 Run Evaluation
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../your_script.py
```

## 📋 Available Roles

| Role | Description | Best For |
|------|-------------|----------|
| `enfj` | Protagonist | Consulting, Education |
| `intj` | Architect | Analysis, Strategy |
| `estp` | Entrepreneur | Practice, Operations |
| `istj` | Logistician | Management, Execution |
| `infp` | Mediator | Creative, Arts |
| `entj` | Commander | Leadership, Decisions |
| `estj` | Supervisor | Execution, Control |
| `isfp` | Adventurer | Flexibility, Adaptation |
| `intp` | Logician | Research, Innovation |
| `esfp` | Entertainer | Entertainment, Social |

## 🌐 Available Models

### Local Models (Ollama)
- `qwen3:8b` - Qwen 8B
- `deepseek-r1:8b` - DeepSeek R1 8B
- `mistral-nemo:latest` - Mistral Nemo
- `llama3:latest` - Llama 3

### Cloud Models
- `deepseek-v3.1:671b-cloud` - DeepSeek V3.1 (671B)
- `gpt-oss:120b-cloud` - GPT (120B)
- `qwen3-vl:235b-cloud` - Qwen VL (235B)
- `gpt-4o` - GPT-4o
- `claude-3.5-sonnet` - Claude 3.5 Sonnet

## 🔍 Result Interpretation

### Big Five Personality Dimensions
- **Openness**: Openness to new experiences
- **Conscientiousness**: Organization and self-discipline
- **Extraversion**: Social activity level
- **Agreeableness**: Cooperation and empathy
- **Neuroticism**: Emotional stability

### Reliability Metrics
- **0.8-1.0** 🟢 High reliability - Results trustworthy
- **0.6-0.8** 🟡 Medium reliability - Reference use
- **0.0-0.6** 🔴 Low reliability - Recommend re-evaluation

## ⚠️ Important Distinction

- 📝 **Assessment System**: AI generates questionnaire responses (`llm_assessment/`)
- 🎯 **Evaluation System**: Scientific scoring analysis (`transparent_pipeline.py` + `adaptive_consensus_algorithm.py`)

**Workflow**: Generate responses → Scoring analysis

## 🛠️ Troubleshooting

### Ollama Issues
```bash
ollama list          # Check models
ollama serve         # Start service
netstat -an | grep 11434  # Check port
```

### API Issues
```bash
echo $DASHSCOPE_API_KEY     # Check key
python -c "import requests; print('OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'FAIL')"
```

### Import Errors
```bash
cd production_pipelines/local_batch_production/single_report_pipeline  # Correct directory
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Set path
```

## 📞 Technical Support

- 🌐 **Project URL**: https://github.com/ptreezh/AgentPsyAssessment
- 📖 **System Separation**: `README_SYSTEM_SEPARATION.md`
- 📚 **Quick Guide**: `QUICK_START_GUIDE.md`
- 🔧 **Usage Manual**: `USAGE_MANUAL.md`

---
🎉 **Start Your Psychological Assessment Journey!**