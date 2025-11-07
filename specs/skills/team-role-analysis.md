# Team Role Analysis Skill Specification

## Skill Overview

**Skill Name**: `team-role-analysis`
**Version**: 1.0.0
**Author**: ptreezh <3061176@qq.com>
**License**: MIT License
**Website**: https://agentpsy.com

**Description**:
专业团队角色分析系统，基于贝尔宾团队角色理论和大五人格特征，深度分析个体在团队中的角色倾向、行为模式和协作风格。为团队建设、人员配置、组织发展提供科学的角色分析和优化建议。

## 功能特性

### 核心功能
- **贝尔宾角色识别**: 基于9种贝尔宾团队角色的精准识别和评估
- **多维度分析**: 结合人格特征、行为模式、沟通风格的综合分析
- **团队适配性评估**: 评估个体在不同团队类型和项目中的适配度
- **角色冲突分析**: 识别和解决潜在的角色冲突和团队动态问题
- **发展建议生成**: 提供个性化的角色发展建议和团队协作改善方案
- **团队配置优化**: 基于角色分析的科学团队配置和优化建议

### 贝尔宾团队角色
- **行动导向角色**: Shaper(塑造者)、Implementer(执行者)、Completer-Finisher(完善者)
- **社交导向角色**: Coordinator(协调者)、TeamWorker(合作者)、Resource Investigator(资源调查者)
- **思维导向角色**: Plant(创新者)、Monitor-Evaluator(评估者)、Specialist(专家)

## 输入输出格式

### 输入格式

#### 团队角色分析配置
```json
{
  "team_role_analysis_id": "team_role_20250107_001",
  "individual_id": "individual_001",
  "analysis_configuration": {
    "primary_framework": "belbin_team_roles",
    "supplementary_frameworks": ["big_five", "mbti", "cognitive_functions"],
    "analysis_depth": "comprehensive",
    "team_context": {
      "industry_type": "technology",
      "team_size": "8-12",
      "project_type": "innovative_development",
      "organizational_level": "middle_management"
    }
  },
  "assessment_data": {
    "personality_assessment": "big_five_results.json",
    "behavioral_patterns": "workplace_behavior.json",
    "team_experiences": "previous_team_roles.json",
    "communication_style": "communication_analysis.json",
    "problem_solving_approach": "cognitive_style.json"
  },
  "analysis_preferences": {
    "include_development_suggestions": true,
    "include_team_compatibility": true,
    "include_leadership_potential": true,
    "include_conflict_prediction": true,
    "include_role_evolution": true
  }
}
```

#### 团队环境配置
```json
{
  "team_environment": {
    "organizational_culture": "innovative_collaborative",
    "leadership_style": "transformational",
    "decision_making_process": "consensus_oriented",
    "communication_patterns": "open_transparent",
    "work_structure": "flexible_agile",
    "performance_expectations": "high_quality_fast_paced",
    "team_maturity": "forming_norming_stage"
  },
  "project_requirements": {
    "primary_objectives": ["innovation", "quality", "speed"],
    "required_skills": ["technical_expertise", "collaboration", "adaptability"],
    "challenge_level": "high_complexity",
    "stakeholder_complexity": "multiple_stakeholders",
    "time_constraints": "moderate_pressure"
  }
}
```

### 输出格式

