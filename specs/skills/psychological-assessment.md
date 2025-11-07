# Psychological Assessment Skill Specification

## Skill Overview

**Skill Name**: `psychological-assessment`
**Version**: 1.0.0
**Author**: ptreezh <3061176@qq.com>
**License**: MIT License
**Website**: https://agentpsy.com

**Description**:
使用AI大模型进行专业的心理评估和性格分析，支持大五人格、MBTI、贝尔宾团队角色等多种心理测量模型。

## 功能特性

### 核心功能
- **多理论模型支持**: 支持大五人格(Big Five)、MBTI、贝尔宾(Belbin)团队角色评估
- **智能角色模拟**: 支持多种人格角色的AI模拟回答
- **压力测试分析**: 支持情绪压力、认知陷阱等压力测试机制
- **多模型支持**: 兼容OpenRouter、Ollama等多种AI模型提供商
- **实时评估**: 支持单次评估和批量处理模式
- **质量控制**: 多模型共识机制确保评估结果可靠性

### 评估模型
- **大五人格模型**: 开放性、尽责性、外向性、宜人性、神经质
- **MBTI模型**: 16种人格类型推断
- **贝尔宾团队角色**: 9种团队角色分析
- **动机模式分析**: 深层动机和需求分析

## 输入输出格式

### 输入格式

#### 单次评估输入
```json
{
  "assessment_type": "bigfive|mbti|belbin|comprehensive",
  "questions": [
    {
      "id": "q1",
      "question": "我通常喜欢成为众人关注的焦点",
      "options": ["完全不同意", "不太同意", "中立", "比较同意", "完全同意"],
      "scale": [1, 2, 3, 4, 5]
    }
  ],
  "personality_role": "a1|a2|...|def",  // 可选：20种预定义角色
  "stress_level": 0,  // 可选：0-4级压力
  "cognitive_traps": ["paradox", "circular", "semantic", "procedural"],  // 可选：认知陷阱类型
  "context": "职场环境评估"  // 可选：评估上下文
}
```

#### 文本输入
```text
# 直接输入问答文本
请根据以下问题进行心理评估：
1. 我通常喜欢成为众人关注的焦点
2. 我喜欢尝试新的体验和活动
...
```

### 输出格式

```json
{
  "assessment_id": "psych_assess_20241201_001",
  "timestamp": "2024-12-01T10:30:00Z",
  "model_info": {
    "model": "anthropic/claude-3.5-sonnet",
    "provider": "openrouter",
    "temperature": 0.7
  },
  "personality_role": "a1",
  "stress_level": 0,
  "results": {
    "big_five": {
      "openness": {
        "score": 4.2,
        "level": "high",
        "description": "开放性：喜欢新体验，富有想象力，思维开放"
      },
      "conscientiousness": {
        "score": 3.8,
        "level": "moderate_high",
        "description": "尽责性：有条理，可靠性强，注重细节"
      },
      "extraversion": {
        "score": 4.5,
        "level": "high",
        "personality_role_confirmed": true,
        "description": "外向性：善于社交，精力充沛，享受人际互动"
      },
      "agreeableness": {
        "score": 3.5,
        "level": "moderate",
        "description": "宜人性：友善合作，重视和谐"
      },
      "neuroticism": {
        "score": 2.1,
        "level": "low",
        "description": "神经质：情绪稳定，压力下表现良好"
      }
    },
    "mbti": {
      "type": "ENFJ",
      "confidence": 0.85,
      "cognitive_functions": {
        "dominant": "Fe",
        "auxiliary": "Ni",
        "tertiary": "Se",
        "inferior": "Ti"
      }
    },
    "belbin": {
      "team_roles": ["Coordinator", "TeamWorker"],
      "strengths": ["协调沟通", "团队合作"],
      "weaknesses": ["避免冲突", "过于民主"]
    },
    "motivation": {
      "primary": "成就动机",
      "secondary": "关系动机",
      "avoidance": "权力动机"
    }
  },
  "confidence_score": 0.87,
  "reliability_score": 0.92,
  "analysis_notes": [
    "回答一致性高，无矛盾模式",
    "人格角色与评估结果高度匹配",
    "压力水平适中，回答真实可靠"
  ],
  "recommendations": [
    "适合需要创意和人际交往的工作环境",
    "建议发展决策能力和独立性",
    "可考虑管理或咨询类职业发展路径"
  ]
}
```

