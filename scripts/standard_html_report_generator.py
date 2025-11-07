#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标准化HTML报告生成器
统一所有人格类型的HTML报告格式，确保一致的用户体验
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class StandardHTMLReportGenerator:
    """标准化HTML报告生成器"""

    def __init__(self):
        self.html_dir = Path("html")
        self.exam_dir = self.html_dir / "exam"
        self.stat_dir = self.html_dir / "stat"

        # 标准化的7个标签页结构
        self.standard_tabs = [
            {"id": "overview", "name": "评测概览", "icon": "📊"},
            {"id": "personality", "name": "人格特征分析", "icon": "🧠"},
            {"id": "detailed-scores", "name": "详细评分", "icon": "📈"},
            {"id": "qa-analysis", "name": "问答分析", "icon": "❓"},
            {"id": "strengths", "name": "优势分析", "icon": "💪"},
            {"id": "suggestions", "name": "改进建议", "icon": "🎯"},
            {"id": "conclusion", "name": "结论总结", "icon": "🏆"}
        ]

    def load_personality_responses(self, personality_type: str) -> Dict:
        """加载人格回答数据"""
        response_file = self.exam_dir / f"{personality_type.lower()}_citizenship_responses.json"

        if not response_file.exists():
            return {}

        try:
            with open(response_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载 {personality_type} 回答文件失败: {e}")
            return {}

    def load_evaluation_data(self, personality_type: str) -> Dict:
        """加载评估数据"""
        eval_file = self.stat_dir / f"{personality_type.lower()}_citizenship_evaluation.json"

        if not eval_file.exists():
            return {}

        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载 {personality_type} 评估文件失败: {e}")
            return {}

    def generate_standard_html_report(self, personality_type: str) -> bool:
        """生成标准化HTML报告"""
        print(f"🔄 生成 {personality_type} 标准化HTML报告...")

        # 加载数据
        responses = self.load_personality_responses(personality_type)
        evaluation = self.load_evaluation_data(personality_type)

        if not responses:
            print(f"❌ 找不到 {personality_type} 的回答数据")
            return False

        # 生成HTML内容
        html_content = self._build_html_structure(personality_type, responses, evaluation)

        # 保存文件
        output_file = self.html_dir / f"{personality_type.lower()}_citizenship_assessment.html"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f"✅ {personality_type} HTML报告已生成: {output_file}")
            return True

        except Exception as e:
            print(f"❌ 保存 {personality_type} HTML报告失败: {e}")
            return False

    def _build_html_structure(self, personality_type: str, responses: Dict, evaluation: Dict) -> str:
        """构建HTML结构"""

        # 基本信息提取
        response_count = len(responses.get('responses', []))
        total_score = evaluation.get('overall_score', 0)
        grade = evaluation.get('grade', 'N/A')

        # 生成CSS样式
        css_styles = self._generate_css_styles()

        # 生成标签页结构
        tabs_html = self._generate_tabs_structure()

        # 生成标签页内容
        tabs_content = self._generate_tabs_content(personality_type, responses, evaluation)

        # 生成JavaScript
        javascript = self._generate_javascript()

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personality_type}人格类型国情知识评估报告</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    {css_styles}
</head>
<body class="bg-gray-50">
    <!-- 头部导航 -->
    <header class="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold">{personality_type}人格类型评估报告</h1>
                    <p class="mt-2 text-blue-100">基于MBTI理论的公民知识综合评估</p>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold">总评分: {total_score}</div>
                    <div class="text-lg">等级: {grade}</div>
                </div>
            </div>
        </div>
    </header>

    <!-- 主要内容 -->
    <main class="container mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
            {tabs_html}
            {tabs_content}
        </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-gray-800 text-white mt-12 py-8">
        <div class="container mx-auto px-4 text-center">
            <p class="mb-2">🧠 AI人格实验室 - 专业心理评估平台</p>
            <p class="text-gray-400">
                <a href="https://cn.agentpsy.com" target="_blank" class="hover:text-white transition">
                    https://cn.agentpsy.com
                </a>
            </p>
            <p class="text-sm text-gray-500 mt-2">
                评估时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
            </p>
        </div>
    </footer>

    {javascript}
