#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
便携式心理评估系统 - 企业级云端批量处理快捷脚本
Portable PsyAgent - Enterprise Cloud Batch Processing Shortcut Script

这个脚本提供了一个便捷的方式来调用 cloud_fallback_enterprise 目录下的批量评估分析系统。
自动设置正确的输入目录（原始测评报告）和输出目录路径。

This script provides a convenient way to call the batch evaluation analysis system
in the cloud_fallback_enterprise directory. Automatically sets the correct input
directory (original assessment reports) and output directory paths.

使用方法 / Usage:
    python run_cloud_batch.py                    # 使用默认设置
    python run_cloud_batch.py --enhanced         # 启用增强算法
    python run_cloud_batch.py --quick            # 快速测试模式（仅处理3个文件）
    python run_cloud_batch.py --no-cloud         # 仅使用本地模型
    python run_cloud_batch.py --help             # 查看所有选项

作者 / Author: pTreezh / Dr Zhang
联系方式 / Contact: 3061176@qq.com
官方网站 / Website: https://cn.agentpsy.com
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()
CLOUD_FALLBACK_DIR = PROJECT_ROOT / "production_pipelines" / "cloud_fallback_enterprise"
BATCH_PROCESSOR_SCRIPT = CLOUD_FALLBACK_DIR / "cloud_fallback_batch_processor.py"

# 默认路径配置
DEFAULT_INPUT_DIR = PROJECT_ROOT / "results" / "readonly-original"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "cloud-fallback-batch-analysis"


def validate_directories():
    """验证必要的目录和文件是否存在"""
    errors = []

    # 检查批量处理器脚本
    if not BATCH_PROCESSOR_SCRIPT.exists():
        errors.append(f"❌ 批量处理器脚本不存在: {BATCH_PROCESSOR_SCRIPT}")

    # 检查输入目录
    if not DEFAULT_INPUT_DIR.exists():
        errors.append(f"❌ 输入目录不存在: {DEFAULT_INPUT_DIR}")

    # 检查输入目录是否有文件
    if DEFAULT_INPUT_DIR.exists():
        json_files = list(DEFAULT_INPUT_DIR.glob("*.json"))
        if len(json_files) == 0:
            errors.append(f"❌ 输入目录为空: {DEFAULT_INPUT_DIR}")
        else:
            print(f"✅ 找到 {len(json_files)} 个测评报告文件")

    if errors:
        print("🚫 目录验证失败:")
        for error in errors:
            print(f"   {error}")
        print()
        print("💡 请确保:")
        print("   1. production_pipelines/cloud_fallback_enterprise/ 目录存在")
        print("   2. cloud_fallback_batch_processor.py 文件存在")
        print("   3. results/readonly-original/ 目录存在且包含JSON文件")
        return False

    return True


def create_output_directory(output_dir: Path):
    """创建输出目录"""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 输出目录已创建: {output_dir}")
        return True
    except Exception as e:
        print(f"❌ 创建输出目录失败: {e}")
        return False


