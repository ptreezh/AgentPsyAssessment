# 云模型评估器选择 (基于上下文长度)

## 高上下文长度模型 (适合处理大型测评报告)

### 1. Google: Gemini 2.0 Flash Experimental (free)
- **上下文长度**: 1,048,576 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 极高 - 上下文长度最大，完全适合处理大型测评报告

### 2. Qwen: Qwen3 Coder 480B A35B (free)
- **上下文长度**: 262,144 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 高 - 上下文长度很大，适合处理大型测评报告

### 3. DeepSeek: DeepSeek V3.1 (free)
- **上下文长度**: 163,800 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 高 - 上下文长度较大，适合处理大型测评报告

### 4. DeepSeek: R1 0528 (free)
- **上下文长度**: 163,840 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 高 - 上下文长度较大，适合处理大型测评报告

### 5. DeepSeek: Deepseek V3 0324 (free)
- **上下文长度**: 163,840 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 高 - 上下文长度较大，适合处理大型测评报告

### 6. TNG: DeepSeek R1T2 Chimera (free)
- **上下文长度**: 163,840 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 高 - 上下文长度较大，适合处理大型测评报告

### 7. Microsoft: MAI DS R1 (free)
- **上下文长度**: 163,840 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 高 - 上下文长度较大，适合处理大型测评报告

### 8. TNG: DeepSeek R1T Chimera (free)
- **上下文长度**: 163,840 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 高 - 上下文长度较大，适合处理大型测评报告

## 中等上下文长度模型

### 1. Tongyi DeepResearch 30B A3B (free)
- **上下文长度**: 131,072 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 中等 - 上下文长度适中，可能需要分段处理

### 2. Meituan: LongCat Flash Chat (free)
- **上下文长度**: 131,072 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 中等 - 上下文长度适中，可能需要分段处理

### 3. NVIDIA: Nemotron Nano 9B V2 (free)
- **上下文长度**: 128,000 tokens
- **输入价格**: $0/1M tokens
- **输出价格**: $0/1M tokens
- **适合性**: 中等 - 上下文长度适中，可能需要分段处理

## 评估器配置建议

### 首选评估器组合 (处理大型测评报告)
1. **评估器1**: Google: Gemini 2.0 Flash Experimental (free) - 1,048,576 tokens
2. **评估器2**: Qwen: Qwen3 Coder 480B A35B (free) - 262,144 tokens
3. **评估器3**: DeepSeek: DeepSeek V3.1 (free) - 163,800 tokens

### 备用评估器组合
1. **评估器4**: DeepSeek: R1 0528 (free) - 163,840 tokens
2. **评估器5**: TNG: DeepSeek R1T2 Chimera (free) - 163,840 tokens

### 本地模型评估器 (Ollama系列)
1. **评估器6**: Ollama Mistral
2. **评估器7**: Ollama Llama3
3. **评估器8**: Ollama Gemma

## 实施建议
1. 优先使用云模型评估器处理大型测评报告
2. 本地模型作为补充评估器使用
3. 根据模型可用性灵活调整评估器组合
4. 确保每个评估器都能完整处理测评报告内容