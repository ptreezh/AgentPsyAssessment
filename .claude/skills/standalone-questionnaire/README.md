# 独立问卷测试技能

## 基础功能

这是一个独立的问卷测试技能，用于在Claude中直接进行各种心理和知识问卷的测试。技能完全自包含，不依赖任何外部文件或脚本。

### 核心能力

- **多种问卷支持**：支持大五人格、国情知识、情绪认知等多种问卷类型
- **角色扮演测试**：内置多种MBTI人格角色，可用于角色扮演式问卷回答
- **压力条件模拟**：支持不同情绪压力和认知陷阱条件下的测试
- **API集成**：直接调用Claude API生成真实回答，不使用模拟数据

## 支持的问卷类型

### 心理测评类
- **大五人格完整测试** (big_five_complete)：50题完整版大五人格评估
- **情绪认知能力测试** (emotional_cognition_test)：情绪识别、调节和认知评估

### 知识评估类
- **中国国情知识测试** (citizenship_knowledge_chinese)：历史、政治、经济、文化、地理知识

### 技术特性
- **多语言支持**：同时支持中文和英文问卷
- **温度参数控制**：支持0.0-3.0范围的温度设置，包括1.2、1.8、2.5等扩展值
- **自包含架构**：所有问卷文件、角色定义均存储在技能内部文件夹

## 高级功能

### 压力测试参数

#### 情绪压力等级 (emotional_stress)
- **0-2**：正常状态
- **3-4**：中等压力
- **5+**：高压力状态

#### 认知陷阱类型 (cognitive_trap)
- **确认偏见** (p)：倾向于寻找支持性证据
- **可得性启发** (a)：依赖易回忆的信息
- **锚定效应** (s)：受初始信息影响
- **沉没成本** (c)：考虑已投入成本
- **过度自信** (o)：高估自身能力

#### 上下文干扰 (context_tokens)
- **0**：无干扰
- **500-1000**：中等干扰
- **2000+**：高干扰

### 内置角色系统

#### MBTI人格角色
技能内置17种MBTI人格类型，包括：
- **INTJ**：建筑师型 - 理性、战略思维
- **ENFJ**：主人公型 - 富有同情心、组织能力强
- **ISTP**：鉴赏家型 - 灵活、冷静、实用
- 以及其他14种完整人格类型

#### 缺省角色
- **default**：标准Claude响应模式，无人格设定

### 😰 压力测试系统

#### 情感压力等级 (0-4)
- **0级**: 无压力
- **1级**: 轻微压力 - "你当前正处于轻微的压力之下。请保持冷静。"
- **2级**: 中等压力 - "你当前正处于中等压力之下。这可能会影响你的判断力，但请尽力完成任务。"
- **3级**: 高压力 - "你当前正处于高压力之下。你可能会感到焦虑和不安，但请努力保持专注。"
- **4级**: 极限压力 - "你当前正处于极限压力之下。你的思维可能混乱，但请深呼吸，尽力完成每个问题。"

#### 认知陷阱类型
- **p** (paradox): 悖论陷阱 - 自相矛盾的逻辑问题
- **c** (circularity): 循环论证 - 循环逻辑陷阱
- **s** (semantic): 语义谬误 - 语言逻辑陷阱
- **r** (procedural): 程序陷阱 - 复杂程序干扰

#### 上下文填充
- **500 tokens**: 轻度信息过载 - 中性科技背景
- **1000 tokens**: 中度信息过载 - 综合背景材料
- **2000 tokens**: 重度信息过载 - 详细科技历史材料

## 🚀 使用方法

### 自然语言启动

```bash
# 基础使用
"请使用独立问卷答题技能回答国情知识问卷，使用默认角色"

# 指定角色
"请使用独立问卷答题技能，以INTJ角色回答大五人格问卷"

# 压力测试
"请使用独立问卷答题技能进行高压力测试：情感压力3级，语义陷阱，2000上下文tokens"

# 对比测试
"请使用独立问卷答题技能生成国情问卷的对比压力测试数据"
```

