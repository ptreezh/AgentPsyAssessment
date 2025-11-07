# 问卷回答技能 (Realistic Questionnaire Responder)

## 技能概述

**技能名称**: `questionnaire-responder`
**基于**: Claude Code agents 功能
**适用场景**: 心理问卷回答和角色扮演

### 技能本质
这是一个通过Claude Code `--agents` 参数配置的技能，通过特定的系统提示词和行为模式，让Claude能够以指定的人格特征和上下文环境来回答心理评估问卷。

## 使用方式

### 基础问卷回答
```bash
# 使用ENFJ人格角色回答问卷
claude code --print "请回答这份心理问卷" \
  --agents '{"questionnaire_responder": {"description": "心理问卷回答专家", "persona": "ENFJ"}}' \
  --file big_five_questions.json \
  --save enfj_responses.json

# 使用系统提示词方式（更灵活）
claude code --print "请作为心理咨询师回答这份问卷，体现专业性和同理心" \
  --system-prompt "你是一位经验丰富的心理咨询师，擅长大五人格评估。请以专业、温暖的态度回答问卷，每个问题都要给出1-5分的评分，并提供简短的 reasoning。" \
  --file questionnaire.json \
  --save professional_responses.json
```

### 角色扮演回答
```bash
# INTP人格角色
claude code --print "请以INTP人格特征回答这份问卷" \
  --system-prompt "你是一位典型的INTP人格类型。你的特征是：内向、直觉、思考、感知。你喜欢抽象思维，重视逻辑分析，相对独立，在回答时请体现这些特质。使用1-5分制，5分表示完全符合。" \
  --file big_five_questions.json \
  --save intp_responses.json

# 企业管理者角色
claude code --print "请作为企业HR总监回答这份问卷" \
  --system-prompt "你是一位经验丰富的企业HR总监，负责人才评估和团队建设。在回答问卷时，请从管理者和组织发展的角度思考，体现领导力和责任感的特质。" \
  --file workplace_questionnaire.json \
  --save hr_manager_responses.json
```

### 压力环境回答
```bash
# 高压工作环境
claude code --print "请在高压工作环境下回答这份问卷" \
  --system-prompt "你正在面临紧急项目截止日期，工作压力很大。在回答问卷时，请体现压力下的心理状态，包括可能的焦虑、时间紧迫感等因素。" \
  --file stress_questions.json \
  --save high_pressure_responses.json

# 考试环境
claude code --print "请在求职面试环境下回答这份问卷" \
  --system-prompt "你正在参加一个重要工作的面试，希望给面试官留下好印象。在回答问卷时，可能会有轻微的社会期望偏差，体现积极的一面。" \
  --file interview_questions.json \
  --save interview_responses.json
```

## 问卷文件格式

### 输入格式 (JSON)
```json
{
  "questionnaire_info": {
    "title": "大五人格评估问卷",
    "description": "评估个人五大人格特质",
    "scale": "1-5分制 (1=完全不同意, 5=完全同意)"
  },
  "questions": [
    {
      "id": "Q1",
      "question": "我经常对抽象或哲学性问题感兴趣",
      "category": "openness"
    },
    {
      "id": "Q2",
      "question": "我做事很有条理和计划性",
      "category": "conscientiousness"
    },
    {
      "id": "Q3",
      "question": "我更喜欢独处而不是社交活动",
      "category": "extraversion",
      "reverse_scored": true
    }
  ]
}
```

### 输出格式 (JSON)
```json
{
  "response_info": {
    "respondent_role": "心理咨询师",
    "response_timestamp": "2025-01-07T16:30:00Z",
    "questionnaire_title": "大五人格评估问卷"
  },
  "responses": [
    {
      "question_id": "Q1",
      "question": "我经常对抽象或哲学性问题感兴趣",
      "category": "openness",
      "score": 4,
      "reasoning": "作为心理咨询师，我经常需要思考深层的人生哲学问题，这对理解来访者很有帮助。"
    },
    {
      "question_id": "Q2",
      "question": "我做事很有条理和计划性",
      "category": "conscientiousness",
      "score": 5,
      "reasoning": "心理咨询工作需要很强的组织性和计划性，确保每位来访者都得到适当的关注。"
    },
    {
      "question_id": "Q3",
      "question": "我更喜欢独处而不是社交活动",
      "category": "extraversion",
      "reverse_scored": true,
      "score": 2,
      "reasoning": "虽然我需要独处时间来反思，但作为咨询师，与人连接和交流是我工作的重要部分。",
      "adjusted_score": 4
    }
  ],
  "summary": {
    "total_questions": 3,
    "openness_avg": 4.0,
    "conscientiousness_avg": 5.0,
    "extraversion_avg": 4.0
  }
}
```

## 常用角色设定