#### 综合团队角色分析报告
```json
{
  "team_role_analysis_id": "team_role_20250107_001",
  "analysis_timestamp": "2025-01-07T17:10:00Z",
  "analysis_summary": {
    "primary_team_role": "TeamWorker",
    "secondary_team_roles": ["Coordinator", "Resource Investigator"],
    "role_confidence_score": 0.87,
    "team_fit_score": 0.91,
    "leadership_potential": 0.82,
    "adaptability_score": 0.85,
    "overall_analysis_quality": 0.89
  },
  "belbin_team_roles_analysis": {
    "primary_role": {
      "role_name": "TeamWorker",
      "role_category": "social_oriented",
      "role_score": 0.88,
      "confidence_level": 0.91,
      "role_description": "合作者 - 团队和谐的维护者和人际关系的润滑剂",
      "core_characteristics": [
        "高度的人际敏感度和同理心",
        "善于协调和调解人际关系",
        "注重团队和谐与凝聚力",
        "优秀的沟通和倾听能力",
        "乐于支持团队成员"
      ],
      "strengths": [
        "促进团队协作和团结",
        "调解团队内部冲突",
        "建立积极的工作氛围",
        "支持团队成员发展",
        "优秀的团队合作精神"
      ],
      "potential_weaknesses": [
        "可能避免必要冲突",
        "决策时可能过于考虑他人感受",
        "在严格问责方面可能表现不足",
        "对批评可能过于敏感"
      ],
      "behavioral_indicators": [
        "主动关心团队成员的状态",
        "在团队会议中促进共识",
        "帮助新成员融入团队",
        "维护团队士气和积极氛围",
        "协调不同意见和观点"
      ]
    },
    "secondary_roles": [
      {
        "role_name": "Coordinator",
        "role_category": "social_oriented",
        "role_score": 0.76,
        "confidence_level": 0.82,
        "role_description": "协调者 - 天生的领导者和目标导向的引导者",
        "contribution_style": "引导团队明确方向，协调各方努力达成目标",
        "when_most_effective": "在需要明确目标和方向时发挥作用"
      },
      {
        "role_name": "Resource Investigator",
        "role_category": "social_oriented",
        "role_score": 0.72,
        "confidence_level": 0.79,
        "role_description": "资源调查者 - 外部资源获取者和机会发现者",
        "contribution_style": "探索外部机会，建立外部联系",
        "when_most_effective": "在需要新资源和外部支持时发挥作用"
      }
    ],
    "least_preferred_roles": [
      {
        "role_name": "Shaper",
        "role_category": "action_oriented",
        "role_score": 0.34,
        "description": "较少的驱动和挑战倾向",
        "development_potential": "moderate"
      },
      {
        "role_name": "Monitor-Evaluator",
        "role_category": "thinking_oriented",
        "role_score": 0.41,
        "description": "较少的批判性分析倾向",
        "development_potential": "high"
      }
    ],
    "role_distribution_profile": {
      "action_oriented_total": 0.42,
      "social_oriented_total": 0.89,
      "thinking_oriented_total": 0.48,
      "role_balance_assessment": {
        "balance_score": 0.67,
        "balance_description": "偏重社交导向角色，在思维导向角色上有发展空间",
        "recommendations": ["发展批判性思维", "培养决策果断性", "增强执行力"]
      }
    }
  },
  "personality_role_correlation_analysis": {
    "big_five_correlations": {
      "openness_to_experience": {
        "correlation_strength": 0.68,
        "influence_on_team_role": "enhances_creativity_and_adaptability",
        "role_impact": "有助于资源调查者角色的发展"
      },
      "conscientiousness": {
        "correlation_strength": 0.74,
        "influence_on_team_role": "supports_reliability_and_follow_through",
        "role_impact": "支持协调者和合作者的可靠性特质"
      },
      "extraversion": {
        "correlation_strength": 0.91,
        "influence_on_team_role": "strongly_drives_social_roles",
        "role_impact": "显著驱动社交导向角色的表现"
      },
      "agreeableness": {
        "correlation_strength": 0.94,
        "influence_on_team_role": "primary_driver_of_teamworker_role",
        "role_impact": "团队合作者角色的主要驱动因素"
      },
      "neuroticism": {
        "correlation_strength": -0.72,
        "influence_on_team_role": "emotional_stability_supports_team_roles",
        "role_impact": "情绪稳定性支持团队角色的稳定性表现"
      }
    },
    "mbti_correlations": {
      "exfeeling_preference": {
        "correlation_strength": 0.89,
        "role_alignment": "perfect_fit_with_teamworker_and_coordinator",
        "description": "外向情感偏好与团队合作者和协调者角色完美匹配"
      },
      "intuitive_preference": {
        "correlation_strength": 0.76,
        "role_alignment": "supports_resource_investigator_role",
        "description": "直觉偏好支持资源调查者角色的创新思维"
      },
      "judging_preference": {
        "correlation_strength": 0.68,
        "role_alignment": "supports_coordinator_organizational_aspects",
        "description": "判断偏好支持协调者角色的组织方面"
      }
    },
    "cognitive_functions_impact": {
      "extraverted_feeling_dominance": {
        "impact_strength": 0.95,
        "role_enhancement": "strongly_enhances_teamworker_capabilities",
        "manifestations": [
          "天然的团队和谐意识",
          "对团队情绪的高度敏感",
          "主动的团队协调行为",
          "出色的人际沟通能力"
        ]
      },
      "introverted_intuition_auxiliary": {
        "impact_strength": 0.71,
        "role_enhancement": "supports_coordinator_strategic_thinking",
        "manifestations": [
          "对团队发展的直觉理解",
          "长期目标导向思维",
          "模式识别和趋势预测",
          "战略性的团队规划"
        ]
      }
    }
  },
  "team_behavioral_patterns_analysis": {
    "communication_style": {
      "primary_style": "collaborative_supportive",
      "style_characteristics": [
        "注重维护和谐的沟通氛围",
        "善于倾听和理解他人观点",
        "在沟通中表现出强烈的同理心",
        "促进不同意见的整合",
        "避免冲突性沟通方式"
      ],
      "strengths": [
        "建立信任和开放沟通",
        "调解沟通冲突",
        "促进团队共识",
        "创造积极的沟通环境"
      ],
      "development_areas": [
        "学习直接而友善的反馈",
        "在必要时表达不同意见",
        "提升批判性沟通能力"
      ]
    },
    "leadership_approach": {
      "primary_approach": "servant_transformational",
      "leadership_characteristics": [
        "以服务团队成员为基础",
        "关注团队成员的成长和发展",
        "通过激励和鼓舞来影响他人",
        "建立基于信任的领导关系",
        "重视团队合作胜过个人成就"
      ],
      "situational_adaptability": {
        "crisis_leadership": 0.65,
        "change_leadership": 0.82,
        "developmental_leadership": 0.94,
        "strategic_leadership": 0.71
      },
      "leadership_development_needs": [
        "提升在压力下的决策能力",
        "发展更果断的领导风格",
        "学习在维护和谐的同时推动变革"
      ]
    },
    "conflict_resolution_style": {
      "primary_style": "collaborative_accommodating",
      "conflict_approach": {
        "tendency": "寻求共赢解决方案",
        "avoidance_level": "moderate",
        "assertiveness_level": "low_moderate",
        "accommodation_level": "high"
      },
      "conflict_resolution_strengths": [
        "维护团队关系和信任",
        "促进各方理解",
        "寻求创造性解决方案",
        "减少冲突的负面情感影响"
      },
      "conflict_resolution_challenges": [
        "可能对重要决策妥协过多",
        "难以处理需要强硬立场的情况",
        "可能避免必要的建设性冲突"
      ]
    },
    "decision_making_patterns": {
      "decision_approach": "consensus_considerate",
      "decision_factors_priority": [
        {"factor": "team_impact", "weight": 0.35},
        {"factor": "stakeholder_consensus", "weight": 0.28},
        {"factor": "long_term_relationships", "weight": 0.22},
        {"factor": "objective_outcomes", "weight": 0.15}
      ],
      "decision_style_strengths": [
        "全面考虑决策影响",
        "获得团队支持和承诺",
        "维护团队团结",
        "促进决策执行"
      ],
      "decision_style_limitations": [
        "决策速度可能较慢",
        "可能过度妥协",
        "在紧急情况下需要提升效率"
      ]
    }
  },
  "team_compatibility_analysis": {
    "ideal_team_composition": {
      "preferred_team_size": "6-10人",
      "optimal_role_mix": {
        "social_roles_percentage": 40,
        "action_roles_percentage": 35,
        "thinking_roles_percentage": 25
      },
      "complementary_roles_needed": [
        {
          "role": "Shaper",
          "reason": "提供驱动力和挑战精神",
          "compatibility_score": 0.89
        },
        {
          "role": "Monitor-Evaluator",
          "reason": "提供客观分析和批判性思维",
          "compatibility_score": 0.85
        },
        {
          "role": "Implementer",
          "reason": "提供执行力和结构化思维",
          "compatibility_score": 0.82
        }
      ]
    },
    "role_conflict_risks": {
      "high_conflict_roles": [
        {
          "role": "Shaper",
          "conflict_source": "vs_直接性_vs_和谐性",
          "conflict_intensity": "moderate_high",
          "mitigation_strategies": [
            "明确分工和责任",
            "建立沟通协议",
            "寻求共同的价值观基础"
          ]
        }
      ],
      "collaborative_enhancement_roles": [
        {
          "role": "Coordinator",
          "synergy_type": "领导协作",
          "synergy_strength": "very_high",
          "combined_value": "卓越的团队领导和协调能力"
        },
        {
          "role": "Resource Investigator",
          "synergy_type": "内外资源整合",
          "synergy_strength": "high",
          "combined_value": "优秀的外部资源获取和团队整合"
        }
      ]
    },
    "project_type_fit": {
      "high_fit_projects": [
        {
          "project_type": "team_building_development",
          "fit_score": 0.96,
          "contribution_value": "卓越的团队建设和人员发展能力"
        },
        {
          "project_type": "customer_relationship_management",
          "fit_score": 0.93,
          "contribution_value": "优秀的人际关系管理和客户满意度提升"
        },
        {
          "project_type": "organizational_change_management",
          "fit_score": 0.89,
          "contribution_value": "有效的变革沟通和员工支持"
        }
      ],
      "moderate_fit_projects": [
        {
          "project_type": "strategic_planning",
          "fit_score": 0.75,
          "development_needs": ["战略分析能力", "客观评估技能"]
        },
        {
          "project_type": "crisis_management",
          "fit_score": 0.68,
          "development_needs": ["快速决策", "压力管理"]
        }
      ]
    }
  },
  "leadership_potential_analysis": {
    "leadership_readiness": {
      "overall_readiness_score": 0.82,
      "readiness_level": "high_ready_for_development",
      "development_timeline": "12-18个月"
    },
    "leadership_strengths": [
      {
        "strength": "emotional_intelligence_leadership",
        "score": 0.94,
        "description": "基于情商和同理心的领导能力",
        "applications": ["团队管理", "员工发展", "冲突解决"]
      },
      {
        "strength": "servant_leadership",
        "score": 0.91,
        "description": "服务导向的领导风格",
        "applications": ["团队建设", "文化塑造", "员工满意度"]
      },
      {
        "strength": "transformational_leadership",
        "score": 0.87,
        "description": "变革和激励导向的领导能力",
        "applications": ["组织变革", "创新推动", "团队激励"]
      }
    ],
    "leadership_development_areas": [
      {
        "area": "strategic_decision_making",
        "current_level": 0.65,
        "target_level": 0.85,
        "development_methods": [
          "战略思维培训",
          "案例分析学习",
          "导师指导",
          "实际项目经验"
        ]
      },
      {
        "area": "performance_management",
        "current_level": 0.58,
        "target_level": 0.80,
        "development_methods": [
          "绩效管理技能培训",
          "反馈技巧学习",
          "目标设定方法",
          "问责机制建立"
        ]
      },
      {
        "area": "change_leadership",
        "current_level": 0.72,
        "target_level": 0.88,
        "development_methods": [
          "变革管理理论学习",
          "变革项目参与",
          "领导力教练指导",
          "跨部门项目实践"
        ]
      }
    ],
    "optimal_leadership_contexts": [
      {
        "context": "team_development_projects",
        "suitability_score": 0.95,
        "reason": "完美契合团队建设和人员发展的领导需求"
      },
      {
        "context": "customer_success_teams",
        "suitability_score": 0.92,
        "reason": "优秀的客户关系管理和团队协调能力"
      },
      {
        "context": "organizational_culture_initiatives",
        "suitability_score": 0.89,
        "reason": "卓越的文化塑造和员工关系管理能力"
      }
    ]
  },
  "role_development_recommendations": {
    "primary_role_enhancement": {
      "role": "TeamWorker",
      "enhancement_focus": [
        "维持和发展核心优势",
        "扩大影响范围",
        "发展领导变体",
        "提升战略思维能力"
      ],
      "specific_development_actions": [
        {
          "action": "团队facilitator_training",
          "description": "获得专业的团队引导和促进技能",
          "expected_impact": "提升团队协调效果和影响力",
          "time_investment": "3-6个月",
          "priority": "high"
        },
        {
          "action": "advanced_emotional_intelligence",
          "description": "深化情商理解和应用技能",
          "expected_impact": "增强人际敏感度和影响力",
          "time_investment": "6-12个月",
          "priority": "high"
        }
      ]
    },
    "secondary_role_development": [
      {
        "role": "Coordinator",
        "current_proficiency": 0.76,
        "target_proficiency": 0.88,
        "development_methods": [
          "领导力技能培训",
          "战略思维发展",
          "项目管理实践",
          "决策能力提升"
        ],
        "development_timeline": "12-18个月"
      },
      {
        "role": "Resource Investigator",
        "current_proficiency": 0.72,
        "target_proficiency": 0.85,
        "development_methods": [
          "人脉网络建设技能",
          "机会识别和评估",
          "外部关系管理",
          "商务谈判技巧"
        ],
        "development_timeline": "9-15个月"
      }
    ],
    "challenge_role_development": [
      {
        "role": "Monitor-Evaluator",
        "development_motivation": "平衡过度和谐倾向",
        "development_approach": "渐进式批判性思维培养",
        "specific_methods": [
          "批判性思维课程",
          "数据分析技能培训",
          "独立思考练习",
          "客观反馈技能"
        ],
        "expected_difficulty": "moderate_high",
        "success_factors": ["持续练习", "反馈接受", "实践应用"]
      }
    ],
    "career_trajectory_suggestions": {
      "natural_progression_path": [
        "Team Member → Team Facilitator → Team Leader → People Manager",
        "从团队成员到团队管理者的发展路径"
      ],
      "alternative_paths": [
        "HR Business Partner → Organizational Development Consultant",
        "Customer Success Manager → Customer Success Leader",
        "Project Coordinator → Program Manager"
      ]
    }
  },
  "team_dynamics_impact": {
    "team_cohesion_contribution": {
      "contribution_score": 0.91,
      "specific_contributions": [
        "建立信任和开放沟通氛围",
        "促进团队共识和统一",
        "调解内部冲突和分歧",
        "提升团队士气和凝聚力",
        "支持新成员融入"
      ]
    },
    "team_performance_impact": {
      "performance_metrics": {
        "team_satisfaction_impact": 0.95,
        "team_retention_impact": 0.88,
        "collaboration_quality_impact": 0.92,
        "innovation_support_impact": 0.78,
        "goal_achievement_support": 0.81
      }
    },
    "organizational_culture_influence": {
      "culture_promotion": [
        "协作和互助文化",
        "员工关怀和发展文化",
        "开放沟通和透明文化",
        "包容性和多元化文化"
      ]
    }
  },
  "analysis_quality_and_validation": {
    "assessment_reliability": 0.89,
    "role_identification_confidence": 0.87,
    "predictive_validity": 0.84,
    "construct_validity": 0.86,
    "cross_validation_results": 0.82,
    "expert_review_alignment": 0.90,
    "self_assessment_alignment": 0.88,
    "peer_feedback_alignment": 0.85
  }
}
```

