#!/usr/bin/env python3
"""
批量复制问卷文件到独立技能文件夹
将所有现有的问卷文件复制到 standalone-questionnaire 技能的 questionnaires 文件夹中
"""

import os
import shutil
import json
from pathlib import Path

def convert_to_skill_format(source_data, filename):
    """将源问卷数据转换为技能格式"""

    # 如果已经是技能格式，直接返回
    if "test_info" in source_data and "test_bank" in source_data:
        return source_data

    # 尝试转换不同的问卷格式
    skill_format = {
        "test_info": {
            "test_name": source_data.get("title", filename),
            "test_category": source_data.get("category", "General Assessment"),
            "scale": source_data.get("scale", "Standard Assessment Scale"),
            "total_questions": len(source_data.get("questions", [])),
            "dimensions": [],
            "instruction": source_data.get("description", "请根据以下问题进行回答"),
            "scoring_methodology": source_data.get("scoring", "Standard scoring"),
            "language": "中文" if any(c in filename for c in ['zh', 'cn', '中文']) else "English",
            "difficulty": source_data.get("difficulty", "中等"),
            "target_audience": source_data.get("target_audience", "General population")
        },
        "test_bank": []
    }

    # 提取维度信息
    questions = source_data.get("questions", [])
    dimensions = set()

    for q in questions:
        if "dimension" in q:
            dimensions.add(q["dimension"])
        elif "trait" in q:
            dimensions.add(q["trait"])
        elif "category" in q:
            dimensions.add(q["category"])

    skill_format["test_info"]["dimensions"] = list(dimensions)

    # 转换问题格式
    for i, q in enumerate(questions):
        skill_question = {
            "question_id": q.get("id", f"Q_{i+1:03d}"),
            "dimension": q.get("dimension", q.get("trait", q.get("category", "General"))),
            "question_type": q.get("type", q.get("question_type", "scenario"))
        }

        # 根据问题类型添加不同字段
        if "scenario" in q:
            skill_question["scenario"] = q["scenario"]
        elif "question" in q:
            skill_question["question"] = q["question"]
        elif "prompt" in q:
            skill_question["question"] = q["prompt"]
        else:
            skill_question["question"] = q.get("text", str(q))

        if "prompt" in q:
            skill_question["prompt"] = q["prompt"]

        # 添加评估标准
        if "evaluation_rubric" in q:
            skill_question["evaluation_rubric"] = q["evaluation_rubric"]
        elif "scoring" in q:
            skill_question["evaluation_rubric"] = q["scoring"]
        else:
            skill_question["evaluation_rubric"] = {
                "description": "标准评估",
                "scale": {
                    "1": "低分表现",
                    "3": "中等表现",
                    "5": "高分表现"
                }
            }

        skill_format["test_bank"].append(skill_question)

    return skill_format

def batch_copy_questionnaires():
    """批量复制问卷文件"""

    # 源文件夹
    source_dirs = [
        "llm_assessment/test_files/中文版",
        "llm_assessment/test_files/English"
    ]

    # 目标文件夹
    target_dir = ".claude/skills/standalone-questionnaire/questionnaires"

    # 确保目标文件夹存在
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    copied_count = 0
    error_count = 0

    print("🔄 开始批量复制问卷文件...")
    print("=" * 60)

    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            print(f"⚠️ 源文件夹不存在: {source_dir}")
            continue

        print(f"\n📁 处理文件夹: {source_dir}")
        print("-" * 40)

        for filename in os.listdir(source_dir):
            if filename.endswith('.json'):
                source_path = os.path.join(source_dir, filename)

                # 生成目标文件名
                target_filename = filename
                if source_dir.endswith("中文版"):
                    target_filename = f"cn_{filename}"
                elif source_dir.endswith("English"):
                    target_filename = f"en_{filename}"

                target_path = os.path.join(target_dir, target_filename)

                try:
                    # 读取源文件
                    with open(source_path, 'r', encoding='utf-8') as f:
                        source_data = json.load(f)

                    # 转换为技能格式
                    skill_data = convert_to_skill_format(source_data, filename)

                    # 保存到目标位置
                    with open(target_path, 'w', encoding='utf-8') as f:
                        json.dump(skill_data, f, ensure_ascii=False, indent=2)

                    print(f"✅ {filename} -> {target_filename}")
                    copied_count += 1

                except Exception as e:
                    print(f"❌ {filename}: {e}")
                    error_count += 1

    print(f"\n📊 批量复制完成!")
    print(f"✅ 成功复制: {copied_count} 个文件")
    print(f"❌ 复制失败: {error_count} 个文件")

    # 统计技能文件夹中的问卷数量
    if os.path.exists(target_dir):
        total_files = len([f for f in os.listdir(target_dir) if f.endswith('.json')])
        print(f"📋 技能文件夹中现有问卷总数: {total_files} 个")

        print("\n📋 已支持的问卷列表:")
        for i, filename in enumerate(sorted(os.listdir(target_dir)), 1):
            if filename.endswith('.json'):
                print(f"  {i:2d}. {filename}")

if __name__ == "__main__":
    batch_copy_questionnaires()