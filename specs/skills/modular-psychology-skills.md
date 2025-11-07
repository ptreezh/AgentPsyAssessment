# 模块化心理评估技能设计

## 技能分解架构

基于您的需求，将心理评估功能分解为独立的、可组合的Claude Code技能：

---

## 📋 技能1: questionnaire-responder

### 功能描述
回答各类心理评估问卷，支持指定人格角色

### 使用方式
```bash
# 基础使用
claude code --print "请回答这份大五人格问卷" \
  --file big_five_questions.json

# 指定角色回答
claude code --print "请以ENFJ人格角色回答这份问卷" \
  --file questions.json \
  --persona ENFJ

# 自定义角色特征
claude code --print "请以28岁女性产品经理的角色回答，特点：注重细节、有同理心、追求创新" \
  --file questions.json \
  --persona "creative_product_manager"
```

### 输入格式
```json
{
  "questionnaire_type": "big_five|mbti|stress_test|team_role",
  "instructions": "请基于您的人格特质回答以下问题",
  "response_format": "1-5分制，并提供简要理由"
}
```

### 输出格式
```json
{
  "respondent_profile": {
    "persona": "ENFJ",
    "response_consistency": "high"
  },
  "answers": [
    {
      "question_id": "Q1",
      "score": 4,
      "reasoning": "作为ENFJ，我..."
    }
  ]
}
```

---

## 📊 技能2: big-five-analyzer

### 功能描述
专门分析大五人格问卷结果

### 使用方式
```bash
claude code --print "作为大五人格专家，分析这份问卷回答" \
  --file responses.json \
  --analysis detailed

claude code --print "计算大五人格得分并生成报告" \
  --file responses.json \
  --include_percentiles
```

### 输出格式
```json
{
  "big_five_scores": {
    "openness": {"score": 4.2, "percentile": 85, "level": "high"},
    "conscientiousness": {"score": 3.8, "percentile": 75, "level": "moderate_high"}
  },
  "personality_summary": "开放性高，尽责性中高水平..."
}
```

---

## 🎭 技能3: mbti-analyzer

### 功能描述
分析MBTI人格类型

### 使用方式
```bash
claude code --print "基于问卷回答推断MBTI类型" \
  --file responses.json \
  --include cognitive_functions

claude code --print "分析认知功能 stack 和人格发展建议" \
  --file responses.json \
  --detailed_analysis
```

### 输出格式
```json
{
  "mbti_type": "ENFJ",
  "confidence": 0.87,
  "cognitive_stack": {
    "dominant": "Fe",
    "auxiliary": "Ni",
    "tertiary": "Se",
    "inferior": "Ti"
  }
}
```

---

## 👥 技能4: team-role-analyzer

### 功能描述
基于贝尔宾理论分析团队角色

### 使用方式
```bash
claude code --print "分析团队角色倾向和协作风格" \
  --file responses.json \
  --include conflict_analysis

claude code --print "评估团队适配性和领导潜力" \
  --file responses.json \
  --focus leadership_potential
```

---

## 🧠 技能5: stress-responder

### 功能描述
回答压力测试问卷

### 使用方式
```bash
claude code --print "请回答压力情境下的心理反应问卷" \
  --file stress_questions.json \
  --stress_level moderate

claude code --print "以高压力职场人士角色回答压力测试" \
  --file stress_questions.json \
  --persona "stressed_manager"
```

### 压力等级配置
- `mild` - 轻微压力（1-2级）
- `moderate` - 中等压力（2-3级）
- `high` - 高压力（3-4级）
- `extreme` - 极端压力（4-5级）

---

## 🔍 技能6: stress-analyzer

### 功能描述
分析压力应对能力和心理韧性

### 使用方式
```bash
claude code --print "分析压力应对模式和心理韧性" \
  --file stress_responses.json

claude code --print "评估压力耐受性并提供管理建议" \
  --file stress_responses.json \
  --include recommendations
```

### 输出格式
```json
{
  "stress_resilience": 0.78,
  "coping_patterns": ["problem_focused", "social_support"],
  "vulnerability_factors": ["perfectionism"],
  "management_strategies": ["mindfulness", "boundary_setting"]
}
```

---

## 🧩 技能7: cognitive-trap-analyzer

### 功能描述
识别和分析认知陷阱模式

### 使用方式
```bash
claude code --print "识别问卷回答中的认知陷阱" \
  --file responses.json \
  --trap_types "paradox,circular,semantic"

claude code --print "分析思维模式和认知偏差" \
  --file responses.json \
  --comprehensive_analysis
```