## 使用场景

### 1. 团队建设和人员配置
- 新团队成员的角色适配性评估
- 现有团队的角色配置优化
- 跨职能团队的组建和配置

### 2. 领导力发展
- 识别潜在的团队领导者
- 发展团队管理技能
- 提升团队协调和引导能力

### 3. 组织发展
- 团队效能提升和改进
- 组织文化建设
- 变革管理中的团队角色调整

### 4. 项目管理
- 项目团队角色分配
- 团队动态监控和管理
- 项目团队的优化和调整

## 技术实现要求

### 核心组件架构
```python
# 1. 贝尔宾角色分析引擎
class BelbinRoleAnalyzer:
    def __init__(self, role_model, assessment_framework)
    def analyze_primary_team_roles(self, personality_data)
    def calculate_role_fit_scores(self, individual_profile)
    def identify_secondary_roles(self, primary_analysis)
    def assess_role_conflicts(self, role_combination)

# 2. 团队适配性评估器
class TeamCompatibilityAssessor:
    def __init__(self, team_models, compatibility_framework)
    def assess_team_fit(self, individual_roles, team_context)
    def analyze_role_dynamics(self, team_composition)
    def predict_team_performance(self, role_configuration)
    def recommend_team_improvements(self, current_team)

# 3. 领导力潜力评估器
class LeadershipPotentialAssessor:
    def __init__(self, leadership_frameworks)
    def assess_leadership_readiness(self, team_role_profile)
    def identify_leadership_styles(self, role_combination)
    def evaluate_leadership_development_needs(self, current_profile)
    def create_leadership_development_plan(self, individual_profile)

# 4. 发展建议生成器
class RoleDevelopmentAdvisor:
    def __init__(self, development_frameworks, best_practices)
    def generate_role_enhancement_plans(self, current_roles)
    def create_skill_development_roadmaps(self, skill_gaps)
    def suggest_career_trajectories(self, role_profile)
    def recommend_training_interventions(self, development_needs)
```

