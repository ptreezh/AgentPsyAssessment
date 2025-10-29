# Ollama模型性能分析报告

## 本地可用模型
```
NAME                               ID              SIZE      MODIFIED
glm4:9b                            5b699761eca5    5.5 GB    3 days ago
Yinr/Smegmma:9b                    638dad6c3236    5.8 GB    2 weeks ago
nomic-embed-text:latest            0a109f422b47    274 MB    2 months ago
mistral:7b-instruct-v0.2-q5_K_M    bec2cbe92b28    5.1 GB    2 months ago
deepseek-r1:8b                     6995872bfe4c    5.2 GB    2 months ago
qwen3:8b                           500a1f067a9f    5.2 GB    2 months ago
qwen3:4b                           2bfd38a7daaf    2.6 GB    2 months ago
deepseek-coder:6.7b-instruct       ce298d984115    3.8 GB    2 months ago
mistral:instruct                   3944fe81ec14    4.1 GB    2 months ago
qwen:7b-chat                       2091ee8c8d8f    4.5 GB    2 months ago
yi:6b                              a7f031bb846f    3.5 GB    2 months ago
llama3:instruct                    365c0bd3c000    4.7 GB    2 months ago
phi3:mini                          4f2222927938    2.2 GB    2 months ago
cogito:latest                      75b508ddece1    4.9 GB    2 months ago
granite-code:3b                    becc94fe1876    2.0 GB    2 months ago
granite3.3:latest                  fd429f23b909    4.9 GB    2 months ago
phi4-mini-reasoning:latest         3ca8c2865ce9    3.2 GB    2 months ago
mistral-nemo:latest                994f3b8b7801    7.1 GB    2 months ago
llama3:latest                      365c0bd3c000    4.7 GB    2 months ago
llama3-groq-tool-use:latest        36211dad2b15    4.7 GB    3 months ago
qwen3:30b-a3b                      2ee832bc15b5    18 GB     4 months ago
gemma3:latest                      a2af6cc3eb7f    3.3 GB    5 months ago
all-minilm:latest                  1b226e2802db    45 MB     7 months ago
mxbai-embed-large:latest           468836162de7    669 MB    7 months ago
```

## 当前配置评估结果

### ✅ 工作但慢的模型
- **ollama_mistral** (mistral:instruct) - 相对稳定，约2-3分钟/段
- **ollama_qwen3_30b** (qwen3:30b-a3b) - 非常慢，约5-7分钟/段，有时超时

### ❌ 不稳定的模型
- **ollama_deepseek_r1** (deepseek-r1:8b) - 持续超时，无法正常工作

## 建议的优化配置

### 高性能配置 (推荐)
```json
{
  "evaluator_priority": ["ollama_mistral"],
  "timeout_settings": {
    "ollama_mistral": 400
  },
  "segment_settings": {
    "max_questions_per_segment": 2,
    "max_segment_size": 30000
  }
}
```

### 快速测试配置
```json
{
  "evaluator_priority": ["phi3:mini", "qwen3:4b"],
  "timeout_settings": {
    "phi3:mini": 120,
    "qwen3:4b": 180
  },
  "segment_settings": {
    "max_questions_per_segment": 3,
    "max_segment_size": 40000
  }
}
```

### 多模型配置 (如果需要多样性)
```json
{
  "evaluator_priority": ["ollama_mistral", "qwen3:8b", "llama3:instruct"],
  "timeout_settings": {
    "ollama_mistral": 400,
    "qwen3:8b": 300,
    "llama3:instruct": 350
  },
  "segment_settings": {
    "max_questions_per_segment": 2,
    "max_segment_size": 30000
  }
}
```

## 关键发现

1. **deepseek-r1:8b存在问题** - 即使优化后仍持续超时
2. **提示优化有效** - 从2776字符减少到1245字符
3. **分段策略改进** - 从17段增加到25段，每段更简单
4. **重试机制必要** - 3次重试+指数退避策略

## 推荐的下一步行动

1. **短期解决方案**: 使用仅`ollama_mistral`的配置
2. **中期优化**: 测试`phi3:mini`和`qwen3:4b`作为快速替代
3. **长期改进**: 监控模型更新，特别是`deepseek-r1`的修复