def run_batch_processing(args):
    """运行批量处理"""
    try:
        # 构建命令行参数
        cmd = [
            sys.executable,
            str(BATCH_PROCESSOR_SCRIPT),
            "--input-dir", str(DEFAULT_INPUT_DIR),
            "--output-dir", str(args.output_dir)
        ]

        # 添加可选参数
        if args.enhanced:
            cmd.append("--enhanced")
            print("🚀 启用增强算法")

        if args.no_cloud:
            cmd.append("--no-cloud-fallback")
            print("🏠 仅使用本地模型")

        if args.no_performance:
            cmd.append("--no-performance-monitoring")
            print("📊 禁用性能监控")

        if args.max_evaluators > 0:
            cmd.extend(["--max-evaluators", str(args.max_evaluators)])
            print(f"🔧 最大评估器数量: {args.max_evaluators}")

        if args.skip_problem_filter:
            print("⚠️  跳过问题报告筛选（处理所有文件）")
            # 注意：cloud_fallback_batch_processor.py 没有这个参数
            # 我们需要通过修改输入或使用其他方法来实现

        # 快速模式：限制文件数量
        if args.quick:
            print("⚡ 快速测试模式")
            # 这里可以通过修改输入目录或者设置环境变量来实现
            # 暂时通过创建临时目录的方式
            quick_input_dir = args.output_dir / "quick_input"
            quick_input_dir.mkdir(exist_ok=True)

            # 复制前3个文件到临时目录
            import shutil
            json_files = list(DEFAULT_INPUT_DIR.glob("*.json"))[:3]
            for file in json_files:
                shutil.copy2(file, quick_input_dir)

            # 更新命令为使用临时目录
            cmd[cmd.index("--input-dir") + 1] = str(quick_input_dir)
            print(f"📁 快速模式输入文件: {len(json_files)} 个")

        print()
        print("🚀 启动企业级云端批量处理系统...")
        print("=" * 80)
        print(f"📂 输入目录: {cmd[cmd.index('--input-dir') + 1]}")
        print(f"📁 输出目录: {cmd[cmd.index('--output-dir') + 1]}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()

        # 运行命令
        result = subprocess.run(cmd, cwd=str(CLOUD_FALLBACK_DIR))

        if result.returncode == 0:
            print()
            print("🎉 批量处理完成！")
            print(f"📊 结果保存在: {args.output_dir}")

            # 列出生成的文件
            if args.output_dir.exists():
                result_files = list(args.output_dir.glob("*"))
                if result_files:
                    print("\n📄 生成的文件:")
                    for file in sorted(result_files):
                        print(f"   📁 {file.name}")
        else:
            print(f"\n❌ 批量处理失败，退出码: {result.returncode}")
            return False

        return True

    except Exception as e:
        print(f"❌ 运行批量处理失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="便携式心理评估系统 - 企业级云端批量处理快捷脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 / Examples:
  python run_cloud_batch.py                    # 默认设置运行
  python run_cloud_batch.py --enhanced         # 启用增强算法
  python run_cloud_batch.py --quick            # 快速测试（3个文件）
  python run_cloud_batch.py --no-cloud         # 仅本地模型
  python run_cloud_batch.py --output-dir custom_output  # 自定义输出目录

注意 / Notes:
  - 输入目录固定为: results/readonly-original
  - 默认输出目录为: results/cloud-fallback-batch-analysis
  - 支持 Cloud Fallback 三层降级策略
  - 自动问题报告筛选和断点续跑功能
        """
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="输出目录路径 (默认: results/cloud-fallback-batch-analysis)"
    )

    parser.add_argument(
        "--enhanced",
        action="store_true",
        help="启用增强算法"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="快速测试模式（仅处理前3个文件）"
    )

    parser.add_argument(
        "--no-cloud",
        action="store_true",
        help="禁用Cloud Fallback，仅使用本地模型"
    )

    parser.add_argument(
        "--no-performance",
        action="store_true",
        help="禁用性能监控"
    )

    parser.add_argument(
        "--max-evaluators",
        type=int,
        default=0,
        help="最大评估器数量（默认：自动）"
    )

    parser.add_argument(
        "--skip-problem-filter",
        action="store_true",
        help="跳过问题报告筛选，处理所有文件（临时解决方案）"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Portable PsyAgent v1.0 - Enterprise Cloud Batch Processor"
    )

    args = parser.parse_args()

    # 显示标题信息
    print("🧠 便携式心理评估系统 - 企业级云端批量处理快捷脚本")
    print("   Portable PsyAgent - Enterprise Cloud Batch Processing Shortcut")
    print()
    print("👤 作者: pTreezh / Dr Zhang")
    print("📧 联系: 3061176@qq.com")
    print("🌐 官网: https://cn.agentpsy.com")
    print()

    # 验证目录
    if not validate_directories():
        sys.exit(1)

    # 创建输出目录
    if not create_output_directory(args.output_dir):
        sys.exit(1)

    # 运行批量处理
    if not run_batch_processing(args):
        sys.exit(1)


if __name__ == "__main__":
    main()