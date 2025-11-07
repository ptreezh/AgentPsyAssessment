# 心理分析技能 (Realistic Psychological Analyzer)

## 技能概述

**技能名称**: `psychological-analyzer`
**基于**: Claude Code 系统提示词功能
**适用场景**: 分析问卷回答，提供专业的心理特征评估和发展建议

### 技能本质
这是一个通过Claude Code的系统提示词配置的技能，让Claude能够基于心理学理论知识，对问卷回答数据进行专业的心理特征分析、人格类型推断和发展建议生成。

## 使用方式

### 基础心理分析
```bash
# 大五人格分析
claude code --print "请分析这份问卷回答的大五人格特征" \
  --system-prompt "你是一位专业的心理测量学专家。请分析这份问卷回答，计算大五人格得分（开放性、尽责性、外向性、宜人性、神经质），并提供专业的心理特征分析和发展建议。" \
  --file questionnaire_responses.json \
  --save big_five_analysis.json

# MBTI类型推断
claude code --print "请推断回答者的MBTI人格类型" \
  --system-prompt "你是一位MBTI专家。请基于问卷回答推断回答者的MBTI人格类型，包括主导功能、辅助功能等，并提供详细的类型描述和发展建议。" \
  --file questionnaire_responses.json \
  --save mbti_analysis.json
```

### 专业视角分析
```bash
# 临床心理学视角
claude code --print "请从临床心理学角度分析" \
  --system-prompt "你是临床心理学专家。请从心理健康、风险评估、治疗建议等专业角度分析这份问卷回答，识别可能的心理健康指标和风险因素。" \
  --file questionnaire_responses.json \
  --save clinical_analysis.json

# 组织心理学视角
claude code --print "请从组织心理学角度分析" \
  --system-prompt "你是组织心理学专家。请从工作适应性、团队角色、领导潜力、职业发展等角度分析这份问卷回答，为组织发展和人才管理提供专业建议。" \
  --file questionnaire_responses.json \
  --save organizational_analysis.json

# 发展心理学视角
claude code --print "请从发展心理学角度分析" \
  --system-prompt "你是发展心理学专家。请从个人成长、心理发展阶段、学习模式等角度分析这份问卷回答，提供适合的发展建议和成长策略。" \
  --file questionnaire_responses.json \
  --save developmental_analysis.json
```

### 团队角色分析
```bash
# 贝尔宾团队角色
claude code --print "请分析适合的贝尔宾团队角色" \
  --system-prompt "你是团队协作专家，熟悉贝尔宾团队角色理论。请分析回答者最适合的团队角色，包括主导角色和辅助角色，并提供团队协作建议。" \
  --file questionnaire_responses.json \
  --save team_role_analysis.json

# 领导风格分析
claude code --print "请分析领导风格和潜力" \
  --system-prompt "你是领导力发展专家。请分析回答者的领导风格、领导潜力和发展需求，为领导力发展提供具体的建议和指导。" \
  --file questionnaire_responses.json \
  --save leadership_analysis.json
```

### 综合评估
```bash
# 全面心理画像
claude code --print "请提供全面的心理评估报告" \
  --system-prompt "你是资深心理评估专家。请提供一份全面的心理评估报告，包括：1)大五人格详细分析 2)MBTI类型推断 3)团队角色建议 4)职业适配性分析 5)个人发展建议 6)潜在优势和发展领域。" \
  --file questionnaire_responses.json \
  --save comprehensive_analysis.json

# 职业发展指导
claude code --print "请提供职业发展指导" \
  --system-prompt "你是职业规划专家。请基于心理特征分析，提供详细的职业发展指导，包括：1)适合的职业领域 2)发展建议 3)技能培养重点 4)职业转换考虑 5)长期职业规划。" \
  --file questionnaire_responses.json \
  --save career_guidance.json
```

## 输入格式

