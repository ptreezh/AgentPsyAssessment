#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测评报告分析器使用示例
展示如何使用支持断点续跑的批量分析器
"""

import sys
import os
from pathlib import Path

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_report_analyzer import BatchAnalyzer


def demonstrate_batch_analyzer_usage():
    """演示批量分析器使用方法"""
    print("批量测评报告分析器使用示例")
    print("="*60)
    
    # 1. 基本使用方法
    print("1. 基本使用方法:")
    print("-"*40)
    
    # 设置输入输出目录
    input_dir = r"../results/readonly-original"
    output_dir = r"../results/batch-analysis-demo"
    
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 创建批量分析器实例
    analyzer = BatchAnalyzer(
        input_dir=input_dir,
        output_dir=output_dir,
        checkpoint_interval=5  # 每处理5个文件保存一次检查点
    )
    
    print(f"检查点间隔: 每 {analyzer.checkpoint_interval} 个文件")
    print()
    
    # 2. 运行批量分析
    print("2. 运行批量分析:")
    print("-"*40)
    
    # 运行分析（限制处理10个文件用于演示）
    success = analyzer.run_batch_analysis(
        pattern="*.json",      # 文件匹配模式
        limit=10,              # 限制处理10个文件
        resume=True,           # 启用断点续跑
        no_save=False          # 保存结果
    )
    
    if success:
        print("  ✅ 批量分析运行成功")
    else:
        print("  ❌ 批量分析运行失败")
    
    print()
    
    # 3. 检查输出文件
    print("3. 输出文件检查:")
    print("-"*40)
    
    output_path = Path(output_dir)
    if output_path.exists():
        output_files = list(output_path.glob("*"))
        print(f"  输出目录文件数: {len(output_files)}")
        for file in output_files:
            print(f"    - {file.name}")
    else:
        print("  ❌ 输出目录不存在")
    
    print()
    
    # 4. 断点续跑演示
    print("4. 断点续跑演示:")
    print("-"*40)
    
    print("  模拟中断后重新运行:")
    print("  new_analyzer = BatchAnalyzer(input_dir, output_dir)")
    print("  new_analyzer.run_batch_analysis(resume=True)")
    print("  系统将自动从上次中断处继续处理")
    
    print()
    
    # 5. 高级使用选项
    print("5. 高级使用选项:")
    print("-"*40)
    
    print("  命令行使用:")
    print("    python batch_report_analyzer.py --input-dir ../results/readonly-original")
    print("    python batch_report_analyzer.py --output-dir ../results/my-results --limit 100")
    print("    python batch_report_analyzer.py --pattern '*gemma3*.json' --checkpoint-interval 10")
    print("    python batch_report_analyzer.py --no-resume  # 不从检查点恢复")
    
    print()
    
    print("="*60)
    print("使用示例演示完成!")
    print("现在可以开始处理真实的测评报告了!")


def main():
    """主函数"""
    demonstrate_batch_analyzer_usage()


if __name__ == "__main__":
    main()