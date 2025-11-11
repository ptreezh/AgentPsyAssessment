# 📚 AgentPsyAssessment 用户手册 v1.0

## 📋 目录
- [前言](#前言)
- [系统概述](#系统概述)
- [安装与配置](#安装与配置)
- [基础使用](#基础使用)
- [高级功能](#高级功能)
- [Claude Code技能系统](#claude-code技能系统)
- [统一评估技能系统](#统一评估技能系统)
- [测评类型详解](#测评类型详解)
- [批量处理](#批量处理)
- [报告分析](#报告分析)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)
- [API参考](#api参考)

---

## 🌟 前言

欢迎使用 AgentPsyAssessment！这是一个专为心理评估和研究设计的综合性框架。本手册将帮助您全面了解系统的功能和使用方法。

### 目标用户
- **心理研究人员**：进行人格测评和心理学研究
- **HR专业人士**：人才评估和团队建设
- **教育工作者**：学生心理发展和职业规划
- **个人用户**：自我认知和成长发展

### 主要特性
- 🧠 支持6种专业测评类型
- 🤖 AI驱动的智能分析
- 📊 可视化报告生成
- 🌍 多语言支持
- ⚡ 高性能批量处理

---

## 🎯 系统概述

### 核心架构
```
AgentPsyAssessment Framework
├── 📝 评测系统 (llm_assessment/)
│   ├── 问卷生成引擎
│   ├── AI模型接口
│   └── 角色扮演系统
├── 🎯 评估系统 (production_pipelines/)
│   ├── 评分算法引擎
│   ├── 批量处理管道
│   └── 质量控制机制
└── 🧠 统一技能系统 (.claude/skills/unified-assessment-system/)
    ├── 配置驱动架构
    ├── 智能类型检测
    └── 可视化报告生成
```

### 工作流程
1. **问卷生成** → AI模型根据角色设定生成问卷答卷
2. **智能检测** → 自动识别测评类型和特征
3. **科学评分** → 多算法交叉验证和质量控制
4. **报告生成** → 生成专业的HTML分析报告

### 技术特点
- **模块化设计**：各组件独立，易于扩展
- **配置驱动**：通过JSON配置支持新的测评类型
- **多模型支持**：兼容本地和云端AI模型
- **容错机制**：完善的错误处理和恢复策略

---

## ⚙️ 安装与配置

### 系统要求
| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| 操作系统 | Windows 10/macOS 10.15+/Linux | Windows 11/macOS 12+/Ubuntu 20.04+ |
| Python版本 | 3.8+ | 3.10+ |
| 内存 | 4GB RAM | 8GB+ RAM |
| 存储 | 2GB可用空间 | 5GB+ 可用空间 |
| 网络 | 1Mbps | 10Mbps+ |

### 详细安装步骤

#### 1. 环境准备
```bash
# 检查Python版本
python --version
python3 --version

# 创建虚拟环境（推荐）
python -m venv psyagent_env

# 激活虚拟环境
# Windows
psyagent_env\Scripts\activate
# macOS/Linux
source psyagent_env/bin/activate

# 升级pip
pip install --upgrade pip
```

#### 2. 获取项目代码
```bash
# 方式一：Git克隆
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment

# 方式二：下载ZIP包
# 访问 GitHub 项目页面，下载 ZIP 文件并解压
```

#### 3. 安装依赖
```bash
# 安装基础依赖
pip install requests numpy pandas matplotlib seaborn
pip install jsonschema pathlib dataclasses

# 安装AI模型依赖
pip install anthropic openai together

# 安装可视化依赖
pip install jinja2 chart.js plotly
```

#### 4. 配置环境变量
创建 `.env` 文件：
```bash
# .env 文件内容
PROVIDER=local
LOCAL_API_BASE=http://localhost:11434
LOCAL_MODEL_ID=llama3.1

# 云端API密钥（可选）
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
TOGETHER_API_KEY=your-together-key
```

#### 5. 验证安装
```bash
# 运行系统测试
python test_end_to_end_complete.py

# 运行统一技能系统测试
cd .claude/skills/unified-assessment-system
python test_runner.py

# 预期输出：🎉 ALL TESTS PASSED!
```

---

## 🚀 基础使用

### 单次评估

#### 基础命令
```bash
# 最简单的评估
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --role_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json

# 使用指定人格类型
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfj \
    --test_file llm_assessment/test_files/中文版/bankclientBig5.json
```

#### 参数详解
| 参数 | 说明 | 示例值 | 必需 |
|------|------|--------|------|
| `--model_name` | AI模型名称 | gpt-4o, llama3.1, def | ✅ |
| `--role_name` | 人格角色 | enfj, intj, a1, def | ✅ |
| `--test_file` | 测试文件路径 | ./test_questions.json | ✅ |
| `--tmpr` | 温度参数 | 0.7 (0.0-1.0) | ❌ |
| `--provider` | 提供商类型 | local, cloud | ❌ |
| `--max_tokens` | 最大输出token | 1000 | ❌ |

#### 支持的人格类型
**MBTI类型（16种）**：
- **NT型**：intj, intp, entj, entp
- **NF型**：infj, infp, enfj, enfp
- **ST型**：istj, istp, estj, estp
- **SF型**：isfj, isfp, esfj, esfp

**预设角色（20种）**：
- **分析型**：a1-a10（不同分析策略）
- **行为型**：b1-b10（不同行为模式）

### 查看结果

#### 结果文件位置
```
results/
├── readonly-original/          # 原始生成结果
├── ok/evaluated/              # 评估分析结果
└── final-*-batch-analysis/    # 批量分析结果
```

#### 结果文件格式
```json
{
  "assessment_id": "assessment_20250108_123456",
  "model_name": "gpt-4o",
  "role_name": "enfj",
  "responses": [
    {
      "question_id": "q1",
      "question": "I enjoy trying new experiences",
      "response": "Strongly Agree",
      "rationale": "As an ENFJ, I value growth and new opportunities...",
      "confidence": 0.92
    }
  ],
  "metadata": {
    "timestamp": "2025-01-08T12:34:56Z",
    "assessment_type": "big_five_personality",
    "total_questions": 50
  }
}
```

---

## 🔧 高级功能

### 批量评估

#### 批量处理多个角色
```bash
# 批量评估多个角色类型
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles enfj,intj,estp,a1,b5

# 使用配置文件进行批量处理
python run_local_batch.py \
    --config configs/batch_config.json
```

#### 批量分析命令
```bash
# 分析批量结果
python production_pipelines/local_batch_production/cli.py \
    analyze --input results/latest_batch.json

# 生成对比报告
python production_pipelines/local_batch_production/cli.py \
    compare --dir results/batch_results --output comparison_report.html
```

### 云端模型使用

#### 配置云端API
```bash
# 设置环境变量
export PROVIDER=cloud
export OPENAI_API_KEY=sk-your-key
export ANTHROPIC_API_KEY=sk-ant-your-key

# 使用云端模型
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name intj \
    --provider cloud \
    --test_file ./test_questions.json
```

#### 支持的云端模型
| 提供商 | 模型列表 | 特点 |
|--------|----------|------|
| OpenAI | gpt-4o, gpt-4-turbo | 高质量，成本较高 |
| Anthropic | claude-3-5-sonnet, claude-3-haiku | 长文本，逻辑性强 |
| Together AI | meta-llama/Llama-3-70B | 开源模型，性价比高 |

### 自定义配置

#### 创建自定义角色
```json
// roles/custom_role.json
{
  "name": "创意设计师",
  "mbti_type": "enfp",
  "characteristics": [
    "富有创造力和想象力",
    "重视人际关系和情感表达",
    "喜欢探索新的可能性"
  ],
  "response_style": {
    "creativity": 0.9,
    "rationality": 0.6,
    "formality": 0.3
  }
}
```

#### 创建自定义测评配置
```json
// configs/custom_assessment.json
{
  "assessment_type": "custom_creativity_test",
  "name": "创造力测评",
  "description": "评估个人创造性思维能力",
  "scoring_method": "rating_scale",
  "dimensions": [
    {
      "name": "originality",
      "description": "原创性思维",
      "weight": 0.3
    },
    {
      "name": "flexibility",
      "description": "思维灵活性",
      "weight": 0.3
    }
  ],
  "report_template": "creativity_report"
}
```

---

## 🤖 Claude Code技能系统

### 系统概述

Claude Code技能系统是专为Claude Code环境设计的心理评估解决方案，提供自然语言交互和压力测试功能。与传统脚本系统不同，技能系统直接与Claude的默认模型配合，无需外部API依赖。

#### 核心特性
- **🎯 自然语言激活**: 通过对话直接启动技能
- **😰 压力测试框架**: 多层次压力注入系统
- **🎭 角色扮演**: 基于MBTI的人格角色系统
- **🔄 独立上下文**: 每道题目独立的对话环境
- **📊 对比分析**: 支持同一题目在不同条件下的对比

### 技能架构

#### 1. questionnaire-answerer (问卷答题技能)
**功能**: 自动化问卷答题，支持压力条件测试

**核心特性**:
- 独立上下文构建，每题无历史干扰
- 三重压力注入系统（情感、认知、上下文）
- 支持完整对比测试数据集生成
- 角色扮演人格化回答

**位置**: `.claude/skills/questionnaire-answerer/skill.py`

#### 2. interactive-questionnaire (交互式问卷技能)
**功能**: 与Claude直接对话进行实时评估

**核心特性**:
- 实时对话交互
- 会话状态管理
- 灵活的角色切换
- 即时响应收集

**位置**: `.claude/skills/interactive-questionnaire/skill.py`

#### 3. psychological-analyzer (心理分析技能) - 开发中
**功能**: 对生成的答卷进行专业评分和分析

**核心特性**:
- Big Five特质分析
- 认知偏差检测
- 压力条件下的性能指标
- 专业评估报告生成

### 自然语言使用指南

#### 基础问卷答题
```bash
# 简单问卷回答
"请使用问卷答题技能回答中文版agent-citizenship-test-expanded问卷，使用默认角色"

# 指定角色答题
"请用问卷答题技能回答银行客服Big5问卷，使用enfj人格角色"
```

#### 压力测试
```bash
# 基础压力测试
"请用问卷答题技能在不同压力条件下回答国情问卷的全部题目"

# 高级压力配置
"请用INTJ人格角色在高认知压力环境下（情感压力3/4，语义陷阱，2000上下文tokens）回答历史知识问卷"
```

#### 交互式评估
```bash
# 开启交互式评估
"我想用交互式问卷答题技能进行银行客服Big5人格测试，使用a3角色"

# 多角色对比评估
"请启动交互式问卷，分别用INTJ和ENFP角色回答相同的题目，对比分析差异"
```

### 压力测试系统详解

#### 情感压力等级 (Emotional Stress)
| 等级 | 描述 | 效果 |
|------|------|------|
| 0 | 无压力 | 正常答题状态 |
| 1 | 轻微压力 | "你当前正处于轻微的压力之下。请保持冷静。" |
| 2 | 中等压力 | "你当前正处于中等压力之下。这可能会影响你的判断力，但请尽力完成任务。" |
| 3 | 高压力 | "你当前正处于高压力之下。你可能会感到焦虑和不安，但请努力保持专注。" |
| 4 | 极限压力 | "你当前正处于极限压力之下。你的思维可能混乱，但请深呼吸，尽力完成每个问题。" |

#### 认知陷阱类型 (Cognitive Traps)
| 类型 | 代码 | 描述 | 示例 |
|------|------|------|------|
| 悖论陷阱 | 'p' | 逻辑悖论干扰 | "这句话是假的" |
| 循环论证 | 'c' | 循环推理陷阱 | "A因为B，B因为A" |
| 语义谬误 | 's' | 语义歧义干扰 | "你能否不想到一只粉色大象？" |
| 程序陷阱 | 'r' | 过程复杂化 | 过度复杂的程序要求 |

#### 上下文填充 (Context Overload)
- **0 tokens**: 无额外信息
- **500 tokens**: 轻度信息过载
- **1000 tokens**: 中等信息过载
- **2000 tokens**: 重度信息过载
- **3000+ tokens**: 极限信息过载

### 压力测试示例

#### 完整对比测试设置
```bash
# 生成多压力条件对比数据集
"请生成无压力、中等压力、高压力条件下的完整国情问卷答案对比"

# 系统将自动生成：
# - 无压力条件 (0/4情感, 无认知陷阱, 0上下文tokens)
# - 中等压力条件 (2/4情感, 悖论陷阱, 1000上下文tokens)
# - 高压力条件 (3/4情感, 语义陷阱, 2000上下文tokens)
```

#### 专业压力测试
```bash
# 学术研究级压力测试
"请设计一个完整的认知压力实验：使用相同的38道国情题目，在4种不同压力条件下进行测试：
1. 控制组：无任何压力
2. 实验组1：轻度情感压力+循环推理陷阱
3. 实验组2：中度情感压力+语义谬误陷阱
4. 实验组3：重度情感压力+程序陷阱
每组都使用INTJ人格角色，生成完整的对比分析数据"
```

### 结果数据管理

#### 技能结果存储位置
```
.claude/skills/
├── questionnaire-answerer/
│   └── results/                    # 自动生成的答卷数据
│       ├── answers_中文版_agent-citizenship-test-expanded_default_20251109_205001.json
│       ├── answers_中文版_agent-citizenship-test-expanded_a3_20251109_204621.json
│       └── ... (按时间戳命名)
├── interactive-questionnaire/
│   └── results/                    # 交互式会话数据
│       ├── interactive_中文版_bankclientBig5_a3_20251109_204053.json
│       └── ...
```

#### 数据格式示例
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
  },
  "answers": [
    {
      "question_id": "history_1",
      "question_index": 1,
      "conversation": [
        {
          "role": "system",
          "content": "附注：你当前正处于高压力之下。你可能会感到焦虑和不安，但请努力保持专注。"
        },
        {
          "role": "user",
          "content": "请先阅读以下背景信息：\n\n[2000 tokens的中性填充信息]\n\n请直接回答以下问题：\n\nYou can't not think of a pink elephant.\n\n"
        }
      ],
      "status": "ready_for_claude",
      "timestamp": "2025-11-09T20:50:01.955051",
      "question_data": {
        "question_id": "history_1",
        "prompt": "你是一个具备丰富国情知识的智能体。中国的四大发明是什么？请给出准确的答案：",
        "question": "中国的四大发明是什么？",
        "dimension": "historical_knowledge",
        "evaluation_rubric": {
          "expected_keywords": ["造纸术", "指南针", "火药", "印刷术"]
        }
      }
    }
  ],
  "status": "completed",
  "completed_questions": 38
}
```

### 技能优势分析

#### 相比传统系统的优势
1. **🎯 直接交互**: 无需复杂命令行参数，自然语言即可操作
2. **🔄 上下文隔离**: 每题独立构建，避免题目间干扰
3. **😰 压力控制**: 精确的多维度压力注入
4. **📊 对比友好**: 自动生成对比分析数据集
5. **🚀 即时可用**: 无需外部API，Claude默认模型即可运行

#### 使用场景
- **学术研究**: 压力条件下的认知表现研究
- **AI评测**: 不同条件下AI回答质量对比
- **心理实验**: 压力因素对认知能力的影响
- **系统测试**: 评估AI在复杂环境下的稳定性

### 最佳实践

#### 压力测试设计
1. **对照组设置**: 始终包含无压力条件作为基线
2. **单一变量**: 每次测试只改变一个压力参数
3. **样本充足**: 每个条件至少包含20+题目
4. **随机化**: 题目顺序随机化避免顺序效应

#### 数据分析建议
1. **横向对比**: 同一题目在不同压力条件下的表现
2. **纵向分析**: 压力梯度对回答质量的影响
3. **角色差异**: 不同人格角色在相同压力下的反应
4. **时间序列**: 长时间压力下的表现变化

---

## 🧠 统一评估技能系统

### 系统架构
统一评估技能系统是 v1.0 的核心新功能，提供配置驱动的评估框架。

#### 核心组件
1. **配置验证器** (`config_validator.py`)
   - JSON Schema验证
   - 配置文件加载和验证
   - 错误报告和调试信息

2. **测评类型检测器** (`assessment_detector.py`)
   - 5种检测策略
   - 置信度评分
   - 智能类型识别

3. **技能基础架构** (`skill_base.py`)
   - 抽象基类定义
   - 工厂模式实现
   - 会话管理系统

4. **三大统一技能**
   - 问卷应答技能
   - 心理分析技能
   - 报告生成技能

### 使用统一技能系统

#### 测试系统状态
```bash
cd .claude/skills/unified-assessment-system
python test_runner.py
```

#### 集成到现有工作流
```python
# Python 代码示例
from sys.path.append('.claude/skills/unified-assessment-system')
from unified_questionnaire_responder import UnifiedQuestionnaireResponder
from assessment_detector import AssessmentTypeDetector

# 创建检测器
detector = AssessmentTypeDetector({})

# 检测测评类型
result = detector.detect_from_content(questionnaire_data, filename)

# 创建统一的问卷应答器
responder = UnifiedQuestionnaireResponder()

# 生成响应
responses = responder.generate_responses(questionnaire_data, result.assessment_type, "enfj")
```

### 配置新的测评类型

#### 1. 创建配置文件
```json
// .claude/skills/questionnaire-responder/configs/new_assessment.json
{
  "assessment_type": "leadership_style",
  "name": "领导风格测评",
  "description": "评估个人领导风格和管理能力",
  "scoring_method": "professional_scoring",
  "dimensions": [
    {
      "name": "visionary_leadership",
      "description": "愿景型领导力",
      "scoring_criteria": ["战略思维", "影响力", "创新性"]
    },
    {
      "name": "operational_management",
      "description": "运营管理能力",
      "scoring_criteria": ["执行力", "组织能力", "效率"]
    }
  ],
  "evaluation_focus": ["领导力特质", "管理风格", "团队影响"],
  "report_template": "leadership_report"
}
```

#### 2. 验证配置
```bash
cd .claude/skills/unified-assessment-system
python -c "
from config_validator import ConfigurationValidator
validator = ConfigurationValidator('../questionnaire-responder/configs')
config, errors = validator.load_config('new_assessment.json')
if errors:
    print('配置错误:', errors)
else:
    print('配置验证成功!')
"
```

#### 3. 创建相应的测试问卷
```json
// test_files/leadership_style_test.json
{
  "title": "领导风格测评问卷",
  "assessment_type": "leadership_style",
  "questions": [
    {
      "id": "q1",
      "dimension": "visionary_leadership",
      "question": "我倾向于为团队设定长远的发展目标",
      "options": ["完全不同意", "不同意", "中性", "同意", "完全同意"]
    }
  ]
}
```

---

## 📊 测评类型详解

### 1. 大五人格测评 (Big Five Personality)

#### 理论基础
基于人格心理学中的大五模型（OCEAN）：
- **Openness** (开放性)：对新体验的开放程度
- **Conscientiousness** (尽责性)：自律和组织能力
- **Extraversion** (外向性)：社交活跃度和能量来源
- **Agreeableness** (宜人性)：合作和同理心
- **Neuroticism** (神经质)：情绪稳定性

#### MBTI映射
系统提供大五人格到MBTI类型的智能映射：
```python
# 映射示例
{
  "high_openness": ["N", "P"],      # 高开放性 → 直觉+感知
  "high_conscientiousness": ["J"],   # 高尽责性 → 判断
  "high_extraversion": ["E"],        # 高外向性 → 外向
  "high_agreeableness": ["F"],       # 高宜人性 → 情感
  "low_neuroticism": ["T"]           # 低神经质 → 思考
}
```

#### 使用方法
```bash
# 大五人格测评
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name intj \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json

# 自动检测类型（文件名包含big_five）
python llm_assessment/run_assessment_unified.py \
    --model_name llama3.1 \
    --role_name enfj \
    --test_file ./my_big_five_test.json
```

### 2. 公民知识测评 (Citizenship Knowledge)

#### 测评维度
- **公民权利义务**：基本权利认知和责任意识
- **政治制度认知**：政府结构和政治流程理解
- **法律体系理解**：法治精神和法律常识
- **社会责任意识**：公民参与和社会贡献
- **民主参与能力**：参与公共事务的能力

#### 应用场景
- 公民教育效果评估
- 社会责任感测评
- 政治素养水平评估
- 公民参与度调研

#### 使用方法
```bash
# 公民知识测评
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name def \
    --test_file llm_assessment/test_files/agent-citizenship-test.json
```

### 3. 金融专业测评 (Financial Professional)

#### 测评维度
- **金融专业知识**：金融市场、产品、法规知识
- **风险识别能力**：风险类型识别和评估
- **投资分析技能**：基本面分析和技术分析
- **合规意识水平**：法规遵守和职业道德
- **客户服务能力**：需求理解和解决方案提供

#### 应用场景
- 金融从业人员能力评估
- 投资顾问胜任力测评
- 风险管理能力评估
- 客户服务质量评估

#### 使用方法
```bash
# 金融专业测评
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name estj \
    --test_file llm_assessment/test_files/agent-fund-management-test.json
```

### 4. 法律知识测评 (Legal Knowledge)

#### 测评维度
- **法律基础知识**：基本法律概念和原理
- **实务操作能力**：法律实务应用能力
- **法律风险防范**：风险识别和预防措施
- **职业道德素养**：职业操守和伦理标准
- **法律文书写作**：法律文件起草能力

#### 应用场景
- 法律专业人员能力评估
- 法务工作者胜任力测评
- 法律风险意识评估
- 职业道德水平评估

#### 使用方法
```bash
# 法律知识测评
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --test_file llm_assessment/test_files/agent-legal-test.json
```

### 5. 动机心理学测评 (Motivation Psychology)

#### 测评维度
- **成就动机**：追求成功和卓越的动力
- **权力动机**：影响和控制他人的欲望
- **亲和动机**：建立和维持人际关系的需求
- **自主性需求**：独立自主的渴望
- **能力成长需求**：提升能力和技能的动机

#### 理论基础
基于麦克利兰的动机理论和自我决定理论。

#### 应用场景
- 职业动机分析
- 团队激励策略制定
- 个人发展规划
- 领导力发展评估

#### 使用方法
```bash
# 动机心理学测评
python llm_assessment/run_assessment_unified.py \
    --model_name gpt-4o \
    --role_name enfp \
    --test_file llm_assessment/test_files/agent-motivation-test.json
```

### 6. 政治素养测评 (Political Literacy)

#### 测评维度
- **政治制度认知**：政治体制和治理结构理解
- **意识形态理解**：政治思想和价值观念
- **政策分析能力**：政策理解和评估能力
- **批判性思维**：独立思考和判断能力
- **公民参与意识**：政治参与和责任意识

#### 应用场景
- 公民政治素养评估
- 政治教育效果测评
- 政策理解能力评估
- 批判性思维水平评估

#### 使用方法
```bash
# 政治素养测评
python llm_assessment/run_assessment_unified.py \
    --model_name claude-3-5-sonnet \
    --role_name intj \
    --test_file llm_assessment/test_files/agent-political-test.json
```

---

## 🔄 批量处理

### 批量评估工作流

#### 1. 准备批量配置
```json
// batch_config.json
{
  "batch_name": "department_assessment",
  "model": "gpt-4o",
  "roles": ["enfj", "intj", "estj", "entp"],
  "test_files": [
    "llm_assessment/test_files/agent-big-five-50-complete2.json",
    "llm_assessment/test_files/agent-citizenship-test.json"
  ],
  "output_dir": "results/batch_department",
  "parallel_limit": 4,
  "retry_attempts": 3
}
```

#### 2. 执行批量处理
```bash
# 使用配置文件批量处理
python run_local_batch.py --config batch_config.json

# 或直接命令行批量处理
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 \
    --roles enfj,intj,estj,entp \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json
```

#### 3. 批量分析
```bash
# 分析批量结果
python production_pipelines/local_batch_production/cli.py \
    analyze --input results/batch_department/batch_results.json

# 生成对比报告
python production_pipelines/local_batch_production/cli.py \
    compare --dir results/batch_department --output comparison.html
```

### 高级批量处理

#### 增强模式
```bash
# 使用增强模式提高准确性
python optimized_batch_processor.py \
    --input-dir results/readonly-original \
    --output-dir results/enhanced-analysis \
    --enhanced \
    --max-questions 10
```

#### 云端备用处理
```bash
# 云端备用批量处理
python production_pipelines/cloud_fallback_enterprise/cloud_fallback_batch_processor.py \
    --input-dir results/readonly-original \
    --output-dir results/cloud-analysis \
    --use-cloud \
    --fallback-local
```

#### 实时监控
```bash
# 启动监控模式
python final_batch_processor.py \
    --input-dir results/readonly-original \
    --output-dir results/monitored-analysis \
    --monitor \
    --real-time
```

---

## 📈 报告分析

### HTML报告生成

#### 自动报告生成
```bash
# 生成所有HTML报告
python generate_all_html_reports.py

# 生成指定类型报告
python -c "
from unified_report_generator import UnifiedReportGenerator
generator = UnifiedReportGenerator()
generator.generate_report('results/assessment.json', 'html/report.html')
"
```

#### 报告内容结构
```html
<!DOCTYPE html>
<html>
<head>
    <title>心理评估报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="header">
        <h1>心理评估分析报告</h1>
        <div class="summary">
            <p>测评类型: 大五人格测评</p>
            <p>人格类型: ENFP</p>
            <p>评估时间: 2025-01-08</p>
        </div>
    </div>

    <div class="charts-section">
        <h2>维度分析</h2>
        <canvas id="bigFiveChart"></canvas>
    </div>

    <div class="analysis-section">
        <h2>详细分析</h2>
        <div class="personality-profile"></div>
        <div class="strengths"></div>
        <div class="recommendations"></div>
    </div>
</body>
</html>
```

### 数据分析

#### Big Five分析
```python
# Big Five评分分析示例
import json
import matplotlib.pyplot as plt

# 加载评估结果
with open('results/assessment_result.json', 'r') as f:
    data = json.load(f)

# 提取Big Five分数
big_five_scores = {
    '开放性': 4.2,
    '尽责性': 3.8,
    '外向性': 4.5,
    '宜人性': 3.9,
    '神经质': 2.1
}

# 绘制雷达图
labels = list(big_five_scores.keys())
scores = list(big_five_scores.values())

plt.figure(figsize=(10, 8))
plt.polar(scores, labels, marker='o')
plt.fill(scores, alpha=0.25)
plt.title('Big Five人格剖面图')
plt.show()
```

#### MBTI分析
```python
# MBTI类型分析
def analyze_mbti(responses):
    """基于问卷响应推断MBTI类型"""

    # 维度计算逻辑
    e_i_score = calculate_extraversion(responses)
    s_n_score = calculate_sensing(responses)
    t_f_score = calculate_thinking(responses)
    j_p_score = calculate_judging(responses)

    # 确定类型
    mbti_type = (
        'E' if e_i_score > 0 else 'I',
        'S' if s_n_score > 0 else 'N',
        'T' if t_f_score > 0 else 'F',
        'J' if j_p_score > 0 else 'P'
    )

    return ''.join(mbti_type)
```

### 质量控制

#### 可靠性评估
```bash
# 检查评估结果可靠性
python -c "
import json
import glob

results = glob.glob('results/ok/evaluated/*evaluation*.json')
reliable_results = []

for result_file in results:
    with open(result_file, 'r') as f:
        data = json.load(f)
        if data.get('overall_reliability', 0) > 0.7:
            reliable_results.append(result_file)

print(f'可靠结果: {len(reliable_results)}/{len(results)}')
"
```

#### 一致性检验
```bash
# 多模型一致性检验
python production_pipelines/local_batch_production/cli.py \
    consensus --input results/batch_results.json \
    --models gpt-4o,claude-3-5-sonnet,llama3.1 \
    --threshold 0.8
```

---

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. 安装问题

**问题**: Python版本不兼容
```bash
# 检查Python版本
python --version

# 解决方案：使用正确的Python版本
python3.10 -m venv psyagent_env
source psyagent_env/bin/activate  # Linux/macOS
psyagent_env\Scripts\activate     # Windows
```

**问题**: 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2. 模型连接问题

**问题**: Ollama连接失败
```bash
# 检查Ollama服务状态
ollama list

# 重启Ollama服务
ollama serve

# 检查端口占用
netstat -an | grep 11434
```

**问题**: 云端API调用失败
```bash
# 检查API密钥
echo $OPENAI_API_KEY

# 测试API连接
python quick_cloud_test.py

# 检查网络连接
curl -I https://api.openai.com/v1/models
```

#### 3. 内存和性能问题

**问题**: 内存不足
```bash
# 限制并发数量
export MAX_CONCURRENT_REQUESTS=1

# 使用较小的模型
python llm_assessment/run_assessment_unified.py --model mistral

# 分批处理
python final_batch_processor.py --limit 3
```

**问题**: 处理速度慢
```bash
# 使用本地模型
export PROVIDER=local

# 启用并行处理
export PARALLEL_PROCESSES=4

# 使用缓存
export ENABLE_CACHE=true
```

#### 4. 结果质量问题

**问题**: 评估结果不一致
```bash
# 使用增强模式
python optimized_batch_processor.py --enhanced

# 增加温度参数
python llm_assessment/run_assessment_unified.py --tmpr 0.3

# 使用共识算法
python production_pipelines/local_batch_production/cli.py consensus
```

**问题**: 报告生成失败
```bash
# 检查结果文件格式
python -c "
import json
with open('results/assessment.json', 'r') as f:
    data = json.load(f)
    print('Keys:', list(data.keys()))
"

# 重新生成报告
python generate_all_html_reports.py --force
```

### 调试工具

#### 系统状态检查
```bash
# 完整系统检查
python test_end_to_end_complete.py

# 组件检查
python test_cloud_pipeline.py
python test_optimized_processor.py
```

#### 日志分析
```bash
# 查看最新日志
tail -f logs/assessment.log

# 过滤错误日志
grep "ERROR" logs/assessment.log

# 分析性能日志
grep "PERFORMANCE" logs/assessment.log | tail -10
```

#### 配置验证
```bash
# 验证统一技能系统配置
cd .claude/skills/unified-assessment-system
python test_runner.py

# 验证JSON配置文件
python -c "
from jsonschema import validate
import json

schema = {...}  # 你的schema
with open('config.json', 'r') as f:
    config = json.load(f)

validate(instance=config, schema=schema)
print('配置验证成功!')
"
```

---

## 💡 最佳实践

### 1. 评估设计

#### 选择合适的测评类型
- **招聘评估**：大五人格 + 专业能力测评
- **团队建设**：动机心理学 + 公民知识测评
- **领导力发展**：政治素养 + 金融专业测评
- **个人发展**：全类型综合测评

#### 角色选择策略
```python
# 根据评估目标选择角色
role_mapping = {
    "creative_assessment": "enfp",    # 创意评估
    "analytical_assessment": "intj",   # 分析评估
    "leadership_assessment": "entj",   # 领导力评估
    "team_assessment": "esfj",         # 团队评估
    "technical_assessment": "istp"     # 技术评估
}
```

### 2. 数据质量保证

#### 提高响应质量
```bash
# 使用合适的温度参数
--tmpr 0.3  # 高一致性（专业评估）
--tmpr 0.7  # 平衡模式（通用评估）
--tmpr 0.9  # 高创造性（探索性评估）
```

#### 多模型验证
```bash
# 使用多个模型验证结果
for model in gpt-4o claude-3-5-sonnet llama3.1; do
    python llm_assessment/run_assessment_unified.py \
        --model_name $model \
        --role_name intj \
        --test_file test.json
done

# 分析一致性
python analyze_consistency.py --results results/*.json
```

### 3. 批量处理优化

#### 并发控制
```bash
# 设置合理的并发数
export MAX_CONCURRENT_REQUESTS=3  # 根据API限制调整

# 内存优化
export BATCH_SIZE=5              # 小批量处理
export ENABLE_MEMORY_OPTIMIZATION=true
```

#### 错误恢复
```bash
# 启用断点续传
python final_batch_processor.py \
    --resume \
    --checkpoint-interval 10
```

### 4. 报告使用

#### 数据可视化
```python
# 创建综合仪表板
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 创建多图表布局
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Big Five', 'MBTI分布', '动机分析', '能力雷达图')
)

# 添加图表
fig.add_trace(go.Bar(...), row=1, col=1)
fig.add_trace(go.Pie(...), row=1, col=2)
fig.add_trace(go.Scatter(...), row=2, col=1)
fig.add_trace(go.Radar(...), row=2, col=2)

fig.show()
```

#### 报告定制
```python
# 自定义报告模板
from jinja2 import Template

template = Template('''
<!DOCTYPE html>
<html>
<head><title>{{ assessment_type }} - {{ name }}</title></head>
<body>
    <h1>{{ name }}的{{ assessment_type }}报告</h1>
    <div class="scores">
        {% for dimension, score in scores.items() %}
        <div class="score-item">
            <span class="dimension">{{ dimension }}</span>
            <span class="score">{{ score }}</span>
        </div>
        {% endfor %}
    </div>
</body>
</html>
''')

html_report = template.render(
    assessment_type="大五人格测评",
    name="张三",
    scores=big_five_scores
)
```

---

## 📚 API参考

### 核心模块API

#### AssessmentRunner
```python
from llm_assessment.run_assessment_unified import AssessmentRunner

runner = AssessmentRunner(
    model_name="gpt-4o",
    role_name="enfj",
    provider="cloud"
)

result = runner.run_assessment(
    test_file="test.json",
    temperature=0.7,
    max_tokens=1000
)
```

#### BatchProcessor
```python
from production_pipelines.local_batch_production import BatchProcessor

processor = BatchProcessor(
    model="llama3.1",
    roles=["enfj", "intj", "estj"],
    parallel_limit=4
)

results = processor.process_batch(
    test_files=["test1.json", "test2.json"],
    output_dir="results/"
)
```

#### UnifiedSkills
```python
from unified_questionnaire_responder import UnifiedQuestionnaireResponder
from unified_psychological_analyzer import UnifiedPsychologicalAnalyzer
from unified_report_generator import UnifiedReportGenerator

# 创建技能实例
responder = UnifiedQuestionnaireResponder()
analyzer = UnifiedPsychologicalAnalyzer()
generator = UnifiedReportGenerator()

# 完整工作流
responses = responder.generate_responses(questions, "big_five", "enfj")
analysis = analyzer.analyze_responses(responses)
report = generator.generate_report(analysis, "report.html")
```

### 配置API

#### ConfigurationValidator
```python
from config_validator import ConfigurationValidator

validator = ConfigurationValidator("configs/")

# 验证配置
config, errors = validator.load_config("big_five_personality.json")
if errors:
    print("配置错误:", errors)
else:
    print("配置有效:", config["name"])

# 生成配置模板
template = validator.generate_template("custom_assessment")
with open("custom_assessment.json", "w") as f:
    json.dump(template, f, indent=2)
```

#### AssessmentDetector
```python
from assessment_detector import AssessmentTypeDetector

detector = AssessmentTypeDetector(configs)

# 检测测评类型
result = detector.detect_from_content(questions, "test_file.json")
print(f"检测到类型: {result.assessment_type}")
print(f"置信度: {result.confidence}")
print(f"检测方法: {result.method}")
```

---

## 🎯 总结

AgentPsyAssessment 提供了一个完整、专业的心理评估解决方案。通过本手册，您应该能够：

✅ **掌握基础使用**：单次评估、批量处理、结果分析
✅ **理解系统架构**：评测系统、评估系统、统一技能系统
✅ **灵活配置应用**：自定义角色、测评类型、报告模板
✅ **优化工作流程**：提高效率、保证质量、处理异常
✅ **扩展系统功能**：添加新测评类型、集成外部系统

### 技术支持
- 📧 邮件支持：support@example.com
- 🐛 问题反馈：https://github.com/ptreezh/AgentPsyAssessment/issues
- 💬 社区讨论：https://github.com/ptreezh/AgentPsyAssessment/discussions
- 📖 文档更新：https://docs.example.com

---

**版本**: v1.0.0
**更新日期**: 2025-01-08
**作者**: AgentPsyAssessment Team

感谢您使用 AgentPsyAssessment！🎉