#!/usr/bin/env python3
"""
批量处理5个文件的多评估器分析
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
        
        print("=== 批量多评估器分析 (限制5个文件) ===")
        
        # 创建分析器
        input_dir = "results/results"
        output_dir = "results/multi_evaluator_5files"
        
        analyzer = ComprehensiveBatchAnalyzer(input_dir, output_dir)
        
        # 获取文件列表
        raw_files = analyzer.find_raw_reports()
        
        if not raw_files:
            print("没有找到测评报告文件")
            return
            
        # 限制为前5个文件
        files_to_process = raw_files[:5]
        print(f"将处理 {len(files_to_process)} 个文件:")
        for file in files_to_process:
            print(f"  - {file.name}")
        
        # 处理文件
        results = []
        for i, file_path in enumerate(files_to_process, 1):
            print(f"\n[{i}/{len(files_to_process)}] 处理文件: {file_path.name}")
            
            result = analyzer.process_single_file(file_path)
            results.append(result)
            
            print(f"  状态: {result['status']}")
            if result['status'] == 'completed':
                evaluator_count = len(result['final_result'].get('evaluator_results', {}))
                print(f"  评估器数量: {evaluator_count}")
            else:
                print(f"  错误: {result.get('error', '未知错误')}")
        
        # 生成汇总报告
        print("\n=== 生成汇总报告 ===")
        summary = analyzer.generate_summary_report(results)
        
        # 保存汇总报告
        summary_file = Path(output_dir) / "04_final_results" / "comprehensive_analysis_report.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        print(f"✓ 汇总报告已保存: {summary_file}")
        
        # 统计结果
        success_count = len([r for r in results if r['status'] == 'completed'])
        failed_count = len([r for r in results if r['status'] == 'failed'])
        
        print(f"\n=== 分析完成 ===")
        print(f"成功分析: {success_count}/{len(files_to_process)} 个文件")
        print(f"失败: {failed_count}/{len(files_to_process)} 个文件")
        
        # 显示评估器对比信息
        if 'cross_evaluator_analysis' in summary:
            cross_analysis = summary['cross_evaluator_analysis']
            if 'mbti_consistency' in cross_analysis:
                mbti_consistency = cross_analysis['mbti_consistency']
                print(f"MBTI一致性: {mbti_consistency.get('average_agreement_rate', 0)*100:.1f}%")
                print(f"完全一致: {mbti_consistency.get('perfect_agreement_count', 0)} 个文件")
            
            if 'score_variability' in cross_analysis:
                variability = cross_analysis['score_variability']
                print(f"平均分数变异度: {variability.get('average_variation', 0):.2f}")
                print(f"最大变异维度: {variability.get('most_variable_trait', 'N/A')}")
                
    except Exception as e:
        print(f"批量分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()