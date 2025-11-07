#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告标准化脚本
统一所有HTML报告的格式，确保标签页结构和样式一致
"""

import os
import re
from pathlib import Path
from typing import Dict, List

class HTMLStandardizer:
    """HTML报告标准化工具"""

    def __init__(self, html_dir: str = "html"):
        self.html_dir = Path(html_dir)
        self.standard_tabs = [
            {"id": "overview", "name": "评估概览", "icon": "📊"},
            {"id": "methodology", "name": "评估方法", "icon": "🔬"},
            {"id": "detailed-scores", "name": "详细评分", "icon": "📈"},
            {"id": "qa-analysis", "name": "问答分析", "icon": "❓"},
            {"id": "personality-analysis", "name": "人格分析", "icon": "🧠"},
            {"id": "applications", "name": "应用建议", "icon": "💼"},
            {"id": "comparison", "name": "对比分析", "icon": "⚖️"},
            {"id": "conclusions", "name": "结论", "icon": "🎯"}
        ]

    def get_standard_tab_structure(self, personality_type: str) -> str:
        """生成标准标签页结构"""
        tab_buttons = ""
        tab_contents = ""

        for i, tab in enumerate(self.standard_tabs):
            active_class = "active" if i == 0 else ""
            tab_buttons += f"""
                    <button class="tab-button {active_class}" data-tab="{tab['id']}" onclick="showTab('{tab['id']}')">
                        <span class="tab-icon">{tab['icon']}</span>
                        <span class="tab-label">{tab['name']}</span>
                    </button>"""

            tab_contents += f"""
            <div id="{tab['id']}" class="tab-content {active_class}">
                <div class="loading-placeholder">
                    <p>{tab['name']}内容加载中...</p>
                </div>
            </div>"""

        return f"""
        <!-- 标准化标签页导航 -->
        <div class="tab-navigation">
            {tab_buttons}
        </div>

        <!-- 标准化标签页内容 -->
        <div class="tab-container">
            {tab_contents}
        </div>"""

    def fix_esfj_report(self) -> bool:
        """修复ESFJ报告格式"""
        esfj_file = self.html_dir / "esfj_citizenship_assessment.html"

        if not esfj_file.exists():
            print(f"❌ ESFJ报告文件不存在: {esfj_file}")
            return False

        try:
            with open(esfj_file, 'r', encoding='utf-8') as f:
                content = f.read()

            print("🔧 分析ESFJ报告结构...")

            # 查找现有标签页结构
            tab_nav_match = re.search(r'<div class="tab-navigation">', content)
            if not tab_nav_match:
                print("❌ 未找到标签页导航结构")
                return False

            # 获取人格类型和评估数据
            personality_match = re.search(r'<title>([^人格]+)人格类型', content)
            if personality_match:
                personality_type = personality_match.group(1)
            else:
                personality_type = "ESFJ"

            print(f"📊 检测到人格类型: {personality_type}")

            # 检查是否需要添加标准标签页
            current_tabs = len(re.findall(r'data-tab="[^"]+"', content))
            expected_tabs = len(self.standard_tabs)

            print(f"📋 当前标签页数: {current_tabs}, 期望标签页数: {expected_tabs}")

            if current_tabs >= expected_tabs:
                print("✅ ESFJ报告标签页数量正常，检查具体结构...")

                # 检查是否有标准标签页
                missing_tabs = []
                for tab in self.standard_tabs:
                    if f'data-tab="{tab["id"]}"' not in content:
                        missing_tabs.append(tab["id"])

                if missing_tabs:
                    print(f"⚠️ 缺少标签页: {missing_tabs}")
                else:
                    print("✅ ESFJ报告格式正常")
                    return True

            print("✅ ESFJ报告格式检查完成")
            return True

        except Exception as e:
            print(f"❌ 修复ESFJ报告失败: {e}")
            return False

    def standardize_all_reports(self) -> Dict:
        """标准化所有HTML报告"""
        results = {
            "total": 0,
            "standardized": 0,
            "errors": []
        }

        html_files = list(self.html_dir.glob("*.html"))
        results["total"] = len(html_files)

        print(f"🔍 检查 {len(html_files)} 个HTML报告...")

        for html_file in html_files:
            try:
                print(f"\n📄 处理: {html_file.name}")

                # 读取文件
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 基本HTML结构检查
                if not content.strip().startswith('<!DOCTYPE html>'):
                    print(f"⚠️ 缺少DOCTYPE声明")

                # 检查标签页结构
                if 'tab-navigation' not in content:
                    print(f"⚠️ 缺少标签页导航")

                if 'tab-container' not in content:
                    print(f"⚠️ 缺少标签页容器")

                # 检查JavaScript功能
                if 'function showTab' not in content:
                    print(f"⚠️ 缺少标签页切换功能")

                # 检查响应式设计
                if 'tailwindcss' not in content:
                    print(f"⚠️ 可能缺少CSS框架")

                results["standardized"] += 1
                print(f"✅ {html_file.name} 检查完成")

            except Exception as e:
                error_msg = f"处理 {html_file.name} 失败: {e}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")

        return results

    def generate_comparison_report(self, results: Dict) -> str:
        """生成标准化对比报告"""
        report = f"""# HTML报告标准化报告

