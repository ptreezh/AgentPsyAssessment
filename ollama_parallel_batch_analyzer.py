#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama并行批量分析器
使用三个Ollama模型从后往前分析所有测评报告
5题分段（每段5题，每个测评报告分10段），三模型独立并行评估
避免与现有云模型进程冲突
"""

import sys
import os
import json
import subprocess
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import statistics
import concurrent.futures
import glob
import math

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入已经验证的TDD分析器
from ollama_tdd_5segment_analyzer import OllamaTDD5SegmentAnalyzer

class OllamaParallelBatchAnalyzer:
    def __init__(self, input_dir: str, output_dir: str, num_processes: int = 3):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.num_processes = num_processes

        # 使用已经验证的TDD分析器
        self.analyzer = OllamaTDD5SegmentAnalyzer()

        # 三个Ollama模型配置
        self.models = [
            {"name": "deepseek-v3.1:671b-cloud", "description": "DeepSeek 671B云模型"},
            {"name": "gpt-oss:120b-cloud", "description": "GPT OSS 120B云模型"},
            {"name": "qwen3-coder:480b-cloud", "description": "Qwen3 Coder 480B云模型"}
        ]

        # 处理统计
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "total_segments": 0,
            "successful_segments": 0,
            "total_processing_time": 0,
            "start_time": None,
            "files_processed_per_model": {model["name"]: 0 for model in self.models}
        }

        # 进程锁，避免冲突
        self.process_locks = {model["name"]: threading.Lock() for model in self.models}

    def get_all_files_sorted_reverse(self) -> List[str]:
        """获取所有文件，按修改时间倒序排列（从最新到最旧）"""
        file_pattern = os.path.join(self.input_dir, "*.json")
        files = glob.glob(file_pattern)

        # 按修改时间倒序排列，从最新的开始
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        print(f"📁 找到 {len(files)} 个文件（从最新开始排序）")
        return files

    def split_files_for_processes(self, files: List[str]) -> List[List[str]]:
        """将文件分配给不同进程"""
        total_files = len(files)
        batch_size = math.ceil(total_files / self.num_processes)

        batches = []
        for i in range(0, total_files, batch_size):
            batch = files[i:i + batch_size]
            batches.append(batch)

        print(f"📦 分配给 {len(batches)} 个进程:")
        for i, batch in enumerate(batches, 1):
            print(f"   进程 {i}: {len(batch)} 个文件")

        return batches

    def check_existing_results(self, output_dir: str) -> set:
        """检查已经处理过的文件"""
        if not os.path.exists(output_dir):
            return set()

        existing_files = set()
        pattern = os.path.join(output_dir, "*_ollama_tdd_5segment_analysis.json")
        for file_path in glob.glob(pattern):
            # 提取原始文件名
            original_name = Path(file_path).stem.replace("_ollama_tdd_5segment_analysis", "")
            existing_files.add(original_name)

        print(f"🔍 发现 {len(existing_files)} 个已处理的文件")
        return existing_files

    def analyze_single_file(self, file_path: str, process_id: int) -> Dict:
        """分析单个文件"""
        start_time = time.time()
        file_name = Path(file_path).name

        print(f"🔄 [进程{process_id}] 开始分析: {file_name}")

        try:
            # 创建进程特定的输出目录
            process_output_dir = os.path.join(self.output_dir, f"process_{process_id}")
            os.makedirs(process_output_dir, exist_ok=True)

            # 使用TDD分析器分析文件
            result = self.analyzer.analyze_file_with_three_models(file_path, process_output_dir)

            processing_time = time.time() - start_time

            if result['success']:
                print(f"   ✅ [进程{process_id}] {file_name} - 成功 (用时{processing_time:.1f}s)")
                print(f"      一致性: {result['consistency_analysis'].get('consensus_mbti', 'UNKNOWN')}")

                return {
                    'success': True,
                    'file_path': file_path,
                    'output_path': result['output_path'],
                    'processing_time': processing_time,
                    'consistency_analysis': result['consistency_analysis'],
                    'process_id': process_id
                }
            else:
                print(f"   ❌ [进程{process_id}] {file_name} - 失败: {result.get('error', 'Unknown error')}")

                return {
                    'success': False,
                    'file_path': file_path,
                    'error': result.get('error', 'Unknown error'),
                    'processing_time': processing_time,
                    'process_id': process_id
                }

        except Exception as e:
            print(f"   ⚠️ [进程{process_id}] {file_name} - 异常: {str(e)}")

            return {
                'success': False,
                'file_path': file_path,
                'error': f"处理异常: {str(e)}",
                'processing_time': time.time() - start_time,
                'process_id': process_id
            }

    def process_batch_files(self, batch_files: List[str], process_id: int) -> List[Dict]:
        """处理一批文件"""
        results = []

        print(f"🚀 [进程{process_id}] 开始处理 {len(batch_files)} 个文件")

        for i, file_path in enumerate(batch_files, 1):
            result = self.analyze_single_file(file_path, process_id)
            results.append(result)

            # 更新统计
            with self.stats_lock:
                self.stats["processed_files"] += 1
                if result['success']:
                    self.stats["successful_segments"] += 1
                else:
                    self.stats["failed_files"] += 1

        print(f"✅ [进程{process_id}] 完成处理，成功率: {sum(1 for r in results if r['success']) / len(results):.1%}")
        return results

    def generate_progress_report(self) -> Dict:
        """生成进度报告"""
        current_time = datetime.now()
        elapsed_time = (current_time - self.stats["start_time"]).total_seconds() if self.stats["start_time"] else 0

        # 计算预估完成时间
        if self.stats["processed_files"] > 0:
            avg_time_per_file = elapsed_time / self.stats["processed_files"]
            remaining_files = self.stats["total_files"] - self.stats["processed_files"]
            estimated_remaining_time = remaining_files * avg_time_per_file / self.num_processes
            estimated_completion = current_time + timedelta(seconds=estimated_remaining_time)
        else:
            estimated_remaining_time = 0
            estimated_completion = current_time

        return {
            "timestamp": current_time.isoformat(),
            "progress": {
                "total_files": self.stats["total_files"],
                "processed_files": self.stats["processed_files"],
                "failed_files": self.stats["failed_files"],
                "success_rate": self.stats["processed_files"] / self.stats["total_files"] if self.stats["total_files"] > 0 else 0,
                "completion_percentage": (self.stats["processed_files"] / self.stats["total_files"]) * 100 if self.stats["total_files"] > 0 else 0
            },
            "performance": {
                "elapsed_time": elapsed_time,
                "avg_time_per_file": elapsed_time / self.stats["processed_files"] if self.stats["processed_files"] > 0 else 0,
                "files_per_hour": (self.stats["processed_files"] / elapsed_time * 3600) if elapsed_time > 0 else 0,
                "estimated_remaining_time": estimated_remaining_time,
                "estimated_completion_time": estimated_completion.isoformat()
            },
            "model_stats": self.stats["files_processed_per_model"]
        }

    def run_parallel_analysis(self):
        """运行并行分析"""
        print("🚀 启动Ollama并行批量分析器")
        print("=" * 60)
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🔧 并行进程数: {self.num_processes}")
        print(f"🌐 Ollama模型: {', '.join([m['name'] for m in self.models])}")
        print(f"📊 分析方式: 5题分段（每段5题，10段/文件）")
        print(f"🔄 处理顺序: 从最新到最旧")
        print()

        # 初始化统计
        self.stats["start_time"] = datetime.now()

        # 获取所有文件
        all_files = self.get_all_files_sorted_reverse()
        self.stats["total_files"] = len(all_files)

        if not all_files:
            print("❌ 未找到需要处理的文件")
            return

        # 检查已处理的文件
        existing_files = self.check_existing_results(self.output_dir)

        # 过滤未处理的文件
        unprocessed_files = []
        for file_path in all_files:
            file_name = Path(file_path).stem
            if file_name not in existing_files:
                unprocessed_files.append(file_path)

        print(f"📋 待处理文件: {len(unprocessed_files)} (跳过已处理的 {len(existing_files)} 个文件)")

        if not unprocessed_files:
            print("✅ 所有文件都已处理完成")
            return

        # 分配文件给不同进程
        file_batches = self.split_files_for_processes(unprocessed_files)

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"\n🚀 启动 {len(file_batches)} 个并行进程...")
        print("=" * 60)

        # 使用线程池并行处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_processes) as executor:
            # 提交所有批次的处理任务
            future_to_batch = {}

            for i, batch_files in enumerate(file_batches, 1):
                print(f"🌐 提交进程 {i} 的任务 ({len(batch_files)} 个文件)")
                future = executor.submit(self.process_batch_files, batch_files, i)
                future_to_batch[future] = i

            # 收集结果
            all_results = []
            completed_batches = 0

            for future in concurrent.futures.as_completed(future_to_batch):
                batch_id = future_to_batch[future]
                completed_batches += 1

                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)

                    print(f"✅ 进程 {batch_id} 完成 (第 {completed_batches}/{len(file_batches)} 个进程)")

                    # 生成进度报告
                    progress_report = self.generate_progress_report()
                    print(f"📊 进度: {progress_report['progress']['completion_percentage']:.1f}% ({progress_report['progress']['processed_files']}/{progress_report['progress']['total_files']} 文件)")
                    print(f"⏱️ 处理速度: {progress_report['performance']['files_per_hour']:.1f} 文件/小时")
                    print(f"⏰ 预计剩余时间: {timedelta(seconds=int(progress_report['performance']['estimated_remaining_time']))")

                    # 保存进度报告
                    progress_file = os.path.join(self.output_dir, "progress_report.json")
                    with open(progress_file, 'w', encoding='utf-8') as f:
                        json.dump(progress_report, f, ensure_ascii=False, indent=2)

                except Exception as e:
                    print(f"❌ 进程 {batch_id} 失败: {e}")

        # 最终统计
        final_stats = self.generate_progress_report()

        print("\n" + "=" * 60)
        print("🎉 Ollama并行批量分析完成!")
        print("=" * 60)

        print(f"📊 最终统计:")
        print(f"   总文件数: {final_stats['progress']['total_files']}")
        print(f"   成功处理: {final_stats['progress']['processed_files']}")
        print(f"   处理失败: {final_stats['progress']['failed_files']}")
        print(f"   成功率: {final_stats['progress']['success_rate']:.1%}")
        print(f"   总耗时: {timedelta(seconds=int(final_stats['performance']['elapsed_time']))}")
        print(f"   平均速度: {final_stats['performance']['files_per_hour']:.1f} 文件/小时")

        # 生成最终报告
        final_report = {
            "analysis_summary": {
                "completion_time": datetime.now().isoformat(),
                "input_directory": self.input_dir,
                "output_directory": self.output_dir,
                "models_used": [{"name": m["name"], "description": m["description"]} for m in self.models],
                "analysis_method": "5题分段，三模型并行",
                "processing_order": "从最新到最旧",
                "progress_stats": final_stats,
                "all_results": all_results
            }
        }

        # 保存最终报告
        final_report_file = os.path.join(self.output_dir, "final_batch_analysis_report.json")
        with open(final_report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)

        print(f"💾 最终报告已保存: {final_report_file}")

        # 统计一致性结果
        successful_results = [r for r in all_results if r['success']]
        if successful_results:
            consensus_types = {}
            for result in successful_results:
                mbti_type = result.get('consistency_analysis', {}).get('consensus_mbti', 'UNKNOWN')
                if mbti_type != 'UNKNOWN':
                    consensus_types[mbti_type] = consensus_types.get(mbti_type, 0) + 1

            if consensus_types:
                print(f"\n🎯 MBTI类型分布:")
                for mbti_type, count in sorted(consensus_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {mbti_type}: {count} 个文件")

        return final_report

def main():
    """主函数"""
    print("🚀 Ollama并行批量分析器")
    print("使用三个Ollama模型从后往前分析所有测评报告")
    print("5题分段，三模型并行，避免与现有云模型进程冲突")
    print("=" * 80)

    # 检查输入目录
    input_dir = "results/results"
    if not os.path.exists(input_dir):
        print(f"❌ 输入目录不存在: {input_dir}")
        return

    # 创建输出目录
    output_dir = "ollama_parallel_batch_results"

    # 创建分析器
    analyzer = OllamaParallelBatchAnalyzer(
        input_dir=input_dir,
        output_dir=output_dir,
        num_processes=3  # 三个并行进程，对应三个模型
    )

    # 运行并行分析
    try:
        analyzer.run_parallel_analysis()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断分析")
        print(f"📊 当前进度: {len([f for f in glob.glob(os.path.join(output_dir, '*')) if f.endswith('.json')])} 个结果文件")
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")

    print("\n✅ Ollama并行批量分析器运行完成")

if __name__ == "__main__":
    main()