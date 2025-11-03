#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析运行脚本
测试批量分析功能并演示断点续跑特性
"""

import sys
import os
import json
from pathlib import Path

# 添加项目目录到路径
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

from simple_batch_analyzer import SimpleBatchAnalyzer


def demonstrate_batch_analysis():
    """演示批量分析功能"""
    print("批量分析功能演示")
    print("="*60)
    
    # 设置输入输出目录
    input_dir = project_dir / "results" / "readonly-original"
    output_dir = project_dir / "results" / "batch-analysis-demo"
    
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 检查输入目录是否存在
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        print("请确保在正确的项目目录下运行此脚本")
        return False
    
    # 创建批量分析器
    print("创建批量分析器...")
    analyzer = SimpleBatchAnalyzer(
        input_dir=str(input_dir),
        output_dir=str(output_dir)
    )
    
    # 查找文件
    print("查找测评报告文件...")
    json_files = analyzer.find_json_files()
    print(f"  找到 {len(json_files)} 个测评报告文件")
    
    if not json_files:
        print("❌ 未找到任何测评报告文件")
        return False
    
    # 显示前几个文件
    print("前5个文件:")
    for i, file_path in enumerate(json_files[:5]):
        print(f"  {i+1}. {file_path.name}")
    
    if len(json_files) > 5:
        print(f"  ... 还有 {len(json_files) - 5} 个文件")
    
    print()
    
    # 运行批量分析（限制处理5个文件用于演示）
    print("开始批量分析 (限制处理5个文件用于演示)...")
    print("-"*60)
    
    try:
        analyzer.run_batch_analysis(limit=5)
        print("\n✅ 批量分析演示完成!")
        return True
    except Exception as e:
        print(f"\n❌ 批量分析演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_checkpoint_resume():
    """演示检查点恢复功能"""
    print("\n检查点恢复功能演示")
    print("="*60)
    
    # 设置相同的输入输出目录
    input_dir = project_dir / "results" / "readonly-original"
    output_dir = project_dir / "results" / "batch-analysis-demo"
    
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 检查是否存在之前的检查点
    checkpoint_file = output_dir / "checkpoint.pkl"
    if not checkpoint_file.exists():
        print("ℹ️  未找到检查点文件，无法演示恢复功能")
        print("请先运行批量分析演示以生成检查点")
        return False
    
    print("✅ 找到检查点文件，演示恢复功能...")
    
    # 创建新的批量分析器实例
    print("创建新的批量分析器实例...")
    new_analyzer = SimpleBatchAnalyzer(
        input_dir=str(input_dir),
        output_dir=str(output_dir)
    )
    
    # 加载检查点
    print("加载检查点...")
    new_analyzer.load_checkpoint()
    
    print(f"  已处理文件数: {len(new_analyzer.processed_files)}")
    print(f"  结果数量: {len(new_analyzer.results)}")
    
    # 继续处理剩余文件（再处理5个文件）
    print("\n继续处理剩余文件 (再处理5个文件)...")
    print("-"*60)
    
    try:
        new_analyzer.run_batch_analysis(limit=len(new_analyzer.processed_files) + 5)
        print("\n✅ 检查点恢复演示完成!")
        return True
    except Exception as e:
        print(f"\n❌ 检查点恢复演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("批量分析运行脚本")
    print("="*80)
    
    # 演示批量分析功能
    success1 = demonstrate_batch_analysis()
    
    # 演示检查点恢复功能
    success2 = demonstrate_checkpoint_resume()
    
    print(f"\n{'='*80}")
    if success1 and success2:
        print("🎉 所有演示完成!")
        print("批量分析系统已验证支持断点续跑功能")
    else:
        print("⚠️  部分演示失败")
        print("请检查系统配置和文件权限")
    
    return 0 if success1 and success2 else 1


if __name__ == "__main__":
    sys.exit(main())