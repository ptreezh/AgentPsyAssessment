# 压力评估技能 (Realistic Stress Evaluator)

## 技能概述

**技能名称**: `stress-evaluator`
**基于**: Claude Code 系统提示词功能
**适用场景**: 心理压力状态评估、压力耐受性分析、心理韧性评估

### 技能本质
这是一个通过Claude Code系统提示词配置的技能，让Claude能够基于心理学理论知识，对个体在不同压力环境下的心理状态、应对机制和韧性能力进行专业评估。

## 使用方式

### 基础压力评估
```bash
# 一般压力状态评估
claude code --print "请评估当前的压力状态和应对能力" \
  --system-prompt "你是压力心理学专家。请分析这份问卷回答，评估个体的压力水平、应对机制和心理韧性，提供专业的压力管理建议。" \
  --file stress_responses.json \
  --save stress_assessment.json

# 压力耐受性评估
claude code --print "请评估压力耐受性和应对策略" \
  --system-prompt "你是临床心理学家，专门研究压力和应对机制。请评估压力耐受性，识别主要的应对模式，分析心理韧性水平。" \
  --file stress_tolerance_responses.json \
  --save tolerance_analysis.json
```

### 环境特定压力评估
```bash
# 工作压力评估
claude code --print "请评估工作环境下的压力状态" \
  --system-prompt "你是组织心理学家，专注于职场压力研究。请从工作负荷、人际关系、角色冲突等方面分析工作压力，提供组织层面的干预建议。" \
  --file workplace_stress.json \
  --save workplace_stress_analysis.json

# 学业压力评估
claude code --print "请评估学业压力和学习适应性" \
  --system-prompt "你是教育心理学家，专门研究学生压力问题。请分析学业压力来源、学习适应性、时间管理能力，提供学业压力管理策略。" \
  --file academic_stress.json \
  --save academic_stress_analysis.json

# 生活事件压力评估
claude code --print "请评估生活事件带来的心理冲击" \
  --system-prompt "你是临床心理学专家，擅长生活应激事件评估。请分析生活事件的心理冲击程度、适应过程和恢复能力，提供心理支持建议。" \
  --file life_event_stress.json \
  --save life_event_analysis.json
```

### 压力等级评估
```bash
# 压力等级分级评估
claude code --print "请进行5级压力等级评估" \
  --system-prompt "请使用1-5级压力等级系统评估：1=无压力，2=轻度压力，3=中度压力，4=高度压力，5=极度压力。请详细分析每个维度的压力等级。" \
  --file stress_level_responses.json \
  --save stress_level_analysis.json

# 急性vs慢性压力分析
claude code --print "请分析急性压力和慢性压力模式" \
  --system-prompt "你是压力研究专家，请区分急性压力和慢性压力的表现模式，分析不同的生理和心理反应，提供针对性的管理策略。" \
  --file stress_pattern_responses.json \
  --save stress_pattern_analysis.json
```

### 心理韧性评估
```bash
# 综合心理韧性评估
claude code --print "请评估综合心理韧性水平" \
  --system-prompt "你是积极心理学专家，请评估心理韧性的各个维度：坚韧性、力量性、乐观性。分析韧性资源和保护因素。" \
  --file resilience_responses.json \
  --save resilience_assessment.json

# 韧性资源和保护因素分析
claude code --print "请分析韧性资源和保护因素" \
  --system-prompt "请识别个体的韧性资源（社会支持、应对技能、自我效能等）和保护因素，评估其在压力应对中的作用。" \
  --file resilience_factors.json \
  --save resilience_factors_analysis.json
```

## 输入格式

### 压力评估问卷格式
```json
{
  "assessment_info": {
    "assessment_type": "stress_evaluation",
    "respondent_info": {
      "role": "职场人士",
      "context": "高压工作环境",
      "assessment_date": "2025-01-07T16:30:00Z"
    }
  },
  "stress_dimensions": {
    "work_stress": {
      "questions": [
        {
          "id": "WS1",
          "question": "我感到工作压力很大，难以应对",
          "response": 4,
          "reasoning": "最近项目截止日期紧张，经常加班"
        },
        {
          "id": "WS2",
          "question": "我对工作中的要求感到不堪重负",
          "response": 3,
          "reasoning": "有时候会觉得任务太多，但还能应对"
        }
      ]
    },
    "interpersonal_stress": {
      "questions": [
        {
          "id": "IS1",
          "question": "我与同事或上级的关系让我感到紧张",
          "response": 2,
          "reasoning": "偶尔有分歧，但总体关系良好"
        }
      ]
    },
    "coping_strategies": {
      "questions": [
        {
          "id": "CS1",
          "question": "面对压力时，我能够找到有效的解决方法",
          "response": 4,
          "reasoning": "通常能够分析问题并采取行动"
        },
        {
          "id": "CS2",
          "question": "我会在压力大时寻求他人的支持和帮助",
          "response": 3,
          "reasoning": "有时会，但更多时候自己处理"
        }
      ]
    }
  }
}
```

