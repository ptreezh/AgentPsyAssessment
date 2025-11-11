# 🚨 重要：评测与评估系统分离说明

## ⚠️ 关键区别：请勿混淆

### 📝 评测系统 (Assessment System)
**功能**: 生成心理问卷答卷
- **位置**: `llm_assessment/` 目录
- **用途**: AI扮演特定人格角色，完成心理问卷
- **特点**: 单一模型创造性工作
- **无需**: 共识算法

### 🎯 评估系统 (Evaluation System)
**功能**: 对答卷进行评分和人格分析
- **位置**: `production_pipelines/local_batch_production/single_report_pipeline/`
- **用途**: 多个AI评估员对已有答卷进行科学评分
- **特点**: 多模型一致性评估
- **必需**: 自适应共识算法

## 🔄 正确的工作流程

```
📝 第一步：生成答卷 (评测系统)
┌─────────────────────────────────────────┐
│  llm_assessment/run_assessment_unified.py │  ← 单一模型生成
│  --model gpt-4 --role enfj               │
└─────────────────────────────────────────┘
                    ↓
                    ↓ 生成答卷.json
                    ↓
🎯 第二步：评分分析 (评估系统)
┌─────────────────────────────────────────┐
│  transparent_pipeline.py                │  ← 多模型评估
│  + adaptive_consensus_algorithm.py       │  ← 自适应共识算法
└─────────────────────────────────────────┘
                    ↓
                    ↓ 评分结果 + 可靠性分析
                    ↓
```

## ❌ 常见错误

### 错误1：试图给评测系统加共识算法
```bash
# ❌ 错误：评测不需要共识
python llm_assessment/run_assessment_unified.py --consensus
```
**原因**: 评测是创造性工作，单一模型即可

### 错误2：混淆系统入口
```bash
# ❌ 错误：混淆功能
python transparent_pipeline.py --generate-questions
```
**原因**: 评估系统只评分，不生成答卷

### 错误3：期望评测系统输出可靠性指标
```bash
# ❌ 错误：评测没有可靠性指标
python llm_assessment/run_assessment_unified.py --reliability
```
**原因**: 只有评估系统才有多模型一致性分析

## ✅ 正确示例

### 生成答卷 (评测系统)
```bash
# ✅ 正确：生成答卷
python llm_assessment/run_assessment_unified.py --model gpt-4 --role enfj
```

### 评分分析 (评估系统)
```python
# ✅ 正确：评估答卷
from transparent_pipeline import TransparentPipeline
pipeline = TransparentPipeline(use_cloud=True)
result = pipeline.process_single_question(question_data, 0)
print(f"评分: {result['final_adjusted_scores']}")
print(f"可靠性: {result['confidence_metrics']['overall_reliability']}")
```

## 📁 目录结构指南

```
AgentPsyAssessment/
├── 📝 llm_assessment/                    # 评测系统 (生成答卷)
│   ├── run_assessment_unified.py          # 主要入口
│   ├── roles/                             # 人格角色定义
│   └── test_files/                        # 问卷文件
│
├── 🎯 production_pipelines/.../single_report_pipeline/  # 评估系统 (评分分析)
│   ├── transparent_pipeline.py            # 主要入口
│   ├── adaptive_consensus_algorithm.py     # 自适应共识算法
│   └── input_parser.py                    # 答卷解析
│
└── 📚 README_SYSTEM_SEPARATION.md         # 本说明文件
```

## 🔗 详细文档

- **评测系统文档**: `llm_assessment/README.md`
- **评估系统文档**: `production_pipelines/local_batch_production/single_report_pipeline/README.md`
- **项目主文档**: `CLAUDE.md`

## 💡 记忆技巧

- **评测 (Assessment)** = **Assess** 评估能力 → 生成答卷展示能力
- **评估 (Evaluation)** = **Evaluate** 评价价值 → 对答卷科学评分

**简单记忆**: 先"评测"生成答卷，再"评估"打分分析

---

**如有疑问，请务必确认您在使用正确的系统阶段！**