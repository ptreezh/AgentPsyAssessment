# Ollama 设置指南

## 问题诊断

当前分析系统正确检测到 Ollama 评估器失败，这是因为 Ollama 服务没有运行。错误信息显示：
```
CRITICAL: No evaluators produced sufficient valid results. Analysis failed and no reports were generated.
```

## 安装 Ollama

### Windows 用户

1. **下载 Ollama**
   ```bash
   # 访问官网下载
   https://ollama.ai/download
   ```

2. **安装步骤**
   - 下载 Windows 安装程序
   - 运行安装程序
   - 安装完成后，Ollama 会自动启动

3. **验证安装**
   ```bash
   # 打开新的命令提示符
   ollama --version
   ```

### Linux 用户

1. **安装 Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **启动服务**
   ```bash
   sudo systemctl start ollama
   sudo systemctl enable ollama
   ```

3. **验证安装**
   ```bash
   ollama --version
   ```

### macOS 用户

1. **下载 Ollama**
   ```bash
   # 访问官网下载
   https://ollama.ai/download
   ```

2. **安装步骤**
   - 下载 macOS 应用程序
   - 拖拽到 Applications 文件夹
   - 启动 Ollama

3. **验证安装**
   ```bash
   ollama --version
   ```

## 下载所需模型

系统需要以下三个模型：

```bash
# 下载 Llama 3
ollama pull llama3:latest

# 下载 Qwen 3
ollama pull qwen2.5:7b

# 下载 Mistral NeMo
ollama pull mistral-nemo:latest
```

## 验证模型可用性

```bash
# 检查已安装的模型
ollama list

# 测试模型功能
ollama run llama3:latest "你好，请简单回复'测试成功'"
```

## 配置文件

系统使用 `config/ollama_config.json` 配置文件：

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "timeout": 120,
    "models": {
      "llama3": {
        "name": "llama3:latest",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Meta Llama 3 - 通用大模型"
      },
      "qwen3": {
        "name": "qwen2.5:7b",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "阿里云通义千问 - 7B参数版本"
      },
      "mistral": {
        "name": "mistral-nemo:latest",
        "temperature": 0.1,
        "max_tokens": 1024,
        "description": "Mistral NeMo - 高性能推理模型"
      }
    }
  }
}
```

## 启动分析

安装并配置完成后，重新运行分析：

```bash
# 快速测试
python ultimate_batch_analysis.py --quick --batch-name "ollama_test"

# 标准分析
python ultimate_batch_analysis.py --mode standard --batch-name "ollama_analysis"
```

## 故障排除

### 1. Ollama 服务未启动

**症状**: 连接失败错误
```bash
# Windows: 在服务中检查 Ollama 服务
services.msc

# Linux: 检查服务状态
sudo systemctl status ollama

# macOS: 检查进程
ps aux | grep ollama
```

### 2. 模型未下载

**症状**: 模型不存在错误
```bash
# 检查已安装模型
ollama list

# 重新下载模型
ollama pull llama3:latest
```

### 3. 端口冲突

**症状**: 11434 端口被占用
```bash
# 检查端口使用情况
netstat -an | grep 11434

# 更改配置文件中的端口
# 编辑 config/ollama_config.json
```

### 4. 内存不足

**症状**: 分析过程中出现内存错误
```bash
# 检查系统内存
free -h  # Linux
wmic OS get TotalVisibleMemorySize /format:value  # Windows

# 考虑使用更小的模型
ollama pull llama3:8b
```

## 性能优化

### 1. 模型选择
- **快速测试**: 使用较小的模型（llama3:8b）
- **高质量分析**: 使用较大的模型（llama3:latest）
- **中文内容**: 优先使用 qwen2.5:7b

### 2. 并发设置
```bash
# 调整 Ollama 并发数
export OLLAMA_NUM_PARALLEL=4
```

### 3. GPU 加速
```bash
# 检查 GPU 支持
ollama ps

# 设置 GPU 使用
export OLLAMA_LLM_LIBRARY="cuda"
```

## 测试脚本

运行测试脚本验证 Ollama 连接：

```bash
python test_ollama.py
```

这个脚本会测试：
- Ollama 服务连接
- 模型列表获取
- 基本生成功能

## 完成验证

成功配置后，你应该看到：
- 分析时间显著增加（真正的 LLM 调用）
- 生成的分析报告文件
- 批量分析摘要显示真实的成功率