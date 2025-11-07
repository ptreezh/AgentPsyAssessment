#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON文件清理脚本
清理人格回答文件，移除JSON格式前的文字说明，确保可以正确解析
"""

import json
import re
from pathlib import Path

class JSONCleaner:
    """JSON文件清理工具"""

    def __init__(self, exam_dir: str = "html/exam"):
        self.exam_dir = Path(exam_dir)

    def clean_json_file(self, file_path: Path) -> bool:
        """清理单个JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找JSON开始的标记
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                print(f"❌ {file_path.name}: 未找到JSON结构")
                return False

            # 提取纯JSON内容
            json_content = content[json_start:json_end]

            # 验证JSON格式
            try:
                data = json.loads(json_content)
                print(f"✅ {file_path.name}: JSON格式正确")
            except json.JSONDecodeError as e:
                print(f"❌ {file_path.name}: JSON格式错误 - {e}")
                return False

            # 重新写入干净的JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ {file_path.name}: 清理完成")
            return True

        except Exception as e:
            print(f"❌ 清理 {file_path.name} 失败: {e}")
            return False

    def clean_all_json_files(self) -> dict:
        """清理所有JSON文件"""
        results = {"total": 0, "success": 0, "failed": 0, "files": []}

        json_files = list(self.exam_dir.glob("*.json"))
        results["total"] = len(json_files)

        print(f"🔍 找到 {len(json_files)} 个JSON文件")

        for file_path in json_files:
            print(f"\n🧹 清理: {file_path.name}")
            success = self.clean_json_file(file_path)

            results["files"].append({
                "name": file_path.name,
                "success": success
            })

            if success:
                results["success"] += 1
            else:
                results["failed"] += 1

        return results

    def validate_json_structure(self, file_path: Path) -> bool:
        """验证JSON文件结构是否符合预期"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查基本结构
            if 'responses' not in data:
                print(f"❌ {file_path.name}: 缺少 'responses' 字段")
                return False

            responses = data['responses']
            if not isinstance(responses, list):
                print(f"❌ {file_path.name}: 'responses' 不是数组")
                return False

            if len(responses) == 0:
                print(f"⚠️ {file_path.name}: 'responses' 为空")
                return True

            # 检查第一个响应的结构
            first_response = responses[0]
            required_fields = ['question', 'answer']

            for field in required_fields:
                if field not in first_response:
                    print(f"❌ {file_path.name}: 响应中缺少 '{field}' 字段")
                    return False

            print(f"✅ {file_path.name}: 结构验证通过")
            return True

        except Exception as e:
            print(f"❌ 验证 {file_path.name} 失败: {e}")
            return False

    def validate_all_files(self) -> dict:
        """验证所有JSON文件结构"""
        results = {"total": 0, "valid": 0, "invalid": 0}

        json_files = list(self.exam_dir.glob("*.json"))
        results["total"] = len(json_files)

        print(f"\n🔍 验证 {len(json_files)} 个JSON文件结构")

        for file_path in json_files:
            print(f"\n📋 验证: {file_path.name}")
            is_valid = self.validate_json_structure(file_path)

            if is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1

        return results

def main():
    """主函数"""
    print("🧠 Portable PsyAgent - JSON文件清理工具")
    print("=" * 50)

    cleaner = JSONCleaner()

    if not cleaner.exam_dir.exists():
        print(f"❌ 目录不存在: {cleaner.exam_dir}")
        return

    # 清理所有JSON文件
    print("\n🧹 开始清理JSON文件...")
    clean_results = cleaner.clean_all_json_files()

    # 验证文件结构
    print(f"\n🔍 验证文件结构...")
    validate_results = cleaner.validate_all_files()

    # 显示总结
    print(f"\n🎉 清理完成!")
    print(f"📊 清理结果:")
    print(f"  - 总文件数: {clean_results['total']}")
    print(f"  - 成功: {clean_results['success']}")
    print(f"  - 失败: {clean_results['failed']}")

    print(f"\n📋 验证结果:")
    print(f"  - 总文件数: {validate_results['total']}")
    print(f"  - 有效: {validate_results['valid']}")
    print(f"  - 无效: {validate_results['invalid']}")

    if clean_results["failed"] > 0:
        print(f"\n❌ 以下文件清理失败:")
        for file_info in clean_results["files"]:
            if not file_info["success"]:
                print(f"  - {file_info['name']}")

if __name__ == "__main__":
    main()