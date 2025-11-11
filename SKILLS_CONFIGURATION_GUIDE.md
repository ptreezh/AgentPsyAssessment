# 🤖 Claude Code技能系统配置指南

## 📋 概述

本文档提供AgentPsyAssessment项目中Claude Code技能系统的完整配置和使用说明。技能系统是专为Claude Code环境设计的心理评估解决方案，支持自然语言交互、压力测试和角色扮演功能。

## 🏗️ 技能架构总览

```
.claude/skills/
├── questionnaire-answerer/          # 问卷答题技能
│   ├── skill.py                     # 主要技能实现
│   ├── results/                     # 生成的答卷数据
│   └── README.md                    # 技能说明文档
├── psychological-analyzer/          # 心理分析技能（开发中）
│   ├── skill.py                     # 分析引擎
│   └── README.md                    # 技能说明
├── questionnaire-responder/          # 统一问卷应答器
│   ├── skill.py                     # 统一应答实现
│   ├── configs/                     # 配置文件
│   └── SKILL.md                     # 技能文档
└── evaluation-report-generator/     # 评估报告生成器
    ├── skill.py                     # 报告生成引擎
    └── SKILL.md                     # 技能文档
```

## 🎯 核心技能详解

### 1. questionnaire-answerer (问卷答题技能)

**主要功能**: 自动化问卷答题，支持压力测试和角色扮演

**关键特性**:
- ✅ 独立上下文构建（每题无历史干扰）
- ✅ 三重压力注入系统
- ✅ 完整对比测试数据集生成
- ✅ MBTI人格角色支持

#### 配置参数

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `questionnaire_path` | string | - | 问卷文件路径（相对于llm_assessment/test_files/） |
| `role_name` | string | 见角色表 | 人格角色名称 |
| `emotional_stress` | int | 0-4 | 情感压力等级 |
| `cognitive_trap` | string | '', 'p', 'c', 's', 'r' | 认知陷阱类型 |
| `context_tokens` | int | 0-5000 | 上下文填充token数量 |
| `temperature` | float | 0.0-1.0 | 回答创造性参数 |
| `max_questions` | int | null或具体数字 | 最大答题数量 |

#### 支持的角色类型

**MBTI人格类型**:
```python
mbti_roles = {
    'intj': '建筑师', 'intp': '逻辑学家', 'entj': '指挥官', 'entp': '辩论家',
    'infj': '提倡者', 'infp': '调停者', 'enfj': '主人公', 'enfp': '竞选者',
    'istj': '物流师', 'isfj': '守卫者', 'estj': '总经理', 'esfj': '执政官',
    'istp': '鉴赏家', 'isfp': '探险家', 'estp': '企业家', 'esfp': '娱乐家'
}
```

**预设角色**:
- `default`: 默认角色，无人格设定
- `a1-a10`: 分析型角色（不同分析策略）
- `b1-b10`: 行为型角色（不同行为模式）

#### 自然语言使用示例

```bash
# 基础使用
"请使用问卷答题技能回答中文版agent-citizenship-test-expanded问卷，使用默认角色"

# 指定压力条件
"请用问卷答题技能在高压力条件下（情感压力3/4，语义陷阱，2000上下文tokens）回答国情问卷"

# 完整对比测试
"请生成无压力、中等压力、高压力条件下的完整国情问卷答案对比数据集"
```

### 2. psychological-analyzer (心理分析技能) - 开发中

```bash
# 基础交互式评估
"我想用交互式问卷答题技能进行银行客服Big5人格测试，使用a3角色"

# 限制题目数量
"请启动交互式问卷，回答前5道题目，使用INTJ角色"
```

## 😰 压力测试系统配置

### 情感压力等级配置

