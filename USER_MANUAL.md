# 分段可信评估系统 - 使用手册

## 目录
1. [简介](#简介)
2. [安装指南](#安装指南)
3. [快速开始](#快速开始)
4. [高级用法](#高级用法)
5. [配置选项](#配置选项)
6. [故障排除](#故障排除)
7. [常见问题](#常见问题)

## 简介

分段可信评估系统是一个专门设计用于对长篇心理测评报告进行可信评估的工具。系统通过将测评报告分段处理，使用多个AI评估器独立评分，通过争议解决机制确保评分一致性，并最终生成包含大五人格和MBTI分析的完整报告。

系统现在支持三种评估模式：
1. **分段评估模式** - 将测评报告按指定大小分段进行评估（原有功能）
2. **每题独立评估模式** - 对每道题进行独立评估（新增功能）
3. **2题分段评估模式** - 每2题为一组进行联合评估（新增功能）

### 主要特性
- **分段评估**：将长测评报告按指定大小分段，每段独立评估
- **每题独立评估**：对每道题进行独立评估，确保评分精细化
- **多评估器**：使用3个初始评估器，支持争议时额外评估器
- **争议解决**：自动识别和解决评分争议
- **信度验证**：计算Cronbach's Alpha和评估者间信度
- **人格分析**：生成大五人格、MBTI和贝尔宾团队角色分析
- **模型重试**：评估器失败时自动重试和标记失效

## 安装指南

### 系统要求
- Python 3.8 或更高版本
- 可访问的AI模型服务（如OpenRouter或Ollama）

### 安装步骤

1. 确保已安装Python 3.8+

2. 安装依赖包
```bash
pip install numpy requests
```

3. 配置环境变量（可选）
```bash
# 设置OpenRouter API密钥
export OPENROUTER_API_KEY=your_api_key_here
# 设置Ollama服务地址（如果使用非默认地址）
export OLLAMA_BASE_URL=http://localhost:11434
```

### 模型配置

系统支持以下模型：

#### 云模型（OpenRouter）
- `qwen/qwen3-235b-a22b:free` - Qwen3 235B（推荐）
- `deepseek/deepseek-r1:free` - DeepSeek R1（推荐）
- `google/gemini-2.0-flash-exp:free` - Google Gemini 2.0 Flash（推荐）
- `mistralai/mistral-small-3.2-24b-instruct:free` - Mistral Small
- `meta-llama/llama-3.3-70b-instruct:free` - Llama 3.3 70B
- `moonshotai/kimi-k2:free` - Moonshot Kimi K2

#### 本地模型（Ollama）
- `qwen3:4b` - Qwen3 4B（推荐）
- `gemma2:2b` - Gemma2 2B（推荐）
- `llama3.2:3b` - Llama3.2 3B
- `deepseek-r1:8b` - DeepSeek R1 8B

确保所需的模型已安装并可访问。

## 快速开始

### 1. 准备输入文件

将测评报告文件放置在 `results/readonly-original/` 目录中，确保文件格式为有效的JSON。

示例文件结构：
```
results/
└── readonly-original/
    ├── assessment_report_1.json
    ├── assessment_report_2.json
    └── assessment_report_3.json
```

### 2. 运行评估

#### 分段评估模式（原有功能）
```bash
# 基本用法
python run_batch_segmented_analysis.py

# 指定分段大小（每段2题）
python run_batch_segmented_analysis.py --segment_size 2

# 限制处理文件数
python run_batch_segmented_analysis.py --max_files 10
```

#### 每题独立评估模式（新增功能）
```bash
# 基本用法 - 每题独立评分
python run_batch_per_question_analysis.py --mode per_question

# 限制处理文件数
python run_batch_per_question_analysis.py --mode per_question --max_files 10
```

#### 2题分段评估模式（新增功能）
```bash
# 每2题为一组进行联合评分
python run_batch_per_question_analysis.py --mode segmented --segment_size 2

# 限制处理文件数
python run_batch_per_question_analysis.py --mode segmented --segment_size 2 --max_files 10
```

### 3. 查看结果

评估完成后，系统会生成以下结果：

#### 评估报告文件
- **位置**：`segmented_scoring_results/` 目录（分段模式）或`per_question_scoring_results/`目录（每题模式）
- **格式**：`{原始文件名}_segmented_scoring_evaluation.json`（分段模式）或`{原始文件名}_per_question_analysis.json`（每题模式）
- **内容**：
  - 模型评分结果
  - 一致性分析
  - 信度验证
  - 争议解决记录
  - 人格分析结果

#### 临时分段文件
- **位置**：`segmented_scoring_results/temp_segments/{原文件名}/`
- **格式**：`segment_001.json`, `segment_002.json` 等
- **用途**：保存每个分段的详细信息，便于复用

#### 完成文件管理
- **原始文件**：移动到 `results/ok/original/`
- **评估结果**：保存到 `results/ok/evaluated/`

## 高级用法

### 1. 自定义分段大小

分段大小影响评估精度和上下文管理：

```bash
# 小分段（每段2题）- 高精度但需更多API调用
python run_batch_segmented_analysis.py --segment_size 2

# 中分段（每段5题）- 平衡精度和效率
python run_batch_segmented_analysis.py --segment_size 5

# 大分段（每段10题）- 少调用但精度可能下降
python run_batch_segmented_analysis.py --segment_size 10
```

**推荐设置**：
- 复杂题目：每段2-3题
- 简单题目：每段5-10题

### 2. 每题独立评分模式

新的每题独立评分模式为每道题提供独立评分：

```bash
# 使用每题独立评分
python run_batch_per_question_analysis.py --mode per_question

# 使用2题分段评分
python run_batch_per_question_analysis.py --mode segmented --segment_size 2
```

### 3. 使用Python API

```python
from segmented_scoring_evaluator import SegmentedScoringEvaluator

# 创建评估器
evaluator = SegmentedScoringEvaluator(
    segment_size=2,           # 每段2题
    use_ollama_first=True     # 优先使用本地模型
)

# 评估文件
result = evaluator.evaluate_file_with_multiple_models(
    file_path="path/to/your/file.json",
    output_dir="results/output"
)

# 检查结果
if result['success']:
    print(f"一致性: {result['consistency_score']:.2f}%")
    print(f"信度: {result['reliability_score']:.2f}%")
    print(f"MBTI: {result['personality_analysis']['mbti_analysis']['mbti_type']}")
```

### 4. 模型优先级配置

```python
# 优先使用云模型
evaluator = SegmentedScoringEvaluator(use_ollama_first=False)

# 优先使用本地模型
evaluator = SegmentedScoringEvaluator(use_ollama_first=True)
```

### 5. 争议解决监控

系统会自动处理争议，您可以通过输出监控：

```
🔍 检查评估争议...
⚠️  发现 X 个争议
🔄 第 1 轮争议解决，当前有 X 个未解决问题
🤖 使用额外评估器: [model1, model2]
📊 第 1 轮后，仍有 Y 个争议
✅ 所有争议在第 N 轮后得到解决
```

## 配置选项

### 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--input_dir` | `results/readonly-original` | 输入文件目录 |
| `--output_dir` | `segmented_scoring_results` | 输出文件目录 |
| `--max_files` | 无限制 | 最大处理文件数 |
| `--segment_size` | `2` | 每段题数 |
| `--mode` | `per_question` | 评估模式（per_question或segmented） |

### Python API参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `segment_size` | `5` | 每段题数 |
| `use_ollama_first` | `False` | 是否优先使用本地模型 |
| `api_key` | 从环境变量获取 | OpenRouter API密钥 |

## 故障排除

### 1. API调用失败

**症状**：模型调用失败，显示连接错误

**解决方案**：
- 检查网络连接
- 验证API密钥是否正确设置
- 确认Ollama服务是否运行

### 2. 模型不存在

**症状**：提示模型不存在

**解决方案**：
- 检查Ollama中是否有对应模型
- 使用 `ollama list` 查看可用模型
- 使用 `ollama pull model_name` 下载模型

### 3. JSON解析错误

**症状**：解析评估结果时出错

**解决方案**：
- 检查输入文件格式是否正确
- 确保JSON文件格式有效
- 验证API返回的响应是否符合预期格式

### 4. 内存不足

**症状**：处理大文件时内存溢出

**解决方案**：
- 减小分段大小
- 降低同时处理的文件数
- 增加系统内存

### 5. 评估器被标记为失败

**症状**：特定模型被标记为失败，不再使用

**解决方案**：
- 重启相关服务（如Ollama）
- 检查模型是否正常
- 重新配置评估器列表

## 常见问题

### Q1: 为什么需要分段评估？
A: 长篇测评报告可能超过AI模型的上下文长度限制。分段评估确保每部分都在模型能力范围内，同时保持评估质量。

### Q2: 多评估器如何提高可靠性？
A: 不同评估器可能有不同偏见或错误。使用多个评估器并比较结果，可以识别异常评分，通过多数决策原则提高评分可靠性。

### Q3: 争议解决机制如何工作？
A: 
1. 系统识别评分差异大于1分的问题
2. 启动额外评估器重新评估争议问题
3. 最多进行3轮争议解决
4. 使用多数决策原则确定最终评分

### Q4: 如何理解信度和一致性指标？
A:
- **一致性(%)**: 模型间评分的一致程度，值越高表示模型意见越统一
- **信度**: 评分的可靠性，Cronbach's Alpha值越高表示评分越可信
- **阈值**: 一致性≥60%，信度≥0.8为可接受

### Q5: 临时分段文件有什么用？
A:
- 保存每个分段的详细评估信息
- 便于后续的争议解决和复用
- 提供完整的处理过程记录

### Q6: 如何处理大文件？
A: 
- 使用较小的分段大小（如2题/段）
- 确保有足够的API配额
- 考虑使用本地模型以避免API限制

### Q7: 模型失败后如何恢复？
A: 
- 系统会自动重试3次，每次等待20秒
- 失败后模型被标记为失效，不再使用
- 继续使用其他可用模型完成评估

### Q8: 如何验证结果质量？
A:
- 检查一致性百分比和信度分数
- 查看争议解决记录
- 验证大五和MBTI分析结果的合理性
- 对比不同模型的评分差异

### Q9: 每题独立评分与分段评分有何区别？
A:
- **每题独立评分**：每道题单独评估，评分更精细，但需要更多API调用
- **分段评分**：将多道题组合评估，效率更高，但评分粒度较粗
- **2题分段**：折中方案，兼顾评分精细度和效率

## 性能优化建议

1. **分段大小选择**：根据题目复杂度选择，复杂题目用小分段
2. **模型选择**：优先使用响应快、准确度高的模型
3. **并行处理**：适当控制同时处理的文件数，避免API限流
4. **缓存利用**：临时分段文件可用于结果复用和分析

## 技术支持

如遇到问题，请：
1. 检查本文档
2. 查看系统输出的错误信息
3. 检查相关日志文件
4. 联系技术支持

## 更新日志

- **v1.0.0**: 初始版本，实现分段评估、多评估器、争议解决、信度验证
- **v1.0.1**: 增加模型失败重试和标记机制
- **v1.0.2**: 添加临时分段文件保存和复用功能
- **v1.1.0**: 新增每题独立评分和2题分段评分模式，支持更精细的评估