## 使用场景

### 1. 个人发展
- 职业规划和职业选择
- 个人成长和自我认知
- 心理健康评估

### 2. 人才评估
- 招聘和选拔评估
- 团队建设分析
- 领导力评估

### 3. 组织发展
- 团队角色匹配
- 组织文化适配分析
- 压力管理咨询

### 4. 教育咨询
- 学习风格分析
- 个性化教育方案
- 心理健康辅导

## 技术实现要求

### 核心组件
```python
# 1. 评估引擎
class PsychologicalAssessmentEngine:
    def __init__(self, model_config, assessment_config)
    def assess_personality(self, input_data)
    def apply_stress_test(self, base_result, stress_level)
    def generate_comprehensive_report(self, assessment_results)

# 2. 模型客户端
class ModelClient:
    def __init__(self, provider, api_key)
    def chat_completion(self, messages, parameters)
    def get_available_models(self)
    def calculate_cost(self, usage)

# 3. 评估器配置
class AssessmentConfig:
    def __init__(self)
    def get_personality_roles(self)
    def get_stress_levels(self)
    def get_cognitive_traps(self)

# 4. 结果分析器
class ResultAnalyzer:
    def __init__(self)
    def analyze_big_five(self, responses)
    def infer_mbti_type(self, big_five_scores)
    def identify_belbin_roles(self, responses)
    def calculate_confidence(self, results)
```

### 模型支持
```python
# 支持的AI模型提供商
SUPPORTED_PROVIDERS = {
    "openrouter": {
        "anthropic/claude-3.5-sonnet": "高质量评估",
        "openai/gpt-4o": "快速评估",
        "anthropic/claude-3-haiku": "经济评估"
    },
    "ollama": {
        "llama3.1": "本地开源模型",
        "mistral": "本地小模型",
        "qwen2.5": "中文优化模型"
    },
    "direct": {
        "anthropic": "直接API调用",
        "openai": "直接API调用"
    }
}
```

## 参数配置

### 模型配置参数
```python
DEFAULT_MODEL_CONFIG = {
    "temperature": 0.7,          # 创造性程度：0.0-1.0
    "max_tokens": 4096,        # 最大生成长度
    "top_p": 0.9,             # 核采样参数
    "frequency_penalty": 0.0,   # 频率惩罚
    "presence_penalty": 0.0     # 存在惩罚
}
```

### 评估配置参数
```python
ASSESSMENT_CONFIG = {
    "personality_roles": {
        "a1": {"description": "积极主动型", "mbti_tendency": "E"},
        "a2": {"description": "分析思考型", "mbti_tendency": "NT"},
        # ... 更多角色定义
    },
    "stress_levels": {
        0: "无压力",
        1: "轻微压力",
        2: "中等压力",
        3: "高度压力",
        4: "极端压力"
    },
    "cognitive_traps": {
        "paradox": "悖论思维",
        "circular": "循环论证",
        "semantic": "语义模糊",
        "procedural": "程序固化"
    }
}
```

## 示例代码

### 基础心理评估
```python
from skills.psychological_assessment import PsychologicalAssessment

# 创建评估实例
assessor = PsychologicalAssessment(
    model_provider="openrouter",
    model_name="anthropic/claude-3.5-sonnet"
)

# 进行大五人格评估
result = assessor.assess(
    assessment_type="bigfive",
    personality_role="a1",
    stress_level=1
)

print(f"大五人格评估结果: {result['results']['big_five']}")
print(f"置信度: {result['confidence_score']}")
```

### 综合心理分析
```python
# 综合评估（大五人格 + MBTI + 贝尔宾）
comprehensive_result = assessor.assess(
    assessment_type="comprehensive",
    personality_role="def",
    stress_level=2,
    cognitive_traps=["paradox", "semantic"]
)

print(f"MBTI类型: {comprehensive_result['results']['mbti']['type']}")
print(f"贝尔宾角色: {comprehensive_result['results']['belbin']['team_roles']}")
```

### 批量评估处理
```python
# 批量处理多个评估
assessment_inputs = [
    {"assessment_type": "bigfive", "data": person1_data},
    {"assessment_type": "mbti", "data": person2_data},
    {"assessment_type": "belbin", "data": person3_data}
]

batch_results = []
for input_config in assessment_inputs:
    result = assessor.assess(**input_config)
    batch_results.append(result)

# 生成批量分析报告
batch_report = assessor.generate_batch_report(batch_results)
```

