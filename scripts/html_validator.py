#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告验证和修复脚本
自动检测和修复HTML格式问题，确保所有文件都是有效的HTML文档
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple

class HTMLValidator:
    """HTML文档验证和修复工具"""

    def __init__(self, html_dir: str = "html"):
        self.html_dir = Path(html_dir)
        self.issues = []

    def validate_html_structure(self, file_path: Path) -> Dict:
        """验证单个HTML文件结构"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查文件大小（太小可能表示内容不完整）
            if len(content) < 1000:
                issues.append(f"文件过小 ({len(content)} bytes)，可能内容不完整")

            # 检查是否以DOCTYPE开头
            if not content.strip().startswith('<!DOCTYPE html>'):
                issues.append("缺少DOCTYPE声明")

            # 检查是否有markdown代码块标记
            if content.startswith('```html'):
                issues.append("包含markdown代码块标记")

            # 检查基本HTML结构
            if '<html' not in content:
                issues.append("缺少<html>标签")

            if '<head>' not in content:
                issues.append("缺少<head>标签")

            if '<body>' not in content:
                issues.append("缺少<body>标签")

            # 检查是否只有纯文本内容
            if '<!DOCTYPE html>' not in content and '<html' not in content and '<' not in content:
                issues.append("纯文本内容，不是HTML格式")

        except Exception as e:
            issues.append(f"读取文件失败: {e}")

        return {
            'file': str(file_path),
            'issues': issues,
            'is_valid': len(issues) == 0
        }

    def fix_html_format(self, file_path: Path) -> bool:
        """修复HTML格式问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # 移除开头的markdown代码块标记
            if content.startswith('```html'):
                lines = content.split('\n')
                # 找到代码块结束位置
                end_marker = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '```':
                        end_marker = i
                        break

                if end_marker > 0:
                    content = '\n'.join(lines[end_marker + 1:]).strip()
                    print(f"✅ 移除markdown代码块标记")

            # 如果修复后内容为空或过短，说明是无效文件
            if len(content) < 1000:
                print(f"❌ 文件修复后仍然过短，可能是纯文本文件")
                return False

            # 确保以DOCTYPE开头
            if not content.strip().startswith('<!DOCTYPE html>'):
                content = f"<!DOCTYPE html>\n{content}"
                print(f"✅ 添加DOCTYPE声明")

            # 写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 修复完成: {file_path.name}")
                return True
            else:
                print(f"ℹ️  无需修复: {file_path.name}")
                return True

        except Exception as e:
            print(f"❌ 修复失败 {file_path.name}: {e}")
            return False

    def scan_all_html_files(self) -> List[Dict]:
        """扫描所有HTML文件"""
        html_files = list(self.html_dir.glob("*.html"))
        results = []

        print(f"🔍 扫描 {len(html_files)} 个HTML文件...")

        for html_file in html_files:
            result = self.validate_html_structure(html_file)
            results.append(result)

            if result['issues']:
                print(f"❌ {html_file.name}: {', '.join(result['issues'])}")
            else:
                print(f"✅ {html_file.name}: 格式正确")

        return results

    def fix_all_files(self, scan_results: List[Dict]) -> Dict:
        """批量修复所有问题文件"""
        fixed_count = 0
        failed_count = 0
        deleted_count = 0

        print(f"\n🔧 开始修复问题文件...")

        for result in scan_results:
            if not result['is_valid']:
                file_path = Path(result['file'])

                # 检查是否是纯文本文件（应该删除）
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 如果是纯文本且没有HTML结构，删除文件
                    if '<!DOCTYPE html>' not in content and '<html' not in content and len(content) < 1000:
                        file_path.unlink()
                        deleted_count += 1
                        print(f"🗑️  删除无效文件: {file_path.name}")
                        continue

                except:
                    pass

                # 尝试修复
                if self.fix_html_format(file_path):
                    fixed_count += 1
                else:
                    failed_count += 1

        return {
            'fixed': fixed_count,
            'failed': failed_count,
            'deleted': deleted_count
        }

    def generate_report(self, scan_results: List[Dict], fix_results: Dict) -> str:
        """生成验证报告"""
        total_files = len(scan_results)
        valid_files = sum(1 for r in scan_results if r['is_valid'])
        invalid_files = total_files - valid_files

        report = f"""
# HTML格式验证报告

## 📊 总体统计
- 总文件数: {total_files}
- 有效文件: {valid_files}
- 无效文件: {invalid_files}

## 🔧 修复结果
- 成功修复: {fix_results['fixed']} 个
- 修复失败: {fix_results['failed']} 个
- 删除无效文件: {fix_results['deleted']} 个

## 📋 文件详情
"""

        for result in scan_results:
            status = "✅ 有效" if result['is_valid'] else "❌ 无效"
            report += f"- {Path(result['file']).name}: {status}\n"
            if result['issues']:
                for issue in result['issues']:
                    report += f"  - {issue}\n"

        return report

def main():
    """主函数"""
    print("🧠 Portable PsyAgent - HTML格式验证工具")
    print("=" * 50)

    # 初始化验证器
    validator = HTMLValidator()

    if not validator.html_dir.exists():
        print(f"❌ HTML目录不存在: {validator.html_dir}")
        return

    # 扫描所有文件
    scan_results = validator.scan_all_html_files()

    # 修复问题文件
    fix_results = validator.fix_all_files(scan_results)

    # 生成报告
    report = validator.generate_report(scan_results, fix_results)

    # 保存报告
    report_path = Path("html_validation_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 验证报告已保存: {report_path}")
    print(f"\n🎉 验证完成!")
    print(f"- 总文件数: {len(scan_results)}")
    print(f"- 修复成功: {fix_results['fixed']}")
    print(f"- 删除无效: {fix_results['deleted']}")
    print(f"- 修复失败: {fix_results['failed']}")

if __name__ == "__main__":
    main()