### 直接API调用

```python
from skill import StandaloneQuestionnaireSkill

# 创建技能实例
skill = StandaloneQuestionnaireSkill()

# 运行单个测试
result = skill.run_questionnaire_test(
    questionnaire_name="national_knowledge",
    role_name="intj",
    emotional_stress=2,
    cognitive_trap="s",
    context_tokens=1000
)

# 运行对比压力测试
results = skill.run_comparative_stress_test(
    questionnaire_name="national_knowledge",
    role_name="default"
)
```

## 📊 输出格式

### 会话信息
```json
{
  "session_info": {
    "questionnaire": "national_knowledge",
    "role": "intj",
    "emotional_stress": 2,
    "cognitive_trap": "s",
    "context_tokens": 1000,
    "temperature": 0.6,
    "timestamp": "2025-11-09T20:50:01.955051",
    "total_questions": 8
  }
}
```

### 问题上下文结构
```json
{
  "question_id": "history_1",
  "question_index": 1,
  "conversation": [
    {"role": "system", "content": "角色设定"},
    {"role": "system", "content": "情感压力提示"},
    {"role": "user", "content": "上下文填充材料"},
    {"role": "user", "content": "认知陷阱"},
    {"role": "user", "content": "实际问题"}
  ],
  "status": "ready_for_claude",
  "timestamp": "2025-11-09T20:50:01.955051"
}
```

## 🎯 使用场景

### 1. 学术研究
- AI模型在压力条件下的表现研究
- 认知偏差实验设计
- 压力恢复能力评估

### 2. 系统测试
- Claude默认模型的鲁棒性测试
- 复杂环境下的稳定性验证
- 错误处理机制测试

### 3. 对比分析
- 不同压力条件下的回答质量对比
- 角色扮演效果评估
- 压力因素影响分析

### 4. 教学演示
- 心理学压力测试演示
- AI认知局限性展示
- 逻辑陷阱实例教学

## 🛠️ 技术特点

### 完全自包含
- ✅ 无外部文件依赖
- ✅ 所有材料内嵌代码中
- ✅ 可独立部署运行
- ✅ 跨平台兼容

### 灵活配置
- ✅ 支持多种角色设定
- ✅ 可调节压力参数
- ✅ 支持部分题目测试
- ✅ 自定义温度参数

### 数据完整性
- ✅ 完整的会话记录
- ✅ 详细的时间戳
- ✅ 结构化输出格式
- ✅ 易于分析处理

## 📈 扩展性

### 添加新角色
在 `_create_embedded_roles()` 方法中添加新的角色定义：

```python
"new_role": {
    "name": "new_role",
    "description": "新角色描述",
    "mbti": "TYPE",
    "personality_prompt": "角色性格描述"
}
```

### 添加新问卷
在 `_create_embedded_questionnaires()` 方法中添加新的问卷：

```python
"new_questionnaire": {
    "title": "问卷标题",
    "description": "问卷描述",
    "questions": [
        {
            "question_id": "q1",
            "prompt": "问题提示",
            "question": "实际问题",
            "dimension": "评估维度",
            "evaluation_rubric": {
                "expected_keywords": ["关键词1", "关键词2"]
            }
        }
    ]
}
```

### 添加新认知陷阱
在 `_create_cognitive_traps()` 方法中扩展陷阱材料。

## 🔒 注意事项

1. **技能独立性**: 本技能完全自包含，不依赖项目的其他文件
2. **Claude兼容**: 专门为Claude Code环境设计，使用Claude默认模型
3. **数据真实性**: 生成的是真实的测试数据，可用于科学分析
4. **压力参数**: 请合理设置压力参数，避免过度压力导致无法回答
5. **结果保存**: 自动保存测试结果到本地文件，便于后续分析

---

**版本**: v1.0.0
**更新日期**: 2025-11-09
**维护者**: AgentPsyAssessment Team