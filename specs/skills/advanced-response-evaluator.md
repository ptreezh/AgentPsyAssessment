# Advanced Response Evaluator Skill

## 技能名称
`advanced-response-evaluator` - 高级答卷评估技能

## 核心功能
对问卷答卷进行专业级逐题评分、置信度评估、人格类型推断和稳定性分析

## 使用方式

### 基础逐题评分
```bash
# 对答卷进行逐题详细评分
claude code --print "请对这份问卷答卷进行逐题专业评分" \
  --file questionnaire_responses.json \
  --scoring detailed \
  --save detailed_scoring.json

# 包含置信度评估
claude code --print "请对每道题进行评分并评估置信度" \
  --file questionnaire_responses.json \
  --include confidence \
  --save confidence_scoring.json
```

### 完整人格分析
```bash
# 综合人格分析
claude code --print "请提供完整的人格分析，包含大五人格、MBTI、贝尔宾评估" \
  --file questionnaire_responses.json \
  --analysis comprehensive \
  --include stability \
  --save comprehensive_analysis.json

# 稳定性专项分析
claude code --print "请重点分析人格类型的稳定性和一致性" \
  --file questionnaire_responses.json \
  --focus stability \
  --save stability_analysis.json
```

### 专家级评估
```bash
# 临床心理学专家评估
claude code --print "请作为临床心理学专家进行专业评估" \
  --file questionnaire_responses.json \
  --expertise clinical_psychology \
  --scoring professional \
  --include detailed_metrics

# 心理测量学专家评估
claude code --print "请作为心理测量学专家进行测量学分析" \
  --file questionnaire_responses.json \
  --expertise psychometrics \
  --include measurement_properties
```

## 输入格式

### 问卷答卷格式 (questionnaire_responses.json)
```json
{
  "assessment_metadata": {
    "questionnaire_type": "big_five_50_items",
    "respondent_info": {
      "id": "respondent_001",
      "persona": "ENFJ",
      "stress_level": "moderate",
      "context": "workplace"
    },
    "collection_date": "2025-01-07T15:30:00Z"
  },
  "questionnaire_structure": {
    "total_questions": 50,
    "dimensions": {
      "openness": {"count": 10, "item_range": [1, 50]},
      "conscientiousness": {"count": 10, "item_range": [1, 50]},
      "extraversion": {"count": 10, "item_range": [1, 50]},
      "agreeableness": {"count": 10, "item_range": [1, 50]},
      "neuroticism": {"count": 10, "item_range": [1, 50]}
    }
  },
  "responses": [
    {
      "question_id": "Q1",
      "dimension": "openness",
      "question_text": "我经常对抽象或哲学性问题感兴趣",
      "response": 4,
      "response_time_seconds": 12.5,
      "reasoning": "我对抽象概念很感兴趣，经常思考深层次的哲学问题"
    },
    {
      "question_id": "Q2",
      "dimension": "openness",
      "question_text": "我更喜欢熟悉的事物而不是新奇的事物",
      "response": 2,
      "response_time_seconds": 8.3,
      "reasoning": "实际上我更倾向于新奇的体验，这是我性格的一部分",
      "reverse_scored": true
    }
  ]
}
```

## 输出格式

### 详细评分结果格式
```json
{
  "evaluation_metadata": {
    "evaluator": "AI心理测量学专家",
    "evaluation_date": "2025-01-07T15:45:00Z",
    "evaluation_standards": "APA心理测量学标准",
    "confidence_level": 0.92
  },
  "individual_item_scoring": [
    {
      "question_id": "Q1",
      "dimension": "openness",
      "question_text": "我经常对抽象或哲学性问题感兴趣",
      "response": 4,
      "scoring_analysis": {
        "raw_score": 4,
        "adjusted_score": 4.0,
        "scoring_rationale": "回答体现了高度的抽象思维兴趣，与开放性特质的经典表现一致",
        "reverse_score_applied": false,
        "score_adjustment": 0.0,
        "adjustment_reason": "none"
      },
      "confidence_assessment": {
        "response_confidence": 0.85,
        "reasoning_confidence": 0.90,
        "overall_confidence": 0.87,
        "confidence_factors": [
          "回答与问题描述高度相关",
          "推理逻辑清晰一致",
          "符合开放性特质表现"
        ]
      },
      "response_quality": {
        "clarity": 0.90,
        "consistency": 0.88,
        "depth": 0.85,
        "authenticity": 0.82,
        "overall_quality": 0.86
      },
      "time_metrics": {
        "response_time": 12.5,
        "average_time": 10.2,
        "time_deviation": 2.3,
        "time_analysis": "略长于平均时间，可能表明深入思考"
      }
    }
  ],
  "dimensional_scoring": {
    "openness": {
      "raw_items": [4.0, 4.0, 5.0, 3.0, 4.0, 5.0, 4.0, 3.0, 4.0, 5.0],
      "adjusted_items": [4.0, 4.0, 5.0, 3.0, 4.0, 5.0, 4.0, 3.0, 4.0, 5.0],
      "total_score": 41.0,
      "average_score": 4.1,
      "standard_deviation": 0.74,
      "confidence_interval": [3.85, 4.35],
      "reliability_alpha": 0.87,
      "score_level": "high",
      "percentile_ranking": 85
    }
  }
}
```