### 问卷回答数据格式
```json
{
  "response_info": {
    "respondent_role": "求职者",
    "response_timestamp": "2025-01-07T16:30:00Z",
    "questionnaire_type": "big_five_personality"
  },
  "responses": [
    {
      "question_id": "Q1",
      "question": "我经常对抽象或哲学性问题感兴趣",
      "category": "openness",
      "score": 4,
      "reasoning": "我喜欢思考人生的意义和价值观问题"
    },
    {
      "question_id": "Q2",
      "question": "我做事很有条理和计划性",
      "category": "conscientiousness",
      "score": 5,
      "reasoning": "我习惯制定详细的计划和待办事项"
    },
    {
      "question_id": "Q3",
      "question": "我更喜欢独处而不是社交活动",
      "category": "extraversion",
      "score": 2,
      "reasoning": "虽然我也喜欢和朋友在一起，但更需要独处时间来充电",
      "reverse_scored": true,
      "adjusted_score": 4
    }
  ]
}
```

### 简化输入格式（1-5分制）
```json
{
  "answers": {
    "Q1": 4,  // 我经常对抽象或哲学性问题感兴趣
    "Q2": 5,  // 我做事很有条理和计划性
    "Q3": 2,  // 我更喜欢独处而不是社交活动（反向计分）
    "Q4": 3,  // 我通常能够信任他人
    "Q5": 4   // 我容易感到紧张和焦虑
  },
  "questions": {
    "Q1": "我经常对抽象或哲学性问题感兴趣",
    "Q2": "我做事很有条理和计划性",
    "Q3": "我更喜欢独处而不是社交活动",
    "Q4": "我通常能够信任他人",
    "Q5": "我容易感到紧张和焦虑"
  }
}
```

## 输出格式

### 大五人格分析报告
```json
{
  "analysis_info": {
    "analyst": "心理测量学专家",
    "analysis_date": "2025-01-07T16:45:00Z",
    "theoretical_basis": "Costa & McCrae 大五人格理论"
  },
  "big_five_results": {
    "openness": {
      "score": 4.2,
      "percentile": 85,
      "level": "high",
      "description": "高度开放，富有创造力和好奇心",
      "behavioral_indicators": [
        "喜欢抽象思维和新体验",
        "对艺术和美学有高度敏感度",
        "思维灵活，善于连接不同概念",
        "对不同的价值观持开放态度"
      ],
      "strengths": [
        "创新能力强",
        "适应变化快",
        "学习能力强",
        "思维开阔"
      ],
      "potential_challenges": [
        "可能过于理想化",
        "需要更多实践导向",
        "可能缺乏细节关注"
      ]
    },
    "conscientiousness": {
      "score": 4.8,
      "percentile": 92,
      "level": "very_high",
      "description": "高度尽责，有条理，可靠性强",
      "behavioral_indicators": [
        "做事有计划性和条理性",
        "注意细节，追求准确性",
        "按时完成任务，责任感强",
        "倾向于制定并遵守规则"
      ],
      "strengths": [
        "执行力强",
        "可靠性高",
        "自我管理好",
        "目标导向"
      ],
      "potential_challenges": [
        "可能过于严格",
        "适应性有时不足",
        "完美主义倾向"
      ]
    },
    "extraversion": {
      "score": 3.5,
      "percentile": 60,
      "level": "moderate",
      "description": "中等外向，平衡社交和独处需求",
      "behavioral_indicators": [
        "在社交场合感到舒适",
        "能够与不同类型的人交流",
        "也享受独处时间",
        "根据情境调整社交行为"
      ],
      "strengths": [
        "社交技能良好",
        "适应性灵活",
        "独立性强"
      ],
      "potential_challenges": [
        "可能在某些情境中不够主动",
        "需要明确动机才能充分表现"
      ]
    },
    "agreeableness": {
      "score": 4.0,
      "percentile": 75,
      "level": "moderate_high",
      "description": "高度友善，重视和谐关系",
      "behavioral_indicators": [
        "通常友善和乐于助人",
        "重视团队和谐与合作",
        "能够理解他人观点",
        "避免不必要的冲突"
      ],
      "strengths": [
        "人际关系良好",
        "团队合作能力强",
        "同理心强"
      ],
      "potential_challenges": [
        "可能避免必要冲突",
        "在决策中过于考虑他人感受"
      ]
    },
    "neuroticism": {
      "score": 2.8,
      "percentile": 35,
      "level": "low_moderate",
      "description": "情绪相对稳定，有一定抗压能力",
      "behavioral_indicators": [
        "大多数情况下情绪稳定",
        "能够应对日常压力",
        "在压力下仍能保持功能",
        "有良好的情绪调节能力"
      ],
      "strengths": [
        "情绪稳定性较好",
        "抗压能力强",
        "心理韧性不错"
      ],
      "potential_challenges": [
        "在极端压力下可能需要支持",
        "需要持续的情绪管理"
      ]
    }
  },
  "overall_profile": {
    "dominant_traits": ["尽责性", "开放性", "宜人性"],
    "personality_summary": "一个高度尽责、开放且友善的人，具有强烈的目标导向和学习能力，情绪相对稳定，在团队中会是可靠且富有创造力的成员。",
    "key_strengths": [
      "自我管理和执行力强",
      "创新思维和学习能力",
      "人际关系和谐",
      "情绪稳定性良好"
    ],
    "development_areas": [
      "在社交场合更加主动",
      "平衡理想与现实",
      "处理冲突的技巧"
    ]
  },
  "career_recommendations": {
    "high_fit_areas": [
      "研究与分析工作",
      "教育咨询",
      "项目管理",
      "创意产业"
    ],
    "development_suggestions": [
      "发展领导力技能",
      "提升公共演讲能力",
      "学习谈判技巧"
    ]
  }
}
```