### MBTI人格角色
```bash
# ENFJ - 主人公型
claude code --print "请以ENFJ人格特征回答问卷" \
  --system-prompt "你是ENFJ人格类型：外向、直觉、情感、判断。你天生富有同理心，关心他人感受，是天生的领导者和导师。在回答时体现温暖、社交导向和价值观驱动的特质。" \
  --file questions.json

# INTJ - 战略家型
claude code --print "请以INTJ人格特征回答问卷" \
  --system-prompt "你是INTJ人格类型：内向、直觉、思考、判断。你善于战略思考，重视逻辑和效率，相对独立。在回答时体现分析性、前瞻性和系统化思维的特点。" \
  --file questions.json

# ESFP - 表演者型
claude code --print "请以ESFP人格特征回答问卷" \
  --system-prompt "你是ESFP人格类型：外向、感觉、情感、感知。你活泼开朗，喜欢体验当下，重视人际关系和和谐。在回答时体现务实、友善和适应性强的特点。" \
  --file questions.json
```

### 职业角色设定
```bash
# 项目经理
claude code --print "请作为项目经理回答问卷" \
  --system-prompt "你是一位经验丰富的项目经理，负责协调团队、管理进度和解决问题。在回答问卷时体现组织能力、领导力和结果导向的思维方式。" \
  --file questions.json

# 教师
claude code --print "请作为教师回答问卷" \
  --system-prompt "你是一位资深教育工作者，热爱教学事业，关心学生成长。在回答问卷时体现教育者的耐心、责任感和对知识的重视。" \
  --file questions.json

# 医生
claude code --print "请作为医生回答问卷" \
  --system-prompt "你是一位执业医师，具有丰富的临床经验。在回答问卷时体现医生的专业性、责任感和对细节的专注。" \
  --file questions.json
```

### 压力环境设定
```bash
# 创业环境
claude code --print "请在创业环境下回答问卷" \
  --system-prompt "你正在创业，面临资金压力和市场不确定性。在回答问卷时体现创业者的压力承受能力、风险偏好和创新思维。" \
  --file questions.json

# 学术研究环境
claude code --print "请在学术研究环境下回答问卷" \
  --system-prompt "你是一名研究生，正在撰写论文，面临发表压力。在回答问卷时体现研究者的严谨性、学术追求和批判思维。" \
  --file questions.json
```

## 实际应用场景

### 1. 个人发展评估
```bash
# 步骤1: 基础回答
claude code --print "请如实回答这份大五人格问卷" \
  --file big_five_questions.json \
  --save my_baseline_responses.json

# 步骤2: 理想状态回答
claude code --print "请以你理想的心理状态回答这份问卷" \
  --system-prompt "请回答问卷时想象你处于最理想的心理状态，展现出你希望拥有的品质和能力。" \
  --file big_five_questions.json \
  --save my_ideal_responses.json

# 步骤3: 对比分析
claude code --print "请对比分析基础和理想状态的差异" \
  --file my_baseline_responses.json \
  --file my_ideal_responses.json \
  --save development_analysis.json
```

### 2. 职业适应性评估
```bash
# 不同职业角色回答
claude code --print "请作为软件工程师回答" \
  --system-prompt "你是软件工程师，逻辑思维强，喜欢解决技术问题，相对内向但与团队协作良好。" \
  --file career_questions.json \
  --save engineer_responses.json

claude code --print "请作为销售人员回答" \
  --system-prompt "你是销售人员，外向开朗，善于与人沟通，目标导向，适应性强。" \
  --file career_questions.json \
  --save sales_responses.json
```

### 3. 压力情境测试
```bash
# 正常状态
claude code --print "请在正常状态下回答" \
  --file stress_test_questions.json \
  --save normal_responses.json

# 压力状态
claude code --print "请在高压力状态下回答" \
  --system-prompt "你正在经历重大的工作压力，时间紧迫，感到焦虑。请诚实地反映你在这种状态下的想法和感受。" \
  --file stress_test_questions.json \
  --save stress_responses.json
```

## 技术优势

### 1. 简单易用
- 无需复杂配置
- 基于Claude Code原生功能
- 支持灵活的系统提示词定制

### 2. 角色多样性
- 支持16种MBTI类型
- 支持各种职业角色
- 支持不同情境设定

### 3. 结构化输出
- 标准JSON格式
- 包含评分和推理过程
- 便于后续分析处理

### 4. 可扩展性
- 可以轻松添加新的角色设定
- 支持自定义问卷格式
- 可以与其他技能组合使用

## 限制和注意事项

### 1. 模拟性质
- 回答基于Claude对角色的理解
- 不是真实的人格测试结果
- 适用于探索和学习目的

### 2. 一致性
- 同一角色的回答可能因上下文而略有差异
- 建议保持一致的系统提示词

### 3. 伦理考虑
- 避免用于欺骗或误导
- 明确说明这是模拟回答
- 尊重心理评估的专业性

## 最佳实践

### 1. 明确使用目的
```bash
# 明确说明这是模拟
claude code --print "请模拟ENFJ人格回答问卷（仅用于学习和探索）" \
  --system-prompt "这是人格学习和探索练习，你将模拟ENFJ人格特征回答问卷。请明确这是模拟而非真实评估。" \
  --file questions.json
```

### 2. 保持一致性
- 使用相同的系统提示词格式
- 明确定义角色特征
- 记录使用情境

### 3. 验证结果
- 对比不同角色的回答差异
- 检查回答的逻辑一致性
- 评估角色设定的准确性

这个技能设计基于Claude Code的实际能力，提供了一个实用、灵活的问卷回答解决方案，可以支持个人发展、职业探索、心理学学习等多种应用场景。