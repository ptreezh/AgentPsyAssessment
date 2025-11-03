@echo off
REM Git提交和推送脚本

cd /d D:\AIDevelop\portable_psyagent

echo 正在添加文件...
git add .

echo 正在提交更改...
git commit -m "feat: 增强版单文件测评流水线完成实现

- 实现多模型评估器增强功能
- 实现透明化流水线增强功能  
- 实现争议解决机制增强功能
- 实现信度验证和置信度评估功能
- 支持反向计分题目的正确处理
- 实现断点续跑和检查点机制
- 添加生产版本批量处理器
- 完善文档和测试用例"

echo 正在推送到远程仓库...
git push origin main

echo 所有更改已成功提交并推送到远程仓库!
pause