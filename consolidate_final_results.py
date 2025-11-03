import os
import json
import shutil
from pathlib import Path
from collections import defaultdict
import re
from datetime import datetime

def consolidate_final_results():
    # 源目录和目标目录
    source_dir = Path('D:/AIDevelop/portable_psyagent/results/ok/evaluated')
    dest_dir = Path('D:/AIDevelop/portable_psyagent/final_evaluated_results')
    
    # 创建目标目录
    dest_dir.mkdir(exist_ok=True)
    
    # 按原始文件名分组所有评估文件
    file_groups = defaultdict(list)
    
    for file in source_dir.glob('*_segmented_scoring_evaluation*.json'):
        # 提取原始文件名部分（不包含评估后缀和时间戳）
        # 匹配两种模式：
        # 1. 基础模式: filename_segmented_scoring_evaluation.json
        # 2. 时间戳模式: filename_segmented_scoring_evaluation_YYYYMMDD_HHMMSS.json
        # 3. 重复模式: filename_segmented_scoring_evaluation_segmented_scoring_evaluation.json
        name_part = re.sub(r'_segmented_scoring_evaluation(?:_\d{8}_\d{6}|_segmented_scoring_evaluation)?\.json$', '', file.name)
        file_groups[name_part].append(file)
    
    print(f'识别到 {len(file_groups)} 组不同的原始文件')
    
    # 为每组选择最合适的评估文件作为最终结果
    final_files = []
    for original_name, files in file_groups.items():
        if len(files) == 1:
            # 只有一个评估文件，直接选择
            final_file = files[0]
        else:
            # 有多个评估文件，根据修改时间选择最新的
            # 优先选择文件名中没有时间戳的（表示最新完成的评估）
            non_timestamp_files = []
            timestamp_files = []
            
            for f in files:
                if re.search(r'_\d{8}_\d{6}\.json$', f.name):
                    timestamp_files.append(f)
                else:
                    non_timestamp_files.append(f)
            
            # 如果有非时间戳文件，选择最新的那个
            if non_timestamp_files:
                final_file = max(non_timestamp_files, key=lambda f: f.stat().st_mtime)
            else:
                # 否则从时间戳文件中选择最新的
                final_file = max(timestamp_files, key=lambda f: f.stat().st_mtime)
        
        final_files.append(final_file)
        
        # 复制到最终结果目录
        dest_path = dest_dir / final_file.name
        shutil.copy2(final_file, dest_path)
        print(f'已复制: {final_file.name} -> {dest_path.name}')
    
    print(f'已将 {len(final_files)} 个最终评估结果文件复制到 {dest_dir}')
    
    # 生成汇总报告
    summary = {
        'total_original_files': len(file_groups),
        'final_evaluated_files': len(final_files),
        'source_directory': str(source_dir),
        'destination_directory': str(dest_dir),
        'processing_date': datetime.now().isoformat(),
        'files_copied': [
            {
                'original_name': re.sub(r'_segmented_scoring_evaluation(?:_\d{8}_\d{6}|_segmented_scoring_evaluation)?\.json$', '', f.name),
                'file_name': f.name,
                'size': f.stat().st_size,
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            } 
            for f in final_files
        ]
    }
    
    summary_path = dest_dir / 'final_evaluation_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f'汇总报告已保存到: {summary_path}')
    
    return summary

if __name__ == "__main__":
    result = consolidate_final_results()
    print(f'\n处理完成！')
    print(f'总共处理了 {result["final_evaluated_files"]} 个最终评估文件')
    print(f'结果保存在: {result["destination_directory"]}')