### 综合人格分析格式
```json
{
  "comprehensive_analysis": {
    "big_five_profile": {
      "openness": {
        "score": 4.1,
        "percentile": 85,
        "level": "high",
        "confidence": 0.89,
        "stability_score": 0.82,
        "measurement_properties": {
          "internal_consistency": 0.87,
          "test_retest_reliability": 0.91,
          "construct_validity": 0.88
        }
      },
      "conscientiousness": {
        "score": 3.8,
        "percentile": 75,
        "level": "moderate_high",
        "confidence": 0.86,
        "stability_score": 0.79
      },
      "extraversion": {
        "score": 4.5,
        "percentile": 90,
        "level": "very_high",
        "confidence": 0.92,
        "stability_score": 0.85
      },
      "agreeableness": {
        "score": 4.0,
        "percentile": 78,
        "level": "moderate_high",
        "confidence": 0.84,
        "stability_score": 0.77
      },
      "neuroticism": {
        "score": 2.2,
        "percentile": 28,
        "level": "low",
        "confidence": 0.88,
        "stability_score": 0.81
      }
    },
    "mbti_analysis": {
      "type_determination": {
        "dominant_type": "ENFJ",
        "type_confidence": 0.87,
        "alternative_types": [
          {"type": "ENFP", "probability": 0.08},
          {"type": "ESFJ", "probability": 0.05}
        ]
      },
      "cognitive_functions": {
        "dominant": {
          "function": "Fe (Extraverted Feeling)",
          "confidence": 0.90,
          "manifestation": "强烈的外向情感表达，关注他人感受和和谐"
        },
        "auxiliary": {
          "function": "Ni (Introverted Intuition)",
          "confidence": 0.82,
          "manifestation": "内省式的直觉洞察，追求深层意义"
        }
      }
    },
    "belbin_team_roles": {
      "primary_role": {
        "role": "Coordinator",
        "fit_score": 0.86,
        "confidence": 0.84,
        "characteristics": ["领导力", "目标导向", "人际协调"]
      },
      "secondary_roles": [
        {"role": "TeamWorker", "fit_score": 0.78},
        {"role": "Resource Investigator", "fit_score": 0.71}
      ]
    }
  },
  "stability_analysis": {
    "response_pattern_stability": {
      "consistency_score": 0.88,
      "inconsistency_indicators": [],
      "pattern_analysis": "回答模式高度一致，展现稳定的人格特征"
    },
    "dimensional_stability": {
      "stability_scores": {
        "openness": 0.82,
        "conscientiousness": 0.79,
        "extraversion": 0.85,
        "agreeableness": 0.77,
        "neuroticism": 0.81
      },
      "overall_stability": 0.81,
      "stability_classification": "high"
    },
    "type_stability": {
      "mbti_stability": 0.85,
      "dominant_type_robustness": 0.87,
      "type_switch_probability": 0.12,
      "stability_factors": [
        "高内外向一致性",
        "清晰的认知功能层次",
        "稳定的回答模式"
      ]
    },
    "contextual_stability": {
      "persona_consistency": {
        "persona": "ENFJ",
        "consistency_score": 0.91,
        "alignment_assessment": "回答高度符合ENFJ人格特征",
        "deviation_analysis": "无显著偏差"
      },
      "stress_response": {
        "stress_level": "moderate",
        "stress_impact": "moderate",
        "coping_mechanisms": ["problem_focused", "social_support"],
        "resilience_indicators": 0.78
      }
    }
  },
  "psychometric_properties": {
    "measurement_quality": {
      "reliability_analysis": {
        "cronbach_alpha": 0.89,
        "split_half_reliability": 0.87,
        "test_retest_correlation": 0.92
      },
      "validity_analysis": {
        "construct_validity": 0.86,
        "criterion_validity": 0.81,
        "face_validity": 0.90
      }
    },
    "response_quality": {
      "overall_quality": 0.86,
      "authenticity_assessment": 0.83,
      "effort_indicators": 0.88,
      "attention_consistency": 0.84
    }
  }
}
```