### 贝尔宾角色评估模型
```python
# 贝尔宾角色评估配置
BELBIN_ROLE_ASSESSMENT_CONFIG = {
    "role_scoring_weights": {
      "plant": {
        "creativity": 0.30,
        "innovation": 0.25,
        "independence": 0.20,
        "problem_solving": 0.15,
        "strategic_thinking": 0.10
      },
      "resource_investigator": {
        "networking": 0.25,
        "exploration": 0.20,
        "communication": 0.20,
        "enthusiasm": 0.15,
        "opportunity_seeking": 0.20
      },
      "coordinator": {
        "leadership": 0.30,
        "delegation": 0.20,
        "clarification": 0.15,
        "goal_orientation": 0.20,
        "confidence": 0.15
      },
      "shaper": {
        "drive": 0.30,
        "challenge": 0.25,
        "courage": 0.20,
        "determination": 0.15,
        "urgency": 0.10
      },
      "monitor_evaluator": {
        "analytical_thinking": 0.30,
        "objectivity": 0.25,
        "critical_judgment": 0.20,
        "discretion": 0.15,
        "strategic_analysis": 0.10
      },
      "teamworker": {
        "cooperation": 0.30,
        "support": 0.25,
        "diplomacy": 0.20,
        "empathy": 0.15,
        "team_orientation": 0.10
      },
      "implementer": {
        "organization": 0.25,
        "efficiency": 0.20,
        "practicality": 0.20,
        "discipline": 0.15,
        "reliability": 0.20
      },
      "completer_finisher": {
        "attention_to_detail": 0.30,
        "quality_orientation": 0.25,
        "perfectionism": 0.20,
        "follow_through": 0.15,
        "anxiety_control": 0.10
      },
      "specialist": {
        "expertise": 0.40,
        "dedication": 0.20,
        "professionalism": 0.15,
        "knowledge_depth": 0.15,
        "continuous_learning": 0.10
      }
    },
    "role_conflict_matrix": {
      "plant_vs_shaper": "moderate_conflict",
      "resource_investigator_vs_specialist": "low_conflict",
      "coordinator_vs_shaper": "moderate_conflict",
      "monitor_evaluator_vs_teamworker": "moderate_conflict",
      "teamworker_vs_shaper": "moderate_conflict",
      "implementer_vs_plant": "low_conflict"
    },
    "team_balance_optimization": {
      "optimal_role_distribution": {
        "social_roles": "30-40%",
        "action_roles": "30-40%",
        "thinking_roles": "20-30%"
      },
      "team_size_adaptations": {
        "small_team_3_5": ["coordinator", "shaper", "implementer"],
        "medium_team_6_10": ["balanced_distribution"],
        "large_team_11_plus": ["multiple_specialists"]
      }
    }
}
```

