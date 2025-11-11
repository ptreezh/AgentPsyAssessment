# 测试脚本组织和索引

## 概述
本目录包含了项目中所有测试脚本的有序组织。测试按照功能和用途进行分类。

## 目录结构

### 📁 unit/ - 单元测试
- `test_personality_assessor_tdd.py` - TDD驱动的人格评估器技能测试

### 📁 integration/ - 集成测试
- `complete_50_questionnaire_test.py` - 完整50题问卷集成测试

### 📁 skills/ - 技能测试
- `test_enhanced_html_real_data.py` - 增强版HTML报告生成器真实数据测试
- `test_html_report_skill.py` - HTML报告生成器技能测试
- `test_html_skill_simple.py` - HTML技能简单测试

### 📁 legacy/ - 遗留测试（已归档）
- `test_high_pressure_fixed.py` - 高压力修复测试（已废弃）
- `test_stress_personality_final.py` - 压力人格最终测试（已废弃）

### 📁 performance/ - 性能测试
（预留目录，未来添加）

### 📁 e2e/ - 端到端测试
（预留目录，未来添加）

## 测试分类说明

### 🟢 活跃测试（推荐使用）
1. **技能测试** (`skills/`)
   - HTML报告生成相关测试
   - 当前技能功能验证

2. **单元测试** (`unit/`)
   - TDD测试框架
   - 核心组件单元测试

3. **集成测试** (`integration/`)
   - 50题完整问卷测试
   - 多组件集成验证

### 🟡 评估中测试
- 暂无

### 🔴 遗留测试（已归档）
- `legacy/` 目录中的测试脚本
- 保留用于历史参考，不推荐在新开发中使用

## 运行指南

### 运行所有活跃测试
```bash
# 运行技能测试
python tests/skills/test_enhanced_html_real_data.py
python tests/skills/test_html_report_skill.py
python tests/skills/test_html_skill_simple.py

# 运行单元测试
python tests/unit/test_personality_assessor_tdd.py

# 运行集成测试
python tests/integration/complete_50_questionnaire_test.py
```

### 运行特定类型测试
```bash
# 只运行技能测试
find tests/skills -name "*.py" -exec python {} \;

# 只运行单元测试
find tests/unit -name "*.py" -exec python {} \;
```

## 测试命名规范

### 当前使用的命名
- `test_*.py` - 标准测试文件
- `*_test.py` - 集成测试文件

### 建议的命名规范
- `test_<functionality>_<type>.py`
  - `<functionality>`: 测试的功能模块
  - `<type>`: 测试类型 (unit, integration, e2e, performance)

## 维护指南

### 添加新测试
1. 确定测试类型和分类
2. 放置到对应目录
3. 更新此README文档
4. 遵循命名规范

### 废弃测试
1. 移动到 `tests/legacy/` 目录
2. 添加废弃说明注释
3. 更新文档中的状态

### 清理__pycache__
```bash
find tests -name "__pycache__" -type d -exec rm -rf {} +
find tests -name "*.pyc" -delete
```

## 历史归档

### 已移动的测试文件
以下文件已经从根目录移动到新的组织结构中：

#### 从根目录移动
- `complete_50_questionnaire_test.py` → `tests/integration/`
- `test_enhanced_html_real_data.py` → `tests/skills/`
- `test_html_report_skill.py` → `tests/skills/`
- `test_html_skill_simple.py` → `tests/skills/`
- `test_personality_assessor_tdd.py` → `tests/unit/`
- `test_high_pressure_fixed.py` → `tests/legacy/`
- `test_stress_personality_final.py` → `tests/legacy/`

### 已归档的测试目录
- `archive/deprecated_scripts/` - 已弃用的脚本
- `archived_test_scripts/` - 旧版测试脚本
- `archived_scripts_pre_adaptive_consensus/` - 共识算法前的脚本

## 统计信息

- **总测试脚本数**: 76 → 28 (已清理)
- **活跃测试**: 7个
- **遗留测试**: 2个
- **已归档**: ~45个
- **生产环境测试**: ~8个

## 最后更新
- 更新时间: 2025-11-10
- 更新内容: 初始测试组织结构建立