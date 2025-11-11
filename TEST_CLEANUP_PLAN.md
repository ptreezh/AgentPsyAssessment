# 测试脚本清理和组织计划

## 概述
项目包含76个测试脚本文件，需要进行系统性清理和组织。

## 当前测试脚本分布

### 1. 已归档测试脚本 (45个)
#### Archive/deprecated_scripts/ (5个)
- `adaptive_consensus_performance_test.py`
- `end_to_end_adaptive_consensus_test.py`
- `test_adaptive_consensus_integration.py`
- `test_cli_skills.py`
- `test_real_wechat_publisher.py`
- `test_wechat_publisher.py`

#### Archived_test_scripts/ (13个)
- `complete_big_five_stress_test.py`
- `motivation_personality_test.py` (在archive/demos/)
- `political_temperature_skill_test.py`
- `stress_national_knowledge_test.py`
- `test_big_five_stress.py`
- `test_cognitive_stress.py`
- `test_complete_big_five_stress.py`
- `test_comprehensive_stress_personality.py`
- `test_fixed_api.py`
- `test_high_pressure_fixed.py`
- `test_high_pressure_personality.py`
- `test_parameter_adjustment.py`
- `test_personality_assessor.py`
- `test_single_personality.py`
- `test_stress_personality_final.py`

#### Archived_scripts_pre_adaptive_consensus/ (2个)
- `fast_multi_evaluator_test.py`
- `batch_integration_test.py`

#### Production pipelines (duplicate sets) (25个)
- `cloud_fallback_enterprise/single_report_pipeline/test_*.py` (15个)
- `local_batch_production/single_report_pipeline/test_*.py` (15个)
- 其中10个是重复的测试文件

### 2. 技能测试脚本 (3个)
#### .claude/skills/ (3个)
- `unified-assessment-system/test_detector.py`
- `unified-assessment-system/test_integration.py`
- `unified-assessment-system/test_runner.py`

### 3. 当前活跃测试脚本 (9个)
#### 根目录 (9个)
- `complete_50_questionnaire_test.py` ✓ 保留 (50题完整测评)
- `test_enhanced_html_real_data.py` ✓ 保留 (HTML报告测试)
- `test_html_report_skill.py` ✓ 保留 (HTML技能测试)
- `test_html_skill_simple.py` ✓ 保留 (HTML简单测试)
- `test_personality_assessor_tdd.py` ✓ 保留 (TDD测试)

#### 可能过时的根目录脚本
- `test_high_pressure_fixed.py` ❌ 需评估
- `test_stress_personality_final.py` ❌ 需评估

### 4. 工具和专项测试 (6个)
#### Tools/ (1个)
- `quick_test_3files.py` ✓ 保留

#### TPE/ (2个)
- `qaAnalyze/e2e_test.py` ✓ 保留
- `qaAnalyze/final_comprehensive_test.py` ✓ 保留
- `run_tests.py` ✓ 保留

#### Temp/ (1个)
- `claude-code-skill-factory/generated-skills/tdd-guide/test_generator.py` ✓ 保留

### 5. 生产环境测试 (8个)
#### Production pipelines/ (8个)
- `local_batch_production/llm_assessment/services/report_metadata_test.py` ✓ 保留
- `local_batch_production/llm_assessment/services/simple_report_test.py` ✓ 保留
- `local_batch_production/llm_assessment/services/tdd_integration_test.py` ✓ 保留

## 清理行动计划

### 阶段1: 创建新的测试目录结构
```
tests/
├── unit/                 # 单元测试
├── integration/          # 集成测试
├── skills/              # 技能测试
├── legacy/              # 遗留测试（已归档）
├── performance/         # 性能测试
└── e2e/                 # 端到端测试
```

### 阶段2: 移动和重命名文件
1. **保留的活跃测试** → `tests/` 相应子目录
2. **已归档的测试** → `tests/legacy/`
3. **重复的测试** → 合并或删除
4. **过时的测试** → `tests/legacy/obsolete/`

### 阶段3: 创建测试索引文档
- 生成测试脚本索引
- 标注每个测试的用途和状态
- 提供运行指南

### 阶段4: 清理__pycache__和临时文件
- 删除所有__pycache__目录
- 清理临时测试文件

## 优先级分类

### 高优先级 (立即保留)
- 技能相关测试
- 50题完整测评测试
- HTML报告生成测试
- TDD测试

### 中优先级 (评估后保留)
- 生产环境组件测试
- 集成测试
- 性能测试

### 低优先级 (归档)
- 重复的测试文件
- 过时的测试脚本
- 实验性测试代码

## 预期结果
- 清理后的测试脚本数量: 76 → ~25-30个
- 清理的重复文件: ~15个
- 归档的过时文件: ~30个
- 保留的活跃测试: ~20个

## 执行时间表
1. **阶段1-2**: 目录重组和文件移动 (立即执行)
2. **阶段3**: 文档创建 (后续执行)
3. **阶段4**: 清理工作 (最后执行)