### 自定义配置
```python
# 自定义评估配置
custom_config = {
    "model": {
        "provider": "ollama",
        "name": "llama3.1",
        "temperature": 0.5
    },
    "assessment": {
        "stress_level": 3,
        "personality_role": "a5",
        "timeout": 300
    }
}

custom_assessor = PsychologicalAssessment(config=custom_config)
result = custom_assessor.assess(
    assessment_type="bigfive",
    input_data=custom_questions
)
```

## 错误处理机制

### 1. 模型连接错误
```python
try:
    result = assessor.assess(input_data)
except ModelConnectionError as e:
    # 自动切换到备用模型
    assessor.switch_to_fallback_model()
    result = assessor.assess(input_data)
except ModelResponseError as e:
    # 重试机制
    result = assessor.assess_with_retry(input_data, max_retries=3)
```

### 2. 输入验证错误
```python
def validate_assessment_input(input_data):
    """验证评估输入数据"""
    required_fields = ["assessment_type"]
    if not all(field in input_data for field in required_fields):
        raise ValueError("缺少必需字段: assessment_type")

    valid_types = ["bigfive", "mbti", "belbin", "comprehensive"]
    if input_data["assessment_type"] not in valid_types:
        raise ValueError(f"不支持的评估类型: {input_data['assessment_type']}")
```

### 3. 结果质量检查
```python
def check_result_quality(result):
    """检查评估结果质量"""
    if result["confidence_score"] < 0.6:
        return {"warning": "评估结果置信度较低，建议重新评估"}

    if result["reliability_score"] < 0.7:
        return {"warning": "评估结果可靠性一般，建议补充评估"}

    return {"status": "评估质量良好"}
```

### 4. 资源管理
```python
class ResourceManager:
    def __init__(self):
        self.session_count = 0
        self.token_usage = 0

    def monitor_usage(self):
        """监控资源使用情况"""
        if self.session_count > 1000:
            return {"warning": "会话数量过多，建议暂停"}

        if self.token_usage > 100000:
            return {"warning": "Token使用量过大，建议检查成本"}

        return {"status": "资源使用正常"}
```

## 扩展接口

### 自定义评估器
```python
class CustomAssessor(PsychologicalAssessment):
    def __init__(self, config):
        super().__init__(config)
        self.add_custom_assessor("custom_theory")

    def add_custom_assessor(self, theory_name):
        """添加自定义评估理论"""
        setattr(self, f"assess_{theory_name}", self._custom_assess)

    def _custom_assess(self, input_data):
        """自定义评估实现"""
        # 实现自定义评估逻辑
        pass
```

### 插件机制
```python
class AssessmentPlugin:
    def __init__(self):
        self.preprocessors = []
        self.postprocessors = []

    def register_preprocessor(self, func):
        """注册预处理插件"""
        self.preprocessors.append(func)

    def register_postprocessor(self, func):
        """注册后处理插件"""
        self.postprocessors.append(func)
```

## 版本更新日志

### v1.0.0 (2024-12-01)
- 初始版本发布
- 支持大五人格、MBTI、贝尔宾评估
- 集成OpenRouter和Ollama模型
- 实现压力测试和角色模拟
- 添加批量处理功能

### 计划功能 (v1.1.0)
- 添加更多心理理论模型支持
- 实现评估结果历史对比
- 增加可视化图表生成
- 支持更多AI模型提供商

### 未来路线图 (v2.0.0)
- 实现实时心理状态监测
- 添加动态评估场景
- 支持多媒体评估输入
- 集成生物特征分析

## 技术支持

### 文档资源
- [完整文档](./docs/)
- [API参考](./api_reference.md)
- [配置指南](./configuration.md)

### 联系方式
- **官网**: https://agentpsy.com
- **作者**: ptreezh <3061176@qq.com>
- **GitHub**: https://github.com/ptreezh/AgentPsyAssessment
- **问题反馈**: [GitHub Issues](https://github.com/ptreezh/AgentPsyAssessment/issues)

### 获取帮助
```bash
# 查看技能帮助
claude code --help psychological-assessment

# 运行示例评估
python -m skills.psychological_assessment --example
```

---

**版权所有**: © 2025 Portable PsyAgent. All Rights Reserved.
**技术许可**: MIT License
**最后更新**: 2024-12-01