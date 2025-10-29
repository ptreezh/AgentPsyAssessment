#!/usr/bin/env python3
import os
import json
import time
from pathlib import Path
from datetime import datetime

def monitor_progress():
    """监控云模型评估分析进度"""
    output_dir = Path("cloud_evaluation_output")
    
    if not output_dir.exists():
        print("输出目录不存在")
        return
    
    print("🔍 监控云模型评估分析进度...")
    print("按 Ctrl+C 停止监控")
    
    try:
        while True:
            # 获取最新的结果文件
            result_files = list(output_dir.glob("cloud_evaluation_results_*.json"))
            
            if not result_files:
                print("等待结果文件生成...")
                time.sleep(10)
                continue
            
            # 获取最新的结果文件
            latest_file = max(result_files, key=os.path.getctime)
            
            # 读取结果文件
            with open(latest_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # 统计处理情况
            total = len(results)
            successful = sum(1 for r in results if "model_results" in r)
            failed = total - successful
            
            # 统计各模型的成功情况
            model_stats = {}
            for result in results:
                if "model_results" in result:
                    for model_name in result["model_results"]:
                        if model_name not in model_stats:
                            model_stats[model_name] = {"success": 0, "failed": 0}
                        
                        if result["model_results"][model_name]["status"] == "success":
                            model_stats[model_name]["success"] += 1
                        else:
                            model_stats[model_name]["failed"] += 1
            
            # 显示进度
            print(f"\n📊 评估进度报告 ({datetime.now().strftime('%H:%M:%S')})")
            print(f"   总文件数: {total}")
            print(f"   成功处理: {successful}")
            print(f"   失败处理: {failed}")
            
            if model_stats:
                print("   各模型详情:")
                for model_name, stats in model_stats.items():
                    print(f"     {model_name}: 成功 {stats['success']}, 失败 {stats['failed']}")
            
            # 检查是否完成
            if successful + failed == total and successful > 0:
                print(f"\n✅ 评估完成! 请查看详细报告: {output_dir}")
                break
            
            time.sleep(30)  # 每30秒检查一次
            
    except KeyboardInterrupt:
        print("\n停止监控")

if __name__ == "__main__":
    monitor_progress()