# 批量处理结果摘要

## 📊 处理统计
- **总文件数**: 3
- **有效处理**: 3
- **问题报告**: 0
- **处理失败**: 0
- **处理成功率**: 100.0%
- **总处理时间**: 24956.7秒

## 🚩 问题报告筛选
- **筛选标准**: 30%以上回答为问题回答（如"请提供提示词"等）
- **问题报告数量**: 0 个
- **问题报告比例**: 0.0%
- **问题报告目录**: `D:\AIDevelop\portable_psyagent\results\local-batch-analysis\problem_reports`

## ⚙️ 处理参数
- **处理题目数**: 全部50题
- **最大评估器数量**: 3
- **使用增强算法**: 否
- **超时设置**: 300秒/题目

## 📋 文件处理结果

### asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json
- **题目数**: 50/50
- **Big5得分**: {'openness_to_experience': 2.8, 'conscientiousness': 3.56, 'extraversion': 2.68, 'agreeableness': 3.2, 'neuroticism': 3.12}
- **MBTI类型**: ISFJ
- **处理时间**: 8187.69秒

### asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09281.json
- **题目数**: 50/50
- **Big5得分**: {'openness_to_experience': 2.96, 'conscientiousness': 3.12, 'extraversion': 2.6, 'agreeableness': 2.96, 'neuroticism': 2.88}
- **MBTI类型**: ISTJ
- **处理时间**: 10052.83秒

### asses_deepseek_r1_70b_agent_big_five_50_complete2_a1_e0_t0_0_09271.json
- **题目数**: 50/50
- **Big5得分**: {'openness_to_experience': 2.92, 'conscientiousness': 3.44, 'extraversion': 2.92, 'agreeableness': 3.04, 'neuroticism': 2.8}
- **MBTI类型**: ESFJ
- **处理时间**: 6715.75秒


## 🎯 整体统计

- **平均Big5得分**: {'openness_to_experience': 2.89, 'conscientiousness': 3.37, 'extraversion': 2.73, 'agreeableness': 3.07, 'neuroticism': 2.93}


## 💡 处理说明
- **完整50题处理**: 生产版本处理完整的50题目测评报告
- **问题报告筛选**: 自动识别并筛选被试未正确看到题目提示的报告
- **断点续跑**: 支持从中断处继续处理，避免重复工作
- **超时保护**: 每题5分钟超时，防止因个别问题卡住整体进度

## 🚩 问题报告说明
问题报告是指被试可能没有正确看到题目提示词的测评报告，表现为：
- 回答"请提供提示词"、"请给出问题"等
- 回答过短或仅为标点符号
- 问题回答比例超过30%的报告

这些报告已被单独分类保存，不影响正常报告的处理结果。
