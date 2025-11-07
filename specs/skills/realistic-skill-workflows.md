# Portable PsyAgent - 技能组合工作流

## 工作流概述

基于真实的Claude Code技能架构，我们设计了一套完整的心理评估技能组合，可以在Claude Code CLI中无缝协作，实现从问卷生成到专业报告的完整流程。

## 完整技能生态系统

### 核心技能列表
1. **questionnaire-responder** - 问卷回答技能
2. **psychological-analyzer** - 心理分析技能
3. **stress-evaluator** - 压力评估技能
4. **report-generator** - 报告生成技能

---

## 实际应用场景工作流

### 场景1: 个人心理评估完整流程

```bash
# 步骤1: 生成问卷回答
claude code --print "请以ENFJ人格特征回答大五人格问卷" \
  --system-prompt "你是ENFJ人格类型：外向、直觉、情感、判断。你天生富有同理心，关心他人感受。在回答问卷时体现这些特质。" \
  --file questionnaires/big_five_questions.json \
  --save responses/enfj_responses.json

# 步骤2: 进行心理分析
claude code --print "请分析这份问卷回答，提供专业心理评估" \
  --system-prompt "你是专业的心理测量学专家。请分析这份问卷回答，计算大五人格得分，推断MBTI类型，提供专业的发展建议。" \
  --file responses/enfj_responses.json \
  --save analysis/enfj_analysis.json

# 步骤3: 压力评估
claude code --print "请评估压力水平和应对能力" \
  --system-prompt "你是压力心理学专家。请分析这份问卷回答中的压力相关指标，评估压力耐受性和心理韧性。" \
  --file responses/enfj_responses.json \
  --save analysis/enfj_stress_assessment.json

# 步骤4: 生成综合报告
claude code --print "请生成包含所有分析结果的专业报告" \
  --file analysis/enfj_analysis.json \
  --file analysis/enfj_stress_assessment.json \
  --template comprehensive \
  --include-charts \
  --output-format pdf \
  --save reports/enfj_comprehensive_assessment.pdf
```

### 场景2: 团队心理评估与发展规划

```bash
# 步骤1: 批量生成团队成员回答
for persona in ENFJ INTJ ESTP ISFJ; do
  claude code --print "请以${persona}人格角色回答团队评估问卷" \
    --system-prompt "你是${persona}人格类型的团队成员，请从团队协作角度回答问卷。" \
    --file questionnaires/team_assessment.json \
    --save "team_responses/${persona}_responses.json"
done

# 步骤2: 批量心理分析
for response_file in team_responses/*.json; do
  claude code --print "请分析团队成员心理特征和团队角色" \
    --system-prompt "你是组织心理学专家，请从团队协作角度分析这份问卷回答，识别团队角色倾向和协作风格。" \
    --file "$response_file" \
    --save "team_analysis/$(basename "$response_file" .json)_analysis.json"
done

# 步骤3: 生成团队分析报告
claude code --print "请生成团队心理分析报告" \
  --system-prompt "请整合所有团队成员的分析结果，生成团队整体心理画像、团队动力学分析和角色配置建议。" \
  --file team_analysis/*.json \
  --template team_analysis \
  --include-charts \
  --output-format docx \
  --save reports/team_psychological_assessment.docx
```

### 场景3: 压力测试和韧性建设

