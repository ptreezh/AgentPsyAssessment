# 快速开始指南

## 开始使用 Portable PsyAgent

本指南将帮助您快速设置并运行第一次心理评估。

### 第1步：安装

1. **安装 Python 3.7+**（如果尚未安装）
2. **克隆代码库**或下载源代码：
   ```bash
   git clone <repository-url>
   cd portable_psyagent_open_source
   ```
3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

### 第2步：设置本地模型（推荐）

本地评估无需API密钥：

1. **安装 Ollama**：
   - Windows: 从 https://ollama.ai/download 下载
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - macOS: `brew install ollama`

2. **启动 Ollama 服务**：
   ```bash
   ollama serve
   ```

3. **下载推荐模型**：
   ```bash
   ollama pull phi3:mini
   ollama pull qwen3:4b
   ```

### 第3步：运行第一次评估

1. **准备 JSON 格式的评估数据**（见下方示例）
2. **运行分析**：
   ```bash
   python shared_analysis/analyze_results.py path/to/your_assessment.json
   ```

### 第4步：查看结果

分析完成后，检查输出文件：
- `analysis_results.json` - 详细分数和分析
- `analysis_report.md` - 人类可读报告
- `logs/` 目录中的日志文件

## 示例评估数据

创建一个简单的评估文件 `my_assessment.json`：

```json
{
  "assessment_results": [
    {
      "question_id": "Q1",
      "dimension": "extraversion",
      "scenario": "在团队会议中，你被要求分享你的想法。",
      "agent_response": "我会积极参与讨论，分享我的观点，并倾听其他人的意见。",
      "evaluation_rubric": {
        "description": "评估外向性，包括社交自信和表达能力",
        "scale": {
          "1": "很少分享想法，更愿意倾听",
          "3": "有时在被提示时分享想法",
          "5": "积极分享想法并鼓励讨论"
        }
      }
    },
    {
      "question_id": "Q2", 
      "dimension": "conscientiousness",
      "scenario": "你需要完成一个重要的项目，截止日期很紧。",
      "agent_response": "我会制定详细的计划，按优先级排序任务，并确保按时完成所有工作。",
      "evaluation_rubric": {
        "description": "评估尽责性，包括组织能力和责任感",
        "scale": {
          "1": "没有计划地工作，经常错过截止日期",
          "3": "制定基本计划但有时会错过截止日期",
          "5": "制定详细计划并始终按时完成"
        }
      }
    }
  ]
}
```

## 运行不同类型的分析

### 基本人格分析
```bash
python shared_analysis/analyze_results.py my_assessment.json
```

### 仅大五分析
```bash
python shared_analysis/analyze_big5_results.py my_assessment.json
```

### 动机分析（无需API）
```bash
python shared_analysis/analyze_motivation.py my_assessment.json --debug
```

## 使用云端模型

要使用基于云端的模型，请在 `.env` 文件中配置API密钥：

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
```

然后运行：
```bash
python shared_analysis/analyze_results.py my_assessment.json --evaluators gpt claude
```

## 批量处理

分析多个文件：

```bash
# 使用独立的批量工具
python batchAnalysizeTools/batch_segmented_analysis.py batch input_directory output_directory
```

## 故障排除

### 常见问题

1. **Ollama 连接失败**：
   - 确保 `ollama serve` 正在运行
   - 在浏览器中检查 `http://localhost:11434/api/tags`

2. **模块未找到**：
   - 运行 `pip install -r requirements.txt`

3. **分析失败**：
   - 检查 `logs/` 目录中的日志文件
   - 确保输入 JSON 格式正确

### 需要帮助？

- 查看 `USER_MANUAL_ZH.md` 中的完整文档
- 查看代码库中的示例文件
- 联系：contact@agentpsy.com

## 下一步

- 探索 `llm_assessment/test_files/` 中的不同评估类型
- 使用 `llm_assessment/roles/` 中的文件尝试基于角色的测试
- 使用 `pressure_test_bank.json` 运行压力测试
- 尝试不同的模型和配置