### 团队环境适配模型
```python
# 团队环境适配配置
TEAM_ENVIRONMENT_MAPPING = {
    "industry_types": {
      "technology": {
        "preferred_roles": ["plant", "specialist", "monitor_evaluator"],
        "challenging_roles": ["teamworker"],
        "adaptation_factor": 0.85
      },
      "healthcare": {
        "preferred_roles": ["teamworker", "specialist", "completer_finisher"],
        "challenging_roles": ["shaper"],
        "adaptation_factor": 0.90
      },
      "finance": {
        "preferred_roles": ["monitor_evaluator", "implementer", "specialist"],
        "challenging_roles": ["plant"],
        "adaptation_factor": 0.80
      },
      "creative": {
        "preferred_roles": ["plant", "resource_investigator", "coordinator"],
        "challenging_roles": ["implementer"],
        "adaptation_factor": 0.95
      },
      "manufacturing": {
        "preferred_roles": ["implementer", "completer_finisher", "coordinator"],
        "challenging_roles": ["plant"],
        "adaptation_factor": 0.75
      }
    },
    "organizational_cultures": {
      "innovative": {
        "role_enhancement": ["plant", "resource_investigator"],
        "role_challenges": ["implementer", "completer_finisher"]
      },
      "hierarchical": {
        "role_enhancement": ["coordinator", "implementer"],
        "role_challenges": ["plant", "shaper"]
      },
      "collaborative": {
        "role_enhancement": ["teamworker", "coordinator"],
        "role_challenges": ["shaper", "monitor_evaluator"]
      },
      "competitive": {
        "role_enhancement": ["shaper", "resource_investigator"],
        "role_challenges": ["teamworker", "implementer"]
      }
    }
}
```

