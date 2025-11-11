#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恢复被错误移动的测评报告文件
Restore incorrectly moved assessment report files
"""

import shutil
from pathlib import Path

def restore_problem_reports():
    """恢复被错误移动的测评报告文件"""

    # 源目录和目标目录
    problem_reports_dir = Path("results/cloud-fallback-batch-analysis/problem_reports")
    readonly_original_dir = Path("results/readonly-original")

    print("🔄 恢复被错误移动的测评报告文件")
    print("=" * 80)

    if not problem_reports_dir.exists():
        print(f"❌ 问题报告目录不存在: {problem_reports_dir}")
        return False

    if not readonly_original_dir.exists():
        print(f"❌ 目标目录不存在: {readonly_original_dir}")
        return False

    # 获取所有文件
    problem_files = list(problem_reports_dir.glob("*.json"))

    if not problem_files:
        print("❌ 问题报告目录中没有找到JSON文件")
        return False

    print(f"📁 找到 {len(problem_files)} 个被移动的文件")
    print(f"📂 源目录: {problem_reports_dir}")
    print(f"📂 目标目录: {readonly_original_dir}")
    print()

    moved_count = 0
    error_count = 0
    skipped_count = 0

    for file_path in problem_files:
        try:
            target_path = readonly_original_dir / file_path.name

            # 检查目标位置是否已存在同名文件
            if target_path.exists():
                print(f"⚠️  跳过（文件已存在）: {file_path.name}")
                skipped_count += 1
                continue

            # 移动文件
            shutil.move(str(file_path), str(target_path))
            moved_count += 1

            if moved_count % 50 == 0:
                print(f"   已恢复 {moved_count} 个文件...")

        except Exception as e:
            print(f"❌ 移动失败 {file_path.name}: {e}")
            error_count += 1

    print()
    print("📊 恢复完成统计:")
    print(f"   ✅ 成功恢复: {moved_count} 个文件")
    print(f"   ⚠️  跳过（已存在）: {skipped_count} 个文件")
    print(f"   ❌ 恢复失败: {error_count} 个文件")
    print()

    # 检查源目录是否为空
    remaining_files = list(problem_reports_dir.glob("*.json"))
    if remaining_files:
        print(f"⚠️  源目录中仍有 {len(remaining_files)} 个文件")
    else:
        print("✅ 源目录已清空")
        # 可以选择删除空目录
        try:
            problem_reports_dir.rmdir()
            print("🗑️  已删除空的问题报告目录")
        except Exception as e:
            print(f"⚠️  无法删除空目录: {e}")

    # 检查目标目录文件数量
    original_files = list(readonly_original_dir.glob("*.json"))
    print(f"📂 目标目录现在有 {len(original_files)} 个文件")

    return error_count == 0

def main():
    """主函数"""
    success = restore_problem_reports()

    if success:
        print("\n🎉 测评报告文件恢复成功！")
        print("💡 现在可以重新运行批量处理了")
    else:
        print("\n❌ 恢复过程中出现一些错误")
        print("💡 请检查错误信息并手动处理剩余文件")

    print("\n📋 建议下一步:")
    print("1. 修复 cloud_fallback_batch_processor.py 的问题报告识别逻辑")
    print("2. 运行修复后的批量处理")
    print("3. 验证处理结果")

if __name__ == "__main__":
    main()