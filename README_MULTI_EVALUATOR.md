# 多评估器独立人格分析系统使用说明

## 系统概述

本系统实现了三个本地LLM评估器（deepseek_r1、mistral、qwen3_30b）对心理测评报告的独立分析和对比评估。每个评估器独立分析所有数据，最终提供评估器间结果对比和一致性分析。

## 系统架构

### 数据流
```
原始报告 → 格式转换 → 报告精简 → 分段处理 → 独立评估 → 结果对比 → 汇总分析
```

### 评估器工作流程
每个评估器独立执行：
1. 接收相同的问题分段
2. 对每个问题进行Big Five评分 (1-10分制)
3. 累积所有问题分数得到最终Big Five分数
4. 基于Big Five分数转换为MBTI类型
5. 输出完整的分析结果

## 环境要求

### 必需模型
系统需要以下Ollama模型：
- `deepseek-r1:8b` - DeepSeek R1 8B参数版本
- `mistral-nemo:latest` - Mistral NeMo 高性能推理模型
- `qwen3:30b-a3b` - 阿里云通义千问3 30B参数版本

### 检查模型可用性
```bash
ollama list
```

### 下载缺失模型
```bash
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull qwen3:30b-a3b
```

## 使用方法

### 1. 基本运行
```bash
python comprehensive_batch_analysis.py <输入目录> <输出目录>
```

### 2. 后台运行（推荐）
```bash
nohup python comprehensive_batch_analysis.py results/results results/multi_evaluator_analysis > analysis.log 2>&1 &
```

### 3. 监控进度
```bash
tail -f analysis.log
```

## 配置说明

### 配置文件位置
`config/ollama_config.json`

### 配置参数
```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "timeout": 120,
    "models": {
      "deepseek_r1": {
        "name": "deepseek-r1:8b",
        "temperature": 0.1,
        "max_tokens": 1024
      },
      "mistral": {
        "name": "mistral-nemo:latest",
        "temperature": 0.1,
        "max_tokens": 1024
      },
      "qwen3_30b": {
        "name": "qwen3:30b-a3b",
        "temperature": 0.1,
        "max_tokens": 1024
      }
    }
  }
}
```

## 输出结果

### 文件结构
```
results/multi_evaluator_analysis/
├── summary_report.json          # 汇总报告
├── individual_results/          # 个人结果目录
│   ├── file1_analysis.json
│   └── file2_analysis.json
└── comparison_analysis/         # 对比分析目录
    ├── mbti_consensus.json
    ├── big_five_comparison.json
    └── evaluator_performance.json
```

### 结果格式
```json
{
  "source_file": "文件名",
  "analysis_time": "时间戳",
  "segment_count": "分段数",
  "question_count": "问题总数",
  "evaluator_results": {
    "evaluator_name": {
      "final_scores": {
        "big_five": {...},
        "mbti": {...}
      }
    }
  },
  "comparison_analysis": {
    "mbti_comparison": {...},
    "big_five_comparison": {...},
    "consensus_analysis": {...}
  }
}
```

## 性能指标

### 预期性能
- **成功率**: ≥95%的文件能被所有评估器成功分析
- **一致性**: MBTI类型评估器间一致性≥70%
- **性能**: 每个文件处理时间≤10分钟
- **准确性**: Big Five分数合理性验证

### 分段处理
- **最大分段大小**: 50KB
- **每段最大问题数**: 5个
- **分段逻辑**: 按顺序分段，保持数据完整性

## 错误处理

### 评估器失败
如果某个评估器失败，系统会：
1. 记录详细的错误信息
2. 继续使用其他评估器进行分析
3. 在最终结果中标记失败的评估器

### 数据格式错误
系统会严格验证输入输出格式，遇到格式错误时会：
1. 记录错误详情
2. 跳过有问题的文件
3. 继续处理下一个文件

## 故障排除

### 常见问题

#### 1. 模型未找到错误
```
API请求失败: 404 - {"error":"model \"xxx\" not found, try pulling it first"}
```
**解决方案**: 使用 `ollama pull` 命令下载相应的模型

#### 2. 超时错误
```
API请求失败: 408 - Request timeout
```
**解决方案**:
- 检查网络连接
- 增加配置中的timeout值
- 确保Ollama服务正常运行

#### 3. 内存不足
```
CUDA out of memory
```
**解决方案**:
- 减少并发处理的文件数量
- 使用更小的模型
- 增加系统内存

### 日志分析
系统会生成详细的日志文件，包含：
- 每个评估器的处理过程
- 错误信息和堆栈跟踪
- 性能指标和统计信息

## 测试验证

### 单元测试
```bash
python -m pytest tests/test_multi_evaluator_analysis.py -v
```

### 集成测试
```bash
python comprehensive_batch_analysis.py test_data test_output
```

## 技术支持

### 日志文件位置
- 主日志: `analysis.log`
- 错误日志: `error.log`

### 获取帮助
如需技术支持，请提供：
1. 完整的错误日志
2. 配置文件内容
3. 输入数据样本
4. 系统环境信息

## 更新日志

### v1.0.0
- 实现多评估器独立分析
- 支持分段式数据处理
- 添加评估器对比分析
- 完善错误处理机制