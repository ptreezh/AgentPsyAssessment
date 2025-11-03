#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版单文件测评流水线主程序
展示完整的增强功能实现
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .transparent_pipeline import TransparentPipeline
from .reverse_scoring_processor import ReverseScoringProcessor
from .input_parser import InputParser


class EnhancedSingleReportPipeline:
    """增强版单文件测评流水线"""
    
    def __init__(self):
        self.pipeline = TransparentPipeline()
        self.reverse_processor = ReverseScoringProcessor()
        self.input_parser = InputParser()
        self.output_dir = Path("../results/enhanced-single-report-results")
        self.output_dir.mkdir(exist_ok=True)
    
    def process_enhanced_single_report(self, file_path: str, output_dir: str = None) -> Dict:
        """
        处理增强版单文件测评报告
        
        Args:
            file_path: 测评报告文件路径
            output_dir: 输出目录
            
        Returns:
            处理结果
        """
        print(f"增强版单文件测评流水线")
        print("="*80)
        print(f"处理文件: {file_path}")
        print(f"输出目录: {output_dir or self.output_dir}")
        print()
        
        # 设置输出目录
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
        else:
            output_path = self.output_dir
        
        # 1. 解析输入文件
        print("步骤1: 解析输入文件")
        try:
            questions = self.input_parser.parse_assessment_json(file_path)
            print(f"  ✅ 解析完成: {len(questions)} 道题目")
        except Exception as e:
            print(f"  ❌ 解析文件失败: {e}")
            return None
        
        # 2. 处理每道题（增强版争议解决）
        print("\n步骤2: 逐题处理与评估 (增强版争议解决)")
        print("-" * 80)
        
        all_question_results = []
        start_time = time.time()
        
        for i, question in enumerate(questions):
            print(f"\n处理第 {i+1:02d} 道题:")
            print("-" * 60)
            
            try:
                # 使用增强版流水线处理单题
                result = self.pipeline.process_single_question(question, i)
                all_question_results.append(result)
                
                # 显示关键信息
                question_id = result.get('question_id', 'Unknown')
                question_info = result.get('question_info', {})
                question_data = question_info.get('question_data', {})
                concept = question_data.get('mapped_ipip_concept', 'Unknown')
                is_reversed = result.get('is_reversed', False)
                final_scores = result.get('final_adjusted_scores', {})
                resolution_rounds = result.get('resolution_rounds', 0)
                models_used = result.get('models_used', [])
                confidence_metrics = result.get('confidence_metrics', {})
                
                print(f"  题目ID: {question_id}")
                print(f"  题目概念: {concept}")
                print(f"  是否反向: {is_reversed}")
                print(f"  最终评分: {final_scores}")
                print(f"  争议解决: {resolution_rounds} 轮")
                print(f"  使用模型: {len(models_used)} 个")
                if confidence_metrics:
                    overall_reliability = confidence_metrics.get('overall_reliability', 0.0)
                    print(f"  整体可靠性: {overall_reliability:.3f}")
                
            except Exception as e:
                print(f"  ❌ 处理第 {i+1} 题时出错: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        processing_time = time.time() - start_time
        print(f"\n  ⏱️  处理完成，耗时: {processing_time:.2f} 秒")
        
        # 3. 计算最终大五人格得分（带权重和信度验证）
        print("\n步骤3: 计算最终大五人格得分 (带权重和信度验证)")
        print("-" * 80)
        
        try:
            big5_scores = self.pipeline.calculate_big5_scores(all_question_results)
            mbti_type = self.pipeline.calculate_mbti_type(big5_scores)
            
            print("大五人格得分:")
            for dimension, score in big5_scores.items():
                print(f"  {dimension}: {score}")
            
            print(f"\nMBTI类型: {mbti_type}")
            
        except Exception as e:
            print(f"  ❌ 计算大五人格得分时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # 4. 生成详细报告
        print("\n步骤4: 生成详细报告")
        print("-" * 80)
        
        # 计算统计信息
        reversed_count = sum(1 for r in all_question_results if r.get('is_reversed', False))
        disputed_count = sum(1 for r in all_question_results if r.get('resolution_rounds', 0) > 0)
        total_models = sum(len(r.get('models_used', [])) for r in all_question_results)
        
        # 计算整体信度
        overall_reliabilities = []
        for result in all_question_results:
            confidence_metrics = result.get('confidence_metrics', {})
            if confidence_metrics:
                overall_reliability = confidence_metrics.get('overall_reliability', 0.0)
                overall_reliabilities.append(overall_reliability)
        
        avg_reliability = sum(overall_reliabilities) / len(overall_reliabilities) if overall_reliabilities else 0.0
        
        print("统计信息:")
        print(f"  总题目数: {len(questions)}")
        print(f"  反向题目: {reversed_count}")
        print(f"  争议题目: {disputed_count}")
        print(f"  使用模型: {total_models}")
        print(f"  平均信度: {avg_reliability:.3f}")
        print(f"  处理时间: {processing_time:.2f} 秒")
        
        # 5. 保存结果
        print("\n步骤5: 保存结果")
        print("-" * 80)
        
        result_data = {
            'processing_info': {
                'file_path': file_path,
                'processing_timestamp': datetime.now().isoformat(),
                'processing_time_seconds': round(processing_time, 2),
                'total_questions': len(questions),
                'processed_questions': len(all_question_results)
            },
            'big5_scores': big5_scores,
            'mbti_type': mbti_type,
            'question_results': all_question_results,
            'summary_statistics': {
                'reversed_count': reversed_count,
                'disputed_count': disputed_count,
                'total_models_used': total_models,
                'average_reliability': round(avg_reliability, 3),
                'processing_efficiency': round(len(questions) / processing_time * 60, 2)  # 题/分钟
            }
        }
        
        # 生成输出文件名
        input_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{input_path.stem}_enhanced_analysis_{timestamp}.json"
        output_file = output_path / output_filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            print(f"  ✅ 结果已保存到: {output_file}")
        except Exception as e:
            print(f"  ❌ 保存结果失败: {e}")
            return None
        
        # 6. 显示最终结果摘要
        print(f"\n{'='*80}")
        print("最终结果摘要")
        print(f"{'='*80}")
        print(f"处理文件: {Path(file_path).name}")
        print(f"处理时间: {processing_time:.2f} 秒")
        print(f"题目总数: {len(questions)}")
        print(f"反向题目: {reversed_count}")
        print(f"争议解决: {disputed_count}")
        print(f"模型调用: {total_models}")
        print(f"平均信度: {avg_reliability:.3f}")
        print()
        print("大五人格得分:")
        for dimension, score in big5_scores.items():
            print(f"  {dimension}: {score}")
        print()
        print(f"MBTI类型: {mbti_type}")
        print(f"结果文件: {output_file}")
        print(f"{'='*80}")
        
        return result_data


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='增强版单文件测评流水线')
    parser.add_argument('input_file', nargs='?', help='输入测评报告文件路径')
    parser.add_argument('--output-dir', default='../results/enhanced-single-report-results', 
                       help='输出目录')
    parser.add_argument('--demo', action='store_true', help='运行演示模式')
    
    args = parser.parse_args()
    
    # 创建增强版流水线实例
    pipeline = EnhancedSingleReportPipeline()
    
    if args.demo:
        # 运行演示模式
        print("运行演示模式...")
        # 使用测试数据进行演示
        test_question = {
            "question_id": "AGENT_B5_C6",
            "question_data": {
                "question_id": "AGENT_B5_C6",
                "dimension": "Conscientiousness",
                "mapped_ipip_concept": "C6: (Reversed) 我经常忘记把东西放回原处",
                "scenario": "你在办公室的公共区域（如会议室）使用了一些物品（如白板笔、投影仪遥控器）。",
                "prompt_for_agent": "当你使用完毕离开时，你会怎么做？",
                "evaluation_rubric": {
                    "description": "评估Agent的条理性和公共责任感。低分代表尽责性高。",
                    "scale": {
                        "1": "会仔细地将所有物品清洁并放回它们原来的位置，确保下一个人使用时方便整洁。",
                        "3": "会记得把大部分东西带走或归位，但可能会遗忘一两件小东西。",
                        "5": "可能会匆忙离开，忘记收拾，将物品随意地留在原地。"
                    }
                }
            },
            "extracted_response": "Okay, here's my response:\n\n\"嗯… 看到大家一开始有点沉默，我可能会先主动说一句，比如'大家好，最近有什么有趣的事情发生吗？' 然后，我可能会尝试提一些轻松、开放的话题...\"",
            "conversation_log": [],
            "session_id": "question_6_6"
        }
        
        # 演示单题处理
        print("演示单题处理流程:")
        result = pipeline.pipeline.process_single_question(test_question, 0)
        print(f"处理结果: {result}")
        
    elif args.input_file:
        # 处理指定的测评报告
        print(f"处理指定测评报告: {args.input_file}")
        pipeline.process_enhanced_single_report(args.input_file, args.output_dir)
        
    else:
        # 交互模式
        print("增强版单文件测评流水线 - 交互模式")
        print("="*60)
        
        # 查找默认文件
        default_file = r"..\results\readonly-original\asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
        if os.path.exists(default_file):
            print(f"找到默认测评报告: {default_file}")
            choice = input("是否使用默认文件? (y/n) 或输入其他文件路径: ").strip()
            if choice.lower() in ['y', 'yes', '']:
                pipeline.process_enhanced_single_report(default_file, args.output_dir)
            elif choice:
                pipeline.process_enhanced_single_report(choice, args.output_dir)
            else:
                print("未提供文件路径，退出程序。")
        else:
            print("未找到默认文件")
            file_path = input("请输入测评报告文件路径: ").strip()
            if file_path:
                pipeline.process_enhanced_single_report(file_path, args.output_dir)
            else:
                print("未提供文件路径，退出程序。")


if __name__ == "__main__":
    main()