### 认知陷阱类型
- `paradox` - 悖论思维
- `circular` - 循环论证
- `semantic` - 语义模糊
- `procedural` - 程序固化

---

## 📈 技能8: personality-integrator

### 功能描述
整合多个心理模型的分析结果

### 使用方式
```bash
claude code --print "整合大五人格和MBTI分析结果" \
  --file big_five_analysis.json \
  --additional-file mbti_analysis.json

claude code --print "生成综合心理画像和发展建议" \
  --files analyses/*.json \
  --comprehensive_report
```

---

## 🎯 技能9: career-fit-analyzer

### 功能描述
基于心理特征分析职业适配性

### 使用方式
```bash
claude code --print "分析职业适配性和发展路径" \
  --file personality_analysis.json \
  --industry technology

claude code --print "提供具体的职业建议和发展规划" \
  --file personality_analysis.json \
  --include action_plan
```

---

## 💑 技能10: relationship-compatibility-analyzer

### 功能描述
分析人际关系适配性

### 使用方式
```bash
claude code --print "分析人际交往风格和关系适配性" \
  --file personality_analysis.json \
  --relationship_type professional

claude code --print "提供社交建议和沟通策略" \
  --file personality_analysis.json \
  --include communication_tips
```

---

## 📝 技能11: report-generator

### 功能描述
生成格化的心理评估报告

### 使用方式
```bash
claude code --print "生成个人发展报告" \
  --file analysis_results.json \
  --report_type personal_development

claude code --print "生成团队建设报告" \
  --file analysis_results.json \
  --report_type team_building \
  --format markdown
```

### 报告类型
- `personal_development` - 个人发展报告
- `team_building` - 团队建设报告
- `career_guidance` - 职业指导报告
- `executive_summary` - 管理层概要报告

---

## 🔗 技能12: questionnaire-optimizer

### 功能描述
优化问卷设计和提升评估效果

### 使用方式
```bash
claude code --print "优化问卷设计和问题顺序" \
  --file questionnaire_draft.json

claude code --print "评估问卷质量和有效性" \
  --file questionnaire.json \
  --quality_check
```

---

## 🔄 集成工作流示例

### 完整心理评估流程
```bash
# 1. 生成问卷回答
claude code --print "请以ENFJ人格角色回答大五人格问卷" \
  --file big_five_questions.json \
  --output enfj_responses.json

# 2. 分析大五人格
claude code --print "分析大五人格特征" \
  --file enfj_responses.json \
  --output big_five_analysis.json

# 3. 分析MBTI类型
claude code --print "推断MBTI类型和认知功能" \
  --file enfj_responses.json \
  --output mbti_analysis.json

# 4. 分析团队角色
claude code --print "评估团队角色倾向" \
  --file enfj_responses.json \
  --output team_role_analysis.json

# 5. 压力测试
claude code --print "以中等压力水平回答压力问卷" \
  --file stress_questions.json \
  --persona ENFJ \
  --stress_level moderate \
  --output stress_responses.json

# 6. 分析压力应对
claude code --print "分析压力应对模式" \
  --file stress_responses.json \
  --output stress_analysis.json

# 7. 整合分析
claude code --print "整合所有分析结果生成综合报告" \
  --files big_five_analysis.json mbti_analysis.json team_role_analysis.json stress_analysis.json \
  --comprehensive_report \
  --output final_report.md
```

### 团队分析流程
```bash
# 为团队成员生成角色回答
for role in leader coordinator specialist; do
  claude code --print "请以${role}角色回答团队问卷" \
    --file team_questions.json \
    --persona "${role}" \
    --output "${role}_responses.json"
done

# 分析团队整体
claude code --print "分析团队角色配置和协作动态" \
  --files *_responses.json \
  --team_dynamics \
  --output team_analysis.json

# 生成团队建议
claude code --print "提供团队建设和发展建议" \
  --file team_analysis.json \
  --actionable_recommendations \
  --output team_recommendations.md
```

---

## 技能组合策略

### 基础组合
- `questionnaire-responder` + `big-five-analyzer` = 基础人格评估

### 进阶组合
- `questionnaire-responder` + `mbti-analyzer` + `team-role-analyzer` = 全面角色分析

### 专业组合
- 所有技能组合 = 综合心理评估和发展规划

### 场景组合
- 职业规划: `big-five-analyzer` + `career-fit-analyzer` + `report-generator`
- 团队建设: `team-role-analyzer` + `relationship-compatibility-analyzer`
- 压力管理: `stress-responder` + `stress-analyzer` + `cognitive-trap-analyzer`

这种模块化设计让每个技能都有明确的职责，可以根据需要灵活组合使用。