## 示例代码

### 基础团队角色分析
```python
from skills.team_role_analysis import TeamRoleAnalysis

# 创建团队角色分析实例
team_analyzer = TeamRoleAnalysis(
    belbin_framework=True,
    personality_integration=True,
    context_adaptation=True
)

# 准备分析数据
analysis_input = {
    "personality_data": load_big_five_results("individual_001.json"),
    "mbti_profile": load_mbti_results("individual_001.json"),
    "behavioral_observations": load_workplace_behavior("individual_001.json"),
    "team_experiences": load_team_history("individual_001.json"),
    "team_context": {
        "industry": "technology",
        "team_size": 8,
        "project_type": "product_development"
    }
}

# 启动团队角色分析
analysis_session = team_analyzer.start_role_analysis(
    individual_data=analysis_input,
    analysis_depth="comprehensive",
    include_development_suggestions=True
)

# 监控分析进度
while not analysis_session.is_complete():
    progress = team_analyzer.get_analysis_progress(analysis_session.session_id)

    print(f"""
    团队角色分析进度:
    - 当前阶段: {progress['current_analysis_stage']}
    - 完成度: {progress['completion_percentage']:.1f}%
    - 角色识别置信度: {progress['role_identification_confidence']:.3f}
    - 剩余时间: {progress['estimated_time_remaining']}
    """)

    time.sleep(3)

# 获取团队角色分析报告
team_role_report = team_analyzer.get_team_role_report(analysis_session.session_id)

print("团队角色分析完成:")
print(f"主要角色: {team_role_report['belbin_team_roles_analysis']['primary_role']['role_name']}")
print(f"角色置信度: {team_role_report['belbin_team_roles_analysis']['primary_role']['confidence_level']:.3f}")
print(f"团队适配度: {team_role_report['team_compatibility_analysis']['ideal_team_composition']['role_balance_assessment']['balance_score']:.3f}")
```