### MBTI类型推断结果
```json
{
  "mbti_results": {
    "inferred_type": "INTJ",
    "confidence": 0.75,
    "cognitive_functions": {
      "dominant": "Ni (Introverted Intuition)",
      "auxiliary": "Te (Extraverted Thinking)",
      "tertiary": "Fi (Introverted Feeling)",
      "inferior": "Se (Extraverted Sensing)"
    },
    "type_description": "战略家型 - 内向直觉思考判断",
    "characteristics": [
      "战略性思维",
      "独立自主",
      "追求效率和逻辑",
      "重视知识和能力"
    ],
    "strengths": [
      "长期规划能力",
      "系统性思维",
      "问题分析能力",
      "独立工作能力"
    ],
    "growth_areas": [
      "人际交往技能",
      "情感表达能力",
      "适应突发变化",
      "实践动手能力"
    ]
  }
}
```

### 团队角色分析
```json
{
  "team_role_results": {
    "belbin_roles": {
      "primary_role": "Plant",
      "fit_score": 0.85,
      "description": "创新者 - 提供创新想法和解决方案",
      "strengths": [
        "创造力强",
        "善于解决复杂问题",
        "思维方式独特"
      ]
    },
    "secondary_roles": [
      {
        "role": "Specialist",
        "fit_score": 0.72,
        "description": "专家 - 提供专业知识和技能"
      },
      {
        "role": "Monitor Evaluator",
        "fit_score": 0.68,
        "description": "监控评估者 - 客观分析判断"
      }
    ]
  },
  "team_contribution": {
    "value_proposition": "在团队中主要贡献创新思维和专业分析能力",
    "best_team_composition": "与创新型、分析型团队配合良好",
    "potential_challenges": [
      "需要团队中有执行型角色来落实想法",
      "可能在过于注重完美而影响效率"
    ]
  }
}
```

## 实际应用示例

