# Stress Testing Analysis Skill Specification

## Skill Overview

**Skill Name**: `stress-testing-analysis`
**Version**: 1.0.0
**Author**: ptreezh <3061176@qq.com>
**License**: MIT License
**Website**: https://agentpsy.com

**Description**:
专业的心理压力测试分析系统，通过认知陷阱、情绪压力测试和应激反应分析，评估个体在不同压力环境下的心理韧性和应对机制。支持多维度压力评估、压力耐受性分析和个性化压力管理建议生成。

## 功能特性

### 核心功能
- **多级压力测试**: 支持0-4级递进式压力强度测试
- **认知陷阱分析**: 识别和分析4种主要认知陷阱类型
- **情绪压力评估**: 综合评估情绪稳定性、焦虑倾向和抗压能力
- **应激反应监测**: 实时监测压力下的认知功能变化
- **压力耐受性评估**: 量化个体压力耐受边界和恢复能力
- **个性化干预建议**: 基于压力特征生成定制化管理策略

### 压力测试类型
- **时间压力测试**: 限时决策和快速响应能力评估
- **信息过载测试**: 复杂信息环境下的处理能力评估
- **社交压力测试**: 群体互动和评价环境下的表现评估
- **认知冲突测试**: 矛盾信息和悖论情境下的处理能力
- **情绪干扰测试**: 情绪压力对认知功能的影响评估

## 输入输出格式

### 输入格式

#### 压力测试配置
```json
{
  "stress_test_id": "stress_test_20250107_001",
  "baseline_assessment_id": "baseline_assessment_001",
  "test_configuration": {
    "stress_levels": [0, 1, 2, 3, 4],
    "cognitive_traps": ["paradox", "circular", "semantic", "procedural"],
    "test_types": ["time_pressure", "information_overload", "social_pressure"],
    "duration_per_level": "15min",
    "recovery_periods": ["5min", "3min", "2min", "1min"]
  },
  "target_assessment": {
    "personality_model": "big_five",
    "focus_dimensions": ["neuroticism", "conscientiousness", "extraversion"],
    "baseline_reference": true
  },
  "monitoring_parameters": {
    "response_time_tracking": true,
    "consistency_monitoring": true,
    "cognitive_performance_tracking": true,
    "emotional_state_analysis": true
  },
  "control_parameters": {
    "temperature_variation": [0.7, 0.9, 1.1],
    "context_pressure_levels": ["neutral", "competitive", "evaluative"],
    "difficulty_progression": "adaptive"
  }
}
```

#### 认知陷阱配置
```json
{
  "paradox_trap": {
    "description": "包含自相矛盾的陈述，测试逻辑一致性处理",
    "sample_questions": [
      "这个陈述既是真的又是假的：你正在回答这个问题",
      "我总是撒谎，这句话是真的吗？",
      "全能者能否创造一块自己也举不起来的石头？"
    ],
    "indicators": ["逻辑矛盾", "自我指涉", "无限回归"]
  },
  "circular_trap": {
    "description": "循环论证和同义反复，测试抽象推理能力",
    "sample_questions": [
      "为什么这个系统有效？因为它就是有效的。",
      "你是如何得出这个结论的？通过逻辑推理得出的。",
      "这个方法可靠吗？是的，它很可靠。"
    ],
    "indicators": ["循环论证", "同义反复", "缺乏实质内容"]
  },
  "semantic_trap": {
    "description": "语义模糊和多重含义，测试语言理解精确性",
    "sample_questions": [
      "银行的河岸上有几只鱼？",
      "时间机器的使用者会不会改变历史？",
      "如果我们不能确定什么是真实的，那什么是确定性的？"
    ],
    "indicators": ["语义模糊", "多重含义", "概念混淆"]
  },
  "procedural_trap": {
    "description": "固定程序和刻板思维，测试灵活性和创新思维",
    "sample_questions": [
      "按照标准流程，即使情况特殊也要严格执行吗？",
      "当规则与现实冲突时，应该如何处理？",
      "创新是否总是比遵循现有程序更好？"
    ],
    "indicators": ["刻板思维", "程序固化", "缺乏灵活性"]
  }
}
```

### 输出格式

