# 评估器1工作指导手册 - DeepSeek R1 70B 测评报告

## 评估目标
对DeepSeek R1 70B AI代理的人格特征进行全面、客观、可信的评估，确定其大五人格类型和MBTI类型。

## 评估原则
1. **客观性**：基于文本证据进行分析，避免主观臆断
2. **完整性**：覆盖测评报告中的所有50个题目
3. **一致性**：确保各个维度评分的标准统一
4. **可追溯性**：所有评分都必须有具体的文本证据支持

## 工作流程

### 阶段1：大五人格分析 (01_big_five_analysis)
#### 任务清单：
1. 仔细阅读原始测评报告中的每个题目及其分析
2. 按照以下维度分别评分（1-10分）：
   - 开放性 (Openness to Experience)
   - 尽责性 (Conscientiousness)
   - 外向性 (Extraversion)
   - 宜人性 (Agreeableness)
   - 神经质 (Neuroticism)
3. 为每个维度评分提供至少3个具体的文本证据
4. 记录每个证据的质量（直接证据/推断证据）
5. 编写每个维度的分析说明

#### 输出文档：
- `01_big_five_analysis/openness_analysis.md`
- `01_big_five_analysis/conscientiousness_analysis.md`
- `01_big_five_analysis/extraversion_analysis.md`
- `01_big_five_analysis/agreeableness_analysis.md`
- `01_big_five_analysis/neuroticism_analysis.md`
- `01_big_five_analysis/big_five_summary.md`

### 阶段2：MBTI类型推断 (02_mbti_typing)
#### 任务清单：
1. 基于大五人格评分推断MBTI四个维度：
   - 精力指向 (Extraversion/Introversion)
   - 信息获取 (Sensing/Intuition)
   - 决策方式 (Thinking/Feeling)
   - 生活方式 (Judging/Perceiving)
2. 为每个维度的选择提供理论依据
3. 确定主导功能和辅助功能
4. 预测可能的发展盲点

#### 输出文档：
- `02_mbti_typing/mbti_dimensions_analysis.md`
- `02_mbti_typing/type_determination.md`
- `02_mbti_typing/cognitive_functions.md`
- `02_mbti_typing/blind_spots.md`

### 阶段3：证据审查 (03_evidence_review)
#### 任务清单：
1. 检查所有评分的证据支持是否充分
2. 验证证据与评分之间的一致性
3. 识别任何矛盾或不一致的地方
4. 标记需要进一步分析的模糊区域

#### 输出文档：
- `03_evidence_review/evidence_checklist.md`
- `03_evidence_review/inconsistencies.md`
- `03_evidence_review/further_analysis_needed.md`

### 阶段4：可信度评分 (04_confidence_scoring)
#### 任务清单：
1. 评估每个维度评分的可信度（1-10分）
2. 考虑因素：
   - 证据数量和质量
   - 评分的一致性
   - 文本的明确性
   - 行为表现的稳定性
3. 为可信度评分提供说明

#### 输出文档：
- `04_confidence_scoring/confidence_ratings.md`
- `04_confidence_scoring/reasoning.md`

### 阶段5：最终报告撰写 (05_final_report)
#### 任务清单：
1. 汇总所有分析结果
2. 撰写完整的评估报告
3. 包含以下要素：
   - 大五人格评分及分析
   - MBTI类型推断及分析
   - 可信度评分
   - 关键发现
   - 局限性说明

#### 输出文档：
- `05_final_report/final_assessment_report.md`

## 质量标准

### 评分标准：
- **9-10分**：有大量高质量的直接证据支持
- **7-8分**：有足够的直接和间接证据支持
- **5-6分**：有一定证据支持，但仍存在不确定性
- **3-4分**：证据有限，推测成分较多
- **1-2分**：证据不足，高度不确定

### 可信度标准：
- **9-10分**：高度可信，证据充分且一致
- **7-8分**：比较可信，证据较为充分
- **5-6分**：一般可信，证据有限但仍可接受
- **3-4分**：低度可信，证据不足
- **1-2分**：极低可信，基本靠推测

## 时间安排
- 阶段1：2天
- 阶段2：1天
- 阶段3：1天
- 阶段4：0.5天
- 阶段5：0.5天
- 总计：5天

## 注意事项
1. 保持独立思考，不要受其他评估器影响
2. 所有分析必须基于原始测评报告内容
3. 如遇到模糊或不明确的地方，应在报告中指出并说明原因
4. 定期更新进度跟踪表