### 心理韧性评估格式
```json
{
  "resilience_info": {
    "assessment_type": "resilience_evaluation",
    "focus_areas": ["坚韧", "力量", "乐观"]
  },
  "resilience_dimensions": {
    "perseverance": {
      "questions": [
        {
          "id": "P1",
          "question": "面对困难时，我会坚持不放弃",
          "response": 4,
          "reasoning": "相信努力可以改变情况"
        }
      ]
    },
    "self_efficacy": {
      "questions": [
        {
          "id": "SE1",
          "question": "我相信自己有能力应对挑战",
          "response": 4,
          "reasoning": "过去成功应对过类似情况"
        }
      ]
    },
    "optimism": {
      "questions": [
        {
          "id": "O1",
          "question": "我对未来保持乐观的态度",
          "response": 3,
          "reasoning": "总体乐观，但也会考虑现实困难"
        }
      ]
    }
  }
}
```

## 输出格式

### 压力评估报告格式
```json
{
  "stress_assessment": {
    "assessment_metadata": {
      "evaluator": "压力心理学专家",
      "assessment_date": "2025-01-07T16:45:00Z",
      "assessment_framework": "应激-应对-韧性综合模型"
    },
    "overall_stress_level": {
      "global_stress_score": 3.7,
      "stress_level": "moderate_high",
      "stress_classification": "中度偏高压力",
      "confidence": 0.88,
      "clinical_significance": "需要关注和干预"
    },
    "dimensional_analysis": {
      "work_stress": {
        "score": 4.2,
        "level": "high",
        "percentile": 85,
        "indicators": [
          "工作负荷过重",
          "时间压力明显",
          "角色模糊或冲突"
        ],
        "impact_assessment": "对工作效率和生活质量产生显著负面影响"
      },
      "interpersonal_stress": {
        "score": 2.8,
        "level": "moderate",
        "percentile": 65,
        "indicators": [
          "偶尔的人际冲突",
          "沟通压力"
        ],
        "impact_assessment": "轻度影响，总体可控"
      },
      "coping_effectiveness": {
        "score": 3.5,
        "level": "moderate_high",
        "percentile": 75,
        "indicators": [
          "问题解决导向",
          "适度寻求支持",
          "情绪调节能力"
        ],
        "impact_assessment": "应对策略基本有效，有提升空间"
      }
    },
    "stress_pattern_analysis": {
      "acute_stress_indicators": [
        "近期工作压力明显增加",
        "生理紧张症状出现",
        "睡眠质量下降"
      ],
      "chronic_stress_indicators": [
        "长期工作负荷过重",
        "应对资源逐渐消耗",
        "生活平衡失调"
      ],
      "pattern_classification": "混合型压力（急性加慢性）",
      "trend_analysis": "压力水平呈上升趋势"
    },
    "risk_assessment": {
      "burnout_risk": {
        "level": "moderate_high",
        "probability": 0.68,
        "risk_factors": [
          "高工作投入低回报感",
          "缺乏恢复时间",
          "支持资源不足"
        ]
      },
      "mental_health_risk": {
        "level": "moderate",
        "probability": 0.35,
        "concern_areas": [
          "焦虑症状",
          "睡眠障碍",
          "情绪波动"
        ]
      },
      "physical_health_risk": {
        "level": "moderate",
        "probability": 0.42,
        "concern_areas": [
          "心血管症状",
          "免疫系统功能下降",
          "消化系统问题"
        ]
      }
    }
  },
  "resilience_assessment": {
    "overall_resilience": {
      "resilience_score": 3.6,
      "resilience_level": "moderate_high",
      "percentile": 78,
      "classification": "较强心理韧性"
    },
    "resilience_dimensions": {
      "perseverance": {
        "score": 4.0,
        "level": "high",
        "description": "面对困难时表现出良好的坚持性",
        "strengths": ["目标导向", "持续努力"],
        "areas_for_development": ["适应性调整"]
      },
      "self_efficacy": {
        "score": 4.1,
        "level": "high",
        "description": "对自身能力有较强信心",
        "strengths": ["问题解决信心", "学习适应能力"],
        "areas_for_development": ["接受局限"]
      },
      "optimism": {
        "score": 3.2,
        "level": "moderate",
        "description": "适度乐观，能平衡期望与现实",
        "strengths": ["积极心态", "希望感"],
        "areas_for_development": ["现实检验"]
      },
      "social_support": {
        "score": 2.9,
        "level": "moderate",
        "description": "有一定的社会支持但利用不充分",
        "strengths": ["支持网络存在"],
        "areas_for_development": ["主动寻求帮助", "支持质量提升"]
      }
    },
    "protective_factors": [
      "良好的自我效能感",
      "问题解决导向的应对风格",
      "适度的乐观心态",
      "学习能力较强"
    ],
    "vulnerability_factors": [
      "社会支持利用不足",
      "过度责任感",
      "恢复时间不足"
    ]
  },
  "intervention_recommendations": {
    "immediate_strategies": [
      {
        "strategy": "工作负荷管理",
        "priority": "high",
        "actions": [
          "重新评估工作优先级",
          "学会拒绝不合理要求",
          "提高时间管理效率"
        ],
        "expected_outcome": "工作压力降低20-30%"
      },
      {
        "strategy": "恢复时间安排",
        "priority": "high",
        "actions": [
          "确保充足的睡眠时间",
          "安排规律的休息时段",
          "培养放松爱好"
        ],
        "expected_outcome": "身心恢复能力提升"
      }
    ],
    "medium_term_strategies": [
      {
        "strategy": "应对技能提升",
        "priority": "medium",
        "actions": [
          "学习压力管理技术",
          "提升沟通技巧",
          "发展情绪调节能力"
        ],
        "expected_outcome": "应对效能提升"
      }
    ],
    "long_term_strategies": [
      {
        "strategy": "社会支持强化",
        "priority": "medium",
        "actions": [
          "主动建立支持网络",
          "学习寻求和接受帮助",
          "参与群体活动"
        ],
        "expected_outcome": "社会支持质量提升"
      }
    ]
  },
  "monitoring_plan": {
    "key_indicators": [
      "睡眠质量评分",
      "工作满意度",
      "情绪稳定性",
      "身体健康症状"
    ],
    "assessment_frequency": "每2周自我评估一次",
    "professional_consultation": "建议在压力持续加重时寻求专业帮助",
    "crisis_intervention": "当出现严重身心症状时立即寻求专业支持"
  }
}
```

