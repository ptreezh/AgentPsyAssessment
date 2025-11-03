#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的批量处理脚本
支持断点续跑和进度跟踪
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import time
import pickle

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_report_pipeline import TransparentPipeline


class RealBatchProcessor:
    """真正的批量处理器 - 支持断点续跑"""
    
    def __init__(self, input_dir: str, output_dir: str, checkpoint_interval: int = 5):
        """
        初始化批量处理器
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
            checkpoint_interval: 检查点间隔
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.checkpoint_interval = checkpoint_interval
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查点文件
        self.checkpoint_file = self.output_dir / "checkpoint.pkl"
        self.results_file = self.output_dir / "batch_results.json"
        self.progress_file = self.output_dir / "progress.txt"
        
        # 创建流水线实例
        self.pipeline = TransparentPipeline()
        
        # 状态变量
        self.processed_files = set()
        self.results = []
        self.start_time = datetime.now()
        self.total_files = 0
        self.current_index = 0
    
    def load_checkpoint(self):
        """加载检查点"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'rb') as f:
                    data = pickle.load(f)
                
                self.processed_files = set(data.get('processed_files', []))
                self.results = data.get('results', [])
                self.start_time = data.get('start_time', datetime.now())
                self.total_files = data.get('total_files', 0)
                self.current_index = data.get('current_index', 0)
                
                print(f"✅ 已加载检查点: {len(self.processed_files)} 个文件已处理")
                return True
            except Exception as e:
                print(f"⚠️  加载检查点失败: {e}")
                return False
        else:
            print("ℹ️  未找到检查点文件，开始全新处理")
            return False
    
    def save_checkpoint(self):
        """保存检查点"""
        data = {
            'processed_files': list(self.processed_files),
            'results': self.results,
            'start_time': self.start_time,
            'total_files': self.total_files,
            'current_index': self.current_index
        }
        
        try:
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump(data, f)
            print("✅ 检查点已保存")
            return True
        except Exception as e:
            print(f"❌ 保存检查点失败: {e}")
            return False
    
    def save_results(self):
        """保存结果"""
        data = {
            'processing_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_files': self.total_files,
                'processed_files': len(self.processed_files),
                'duration_seconds': (datetime.now() - self.start_time).total_seconds()
            },
            'results': self.results
        }
        
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {self.results_file}")
            return True
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")
            return False
    
    def save_progress(self, message: str):
        """保存进度信息"""
        try:
            with open(self.progress_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        except Exception as e:
            print(f"⚠️  保存进度信息失败: {e}")
    
    def find_json_files(self) -> list:
        """查找JSON文件"""
        json_files = list(self.input_dir.glob("*.json"))
        json_files.sort()
        return json_files
    
    def process_single_file(self, file_path: Path) -> dict:
        """
        处理单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理结果
        """
        print(f"🔍 处理文件: {file_path.name}")
        self.save_progress(f"开始处理文件: {file_path.name}")
        
        try:
            result = self.pipeline.process_single_report(str(file_path))
            
            if result and result.get('success', False):
                print(f"  ✅ 处理完成: {file_path.name}")
                print(f"    大五人格: {result.get('big5_scores', {})}")
                print(f"    MBTI类型: {result.get('mbti_type', 'Unknown')}")
                self.save_progress(f"处理完成: {file_path.name} - 成功")
                return result
            else:
                print(f"  ❌ 处理失败: {file_path.name}")
                error_msg = result.get('error', 'Unknown error') if result else 'No result'
                print(f"    错误: {error_msg}")
                self.save_progress(f"处理完成: {file_path.name} - 失败 - {error_msg}")
                return {
                    'success': False,
                    'file_path': str(file_path),
                    'error': error_msg
                }
                
        except Exception as e:
            print(f"  💥 处理异常: {file_path.name} - {e}")
            import traceback
            traceback.print_exc()
            self.save_progress(f"处理完成: {file_path.name} - 异常 - {str(e)}")
            return {
                'success': False,
                'file_path': str(file_path),
                'error': str(e)
            }
    
    def run_batch_processing(self, limit: int = None, resume: bool = True):
        """
        运行批量处理
        
        Args:
            limit: 限制处理文件数量
            resume: 是否从检查点恢复
        """
        print("🚀 真正的批量处理脚本 - 支持断点续跑")
        print("="*80)
        print(f"输入目录: {self.input_dir}")
        print(f"输出目录: {self.output_dir}")
        print(f"检查点间隔: 每 {self.checkpoint_interval} 个文件")
        print()
        
        # 加载检查点（如果启用）
        if resume:
            self.load_checkpoint()
        
        # 查找文件
        print("📂 查找测评报告文件...")
        json_files = self.find_json_files()
        
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
        
        # 从检查点位置开始处理
        start_index = 0
        if resume and self.current_index < len(json_files):
            start_index = self.current_index
        
        print(f"▶️  从第 {start_index + 1} 个文件开始处理")
        print()
        
        # 处理文件
        processed_count = 0
        success_count = 0
        failed_count = 0
        
        for i in range(start_index, len(json_files)):
            file_path = json_files[i]
            
            # 检查是否已处理
            if str(file_path) in self.processed_files:
                print(f"⏭️  跳过已处理文件: {file_path.name}")
                continue
            
            # 处理文件
            result = self.process_single_file(file_path)
            
            # 更新状态
            self.processed_files.add(str(file_path))
            self.results.append(result)
            self.current_index = i + 1
            
            if result.get('success', False):
                success_count += 1
            else:
                failed_count += 1
            
            processed_count += 1
            
            # 显示进度
            if processed_count % 10 == 0:
                print(f"  📊 进度: {processed_count} 个文件已处理 "
                      f"(成功: {success_count}, 失败: {failed_count})")
                self.save_progress(f"进度: {processed_count} 个文件已处理 "
                                 f"(成功: {success_count}, 失败: {failed_count})")
            
            # 保存检查点
            if processed_count % self.checkpoint_interval == 0:
                print(f"  💾 保存检查点...")
                self.save_checkpoint()
                self.save_results()
                self.save_progress(f"保存检查点: 处理了 {processed_count} 个文件")
            
            # 添加延迟避免API过载
            time.sleep(1)
        
        # 保存最终结果
        print(f"\n🏁 批量处理完成!")
        print("="*80)
        print(f"总文件数: {len(json_files)}")
        print(f"已处理数: {processed_count}")
        print(f"成功处理: {success_count}")
        print(f"处理失败: {failed_count}")
        print(f"成功率: {success_count/processed_count*100:.1f}%" if processed_count > 0 else "N/A")
        
        self.save_checkpoint()
        self.save_results()
        self.save_progress(f"批量处理完成: 总文件数 {len(json_files)}, "
                         f"成功 {success_count}, 失败 {failed_count}")
        
        print(f"\n✅ 结果已保存到: {self.results_file}")
        print(f"🔁 如需继续处理剩余文件，请重新运行此脚本")
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='真正的批量处理脚本 - 支持断点续跑')
    parser.add_argument('--input-dir', default='../results/readonly-original',
                       help='输入目录 (默认: ../results/readonly-original)')
    parser.add_argument('--output-dir', default='../results/batch-processing-results',
                       help='输出目录 (默认: ../results/batch-processing-results)')
    parser.add_argument('--limit', type=int,
                       help='限制处理文件数量')
    parser.add_argument('--checkpoint-interval', type=int, default=5,
                       help='检查点间隔 (默认: 每5个文件)')
    parser.add_argument('--no-resume', action='store_true',
                       help='不从检查点恢复，重新开始')
    
    args = parser.parse_args()
    
    # 创建批量处理器
    processor = RealBatchProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        checkpoint_interval=args.checkpoint_interval
    )
    
    # 运行批量处理
    success = processor.run_batch_processing(
        limit=args.limit,
        resume=not args.no_resume
    )
    
    if success:
        print("\n🎉 批量处理成功完成!")
        return 0
    else:
        print("\n❌ 批量处理失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())