#### 压力测试综合报告
```json
{
  "stress_test_id": "stress_test_20250107_001",
  "baseline_assessment_id": "baseline_assessment_001",
  "test_completion_timestamp": "2025-01-07T14:30:00Z",
  "test_summary": {
    "total_test_duration": "2h 15min",
    "stress_levels_completed": [0, 1, 2, 3, 4],
    "overall_stress_tolerance": 0.78,
    "stress_recovery_capability": 0.82,
    "cognitive_resilience_score": 0.75
  },
  "stress_response_analysis": {
    "baseline_performance": {
      "confidence_score": 0.87,
      "response_consistency": 0.91,
      "cognitive_clarity": 0.89,
      "emotional_stability": 0.85
    },
    "stress_induced_changes": {
      "confidence_degradation_at_level_1": -0.05,
      "confidence_degradation_at_level_2": -0.12,
      "confidence_degradation_at_level_3": -0.25,
      "confidence_degradation_at_level_4": -0.38,
      "response_consistency_degradation": -0.18,
      "cognitive_clarity_impact": -0.22,
      "emotional_volatility_increase": 0.31
    },
    "critical_pressure_points": {
      "performance_decline_threshold": "stress_level_3",
      "cognitive_impairment_onset": "stresslevel_2",
      "emotional_destabilization_point": "stress_level_3",
      "recovery_ability_limit": "stress_level_4"
    }
  },
  "cognitive_trap_analysis": {
    "paradox_trap_performance": {
      "baseline_success_rate": 0.82,
      "stress_level_4_success_rate": 0.58,
      "degradation_percentage": 29.3,
      "common_error_patterns": [
        "陷入自指循环",
        "忽视逻辑矛盾",
        "过度简化复杂悖论"
      ],
      "coping_strategies_observed": [
        "元认知反思（有效）",
        "逐步分解（部分有效）",
        "回避矛盾（无效）"
      ]
    },
    "circular_trap_performance": {
      "baseline_success_rate": 0.89,
      "stress_level_4_success_rate": 0.71,
      "degradation_percentage": 20.2,
      "vulnerability_indicators": [
        "容易被空洞说服",
        "缺乏批判性思维",
        "满足于表面逻辑"
      ]
    },
    "semantic_trap_performance": {
      "baseline_success_rate": 0.76,
      "stress_level_4_success_rate": 0.49,
      "degradation_percentage": 35.5,
      "language_processing_impact": {
        "semantic_precision": -0.31,
        "context_resolution": -0.27,
        "ambiguity_tolerance": -0.19
      }
    },
    "procedural_trap_performance": {
      "baseline_success_rate": 0.84,
      "stress_level_4_success_rate": 0.67,
      "degradation_percentage": 20.2,
      "cognitive_flexibility_metrics": {
        "adaptation_speed": -0.18,
        "innovation_willingness": -0.24,
        "rule_deviation_ability": -0.15
      }
    },
    "overall_cognitive_trap_vulnerability": {
      "most_vulnerable_trap": "semantic_trap",
      "least_vulnerable_trap": "circular_trap",
      "cognitive_traps_resilience_score": 0.73
    }
  },
  "dimensional_stress_analysis": {
    "neuroticism_stress_response": {
      "baseline_score": 2.8,
      "stress_level_4_score": 4.1,
      "sensitivity_index": 0.87,
      "stress_amplification_factor": 1.46,
      "emotional_regulation_under_pressure": 0.62,
      "anxiety_manifestation_patterns": [
        "认知功能下降",
        "决策时间延长",
        "注意力分散"
      ],
      "stress_management_effectiveness": 0.58
    },
    "conscientiousness_stress_response": {
      "baseline_score": 3.9,
      "stress_level_4_score": 3.2,
      "stability_index": 0.82,
      "stress_resistance_factor": 0.82,
      "quality_maintenance_under_pressure": 0.75,
      "organization_impact": -0.22,
      "perfectionism_pressure_response": -0.31
    },
    "extraversion_stress_response": {
      "baseline_score": 4.2,
      "stress_level_4_score": 3.1,
      "energy_depletion_rate": 0.26,
      "social_engagement_decline": -0.35,
      "communication_clarity_impact": -0.18,
      "assertiveness_maintenance": 0.67
    },
    "agreeableness_stress_response": {
      "baseline_score": 3.6,
      "stress_level_4_score": 2.8,
      "conflict_avoidance_increase": 0.42,
      "cooperation_maintenance": 0.73,
      "empathy_preservation": 0.68,
      "harmony_prioritization_amplification": 0.38
    },
    "openness_stress_response": {
      "baseline_score": 3.4,
      "stress_level_4_score": 2.7,
      "cognitive_flexibility_retention": 0.79,
      "creativity_impact": -0.21,
      "novelty_seeking_decline": -0.18,
      "idea_generation_under_pressure": 0.65
    }
  },
  "stress_mechanism_analysis": {
    "primary_stress_triggers": [
      "时间压力（权重: 0.35）",
      "评价焦虑（权重: 0.28）",
      "信息过载（权重: 0.22）",
      "认知冲突（权重: 0.15）"
    ],
    "coping_mechanisms_identified": {
      "problem_focused_coping": {
        "effectiveness": 0.78,
        "usage_frequency": "high",
        "stress_levels_applicable": [1, 2]
      },
      "emotion_focused_coping": {
        "effectiveness": 0.62,
        "usage_frequency": "moderate",
        "stress_levels_applicable": [3, 4]
      },
      "avoidance_coping": {
        "effectiveness": 0.31,
        "usage_frequency": "low",
        "stress_levels_applicable": [4]
      },
      "seeking_social_support": {
        "effectiveness": 0.71,
        "usage_frequency": "moderate",
        "stress_levels_applicable": [2, 3]
      }
    },
    "maladaptive_patterns": [
      "过度思考（ruminations）",
      "完美主义加剧",
      "决策拖延",
      "情绪压抑"
    ]
  },
  "stress_tolerance_profile": {
    "overall_stress_tolerance": 0.78,
    "stress_recovery_capability": 0.82,
    "psychological_resilience_score": 0.75,
    "stress_endurance_limits": {
      "optimal_performance_zone": "stress_level_0-2",
      "acceptable_performance_zone": "stress_level_0-3",
      "performance_decline_zone": "stress_level_3-4",
      "critical_failure_zone": "stress_level_4"
    },
    "recovery_patterns": {
      "immediate_recovery_speed": 0.68,
      "short_term_recovery_effectiveness": 0.81,
      "long_term_adaptation_capacity": 0.74,
      "stress_inoculation_potential": 0.77
    }
  },
  "personalized_stress_management_recommendations": {
    "immediate_intervention_strategies": [
      {
        "strategy": "正念呼吸练习",
        "targeted_stress_level": [2, 3],
        "effectiveness_estimate": 0.85,
        "implementation_difficulty": "low",
        "time_requirement": "3-5分钟"
      },
      {
        "strategy": "认知重构技术",
        "targeted_stress_level": [3, 4],
        "effectiveness_estimate": 0.78,
        "implementation_difficulty": "moderate",
        "time_requirement": "5-10分钟"
      },
      {
        "strategy": " Progressive Muscle Relaxation",
        "targeted_stress_level": [2, 3, 4],
        "effectiveness_estimate": 0.82,
        "implementation_difficulty": "low",
        "time_requirement": "10-15分钟"
      }
    ],
    "long_term_development_goals": [
      {
        "goal": "增强认知灵活性",
        "current_level": 0.73,
        "target_level": 0.85,
        "development_methods": [
          "多样化思维训练",
          "跨学科学习",
          "创新问题解决练习"
        ],
        "estimated_timeframe": "3-6个月"
      },
      {
        "goal": "提升情绪调节能力",
        "current_level": 0.62,
        "target_level": 0.80,
        "development_methods": [
          "情绪识别训练",
          "冥想和正念练习",
          "情绪表达技巧学习"
        ],
        "estimated_timeframe": "2-4个月"
      },
      {
        "goal": "优化时间管理技能",
        "current_level": 0.71,
        "target_level": 0.88,
        "development_methods": [
          "优先级管理培训",
          "效率工具使用",
          "专注力训练"
        ],
        "estimated_timeframe": "1-3个月"
      }
    ],
    "environmental_optimization_suggestions": [
      {
        "area": "工作环境设计",
        "specific_recommendations": [
          "减少环境干扰因素",
          "优化工作流程",
          "建立合理的休息机制"
        ],
        "expected_stress_reduction": "15-20%"
      },
      {
        "area": "社会支持系统",
        "specific_recommendations": [
          "建立同事支持网络",
          "寻求导师指导",
          "参与专业交流团体"
        ],
        "expected_stress_reduction": "20-25%"
      }
    ]
  },
  "professional_implications": {
    "career_suitability_analysis": {
      "high_stress_tolerance_careers": [
        {
          "career": "项目管理",
          "suitability_score": 0.84,
          "stress_compatibility": "high",
          "development_needs": ["时间管理", "团队协调"]
        },
        {
          "career": "急诊医疗",
          "suitability_score": 0.68,
          "stress_compatibility": "moderate",
          "development_needs": ["情绪稳定", "快速决策"]
        }
      ],
      "low_stress_tolerance_careers": [
        {
          "career": "精密工艺",
          "suitability_score": 0.91,
          "stress_compatibility": "low",
          "natural_alignment": "high"
        }
      ]
    },
    "workplace_performance_predictions": {
      "normal_stress_environment_performance": "优秀",
      "high_stress_environment_performance": "良好",
      "crisis_situation_performance": "可接受",
      "burnout_risk_level": "中等"
    }
  },
  "quality_assessment": {
    "test_reliability": 0.94,
    "result_consistency": 0.89,
    "predictive_validity": 0.82,
    "clinical_utility": 0.87,
    "ethical_considerations": {
      "informed_consent_obtained": true,
      "debriefing_provided": true,
      "follow_up_support_available": true,
      "data_privacy_protected": true
    }
  }
}
```

