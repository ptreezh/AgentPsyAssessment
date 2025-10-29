import glob
import os

# 统计results/results目录中JSON文件的数量
files = glob.glob('results/results/*.json')
print(f'找到 {len(files)} 个JSON文件')

# 显示前10个文件名
print('\n前10个文件:')
for file in files[:10]:
    print(f'  {os.path.basename(file)}')