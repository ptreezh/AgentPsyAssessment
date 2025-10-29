#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行5题分段批量分析
"""

import sys
import os
import json
import time
import glob
from pathlib import Path
from datetime import datetime

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-ded837735b3c44599a9bc138da561c27'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def analyze_single_file(file_path: str, output_dir: str):
    """分析单个文件"""
    try:
        print(f"\n📈 处理文件: {Path(file_path).name}")

        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取问题
        questions = []
        if 'assessment_results' in data and isinstance(data['assessment_results'], list):
            for item in data['assessment_results']:
                if isinstance(item, dict) and 'question_data' in item:
                    question_data = item['question_data']
                    if isinstance(question_data, dict):
                        question_text = question_data.get('prompt_for_agent', '')
                        answer_text = ''
                        if 'extracted_response' in item and item['extracted_response']:
                            answer_text = item['extracted_response']

                        if question_text and answer_text:
                            questions.append({
                                'question': question_text,
                                'answer': answer_text
                            })

        if len(questions) < 5:
            print(f"  ❌ 问题数量不足：{len(questions)}")
            return False

        print(f"  📊 提取了 {len(questions)} 个问题")

        # 分段处理
        segment_size = 5
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i+segment_size]
            if len(segment) == segment_size:
                segments.append(segment)

        total_segments = len(segments)
        print(f"  📊 分成 {total_segments} 个5题分段")

        # 分析每个分段
        import openai
        client = openai.OpenAI(
            api_key=os.getenv('DASHSCOPE_API_KEY'),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        segment_results = []
        for i, segment in enumerate(segments[:2], 1):  # 只处理前2个分段
            print(f"    🔍 分析分段 {i}...")

            prompt = f"""你是专业的心理评估分析师。分析以下5个问题的回答，评估Big5人格特质。

**严格评分标准：**
- 1分：极低表现
- 3分：中等表现
- 5分：极高表现

请返回JSON格式：
{{
  "success": true,
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }}
}}

第{i}段内容：
"""

            for j, item in enumerate(segment, 1):
                prompt += f"\n问题{j}: {item['question']}"
                prompt += f"\n回答{j}: {item['answer']}\n"

            try:
                response = client.chat.completions.create(
                    model="qwen-long",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )

                content = response.choices[0].message.content

                # 解析JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)

                    if 'scores' in result:
                        scores = result['scores']
                        print(f"      ✅ 评分: {scores}")

                        # 验证评分标准
                        invalid_scores = [s for s in scores.values() if s not in [1, 3, 5]]
                        if invalid_scores:
                            print(f"      ⚠️ 无效评分: {invalid_scores}")
                        else:
                            print(f"      ✅ 评分符合标准")

                        segment_results.append(result)
                    else:
                        print(f"      ❌ 无scores字段")
                else:
                    print(f"      ❌ JSON解析失败")

            except Exception as e:
                print(f"      ❌ 分析失败: {e}")

            time.sleep(3)  # API限制

        if segment_results:
            # 计算最终评分
            import statistics
            final_scores = {}
            for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                all_scores = [result['scores'][trait] for result in segment_results if 'scores' in result]
                if all_scores:
                    final_scores[trait] = int(statistics.median(all_scores))

            # 保存结果
            output_filename = f"{Path(file_path).stem}_5segment.json"
            output_path = os.path.join(output_dir, output_filename)

            result_data = {
                "file_info": {
                    "filename": Path(file_path).name,
                    "total_questions": len(questions),
                    "segments_processed": len(segment_results),
                    "analysis_date": datetime.now().isoformat()
                },
                "segment_results": segment_results,
                "final_scores": final_scores
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            print(f"  💾 结果已保存: {output_filename}")
            return True
        else:
            print(f"  ❌ 没有成功的分段结果")
            return False

    except Exception as e:
        print(f"  ❌ 文件处理失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始5题分段批量分析")
    print("=" * 50)

    # 输入输出目录
    input_dir = "results/results"
    output_dir = "5segment_results"

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 查找文件
    files = glob.glob(os.path.join(input_dir, "*.json"))
    files = files[:5]  # 只处理前5个文件

    print(f"📊 找到 {len(files)} 个文件")

    if not files:
        print("❌ 未找到文件")
        return

    # 批量处理
    success_count = 0
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 开始处理...")
        if analyze_single_file(file_path, output_dir):
            success_count += 1

    print(f"\n🎯 批量处理完成")
    print(f"✅ 成功: {success_count}/{len(files)}")
    print(f"📁 输出目录: {output_dir}")

if __name__ == "__main__":
    main()