## 使用场景

### 1. 企业心理健康评估
- 高压岗位员工心理适应性评估
- 领导力发展和压力管理培训需求分析
- 团队心理韧性建设和危机应对能力评估

### 2. 临床心理评估
- 焦虑症、抑郁症等心理疾病的辅助诊断
- 心理治疗方案的制定和效果评估
- 创伤后应激障碍(PTSD)的风险评估

### 3. 教育心理咨询
- 学生考试焦虑评估和干预
- 学习压力适应性评估
- 心理韧性培养方案设计

### 4. 军事和紧急服务
- 特种作战人员心理选拔
- 应急响应人员压力承受能力评估
- 高风险作业适应性分析

## 技术实现要求

### 核心组件架构
```python
# 1. 压力测试引擎
class StressTestingEngine:
    def __init__(self, test_config, ai_model_client)
    def conduct_baseline_assessment(self, participant_id)
    def apply_stress_level(self, level, cognitive_trap_type)
    def monitor_stress_response(self, participant_responses)
    def analyze_stress_impact(self, baseline_data, stress_data)
    def generate_stress_profile(self, all_stress_levels)

# 2. 认知陷阱生成器
class CognitiveTrapGenerator:
    def __init__(self, trap_templates, difficulty_levels)
    def generate_paradox_questions(self, complexity_level)
    def create_circular_reasoning_scenarios(self, sophistication)
    def design_semantic_ambiguity_tests(self, language_complexity)
    def construct_procedural_rigidity_challenges(self, flexibility_requirements)

# 3. 压力响应监测器
class StressResponseMonitor:
    def __init__(self, monitoring_config)
    def track_response_times(self, question_responses)
    def analyze_consistency_patterns(self, response_data)
    def detect_cognitive_degradation(self, performance_metrics)
    assess_emotional_volatility(self, language_patterns)
    def calculate_stress_indicators(self, monitoring_data)

# 4. 压力耐受性分析器
class StressToleranceAnalyzer:
    def __init__(self, tolerance_models)
    def calculate_tolerance_thresholds(self, stress_response_data)
    def identify_critical_pressure_points(self, performance_curves)
    def assess_recovery_capacity(self, recovery_patterns)
    def generate_resilience_profile(self, tolerance_analysis)

# 5. 干预建议生成器
class InterventionRecommender:
    def __init__(self, intervention_database, effectiveness_models)
    def analyze_coping_mechanisms(self, response_patterns)
    def recommend_immediate_strategies(self, stress_triggers)
    def suggest_long_term_development(self, resilience_gaps)
    def personalize_interventions(self, individual_profile)
```

