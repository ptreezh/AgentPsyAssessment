#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产版本批量测评报告处理器
处理大量真实的测评报告文件，支持断点续跑和高性能处理
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time
import argparse
import logging

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_report_pipeline import TransparentPipeline


class ProductionBatchProcessor:
    """生产版本批量处理器"""
    
    def __init__(self, input_dir: str, output_dir: str, checkpoint_interval: int = 10):
        """
        初始化生产批处理器
        
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
        self.checkpoint_file = self.output_dir / "production_checkpoint.pkl"
        self.results_file = self.output_dir / "production_results.json"
        self.log_file = self.output_dir / "production_processing.log"
        
        # 设置日志
        self.setup_logging()
        
        # 创建流水线实例
        self.pipeline = TransparentPipeline()
        
        # 状态变量
        self.processed_files = set()
        self.results = []
        self.start_time = datetime.now()
        self.total_files = 0
        self.current_index = 0
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_checkpoint(self):
        """加载检查点"""
        if self.checkpoint_file.exists():
            try:
                import pickle
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)
                
                self.processed_files = set(checkpoint_data.get('processed_files', []))
                self.results = checkpoint_data.get('results', [])
                self.start_time = checkpoint_data.get('start_time', datetime.now())
                self.total_files = checkpoint_data.get('total_files', 0)
                self.current_index = checkpoint_data.get('current_index', 0)
                
                self.logger.info(f"已加载检查点: 处理了 {len(self.processed_files)} 个文件")
                return True
            except Exception as e:
                self.logger.warning(f"加载检查点失败: {e}")
                return False
        else:
            self.logger.info("未找到检查点文件")
            return False
    
    def save_checkpoint(self):
        """保存检查点"""
        import pickle
        checkpoint_data = {
            'processed_files': list(self.processed_files),
            'results': self.results,
            'start_time': self.start_time,
            'total_files': self.total_files,
            'current_index': self.current_index
        }
        
        try:
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            self.logger.info("检查点已保存")
            return True
        except Exception as e:
            self.logger.error(f"保存检查点失败: {e}")
            return False
    
    def save_results(self):
        """保存结果"""
        results_data = {
            'processing_info': {
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
            self.logger.info(f"结果已保存到: {self.results_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return False
    
    def find_json_files(self, pattern: str = "*.json") -> list:
        """查找JSON文件"""
        json_files = list(self.input_dir.glob(pattern))
        json_files.sort()  # 按文件名排序确保处理顺序一致
        return json_files
    
    def process_single_report(self, file_path: Path) -> dict:
        """
        处理单个测评报告
        
        Args:
            file_path: 测评报告文件路径
            
        Returns:
            处理结果
        """
        self.logger.info(f"处理: {file_path.name}")
        
        start_time = time.time()
        
        try:
            # 处理测评报告
            result = self.pipeline.process_single_report(str(file_path))
            
            processing_time = time.time() - start_time
            
            if result and result.get('success', False):
                self.logger.info(f"完成: {file_path.name}")
                self.logger.info(f"  处理时间: {processing_time:.1f}秒")
                self.logger.info(f"  大五人格: {result.get('big5_scores', {})}")
                self.logger.info(f"  MBTI类型: {result.get('mbti_type', 'Unknown')}")
                return {
                    **result,
                    'file_path': str(file_path),
                    'processing_time': round(processing_time, 1),
                    'success': True
                }
            else:
                self.logger.error(f"失败: {file_path.name}")
                error_msg = result.get('error', 'Unknown error') if result else 'No result'
                self.logger.error(f"  错误: {error_msg}")
                return {
                    'success': False,
                    'file_path': str(file_path),
                    'error': error_msg,
                    'processing_time': round(processing_time, 1)
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.exception(f"异常: {file_path.name} - {e}")
            return {
                'success': False,
                'file_path': str(file_path),
                'error': str(e),
                'processing_time': round(processing_time, 1)
            }
    
    def run_production_batch(self, pattern: str = "*.json", limit: int = None, 
                           resume: bool = True, no_save: bool = False) -> bool:
        """
        运行生产批处理
        
        Args:
            pattern: 文件匹配模式
            limit: 限制处理文件数量
            resume: 是否从检查点恢复
            no_save: 是否不保存结果（用于测试）
            
        Returns:
            是否成功完成
        """
        self.logger.info("🚀 生产版本批量处理启动")
        self.logger.info("="*80)
        self.logger.info(f"输入目录: {self.input_dir}")
        self.logger.info(f"输出目录: {self.output_dir}")
        self.logger.info(f"检查点间隔: 每 {self.checkpoint_interval} 个文件")
        self.logger.info(f"恢复模式: {'启用' if resume else '禁用'}")
        self.logger.info()
        
        # 加载检查点
        if resume:
            self.load_checkpoint()
        
        # 查找文件
        self.logger.info("📂 查找测评报告文件...")
        json_files = self.find_json_files(pattern)
        
        if not json_files:
            self.logger.error("未找到任何测评报告文件")
            return False
        
        self.total_files = len(json_files)
        if limit:
            json_files = json_files[:limit]
            self.total_files = len(json_files)
        
        self.logger.info(f"找到 {len(json_files)} 个测评报告文件")
        self.logger.info(f"已处理: {len(self.processed_files)} 个")
        self.logger.info(f"剩余: {len(json_files) - len(self.processed_files)} 个")
        self.logger.info()
        
        # 确定起始位置
        start_index = 0
        if resume and self.current_index < len(json_files):
            start_index = self.current_index
        
        self.logger.info(f"▶️  从第 {start_index + 1} 个文件开始处理")
        self.logger.info()
        
        # 处理文件
        processed_count = 0
        success_count = 0
        failed_count = 0
        
        for i, file_path in enumerate(json_files[start_index:], start_index):
            # 检查是否已处理过
            if str(file_path) in self.processed_files:
                self.logger.info(f"⏭️  跳过已处理文件: {file_path.name}")
                continue
            
            # 处理文件
            result = self.process_single_report(file_path)
            
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
            if processed_count % 100 == 0:
                self.logger.info(f"📊 进度: {processed_count} 个文件已处理 "
                               f"(成功: {success_count}, 失败: {failed_count})")
            
            # 保存检查点
            if processed_count % self.checkpoint_interval == 0 and not no_save:
                self.logger.info(f"💾 保存检查点...")
                self.save_checkpoint()
                self.save_results()
            
            # 添加延迟避免API过载
            time.sleep(0.5)
        
        # 保存最终结果
        self.logger.info(f"\n🏁 批量处理完成!")
        self.logger.info("="*80)
        self.logger.info(f"总文件数: {len(json_files)}")
        self.logger.info(f"已处理数: {processed_count}")
        self.logger.info(f"成功处理: {success_count}")
        self.logger.info(f"处理失败: {failed_count}")
        self.logger.info(f"成功率: {success_count/processed_count*100:.1f}%" if processed_count > 0 else "N/A")
        
        if not no_save:
            self.save_checkpoint()
            self.save_results()
        
        self.logger.info(f"\n✅ 结果已保存到: {self.output_dir}")
        self.logger.info(f"🔁 如需继续处理剩余文件，请重新运行此脚本")
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生产版本批量测评报告处理器 - 支持断点续跑')
    parser.add_argument('--input-dir', default=r'D:\AIDevelop\portable_psyagent\results\readonly-original',
                       help='输入目录 (默认: D:\\AIDevelop\\portable_psyagent\\results\\readonly-original)')
    parser.add_argument('--output-dir', default=r'D:\AIDevelop\portable_psyagent\results\production-batch-results',
                       help='输出目录 (默认: D:\\AIDevelop\\portable_psyagent\\results\\production-batch-results)')
    parser.add_argument('--pattern', default='*.json',
                       help='文件匹配模式 (默认: *.json)')
    parser.add_argument('--limit', type=int,
                       help='限制处理文件数量')
    parser.add_argument('--checkpoint-interval', type=int, default=10,
                       help='检查点间隔 (默认: 每10个文件)')
    parser.add_argument('--no-resume', action='store_true',
                       help='不从检查点恢复，重新开始')
    parser.add_argument('--no-save', action='store_true',
                       help='不保存结果（用于测试）')
    
    args = parser.parse_args()
    
    # 创建生产批处理器
    processor = ProductionBatchProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        checkpoint_interval=args.checkpoint_interval
    )
    
    # 运行生产批处理
    success = processor.run_production_batch(
        pattern=args.pattern,
        limit=args.limit,
        resume=not args.no_resume,
        no_save=args.no_save
    )
    
    if success:
        print("\n🎉 生产版本批量处理成功完成!")
        return 0
    else:
        print("\n❌ 生产版本批量处理失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())