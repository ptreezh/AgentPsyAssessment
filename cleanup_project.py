#!/usr/bin/env python3
"""
项目根目录清理脚本
整理项目根目录，将测试脚本移动到专门目录，只保留核心文件
"""

import os
import shutil
from datetime import datetime

def cleanup_project_root():
    """清理项目根目录"""

    print("🧹 开始清理项目根目录")
    print("=" * 60)

    # 核心文件列表 - 这些应该保留在根目录
    CORE_FILES = {
        # 配置文件
        'README.md',
        'CLAUDE.md',
        '.gitignore',
        'requirements.txt',
        'setup.py',

        # 核心配置
        'python_utf8_config.py',
        'i18n.py',

        # MCP服务器
        'mcp_cli_server.py',

        # 核心CLI
        'cli-wrapper.py',
        'skill_activator.py'
    }

    # 需要移动到测试目录的文件
    TEST_SCRIPTS_PATTERN = [
        'test_*.py',
        '*_test.py',
        'analyze_*.py',
        'claude_code_*.py',
        'simple_*.py',
        'political_*.py',
        'stress_*.py',
        'batch_*.py',
        'quick_*.py',
        'demo_*.py',
        'end_to_end_*.py',
        'run_*.py',
        'wechat_*.py',
        'generate_*.py',
        'restore_*.py',
        'debug_*.py',
        'assessment_*.py',
        'fixed_*.py',
        'complete_*.py'
    ]

    # 创建测试目录
    test_dir = 'archived_test_scripts'
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"✅ 创建测试目录: {test_dir}")

    # 移动测试脚本
    moved_count = 0
    kept_files = []

    # 获取根目录所有Python文件
    root_files = [f for f in os.listdir('.') if f.endswith('.py')]

    for file in root_files:
        # 跳过当前清理脚本
        if file == 'cleanup_project.py':
            continue

        # 检查是否是核心文件
        if file in CORE_FILES:
            kept_files.append(file)
            print(f"✅ 保留核心文件: {file}")
            continue

        # 检查是否匹配测试脚本模式
        is_test_script = False
        for pattern in TEST_SCRIPTS_PATTERN:
            if pattern.replace('*', '') in file or 'test' in file.lower():
                is_test_script = True
                break

        if is_test_script:
            # 移动到测试目录
            dest_path = os.path.join(test_dir, file)
            if os.path.exists(dest_path):
                # 如果目标文件已存在，添加时间戳
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(file)
                dest_path = os.path.join(test_dir, f"{name}_{timestamp}{ext}")

            shutil.move(file, dest_path)
            moved_count += 1
            print(f"📦 移动测试脚本: {file} → {test_dir}/")
        else:
            # 不确定用途的文件，询问或保留
            kept_files.append(file)
            print(f"❓ 保留文件: {file} (用途不明确)")

    print(f"\n📊 清理统计:")
    print(f"   📦 移动测试脚本: {moved_count} 个")
    print(f"   ✅ 保留核心文件: {len(kept_files)} 个")
    print(f"   📁 测试脚本目录: {test_dir}/")

    # 生成README
    readme_content = f"""# Archived Test Scripts

此目录包含从项目根目录移动的测试脚本。

## 移动时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 移动的文件
- 共移动了 {moved_count} 个测试脚本

## 使用建议
- 这些脚本主要用于测试和验证
- 如需使用，请复制到根目录或直接在此目录运行
- 建议使用技能系统进行测试，而不是直接运行这些脚本

## 技能系统使用方法
请参考 `.claude/skills/` 目录下的技能文档，直接使用技能进行测试。
"""

    readme_path = os.path.join(test_dir, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"📝 生成测试目录说明: {readme_path}")

    # 检查整理后的根目录
    remaining_files = [f for f in os.listdir('.') if f.endswith('.py')]
    print(f"\n📋 整理后根目录Python文件 ({len(remaining_files)}个):")
    for file in sorted(remaining_files):
        size = os.path.getsize(file)
        print(f"   📄 {file} ({size:,} bytes)")

    print(f"\n🎉 项目根目录清理完成！")
    print(f"💡 建议: 使用技能系统进行测试，而不是创建新的测试脚本")
    print(f"🔧 技能位置: .claude/skills/")

    return moved_count, len(kept_files)

if __name__ == "__main__":
    cleanup_project_root()