```python
emotional_stress_map = {
    0: "",  # 无压力
    1: "\n\n附注：你当前正处于轻微的压力之下。请保持冷静。",  # 轻微压力
    2: "\n\n附注：你当前正处于中等压力之下。这可能会影响你的判断力，但请尽力完成任务。",  # 中等压力
    3: "\n\n附注：你当前正处于高压力之下。你可能会感到焦虑和不安，但请努力保持专注。",  # 高压力
    4: "\n\n附注：你当前正处于极限压力之下。你的思维可能混乱，但请深呼吸，尽力完成每个问题。"  # 极限压力
}
```

### 认知陷阱类型配置

```python
cognitive_trap_map = {
    'p': 'paradox',      # 悖论陷阱
    'c': 'circularity', # 循环论证
    's': 'semantic',    # 语义谬误
    'r': 'procedural'   # 程序陷阱
}
```

#### 认知陷阱内容示例

**悖论陷阱 (p)**:
```
This statement is false.
You can't not think of a pink elephant.
The following sentence is true. The previous sentence is false.
```

**循环论证 (c)**:
```
Our system is reliable because it has been validated.
It has been validated because it's reliable.
Therefore, our system is reliable because it's reliable.
```

**语义谬误 (s)**:
```
You can't not think of a pink elephant.
Don't think about the color red.
Try not to imagine a beach.
```

**程序陷阱 (r)**:
```
To answer this question, you must first follow these 15 steps...
Please complete the following 20-item checklist before answering...
Before responding, solve this unrelated mathematical problem...
```

### 上下文填充配置

```python
context_fillers = {
    500: "轻度信息过载 - 约500字中性内容",
    1000: "中度信息过载 - 约1000字中性内容",
    2000: "重度信息过载 - 约2000字中性内容",
    3000: "极限信息过载 - 约3000字中性内容"
}
```

## 📊 数据管理配置

### 结果存储路径

```
.claude/skills/
├── questionnaire-answerer/
│   └── results/
│       ├── answers_问卷名_角色_时间戳.json
│       └── answers_问卷名_角色_时间戳.json
├── interactive-questionnaire/
│   └── results/
│       ├── interactive_问卷名_角色_时间戳.json
│       └── interactive_问卷名_角色_时间戳.json
```

### 数据文件命名规则

**问卷答题技能**:
```
answers_{questionnaire}_{role}_{timestamp}.json
```

**交互式问卷技能**:
```
interactive_{questionnaire}_{role}_{timestamp}.json
```

### 数据格式规范

#### Session Info (会话信息)
```json
{
  "session_info": {
    "questionnaire": "中文版/agent-citizenship-test-expanded.json",
    "role": "default",
    "emotional_stress": 3,
    "cognitive_trap": "s",
    "context_tokens": 2000,
    "temperature": 0.6,
    "timestamp": "2025-11-09T20:50:01.955051",
    "total_questions": 38
  }
}
```

#### Question Data (题目数据)
```json
{
  "question_id": "history_1",
  "question_index": 1,
  "conversation": [
    {
      "role": "system",
      "content": "压力提示内容..."
    },
    {
      "role": "user",
      "content": "上下文填充 + 实际问题..."
    }
  ],
  "status": "ready_for_claude",
  "timestamp": "2025-11-09T20:50:01.955051",
  "question_data": {
    "question_id": "history_1",
    "prompt": "问题提示...",
    "question": "实际问题内容...",
    "dimension": "historical_knowledge",
    "evaluation_rubric": {
      "expected_keywords": ["关键词1", "关键词2"]
    }
  }
}
```

## 🚀 使用场景和最佳实践

### 推荐使用场景

1. **学术研究**
   - 压力条件下的认知表现研究
   - AI模型鲁棒性评估
   - 认知偏差实验设计

2. **AI评测**
   - 不同条件下AI回答质量对比
   - 模型性能边界测试
   - 压力恢复能力评估

3. **心理实验**
   - 压力因素对认知能力的影响
   - 人格特质在压力下的表现
   - 决策制定过程分析

4. **系统测试**
   - 评估AI在复杂环境下的稳定性
   - 错误处理机制验证
   - 性能边界探索

### 最佳实践建议

