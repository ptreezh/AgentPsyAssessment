#!/usr/bin/env python3
"""
简化版批量处理问卷脚本
使用技能回答 llm_assessment/test_files 目录下的所有问卷
结果输出到 html/alldefault 目录
"""

import os
import json
import sys
import glob
import subprocess
from pathlib import Path
from datetime import datetime

class SimpleBatchProcessor:
    def __init__(self, input_dir="llm_assessment/test_files", output_dir="html/alldefault"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 默认参数
        self.default_model = "def"
        self.default_role = "def"
        self.default_temperature = 0.7

    def get_questionnaire_files(self):
        """获取所有问卷文件"""
        json_files = list(self.input_dir.glob("*.json"))
        print(f"找到 {len(json_files)} 个问卷文件:")
        for i, file in enumerate(json_files, 1):
            print(f"  {i}. {file.name}")
        return json_files

    def get_output_filename(self, input_file):
        """生成输出文件名"""
        base_name = input_file.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{base_name}_responses_{timestamp}.json"

    def process_single_questionnaire(self, file_path):
        """处理单个问卷"""
        print(f"\n🔍 处理问卷: {file_path.name}")
        print("=" * 60)

        try:
            # 使用CLI命令运行评估
            cmd = [
                sys.executable,
                "llm_assessment/run_assessment_unified.py",
                "--model_name", self.default_model,
                "--test_file", str(file_path),
                "--role_name", self.default_role,
                "--tmpr", str(self.default_temperature)
            ]

            print(f"🚀 执行命令: {' '.join(cmd)}")

            # 运行命令
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

            if result.returncode == 0:
                print(f"✅ 问卷 {file_path.name} 处理成功")
                print(f"📁 结果保存到: {self.get_output_filename(file_path)}")
                if result.stdout:
                    print(f"📄 输出: {result.stdout[:500]}...")
                return True
            else:
                print(f"❌ 问卷 {file_path.name} 处理失败")
                print(f"📄 错误: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 处理问卷 {file_path.name} 时出错: {str(e)}")
            return False

    def create_summary_report(self, results):
        """创建汇总报告"""
        summary = {
            "batch_processing_summary": {
                "timestamp": datetime.now().isoformat(),
                "input_directory": str(self.input_dir),
                "output_directory": str(self.output_dir),
                "total_questionnaires": len(results),
                "successful": sum(1 for r in results if r["success"]),
                "failed": sum(1 for r in results if not r["success"]),
                "success_rate": sum(1 for r in results if r["success"]) / len(results) * 100 if results else 0
            },
            "processed_questionnaires": results
        }

        summary_file = self.output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n📊 汇总报告保存到: {summary_file}")
        return summary_file

    def run_batch_processing(self):
        """运行批量处理"""
        print("🚀 开始批量处理问卷")
        print(f"📁 输入目录: {self.input_dir}")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"🤖 使用模型: {self.default_model}")
        print(f"🎭 使用角色: {self.default_role}")
        print("=" * 60)

        # 获取所有问卷文件
        questionnaire_files = self.get_questionnaire_files()

        if not questionnaire_files:
            print("❌ 没有找到问卷文件")
            return

        # 处理结果
        results = []

        # 逐个处理问卷
        for i, file_path in enumerate(questionnaire_files, 1):
            print(f"\n📍 进度: {i}/{len(questionnaire_files)}")

            success = self.process_single_questionnaire(file_path)

            result = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "success": success,
                "output_file": str(self.get_output_filename(file_path)) if success else None,
                "timestamp": datetime.now().isoformat()
            }
            results.append(result)

        # 创建汇总报告
        summary_file = self.create_summary_report(results)

        # 打印最终统计
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        print(f"\n🎉 批量处理完成!")
        print(f"📊 成功: {successful}/{total} ({successful/total*100:.1f}%)")
        print(f"📁 所有结果保存在: {self.output_dir}")
        print(f"📋 汇总报告: {summary_file}")

if __name__ == "__main__":
    processor = SimpleBatchProcessor()
    processor.run_batch_processing()