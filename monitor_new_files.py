import os
import time
from datetime import datetime

def monitor_new_files():
    """监控新结果文件的生成"""
    output_dir = "cloud_evaluation_output"
    
    # 获取当前文件列表
    initial_files = set(os.listdir(output_dir))
    print(f"初始文件数量: {len(initial_files)}")
    print("开始监控新文件生成...")
    
    try:
        while True:
            current_files = set(os.listdir(output_dir))
            new_files = current_files - initial_files
            
            if new_files:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 发现新文件:")
                for file in new_files:
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"  {file} ({file_size} 字节)")
                
                initial_files = current_files
            
            time.sleep(30)  # 每30秒检查一次
            
    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == "__main__":
    monitor_new_files()