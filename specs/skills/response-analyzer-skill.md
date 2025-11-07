# Response Analyzer Skill

## 技能名称
`response-analyzer` - 问卷回答分析技能

## 核心功能
分析问卷回答结果，提供专业的心理评估和详细分析报告

## 使用方式

### 基础分析
```bash
# 基础大五人格分析
claude code --print "请分析这份问卷回答，计算大五人格得分" \
  --file responses.json \
  --analysis-type big_five

# 保存分析结果
claude code --print "分析问卷回答并生成详细报告" \
  --file responses.json \
  --analysis detailed \
  --save analysis_report.json
```

### 指定分析模型
```bash
# 大五人格分析
claude code --print "请进行大五人格专业分析" \
  --file responses.json \
  --model big_five \
  --include percentiles

# MBTI类型分析
claude code --print "请推断MBTI类型和认知功能" \
  --file responses.json \
  --model mbti \
  --include cognitive_stack

# 贝尔宾团队角色分析
claude code --print "请分析团队角色倾向和协作风格" \
  --file responses.json \
  --model belbin

# 综合分析
claude code --print "请进行全面心理分析，包含大五人格、MBTI、贝尔宾团队角色" \
  --file responses.json \
  --model comprehensive
```

### 分析深度设置
```bash
# 基础分析
claude code --print "提供基础的人格特征分析" \
  --file responses.json \
  --depth basic

# 详细分析
claude code --print "提供详细的心理特征分析和发展建议" \
  --file responses.json \
  --depth detailed

# 专业分析
claude code --print "作为心理学专家提供专业评估和临床见解" \
  --file responses.json \
  --depth professional
```

### 专业视角设置
```bash
# 临床心理学视角
claude code --print "请以临床心理学专家视角分析" \
  --file responses.json \
  --expertise clinical_psychology

# 组织心理学视角
claude code --print "请以组织心理学专家视角分析" \
  --file responses.json \
  --expertise organizational_psychology

# 发展心理学视角
claude code --print "请以发展心理学专家视角分析" \
  --file responses.json \
  --expertise developmental_psychology
```

## 输入格式

### 回答文件格式 (responses.json)
```json
{
  "session_info": {
    "respondent_id": "user_001",
    "timestamp": "2025-01-07T15:30:00Z"
  },
  "responses": [
    {
      "question_id": "Q1",
      "question": "我喜欢尝试新事物和体验",
      "answer": 4,
      "reasoning": "我对新体验持开放态度"
    },
    {
      "question_id": "Q2",
      "question": "我做事很有条理和计划性",
      "answer": 3,
      "reasoning": "计划性适中，根据情况调整"
    }
  ]
}
```

### 分析参数说明

#### 分析模型 (model)
- **big_five**: 大五人格分析
- **mbti**: MBTI人格类型分析
- **belbin**: 贝尔宾团队角色分析
- **comprehensive**: 综合多模型分析

#### 分析深度 (depth)
- **basic**: 基础特征描述
- **detailed**: 详细分析和建议
- **professional**: 专业级评估

#### 专业视角 (expertise)
- **clinical_psychology**: 临床心理学
- **organizational_psychology**: 组织心理学
- **developmental_psychology**: 发展心理学
- **educational_psychology**: 教育心理学

## 输出格式

### 基础分析结果格式
```json
{
  "analysis_metadata": {
    "analyst": "AI心理学专家",
    "analysis_date": "2025-01-07T15:35:00Z",
    "analysis_type": "big_five",
    "confidence_level": 0.87,
    "expertise_level": "professional"
  },
  "big_five_results": {
    "openness": {
      "raw_score": 4.2,
      "percentile": 85,
      "level": "high",
      "description": "高度开放，富有创造力和好奇心",
      "behavioral_indicators": [
        "喜欢抽象思维和新体验",
        "对艺术和美学有高度敏感度",
        "思维灵活，善于连接不同概念"
      ]
    },
    "conscientiousness": {
      "raw_score": 3.6,
      "percentile": 72,
      "level": "moderate_high",
      "description": "中等偏高的尽责性，有计划性但保持灵活性",
      "behavioral_indicators": [
        "能够制定和遵循计划",
        "注意细节和准确性",
        "在面对变化时保持适应性"
      ]
    },
    "extraversion": {
      "raw_score": 4.5,
      "percentile": 90,
      "level": "high",
      "description": "高度外向，善于社交和领导",
      "behavioral_indicators": [
        "在社交场合感到舒适和充满活力",
        "善于表达和沟通",
        "具有天然的领导影响力"
      ]
    },
    "agreeableness": {
      "raw_score": 3.9,
      "percentile": 78,
      "level": "moderate_high",
      "description": "高度友善和合作，重视人际和谐",
      "behavioral_indicators": [
        "关心他人感受和需求",
        "倾向于合作而非对抗",
        "建立和维护良好的人际关系"
      ]
    },
    "neuroticism": {
      "raw_score": 2.1,
      "percentile": 25,
      "level": "low",
      "description": "情绪稳定，抗压能力强",
      "behavioral_indicators": [
        "在压力环境下保持相对冷静",
        "能够快速从负面情绪中恢复",
        "具有较好的情绪调节能力"
      ]
    }
  },
  "mbti_inference": {
    "type": "ENFJ",
    "confidence": 0.85,
    "cognitive_functions": {
      "dominant": "Fe (Extraverted Feeling)",
      "auxiliary": "Ni (Introverted Intuition)",
      "tertiary": "Se (Extraverted Sensing)",
      "inferior": "Ti (Introverted Thinking)"
    },
    "description": "主人公型：天生的领导者和导师，富有同理心和影响力"
  },
  "team_roles": {
    "primary_role": "Coordinator",
    "secondary_roles": ["TeamWorker", "Resource Investigator"],
    "leadership_style": "transformational",
    "team_contribution": "协调者-支持者"
  },
  "analysis_summary": {
    "overall_profile": "富有同理心的外向型领导，具有很强的社会影响力",
    "key_strengths": ["同理心", "领导力", "沟通能力", "社会影响力"],
    "development_areas": ["边界设定", "决策果断性", "批判性思维"],
    "quality_assessment": {
      "response_consistency": "high",
      "pattern_recognition": "clear",
      "clinical_validity": "good"
    }
  }
}
```

