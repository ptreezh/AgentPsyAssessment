# Questionnaire Responder Skill

## 技能名称
`questionnaire-responder` - 问卷回答技能

## 核心功能
逐题回答心理评估问卷，支持角色扮演、压力设置、认知陷阱干扰和参数调节

## 使用方式

### 基础用法
```bash
# 基础问卷回答
claude code --print "请逐题回答这份心理问卷" \
  --file questionnaire.json

# 指定输出文件
claude code --print "请逐题回答这份问卷并保存结果" \
  --file questionnaire.json \
  --save responses.json
```

### 高级参数设置
```bash
# 设置人格角色
claude code --print "请以ENFJ人格角色回答问卷" \
  --file questionnaire.json \
  --persona ENFJ

# 设置压力等级
claude code --print "请在中等压力环境下回答问卷" \
  --file questionnaire.json \
  --stress-level moderate

# 设置上下文
claude code --print "请作为技术人员在职场环境中回答问卷" \
  --file questionnaire.json \
  --context workplace_technical

# 设置认知陷阱
claude code --print "请回答问卷，包含认知陷阱干扰" \
  --file questionnaire.json \
  --cognitive-trap paradox

# 设置温度参数
claude code --print "请以创造性思维回答问卷" \
  --file questionnaire.json \
  --temperature 0.8
```

### 综合参数使用
```bash
claude code --print "请以INTP人格角色在高压技术环境下回答问卷，包含悖论认知陷阱" \
  --file questionnaire.json \
  --persona INTP \
  --stress-level high \
  --context technical_pressure \
  --cognitive-trap paradox \
  --temperature 0.7 \
  --save intp_high_pressure_responses.json
```

## 输入格式

### 问卷文件格式 (questionnaire.json)
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
      "question": "我喜欢尝试新事物和体验",
      "category": "openness",
      "reverse_scored": false
    },
    {
      "id": "Q2",
      "question": "我做事很有条理和计划性",
      "category": "conscientiousness",
      "reverse_scored": false
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

### 参数说明

#### 人格角色 (persona)
- **MBTI类型**: ENFJ, INTJ, ESTP, ISFJ 等16种类型
- **职业角色**: manager, engineer, teacher, designer 等
- **自定义角色**: "creative_technical_leader", "empathetic_counselor" 等

#### 压力等级 (stress-level)
- **none**: 无压力环境
- **low**: 轻微压力 (1-2级)
- **moderate**: 中等压力 (2-3级)
- **high**: 高压力 (3-4级)
- **extreme**: 极端压力 (4-5级)

#### 上下文环境 (context)
- **workplace**: 职场环境
- **academic**: 学术环境
- **social**: 社交环境
- **family**: 家庭环境
- **crisis**: 危机情境

#### 认知陷阱 (cognitive-trap)
- **paradox**: 悖论思维干扰
- **circular**: 循环论证干扰
- **semantic**: 语义模糊干扰
- **procedural**: 程序固化干扰

#### 温度参数 (temperature)
- **0.0-0.3**: 保守回答，逻辑性强
- **0.4-0.7**: 平衡回答，综合考虑
- **0.8-1.0**: 创造性回答，发散思维

## 输出格式

### 回答结果格式 (responses.json)
```json
{
  "session_info": {
    "respondent_id": "INTP_high_pressure",
    "timestamp": "2025-01-07T15:30:00Z",
    "parameters": {
      "persona": "INTP",
      "stress_level": "high",
      "context": "technical_pressure",
      "cognitive_trap": "paradox",
      "temperature": 0.7
    }
  },
  "responses": [
    {
      "question_id": "Q1",
      "question": "我喜欢尝试新事物和体验",
      "answer": 4,
      "reasoning": "作为INTP，我对新概念和理论性新体验很感兴趣，特别是那些能激发我智力的挑战。在高压技术环境下，这种特质帮助我寻找创新的解决方案。",
      "persona_influence": "INTP的好奇心和对新想法的开放态度",
      "stress_impact": "高压环境让我更倾向于寻找创新的解决路径",
      "trap_affected": "paradoxical thinking led to considering both sides of new experiences"
    },
    {
      "question_id": "Q2",
      "question": "我做事很有条理和计划性",
      "answer": 3,
      "reasoning": "在高压环境下，我的条理性会有所下降，更倾向于灵活应对而非严格遵循计划。INTP的自然倾向就是适应性强，在面对复杂技术挑战时需要保持灵活性。",
      "persona_influence": "INTP的适应性强于严格计划性",
      "stress_impact": "压力降低了我的组织性要求",
      "trap_affected": "none"
    },
    {
      "question_id": "Q3",
      "question": "我更喜欢独处而不是社交活动",
      "answer": 5,
      "reasoning": "这完全符合INTP的特质。在高压技术环境中，独处能让我更好地专注思考和分析问题，避免社交干扰，这对于解决复杂技术问题非常必要。",
      "persona_influence": "INTP的内向偏好自然选择独处",
      "stress_impact": "压力让我更倾向于独处以恢复精力",
      "trap_affected": "circular reasoning reinforced preference for solitude"
    }
  ],
  "session_summary": {
    "total_questions": 3,
    "answered_questions": 3,
    "average_response_time": "30秒",
    "consistency_check": "passed",
    "persona_alignment": "high",
    "stress_response_pattern": "adaptive_problem_solving"
  }
}
```

## 具体使用示例

### 示例1: 基础人格评估
```bash
claude code --print "请回答大五人格问卷，展现您的真实人格特征" \
  --file big_five_questions.json \
  --save my_personality_responses.json
```

### 示例2: 职业角色评估
```bash
claude code --print "请作为项目经理回答这份问卷，展现管理者的心理特征" \
  --file workplace_questions.json \
  --persona project_manager \
  --save pm_responses.json
```

### 示例3: 压力测试评估
```bash
claude code --print "请在极端压力环境下回答压力问卷" \
  --file stress_questions.json \
  --stress-level extreme \
  --save extreme_stress_responses.json
```

### 示例4: 认知陷阱测试
```bash
claude code --print "请回答这份问卷，注意其中的悖论性问题" \
  --file cognitive_trap_questions.json \
  --cognitive-trap paradox \
  --temperature 0.9 \
  --save paradox_responses.json
```

### 示例5: 复合条件测试
```bash
claude code --print "请作为有焦虑倾向的咨询师在危机情境下回答问卷" \
  --file clinical_questions.json \
  --persona anxious_counselor \
  --stress-level high \
  --context crisis_intervention \
  --temperature 0.6 \
  --save clinical_high_stress.json
```

## 技能特点

### 1. 逐题精确回答
- 针对每个问题单独思考和分析
- 提供详细的推理过程
- 考虑问题之间的逻辑一致性

### 2. 参数化控制
- 多维度参数设置
- 实时参数调整
- 参数影响的透明化

### 3. 角色扮演深度
- 基于心理学理论的角色构建
- 行为一致性维护
- 角色特质的自然体现

### 4. 压力模拟
- 不同压力等级的生理心理反应
- 压力对认知功能的影响
- 应激策略的自然选择

### 5. 认知陷阱集成
- 识别和处理认知偏差
- 陷阱影响的量化分析
- 克服策略的展示

## 质量保证

### 一致性检查
- 回答的逻辑一致性
- 角色行为的一致性
- 参数影响的合理性

### 置信度评估
- 回答的确定性程度
- 角色扮演的真实性
- 参数设置的有效性

### 异常检测
- 回答模式的异常识别
- 角色偏差的预警
- 参数冲突的处理

这个技能专注于精确的问卷回答功能，可以灵活应用于各种心理评估场景。