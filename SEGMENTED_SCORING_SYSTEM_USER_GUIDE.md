# 独立评估器分段评分系统使用指南

## 系统概述
独立评估器分段评分系统是一个用于对原始测评报告进行可信评估分析的工具。它将大型测评报告分割成小段（每段5题），使用多个模型进行独立评估，并通过一致性检验和信度验证确保评估结果的可靠性。

## 系统要求
- Python 3.8+
- requests库
- aiohttp库（可选，用于异步处理）
- OpenRouter API密钥（可选）
- Ollama本地服务（可选）

## 安装步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd portable_psyagent
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

## 配置API密钥

### 1. OpenRouter API密钥
1. 访问 https://openrouter.ai/ 注册账户
2. 在账户设置中生成新的API密钥
3. 将API密钥设置为环境变量：
   ```bash
   # Linux/macOS
   export OPENROUTER_API_KEY="your_actual_api_key_here"
   
   # Windows
   set OPENROUTER_API_KEY=your_actual_api_key_here
   ```

### 2. Ollama本地服务
1. 下载并安装Ollama：https://ollama.ai/
2. 启动Ollama服务：
   ```bash
   ollama serve
   ```
3. 下载所需的本地模型：
   ```bash
   ollama pull qwen3:4b
   ollama pull gemma2:2b
   ollama pull llama3.2:3b
   ollama pull mistral:7b
   ```

## 使用方法

### 1. 单文件处理
```bash
python segmented_scoring_evaluator.py --input_file path/to/your/report.json --output_dir results
```

### 2. 批量处理
```bash
python run_batch_segmented_analysis.py --input_dir results/readonly-original --output_dir segmented_scoring_results --max_files 10
```

### 3. 参数说明
- `--input_file`: 输入的测评报告文件路径（单文件模式）
- `--input_dir`: 包含测评报告的输入目录（批量模式）
- `--output_dir`: 输出结果的目录
- `--max_files`: 最大处理文件数（可选，用于测试）

## 系统特性

### 1. 分段评分
- 将大型测评报告按5题一段进行分割
- 每段独立进行评估，减少上下文长度压力
- 支持大规模报告的处理

### 2. 多模型评估
- 使用多个云模型进行独立评估
- 支持本地Ollama模型作为备选
- 自动故障转移和重试机制

### 3. 一致性检验
- 计算模型间的一致性指标
- 识别评分分歧和异常值
- 提供一致性分析报告

### 4. 信度验证
- 计算Cronbach's Alpha系数
- 评估者间信度分析
- 设置信度阈值验证

### 5. 分歧处理
- 多轮争议解决机制
- 动态增加评估器
- 多数一致判定原则

## 输出结果

### 1. 评估结果文件
每个测评报告都会生成对应的评估结果文件，包含：
- 模型评估结果
- 一致性分析
- 信度指标
- 分歧处理记录

### 2. 结构化JSON格式
```json
{
  "file_info": {
    "filename": "report_name.json",
    "total_questions": 50,
    "segments_count": 10,
    "questions_per_segment": 5
  },
  "models_used": [...],
  "model_results": {...},
  "consistency_analysis": {...},
  "reliability_analysis": {...},
  "dispute_analysis": {...}
}
```

## 故障排查

### 1. API认证失败
- 检查OPENROUTER_API_KEY环境变量是否正确设置
- 确认API密钥未过期或被撤销
- 生成新的API密钥并重新设置

### 2. Ollama服务连接失败
- 确保Ollama服务正在运行：`ollama serve`
- 检查OLLAMA_BASE_URL环境变量（默认http://localhost:11434）
- 确认所需模型已下载：`ollama list`

### 3. 评估失败
- 检查输入文件格式是否正确
- 确认测评报告包含完整的评估结果数据
- 查看详细错误日志定位问题

## 最佳实践

### 1. API密钥管理
- 绝不要将API密钥硬编码在源代码中
- 使用环境变量管理敏感信息
- 定期轮换API密钥

### 2. 批量处理
- 先使用--max_files参数进行小规模测试
- 监控API调用频率和成本
- 合理安排处理时间避免超时

### 3. 结果验证
- 检查一致性指标是否满足要求
- 验证信度系数是否达到阈值
- 审核分歧处理记录

## 支持的模型

### 云模型（OpenRouter）
- google/gemini-2.0-flash-exp:free
- deepseek/deepseek-r1:free
- qwen/qwen3-235b-a22b:free
- mistralai/mistral-small-3.2-24b-instruct:free
- meta-llama/llama-3.3-70b-instruct:free
- moonshotai/kimi-k2:free

### 本地模型（Ollama）
- qwen3:4b
- gemma2:2b
- llama3.2:3b
- mistral:7b

## 联系和支持
如有问题，请联系项目维护者或提交GitHub issue。