### 压力测试配置参数
```python
# 压力测试配置
STRESS_TESTING_CONFIG = {
    "stress_levels": {
        0: {
            "name": "baseline",
            "description": "无压力基线测试",
            "pressure_intensity": 0.0,
            "time_constraints": "none",
            "evaluation_context": "neutral"
        },
        1: {
            "name": "mild_stress",
            "description": "轻微压力环境",
            "pressure_intensity": 0.25,
            "time_constraints": "slight",
            "evaluation_context": "low_stakes"
        },
        2: {
            "name": "moderate_stress",
            "description": "中等压力环境",
            "pressure_intensity": 0.5,
            "time_constraints": "moderate",
            "evaluation_context": "performance_monitored"
        },
        3: {
            "name": "high_stress",
            "description": "高压环境",
            "pressure_intensity": 0.75,
            "time_constraints": "significant",
            "evaluation_context": "high_stakes"
        },
        4: {
            "name": "extreme_stress",
            "description": "极端压力环境",
            "pressure_intensity": 1.0,
            "time_constraints": "critical",
            "evaluation_context": "crisis_simulation"
        }
    },
    "cognitive_traps": {
        "paradox": {
            "complexity_levels": [1, 2, 3, 4, 5],
            "cognitive_load_impact": "high",
            "emotional_stress_trigger": "confusion"
        },
        "circular": {
            "complexity_levels": [1, 2, 3],
            "cognitive_load_impact": "moderate",
            "emotional_stress_trigger": "frustration"
        },
        "semantic": {
            "complexity_levels": [2, 3, 4, 5],
            "cognitive_load_impact": "moderate_high",
            "emotional_stress_trigger": "ambiguity"
        },
        "procedural": {
            "complexity_levels": [1, 2, 3, 4],
            "cognitive_load_impact": "low_moderate",
            "emotional_stress_trigger": "rigidity"
        }
    }
}

# 监测指标配置
MONITORING_INDICATORS = {
    "cognitive_performance": {
        "response_time": {
            "baseline_threshold": "30s",
            "stress_impact_factor": 1.5,
            "critical_threshold": "120s"
        },
        "accuracy": {
            "baseline_minimum": 0.8,
            "acceptable_degradation": 0.2,
            "critical_threshold": 0.5
        },
        "consistency": {
            "baseline_minimum": 0.85,
            "acceptable_degradation": 0.15,
            "critical_threshold": 0.6
        }
    },
    "emotional_indicators": {
        "language_sentiment": {
            "positivity_threshold": 0.6,
            "negativity_alert": 0.3,
            "volatility_threshold": 0.4
        },
        "certainty_expression": {
            "confidence_baseline": 0.75,
            "uncertainty_increase_alert": 0.3,
            "decision_avoidance_threshold": 0.5
        }
    },
    "behavioral_patterns": {
        "engagement_level": {
            "response_rate_threshold": 0.9,
            "participation_decline_alert": 0.2,
            "withdrawal_threshold": 0.5
        },
        "effort_indicators": {
            "detail_level_baseline": "moderate",
            "effort_reduction_alert": 0.3,
            "minimal_effort_threshold": 0.2
        }
    }
}
```

