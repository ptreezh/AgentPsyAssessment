#!/usr/bin/env python3
"""
优化版批量分析脚本 - 提高处理效率
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
from iflow_sdk_evaluator import IFlowSDKEvaluator, IFlowBatchProcessor


class OptimizedBatchAnalyzer:
    """优化版批量分析器"""
    
    def __init__(self, model: str = "deepseek-v3.2-exp", batch_size: int = 10):
        self.model = model
        self.batch_size = batch_size
        self.processed_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.start_time = datetime.now()
    
    def load_assessment_file(self, file_path: Path) -> Optional[List[Dict]]:
        """加载测评文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = []
            if isinstance(data, dict) and 'assessment_results' in data:
                assessment_results = data['assessment_results']
                
                for item in assessment_results:
                    if isinstance(item, dict) and 'question_data' in item and 'conversation_log' in item:
                        question_data = item['question_data']
                        conversation_log = item['conversation_log']
                        
                        question = None
                        answer = None
                        
                        for log_item in conversation_log:
                            if log_item.get('role') == 'user':
                                content = log_item.get('content', '')
                                if '[ASSESSMENT_QUESTION]' in content:
                                    question = content.replace('[ASSESSMENT_QUESTION]', '').strip()
                            elif log_item.get('role') == 'assistant':
                                answer = log_item.get('content', '')
                                if '\n\n' in answer:
                                    answer = answer.split('\n\n')[-1].strip()
                        
                        if question and answer:
                            questions.append({
                                'question': question,
                                'answer': answer,
                                'dimension': question_data.get('dimension', ''),
                                'question_id': question_data.get('question_id', '')
                            })
            
            return questions
        
        except Exception as e:
            print(f"❌ 加载文件 {file_path.name} 失败: {e}")
            return None
    
    def create_segments(self, questions: List[Dict], segment_size: int = 5) -> List[List[Dict]]:
        """将问题列表分成5题分段"""
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i + segment_size]
            if segment:
                segments.append(segment)
        return segments
    
    async def analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""
        
        self.processed_files += 1
        print(f"\n📊 [{self.processed_files}] 分析文件: {file_path.name}")
        
        # 加载数据
        questions = self.load_assessment_file(file_path)
        if not questions:
            self.failed_files += 1
            return {
                'success': False,
                'error': f'无法加载或解析文件: {file_path.name}',
                'file': str(file_path)
            }
        
        print(f"   找到 {len(questions)} 个问答对")
        
        # 创建分段
        segments = self.create_segments(questions, segment_size=5)
        print(f"   分成 {len(segments)} 个分段")
        
        # 批量处理
        try:
            processor = IFlowBatchProcessor(model=self.model)
            segment_results = await processor.batch_evaluate(segments)
            
            # 计算最终分数
            final_scores = processor.calculate_final_scores(segment_results['results'])
            
            if final_scores['success']:
                self.successful_files += 1
                scores = final_scores['big5_scores']
                score_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in scores.items()])
                print(f"   ✅ 分析成功: {score_str}")
            else:
                self.failed_files += 1
                print(f"   ❌ 分析失败: {final_scores.get('error', '未知错误')}")
            
            return {
                'success': True,
                'file': str(file_path),
                'total_questions': len(questions),
                'segments': len(segments),
                'segment_results': segment_results,
                'final_scores': final_scores,
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.failed_files += 1
            print(f"   ❌ 分析异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'file': str(file_path)
            }
    
    async def batch_analyze_files(self, results_dir: str) -> Dict[str, Any]:
        """批量分析目录下的所有文件"""
        
        results_path = Path(results_dir)
        if not results_path.exists():
            return {
                'success': False,
                'error': f'目录不存在: {results_dir}'
            }
        
        # 查找所有 JSON 文件
        json_files = list(results_path.glob("*.json"))
        if not json_files:
            return {
                'success': False,
                'error': f'在 {results_dir} 中没有找到 JSON 文件'
            }
        
        print(f"🔍 找到 {len(json_files)} 个 JSON 文件")
        print(f"🤖 使用模型: {self.model}")
        print(f"⚡ 开始批量分析...")
        
        results = {}
        for file_path in json_files:
            file_result = await self.analyze_single_file(file_path)
            results[file_path.name] = file_result
            
            # 显示进度
            if self.processed_files % 10 == 0:
                elapsed_time = (datetime.now() - self.start_time).total_seconds()
                print(f"\n📈 进度: {self.processed_files}/{len(json_files)} (成功: {self.successful_files}, 失败: {self.failed_files})")
                print(f"⏱️  已用时: {elapsed_time:.1f}秒")
        
        # 统计信息
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'success': True,
            'total_files': len(json_files),
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'processed_files': self.processed_files,
            'processing_time': elapsed_time,
            'results': results,
            'analysis_time': datetime.now().isoformat(),
            'model_used': self.model
        }
    
    def save_results(self, results: Dict[str, Any], output_file: str = None):
        """保存分析结果"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"optimized_iflow_batch_analysis_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: {output_file}")
        return output_file
    
    def print_summary(self, results: Dict[str, Any]):
        """打印分析摘要"""
        
        print("\n" + "="*60)
        print("📋 批量分析摘要")
        print("="*60)
        
        if not results.get('success', False):
            print(f"❌ 分析失败: {results.get('error', '未知错误')}")
            return
        
        total_files = results['total_files']
        successful_files = results['successful_files']
        failed_files = results['failed_files']
        processing_time = results['processing_time']
        
        print(f"📊 文件总数: {total_files}")
        print(f"✅ 成功分析: {successful_files}")
        print(f"❌ 分析失败: {failed_files}")
        print(f"🤖 使用模型: {results.get('model_used', '未知')}")
        print(f"⏱️  总用时: {processing_time:.1f}秒")
        print(f"📈 平均速度: {total_files/processing_time*60:.1f} 文件/分钟")
        
        if successful_files > 0:
            print("\n📈 成功文件的大五人格平均分:")
            
            all_scores = []
            for filename, file_result in results['results'].items():
                if file_result.get('success', False) and file_result.get('final_scores', {}).get('success', False):
                    scores = file_result['final_scores']['big5_scores']
                    all_scores.append(scores)
            
            if all_scores:
                print("\n📊 所有文件平均分:")
                avg_scores = {}
                for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    avg_score = sum(s[trait] for s in all_scores) / len(all_scores)
                    avg_scores[trait] = round(avg_score, 2)
                    print(f"     {trait:15}: {avg_scores[trait]}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='优化版 iFlow SDK 批量分析器')
    parser.add_argument('--dir', default='results/results', help='结果目录路径 (默认: results/results)')
    parser.add_argument('--model', default='deepseek-v3.2-exp', help='模型名称 (默认: deepseek-v3.2-exp)')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    print("🚀 启动优化版 iFlow SDK 批量分析")
    
    analyzer = OptimizedBatchAnalyzer(model=args.model)
    
    # 批量分析
    results = await analyzer.batch_analyze_files(args.dir)
    
    # 保存结果
    output_file = analyzer.save_results(results, args.output)
    
    # 打印摘要
    analyzer.print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())