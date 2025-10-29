import json

# 统计结果文件中处理的文件数量
with open('cloud_evaluation_output/cloud_evaluation_results_20251010_193938.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'处理了 {len(data)} 个文件')

# 统计成功和失败的数量
successful = 0
failed = 0
for item in data:
    if "model_results" in item:
        for model_name in item["model_results"]:
            if item["model_results"][model_name]["status"] == "success":
                successful += 1
            else:
                failed += 1

print(f'成功处理: {successful}')
print(f'失败处理: {failed}')