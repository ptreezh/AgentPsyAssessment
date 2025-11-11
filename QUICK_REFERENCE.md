# 🚀 AgentPsyAssessment 快速参考卡片

## ⚡ 一键启动

### 🔽 下载安装
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 🔧 安装 Ollama
```bash
# Windows
choco install ollama && ollama serve

# Linux
curl -fsSL https://ollama.ai/install.sh | sh && ollama serve

# macOS
brew install ollama && ollama serve

# 下载模型
ollama pull qwen3:8b deepseek-r1:8b
```

### 🔑 设置 API (云端模型)
```bash
export DASHSCOPE_API_KEY=sk-your-key
export ANTHROPIC_API_KEY=sk-ant-key
```

## 🎯 核心命令

### 📝 生成答卷 (评测系统)
```bash
# 基础
python llm_assessment/run_assessment_unified.py

# 指定角色
python llm_assessment/run_assessment_unified.py --role_name enfj

# 云模型
export PROVIDER=cloud
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj
```

### 📊 科学评分 (评估系统 + 自适应共识算法)
```python
# 创建评估脚本
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

pipeline = TransparentPipeline(use_cloud=True)  # 云模型 + 自适应共识算法
parser = InputParser()
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ 评分: {result['final_adjusted_scores']}")
print(f"🎯 可靠性: {result['confidence_metrics']['overall_reliability']:.3f}")
```

### 🚀 运行评估
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../your_script.py
```

## 📋 可用角色

| 角色 | 描述 | 适用场景 |
|------|------|----------|
| `enfj` | 提倡者 | 咨询、教育 |
| `intj` | 建筑师 | 分析、战略 |
| `estp` | 企业家 | 实践、操作 |
| `istj` | 物流师 | 管理、执行 |
| `infp` | 调停员 | 创意、艺术 |
| `entj` | 指挥官 | 领导、决策 |
| `estj` | 监督者 | 执行、控制 |
| `isfp` | 探险家 | 灵活、适应 |
| `intp` | 逻辑学家 | 研究、创新 |
| `esfp` | 表演者 | 娱乐、社交 |

## 🌐 可用模型

### 本地模型 (Ollama)
- `qwen3:8b` - 通义千问 8B
- `deepseek-r1:8b` - DeepSeek R1 8B
- `mistral-nemo:latest` - Mistral Nemo
- `llama3:latest` - Llama 3

### 云端模型
- `deepseek-v3.1:671b-cloud` - DeepSeek V3.1 (671B)
- `gpt-oss:120b-cloud` - GPT (120B)
- `qwen3-vl:235b-cloud` - 通义千问 VL (235B)
- `gpt-4o` - GPT-4o
- `claude-3.5-sonnet` - Claude 3.5 Sonnet

## 🔍 结果解读

### 大五人格维度
- **Openness (开放性)**: 对新体验的开放程度
- **Conscientiousness (尽责性)**: 组织性和自律性
- **Extraversion (外向性)**: 社交活跃度
- **Agreeableness (宜人性)**: 合作和同理心
- **Neuroticism (神经质)**: 情绪稳定性

### 可靠性指标
- **0.8-1.0** 🟢 高可靠性 - 结果可信
- **0.6-0.8** 🟡 中等可靠性 - 可参考
- **0.0-0.6** 🔴 低可靠性 - 建议重评

## ⚠️ 重要区分

- 📝 **评测系统**: AI 生成问卷答卷 (`llm_assessment/`)
- 🎯 **评估系统**: 科学评分分析 (`transparent_pipeline.py` + `adaptive_consensus_algorithm.py`)

**工作流程**: 生成答卷 → 评分分析

## 🛠️ 故障排除

### Ollama 问题
```bash
ollama list          # 检查模型
ollama serve         # 启动服务
netstat -an | grep 11434  # 检查端口
```

### API 问题
```bash
echo $DASHSCOPE_API_KEY     # 检查密钥
python -c "import requests; print('OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'FAIL')"
```

### 导入错误
```bash
cd production_pipelines/local_batch_production/single_report_pipeline  # 正确目录
export PYTHONPATH=$PYTHONPATH:$(pwd)  # 设置路径
```

## 📞 技术支持

- 🌐 **项目地址**: https://github.com/ptreezh/AgentPsyAssessment
- 📖 **系统分离**: `README_SYSTEM_SEPARATION.md`
- 📚 **快速指南**: `QUICK_START_GUIDE.md`
- 🔧 **使用手册**: `USAGE_MANUAL.md`

---
🎉 **开始您的心理评估之旅吧！**