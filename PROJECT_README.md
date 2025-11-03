# 分段可信评估系统

## 项目概述

分段可信评估系统是一个用于对心理测评报告进行独立评估、争议解决和人格分析的工具。该系统使用多个AI评估器对测评报告的每个部分进行独立评分，解决评分争议，并最终生成可信的人格分析报告。

系统现在支持两种评估模式：
1. **分段评估模式** - 将测评报告按指定大小分段进行评估（原有功能）
2. **每题独立评估模式** - 对每道题进行独立评估（新增功能）

## 核心功能

### 1. 分段评分
- 支持将长测评报告按指定大小分段
- 每段独立评估，避免上下文长度限制
- 为每个原始测评报告创建临时目录保存分段文件

### 2. 每题独立评分（新增）
- 对每道题进行独立评估
- 确保每道题的评分基于真实的大模型调用
- 支持双模型验证提高评分信度

### 3. 多评估器机制
- 使用多个AI模型进行独立评估
- 支持云模型（如Gemini, Qwen等）和本地模型（如Ollama）
- 自动处理模型失败和回退

### 4. 争议解决
- 自动识别评分争议（评分差异大于1分）
- 多轮争议解决机制（最多3轮）
- 每轮添加2个额外评估器

### 5. 信度验证
- 计算Cronbach's Alpha系数
- 评估者间信度分析
- 确保评分可靠性

### 6. 人格分析
- 大五人格分析（开放性、尽责性、外向性、宜人性、神经质）
- MBTI类型推断
- 贝尔宾团队角色分析
- 详细人格特征描述

## 系统架构

```
分段可信评估系统
├── segmented_scoring_evaluator.py         # 主评估系统（分段评分）
├── personality_analyzer.py                 # 人格分析模块
├── report_manager.py                       # 报告管理模块
├── parameter_extraction.py                 # 参数提取模块（新增）
├── bigfive_mapping.py                     # 人格类型映射模块（新增）
├── per_question_scoring_real.py           # 每题独立评分核心实现（新增）
├── test_segmented_assessment.py           # 测试套件
├── run_batch_segmented_analysis.py        # 批量运行脚本（分段模式）
└── run_batch_per_question_analysis.py     # 批量运行脚本（每题独立模式）
```

## 安装和环境配置

### 环境要求
- Python 3.8+
- numpy（可选，用于信度计算）

### 安装步骤
```bash
pip install numpy requests
```

### 环境变量配置
```bash
# 配置OpenRouter API密钥
OPENROUTER_API_KEY = "your_openrouter_api_key"
# 配置Ollama服务地址（默认为localhost:11434）
OLLAMA_BASE_URL = "http://localhost:11434"
```

## 使用方法

### 1. 单文件评估
```python
from segmented_scoring_evaluator import SegmentedScoringEvaluator

# 创建评估器实例
evaluator = SegmentedScoringEvaluator(
    segment_size=2,      # 每段包含2道题
    use_ollama_first=True # 优先使用本地模型
)

# 评估单个文件
result = evaluator.evaluate_file_with_multiple_models(
    file_path="path/to/input.json",
    output_dir="path/to/output"
)
```

### 2. 每题独立评估（新增）
```bash
python run_batch_per_question_analysis.py --input_dir results/readonly-original --output_dir per_question_scoring_results --max_files 10 --mode per_question
```

### 3. 批量评估
#### 分段模式（原有功能）
```bash
python run_batch_segmented_analysis.py --input_dir results/readonly-original --output_dir segmented_scoring_results --max_files 10 --segment_size 2
```

#### 每题独立模式（新增功能）
```bash
python run_batch_per_question_analysis.py --input_dir results/readonly-original --output_dir per_question_scoring_results --max_files 10 --mode per_question
```

#### 2题分段模式（新增功能）
```bash
python run_batch_per_question_analysis.py --input_dir results/readonly-original --output_dir two_question_segment_results --max_files 10 --mode segmented --segment_size 2
```

### 4. 命令行参数
#### 分段评估模式
- `--input_dir`: 输入目录路径（默认: results/readonly-original）
- `--output_dir`: 输出目录路径（默认: segmented_scoring_results）
- `--max_files`: 最大处理文件数（可选）
- `--segment_size`: 每段题数（默认: 2题/段）

#### 每题独立评估模式
- `--input_dir`: 输入目录路径（默认: results/readonly-original）
- `--output_dir`: 输出目录路径（默认: per_question_scoring_results）
- `--max_files`: 最大处理文件数（可选）
- `--mode`: 评估模式（per_question 或 segmented）
- `--segment_size`: 每段题数（仅在segmented模式下使用，默认: 2题/段）

## 评估流程

### 1. 分段处理
- 将原始测评报告按指定大小分段
- 为每段创建独立的评估提示
- 保存分段文件到临时目录

### 2. 多模型评估
- 选择前3个可用模型进行评估
- 每个模型对所有分段进行独立评估
- 模型失败时自动重试（3次，每次等待20秒），失败后标记为失效

### 3. 争议解决
- 识别评分差异大于1分的争议问题
- 最多进行3轮争议解决
- 每轮添加2个额外评估器

### 4. 汇总分析
- 计算模型间一致性
- 进行信度验证
- 执行大五和MBTI人格分析

## 输出结果

### 1. 评估结果文件
- 包含所有模型的分段评分结果
- 一致性分析报告
- 信度验证结果
- 争议解决记录
- 人格分析结果

### 2. 临时分段文件
- 保存在 `output_dir/temp_segments/{filename}/`
- 每个分段保存为独立文件

### 3. 完成文件
- 原始文件移动到 `results/ok/original/`
- 评估结果保存到 `results/ok/evaluated/`

## 配置参数

### 1. 评估器参数
- `segment_size`: 分段大小（默认5题/段）
- `use_ollama_first`: 是否优先使用Ollama模型（默认False）

### 2. 争议解决参数
- `max_rounds`: 最大争议解决轮次（固定为3）
- `dispute_threshold`: 争议识别阈值（默认1）

### 3. 重试参数
- `max_retries`: 模型调用最大重试次数（默认3）
- `retry_delay`: 重试间隔（固定20秒）

## 评分标准

### 1. 分数范围
- 1分: 极低表现 - 明显缺乏该特质
- 3分: 中等表现 - 平衡或不确定
- 5分: 极高表现 - 明确具备该特质

### 2. 评分验证
- 自动验证并修正无效评分
- 2和4修正为3
- 超出范围的值修正为最接近的有效值

## 错误处理

### 1. 模型失败
- 自动重试机制（3次）
- 重试失败后将模型标记为失效
- 继续使用其他可用模型

### 2. API错误
- 云模型和本地模型自动切换
- 多服务回退机制

### 3. JSON解析错误
- 自动尝试多种解析方法
- 包含错误恢复机制

## 性能特点

- 支持大文件分段处理
- 多模型并行评估
- 高效争议解决
- 信度和一致性验证
- 临时文件管理

## 依赖关系

- Python 3.8+
- requests
- numpy（可选）
- 配置的AI模型服务（OpenRouter或Ollama）

## 维护和扩展

### 1. 添加新评估器
在 `self.models` 列表中添加新的模型配置

### 2. 调整争议解决策略
修改 `EnhancedDisputeResolutionManager` 类中的相关参数

### 3. 修改评分标准
调整 `_validate_scores` 方法中的验证逻辑

## 许可证

此项目使用MIT许可证。详情请见LICENSE文件。