### 安全和伦理考虑
```python
# 安全协议配置
SAFETY_PROTOCOLS = {
    "stress_level_limits": {
        "maximum_duration_per_level": "20min",
        "required_recovery_periods": {
            "after_level_2": "5min",
            "after_level_3": "10min",
            "after_level_4": "15min"
        },
        "emergency_stop_triggers": [
            "severe_distress_indicators",
            "cognitive_overload_signals",
            "participant_requested_stop"
        ]
    },
    "participant_protection": {
        "informed_consent_required": True,
        "right_to_withdraw": "any_time",
        "debriefing_mandatory": True,
        "follow_up_support_available": True
    },
    "data_privacy": {
        "anonymization_required": True,
        "secure_storage_encryption": True,
        "access_control_strict": True,
        "retention_policy": "5_years"
    },
    "clinical_referral_triggers": {
        "severe_anxiety_indicators": True,
        "depression_risk_factors": True,
        "trauma_responses": True,
        "suicidal_ideation": True
    }
}
```

## 示例代码

### 基础压力测试实施
```python
from skills.stress_testing_analysis import StressTestingAnalysis

# 创建压力测试实例
stress_tester = StressTestingAnalysis(
    ai_model_client="claude-3.5-sonnet",
    safety_monitoring=True,
    clinical_thresholds="standard"
)

# 配置压力测试
test_config = {
    "participant_id": "participant_001",
    "baseline_assessment": "baseline_big_five_result.json",
    "stress_levels": [0, 1, 2, 3],
    "cognitive_traps": ["paradox", "semantic"],
    "focus_dimensions": ["neuroticism", "conscientiousness"],
    "safety_protocols": "enhanced"
}

# 执行压力测试
test_session = stress_tester.start_stress_test(test_config)

# 监控测试进度
while not test_session.is_complete():
    current_status = stress_tester.get_test_status(test_session.session_id)

    print(f"""
    当前测试状态:
    - 压力等级: {current_status['current_stress_level']}
    - 认知表现: {current_status['cognitive_performance_score']:.3f}
    - 情绪稳定性: {current_status['emotional_stability_score']:.3f}
    - 安全指标: {current_status['safety_status']}
    """)

    # 检查安全阈值
    if stress_tester.check_safety_thresholds(current_status):
        print("⚠️ 检测到压力过载信号，启动安全协议")
        stress_tester.activate_safety_protocol(test_session.session_id)
        break

    time.sleep(60)

# 获取压力测试报告
stress_report = stress_tester.generate_stress_analysis_report(test_session.session_id)
print(f"压力耐受性评分: {stress_report['overall_stress_tolerance']:.3f}")
print(f"心理韧性评分: {stress_report['psychological_resilience_score']:.3f}")
```