</body>
</html>"""

    def _generate_css_styles(self) -> str:
        """生成CSS样式"""
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

            * {
                font-family: 'Noto Sans SC', sans-serif;
            }

            .tab {
                @apply px-6 py-3 font-semibold border-b-2 cursor-pointer transition-colors duration-200;
            }

            .tab.active {
                @apply text-blue-600 border-blue-600;
            }

            .tab:not(.active) {
                @apply text-gray-600 border-transparent hover:text-blue-600;
            }

            .tab-content {
                display: none;
            }

            .tab-content.active {
                display: block;
            }

            .gradient-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }

            .card-hover {
                @apply transition-transform duration-200 hover:scale-105;
            }
        </style>
        """

    def _generate_tabs_structure(self) -> str:
        """生成标签页导航结构"""
        tabs_html = '<div class="tabs flex flex-wrap border-b mb-6">'

        for i, tab in enumerate(self.standard_tabs):
            active_class = "active" if i == 0 else ""
            tabs_html += f'''
                <button class="tab {active_class}" onclick="showTab('{tab['id']}')">
                    <span class="mr-2">{tab['icon']}</span>
                    {tab['name']}
                </button>'''

        tabs_html += '</div>'
        return tabs_html

    def _generate_tabs_content(self, personality_type: str, responses: Dict, evaluation: Dict) -> str:
        """生成标签页内容"""
        content_html = '<div class="tab-contents">'

        for i, tab in enumerate(self.standard_tabs):
            active_class = "active" if i == 0 else ""
            content_html += f'''
            <div id="{tab['id']}" class="tab-content {active_class}">
                {self._generate_tab_content(tab['id'], personality_type, responses, evaluation)}
            </div>'''

        content_html += '</div>'
        return content_html

    def _generate_tab_content(self, tab_id: str, personality_type: str, responses: Dict, evaluation: Dict) -> str:
        """生成单个标签页内容"""

        if tab_id == "overview":
            return self._generate_overview_content(personality_type, responses, evaluation)
        elif tab_id == "personality":
            return self._generate_personality_content(personality_type, responses)
        elif tab_id == "detailed-scores":
            return self._generate_scores_content(personality_type, evaluation)
        elif tab_id == "qa-analysis":
            return self._generate_qa_content(responses)
        elif tab_id == "strengths":
            return self._generate_strengths_content(personality_type, evaluation)
        elif tab_id == "suggestions":
            return self._generate_suggestions_content(personality_type, evaluation)
        elif tab_id == "conclusion":
            return self._generate_conclusion_content(personality_type, evaluation)
        else:
            return "<p>内容开发中...</p>"

    def _generate_overview_content(self, personality_type: str, responses: Dict, evaluation: Dict) -> str:
        """生成概览内容"""
        response_count = len(responses.get('responses', []))
        total_score = evaluation.get('overall_score', 0)
        grade = evaluation.get('grade', 'N/A')

        return f"""
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-blue-50 p-6 rounded-lg text-center">
                <div class="text-3xl font-bold text-blue-600">{personality_type}</div>
                <div class="text-gray-600 mt-2">人格类型</div>
            </div>
            <div class="bg-green-50 p-6 rounded-lg text-center">
                <div class="text-3xl font-bold text-green-600">{response_count}</div>
                <div class="text-gray-600 mt-2">回答题目数</div>
            </div>
            <div class="bg-purple-50 p-6 rounded-lg text-center">
                <div class="text-3xl font-bold text-purple-600">{total_score}</div>
                <div class="text-gray-600 mt-2">总评分</div>
            </div>
        </div>

        <div class="prose max-w-none">
            <h3 class="text-xl font-bold mb-4">评估概览</h3>
            <p>本报告基于{personality_type}人格类型特征，对公民知识问卷进行了全面评估。</p>
            <p>评估等级：<span class="text-2xl font-bold text-blue-600">{grade}</span></p>
        </div>
        """

    def _generate_personality_content(self, personality_type: str, responses: Dict) -> str:
        """生成人格特征内容"""
        return f"""
        <div class="prose max-w-none">
            <h3 class="text-xl font-bold mb-4">{personality_type}人格特征分析</h3>
            <p>基于{personality_type}人格类型的认知功能特点，分析其在公民知识问答中体现的思维模式和行为特征。</p>

            <div class="bg-blue-50 p-4 rounded-lg mt-4">
                <h4 class="font-bold mb-2">核心特征：</h4>
                <ul class="list-disc pl-5">
                    <li>基于人格类型的认知偏好回答问题</li>
                    <li>体现独特的信息处理方式</li>
                    <li>展现特定的人格优势</li>
                </ul>
            </div>
        </div>
        """

    def _generate_scores_content(self, personality_type: str, evaluation: Dict) -> str:
        """生成详细评分内容"""
        if not evaluation:
            return "<p>评估数据暂未生成</p>"

        return f"""
        <div class="prose max-w-none">
            <h3 class="text-xl font-bold mb-4">详细评分分析</h3>
            <div class="bg-yellow-50 p-4 rounded-lg">
                <p><strong>总评分：</strong>{evaluation.get('overall_score', 0)}</p>
                <p><strong>等级：</strong>{evaluation.get('grade', 'N/A')}</p>
                <p><strong>人格一致性：</strong>{evaluation.get('personality_consistency', 0)}%</p>
            </div>
        </div>
        """

    def _generate_qa_content(self, responses: Dict) -> str:
        """生成问答分析内容"""
        response_list = responses.get('responses', [])
        qa_html = '<div class="space-y-4">'

        for i, response in enumerate(response_list[:10]):  # 显示前10题
            question = response.get('question', 'N/A')
            answer = response.get('answer', 'N/A')

            qa_html += f"""
            <div class="border-l-4 border-blue-500 pl-4">
                <h4 class="font-bold">问题 {i+1}:</h4>
                <p class="text-gray-700">{question[:100]}...</p>
                <h5 class="font-semibold mt-2">回答:</h5>
                <p class="text-blue-700">{answer[:150]}...</p>
            </div>
            """

        qa_html += '</div>'
        return qa_html

    def _generate_strengths_content(self, personality_type: str, evaluation: Dict) -> str:
        """生成优势分析内容"""
        return f"""
        <div class="prose max-w-none">
            <h3 class="text-xl font-bold mb-4">{personality_type}人格优势分析</h3>
            <div class="bg-green-50 p-4 rounded-lg">
                <h4 class="font-bold mb-2">主要优势：</h4>
                <ul class="list-disc pl-5">
                    <li>基于人格特长的独特视角</li>
                    <li>个性化的思考方式</li>
                    <li>特色的问题解决策略</li>
                </ul>
            </div>
        </div>
        """

    def _generate_suggestions_content(self, personality_type: str, evaluation: Dict) -> str:
        """生成改进建议内容"""
        return f"""
        <div class="prose max-w-none">
            <h3 class="text-xl font-bold mb-4">个性化发展建议</h3>
            <div class="bg-orange-50 p-4 rounded-lg">
                <h4 class="font-bold mb-2">针对{personality_type}的建议：</h4>
                <ul class="list-disc pl-5">
                    <li>发挥人格优势，提升认知能力</li>
                    <li>补强知识短板，完善公民素养</li>
                    <li>实践个性化学习策略</li>
                </ul>
            </div>
        </div>
        """

    def _generate_conclusion_content(self, personality_type: str, evaluation: Dict) -> str:
        """生成结论总结内容"""
        total_score = evaluation.get('overall_score', 0)
        grade = evaluation.get('grade', 'N/A')

        return f"""
        <div class="prose max-w-none">
            <h3 class="text-xl font-bold mb-4">评估结论</h3>
            <div class="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
                <p class="text-lg"><strong>综合评价：</strong></p>
                <p>{personality_type}人格类型在此次公民知识评估中表现{grade}，总评分{total_score}分。</p>
                <p class="mt-4">评估结果体现了该人格类型在认知能力、知识储备和学习潜力等方面的综合特征。</p>
            </div>
        </div>
        """

    def _generate_javascript(self) -> str:
        """生成JavaScript代码"""
        return """
        <script>
        function showTab(tabName) {
            // 隐藏所有标签页内容
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {
                content.classList.remove('active');
            });

            // 移除所有标签页按钮的active状态
            const tabButtons = document.querySelectorAll('.tab');
            tabButtons.forEach(button => {
                button.classList.remove('active');
            });

            // 显示选中的标签页内容
            document.getElementById(tabName).classList.add('active');

            // 添加active状态到点击的标签页按钮
            const activeBtn = document.querySelector(`[onclick="showTab('${tabName}')"]`);
            if (activeBtn) {
                activeBtn.classList.add('active');
            }
        }

        // 页面加载时显示第一个标签页
        document.addEventListener('DOMContentLoaded', function() {
            showTab('overview');
        });
        </script>
        """

    def generate_all_reports(self) -> Dict[str, bool]:
        """为所有已有人格数据生成标准化HTML报告"""
        results = {}

        # 扫描exam目录获取所有人格类型
        personality_files = list(self.exam_dir.glob("*_citizenship_responses.json"))

        print(f"🔍 发现 {len(personality_files)} 个人格回答文件")

        for file_path in personality_files:
            # 从文件名提取人格类型
            personality_type = file_path.stem.replace('_citizenship_responses', '').upper()

            success = self.generate_standard_html_report(personality_type)
            results[personality_type] = success

        return results

def main():
    """主函数"""
    print("🧠 Portable PsyAgent - 标准化HTML报告生成器")
    print("=" * 60)

    generator = StandardHTMLReportGenerator()

    # 检查必要目录
    if not generator.exam_dir.exists():
        print(f"❌ exam目录不存在: {generator.exam_dir}")
        return

    # 生成所有报告
    results = generator.generate_all_reports()

    # 统计结果
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)

    print(f"\n🎉 HTML报告生成完成!")
    print(f"- 总计: {total_count} 个")
    print(f"- 成功: {success_count} 个")
    print(f"- 失败: {total_count - success_count} 个")

    if results:
        print(f"\n📋 生成结果:")
        for personality, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {personality}")

if __name__ == "__main__":
    main()