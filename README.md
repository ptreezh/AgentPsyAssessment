# Portable PsyAgent - 便携式心理评估系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-integrated-orange.svg)](https://openrouter.ai)
[![Author](https://img.shields.io/badge/author-ptreezh-blue.svg)](https://agentpsy.com)
[![Email](https://img.shields.io/badge/email-3061176%40qq.com-green.svg)](mailto:3061176@qq.com)

**作者**: ptreezh <3061176@qq.com>
**官网**: https://agentpsy.com
**版权**: © 2025 Portable PsyAgent. All Rights Reserved.

🧠 一个专业的心理评估系统，支持大五人格、MBTI和贝尔宾团队角色的多模型评估分析。

## ✨ 主要特性

- 🔬 **多理论模型**: 支持大五人格（Big Five）、MBTI和贝尔宾（Belbin）团队角色评估
- 🤖 **多AI引擎**: 集成OpenRouter云模型和Ollama本地模型
- ⚡ **批量处理**: 高效的批量评估处理能力，支持断点续跑
- 🎯 **质量控制**: 多模型共识机制，确保评估结果可靠性
- 📊 **详细报告**: 生成专业的心理分析报告和可视化图表
- 🔒 **安全可靠**: 支持本地处理，保护数据隐私

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Ollama (可选，用于本地模型)
- OpenRouter API 密钥 (可选，用于云模型)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加您的API密钥
# OPENROUTER_API_KEY=your_openrouter_api_key_here
```

4. **验证安装**
```bash
# 测试OpenRouter集成
python test_openrouter_integration.py

# 测试本地Ollama（如果已安装）
python -c "from utils.ollama_client import OllamaClient; print('Ollama连接正常')"
```

## 🎛️ 模型配置

### OpenRouter云模型 (推荐)

支持多种顶级AI模型：

| 模型 | 描述 | 适用场景 |
|------|------|----------|
| `anthropic/claude-3.5-sonnet` | Claude 3.5 Sonnet | 🏆 高质量心理评估 |
| `openai/gpt-4o` | GPT-4o | ⚡ 快速准确分析 |
| `anthropic/claude-3-haiku` | Claude 3 Haiku | 💰 经济快速测试 |

**配置方法**：
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Ollama本地模型

支持本地运行的开源模型：

| 模型 | 描述 | 安装命令 |
|------|------|----------|
| `llama3.1` | Llama 3.1 | `ollama pull llama3.1` |
| `qwen2.5` | Qwen 2.5 | `ollama pull qwen2.5` |
| `mistral` | Mistral | `ollama pull mistral` |

**配置方法**：
```env
OLLAMA_HOST=http://localhost:11434
```

## 📖 使用方法

### 单文件评估

```python
from unified_api_client import create_unified_client

# 创建统一客户端
client = create_unified_client()

# 进行心理评估分析
messages = [
    {"role": "system", "content": "你是一个专业的心理评估师。"},
    {"role": "user", "content": "请分析这份评估结果..."}
]

# 使用OpenRouter模型
response = client.chat_completion(
    model="anthropic/claude-3.5-sonnet",
    messages=messages
)

print(response["choices"][0]["message"]["content"])
```

### 批量处理

```bash
# 使用优化批量处理器（推荐）
python optimized_batch_processor.py \
  --input-dir results/original-data \
  --output-dir results/processed \
  --enhanced

# 使用完整批量处理器
python final_batch_processor.py \
  --input-dir results/assessment-files \
  --output-dir results/batch-analysis

# 快速测试3文件版本
python quick_test_3files.py \
  --input-dir results/test-data \
  --output-dir results/quick-test
```

### 获取模型推荐

```python
from unified_api_client import create_unified_client

client = create_unified_client()

# 获取评估任务推荐模型
models = client.get_recommended_models("evaluation")
for model in models:
    print(f"{model['model']}: {model['reason']}")
```

## 📁 项目结构

```
portable_psyagent/
├── README.md                          # 项目说明
├── .env.example                       # 环境变量模板
├── requirements.txt                   # Python依赖
├── unified_api_client.py              # 统一API客户端
├── config/
│   └── models_config.json             # 模型配置文件
├── integrations/
│   └── openrouter_client.py           # OpenRouter客户端
├── utils/
│   └── ollama_client.py               # Ollama客户端
├── analysis/                          # 分析模块
│   ├── analyze_big5_results.py        # 大五人格分析
│   ├── analyze_mbti_results.py        # MBTI分析
│   └── analyze_belbin_results.py      # 贝尔宾分析
├── batch_processing/                  # 批量处理模块
│   ├── optimized_batch_processor.py   # 优化批量处理器
│   ├── final_batch_processor.py       # 完整批量处理器
│   └── quick_test_3files.py           # 快速测试处理器
└── docs/                              # 文档目录
    ├── OPENROUTER_SETUP_GUIDE.md      # OpenRouter设置指南
    └── BATCH_PROCESSOR_MANUAL.md      # 批量处理器手册
```

## 🔧 详细配置

### 统一API客户端配置

```python
from unified_api_client import UnifiedAPIClient

# 使用自定义配置文件
client = UnifiedAPIClient(config_path="path/to/your/config.json")

# 测试连接状态
connections = client.test_connection()
print(f"OpenRouter: {'✅' if connections['openrouter'] else '❌'}")
print(f"Ollama: {'✅' if connections['ollama'] else '❌'}")
```

### 成本控制

```python
# 计算API调用成本
model = "anthropic/claude-3.5-sonnet"
input_tokens = 1000
output_tokens = 500

cost = client.calculate_cost(model, input_tokens, output_tokens)
print(f"预计成本: ${cost:.6f}")
```

### 批量处理器参数

```bash
# 优化批量处理器参数
python optimized_batch_processor.py \
  --input-dir input/folder \           # 输入目录
  --output-dir output/folder \         # 输出目录
  --max-questions 50 \                 # 最大题目数
  --enhanced \                         # 启用增强模式
  --concurrent-limit 5                 # 并发限制
```

## 📊 输出结果

### 评估报告结构

```
results/
├── checkpoints/                       # 断点保存目录
├── final_evaluated/                   # 最终评估结果
│   ├── *_evaluation.json              # 单文件评估结果
│   └── *_segmented_analysis.json     # 分段分析结果
├── reports/                           # 分析报告
│   ├── big_five/                      # 大五人格报告
│   ├── mbti/                          # MBTI报告
│   └── belbin/                        # 贝尔宾报告
└── summary/                           # 汇总报告
    ├── batch_summary.json             # 批量处理汇总
    └── reliability_report.md          # 可靠性报告
```

### 报告内容

**评估结果文件** (`*_evaluation.json`):
```json
{
  "file_info": {...},
  "final_scores": {
    "openness": 0.75,
    "conscientiousness": 0.82,
    "extraversion": 0.68,
    "agreeableness": 0.79,
    "neuroticism": 0.45
  },
  "mbti_type": "INTJ",
  "belbin_roles": ["Plant", "Specialist"],
  "reliability": 0.87,
  "confidence_level": "high"
}
```

## 🔍 故障排除

### 常见问题

**Q: OpenRouter连接失败**
```bash
# 检查API密钥
python -c "import os; print('API Key存在' if os.getenv('OPENROUTER_API_KEY') else 'API Key缺失')"

# 测试连接
python test_openrouter_integration.py
```

**Q: Ollama连接失败**
```bash
# 检查Ollama服务
ollama list

# 重启Ollama服务
ollama serve
```

**Q: 批量处理中断**
```bash
# 使用断点续跑功能
python optimized_batch_processor.py \
  --input-dir input/folder \
  --output-dir output/folder \
  --resume  # 启用断点续跑
```

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试单个文件
python -c "
from batch_processing.optimized_batch_processor import OptimizedBatchProcessor
processor = OptimizedBatchProcessor()
processor.process_single_file('test_file.json')
"
```

## 📚 相关文档

- [OpenRouter设置指南](docs/OPENROUTER_SETUP_GUIDE.md)
- [批量处理器手册](docs/BATCH_PROCESSOR_MANUAL.md)
- [API参考文档](docs/API_REFERENCE.md)
- [配置文件说明](docs/CONFIGURATION.md)

## 🤝 贡献指南

我们欢迎社区贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black . && isort .
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [OpenRouter](https://openrouter.ai) - 提供统一AI模型访问接口
- [Ollama](https://ollama.ai) - 本地AI模型运行平台
- [Anthropic](https://anthropic.com) - Claude模型支持
- [OpenAI](https://openai.com) - GPT模型支持

## 📞 联系方式

- **官方网站**: https://agentpsy.com
- **项目主页**: https://github.com/ptreezh/AgentPsyAssessment
- **问题反馈**: [GitHub Issues](https://github.com/ptreezh/AgentPsyAssessment/issues)
- **作者邮箱**: ptreezh <3061176@qq.com>

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

## 🚀 路线图

### v2.0 计划功能

- [ ] Web界面支持
- [ ] 实时协作评估
- [ ] 更多心理理论模型
- [ ] 高级数据可视化
- [ ] 移动端应用
- [ ] API服务接口

### v1.5 计划功能

- [ ] 批量报告导出
- [ ] 自定义评估模板
- [ ] 数据加密存储
- [ ] 多语言支持