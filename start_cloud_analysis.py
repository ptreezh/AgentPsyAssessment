#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def start_background_analysis():
    """启动后台云模型评估分析"""
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    try:
        # 使用Python模块方式运行
        cmd = f"start /b python -c \"import asyncio; from cloud_model_evaluator import main; asyncio.run(main())\""
        subprocess.Popen(cmd, shell=True, cwd=str(project_root))
        print("✅ 云模型评估分析已在后台启动")
        print("💡 查看 cloud_evaluation_output 目录中的结果文件")
        print("💡 使用任务管理器或 'tasklist | findstr python' 查看进程")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

if __name__ == "__main__":
    start_background_analysis()