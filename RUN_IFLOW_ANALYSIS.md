# iFlow CLI 分析results\results目录指南

## 快速开始

### 1. 单模型分析
```bash
# 使用默认模型分析所有JSON文件
python analyze_results_with_iflow.py

# 指定特定模型
python analyze_results_with_iflow.py --models deepseek-v3.2-exp

# 分析前5个文件
python analyze_results_with_iflow.py --max_files 5

# 自定义输出目录
python analyze_results_with_iflow.py --output_dir results/iflow_results
```

### 2. 多模型分析
```bash
# 使用多个模型轮流分析
python analyze_results_with_iflow.py --models deepseek-v3.2-exp qwen-long gpt-4

# 指定分段大小
python analyze_results_with_iflow.py --segment_size 3
```

### 3. 测试评估器
```bash
# 测试iFlow评估器功能
python iflow_evaluator_final.py
```

## 输出结果

分析结果将保存在 `results/iflow_analysis/` 目录下，格式为：
```
iflow_<model>_<original_filename>_<timestamp>.json
```

每个结果文件包含：
- 原始文件名
- 使用的模型
- 分段分析结果
- 最终Big5分数
- 统计信息

## 支持的模型

- `deepseek-v3.2-exp`（推荐）
- `qwen-long`
- `gpt-4`
- `claude-3.5-sonnet`
- `gemini-1.5-pro`

## 注意事项

1. **iFlow CLI必须可用** - 确保已正确安装和配置
2. **分段大小** - 默认5题一段，可根据需要调整
3. **处理时间** - 大文件可能需要较长时间
4. **错误处理** - 自动跳过失败的文件并继续处理

## 故障排除

如果遇到问题：
1. 运行 `python iflow_evaluator_final.py` 测试基本功能
2. 检查iFlow CLI是否正常工作
3. 确认模型可用性
4. 查看错误日志获取详细信息