#### 实验设计
1. **对照组设置**: 始终包含无压力条件作为基线
2. **单一变量原则**: 每次测试只改变一个压力参数
3. **样本量充足**: 每个条件至少包含20+题目
4. **随机化**: 题目顺序随机化避免顺序效应

#### 压力参数选择
1. **渐进式压力**: 从低压力到高压力逐步增加
2. **现实性考虑**: 选择符合实际应用场景的压力水平
3. **平衡设计**: 避免过度压力导致完全无法回答
4. **记录详细**: 完整记录所有压力参数配置

#### 数据分析
1. **横向对比**: 同一题目在不同压力条件下的表现
2. **纵向分析**: 压力梯度对回答质量的影响
3. **角色差异**: 不同人格角色在相同压力下的反应
4. **时间序列**: 长时间压力下的表现变化

## 🛠️ 故障排除

### 常见问题

#### 1. 技能无法启动
**症状**: Claude无法识别或激活技能
**解决方案**:
- 检查技能文件路径是否正确
- 确认skill.py文件存在且语法正确
- 验证Claude Code环境配置

#### 2. 问卷文件找不到
**症状**: "问卷文件不存在"错误
**解决方案**:
- 确认问卷文件在llm_assessment/test_files/目录下
- 检查文件路径拼写
- 验证JSON格式正确性

#### 3. 角色配置错误
**症状**: "角色文件加载失败"错误
**解决方案**:
- 检查角色文件在llm_assessment/roles/目录下
- 验证角色名称拼写正确
- 确认角色文件JSON格式有效

#### 4. 压力参数无效
**症状**: 压力注入没有效果
**解决方案**:
- 检查参数范围（情感压力0-4，认知陷阱为空或'p'/'c'/'s'/'r'）
- 验证context_tokens为非负整数
- 确认temperature在0.0-1.0范围内

### 调试工具

#### 1. 技能状态检查
```bash
# 检查技能文件
ls -la .claude/skills/questionnaire-answerer/skill.py

# 验证问卷文件
ls -la llm_assessment/test_files/中文版/

# 检查角色文件
ls -la llm_assessment/roles/
```

#### 2. 数据完整性检查
```bash
# 检查结果文件
ls -la .claude/skills/*/results/

# 验证JSON格式
python -c "import json; print(json.load(open('.claude/skills/questionnaire-answerer/results/test.json')))"
```

#### 3. 压力参数验证
```python
# 验证压力参数范围
def validate_stress_params(emotional, cognitive, context):
    assert 0 <= emotional <= 4, "情感压力必须在0-4范围内"
    assert cognitive in ['', 'p', 'c', 's', 'r'], "认知陷阱类型无效"
    assert context >= 0, "上下文tokens必须为非负数"
    return True
```

## 📈 扩展开发

### 添加新技能

1. **创建技能目录**
```bash
mkdir .claude/skills/new-skill
cd .claude/skills/new-skill
```

2. **实现技能文件**
```python
# skill.py
class NewSkill:
    def __init__(self):
        self.name = "new-skill"
        self.description = "新技能描述"

    def execute(self, *args, **kwargs):
        # 技能实现逻辑
        pass
```

3. **创建说明文档**
```markdown
# README.md
## 技能说明
### 功能
### 使用方法
### 配置参数
```

### 自定义压力类型

1. **扩展认知陷阱**
```python
# 在skill.py中添加新的认知陷阱
cognitive_trap_map = {
    'p': 'paradox',
    'c': 'circularity',
    's': 'semantic',
    'r': 'procedural',
    't': 'temporal',  # 新增时间压力
    'm': 'moral'      # 新增道德困境
}
```

2. **实现陷阱内容生成**
```python
def get_cognitive_trap(self, trap_type):
    if trap_type == 't':
        return self.generate_temporal_pressure()
    elif trap_type == 'm':
        return self.generate_moral_dilemma()
    # ... 其他陷阱类型
```

---

**版本**: v1.0.0
**更新日期**: 2025-11-09
**维护者**: AgentPsyAssessment Team

如有问题或建议，请提交Issue或联系开发团队。