```bash
# 步骤1: 正常状态基准评估
claude code --print "请进行正常状态下的心理评估" \
  --system-prompt "请如实回答这份心理评估问卷，建立正常状态下的心理特征基准。" \
  --file questionnaires/comprehensive_assessment.json \
  --save stress_testing/baseline_responses.json

# 步骤2: 压力状态评估
claude code --print "请在高压工作环境下回答问卷" \
  --system-prompt "你正在面临紧急项目截止日期和重大工作压力。在回答问卷时，请体现压力下的心理状态，包括可能的焦虑、时间紧迫感等因素。" \
  --file questionnaires/comprehensive_assessment.json \
  --save stress_testing/stress_responses.json

# 步骤3: 对比压力影响分析
claude code --print "请对比分析正常和压力状态的差异" \
  --system-prompt "你是临床心理学家，请对比分析正常状态和压力状态下的心理特征差异，识别压力反应模式，评估心理韧性水平。" \
  --file stress_testing/baseline_responses.json \
  --file stress_testing/stress_responses.json \
  --save stress_testing/stress_impact_analysis.json

# 步骤4: 生成压力管理方案
claude code --print "请生成个性化压力管理和发展方案" \
  --system-prompt "请基于压力分析结果，制定个性化的压力管理策略和心理韧性提升方案，包括具体的干预措施和发展建议。" \
  --file stress_testing/stress_impact_analysis.json \
  --template development \
  --output-format pdf \
  --save reports/stress_management_plan.pdf
```

### 场景4: 职业发展和人才评估

```bash
# 步骤1: 职业情境问卷回答
claude code --print "请从软件工程师职业角度回答问卷" \
  --system-prompt "你是一位经验丰富的软件工程师，在回答问卷时请体现技术人员的思维特点、工作方式和职业发展需求。" \
  --file questionnaires/career_assessment.json \
  --save career/developer_responses.json

# 步骤2: 职业适配性分析
claude code --print "请进行职业适配性和发展潜力分析" \
  --system-prompt "你是职业发展专家，请从职业适配性、领导潜力、技能发展需求等角度分析这份问卷回答，提供职业发展指导。" \
  --file career/developer_responses.json \
  --save career/developer_career_analysis.json

# 步骤3: 生成职业发展报告
claude code --print "请生成职业发展评估报告" \
  --system-prompt "请生成专业的职业发展评估报告，包含适合的职业领域、技能发展重点、领导力潜力和具体的发展建议。" \
  --file career/developer_career_analysis.json \
  --template professional \
  --include-charts \
  --output-format docx \
  --save reports/career_development_assessment.docx
```

---

## 高级组合工作流

### 工作流1: 多人格对比研究

```bash
# 为多种人格类型生成对比数据
personas=("ENFJ" "INTJ" "ESTP" "ISFJ" "ENTP" "ISTJ" "ESFP" "INFJ")

for persona in "${personas[@]}"; do
  # 生成问卷回答
  claude code --print "请以${persona}人格特征回答问卷" \
    --system-prompt "你是典型的${persona}人格类型，请在回答问卷时充分体现该类型的核心特征和行为模式。" \
    --file questionnaires/big_five_questions.json \
    --save "comparison/${persona}_responses.json"

  # 进行心理分析
  claude code --print "请分析${persona}人格的心理特征" \
    --system-prompt "请深度分析${persona}人格类型的心理特征，包括认知模式、决策风格、团队角色和职业倾向。" \
    --file "comparison/${persona}_responses.json" \
    --save "comparison/${persona}_analysis.json"
done

# 生成对比分析报告
claude code --print "请生成多人格类型对比分析报告" \
  --system-prompt "请整合所有人格类型的分析结果，生成对比分析报告，识别不同人格类型的特征差异、优势和适用场景。" \
  --file comparison/*_analysis.json \
  --template comprehensive \
  --include-charts \
  --chart-types radar,bar,heatmap \
  --output-format pdf \
  --save reports/personality_comparison_study.pdf
```

### 工作流2: 组织心理健康评估

