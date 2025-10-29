#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控批量分析 - 无缓冲输出
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def monitor_progress():
    print("🔍 实时监控批量分析进度...")

    try:
        # 检查进度文件
        progress_file = Path("batch_four_model_progress.json")
        if not progress_file.exists():
            print("❌ 进度文件不存在")
            return

        # 检查结果目录
        results_dir = Path("four_model_results/multi_model_results")
        if not results_dir.exists():
            print("❌ 结果目录不存在")
            return

        print(f"📊 开始实时监控...")
        print(f"⏰ 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 实时监控循环
        last_processed = 0
        start_time = datetime.now()

        while True:
            try:
                # 读取进度文件
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)

                current_processed = progress_data.get('total_processed', 0)
                completed_files = progress_data.get('completed_files', [])
                failed_files = progress_data.get('failed_files', [])

                # 检查是否有新进展
                if current_processed > last_processed:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed > 0:
                        rate = current_processed / (elapsed / 60)  # 文件/分钟
                        eta_files = 550 - current_processed
                        eta_minutes = eta_files / rate if rate > 0 else float('inf')
                        eta_hours = eta_minutes / 60

                    print(f"\n📈 [{datetime.now().strftime('%H:%M:%S')}] 进度更新:")
                    print(f"   已完成: {current_processed}/550 ({current_processed/550*100:.1f}%)")
                    print(f"   成功文件: {len(completed_files)}")
                    print(f"   失败文件: {len(failed_files)}")
                    print(f"   处理速度: {rate:.2f} 文件/分钟")
                    print(f"   预计剩余: {eta_minutes:.1f}分钟 ({eta_hours:.1f}小时)")

                    # 检查最新结果
                    if completed_files:
                        latest_file = completed_files[-1]
                        print(f"   最新完成: {Path(latest_file).name}")

                    last_processed = current_processed

                # 检查结果目录中的文件数量
                try:
                    all_files = []
                    for model_dir in results_dir.iterdir():
                        if model_dir.is_dir():
                            model_files = list(model_dir.glob("*summary.json"))
                            all_files.extend(model_files)

                    print(f"   📁 结果文件总数: {len(all_files)}")

                    # 如果文件数量增加，显示详细信息
                    if len(all_files) > last_processed * 3:  # 每个文件3个模型
                        print(f"   ✅ 检测到新结果文件")

                except:
                    pass

                # 等待5秒
                import time
                time.sleep(5)

            except KeyboardInterrupt:
                print(f"\n👋 监控已停止")
                break
            except Exception as e:
                print(f"❌ 监控错误: {e}")
                time.sleep(5)

    except Exception as e:
        print(f"💥 监控失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    monitor_progress()