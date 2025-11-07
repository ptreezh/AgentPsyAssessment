# Practical Psychology Skills for Claude Code

## 设计原则

基于您的需求重新设计实用的Claude Code技能，聚焦于可实现的核心功能：

### 核心工作流
1. **问卷回答技能** - AI扮演指定角色回答心理问卷
2. **结果分析技能** - AI作为心理学专家分析问卷结果
3. **报告生成技能** - 生成综合心理分析报告

---

## 技能1: psychological-questionnaire-responder

### 功能描述
让Claude Code扮演指定的人格角色，回答心理评估问卷

### 使用方式
```bash
# 基础用法：让Claude回答大五人格问卷
claude code --print "请以ENFJ人格角色回答这份心理问卷" \
  --file big_five_questionnaire.json \
  --role ENFJ

# 高级用法：指定具体的角色特征
claude code --print "请以28岁技术项目经理的角色回答这份问卷，具有高度的责任心和团队协作精神" \
  --file questionnaire.json \
  --persona "tech_project_manager"
```

### 输入格式 (questionnaire.json)
```json
{
  "questionnaire_type": "big_five",
  "questions": [
    {
      "id": "Q1",
      "question": "我喜欢尝试新事物和体验",
      "scale": "1-5 (完全不同意到完全同意)"
    },
    {
      "id": "Q2",
      "question": "我做事很有条理和计划性",
      "scale": "1-5 (完全不同意到完全同意)"
    }
  ]
}
```

### 输出格式 (responses.json)
```json
{
  "respondent_profile": {
    "persona": "ENFJ",
    "demographics": {
      "age": "28岁",
      "occupation": "技术项目经理"
    }
  },
  "responses": [
    {
      "question_id": "Q1",
      "answer": 4,
      "reasoning": "作为ENFJ，我对新体验持开放态度，特别是能帮助团队和个人的新事物"
    },
    {
      "question_id": "Q2",
      "answer": 5,
      "reasoning": "项目管理需要高度的组织性和计划性，这是我的核心优势"
    }
  ],
  "response_metadata": {
    "completion_time": "2025-01-07",
    "consistency_check": "passed"
  }
}
```

---

## 技能2: psychological-response-analyzer

### 功能描述
作为心理学专家分析问卷回答，生成专业评估

### 使用方式
```bash
# 基础分析：分析大五人格结果
claude code --print "作为心理学专家，分析这份问卷回答，提供大五人格评估" \
  --file responses.json \
  --analysis-type big_five

# 综合分析：包含多种心理模型
claude code --print "请提供全面的心理分析，包括大五人格、MBTI类型、团队角色和社交建议" \
  --file responses.json \
  --analysis comprehensive \
  --include recommendations
```

### 分析参数配置
```json
{
  "analysis_scope": "comprehensive",
  "models": ["big_five", "mbti", "belbin"],
  "focus_areas": ["personality_traits", "team_dynamics", "career_fit"],
  "expertise_level": "clinical_psychologist",
  "report_depth": "detailed"
}
```

### 输出格式 (analysis_report.json)
```json
{
  "analysis_metadata": {
    "analyst": "AI心理学专家",
    "analysis_date": "2025-01-07",
    "confidence_level": 0.85
  },
  "big_five_assessment": {
    "openness": {"score": 4.2, "level": "high", "description": "高度开放，富有创造力"},
    "conscientiousness": {"score": 4.8, "level": "very_high", "description": "极强的组织性和责任感"},
    "extraversion": {"score": 4.5, "level": "high", "description": "善于社交，自然领导者"},
    "agreeableness": {"score": 4.3, "level": "high", "description": "富有同理心，团队协作者"},
    "neuroticism": {"score": 2.1, "level": "low", "description": "情绪稳定，抗压能力强"}
  },
  "mbti_analysis": {
    "type": "ENFJ",
    "confidence": 0.87,
    "description": "主人公型：天生的领导者和导师",
    "strengths": ["同理心", "领导力", "沟通能力"],
    "development_areas": ["边界设定", "决策果断性"]
  },
  "team_roles": {
    "primary_role": "Coordinator",
    "secondary_roles": ["TeamWorker", "Resource Investigator"],
    "leadership_style": "transformational"
  },
  "recommendations": {
    "career_suggestions": ["项目管理", "人力资源", "教育培训"],
    "relationship_advice": ["保持工作生活平衡", "学会说不"],
    "personal_growth": ["发展批判性思维", "提升独立决策能力"]
  }
}
```

---

## 技能3: psychological-report-generator

### 功能描述
生成格式化的心理评估报告

### 使用方式
```bash
# 生成个人发展报告
claude code --print "基于这份心理分析，生成个人发展报告" \
  --file analysis_report.json \
  --report-type personal_development \
  --format detailed

# 生成团队适配报告
claude code --print "生成团队角色适配和协作建议报告" \
  --file analysis_report.json \
  --report-type team_fit \
  --format executive_summary
```

### 报告类型
- `personal_development` - 个人发展建议
- `career_guidance` - 职业规划指导
- `team_fit` - 团队适配分析
- `relationship_advice` - 人际关系建议
- `executive_summary` - 简要概要报告

---

## 集成使用示例

### 完整工作流
```bash
# 步骤1：生成问卷回答
claude code --print "请以ENFJ人格角色回答这份大五人格问卷" \
  --file big_five_questions.json \
  --output responses.json

# 步骤2：专业分析
claude code --print "作为心理学专家分析这份回答" \
  --file responses.json \
  --analysis comprehensive \
  --output analysis.json

# 步骤3：生成报告
claude code --print "生成个人发展报告" \
  --file analysis.json \
  --report-type personal_development \
  --output final_report.md
```

### 批量处理
```bash
# 为不同人格角色生成分析
for persona in ENFJ INTJ ESTP ISFJ; do
  claude code --print "请以${persona}人格角色回答问卷" \
    --file questionnaire.json \
    --role ${persona} \
    --output "responses_${persona}.json"

  claude code --print "分析这份${persona}角色的心理特征" \
    --file "responses_${persona}.json" \
    --analysis comprehensive \
    --output "analysis_${persona}.json"
done
```

---

## 技术实现要点

### 1. 简单直接的设计
- 每个技能专注单一功能
- 输入输出格式标准化
- 使用Claude的自然语言理解能力

### 2. 可操作性强
- 基于现有的Claude Code能力
- 无需复杂的后端服务
- 可以立即使用和测试

### 3. 扩展性好
- 可以轻松添加新的分析模型
- 支持自定义报告格式
- 便于集成到现有工作流

### 4. 专业性保障
- 提供专家角色设定
- 基于成熟的心理测量理论
- 包含置信度评估和质量检查

---

## 实际应用场景

### 1. 个人自我认知
```bash
claude code --print "我想了解自己的心理特征，请帮我分析这份问卷" \
  --file my_responses.json \
  --analysis comprehensive \
  --include actionable_advice
```

### 2. 团队建设
```bash
claude code --print "分析团队成员的心理特征，提供团队配置建议" \
  --files team_responses/*.json \
  --analysis team_dynamics \
  --output team_composition_report.md
```

### 3. 职业规划
```bash
claude code --print "基于心理分析，提供职业发展建议" \
  --file analysis_results.json \
  --focus career_planning \
  --include skill_development
```

---

这种设计更符合Claude Code的实际能力，提供了可立即使用的实用技能，而不是过度复杂的系统架构。