### 心理韧性发展计划格式
```json
{
  "resilience_development_plan": {
    "current_status": "心理韧性水平良好，有进一步提升空间",
    "development_goals": [
      "提升社会支持利用能力",
      "增强情绪调节技能",
      "改善工作生活平衡",
      "培养更积极的应对策略"
    ],
    "specific_interventions": {
      "perseverance_enhancement": {
        "current_level": 4.0,
        "target_level": 4.5,
        "methods": [
          "设定阶段性目标",
          "庆祝小的成功",
          "从失败中学习"
        ],
        "timeline": "3-6个月"
      },
      "self_efficacy_building": {
        "current_level": 4.1,
        "target_level": 4.6,
        "methods": [
          "技能培训和学习",
          "成功经验积累",
          "积极自我对话"
        ],
        "timeline": "2-4个月"
      },
      "optimism_cultivation": {
        "current_level": 3.2,
        "target_level": 4.0,
        "methods": [
          "感恩练习",
          "积极重构训练",
          "希望感培养"
        ],
        "timeline": "4-6个月"
      }
    }
  }
}
```

## 具体使用示例

### 示例1: 职场压力全面评估
```bash
claude code --print "请进行全面的职场压力评估" \
  --system-prompt "你是组织心理学专家，请从工作负荷、人际关系、角色冲突、职业发展等多个维度评估职场压力，提供组织和个人的双重干预建议。" \
  --file workplace_stress_assessment.json \
  --save comprehensive_workplace_analysis.json
```

### 示例2: 压力应对技能评估
```bash
claude code --print "请评估压力应对技能的有效性" \
  --system-prompt "你是临床心理学家，请评估个体的压力应对技能，包括问题解决、情绪调节、认知重构、寻求支持等策略的有效性。" \
  --file coping_skills_responses.json \
  --save coping_skills_evaluation.json
```

### 示例3: 心理韧性专项提升计划
```bash
claude code --print "请制定心理韧性提升计划" \
  --system-prompt "你是积极心理学专家，请基于当前评估结果，制定个性化的心理韧性提升计划，包括具体的目标、方法和时间安排。" \
  --file resilience_assessment.json \
  --save resilience_development_plan.json
```

### 示例4: 压力相关风险预警
```bash
claude code --print "请评估压力相关健康风险" \
  --system-prompt "你是心身医学专家，请评估当前压力水平对身心健康的风险，识别早期预警信号，提供预防性干预建议。" \
  --file health_risk_assessment.json \
  --save health_risk_analysis.json
```

## 技能特点

### 1. 多维度压力评估
- 工作、人际、生活等多方面压力分析
- 急性vs慢性压力模式识别
- 压力源和压力反应的关联分析

### 2. 专业的心理韧性评估
- 坚韧性、力量性、乐观性三维评估
- 保护因素和风险因素识别
- 韧性资源分析和利用建议

### 3. 科学的风险评估
- 职业倦怠风险评估
- 心理健康风险预测
- 生理健康影响评估

### 4. 实用的干预建议
- 即时、中期、长期策略结合
- 个人和组织层面并重
- 可操作的具体行动计划

### 5. 持续的监控机制
- 关键指标追踪
- 定期评估安排
- 危机干预预案

这个技能设计基于Claude Code的实际能力，提供了专业、实用的压力评估和心理韧性分析服务，可以支持个人发展、企业健康管理和临床咨询等多种应用场景。