### 团队配置优化分析
```python
# 进行团队配置优化
team_optimization = team_analyzer.optimize_team_composition(
    existing_team_members=[
        {"id": "member_001", "primary_role": "Plant"},
        {"id": "member_002", "primary_role": "Shaper"},
        {"id": "member_003", "primary_role": "Monitor-Evaluator"}
    ],
    target_team_size=10,
    project_requirements={
        "innovation_level": "high",
        "execution_speed": "medium",
        "quality_requirements": "high"
    }
)

print("团队配置优化建议:")
print("=" * 50)

# 分析当前团队配置
current_analysis = team_optimization['current_team_analysis']
print(f"当前团队角色平衡评分: {current_analysis['balance_score']:.3f}")
print(f"角色覆盖率: {current_analysis['role_coverage']:.1%}")
print(f"主要优势: {', '.join(current_analysis['strengths'])}")
print(f"主要缺口: {', '.join(current_analysis['gaps'])}")
print()

# 获取推荐的角色补充
recommended_roles = team_optimization['recommended_additions']
print("推荐补充的团队角色:")
for recommendation in recommended_roles:
    print(f"🎯 {recommendation['role']}")
    print(f"   适配度: {recommendation['fit_score']:.1%}")
    print(f"   解决问题: {recommendation['addresses_gaps']}")
    print(f"   优先级: {recommendation['priority']}")
    print()
```

### 领导力发展分析
```python
# 进行领导力潜力分析
leadership_analysis = team_analyzer.analyze_leadership_potential(
    team_role_profile=team_role_report,
    leadership_context="people_management",
    career_stage="mid_level"
)

# 分析领导力准备度
leadership_readiness = leadership_analysis['leadership_readiness']
print(f"领导力准备度评分: {leadership_readiness['overall_readiness_score']:.3f}")
print(f"准备度等级: {leadership_readiness['readiness_level']}")
print(f"发展时间预期: {leadership_readiness['development_timeline']}")
print()

# 分析领导力优势
leadership_strengths = leadership_analysis['leadership_strengths']
print("核心领导力优势:")
for strength in leadership_strengths:
    print(f"💪 {strength['strength']}")
    print(f"   评分: {strength['score']:.3f}")
    print(f"   描述: {strength['description']}")
    print(f"   应用场景: {', '.join(strength['applications'])}")
    print()

# 生成领导力发展计划
leadership_development = team_analyzer.create_leadership_development_plan(
    current_profile=leadership_analysis,
    target_level="senior_leader",
    time_horizon="18_months"
)

print("个性化领导力发展计划:")
print("=" * 50)

for phase in leadership_development['development_phases']:
    print(f"📅 阶段: {phase['phase_name']} ({phase['duration']})")
    print(f"目标: {phase['development_objectives']}")
    print(f"发展行动:")
    for action in phase['development_actions']:
        print(f"  • {action}")
    print()
```

