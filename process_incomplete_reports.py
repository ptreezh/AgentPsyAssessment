import os
import json
import time
import subprocess
import sys

def find_incomplete_reports():
    """查找所有未完成分段分析的测评报告"""
    results_dir = r"D:\AIDevelop\portable_psyagent\results\results"
    incomplete_reports = []
    
    # 遍历results目录下的所有json文件
    for filename in os.listdir(results_dir):
        if filename.endswith('.json') and '_segmented_analysis' not in filename:
            # 检查是否存在对应的分段分析文件
            segmented_filename = filename.replace('.json', '_segmented_analysis.json')
            segmented_filepath = os.path.join(results_dir, segmented_filename)
            
            # 如果分段分析文件不存在，则将该报告标记为未完成
            if not os.path.exists(segmented_filepath):
                incomplete_reports.append(filename)
    
    return incomplete_reports

def run_segmented_analysis(report_filename):
    """运行五题分段评估分析"""
    try:
        # 构建命令
        cmd = [
            "python", 
            "segmented_analysis.py", 
            f"D:\\AIDevelop\\portable_psyagent\\results\\results\\{report_filename}"
        ]
        
        print(f"正在处理: {report_filename}")
        print(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5分钟超时
        
        if result.returncode == 0:
            print(f"成功完成: {report_filename}")
            return True
        else:
            print(f"处理失败: {report_filename}")
            print(f"错误信息: {result.stderr}")
            # 检查是否是由于模型调用失败导致的错误
            if "评估器调用失败" in result.stderr or "评估器不可用" in result.stderr:
                print(f"模型调用失败，不生成虚假评估结果: {report_filename}")
                # 删除可能生成的不完整分段分析文件
                segmented_file = report_filename.replace('.json', '_segmented_analysis.json')
                segmented_path = f"D:\\AIDevelop\\portable_psyagent\\results\\results\\{segmented_file}"
                if os.path.exists(segmented_path):
                    os.remove(segmented_path)
                    print(f"删除不完整的分段分析文件: {segmented_file}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"处理超时: {report_filename}")
        return False
    except Exception as e:
        print(f"处理出错: {report_filename}, 错误: {str(e)}")
        return False

def process_all_incomplete_reports():
    """处理所有未完成的测评报告"""
    incomplete_reports = find_incomplete_reports()
    print(f"找到 {len(incomplete_reports)} 个未完成分段分析的测评报告")
    
    success_count = 0
    fail_count = 0
    
    for i, report in enumerate(incomplete_reports, 1):
        print(f"\n[{i}/{len(incomplete_reports)}] 处理进度")
        
        # 重试机制
        retry_count = 0
        max_retries = 3
        success = False
        
        while retry_count < max_retries and not success:
            if retry_count > 0:
                print(f"重试第 {retry_count} 次: {report}")
                time.sleep(5)  # 等待5秒后重试
            
            success = run_segmented_analysis(report)
            retry_count += 1
            
            if success:
                success_count += 1
            elif retry_count < max_retries:
                print(f"第 {retry_count} 次尝试失败，准备重试...")
        
        if not success:
            fail_count += 1
            print(f"处理失败 (已重试 {max_retries} 次): {report}")
        
        # 每处理10个文件休息一下，避免过于频繁的请求
        if i % 10 == 0:
            print(f"已处理 {i} 个文件，休息5秒...")
            time.sleep(5)
    
    print(f"\n处理完成!")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")

if __name__ == "__main__":
    process_all_incomplete_reports()