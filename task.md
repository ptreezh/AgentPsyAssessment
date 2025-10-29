# 任务清单（TDD 与管线修复）

## 已完成
- 制定规格与整体计划（转换/简化保留项与去除项、本地评估产物与目录）
- 新增测试（TDD）
  - tests/test_conversion_spec.py
  - tests/test_simplification_spec.py
  - tests/test_local_evaluator_outputs.py
- UTF-8 配置修复
  - 新增 ensure_utf8()，移除导入期 stdout/stderr 改写；多处脚本在 main 内调用
  - 已修改：
    - unified_processing_pipeline.py
    - simplify_assessment_reports.py
    - optimized_batch_simplifier.py
    - enhanced_simplify_assessment_reports.py
    - run_complete_processing.py
    - batch_evaluate_reports_fixed.py
    - batch_evaluate_reports.py
    - batch_evaluate_models.py
    - multi_dimension_analysis.py
    - enhanced_simplify_from_original.py
    - start_complete_analysis.py
    - llm_assessment/demo_i18n.py
    - test_evaluation_detailed.py

## 进行中
- 转换/简化过滤器实现以通过新增测试
- 本地评估产物实现
  - Persona（顶级心理学家测评专家）注入
  - Big Five 评分与 MBTI 映射
  - 每报告独立 analysis.{md,json} 输出与独立日志
- 补充 monitor 对 03_local_models_evaluation 完成度统计

## 待办
- 在 convert_assessment_format.py 中实现 convert_assessment_report，按规格生成 meta/qa，并去除思维痕迹与注入噪声
- 在 enhanced_simplify_assessment_reports.py/simplify_assessment_reports.py 完成简化逻辑以删除思维痕迹，保留评分方法与标准
- 在 shared_analysis/analyze_results.py 接入对 01/02 产物的本地评估，输出：
  - results/complete_processing_workspace/03_local_models_evaluation/<report_id>/analysis.{json,md}
  - logs/local_eval/<report_id>.log
- 在 config/ollama_config.json 中为本地评估器添加 persona 前缀与参数透传
- monitor_batch_progress.py 增加 03 阶段计数与完成率
- 端到端 quick 批次运行与回归

## 风险与对策
- pytest 收集期再次崩溃：继续搜寻残留 stdout/stderr 改写，统一改为 ensure_utf8()
- 评估输出路径不一致：集中通过统一函数生成 eval 输出与日志路径
- 本地模型不可用：先在测试中打桩或用最小输入绕过实际推理，仅校验产物结构与存在性
