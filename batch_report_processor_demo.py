#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理示例脚本
展示如何使用批量处理器处理多个测评报告
"""

import sys
import os
from pathlib import Path

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from batch_report_processor import BatchReportProcessor


def demonstrate_batch_processing():
    """演示批量处理功能"""
    print("批量处理示例演示")
    print("="*60)
    
    # 1. 创建批量处理器实例
    print("1. 创建批量处理器实例:")
    print("-"*40)
    
    # 设置输入输出目录
    input_dir = r"../results/readonly-original"
    output_dir = r"../results/batch-processing-demo"
    
    print(f"  输入目录: {input_dir}")
    print(f"  输出目录: {output_dir}")
    
    # 创建批量处理器
    processor = BatchReportProcessor(
        input_dir=input_dir,
        output_dir=output_dir,
        checkpoint_interval=3  # 每3个文件保存一次检查点
    )
    
    print(f"  检查点间隔: 每 {processor.checkpoint_interval} 个文件")
    print()
    
    # 2. 查找测评报告文件
    print("2. 查找测评报告文件:")
    print("-"*40)
    
    json_files = processor.find_json_files("*.json")
    print(f"  找到 {len(json_files)} 个测评报告文件")
    
    if json_files:
        print("  前5个文件:")
        for i, file_path in enumerate(json_files[:5]):
            print(f"    {i+1}. {file_path.name}")
        
        if len(json_files) > 5:
            print(f"    ... 还有 {len(json_files) - 5} 个文件")
    else:
        print("  ❌ 未找到任何测评报告文件")
        return False
    
    print()
    
    # 3. 演示断点续跑功能
    print("3. 演示断点续跑功能:")
    print("-"*40)
    
    # 模拟已处理的文件（用于演示检查点加载）
    print("  模拟已处理文件 (检查点加载):")
    for i, file_path in enumerate(json_files[:2]):  # 模拟已处理2个文件
        processor.processed_files.add(str(file_path))
        processor.results.append({
            'file_path': str(file_path),
            'success': True,
            'big5_scores': {
                'openness_to_experience': 3.2,
                'conscientiousness': 4.1,
                'extraversion': 2.8,
                'agreeableness': 3.9,
                'neuroticism': 2.1
            },
            'mbti_type': 'ISTJ' if i % 2 == 0 else 'ENFP',
            'processing_time': 120.5 + i * 10.2
        })
        processor.current_file_index = i + 1
    
    print(f"  已处理文件: {len(processor.processed_files)} 个")
    print(f"  当前索引: {processor.current_file_index}")
    
    # 保存检查点
    print("  保存检查点...")
    processor.save_checkpoint()
    
    # 模拟中断后重新运行
    print("  模拟中断后重新运行:")
    new_processor = BatchReportProcessor(
        input_dir=input_dir,
        output_dir=output_dir,
        checkpoint_interval=3
    )
    
    # 加载检查点
    new_processor.load_checkpoint()
    print(f"  重新加载检查点: {len(new_processor.processed_files)} 个文件已处理")
    print(f"  从中断处继续处理...")
    
    print()
    
    # 4. 处理剩余文件
    print("4. 处理剩余文件:")
    print("-"*40)
    
    # 限制处理文件数量用于演示
    limit = min(5, len(json_files))  # 最多处理5个文件
    
    success = new_processor.run_batch_processing(
        pattern="*.json",
        limit=limit,
        resume=True,
        no_save=False
    )
    
    if success:
        print("  ✅ 批量处理运行成功")
    else:
        print("  ❌ 批量处理运行失败")
    
    print()
    
    # 5. 检查输出文件
    print("5. 检查输出文件:")
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
    
    return success


def main():
    """主函数"""
    print("批量处理示例脚本")
    print("="*80)
    
    success = demonstrate_batch_processing()
    
    if success:
        print("🎉 批量处理示例演示完成!")
        print("批量处理器已准备好处理真实的测评报告!")
    else:
        print("❌ 批量处理示例演示失败!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())