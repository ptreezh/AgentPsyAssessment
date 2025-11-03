# 批量可信评估分析操作指南

## 1. 安全配置

### 1.1 环境变量设置
在运行任何脚本之前，请确保正确配置环境变量：

**Linux/macOS:**
```bash
export OPENROUTER_API_KEY="your_actual_api_key_here"
export OLLAMA_BASE_URL="http://localhost:11434"  # 如果使用Ollama
```

**Windows:**
```cmd
set OPENROUTER_API_KEY=your_actual_api_key_here
set OLLAMA_BASE_URL=http://localhost:11434
```

### 1.2 API密钥获取
1. 访问 https://openrouter.ai/ 注册并获取API密钥
2. 如果使用Ollama，请确保Ollama服务正在运行

## 2. 系统运行

### 2.1 批量处理所有原始测评报告
```bash
python run_batch_segmented_analysis.py
```

### 2.2 处理指定数量的文件
```bash
python run_batch_segmented_analysis.py --max_files 10
```

### 2.3 预览将要处理的文件
```bash
python run_batch_segmented_analysis.py --dry_run
```

## 3. 输出结果

处理结果将保存在以下目录中：
- `segmented_scoring_results/` - 详细的分析结果
- `final_batch_report.json` - 批量处理总结报告

## 4. 多级重试机制

系统包含智能的多级重试机制：
1. 首选使用OpenRouter云API
2. 如果云API失败，自动尝试Ollama本地API
3. 实施指数退避重试策略
4. 支持最多3轮争议解决

## 5. 故障排除

### 5.1 API认证失败
- 检查环境变量中的API密钥是否正确
- 确认API密钥未过期或被撤销
- 验证网络连接是否正常

### 5.2 Ollama服务不可用
- 确保Ollama服务正在运行
- 检查OLLAMA_BASE_URL环境变量
- 验证所需模型是否已下载

### 5.3 处理速度慢
- 考虑减少同时处理的文件数量
- 检查API调用频率限制
- 使用本地Ollama模型作为替代方案