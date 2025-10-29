import os
import json

def find_incomplete_reports():
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

if __name__ == "__main__":
    incomplete = find_incomplete_reports()
    print(f"找到 {len(incomplete)} 个未完成分段分析的测评报告:")
    for report in incomplete:
        print(report)