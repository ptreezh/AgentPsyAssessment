# Psychological Assessment Skill - Revised

## Skill Overview

**Skill Name**: `psychological-assessment`
**Type**: Analysis and Processing Skill
**Author**: ptreezh <3061176@qq.com>
**License**: MIT License

**Description**:
分析心理评估问卷数据，生成基于大五人格和MBTI模型的心理特征分析报告。

## Skill Interface

### Command Line Interface
```bash
# 基础心理评估分析
claude code --print "请分析这份心理评估数据" --file assessment.json

# 详细分析模式
claude code --print "生成详细的心理分析报告" --file assessment.json --mode detailed

# 多份报告批量分析
claude code --print "批量分析心理评估报告" --files *.json --output results/
```

### Input Format

#### 单份评估数据 (assessment.json)
```json
{
  "respondent_id": "user_001",
  "assessment_type": "big_five",
  "responses": [
    {"question_id": "Q1", "question": "我喜欢尝试新事物", "answer": 4},
    {"question_id": "Q2", "question": "我做事很有条理", "answer": 3}
  ],
  "context": {
    "purpose": "self_development",
    "demographics": {"age": "25-35", "occupation": "technology"}
  }
}
```

### Output Format

#### 基础分析结果
```json
{
  "analysis_id": "analysis_001",
  "respondent_id": "user_001",
  "big_five_scores": {
    "openness": 4.2,
    "conscientiousness": 3.8,
    "extraversion": 3.5,
    "agreeableness": 4.1,
    "neuroticism": 2.3
  },
  "mbti_type": "ENFJ",
  "confidence_score": 0.87,
  "key_insights": [
    "高开放性和宜人性表明创造力和合作倾向",
    "中等外向性适合团队协作环境"
  ]
}
```

## Core Capabilities

### 1. 数据验证和预处理
- 检查输入数据格式完整性
- 验证答案有效性（1-5分制）
- 处理缺失数据和异常值

### 2. 心理特征计算
- 大五人格维度得分计算
- MBTI类型推断
- 行为模式识别

### 3. 报告生成
- 生成结构化的分析报告
- 提供个性化建议
- 标注置信度和局限性

## Usage Examples

### Example 1: 基础评估分析
```bash
# 准备评估数据
cat > my_assessment.json << EOF
{
  "respondent_id": "john_doe",
  "responses": [
    {"question_id": "O1", "question": "我喜欢抽象思考", "answer": 4},
    {"question_id": "C1", "question": "我喜欢按计划行事", "answer": 3}
  ]
}
EOF

# 执行分析
claude code --print "分析这份心理评估数据" --file my_assessment.json
```

### Example 2: 详细报告生成
```bash
# 生成详细分析报告
claude code --print "生成详细的心理分析报告，包括职业建议" \
  --file assessment.json \
  --mode detailed \
  --include career_guidance
```

### Example 3: 批量处理
```bash
# 批量分析多个评估文件
claude code --print "批量分析这些心理评估，生成对比报告" \
  --files assessments/*.json \
  --output analysis_results/
```

## Technical Implementation

### Processing Pipeline
1. **Input Validation**: 验证数据格式和完整性
2. **Score Calculation**: 计算各心理维度得分
3. **Pattern Analysis**: 识别行为模式和特征
4. **Report Generation**: 生成结构化分析结果
5. **Quality Check**: 验证结果合理性和置信度

### Error Handling
- 数据格式错误：提供清晰的错误信息和修正建议
- 不完整数据：标记缺失部分，基于可用数据进行分析
- 异常模式：识别可能的回答偏差或异常行为

## Limitations

- 基于自我报告的主观评估
- 结果仅供参考，不能替代专业心理诊断
- 需要结合具体情境解读结果
- 建议定期重复评估以追踪变化

## Integration Options

### with File Processing
```bash
# 结合文件操作技能
claude code --print "读取评估文件，分析心理特征，保存结果" \
  --file "assessments/user_001.json" \
  --save-to "results/user_001_analysis.json"
```

### with Data Analysis
```bash
# 结合数据分析技能
claude code --print "分析团队心理评估数据，生成统计报告" \
  --files "team_assessments/*.json" \
  --analysis-type "team_dynamics"
```

## Best Practices

1. **Data Quality**: 确保评估数据的真实性和完整性
2. **Context Awareness**: 考虑评估的具体场景和目的
3. **Result Interpretation**: 结合专业知识解读分析结果
4. **Privacy Protection**: 妥善处理敏感个人信息
5. **Continuous Improvement**: 基于反馈优化分析算法

---

**技术实现**: 基于现有心理测量学理论的算法实现
**数据处理**: 支持JSON格式的输入输出
**扩展性**: 可与其他Claude Code技能组合使用
**可靠性**: 包含置信度评估和质量检查机制