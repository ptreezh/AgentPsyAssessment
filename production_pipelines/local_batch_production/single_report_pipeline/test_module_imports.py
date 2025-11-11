#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块导入测试脚本
验证所有模块能否正确导入
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_module_imports():
    """测试模块导入"""
    print("模块导入测试")
    print("="*60)
    
    # 测试核心模块导入
    print("1. 测试核心模块导入:")
    try:
        from transparent_pipeline import TransparentPipeline
        from reverse_scoring_processor import ReverseScoringProcessor
        from input_parser import InputParser
        from context_generator import ContextGenerator
        print("  ✅ 核心模块导入成功")
    except ImportError as e:
        print(f"  ❌ 核心模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试增强模块导入
    print("2. 测试增强模块导入:")
    try:
        # 检查增强模块文件是否存在
        import os
        if os.path.exists("enhanced_reverse_scoring_processor.py"):
            from enhanced_reverse_scoring_processor import EnhancedReverseScoringProcessor
            print("  ✅ 增强反向计分处理器导入成功")
        else:
            print("  ⚠️  增强反向计分处理器文件不存在")
            
        if os.path.exists("enhanced_dispute_resolution_pipeline.py"):
            from enhanced_dispute_resolution_pipeline import EnhancedDisputeResolutionPipeline
            print("  ✅ 增强争议解决流水线导入成功")
        else:
            print("  ⚠️  增强争议解决流水线文件不存在")
    except ImportError as e:
        print(f"  ⚠️  增强模块导入警告: {e}")
        # 不影响整体测试
    
    # 测试类实例化
    print("3. 测试类实例化:")
    try:
        pipeline = TransparentPipeline()
        reverse_processor = ReverseScoringProcessor()
        input_parser = InputParser()
        context_generator = ContextGenerator()
        print("  ✅ 核心类实例化成功")
        print(f"    流水线: {type(pipeline).__name__}")
        print(f"    反向处理器: {type(reverse_processor).__name__}")
        print(f"    输入解析器: {type(input_parser).__name__}")
        print(f"    上下文生成器: {type(context_generator).__name__}")
    except Exception as e:
        print(f"  ❌ 类实例化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试方法调用
    print("4. 测试方法调用:")
    try:
        # 测试反向计分识别
        is_reversed = reverse_processor.is_reverse_item("AGENT_B5_C6")
        print(f"  ✅ 反向计分识别测试: AGENT_B5_C6 是反向题 = {is_reversed}")
        
        # 测试分数反向
        reversed_score = reverse_processor.reverse_score(1)
        print(f"  ✅ 分数反向测试: 1 → {reversed_score}")
        
        # 测试争议严重程度评估
        severity = reverse_processor.assess_dispute_severity([1, 3, 5])
        print(f"  ✅ 争议严重程度评估: [1, 3, 5] = {severity}")
        
        # 测试信度计算
        reliability = reverse_processor.calculate_trait_reliability([1, 3, 5])
        print(f"  ✅ 信度计算测试: [1, 3, 5] = {reliability}")
        
    except Exception as e:
        print(f"  ❌ 方法调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("所有模块导入测试通过!")
    print("="*60)
    return True


def main():
    """主函数"""
    success = test_module_imports()
    if success:
        print("\n🎉 模块导入测试成功!")
        print("现在可以正常使用single_report_pipeline包了!")
    else:
        print("\n❌ 模块导入测试失败!")
        print("请检查模块导入配置!")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())