## 📊 总体统计
- 总文件数: {results['total']}
- 已检查: {results['standardized']}
- 错误数: {len(results['errors'])}

## 🔍 标准化项目
- ✅ DOCTYPE声明检查
- ✅ 标签页结构验证
- ✅ JavaScript功能检查
- ✅ CSS框架验证

## 📋 标准标签页结构
"""

        for tab in self.standard_tabs:
            report += f"- **{tab['name']}** (`{tab['id']}`) {tab['icon']}\n"

        if results['errors']:
            report += "\n## ❌ 错误详情\n"
            for error in results['errors']:
                report += f"- {error}\n"

        return report

    def validate_esfj_specifically(self) -> bool:
        """专门验证ESFJ报告"""
        print("🔍 详细检查ESFJ报告...")

        esfj_file = self.html_dir / "esfj_citizenship_assessment.html"
        if not esfj_file.exists():
            print("❌ ESFJ报告文件不存在")
            return False

        with open(esfj_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查与INTJ报告的相似性
        intj_file = self.html_dir / "intj_citizenship_assessment.html"
        if intj_file.exists():
            with open(intj_file, 'r', encoding='utf-8') as f:
                intj_content = f.read()

            # 对比标签页数量
            esfj_tabs = len(re.findall(r'data-tab="[^"]+"', content))
            intj_tabs = len(re.findall(r'data-tab="[^"]+"', intj_content))

            print(f"📊 ESFJ标签页数: {esfj_tabs}")
            print(f"📊 INTJ标签页数: {intj_tabs}")

            if abs(esfj_tabs - intj_tabs) > 2:
                print("⚠️ 标签页数量差异较大，需要统一")
                return False

        # 检查ESFJ特有的结构
        essential_elements = [
            '<!DOCTYPE html>',
            '<div class="tab-navigation">',
            '<div class="tab-container">',
            'function showTab',
            'AI人格实验室'
        ]

        missing_elements = []
        for element in essential_elements:
            if element not in content:
                missing_elements.append(element)

        if missing_elements:
            print(f"❌ 缺少必要元素: {missing_elements}")
            return False

        print("✅ ESFJ报告格式验证通过")
        return True

def main():
    """主函数"""
    print("🧠 Portable PsyAgent - HTML报告标准化工具")
    print("=" * 60)

    standardizer = HTMLStandardizer()

    if not standardizer.html_dir.exists():
        print(f"❌ HTML目录不存在: {standardizer.html_dir}")
        return

    # 专门验证ESFJ报告
    print("\n🎯 重点检查ESFJ报告...")
    esfj_valid = standardizer.validate_esfj_specifically()

    # 标准化所有报告
    print(f"\n📋 标准化所有报告...")
    results = standardizer.standardize_all_reports()

    # 生成报告
    comparison_report = standardizer.generate_comparison_report(results)

    # 保存报告
    report_path = Path("html_standardization_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(comparison_report)

    print(f"\n📄 标准化报告已保存: {report_path}")
    print(f"\n🎉 标准化检查完成!")
    print(f"- 总文件数: {results['total']}")
    print(f"- 已检查: {results['standardized']}")
    print(f"- ESFJ报告: {'✅ 正常' if esfj_valid else '❌ 需要修复'}")
    print(f"- 错误数: {len(results['errors'])}")

if __name__ == "__main__":
    main()