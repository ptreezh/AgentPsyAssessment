# 可信评估报告移动脚本

## 功能说明
此脚本用于将通过可信度验证的评估报告移动到最终验证报告目录。

## 使用方法
1. 确认评估报告已通过可信度验证
2. 运行此脚本将报告移动到final_verified_reports目录

## 移动命令示例

```bash
# 移动DeepSeek R1 70B的评估报告
move "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\assessment_reports\deepseek_r1_70b_assessment" "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\final_verified_reports\"

# 移动DeepSeek R1 8B的评估报告
move "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\assessment_reports\deepseek_r1_8b_assessment" "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\final_verified_reports\"

# 移动GLM4 9B的评估报告
move "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\assessment_reports\glm4_9b_assessment" "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\final_verified_reports\"

# 移动Llama3.2 1B的评估报告
move "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\assessment_reports\llama3_2_1b_assessment" "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\final_verified_reports\"

# 移动Qwen3 32B (版本1)的评估报告
move "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\assessment_reports\qwen3_32b_v1_assessment" "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\final_verified_reports\"

# 移动Qwen3 32B (版本2)的评估报告
move "D:\AIDeDevelop\portable_psyagent\results\trustworthy_assessment_system\assessment_reports\qwen3_32b_v2_assessment" "D:\AIDevelop\portable_psyagent\results\trustworthy_assessment_system\final_verified_reports\"
```

## 注意事项
1. 只有通过可信度验证的报告才能移动
2. 移动前请确保所有评估器已完成评估
3. 移动后请更新状态跟踪文档