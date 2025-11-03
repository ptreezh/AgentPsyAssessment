#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量测评报告分析器 - 支持断点续跑
处理多个测评报告文件，支持中断后继续运行
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import time
import pickle
from typing import List, Dict, Any

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_report_pipeline import TransparentPipeline


class BatchReportAnalyzer:
    """批量测评报告分析器 - 支持断点续跑"""
    
    def __init__(self, input_dir: str, output_dir: str, checkpoint_interval: int = 5):
        """
        初始化批量分析器
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
            checkpoint_interval: 检查点间隔（处理多少文件后保存检查点）
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.checkpoint_interval = checkpoint_interval
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查点文件路径
        self.checkpoint_file = self.output_dir / "batch_analysis_checkpoint.pkl"
        self.results_file = self.output_dir / "batch_analysis_results.json"
        self.summary_file = self.output_dir / "batch_analysis_summary.md"
        
        # 创建流水线实例
        self.pipeline = TransparentPipeline()
        
        # 初始化状态变量
        self.processed_files = set()
        self.results = []
        self.start_time = datetime.now()
        self.total_files = 0
        self.current_file_index = 0
        
        # 加载检查点（如果存在）
        self.load_checkpoint()
    
    def load_checkpoint(self):
        """加载检查点"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)
                
                self.processed_files = set(checkpoint_data.get('processed_files', []))
                self.results = checkpoint_data.get('results', [])
                self.start_time = checkpoint_data.get('start_time', datetime.now())
                self.total_files = checkpoint_data.get('total_files', 0)
                self.current_file_index = checkpoint_data.get('current_file_index', 0)
                
                print(f"✅ 已加载检查点: 处理了 {len(self.processed_files)} 个文件")
                print(f"   当前索引: {self.current_file_index}")
                print(f"   总文件数: {self.total_files}")
                return True
                
            except Exception as e:
                print(f"⚠️  加载检查点失败: {e}")
                self.reset_state()
                return False
        else:
            print("ℹ️  未找到检查点文件，开始全新分析")
            self.reset_state()
            return False
    
    def reset_state(self):
        """重置状态"""
        self.processed_files = set()
        self.results = []
        self.start_time = datetime.now()
        self.total_files = 0
        self.current_file_index = 0
    
    def save_checkpoint(self):
        """保存检查点"""
        checkpoint_data = {
            'processed_files': list(self.processed_files),
            'results': self.results,
            'start_time': self.start_time,
            'total_files': self.total_files,
            'current_file_index': self.current_file_index
        }
        
        try:
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            print("✅ 检查点已保存")
            return True
        except Exception as e:
            print(f"❌ 保存检查点失败: {e}")
            return False
    
    def save_results(self):
        """保存结果"""
        results_data = {
            'analysis_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_files': self.total_files,
                'processed_files': len(self.processed_files),
                'remaining_files': self.total_files - len(self.processed_files),
                'duration_seconds': (datetime.now() - self.start_time).total_seconds()
            },
            'results': self.results
        }
        
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {self.results_file}")
            return True
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")
            return False
    
    def save_summary_report(self):
        """保存摘要报告"""
        if not self.results:
            return False
        
        # 计算统计信息
        total_processed = len(self.processed_files)
        total_files = self.total_files
        duration = (datetime.now() - self.start_time).total_seconds()
        
        # 计算大五人格统计
        big5_stats = {
            'openness_to_experience': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        }
        
        for result in self.results:
            if result.get('success', False):
                big5_scores = result.get('big5_scores', {})
                for trait in big5_stats:
                    if trait in big5_scores:
                        big5_stats[trait].append(big5_scores[trait])
        
        # 生成摘要报告
        summary_lines = [
            "# 批量测评报告分析摘要",
            "",
            "## 基本信息",
            f"- **开始时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **结束时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **处理时长**: {duration:.1f} 秒",
            f"- **总文件数**: {total_files}",
            f"- **已处理数**: {total_processed}",
            f"- **剩余文件**: {total_files - total_processed}",
            f"- **处理速率**: {total_processed/duration*60:.1f} 文件/分钟" if duration > 0 else "-",
            "",
            "## 大五人格统计",
        ]
        
        for trait, scores in big5_stats.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                std_dev = (sum((s - avg_score)**2 for s in scores) / len(scores))**0.5 if len(scores) > 1 else 0
                
                trait_name = {
                    'openness_to_experience': '开放性',
                    'conscientiousness': '尽责性',
                    'extraversion': '外向性',
                    'agreeableness': '宜人性',
                    'neuroticism': '神经质'
                }.get(trait, trait)
                
                summary_lines.extend([
                    f"### {trait_name}",
                    f"- **平均分**: {avg_score:.2f}",
                    f"- **最小值**: {min_score:.2f}",
                    f"- **最大值**: {max_score:.2f}",
                    f"- **标准差**: {std_dev:.2f}",
                    f"- **样本数**: {len(scores)}",
                    ""
                ])
        
        # 添加处理详情
        summary_lines.extend([
            "## 处理详情",
            "| 文件名 | 状态 | 处理时间 | 大五得分 | MBTI类型 |",
            "|-------|------|----------|---------|----------|"
        ])
        
        for result in self.results[:20]:  # 只显示前20个结果
            filename = Path(result.get('file_path', '')).name
            status = "✅ 成功" if result.get('success', False) else "❌ 失败"
            processing_time = result.get('processing_time', 0)
            big5_scores = result.get('big5_scores', {})
            mbti_type = result.get('mbti_type', 'Unknown')
            
            # 简化大五得分显示
            big5_str = ", ".join([f"{k[:1]}:{v}" for k, v in big5_scores.items()]) if big5_scores else "N/A"
            
            summary_lines.append(
                f"| {filename} | {status} | {processing_time:.1f}s | {big5_str} | {mbti_type} |"
            )
        
        if len(self.results) > 20:
            summary_lines.append(f"| ...还有 {len(self.results) - 20} 个文件... | | | | |")
        
        summary_lines.extend([
            "",
            "## 处理完成",
            f"✅ 批量分析已完成 {total_processed}/{total_files} 个文件",
            f"🔁 如需继续处理剩余文件，请重新运行此脚本"
        ])
        
        try:
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(summary_lines))
            print(f"✅ 摘要报告已保存到: {self.summary_file}")
            return True
        except Exception as e:
            print(f"❌ 保存摘要报告失败: {e}")
            return False
    
    def find_json_files(self, pattern: str = "*.json") -> List[Path]:
        """
        查找JSON文件
        
        Args:
            pattern: 文件匹配模式
            
        Returns:
            JSON文件路径列表
        """
        json_files = list(self.input_dir.glob(pattern))
        json_files.sort()  # 按文件名排序确保处理顺序一致
        return json_files
    
    def process_single_report(self, file_path: Path) -> Dict[str, Any]:
        """
        处理单个测评报告
        
        Args:
            file_path: 测评报告文件路径
            
        Returns:
            处理结果
        """
        print(f"🔍 处理: {file_path.name}")
        
        start_time = time.time()
        
        try:
            # 处理测评报告
            result = self.pipeline.process_single_report(str(file_path))
            
            processing_time = time.time() - start_time
            
            if result and result.get('success', False):
                print(f"  ✅ 完成: {file_path.name}")
                print(f"    处理时间: {processing_time:.1f}秒")
                print(f"    大五人格: {result.get('big5_scores', {})}")
                print(f"    MBTI类型: {result.get('mbti_type', 'Unknown')}")
                return {
                    **result,
                    'file_path': str(file_path),
                    'processing_time': round(processing_time, 1),
                    'success': True
                }
            else:
                print(f"  ❌ 失败: {file_path.name}")
                error_msg = result.get('error', 'Unknown error') if result else 'No result'
                print(f"    错误: {error_msg}")
                return {
                    'success': False,
                    'file_path': str(file_path),
                    'error': error_msg,
                    'processing_time': round(processing_time, 1)
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"  💥 异常: {file_path.name} - {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'file_path': str(file_path),
                'error': str(e),
                'processing_time': round(processing_time, 1)
            }
    
    def run_batch_analysis(self, pattern: str = "*.json", limit: int = None, 
                          resume: bool = True, no_save: bool = False) -> bool:
        """
        运行批量分析
        
        Args:
            pattern: 文件匹配模式
            limit: 限制处理文件数量
            resume: 是否从检查点恢复
            no_save: 是否不保存结果（用于测试）
            
        Returns:
            是否成功完成
        """
        print("🚀 批量测评报告分析器 - 断点续跑版")
        print("="*80)
        print(f"输入目录: {self.input_dir}")
        print(f"输出目录: {self.output_dir}")
        print(f"检查点间隔: 每 {self.checkpoint_interval} 个文件")
        print(f"恢复模式: {'启用' if resume else '禁用'}")
        print()
        
        # 加载检查点（如果启用）
        if resume:
            self.load_checkpoint()
        
        # 查找文件
        print("📂 查找测评报告文件...")
        json_files = self.find_json_files(pattern)
        
        if not json_files:
            print("❌ 未找到任何测评报告文件")
            return False
        
        self.total_files = len(json_files)
        if limit:
            json_files = json_files[:limit]
            self.total_files = len(json_files)
        
        print(f"  找到 {len(json_files)} 个测评报告文件")
        print(f"  已处理: {len(self.processed_files)} 个")
        print(f"  剩余: {len(json_files) - len(self.processed_files)} 个")
        print()
        
        # 确定起始位置
        start_index = 0
        if resume and self.current_file_index < len(json_files):
            start_index = self.current_file_index
        
        print(f"▶️  从第 {start_index + 1} 个文件开始处理")
        print()
        
        # 处理文件
        processed_count = 0
        success_count = 0
        failed_count = 0
        
        for i, file_path in enumerate(json_files[start_index:], start_index):
            # 检查是否已处理过
            if str(file_path) in self.processed_files:
                print(f"⏭️  跳过已处理文件: {file_path.name}")
                continue
            
            # 处理文件
            result = self.process_single_report(file_path)
            
            # 更新状态
            self.processed_files.add(str(file_path))
            self.results.append(result)
            self.current_file_index = i + 1
            
            if result.get('success', False):
                success_count += 1
            else:
                failed_count += 1
            
            processed_count += 1
            
            # 显示进度
            if processed_count % 10 == 0:
                print(f"  📊 进度: {processed_count} 个文件已处理 "
                      f"(成功: {success_count}, 失败: {failed_count})")
            
            # 保存检查点
            if processed_count % self.checkpoint_interval == 0 and not no_save:
                print(f"  💾 保存检查点...")
                self.save_checkpoint()
                self.save_results()
                self.save_summary_report()
            
            # 添加延迟避免API过载
            time.sleep(1)
        
        # 保存最终结果
        print(f"\n🏁 批量分析完成!")
        print("="*80)
        print(f"总文件数: {len(json_files)}")
        print(f"已处理数: {processed_count}")
        print(f"成功处理: {success_count}")
        print(f"处理失败: {failed_count}")
        print(f"成功率: {success_count/processed_count*100:.1f}%" if processed_count > 0 else "N/A")
        
        if not no_save:
            self.save_checkpoint()
            self.save_results()
            self.save_summary_report()
        
        print(f"\n✅ 结果已保存到: {self.output_dir}")
        print(f"🔁 如需继续处理剩余文件，请重新运行此脚本")
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量测评报告分析器 - 支持断点续跑')
    parser.add_argument('--input-dir', default='../results/readonly-original',
                       help='输入目录 (默认: ../results/readonly-original)')
    parser.add_argument('--output-dir', default='../results/batch-analysis-results',
                       help='输出目录 (默认: ../results/batch-analysis-results)')
    parser.add_argument('--pattern', default='*.json',
                       help='文件匹配模式 (默认: *.json)')
    parser.add_argument('--limit', type=int,
                       help='限制处理文件数量')
    parser.add_argument('--checkpoint-interval', type=int, default=5,
                       help='检查点间隔 (默认: 每5个文件)')
    parser.add_argument('--no-resume', action='store_true',
                       help='不从检查点恢复，重新开始')
    parser.add_argument('--no-save', action='store_true',
                       help='不保存结果（用于测试）')
    
    args = parser.parse_args()
    
    # 创建批量分析器
    analyzer = BatchReportAnalyzer(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        checkpoint_interval=args.checkpoint_interval
    )
    
    # 运行批量分析
    success = analyzer.run_batch_analysis(
        pattern=args.pattern,
        limit=args.limit,
        resume=not args.no_resume,
        no_save=args.no_save
    )
    
    if success:
        print("\n🎉 批量分析成功完成!")
        return 0
    else:
        print("\n❌ 批量分析失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())