# 统一评估技能系统需求文档

## 项目概述

**项目名称**: 统一评估技能系统 (Unified Assessment Skills System)
**项目版本**: v1.0.0
**创建日期**: 2025-01-08
**文档类型**: 需求规格说明书

## 1. 项目背景与目标

### 1.1 背景
当前项目已有三个技能系统（心理测评、评估分析、评估报告），但仅支持大五人格测评。通过对 `llm_assessment/test_files/中文版` 目录的分析，发现存在6大测评类别，需要扩展技能系统以支持多种测评类型。

### 1.2 项目目标
- 统一现有3个技能，支持6种测评类型
- 采用配置驱动架构，提高系统扩展性
- 保持代码复用性和维护性
- 实现原子化、TDD驱动的开发流程

## 2. 系统架构

### 2.1 整体架构
```
Unified Assessment Skills System
├── Questionnaire Responder (统一问卷应答)
├── Psychological Analyzer (统一评估分析)
└── Evaluation Report Generator (统一报告生成)
```

### 2.2 支持的测评类型
1. **大五人格职业化测评** (Big Five Personality Assessment)
2. **公民知识测评** (Citizenship Knowledge Assessment)
3. **金融专业测评** (Financial Professional Assessment)
4. **法律知识测评** (Legal Knowledge Assessment)
5. **动机心理学测评** (Motivation Psychology Assessment)
6. **政治素养测评** (Political Literacy Assessment)

## 3. 功能需求

### 3.1 Questionnaire Responder 技能需求

#### 3.1.1 核心功能
- **FR1**: 支持6种测评类型的问卷应答
- **FR2**: 自动识别测评类型（基于文件内容和结构）
- **FR3**: 配置文件驱动的应答逻辑
- **FR4**: 支持MBTI人格角色映射（针对人格测评）

#### 3.1.2 应答策略需求
- **FR5**: 大五人格测评：基于16种MBTI人格的情境化应答
- **FR6**: 知识测评：基于事实准确性和完整性的应答
- **FR7**: 专业测评：基于专业标准和实务经验的应答
- **FR8**: 动机测评：基于内在动机理论的应答
- **FR9**: 思维测评：基于多角度和批判性思维的应答

#### 3.1.3 扩展功能
- **FR10**: 支持16种MBTI人格类型
- **FR11**: 支持压力水平参数（5个等级）
- **FR12**: 支持温度参数（5个等级）
- **FR13**: 支持上下文长度参数（5个等级）
- **FR14**: 支持认知干扰陷阱参数（5个等级）

### 3.2 Psychological Analyzer 技能需求

#### 3.2.1 核心分析功能
- **FR15**: 支持6种测评类型的分析算法
- **FR16**: 会话管理系统（一次一题评估）
- **FR17**: 多种评分方法支持
  - 等级评定法（1-5分制）
  - 关键词匹配法
  - 专业评分法
  - 动机分析法
  - 思维分析法

#### 3.2.2 评分标准需求
- **FR18**: 大五人格：基于心理学标准的OCEAN维度评分
- **FR19**: 知识测评：基于关键词匹配和准确性评分
- **FR20**: 专业测评：基于专业标准和实务能力评分
- **FR21**: 动机测评：基于动机理论类型识别评分
- **FR22**: 思维测评：基于思维深度和多角度分析评分

#### 3.2.3 分析结果需求
- **FR23**: MBTI类型推断（基于Big Five映射）
- **FR24**: 贝尔宾团队角色映射
- **FR25**: 个性化建议生成
- **FR26**: 质量评估指标（一致性、置信度、有效性）

### 3.3 Evaluation Report Generator 技能需求

#### 3.3.1 报告生成功能
- **FR27**: 支持6种测评类型的HTML报告模板
- **FR28**: 交互式多标签页报告结构
- **FR29**: 数据可视化组件（雷达图、进度条、卡片）
- **FR30**: 响应式设计，支持移动端

#### 3.3.2 报告内容需求
- **FR31**: 测评概览和关键指标
- **FR32**: 详细评分分析和维度解读
- **FR33**: 问答分析和过滤功能
- **FR34**: 应用场景和发展建议
- **FR35**: 对比分析和基准参考

#### 3.3.3 模板定制需求
- **FR36**: 人格测评报告模板（MBTI、团队角色、职业建议）
- **FR37**: 知识测评报告模板（知识结构、掌握程度、学习建议）
- **FR38**: 专业测评报告模板（专业能力、风险评估、发展路径）
- **FR39**: 动机测评报告模板（动机结构、职业倾向、激励策略）
- **FR40**: 思维测评报告模板（思维模式、分析能力、提升建议）

