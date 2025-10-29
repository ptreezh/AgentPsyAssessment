# 批量分析系统使用指南

## 🚀 快速开始

### 1. 查看文件统计
```bash
python ultimate_batch_analysis.py --stats
```

### 2. 快速测试 (5个文件)
```bash
python ultimate_batch_analysis.py --quick
```

### 3. 分析特定模型
```bash
# 分析deepseek模型的所有文件
python ultimate_batch_analysis.py --filter deepseek

# 分析llama3.2模型的所有文件
python ultimate_batch_analysis.py --filter llama3.2
```

### 4. 自定义分析
```bash
# 分析10个deepseek文件
python ultimate_batch_analysis.py --filter deepseek --sample 10

# 使用特定评估器
python ultimate_batch_analysis.py --filter deepseek --evaluators ollama_llama3
```

### 5. Windows用户
```cmd
start_batch_analysis.bat
```

## 📊 可用模型

| 模型 | 文件数量 | 描述 |
|------|----------|------|
| deepseek | 65 | DeepSeek R1系列 |
| orca | 96 | Orca Mini系列 |
| llama3.2 | 23 | Llama 3.2系列 |
| Yinr | 63 | Yinr模型系列 |
| wizardlm2 | 21 | WizardLM 2系列 |
| qwen2 | 21 | Qwen 2系列 |
| llama3.1 | 2 | Llama 3.1系列 |
| qwen3 | 2 | Qwen 3系列 |
| qwen2.5 | 1 | Qwen 2.5系列 |

## 🤖 可用评估器

- **ollama_llama3**: Llama 3 本地评估器
- **ollama_qwen3**: Qwen 3 本地评估器  
- **ollama_mistral**: Mistral NeMo 本地评估器

## 📁 输出文件

分析完成后，结果将保存在 `batch_analysis_results/` 目录中：

```
batch_analysis_results/
├── batch_analysis_summary.json    # JSON格式摘要
├── batch_analysis_summary.md      # Markdown格式摘要
└── [batch_name]/                  # 批次子目录
    ├── analysis_results.json       # 原始分析结果
    ├── analysis_report.md         # 人类可读报告
    └── analysis_report.html       # HTML格式报告
```

## ⚡ 性能优化

- 每个文件平均耗时：~2分钟
- 建议批量处理：10-20个文件
- 支持多评估器并行分析
- 自动错误恢复和重试机制

## 🔧 故障排除

1. **Ollama连接问题**
   ```bash
   ollama ps
   curl http://localhost:11434/api/tags
   ```

2. **内存不足**
   - 减少批量大小 `--sample 5`
   - 使用单个评估器 `--evaluators ollama_llama3`

3. **文件格式错误**
   - 检查原始文件格式
   - 手动转换：`python convert_assessment_format.py --batch`

## 📈 预计耗时

| 文件数量 | 预计时间 | 评估器数量 |
|----------|----------|------------|
| 5 | ~10分钟 | 1个 |
| 10 | ~20分钟 | 1个 |
| 20 | ~40分钟 | 1个 |
| 50 | ~1.5小时 | 1个 |
| 100 | ~3小时 | 1个 |

*注意：使用多个评估器会线性增加耗时*