### 详细分析报告格式
```json
{
  "analysis_metadata": {
    "analyst": "AI临床心理学专家",
    "analysis_date": "2025-01-07T15:35:00Z",
    "expertise_level": "professional"
  },
  "comprehensive_analysis": {
    "personality_profile": {
      "core_identity": "ENFJ主人公型 - 富有同理心的领导者和导师",
      "strengths": [
        "天生的同理心和人际敏感度",
        "优秀的沟通和激励能力",
        "强烈的责任感和帮助他人的愿望",
        "在团队中具有天然的影响力"
      ],
      "potential_challenges": [
        "可能过度关注他人需求而忽视自己",
        "在必要时难以做出不受欢迎的决定",
        "可能因过度和谐而回避必要冲突"
      ]
    },
    "career_guidance": {
      "high_fit_careers": [
        {
          "career": "心理咨询师",
          "fit_score": 0.95,
          "reasons": ["完美匹配同理心和帮助他人动机", "需要强大的沟通能力"]
        },
        {
          "career": "人力资源经理",
          "fit_score": 0.90,
          "reasons": ["需要人际协调和团队建设能力", "适合发展型角色"]
        }
      ],
      "development_suggestions": [
        "培养更客观的决策能力",
        "学习在必要时设立健康界限",
        "发展批判性思维和分析能力"
      ]
    },
    "relationship_dynamics": {
      "communication_style": "温暖、支持性、富有同理心",
      "conflict_resolution": "倾向于寻求和谐，可能需要发展更直接的处理方式",
      "leadership_approach": "服务型领导，关注团队成员的成长和发展",
      "team_preferences": "重视团队和谐，在合作环境中表现最佳"
    },
    "stress_response_patterns": {
      "strengths": [
        "在支持性环境中表现出韧性",
        "能够利用人际关系资源应对压力",
        "在帮助他人时获得力量"
      ],
      "vulnerabilities": [
        "可能过度承担他人情绪负担",
        "在面对人际冲突时容易受到影响",
        "可能因过度共情而忽略自我照顾"
      ]
    }
  },
  "professional_recommendations": {
    "personal_growth": [
      "发展更健康的自我边界",
      "学习平衡他人需求与自我需求",
      "培养必要的批判性思维和客观分析能力"
    ],
    "relationship_improvement": [
      "练习在必要时直接而友善地表达不同意见",
      "学习处理人际冲突的建设性方法",
      "在保持同理心的同时维护个人立场"
    ],
    "career_development": [
      "继续发展领导力和影响力技能",
        "考虑发展专业咨询或辅导技能",
        "学习组织变革和项目管理技能"
    ]
  },
  "clinical_observations": {
    "mental_health_indicators": "总体健康，具有良好的心理韧性基础",
    "risk_factors": ["可能存在过度承担他人情绪负担的风险"],
    "protective_factors": ["良好的社交支持系统", "强烈的目标感和价值观"],
    "monitoring_suggestions": ["注意工作生活平衡", "定期进行自我反思和调整"]
  }
}
```

## 具体使用示例

### 示例1: 快速人格评估
```bash
claude code --print "请快速分析这份问卷，提供主要人格特征" \
  --file responses.json \
  --analysis-type big_five \
  --depth basic
```

### 示例2: 职业发展分析
```bash
claude code --print "请基于问卷回答提供职业发展建议" \
  --file responses.json \
  --model comprehensive \
  --expertise organizational_psychology \
  --depth detailed
```

### 示例3: 团队角色分析
```bash
claude code --print "请分析团队角色倾向和协作建议" \
  --file responses.json \
  --model belbin \
  --include team_compatibility
```

### 示例4: 专业临床评估
```bash
claude code --print "请作为临床心理学专家进行专业评估" \
  --file responses.json \
  --model comprehensive \
  --expertise clinical_psychology \
  --depth professional
```

### 示例5: 批量分析
```bash
# 分析多个团队成员的问卷
for response_file in team_responses/*.json; do
  claude code --print "分析团队成员心理特征" \
    --file "$response_file" \
    --model comprehensive \
    --save "analysis_$(basename "$response_file")"
done
```

## 技能特点

### 1. 多模型支持
- 集成多个成熟的心理测量模型
- 提供交叉验证和分析
- 支持自定义分析框架

### 2. 专业视角
- 不同心理学专业领域的分析角度
- 基于理论和实证研究的分析
- 临床和实用性并重的评估

### 3. 可调节深度
- 从基础到专业的多层次分析
- 根据需求调整分析详细程度
- 灵活的输出格式控制

### 4. 实用导向
- 提供具体的行动建议
- 关注实际应用场景
- 包含发展和改进方案

### 5. 质量保证
- 置信度和可靠性评估
- 一致性检查机制
- 异常模式识别

这个技能专注于专业级的问卷分析，可以为各种应用场景提供可靠的心理评估服务。