### 高级认知陷阱分析
```python
# 高级认知陷阱分析配置
advanced_trap_config = {
    "trap_analysis_depth": "comprehensive",
    "individual_trap_focus": {
        "primary_vulnerability": "semantic_trap",
        "secondary_focus": "paradox_trap",
        "exploratory_traps": ["circular", "procedural"]
    },
    "adaptive_difficulty": True,
    "real_time_adaptation": True
}

# 进行深度认知陷阱分析
trap_analysis = stress_tester.conduct_cognitive_trap_analysis(
    session_id=test_session.session_id,
    config=advanced_trap_config
)

# 分析认知脆弱性模式
vulnerability_patterns = stress_tester.analyze_cognitive_vulnerability_patterns(
    trap_analysis_results=trap_analysis
)

print("认知脆弱性分析:")
for trap, analysis in vulnerability_patterns.items():
    print(f"{trap}:")
    print(f"  基线表现: {analysis['baseline_performance']:.3f}")
    print(f"  压力下降解: {analysis['stress_degradation']:.3f}")
    print(f"  主要错误模式: {analysis['dominant_error_patterns']}")
    print(f"  应对策略效果: {analysis['coping_strategy_effectiveness']:.3f}")
```

### 个性化压力管理方案生成
```python
# 生成个性化压力管理方案
management_plan = stress_tester.generate_personalized_stress_management_plan(
    stress_profile=stress_report,
    individual_preferences="moderate_intervention_preference",
    time_commitment="15min_daily",
    intervention_types=["cognitive", "behavioral", "mindfulness"]
)

print("个性化压力管理方案:")
print("=" * 50)

# 即时干预策略
print("即时压力干预:")
for strategy in management_plan['immediate_strategies']:
    print(f"• {strategy['name']}")
    print(f"  适用压力等级: {strategy['applicable_stress_levels']}")
    print(f"  预期效果: {strategy['effectiveness_estimate']:.1%}")
    print(f"  实施难度: {strategy['difficulty_level']}")
    print()

# 长期发展计划
print("长期韧性发展:")
for goal in management_plan['long_term_development_goals']:
    print(f"• {goal['goal']}")
    print(f"  当前水平: {goal['current_level']:.1%}")
    print(f"  目标水平: {goal['target_level']:.1%}")
    print(f"  发展时间: {goal['estimated_timeframe']}")
    print(f"  具体方法: {', '.join(goal['development_methods'])}")
    print()
```