### 1. 个人发展分析流程
```bash
# 步骤1: 基础分析
claude code --print "请分析我的心理特征" \
  --system-prompt "请分析这份问卷回答，提供大五人格和MBTI的详细分析，重点关注个人发展建议。" \
  --file my_responses.json \
  --save personal_analysis.json

# 步骤2: 职业指导
claude code --print "请提供职业发展指导" \
  --system-prompt "基于心理特征分析，请提供详细的职业发展指导，包括最适合的职业领域和发展路径。" \
  --file personal_analysis.json \
  --save career_guidance.json

# 步骤3: 行动计划
claude code --print "请制定个人发展计划" \
  --system-prompt "请基于分析结果，制定一个具体的个人发展计划，包括具体的学习目标和实施步骤。" \
  --file career_guidance.json \
  --save development_plan.json
```

### 2. 团队建设应用
```bash
# 分析团队成员
for member in team_member_*.json; do
  claude code --print "请分析团队成员的心理特征" \
    --system-prompt "请分析这位团队成员的心理特征，重点关注其在团队中的角色定位和协作方式。" \
    --file "$member" \
    --save "analysis_$(basename $member)"
done

# 团队角色优化建议
claude code --print "请提供团队角色优化建议" \
  --system-prompt "基于所有团队成员的分析，请提供团队角色优化的具体建议，包括如何平衡团队技能和协作方式。" \
  --file all_team_analyses.json \
  --save team_optimization.json
```

### 3. 压力评估应用
```bash
# 正常状态分析
claude code --print "请分析正常心理状态" \
  --system-prompt "请分析这份问卷回答，评估正常心理状态下的心理特征和适应能力。" \
  --file normal_responses.json \
  --save baseline_analysis.json

# 压力状态分析
claude code --print "请分析压力状态下的心理反应" \
  --system-prompt "请分析这份在压力状态下回答的问卷，评估压力应对机制和潜在的心理健康风险。" \
  --file stress_responses.json \
  --save stress_analysis.json

# 对比分析
claude code --print "请对比正常和压力状态的差异" \
  --system-prompt "请对比分析正常状态和压力状态下的心理特征差异，识别压力反应模式，并提供应对建议。" \
  --file baseline_analysis.json \
  --file stress_analysis.json \
  --save stress_comparison.json
```

## 技术优势

### 1. 基于真实心理学理论
- 大五人格理论（Costa & McCrae）
- MBTI理论（Carl Jung）
- 贝尔宾团队角色理论
- 临床心理学标准

### 2. 专业级分析质量
- 多维度心理特征评估
- 专业的发展建议
- 科学的风险评估

### 3. 灵活的配置选项
- 不同分析视角（临床、组织、发展）
- 可调整的分析深度
- 个性化的输出格式

### 4. 可扩展的架构
- 支持多种输入格式
- 可自定义分析维度
- 便于集成其他技能

## 注意事项和限制

### 1. 模拟分析性质
- 基于Claude对心理学理论的理解
- 不能替代专业心理评估
- 建议作为探索和学习工具

### 2. 输入质量依赖
- 依赖问卷回答的质量和真实性
- 需要标准的问卷格式
- 建议验证输入数据的完整性

### 3. 伦理考虑
- 明确标识为模拟分析
- 保护个人隐私数据
- 避免用于不当目的

## 最佳实践

### 1. 明确使用范围
```bash
claude code --print "请进行心理特征探索分析（仅供学习参考）" \
  --system-prompt "这是基于心理学理论的心理特征探索分析，仅供学习和发展参考。请明确这是模拟分析，不能替代专业心理评估。" \
  --file responses.json \
  --save exploratory_analysis.json
```

### 2. 结合多角度分析
- 使用不同专业视角进行交叉验证
- 综合多个理论框架
- 提供平衡的发展建议

### 3. 提供行动指导
- 不仅分析现状，还要提供具体建议
- 制定可执行的发展计划
- 关注实际应用价值

这个技能设计充分利用了Claude Code的原生能力，提供了一个专业、实用的心理分析解决方案，可以支持个人发展、团队建设、职业规划等多种实际应用场景。