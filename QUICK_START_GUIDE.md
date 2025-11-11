# 🚀 AgentPsyAssessment 快速上手指南 v1.0

## 📋 目录
- [系统概述](#系统概述)
- [环境准备](#环境准备)
- [快速安装](#快速安装)
- [5分钟体验](#5分钟体验)
- [统一评估技能系统](#统一评估技能系统)
- [基本使用](#基本使用)
- [API配置](#api配置)
- [支持测评类型](#支持测评类型)
- [常见问题](#常见问题)
- [故障排除](#故障排除)

## 🎯 系统概述

AgentPsyAssessment 是一个便携式、综合性的心理评估框架，结合了多种心理测量模型（大五人格、MBTI、认知功能）与AI驱动的分析能力。

### ⚠️ 重要：评测 vs 评估系统分离

- **📝 评测系统** (`llm_assessment/`)：AI生成心理问卷答卷
- **🎯 评估系统** (`production_pipelines/`)：对答卷进行科学评分分析
- **🧠 统一技能系统** (`.claude/skills/unified-assessment-system/`)：配置驱动的评估框架

### 🆕 新功能亮点 (v1.0)
- ✨ **统一评估技能系统**：支持6种专业测评类型的配置驱动架构
- 🤖 **智能类型检测**：自动识别测评类型，无需手动配置
- 📊 **可视化报告**：交互式HTML报告与Chart.js数据图表
- 🌍 **多语言支持**：中英文双语界面和内容
- 🎭 **16种MBTI人格**：详细的人格类型分析和映射

## 🔧 环境准备

### 系统要求
- **Python**: 3.8+
- **内存**: 4GB+ (推荐8GB+)
- **存储**: 2GB+ 可用空间
- **系统**: Windows 10/11, macOS 10.15+, Linux

## ⚡ 快速安装

### 1. 克隆项目
```bash
# 使用 Git 克隆项目
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# 或直接下载 ZIP 包
# 访问：https://github.com/ptreezh/AgentPsyAssessment
# 点击 "Code" → "Download ZIP"
```

### 2. Python 环境管理
```bash
# 推荐使用虚拟环境
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# 安装依赖
pip install -r requirements.txt  # 如果存在
pip install ollama requests numpy pandas
```

### 2. 配置环境变量
```bash
# 设置提供商（本地或云端）
export PROVIDER="local"  # 或 "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 3. 验证安装
```bash
# 运行统一评估系统测试
cd .claude/skills/unified-assessment-system
python test_runner.py

# 预期输出: 🎉 ALL TESTS PASSED!
```

## 🎯 5分钟体验

### 方式一：快速测试体验
```bash
# 1. 体验问卷生成
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. 体验批量分析
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. 查看结果
ls results/
```

### 方式二：本地模型体验
```bash
# 启动Ollama (如果使用本地模型)
ollama serve

# 下载模型
ollama pull llama3.1

# 运行本地评估
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### 方式三：技能演示体验
```bash
# 运行技能演示
python skills_demo_chinese_questionnaire.py

# 查看生成的HTML报告
ls html/
```

## 🧠 统一评估技能系统

### 系统架构
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # 配置验证器
├── 🔍 assessment_detector.py        # 测评类型检测器
├── 🏗️ skill_base.py                 # 技能基础架构
├── 📝 unified_questionnaire_responder.py    # 统一问卷应答技能
├── 📊 unified_psychological_analyzer.py    # 统一心理分析技能
├── 📄 unified_report_generator.py          # 统一报告生成技能
└── 📁 configs/                       # 配置文件目录
    ├── big_five_personality.json     # 大五人格测评
    ├── citizenship_knowledge.json   # 公民知识测评
    ├── financial_professional.json  # 金融专业测评
    ├── legal_knowledge.json         # 法律知识测评
    ├── motivation_psychology.json   # 动机心理学测评
    └── political_literacy.json      # 政治素养测评
```

### 支持的测评类型
1. **大五人格测评** - OCEAN五大维度 + MBTI映射
2. **公民知识测评** - 公民权利义务、政治制度认知等
3. **金融专业测评** - 金融专业知识、风险识别能力等
4. **法律知识测评** - 法律基础知识、实务操作能力等
5. **动机心理学测评** - 成就动机、权力动机、亲和动机等
6. **政治素养测评** - 政治制度认知、批判性思维等

### 使用统一技能系统
```bash
# 测试统一评估系统
cd .claude/skills/unified-assessment-system
python test_runner.py

# 预期输出:
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

## 🌐 安装部署

### 方案一：本地部署 (推荐新手)

#### 1. 安装 Ollama
```bash
# Windows (推荐使用 Chocolatey)
choco install ollama

# Linux (使用 curl)
curl -fsSL https://ollama.ai/install.sh | sh

# macOS (使用 Homebrew)
brew install ollama
```

#### 2. 启动 Ollama 服务
```bash
# 启动 Ollama 服务
ollama serve

# 新开一个终端，下载推荐模型
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

### 方案二：云端部署 (推荐专业用户)

#### 1. 获取 API 密钥

**阿里云通义千问 (DashScope)**
```bash
# 注册：https://bailian.console.aliyun.com/
# 获取 API Key
export DASHSCOPE_API_KEY=sk-your-api-key-here
```

**Anthropic Claude**
```bash
# 注册：https://console.anthropic.com/
# 获取 API Key
export ANTHROPIC_API_KEY=sk-ant-api-key-here
```

**OpenAI GPT**
```bash
# 注册：https://platform.openai.com/
# 获取 API Key
export OPENAI_API_KEY=sk-openai-key-here
```

#### 2. 环境变量配置
```bash
# Windows (PowerShell)
$env:DASHSCOPE_API_KEY="sk-your-api-key"
$env:ANTHROPIC_API_KEY="sk-ant-api-key"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-your-api-key"
export ANTHROPIC_API_KEY="sk-ant-api-key"
export OPENAI_API_KEY="sk-openai-key"
```

## 🚀 快速使用

### 第一步：生成心理问卷答卷 (评测系统)

```bash
# 基础用法 - 使用默认模型
python llm_assessment/run_assessment_unified.py

# 指定模型和角色
python llm_assessment/run_assessment_unified.py \
    --model_name deepseek-r1:8b \
    --role_name enfj \
    --tmpr 0.7

# 使用中文问卷
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name def \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

**输出示例**：
```
🎯 AI评估完成！
模型: deepseek-r1:8b
角色: enfj
输出文件: results/assessment_result_20250108_123456.json
```

### 第二步：科学评分分析 (评估系统)

```python
# 创建评估脚本 evaluate_result.py
from production_pipelines.local_batch_production.single_report_pipeline.transparent_pipeline import TransparentPipeline
from production_pipelines.local_batch_production.single_report_pipeline.input_parser import InputParser
import json

# 初始化评估流水线 (使用云模型 + 自适应共识算法)
pipeline = TransparentPipeline(use_cloud=True)

# 解析答卷
parser = InputParser()
questions = parser.parse_assessment_json('results/assessment_result_20250108_123456.json')

# 评估第一个问题
question = questions[0]
result = pipeline.process_single_question(question, 0)

# 输出结果
print(f"✅ 评估完成！")
print(f"最终评分: {result['final_adjusted_scores']}")
print(f"整体可靠性: {result['confidence_metrics']['overall_reliability']:.3f}")
print(f"使用模型数: {len(result['models_used'])}")
print(f"共识方法: {result['confidence_metrics']['consensus_method']}")
```

运行评估：
```bash
python evaluate_result.py
```

## 🔑 API 配置详解

### 模型配置文件
编辑 `llm_assessment/config/ollama_config.json`：

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

### 云模型配置
编辑 `production_pipelines/local_batch_production/single_report_pipeline/config.yaml`：

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

## 📚 完整示例

### 示例1：完整评估流程

```bash
# 1. 生成答卷
python llm_assessment/run_assessment_unified.py \
    --model_name qwen3:8b \
    --role_name enfj \
    --tmpr 0.7

# 2. 创建评估脚本
cat > complete_evaluation.py << 'EOF'
from transparent_pipeline import TransparentPipeline
from input_parser import InputParser

# 初始化云评估系统
pipeline = TransparentPipeline(use_cloud=True)
parser = InputParser()

# 解析答卷
questions = parser.parse_assessment_json('results/latest_assessment.json')

# 批量评估
all_results = []
for i, question in enumerate(questions):
    print(f"评估问题 {i+1}/{len(questions)}: {question.get('question_id', 'Unknown')}")
    result = pipeline.process_single_question(question, i)
    all_results.append(result)

# 生成汇总报告
print("\n🎉 评估完成！")
print(f"总问题数: {len(all_results)}")
print(f"平均可靠性: {sum(r['confidence_metrics']['overall_reliability'] for r in all_results) / len(all_results):.3f}")

# 保存结果
import json
with open('evaluation_results.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
EOF

# 3. 运行评估
cd production_pipelines/local_batch_production/single_report_pipeline
python ../../../../complete_evaluation.py
```

### 示例2：批量处理多个角色

```bash
# 生成多个角色的答卷
for role in enfj intj estp istj; do
    python llm_assessment/run_assessment_unified.py \
        --model_name qwen3:8b \
        --role_name $role \
        --tmpr 0.7
    echo "✅ 完成 $role 角色评估"
done

# 批量评估
python batch_evaluation.py
```

## 🛠️ 高级功能

### 1. 自定义角色配置
编辑 `llm_assessment/roles/enfj.json`：
```json
{
  "name": "ENFJ - 提倡者",
  "description": "热情、理想主义、有同理心的人格类型",
  "traits": {
    "extraversion": 0.7,
    "intuition": 0.8,
    "feeling": 0.9,
    "judging": 0.8
  },
  "communication_style": "温暖、鼓励性、富有洞察力"
}
```

### 2. 批量处理脚本
```bash
# 创建批量脚本
cat > batch_assess.sh << 'EOF'
#!/bin/bash
ROLES=("enfj" "intj" "estp" "istj" "infp" "entj")
MODEL="qwen3:8b"

for role in "${ROLES[@]}"; do
    echo "🎯 处理角色: $role"
    python llm_assessment/run_assessment_unified.py \
        --model_name $MODEL \
        --role_name $role \
        --tmpr 0.7
    sleep 2  # 避免API限制
done

echo "✅ 批量评估完成！"
EOF

chmod +x batch_assess.sh
./batch_assess.sh
```

### 3. 结果可视化
```python
# 创建可视化脚本
import matplotlib.pyplot as plt
import json

# 读取评估结果
with open('evaluation_results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# 提取大五人格分数
dimensions = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
scores = {dim: [] for dim in dimensions}

for result in results:
    for dim, score in result['final_adjusted_scores'].items():
        if dim in scores:
            scores[dim].append(score)

# 绘制雷达图
angles = [n / float(len(dimensions)) * 2 * 3.14159 for n in range(len(dimensions))]
angles += angles[:1]

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)

for dim in dimensions:
    values = scores[dim]
    avg_value = sum(values) / len(values)
    # 绘制逻辑...

plt.title('人格特质分析', size=16, weight='bold')
plt.savefig('personality_radar.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 🔍 故障排除

### 常见问题及解决方案

#### 1. Ollama 连接失败
```bash
# 检查 Ollama 服务状态
ollama list

# 如果服务未启动
ollama serve

# 检查端口占用
netstat -an | grep 11434
```

#### 2. 模型下载失败
```bash
# 手动下载模型
ollama pull qwen3:8b

# 检查模型列表
ollama list

# 删除损坏的模型重新下载
ollama rm qwen3:8b
ollama pull qwen3:8b
```

#### 3. API 密钥错误
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY
echo $ANTHROPIC_API_KEY

# 测试 API 连接
python -c "
import requests
response = requests.get('https://dashscope.aliyuncs.com/api/v1/models',
    headers={'Authorization': f'Bearer {os.environ.get(\"DASHSCOPE_API_KEY\")}'})
print('API 状态码:', response.status_code)
"
```

#### 4. 内存不足
```bash
# 监控内存使用
htop  # Linux/macOS
tasklist  # Windows

# 减少并发数
export OLLAMA_MAX_LOADED_MODELS=1

# 使用更小的模型
ollama pull qwen3:1.8b  # 1.8B 参数版本
```

#### 5. 相对导入错误
```bash
# 确保在正确的目录运行
cd production_pipelines/local_batch_production/single_report_pipeline
python -m transparent_pipeline

# 或使用 PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python your_script.py
```

## 📖 延伸学习

### 官方文档
- **项目地址**: https://github.com/ptreezh/AgentPsyAssessment
- **系统分离说明**: `README_SYSTEM_SEPARATION.md`
- **评测系统文档**: `llm_assessment/README.md`
- **评估系统文档**: `production_pipelines/local_batch_production/single_report_pipeline/README.md`

### 技术文档
- **自适应共识算法**: `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py`
- **API配置**: `CLAUDE.md`
- **批量处理**: `production_pipelines/local_batch_production/cli.py`

### 社区资源
- **Issues**: https://github.com/ptreezh/AgentPsyAssessment/issues
- **Discussions**: https://github.com/ptreezh/AgentPsyAssessment/discussions
- **Wiki**: https://github.com/ptreezh/AgentPsyAssessment/wiki

## 🎉 恭喜！

您已经成功部署了 AgentPsyAssessment 系统！

🔥 **下一步建议**：
1. 尝试运行示例脚本
2. 探索不同的角色配置
3. 使用云端模型获得更准确的评估
4. 查看生成的详细报告

如有问题，请查看故障排除部分或提交 Issue！