### 安全监控和危机干预
```python
# 启动增强安全监控
safety_monitor = stress_tester.get_safety_monitor()

# 设置安全阈值
safety_monitor.configure_thresholds({
    "distress_level_threshold": 0.8,
    "cognitive_overload_threshold": 0.75,
    "response_time_critical_threshold": 180,  # 3分钟
    "emotional_volatility_threshold": 0.6
})

# 启动实时监控
safety_monitor.start_real_time_monitoring(test_session.session_id)

# 定义危机干预协议
crisis_intervention_protocols = {
    "moderate_distress": {
        "trigger_level": 0.7,
        "interventions": [
            "暂停测试",
            "提供放松指导",
            "评估继续意愿"
        ],
        "follow_up_required": True
    },
    "severe_distress": {
        "trigger_level": 0.85,
        "interventions": [
            "立即停止测试",
            "启动危机干预",
            "联系心理健康专业人员",
            "提供即时支持资源"
        ],
        "clinical_referral": True
    },
    "emergency_situation": {
        "trigger_level": 0.95,
        "interventions": [
            "紧急停止所有测试活动",
            "立即启动应急响应程序",
            "联系紧急服务（如需要）",
            "确保参与者安全"
        ],
        "emergency_response": True
    }
}

safety_monitor.set_intervention_protocols(crisis_intervention_protocols)

# 监控测试过程中的安全状态
while stress_tester.is_test_running(test_session.session_id):
    safety_status = safety_monitor.get_current_safety_status(test_session.session_id)

    if safety_status['risk_level'] > 0.5:
        print(f"⚠️ 检测到安全风险: {safety_status['risk_indicators']}")

        # 根据风险级别启动相应干预
        if safety_status['risk_level'] >= 0.85:
            safety_monitor.activate_emergency_protocol(test_session.session_id)
            print("🚨 启动紧急安全协议")
            break
        elif safety_status['risk_level'] >= 0.7:
            safety_monitor.activate_moderate_intervention(test_session.session_id)
            print("⚡ 启动中等干预程序")

    time.sleep(30)

# 生成安全监控报告
safety_report = safety_monitor.generate_safety_monitoring_report(test_session.session_id)
print(f"安全监控完成，无安全事故发生: {safety_report['incidents_detected'] == 0}")
```

## 扩展接口

### 自定义压力场景
```python
class CustomStressScenario:
    def __init__(self, scenario_name, stress_parameters):
        self.scenario_name = scenario_name
        self.stress_parameters = stress_parameters

    def create_industry_specific_stress_test(self, industry_type, job_role):
        """创建行业特定的压力测试场景"""
        if industry_type == "healthcare":
            return self.create_medical_emergency_scenario()
        elif industry_type == "finance":
            return self.create_trading_floor_scenario()
        elif industry_type == "education":
            return self.create_classroom_management_scenario()

    def create_medical_emergency_scenario(self):
        return {
            "scenario_type": "medical_emergency",
            "stress_components": [
                "time_pressure_critical",
                "life_stakes_decision",
                "information_incompleteness",
                "team_coordination_pressure"
            ],
            "ethical_dilemmas": [
                "resource_allocation_decisions",
                "patient confidentiality_vs_public_safety",
                "professional_judgment_vs_protocols"
            ]
        }
```

### 集成外部生理监测
```python
class BiometricIntegration:
    def __init__(self, biometric_sensors):
        self.sensors = biometric_sensors

    def integrate_heart_rate_variability(self, hrv_data):
        """整合心率变异性数据"""
        stress_indicators = {
            "hrv_stress_index": self.calculate_hrv_stress(hrv_data),
            "autonomic_nervous_system_balance": self.assess_ans_balance(hrv_data),
            "physiological_stress_correlation": self.correlate_with_psychological_stress(hrv_data)
        }
        return stress_indicators

    def integrate_skin_conductance(self, eda_data):
        """整合皮肤电导响应数据"""
        return {
            "stress_response_amplitude": self.calculate_eda_amplitude(eda_data),
            "stress_recovery_speed": self.measure_eda_recovery(eda_data),
            "anticipatory_stress": self.detect_anticipatory_responses(eda_data)
        }
```

---

**版权所有**: © 2025 Portable PsyAgent. All Rights Reserved.
**技术许可**: MIT License
**最后更新**: 2025-01-07