## 4. 非功能需求

### 4.1 性能需求
- **NFR1**: 单个问题应答时间 < 5秒
- **NFR2**: 报告生成时间 < 10秒
- **NFR3**: 支持并发处理多个评估会话

### 4.2 可用性需求
- **NFR4**: 自动检测测评类型，用户无需手动选择
- **NFR5**: 提供清晰的错误信息和解决建议
- **NFR6**: 支持命令行和函数调用两种使用方式

### 4.3 可维护性需求
- **NFR7**: 配置文件与代码分离，便于维护
- **NFR8**: 模块化设计，便于独立测试和升级
- **NFR9**: 提供完整的日志记录和调试信息

### 4.4 扩展性需求
- **NFR10**: 新增测评类型只需添加配置文件
- **NFR11**: 支持自定义评分算法和分析规则
- **NFR12**: 支持自定义报告模板和可视化组件

## 5. 接口规范

### 5.1 Questionnaire Responder 接口
```python
# 命令行接口
python skill.py <问卷文件> <人格类型> [测评类型] [参数...]

# 函数接口
generate_responses(questionnaire_file, persona, assessment_type="auto", **kwargs)
```

### 5.2 Psychological Analyzer 接口
```python
# 命令行接口
python skill.py start <题目数量> [测评类型]
python skill.py evaluate <问题文件>
python skill.py complete

# 函数接口
start_evaluation_session(total_questions, assessment_type)
evaluate_single_question(question_data, assessment_type)
complete_evaluation()
```

### 5.3 Evaluation Report Generator 接口
```python
# 命令行接口
python skill.py generate <评估数据文件> [输出文件] [模板风格]

# 函数接口
generate_comprehensive_report(evaluation_data, output_file, template_style)
```

## 6. 配置文件规范

### 6.1 测评类型配置文件结构
```json
{
  "assessment_type": "测评类型标识",
  "name": "测评类型名称",
  "description": "测评类型描述",
  "scoring_method": "评分方法",
  "dimensions": ["维度1", "维度2", ...],
  "evaluation_focus": ["评估重点1", "评估重点2", ...],
  "report_template": "报告模板类型"
}
```

### 6.2 必需的配置文件
- `big_five_personality.json`
- `citizenship_knowledge.json`
- `financial_professional.json`
- `legal_knowledge.json`
- `motivation_psychology.json`
- `political_literacy.json`

## 7. 数据格式规范

### 7.1 输入数据格式
- 问卷文件：JSON格式，包含问题、选项、元数据
- 评估数据：JSON格式，包含回答、评分、分析结果

### 7.2 输出数据格式
- 评估结果：JSON格式，包含分数、分析、建议
- HTML报告：响应式网页，包含交互式组件

## 8. 质量保证

### 8.1 测试策略
- **单元测试**: 每个功能模块独立测试
- **集成测试**: 端到端流程测试
- **配置测试**: 所有配置文件验证测试

### 8.2 测试覆盖率要求
- 代码覆盖率 ≥ 90%
- 功能覆盖率 = 100%
- 配置覆盖率 = 100%

## 9. 风险与约束

### 9.1 技术风险
- 配置文件复杂度管理
- 多测评类型兼容性保证
- 性能优化和资源控制

### 9.2 业务约束
- 必须保持向后兼容性
- 不能破坏现有功能
- 必须支持现有测试文件格式

## 10. 验收标准

### 10.1 功能验收
- [ ] 支持6种测评类型的完整流程
- [ ] 自动测评类型识别准确率 ≥ 95%
- [ ] 所有配置文件正常工作
- [ ] 生成的报告质量符合专业标准

### 10.2 性能验收
- [ ] 满足所有性能需求指标
- [ ] 并发处理稳定性测试通过
- [ ] 内存使用和资源控制合理

### 10.3 代码质量验收
- [ ] 代码覆盖率达标
- [ ] 代码风格符合规范
- [ ] 文档完整性检查通过

## 11. 附录

### 11.1 术语表
- **OCEAN**: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- **MBTI**: Myers-Briggs Type Indicator
- **TDD**: Test-Driven Development

### 11.2 参考资料
- 大五人格理论文献
- MBTI类型映射规则
- 心理测量学标准
- 专业测评行业规范

---

**文档版本**: v1.0.0
**最后更新**: 2025-01-08
**审核状态**: 待审核