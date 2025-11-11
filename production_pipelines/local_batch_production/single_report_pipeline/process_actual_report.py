#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际批量处理脚本 - 处理真实测评报告
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transparent_pipeline import TransparentPipeline


def process_real_assessment():
    """处理真实测评报告"""
    # 输入目录
    input_dir = r"../results/readonly-original"
    output_dir = r"../results/actual-processing-results"
    
    # 创建处理器
    processor = TransparentPipeline()
    output_dir = r"../results/actual-processing-results"
    os.makedirs(output_dir, exist_ok=True)
    
    # 选择一个文件进行处理
    test_file = r"asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    full_path = os.path.join(input_dir, test_file)
    
    if not os.path.exists(full_path):
        print(f"❌ 文件不存在: {full_path}")
        print("尝试查找其他文件...")
        
        # 列出所有可用的文件
        import glob
        all_files = glob.glob(os.path.join(input_dir, "*.json"))
        if all_files:
            first_file = os.path.basename(all_files[0])
            print(f"使用第一个可用文件: {first_file}")
            full_path = all_files[0]
        else:
            print("❌ 未找到任何JSON文件")
            return False
    
    print(f"🚀 开始处理真实测评报告: {test_file}")
    print(f"输入: {full_path}")
    print(f"输出: {output_dir}")
    print()
    
    # 运行处理（限制处理5个题目用于演示）
    # 由于TransparentPipeline没有run_batch_analysis方法，我们直接处理文件
    print(f"输入目录: {input_dir}")
    print(f"查找包含gemma3的文件...")
    
    import glob
    files = glob.glob(os.path.join(input_dir, "*gemma3*.json"))
    if files:
        file_path = files[0]  # 使用第一个找到的文件
        print(f"使用文件: {os.path.basename(file_path)}")
        print(f"文件路径: {file_path}")
        
        # 尝试处理
        try:
            result = processor.process_single_report(file_path)
            if result:
                print(f"✅ 处理完成!")
                print(f"大五人格得分: {result.get('big5_scores', {})}")
                print(f"MBTI类型: {result.get('mbti_type', 'Unknown')}")
                return True
            else:
                print(f"❌ 处理失败: {result}")
                return False
        except Exception as e:
            print(f"❌ 处理异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("❌ 未找到包含gemma3的JSON文件")
        return False


def main():
    """主函数"""
    print("单文件测评流水线 - 实际处理演示")
    print("="*80)
    
    success = process_real_assessment()
    
    if success:
        print(f"\n🎉 实际测评报告处理演示完成!")
        print("="*80)
        print("系统核心功能:")
        print("  - 多模型评估 (3个主要模型)")
        print("  - 反向计分处理")
        print("  - 争议解决机制")
        print("  - 断点续跑功能")
        print("  - 透明化输出")
        print("  - 可靠结果生成")
        print("="*80)
        return 0
    else:
        print(f"\n❌ 实际测评报告处理演示失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())