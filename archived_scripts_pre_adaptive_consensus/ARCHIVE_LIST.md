# 批量评估和单个评估分析脚本存档清单

## 存档原因
这些脚本未使用 adaptive_consensus_algorithm.py 中的自适应共识算法，按照用户要求"不要改造，直接废弃 存档"进行归档。

## 存档的脚本列表

### 批量处理脚本
1. `llm_assessment/interactive_batch.py` - 交互式批量处理
2. `production_pipelines/cloud_fallback_enterprise/single_report_pipeline/batch_processor.py` - 云端回退批量处理器
3. `production_pipelines/cloud_fallback_enterprise/single_report_pipeline/batch_report_analyzer.py` - 批量报告分析器
4. `production_pipelines/cloud_fallback_enterprise/single_report_pipeline/standalone_batch_processor.py` - 独立批量处理器
5. `production_pipelines/cloud_fallback_enterprise/single_report_pipeline/usage_example_batch.py` - 批量使用示例
6. `production_pipelines/local_batch_production/batch_processor_original.py` - 原始批量处理器
7. `production_pipelines/local_batch_production/cloud_fallback_batch_processor.py` - 云端回退批量处理器
8. `production_pipelines/local_batch_production/llm_assessment/batch_analysis.py` - LLM批量分析
9. `production_pipelines/local_batch_production/llm_assessment/batch_analysis_complete.py` - 完整批量分析
10. `production_pipelines/local_batch_production/llm_assessment/batch_analysis_enhanced.py` - 增强批量分析
11. `production_pipelines/local_batch_production/llm_assessment/batch_analysis_final.py` - 最终批量分析
12. `production_pipelines/local_batch_production/llm_assessment/interactive_batch.py` - 交互式批量处理
13. `production_pipelines/local_batch_production/llm_assessment/interactive_batch_runner.py` - 交互式批量运行器
14. `production_pipelines/local_batch_production/llm_assessment/quick_batch.py` - 快速批量处理
15. `production_pipelines/local_batch_production/llm_assessment/run_batch_suite.py` - 批量套件运行器
16. `production_pipelines/local_batch_production/llm_assessment/services/batch_integration_test.py` - 批量集成测试
17. `production_pipelines/local_batch_production/unbuffered_batch_optimizer.py` - 无缓冲批量优化器
18. `batch_personality_generator.py` - 人格批量生成器
19. `batch_html_reports.py` - HTML批量报告
20. `scripts/bank_big5_batch_generator.py` - 银行大五批量生成器
21. `run_cloud_batch.py` - 云端批量运行器
22. `production_pipelines/cloud_fallback_enterprise/cloud_fallback_batch_processor.py` - 云端回退批量处理器
23. `run_local_batch.py` - 本地批量运行器
24. `production_pipelines/local_batch_production/single_report_pipeline/usage_example_batch.py` - 批量使用示例
25. `production_pipelines/local_batch_production/single_report_pipeline/standalone_batch_processor.py` - 独立批量处理器
26. `production_pipelines/local_batch_production/single_report_pipeline/batch_report_analyzer.py` - 批量报告分析器
27. `production_pipelines/local_batch_production/single_report_pipeline/batch_processor.py` - 批量处理器
28. `batch_process_all_questionnaires.py` - 问卷批量处理器
29. `simple_batch_processor.py` - 简单批量处理器

### 分析脚本
1. `production_pipelines/local_batch_production/llm_assessment/batch_analysis.py` - 批量分析
2. `production_pipelines/local_batch_production/llm_assessment/batch_analysis_complete.py` - 完整批量分析
3. `production_pipelines/local_batch_production/llm_assessment/batch_analysis_enhanced.py` - 增强批量分析
4. `production_pipelines/local_batch_production/llm_assessment/batch_analysis_final.py` - 最终批量分析
5. `production_pipelines/local_batch_production/llm_assessment/comprehensive_big5_analysis.py` - 综合大五分析
6. `production_pipelines/local_batch_production/llm_assessment/full_comprehensive_big5_analysis.py` - 完整综合大五分析
7. `production_pipelines/local_batch_production/llm_assessment/perform_comparison_analysis.py` - 比较分析
8. `production_pipelines/local_batch_production/shared_analysis/interactive_analysis.py` - 交互式分析

### 评估器脚本
1. `production_pipelines/local_batch_production/data_quality_enhanced_evaluator.py` - 数据质量增强评估器
2. `production_pipelines/local_batch_production/fast_multi_evaluator_test.py` - 快速多评估器测试
3. `production_pipelines/local_batch_production/shared_analysis/ollama_evaluator.py` - Ollama评估器
4. `production_pipelines/local_batch_production/smart_evaluator.py` - 智能评估器
5. `production_pipelines/local_batch_production/three_model_ollama_evaluator.py` - 三模型Ollama评估器

### 处理器脚本
1. `production_pipelines/cloud_fallback_enterprise/single_report_pipeline/enhanced_reverse_scoring_processor.py` - 增强反向评分处理器
2. `production_pipelines/cloud_fallback_enterprise/single_report_pipeline/reverse_scoring_processor.py` - 反向评分处理器
3. `production_pipelines/local_batch_production/assessment_processor.py` - 评估处理器
4. `production_pipelines/local_batch_production/batch_processor_original.py` - 原始批量处理器
5. `production_pipelines/local_batch_production/cloud_fallback_batch_processor.py` - 云端回退批量处理器
6. `production_pipelines/local_batch_production/single_report_pipeline/enhanced_reverse_scoring_processor.py` - 增强反向评分处理器
7. `production_pipelines/local_batch_production/single_report_pipeline/reverse_scoring_processor.py` - 反向评分处理器
8. `simple_batch_processor.py` - 简单批量处理器

## 保留的脚本（已对齐自适应共识算法）
以下脚本使用 adaptive_consensus_algorithm.py，予以保留：

### 核心脚本
1. `production_pipelines/cloud_fallback_enterprise/adaptive_consensus_algorithm.py` - **核心自适应共识算法**
2. `production_pipelines/local_batch_production/single_report_pipeline/transparent_pipeline.py` - **已集成自适应共识算法的透明流水线**
3. `production_pipelines/local_batch_production/single_report_pipeline/adaptive_consensus_algorithm.py` - **流水线版本的自适应共识算法**

### 测试脚本
1. `adaptive_consensus_performance_test.py` - 自适应共识算法性能测试
2. `end_to_end_adaptive_consensus_test.py` - 端到端自适应共识测试
3. `test_adaptive_consensus_integration.py` - 自适应共识集成测试

## 存档时间
2025-11-08

## 说明
- 所有存档脚本保持原有功能不变，仅移动到存档目录
- 如需使用旧脚本，请从 archived_scripts_pre_adaptive_consensus 目录中恢复
- 推荐使用保留的基于自适应共识算法的脚本进行新的开发