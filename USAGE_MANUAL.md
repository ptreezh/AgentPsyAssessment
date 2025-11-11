# 📖 AgentPsyAssessment 使用手册

## 🎯 快速开始

### 1️⃣ 下载项目
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2️⃣ 安装 Ollama (本地模型)
```bash
# Windows
choco install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# 启动服务
ollama serve

# 下载模型 (新终端)
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
```

### 3️⃣ 配置 API 密钥 (云端模型)
```bash
# 阿里云通义千问
export DASHSCOPE_API_KEY=sk-your-api-key

# Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-api-key

# OpenAI GPT
export OPENAI_API_KEY=sk-openai-key
```

## 🚀 核心使用流程

### 第一步：生成心理问卷答卷
```bash
# 基础用法 (本地模型)
python llm_assessment/run_assessment_unified.py

# 指定角色
python llm_assessment/run_assessment_unified.py --role_name enfj

# 使用中文问卷
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

### 第二步：科学评分分析
```python
# 创建 evaluate.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser

# 初始化评估系统
pipeline = TransparentPipeline(use_cloud=True)  # 云模型 + 自适应共识算法
parser = InputParser()

# 解析并评估
questions = parser.parse_assessment_json('results/latest_assessment.json')
result = pipeline.process_single_question(questions[0], 0)

print(f"✅ 评分: {result['final_adjusted_scores']}")
print(f"🎯 可靠性: {result['confidence_metrics']['overall_reliability']:.3f}")
```

运行评估：
```bash
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../evaluate.py
```

## 📋 常用命令速查

### 本地模型评估
```bash
# 生成答卷
python llm_assessment/run_assessment_unified.py --model_name qwen3:8b --role_name enfj

# 批量角色评估
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py --role_name $role
done
```

### 云端模型评估
```bash
# 设置云模型
export PROVIDER=cloud

# 使用云模型生成答卷
python llm_assessment/run_assessment_unified.py --model_name gpt-4o --role_name enfj

# 运行端到端测试
python test_end_to_end_complete.py
```

### 批量处理
```bash
# 批量分析已有结果
python production_pipelines/local_batch_production/cli.py analyze --input results/

# 性能测试
python adaptive_consensus_performance_test.py

# 集成测试
python test_adaptive_consensus_integration.py
```

## 🔧 配置文件

### 模型配置：`llm_assessment/config/ollama_config.json`
```json
{
  "models": {
    "qwen3:8b": {"provider": "ollama", "temperature": 0.7},
    "deepseek-r1:8b": {"provider": "ollama", "temperature": 0.7}
  }
}
```

### 角色配置：`llm_assessment/roles/enfj.json`
```json
{
  "name": "ENFJ - 提倡者",
  "description": "热情、理想主义、有同理心",
  "traits": {"extraversion": 0.7, "intuition": 0.8}
}
```

## 📊 结果解读

### 评估输出示例
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

### 可靠性指标说明
- **0.8-1.0**: 高可靠性，结果可信
- **0.6-0.8**: 中等可靠性，可参考使用
- **0.0-0.6**: 低可靠性，建议重新评估

## 🆘 故障排除

### Ollama 问题
```bash
# 检查服务
ollama list

# 重新启动
ollama serve

# 检查端口
netstat -an | grep 11434
```

### API 问题
```bash
# 检查密钥
echo $DASHSCOPE_API_KEY

# 测试连接
python -c "import requests; print('API OK' if requests.get('https://dashscope.aliyuncs.com').status_code == 200 else 'API Failed')"
```

### 导入错误
```bash
# 正确的工作目录
cd production_pipelines/local_batch_production/single_report_pipeline

# 或设置 Python 路径
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 📚 扩展功能

### 1. 自定义角色
创建 `llm_assessment/roles/custom.json`：
```json
{
  "name": "自定义角色",
  "description": "您的角色描述",
  "traits": {"extraversion": 0.5, "openness": 0.6}
}
```

### 2. 批量处理脚本
```bash
# 创建批量脚本
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

### 3. 结果可视化
```python
import matplotlib.pyplot as plt
import json

# 读取结果
with open('results/evaluation_result.json') as f:
    data = json.load(f)

# 绘制大五人格雷达图
# ... 绘图代码 ...

plt.savefig('personality_profile.png')
```

## 🎯 最佳实践

### 1. 选择合适的模型
- **新手**: 使用本地 Ollama 模型
- **专业**: 使用云端 GPT-4/Claude-3.5
- **研究**: 使用自适应共识算法的多模型评估

### 2. 角色选择建议
- **ENFJ**: 适合咨询、教育场景
- **INTJ**: 适合分析、战略场景
- **ESTP**: 适合实践、操作场景
- **ISTJ**: 适合管理、执行场景

### 3. 可靠性优化
- 使用云模型提高准确性
- 启用自适应共识算法
- 设置合适的 temperature (0.3-0.7)
- 多次评估取平均值

## 📞 技术支持

- **项目地址**: https://github.com/ptreezh/AgentPsyAssessment
- **问题反馈**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **系统分离说明**: `README_SYSTEM_SEPARATION.md`

---
🎉 现在您可以开始使用 AgentPsyAssessment 进行专业的心理评估了！