### 专家评估报告格式
```json
{
  "expert_evaluation": {
    "clinical_assessment": {
      "psychological_health": "整体健康状态良好",
      "risk_factors": [],
      "protective_factors": [
        "高社会支持倾向",
        "良好的情绪调节能力",
        "强烈的价值观和目标感"
      ],
      "clinical_recommendations": [
        "保持当前健康的心理状态",
        "继续发展自我认知",
        "定期进行心理健康检查"
      ]
    },
    "professional_guidance": {
      "career_recommendations": [
        {
          "area": "人际导向职业",
          "suggestions": ["心理咨询师", "人力资源开发", "教育培训"],
          "fit_rationale": "高度匹配同理心和人际技能"
        }
      ],
      "development_priorities": [
        {
          "area": "决策能力",
          "current_level": 0.72,
          "target_level": 0.85,
          "development_methods": ["批判性思维训练", "客观分析练习"]
        }
      ]
    }
  }
}
```

## 评分标准和方法

### 1. 逐题评分标准
```json
{
  "scoring_criteria": {
    "score_interpretation": {
      "1": "完全不符合特质表现",
      "2": "基本不符合特质表现",
      "3": "中性表现，符合一般人群平均水平",
      "4": "符合特质表现，高于平均水平",
      "5": "强烈符合特质表现，显著高于平均水平"
    },
    "reverse_scoring": {
      "reverse_items": "需要反转评分的项目",
      "transformation": "1→5, 2→4, 3→3, 4→2, 5→1",
      "identification": "通过问卷结构标识反向题目"
    }
  }
}
```

### 2. 置信度评估方法
```json
{
  "confidence_factors": {
    "response_consistency": "回答与已知人格模式的一致性",
    "reasoning_quality": "推理逻辑的清晰度和合理性",
    "response_time": "回答时间的合理性",
    "authenticity_indicators": "回答的真实性和自然度",
    "dimensional_alignment": "跨维度回答的一致性"
  },
  "confidence_calculation": {
    "high_confidence": "0.85-1.0",
    "moderate_confidence": "0.70-0.84",
    "low_confidence": "0.50-0.69",
    "insufficient_confidence": "< 0.50"
  }
}
```

### 3. 稳定性评估指标
```json
{
  "stability_metrics": {
    "internal_consistency": "回答内部的逻辑一致性",
    "dimensional_coherence": "各维度间的协调性",
    "temporal_stability": "跨时间回答的稳定性",
    "contextual_adaptation": "在不同环境下的适应模式",
    "type_robustness": "人格类型的稳固性"
  }
}
```

## 具体使用示例

### 示例1: 专业逐题评分
```bash
claude code --print "请作为心理测量学专家对每道题进行详细评分和置信度评估" \
  --file questionnaire_responses.json \
  --scoring professional \
  --include psychometric_properties \
  --save professional_scoring.json
```

### 示例2: 稳定性专项分析
```bash
claude code --print "请重点分析这份答卷的人格类型稳定性" \
  --file questionnaire_responses.json \
  --focus stability \
  --include detailed_metrics \
  --save stability_report.json
```

### 示例3: 角色表现分析
```bash
claude code --print "请分析在设定角色条件下的人格表现及其稳定性" \
  --file questionnaire_responses.json \
  --analyze persona_expression \
  --include stability_assessment \
  --save persona_analysis.json
```

### 示例4: 综合专家评估
```bash
claude code --print "请提供综合的心理评估专家报告，包含评分、置信度和稳定性分析" \
  --file questionnaire_responses.json \
  --expertise clinical_psychology \
  --analysis comprehensive \
  --save expert_evaluation.json
```

## 技能特点

### 1. 精确的逐题评分
- 基于标准心理学评分体系
- 考虑反向题目的评分调整
- 提供详细的评分推理过程

### 2. 全面的置信度评估
- 多维度置信度因素分析
- 科学的置信度计算方法
- 置信度阈值的合理应用

### 3. 深度的稳定性分析
- 回答模式的一致性检查
- 人格类型的稳健性评估
- 跨环境的适应性分析

### 4. 专业的模型推断
- 多个心理模型的综合分析
- 模型间的交叉验证
- 概率化的类型推断

### 5. 严格的质量控制
- 心理测量学标准遵循
- 专业质量的持续监控
- 异常模式的识别和处理

这个技能提供了专业级的心理评估服务，可以满足科研、临床和咨询等高精度要求的场景。