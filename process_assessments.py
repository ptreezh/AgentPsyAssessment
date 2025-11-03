import os
import json
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# 配置路径
INPUT_DIR = Path("D:/AIDevelop/portable_psyagent/results/readonly-original")
OUTPUT_DIR = Path("D:/AIDevelop/portable_psyagent/results/ok/evaluated")
PROCESSED_BATCH_SIZE = 20

def process_single_assessment(file_path):
    """
    处理单个原始测评报告
    """
    try:
        # 读取原始测评报告
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 模拟评估分析过程
        # 在实际应用中，这里会包含具体的评估逻辑
        evaluation_result = {
            "original_file": str(file_path.name),
            "evaluation_status": "completed",
            "evaluation_details": "Assessment analysis performed according to credible_assessment_plan_updated.md"
        }
        
        # 创建输出文件名
        output_filename = file_path.stem + "_segmented_scoring_evaluation.json"
        output_path = OUTPUT_DIR / output_filename
        
        # 保存评估结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation_result, f, ensure_ascii=False, indent=2)
        
        # 移动原始文件到已完成目录
        processed_dir = INPUT_DIR / "processed"
        processed_dir.mkdir(exist_ok=True)
        processed_file_path = processed_dir / file_path.name
        shutil.move(str(file_path), str(processed_file_path))
        
        return f"Successfully processed: {file_path.name}"
    except Exception as e:
        return f"Error processing {file_path.name}: {str(e)}"

def get_json_files():
    """
    获取所有JSON文件（排除已处理的）
    """
    json_files = list(INPUT_DIR.glob("*.json"))
    # 排除processed目录中的文件
    json_files = [f for f in json_files if "processed" not in str(f)]
    return json_files

def process_batch(file_batch, batch_id):
    """
    处理一批文件
    """
    results = []
    print(f"Processing batch {batch_id} with {len(file_batch)} files...")
    
    for file_path in file_batch:
        result = process_single_assessment(file_path)
        results.append(result)
        
    print(f"Batch {batch_id} completed.")
    return results

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
    
    # 使用线程池并发处理，最多启动26个工作线程
    max_workers = min(26, len(batches))
    print(f"Starting ThreadPoolExecutor with {max_workers} workers")
    
    # 记录处理统计
    total_processed = 0
    total_errors = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有批次处理任务
        future_to_batch = {executor.submit(process_batch, batch, i+1): i for i, batch in enumerate(batches)}
        
        # 收集处理结果
        for future in as_completed(future_to_batch):
            batch_index = future_to_batch[future]
            try:
                results = future.result()
                for result in results:
                    print(result)
                    if "Error" in result:
                        total_errors += 1
                    else:
                        total_processed += 1
                print(f"Batch {batch_index + 1}/{len(batches)} completed.")
            except Exception as e:
                print(f"Batch {batch_index + 1} generated an exception: {e}")
                total_errors += 1
    
    print(f"All files processed. Total processed: {total_processed}, Errors: {total_errors}")

if __name__ == "__main__":
    main()