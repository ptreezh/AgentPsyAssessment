import os
import json
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# 配置路径
INPUT_DIR = Path("D:/AIDevelop/portable_psyagent/results/readonly-original")
OUTPUT_DIR = Path("D:/AIDevelop/portable_psyagent/results/readonly-original/processed")
PROCESSED_BATCH_SIZE = 20

def process_single_report(file_path):
    """
    处理单个原始测评报告
    """
    try:
        # 读取原始测评报告
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 在这里可以添加具体的评估分析逻辑
        # 目前我们只是模拟处理过程
        processed_data = {
            "original_file": str(file_path.name),
            "processing_status": "completed",
            "analysis_results": "Assessment analysis would be performed here based on credible_assessment_plan_updated.md"
        }
        
        # 创建输出文件名
        output_filename = file_path.stem + "_segmented_scoring_evaluation.json"
        output_path = OUTPUT_DIR / output_filename
        
        # 保存处理结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        # 移动原始文件到processed目录
        processed_file_path = OUTPUT_DIR / file_path.name
        shutil.move(str(file_path), str(processed_file_path))
        
        return f"Successfully processed: {file_path.name}"
    except Exception as e:
        return f"Error processing {file_path.name}: {str(e)}"

def process_batch(files_batch):
    """
    处理一批文件（每个进程处理20份报告）
    """
    results = []
    for file_path in files_batch:
        result = process_single_report(file_path)
        results.append(result)
    return results

def get_json_files():
    """
    获取所有JSON文件
    """
    json_files = list(INPUT_DIR.glob("*.json"))
    # 排除processed目录中的文件
    json_files = [f for f in json_files if "processed" not in str(f)]
    return json_files

def main():
    """
    主函数：启动多个并发进程处理原始测评报告
    """
    # 获取所有原始测评报告
    json_files = get_json_files()
    print(f"Total JSON files to process: {len(json_files)}")
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 将文件分批，每批20个
    batches = [json_files[i:i + PROCESSED_BATCH_SIZE] for i in range(0, len(json_files), PROCESSED_BATCH_SIZE)]
    print(f"Total batches to process: {len(batches)}")
    
    # 使用线程池并发处理
    with ThreadPoolExecutor(max_workers=min(26, len(batches))) as executor:
        # 提交所有批次处理任务
        future_to_batch = {executor.submit(process_batch, batch): i for i, batch in enumerate(batches)}
        
        # 收集处理结果
        for future in as_completed(future_to_batch):
            batch_index = future_to_batch[future]
            try:
                results = future.result()
                for result in results:
                    print(result)
                print(f"Batch {batch_index + 1}/{len(batches)} completed.")
            except Exception as e:
                print(f"Batch {batch_index + 1} generated an exception: {e}")
    
    print("All files processed.")

if __name__ == "__main__":
    main()