### 角色冲突分析和解决
```python
# 进行角色冲突分析
conflict_analysis = team_analyzer.analyze_role_conflicts(
    individual_roles=team_role_report['belbin_team_roles_analysis'],
    team_environment={
        "existing_team_roles": ["Shaper", "Monitor-Evaluator", "Implementer"],
        "team_culture": "competitive",
        "decision_making_style": "consensus_based"
    }
)

# 识别潜在冲突
potential_conflicts = conflict_analysis['potential_conflicts']
print("潜在角色冲突分析:")
for conflict in potential_conflicts:
    print(f"⚠️ 冲突类型: {conflict['conflict_type']}")
    print(f"   冲突强度: {conflict['conflict_intensity']}")
    print(f"   冲突原因: {conflict['conflict_source']}")
    print(f"   可能表现: {conflict['potential_manifestations']}")
    print()

# 获取冲突解决策略
conflict_resolution = team_analyzer.generate_conflict_resolution_strategies(
    conflict_analysis=conflict_analysis,
    individual_style="collaborative_accommodating"
)

print("冲突解决策略:")
print("=" * 50)

for strategy in conflict_resolution['resolution_strategies']:
    print(f"🔧 策略: {strategy['strategy_name']}")
    print(f"   适用场景: {strategy['applicable_situations']}")
    print(f"   具体方法: {', '.join(strategy['concrete_methods'])}")
    print(f"   预期效果: {strategy['expected_outcome']}")
    print()
```

### 职业发展路径规划
```python
# 生成职业发展路径
career_planning = team_analyzer.create_career_development_path(
    current_team_role_profile=team_role_report,
    career_preferences=["leadership", "team_development", "organizational_impact"],
    industry_context="technology",
    growth_timeline="5_years"
)

# 分析自然发展路径
natural_path = career_planning['natural_progression_path']
print("自然职业发展路径:")
for i, stage in enumerate(natural_path, 1):
    print(f"{i}. {stage['title']}")
    print(f"   描述: {stage['description']}")
    print(f"   预期时间: {stage['timeframe']}")
    print(f"   关键发展: {stage['key_developments']}")
    print()

# 分析替代发展路径
alternative_paths = career_planning['alternative_paths']
print("替代发展路径:")
for path in alternative_paths:
    print(f"🛤️ {path['path_name']}")
    print(f"   适合性: {path['suitability_score']:.1%}")
    print(f"   发展机会: {path['development_opportunities']}")
    print(f"   所需技能: {', '.join(path['required_skills'])}")
    print()

# 生成技能发展计划
skill_development = team_analyzer.generate_skill_development_plan(
    current_skills=team_role_report,
    target_role_suitabilities=["Coordinator", "Resource Investigator"],
    development_timeframe="24_months"
)

print("技能发展计划:")
print("=" * 50)

for skill_area in skill_development['development_areas']:
    print(f"📚 {skill_area['skill_category']}")
    print(f"当前水平: {skill_area['current_level']:.1%}")
    print(f"目标水平: {skill_area['target_level']:.1%}")
    print(f"发展方法:")
    for method in skill_area['development_methods']:
        print(f"  • {method['method']}: {method['description']}")
    print()
```

## 扩展接口

### 自定义团队角色模型
```python
class CustomTeamRoleModel:
    def __init__(self, model_name, theoretical_framework):
        self.model_name = model_name
        self.theoretical_framework = theoretical_framework

    def integrate_with_analyzer(self, team_analyzer):
        """将自定义团队角色模型集成到分析系统中"""
        team_analyzer.register_custom_role_model(
            self.model_name,
            self.theoretical_framework,
            self.custom_role_assessment_function
        )

    def custom_role_assessment_function(self, individual_data):
        """自定义的角色评估函数"""
        # 实现特定团队的评估逻辑
        pass

    def validate_model_accuracy(self, validation_data):
        """验证自定义模型的准确性"""
        # 实现模型验证逻辑
        pass
```

### 动态团队监控
```python
class DynamicTeamMonitor:
    def __init__(self, monitoring_frequency, analysis_depth):
        self.monitoring_frequency = monitoring_frequency
        self.analysis_depth = analysis_depth

    def monitor_team_dynamics(self, team_id, role_profiles):
        """持续监控团队动态和角色表现"""
        dynamics_data = {
            "role_performance_trends": [],
            "team_cohesion_metrics": [],
            "conflict_indicators": [],
            "productivity_correlations": []
        }
        return dynamics_data

    def detect_role_evolution(self, individual_id, longitudinal_data):
        """检测个体角色的演变和发展"""
        return {
            "role_strength_changes": [],
            "new_role_emergence": [],
            "developmental_milestones": [],
            "adaptive_strategies": []
        }
```

---

**版权所有**: © 2025 Portable PsyAgent. All Rights Reserved.
**技术许可**: MIT License
**最后更新**: 2025-01-07