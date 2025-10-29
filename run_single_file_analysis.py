#!/usr/bin/env python3
"""
运行单个文件的五题分段多评估器分析
"""

import sys
import os
import json
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        from comprehensive_batch_analysis import ComprehensiveBatchAnalyzer
        
        print("=== 运行单个文件的多评估器分析 ===")
        
        # 创建分析器
        input_dir = "results/results"
        output_dir = "results/single_file_test"
        
        analyzer = ComprehensiveBatchAnalyzer(input_dir, output_dir)
        
        # 获取文件列表
        raw_files = analyzer.find_raw_reports()
        
        if not raw_files:
            print("没有找到测评报告文件")
            return
            
        # 只处理第一个文件
        first_file = raw_files[0]
        print(f"处理文件: {first_file.name}")
        
        # 处理单个文件
        result = analyzer.process_single_file(first_file)
        
        print(f"处理结果: {result['status']}")
        
        if result['status'] == 'completed':
            print("✓ 分析成功")
            print(f"评估器数量: {len(result['final_result'].get('evaluator_results', {}))}")
        else:
            print(f"✗ 分析失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()