```bash
# 1. 员工个体评估
employee_ids=("emp001" "emp002" "emp003" "emp004" "emp005")

for emp_id in "${employee_ids[@]}"; do
  claude code --print "请生成员工${emp_id}的心理评估" \
    --system-prompt "请基于员工${emp_id}的工作角色和表现，生成符合其职业特征的心理问卷回答。" \
    --file questionnaires/workplace_assessment.json \
    --save "organization/${emp_id}_assessment.json"

  claude code --print "请分析员工${emp_id}的心理特征" \
    --system-prompt "请从组织心理学角度分析员工${emp_id}的心理特征，评估其工作适应性、团队角色和发展潜力。" \
    --file "organization/${emp_id}_assessment.json" \
    --save "organization/${emp_id}_analysis.json"
done

# 2. 组织层面分析
claude code --print "请生成组织心理健康评估报告" \
  --system-prompt "请整合所有员工的心理评估结果，从组织层面分析团队心理特征、潜在风险因素和发展建议。" \
  --file organization/*_analysis.json \
  --template team_analysis \
  --include-charts \
  --output-format docx \
  --save reports/organizational_psychological_assessment.docx

# 3. 制定干预方案
claude code --print "请制定组织心理发展干预方案" \
  --system-prompt "基于组织心理评估结果，请制定具体的心理发展干预方案，包括团队建设、个人发展和组织文化改进建议。" \
  --file reports/organizational_psychological_assessment.docx \
  --template professional \
  --output-format pdf \
  --save reports/organizational_intervention_plan.pdf
```

---

## 技能组合优势

### 1. 完整性覆盖
- **数据生成**: questionnaire-responder
- **专业分析**: psychological-analyzer, stress-evaluator
- **报告输出**: report-generator
- **端到端**: 从需求到报告的完整链条

### 2. 灵活组合
- 技能可独立使用
- 支持多种组合方式
- 适应不同应用场景
- 可扩展新技能

### 3. 专业质量
- 基于成熟心理学理论
- 多角度交叉验证
- 专业级分析深度
- 实用导向的建议

### 4. 技术实现
- 基于真实Claude Code架构
- 使用系统提示词和行为模式
- 支持命令行工具执行
- 符合实际技术约束

---

## 实施建议

### 1. 环境准备
```bash
# 创建工作目录
mkdir -p psychological_assessment/{responses,analysis,reports,questionnaires}

# 安装Python依赖（用于报告生成）
pip install pandas matplotlib seaborn jinja2 reportlab

# 检查Claude Code版本
claude code --version
```

### 2. 技能安装
```bash
# 将技能文件复制到Claude技能目录
cp -r specs/skills/* ~/.claude/skills/

# 或项目级别安装
cp -r specs/skills/* .claude/skills/
```

### 3. 测试验证
```bash
# 测试单个技能
claude code --print "测试问卷回答技能" \
  --file questionnaires/test_questions.json \
  --save test_responses.json

# 测试完整流程
claude code --print "测试完整评估流程" \
  --file test_responses.json \
  --template comprehensive \
  --output-format html \
  --save test_report.html
```

### 4. 定制化配置
```bash
# 自定义系统提示词
export PSYAGENT_PERSONA="临床心理学专家"
export PSYAGENT_LANGUAGE="zh-CN"
export PSYAGENT_OUTPUT_DIR="./custom_reports"
```

---

## 成功指标

### 1. 功能性指标
- ✅ 支持完整的心理评估流程
- ✅ 生成专业级分析报告
- ✅ 多场景灵活应用
- ✅ 高质量输出结果

### 2. 可用性指标
- ✅ 简单的命令行操作
- ✅ 清晰的文档和示例
- ✅ 错误处理和用户提示
- ✅ 批量处理能力

### 3. 专业性指标
- ✅ 基于科学心理学理论
- ✅ 多维度交叉验证
- ✅ 实用的发展建议
- ✅ 专业的报告格式

### 4. 技术性指标
- ✅ 基于真实Claude Code架构
- ✅ 符合技能实现规范
- ✅ 良好的代码组织
- ✅ 可扩展的模块设计

这套技能组合完全基于真实的Claude Code实现能力，提供了专业、实用、可扩展的心理评估解决方案，可以满足个人发展、团队建设、组织管理等多种应用需求。