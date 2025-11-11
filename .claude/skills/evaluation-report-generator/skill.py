#!/usr/bin/env python3
"""
Evaluation Report Generator Skill Implementation
专业评估报告生成器 - 创建交互式HTML报告和数据可视化
"""

import json
import sys
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class EvaluationReportGenerator:
    """评估报告生成器技能实现"""

    def __init__(self):
        """初始化报告生成器"""

        # HTML模板配置
        self.html_template_config = {
            "theme": "professional",
            "primary_color": "#2c3e50",
            "secondary_color": "#3498db",
            "accent_color": "#e74c3c",
            "background_color": "#f8f9fa",
            "text_color": "#2c3e50"
        }

        # 可视化图表配置
        self.chart_config = {
            "radar_chart": {
                "enabled": True,
                "width": 500,
                "height": 500,
                "background_color": "rgba(255, 255, 255, 0.9)"
            },
            "bar_chart": {
                "enabled": True,
                "width": 600,
                "height": 400,
                "bar_colors": ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]
            },
            "progress_bars": {
                "enabled": True,
                "height": 30,
                "border_radius": 15
            }
        }

        # 报告标签页配置
        self.report_tabs = [
            {"id": "overview", "title": "📊 评测概览", "icon": "chart-bar"},
            {"id": "methodology", "title": "🔬 评测方法", "icon": "flask"},
            {"id": "scores", "title": "📈 详细评分", "icon": "analytics"},
            {"id": "qa_analysis", "title": "❓ 问答分析", "icon": "question-answer"},
            {"id": "applications", "title": "🎯 应用场景", "icon": "target"},
            {"id": "comparison", "title": "📊 对比分析", "icon": "comparison"},
            {"id": "recommendations", "title": "📝 结论建议", "icon": "clipboard-check"}
        ]

        # MBTI类型详细描述
        self.mbti_descriptions = {
            "INTJ": {
                "name": "建筑师",
                "description": "战略思考者，具有创新精神和远见",
                "strengths": ["战略思维", "独立性强", "追求卓越", "创新精神"],
                "challenges": ["可能过于理想化", "社交需求低", "可能显得冷漠"],
                "suitable_roles": ["战略规划", "系统架构", "科研开发", "咨询顾问"]
            },
            "INTP": {
                "name": "逻辑学家",
                "description": "理论探索者，追求知识和理解",
                "strengths": ["逻辑分析", "好奇心强", "创新思维", "客观理性"],
                "challenges": ["行动力不足", "社交能力有限", "拖延倾向"],
                "suitable_roles": ["科学研究", "技术开发", "学术研究", "分析咨询"]
            },
            "ENTJ": {
                "name": "指挥官",
                "description": "天生的领导者，追求目标和成就",
                "strengths": ["领导能力", "目标导向", "决策果断", "组织协调"],
                "challenges": ["可能过于强势", "耐心不足", "可能忽视他人感受"],
                "suitable_roles": ["企业管理", "项目领导", "创业", "战略咨询"]
            },
            "ENTP": {
                "name": "辩论家",
                "description": "创新挑战者，追求可能性和变化",
                "strengths": ["创新思维", "辩论能力", "适应性强", "思维敏捷"],
                "challenges": ["注意力分散", "执行力不足", "可能缺乏专注"],
                "suitable_roles": ["产品开发", "市场营销", "创业投资", "创意咨询"]
            },
            "INFJ": {
                "name": "提倡者",
                "description": "理想主义者，追求意义和价值",
                "strengths": ["同理心强", "理想主义", "洞察力", "创造力"],
                "challenges": ["可能过于理想化", "容易受到伤害", "完美主义"],
                "suitable_roles": ["心理咨询", "教育科研", "非营利组织", "文化创意"]
            },
            "INFP": {
                "name": "调停者",
                "description": "理想主义者，追求和谐和创意",
                "strengths": ["创造力强", "同理心", "价值观坚定", "适应性强"],
                "challenges": ["决策困难", "避免冲突", "执行力不足"],
                "suitable_roles": ["艺术创作", "写作编辑", "心理咨询", "教育研究"]
            },
            "ENFJ": {
                "name": "主人公",
                "description": "鼓舞人心者，追求他人成长",
                "strengths": ["人际魅力", "同理心", "领导能力", "激励他人"],
                "challenges": ["可能忽视自己", "容易情绪化", "完美主义"],
                "suitable_roles": ["教育培训", "人力资源", "咨询服务", "公共关系"]
            },
            "ENFP": {
                "name": "竞选者",
                "description": "热情洋溢者，追求自由和可能性",
                "strengths": ["热情乐观", "创造力", "社交能力", "适应性强"],
                "challenges": ["注意力分散", "决策困难", "容易情绪化"],
                "suitable_roles": ["媒体传播", "市场营销", "创意设计", "公共关系"]
            },
            "ISTJ": {
                "name": "物流师",
                "description": "务实的组织者，追求秩序和传统",
                "strengths": ["责任感强", "组织能力", "可靠性", "注重细节"],
                "challenges": ["变化适应慢", "可能过于保守", "缺乏灵活性"],
                "suitable_roles": ["财务管理", "项目管理", "质量控制", "法律咨询"]
            },
            "ISFJ": {
                "name": "守护者",
                "description": "温暖的保护者，追求和谐和服务",
                "strengths": ["关怀他人", "责任感", "耐心细致", "忠诚可靠"],
                "challenges": ["避免冲突", "变化适应慢", "可能忽视自己"],
                "suitable_roles": ["医疗护理", "教育培训", "客户服务", "行政支持"]
            },
            "ESTJ": {
                "name": "总经理",
                "description": "高效的管理者，追求结果和秩序",
                "strengths": ["组织能力", "执行力", "决策果断", "责任心强"],
                "challenges": ["可能过于强势", "灵活性不足", "可能忽视感受"],
                "suitable_roles": ["企业管理", "项目管理", "运营管理", "财务分析"]
            },
            "ESFJ": {
                "name": "执政官",
                "description": "热心的支持者，追求和谐和合作",
                "strengths": ["人际能力", "组织能力", "责任感", "服务精神"],
                "challenges": ["可能过分在意他人", "避免冲突", "决策困难"],
                "suitable_roles": ["人力资源", "客户服务", "教育培训", "销售管理"]
            },
            "ISTP": {
                "name": "鉴赏家",
                "description": "灵活的实践者，追求实用和技能",
                "strengths": ["实践能力", "适应性强", "冷静理性", "问题解决"],
                "challenges": ["长期规划不足", "表达能力有限", "可能显得冷漠"],
                "suitable_roles": ["技术操作", "工程维护", "体育运动", "手工艺"]
            },
            "ISFP": {
                "name": "探险家",
                "description": "艺术的创作者，追求美学和价值",
                "strengths": ["艺术天赋", "敏感度", "价值观坚定", "适应性强"],
                "challenges": ["自信不足", "避免冲突", "执行力有限"],
                "suitable_roles": ["艺术设计", "音乐创作", "摄影摄像", "美容美发"]
            },
            "ESTP": {
                "name": "企业家",
                "description": "精力充沛的行动者，追求行动和结果",
                "strengths": ["行动力强", "适应能力", "社交能力", "问题解决"],
                "challenges": ["缺乏长期规划", "容易冲动", "耐心不足"],
                "suitable_roles": ["销售营销", "体育教练", "活动策划", "创业经营"]
            },
            "ESFP": {
                "name": "娱乐家",
                "description": "活泼的开朗者，追求快乐和体验",
                "strengths": ["热情开朗", "社交能力", "适应性强", "乐观积极"],
                "challenges": ["注意力分散", "缺乏规划", "容易情绪化"],
                "suitable_roles": ["娱乐演艺", "活动策划", "客户服务", "旅游导游"]
            }
        }

    def generate_comprehensive_report(self, evaluation_data: Dict[str, Any],
                                    output_file: str = None,
                                    template_style: str = "professional") -> str:
        """
        生成综合HTML评估报告

        Args:
            evaluation_data: 评估数据
            output_file: 输出文件路径
            template_style: 模板风格

        Returns:
            生成的HTML文件路径
        """

        # 生成文件名
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = evaluation_data.get("session_info", {}).get("session_id", "unknown")
            persona = evaluation_data.get("assessment_metadata", {}).get("persona", "unknown")
            output_file = f"html/{persona}_assessment_report_{timestamp}.html"

        # 生成HTML内容
        html_content = self._build_html_report(evaluation_data, template_style)

        # 保存文件
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_path.absolute())

    def _build_html_report(self, data: Dict[str, Any], template_style: str) -> str:
        """构建完整的HTML报告"""

        # 获取关键数据
        session_info = data.get("session_info", {})
        big_five_results = data.get("big_five_results", {})
        mbti_analysis = data.get("mbti_analysis", {})
        belbin_roles = data.get("belbin_team_roles", {})
        recommendations = data.get("recommendations", [])
        question_details = data.get("question_details", [])

        # 构建HTML页面
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>心理评估报告 - {mbti_analysis.get('mbti_type', 'Unknown')}</title>
    {self._build_css_styles()}
    {self._build_javascript()}
</head>
<body>
    <div class="container">
        {self._build_header(session_info, mbti_analysis)}
        {self._build_navigation_tabs()}
        {self._build_overview_tab(data)}
        {self._build_methodology_tab(data)}
        {self._build_scores_tab(big_five_results)}
        {self._build_qa_analysis_tab(question_details)}
        {self._build_applications_tab(mbti_analysis, belbin_roles)}
        {self._build_comparison_tab(data)}
        {self._build_recommendations_tab(recommendations)}
        {self._build_footer()}
    </div>
</body>
</html>"""

        return html

    def _build_css_styles(self) -> str:
        """构建CSS样式"""

        return """
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 20px;
    }

    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }

    .header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 40px;
        text-align: center;
    }

    .header h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        font-weight: 300;
    }

    .header .subtitle {
        font-size: 1.2em;
        opacity: 0.9;
        margin-bottom: 20px;
    }

    .header .meta-info {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 20px;
    }

    .meta-item {
        text-align: center;
    }

    .meta-item .label {
        font-size: 0.9em;
        opacity: 0.8;
        margin-bottom: 5px;
    }

    .meta-item .value {
        font-size: 1.1em;
        font-weight: bold;
    }

    .navigation {
        display: flex;
        background: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        overflow-x: auto;
    }

    .nav-tab {
        padding: 15px 25px;
        cursor: pointer;
        border: none;
        background: none;
        font-size: 1em;
        transition: all 0.3s ease;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .nav-tab:hover {
        background: #e9ecef;
    }

    .nav-tab.active {
        background: #3498db;
        color: white;
        border-bottom: 3px solid #2c3e50;
    }

    .tab-content {
        display: none;
        padding: 40px;
        animation: fadeIn 0.5s ease;
    }

    .tab-content.active {
        display: block;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .score-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 30px;
        margin: 30px 0;
    }

    .score-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .score-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }

    .score-card h3 {
        color: #2c3e50;
        margin-bottom: 15px;
        font-size: 1.3em;
    }

    .score-value {
        font-size: 3em;
        font-weight: bold;
        color: #3498db;
        margin: 10px 0;
    }

    .score-label {
        color: #7f8c8d;
        font-size: 0.9em;
        margin-bottom: 15px;
    }

    .progress-bar {
        width: 100%;
        height: 10px;
        background: #ecf0f1;
        border-radius: 5px;
        overflow: hidden;
        margin: 15px 0;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        border-radius: 5px;
        transition: width 1s ease;
    }

    .radar-chart-container {
        width: 100%;
        max-width: 500px;
        margin: 30px auto;
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .qa-item {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #3498db;
    }

    .qa-item .question {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }

    .qa-item .response {
        color: #34495e;
        line-height: 1.6;
        margin-bottom: 10px;
    }

    .qa-item .scores {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin-top: 10px;
    }

    .score-badge {
        background: #3498db;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.9em;
    }

    .mbti-profile {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        text-align: center;
    }

    .mbti-profile h2 {
        font-size: 2em;
        margin-bottom: 10px;
    }

    .mbti-profile .type-code {
        font-size: 3em;
        font-weight: bold;
        margin: 20px 0;
    }

    .mbti-profile .description {
        font-size: 1.1em;
        opacity: 0.9;
        margin-bottom: 30px;
    }

    .traits-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }

    .trait-item {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }

    .trait-item h4 {
        margin-bottom: 10px;
        color: #fff;
    }

    .trait-item ul {
        list-style: none;
        padding: 0;
    }

    .trait-item li {
        margin: 5px 0;
        opacity: 0.9;
    }

    .recommendation-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2ecc71;
    }

    .recommendation-card h4 {
        color: #2c3e50;
        margin-bottom: 10px;
    }

    .recommendation-card .category {
        display: inline-block;
        background: #3498db;
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        margin-bottom: 10px;
    }

    .filter-controls {
        display: flex;
        gap: 15px;
        margin: 20px 0;
        flex-wrap: wrap;
    }

    .filter-controls input, .filter-controls select {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 1em;
    }

    .filter-controls button {
        padding: 10px 20px;
        background: #3498db;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1em;
        transition: background 0.3s ease;
    }

    .filter-controls button:hover {
        background: #2980b9;
    }

    .footer {
        background: #2c3e50;
        color: white;
        text-align: center;
        padding: 30px;
        margin-top: 40px;
    }

    .footer .links {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 15px;
    }

    .footer .links a {
        color: #3498db;
        text-decoration: none;
        transition: color 0.3s ease;
    }

    .footer .links a:hover {
        color: #5dade2;
    }

    @media (max-width: 768px) {
        .container {
            margin: 10px;
            border-radius: 10px;
        }

        .header {
            padding: 20px;
        }

        .header h1 {
            font-size: 1.8em;
        }

        .header .meta-info {
            flex-direction: column;
            gap: 15px;
        }

        .navigation {
            flex-direction: column;
        }

        .nav-tab {
            width: 100%;
            text-align: center;
        }

        .tab-content {
            padding: 20px;
        }

        .score-grid {
            grid-template-columns: 1fr;
        }

        .traits-grid {
            grid-template-columns: 1fr;
        }
    }
</style>"""

    def _build_javascript(self) -> str:
        """构建JavaScript功能"""

        return """
<script>
    // 标签页切换功能
    function initTabs() {
        const tabs = document.querySelectorAll('.nav-tab');
        const contents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.getAttribute('data-tab');

                // 移除所有active类
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));

                // 添加active类到当前标签
                tab.classList.add('active');
                const targetContent = document.getElementById(targetId);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });

        // 默认激活第一个标签
        if (tabs.length > 0) {
            tabs[0].click();
        }
    }

    // 进度条动画
    function animateProgressBars() {
        const progressFills = document.querySelectorAll('.progress-fill');
        progressFills.forEach(fill => {
            const width = fill.getAttribute('data-width');
            if (width) {
                setTimeout(() => {
                    fill.style.width = width;
                }, 100);
            }
        });
    }

    // 雷达图绘制
    function drawRadarChart() {
        const canvas = document.getElementById('radarChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 40;

        // 数据
        const data = {
            labels: ['开放性', '尽责性', '外向性', '宜人性', '神经质'],
            values: canvas.dataset.values ? canvas.dataset.values.split(',').map(Number) : [3, 3, 3, 3, 3]
        };

        // 清空画布
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 绘制网格
        for (let i = 1; i <= 5; i++) {
            ctx.beginPath();
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 1;

            for (let j = 0; j < data.labels.length; j++) {
                const angle = (Math.PI * 2 * j) / data.labels.length - Math.PI / 2;
                const x = centerX + Math.cos(angle) * (radius * i / 5);
                const y = centerY + Math.sin(angle) * (radius * i / 5);

                if (j === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();
            ctx.stroke();
        }

        // 绘制轴线
        for (let i = 0; i < data.labels.length; i++) {
            const angle = (Math.PI * 2 * i) / data.labels.length - Math.PI / 2;
            ctx.beginPath();
            ctx.strokeStyle = '#ccc';
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(
                centerX + Math.cos(angle) * radius,
                centerY + Math.sin(angle) * radius
            );
            ctx.stroke();

            // 绘制标签
            ctx.fillStyle = '#333';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            const labelX = centerX + Math.cos(angle) * (radius + 25);
            const labelY = centerY + Math.sin(angle) * (radius + 25);
            ctx.fillText(data.labels[i], labelX, labelY);
        }

        // 绘制数据区域
        ctx.beginPath();
        ctx.fillStyle = 'rgba(52, 152, 219, 0.3)';
        ctx.strokeStyle = '#3498db';
        ctx.lineWidth = 2;

        for (let i = 0; i < data.values.length; i++) {
            const angle = (Math.PI * 2 * i) / data.values.length - Math.PI / 2;
            const value = data.values[i] / 5; // 标准化到0-1
            const x = centerX + Math.cos(angle) * (radius * value);
            const y = centerY + Math.sin(angle) * (radius * value);

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }

        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // 绘制数据点
        for (let i = 0; i < data.values.length; i++) {
            const angle = (Math.PI * 2 * i) / data.values.length - Math.PI / 2;
            const value = data.values[i] / 5;
            const x = centerX + Math.cos(angle) * (radius * value);
            const y = centerY + Math.sin(angle) * (radius * value);

            ctx.beginPath();
            ctx.fillStyle = '#3498db';
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // 问答过滤功能
    function initQAFilter() {
        const searchInput = document.getElementById('qaSearch');
        const dimensionFilter = document.getElementById('dimensionFilter');
        const qaItems = document.querySelectorAll('.qa-item');

        function filterQA() {
            const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
            const selectedDimension = dimensionFilter ? dimensionFilter.value : '';

            qaItems.forEach(item => {
                const question = item.querySelector('.question').textContent.toLowerCase();
                const response = item.querySelector('.response').textContent.toLowerCase();
                const scores = item.getAttribute('data-dimensions') || '';

                const matchesSearch = question.includes(searchTerm) || response.includes(searchTerm);
                const matchesDimension = selectedDimension === '' || scores.includes(selectedDimension);

                if (matchesSearch && matchesDimension) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        if (searchInput) searchInput.addEventListener('input', filterQA);
        if (dimensionFilter) dimensionFilter.addEventListener('change', filterQA);
    }

    // 页面加载完成后初始化
    document.addEventListener('DOMContentLoaded', () => {
        initTabs();
        animateProgressBars();
        setTimeout(drawRadarChart, 500);
        initQAFilter();
    });

    // 窗口大小改变时重绘图表
    window.addEventListener('resize', () => {
        setTimeout(drawRadarChart, 100);
    });
</script>"""

    def _build_header(self, session_info: Dict, mbti_analysis: Dict) -> str:
        """构建页面头部"""

        mbti_type = mbti_analysis.get('mbti_type', 'Unknown')
        mbti_desc = self.mbti_descriptions.get(mbti_type, {})
        mbti_name = mbti_desc.get('name', '未知类型')

        evaluation_date = session_info.get('evaluation_date', datetime.now().isoformat())
        formatted_date = evaluation_date.split('T')[0] if 'T' in evaluation_date else evaluation_date

        return f"""
        <div class="header">
            <h1>心理评估报告</h1>
            <div class="subtitle">{mbti_name} ({mbti_type}) - 专业心理分析</div>

            <div class="meta-info">
                <div class="meta-item">
                    <div class="label">评估日期</div>
                    <div class="value">{formatted_date}</div>
                </div>
                <div class="meta-item">
                    <div class="label">会话编号</div>
                    <div class="value">{session_info.get('session_id', 'N/A')}</div>
                </div>
                <div class="meta-item">
                    <div class="label">评估题目</div>
                    <div class="value">{session_info.get('total_questions', 0)} 道</div>
                </div>
                <div class="meta-item">
                    <div class="label">MBTI类型</div>
                    <div class="value">{mbti_type}</div>
                </div>
            </div>
        </div>"""

    def _build_navigation_tabs(self) -> str:
        """构建导航标签"""

        tabs_html = '<div class="navigation">'
        for tab in self.report_tabs:
            tabs_html += f'<button class="nav-tab" data-tab="{tab["id"]}">{tab["title"]}</button>'
        tabs_html += '</div>'

        return tabs_html

    def _build_overview_tab(self, data: Dict) -> str:
        """构建概览标签页"""

        session_info = data.get("session_info", {})
        big_five_results = data.get("big_five_results", {})
        mbti_analysis = data.get("mbti_analysis", {})
        belbin_roles = data.get("belbin_team_roles", {})
        quality_metrics = data.get("quality_metrics", {})

        final_scores = big_five_results.get("final_scores", {})
        score_analysis = big_five_results.get("score_analysis", {})

        mbti_type = mbti_analysis.get('mbti_type', 'Unknown')
        mbti_desc = self.mbti_descriptions.get(mbti_type, {})

        # 构建评分卡片
        score_cards = ""
        for dimension, score in final_scores.items():
            dim_name = self._get_dimension_name(dimension)
            score_level = score_analysis.get(dimension, {}).get('level_label', '中等')

            score_cards += f"""
            <div class="score-card">
                <h3>{dim_name}</h3>
                <div class="score-value">{score:.1f}</div>
                <div class="score-label">{score_level}</div>
                <div class="progress-bar">
                    <div class="progress-fill" data-width="{score * 20}%"></div>
                </div>
            </div>"""

        # 构建雷达图数据
        radar_data = ','.join([str(final_scores.get(dim, 3.0)) for dim in ['O', 'C', 'E', 'A', 'N']])

        return f"""
        <div id="overview" class="tab-content">
            <h2>评估概览</h2>

            <div class="mbti-profile">
                <h2>您的MBTI类型</h2>
                <div class="type-code">{mbti_type}</div>
                <div class="description">{mbti_desc.get('description', '未知类型描述')}</div>
            </div>

            <div class="score-grid">
                {score_cards}
            </div>

            <div class="radar-chart-container">
                <h3>大五人格雷达图</h3>
                <canvas id="radarChart" width="500" height="500" data-values="{radar_data}"></canvas>
            </div>

            <div class="score-grid">
                <div class="score-card">
                    <h3>主要团队角色</h3>
                    <div class="score-value">{belbin_roles.get('primary_role_name', '未确定')}</div>
                    <div class="score-label">贝尔宾团队角色</div>
                </div>
                <div class="score-card">
                    <h3>评估置信度</h3>
                    <div class="score-value">{quality_metrics.get('evaluation_confidence', 0.8):.1%}</div>
                    <div class="score-label">整体评估可信度</div>
                </div>
                <div class="score-card">
                    <h3>回答一致性</h3>
                    <div class="score-value">{quality_metrics.get('response_consistency', 0.8):.1%}</div>
                    <div class="score-label">回答模式一致性</div>
                </div>
            </div>
        </div>"""

    def _build_methodology_tab(self, data: Dict) -> str:
        """构建方法论标签页"""

        return f"""
        <div id="methodology" class="tab-content">
            <h2>评测方法与标准</h2>

            <div class="score-card">
                <h3>Big Five 大五人格模型</h3>
                <p>大五人格模型是现代心理学中最权威的人格理论之一，通过五个核心维度来描述个体的人格特征：</p>
                <ul>
                    <li><strong>开放性 (Openness)</strong>：对新体验、艺术、情感、冒险、不寻常想法的开放程度</li>
                    <li><strong>尽责性 (Conscientiousness)</strong>：组织性、勤奋性、可靠性、自律性</li>
                    <li><strong>外向性 (Extraversion)</strong>：社交性、果断性、活跃度、积极情绪</li>
                    <li><strong>宜人性 (Agreeableness)</strong>：信任、直率、利他、顺从、谦虚、同理心</li>
                    <li><strong>神经质 (Neuroticism)</strong>：焦虑、愤怒、抑郁、自我意识、冲动、脆弱性</li>
                </ul>
            </div>

            <div class="score-card">
                <h3>MBTI 类型推断</h3>
                <p>基于大五人格评分，通过专业的映射算法推断出最符合的MBTI人格类型：</p>
                <ul>
                    <li><strong>E/I维度</strong>：基于外向性评分</li>
                    <li><strong>S/N维度</strong>：基于开放性评分</li>
                    <li><strong>T/F维度</strong>：基于宜人性评分</li>
                    <li><strong>J/P维度</strong>：基于尽责性评分</li>
                </ul>
            </div>

            <div class="score-card">
                <h3>评分标准</h3>
                <p>采用5分制评分体系，每个分数对应的百分位数：</p>
                <ul>
                    <li><strong>1分 (非常低)</strong>：&lt; 5% 分位数</li>
                    <li><strong>2分 (较低)</strong>：5-25% 分位数</li>
                    <li><strong>3分 (中等)</strong>：25-75% 分位数</li>
                    <li><strong>4分 (较高)</strong>：75-95% 分位数</li>
                    <li><strong>5分 (非常高)</strong>：&gt; 95% 分位数</li>
                </ul>
            </div>

            <div class="score-card">
                <h3>评估流程</h3>
                <ol>
                    <li>收集问卷回答数据</li>
                    <li>分析问题所属的大五维度</li>
                    <li>基于专家标准进行评分</li>
                    <li>计算各维度平均分</li>
                    <li>推断MBTI类型和团队角色</li>
                    <li>生成个性化建议和报告</li>
                </ol>
            </div>
        </div>"""

    def _build_scores_tab(self, big_five_results: Dict) -> str:
        """构建详细评分标签页"""

        final_scores = big_five_results.get("final_scores", {})
        score_analysis = big_five_results.get("score_analysis", {})
        dimension_profiles = big_five_results.get("dimension_profiles", {})

        tabs_html = ""
        for dimension in ["O", "C", "E", "A", "N"]:
            dim_name = self._get_dimension_name(dimension)
            profile = dimension_profiles.get(dimension, {})
            analysis = score_analysis.get(dimension, {})

            tabs_html += f"""
            <div class="score-card">
                <h3>{dim_name} - 详细分析</h3>
                <div class="score-value">{final_scores.get(dimension, 3.0):.1f}</div>
                <div class="score-label">{analysis.get('level_label', '中等')} ({analysis.get('percentile_range', '25-75%')})</div>

                <p><strong>维度描述：</strong>{profile.get('description', '')}</p>

                <div class="progress-bar">
                    <div class="progress-fill" data-width="{final_scores.get(dimension, 3.0) * 20}%"></div>
                </div>

                <p><strong>详细分析：</strong>{profile.get('detailed_analysis', '')}</p>

                <p><strong>表现特质：</strong></p>
                <ul>
                    {''.join([f'<li>{trait}</li>' for trait in profile.get('displayed_traits', [])])}
                </ul>

                <p><strong>个体评分：</strong>{analysis.get('individual_scores', [])}</p>
                <p><strong>评分一致性：</strong>{analysis.get('score_consistency', 0):.3f}</p>
            </div>"""

        return f"""
        <div id="scores" class="tab-content">
            <h2>详细评分分析</h2>
            <div class="score-grid">
                {tabs_html}
            </div>
        </div>"""

    def _build_qa_analysis_tab(self, question_details: List) -> str:
        """构建问答分析标签页"""

        # 构建过滤控件
        filter_html = """
        <div class="filter-controls">
            <input type="text" id="qaSearch" placeholder="搜索问题或回答...">
            <select id="dimensionFilter">
                <option value="">所有维度</option>
                <option value="O">开放性</option>
                <option value="C">尽责性</option>
                <option value="E">外向性</option>
                <option value="A">宜人性</option>
                <option value="N">神经质</option>
            </select>
            <button onclick="initQAFilter()">筛选</button>
        </div>"""

        # 构建问答项目
        qa_items = ""
        for i, qa in enumerate(question_details[:20]):  # 限制显示前20个
            question = qa.get("question", "")
            response = qa.get("response", "")
            scores = qa.get("scores", {})
            primary_dimension = qa.get("primary_dimension", "")

            # 构建分数徽章
            score_badges = ""
            for dim, score in scores.items():
                dim_name = self._get_dimension_name(dim)
                score_badges += f'<span class="score-badge">{dim_name}: {score}</span>'

            qa_items += f"""
            <div class="qa-item" data-dimensions="{','.join(scores.keys())}">
                <div class="question">问题 {i+1}: {question}</div>
                <div class="response">回答: {response}</div>
                <div class="scores">{score_badges}</div>
            </div>"""

        return f"""
        <div id="qa_analysis" class="tab-content">
            <h2>问答分析</h2>
            {filter_html}
            <div class="qa-list">
                {qa_items}
            </div>
            {f'<p><em>显示前20个问题，总共{len(question_details)}个问题</em></p>' if len(question_details) > 20 else ''}
        </div>"""

    def _build_applications_tab(self, mbti_analysis: Dict, belbin_roles: Dict) -> str:
        """构建应用场景标签页"""

        mbti_type = mbti_analysis.get('mbti_type', 'Unknown')
        mbti_desc = self.mbti_descriptions.get(mbti_type, {})

        # 构建优势特质
        strengths_html = "".join([f'<li>{strength}</li>' for strength in mbti_desc.get('strengths', [])])
        challenges_html = "".join([f'<li>{challenge}</li>' for challenge in mbti_desc.get('challenges', [])])
        roles_html = "".join([f'<li>{role}</li>' for role in mbti_desc.get('suitable_roles', [])])

        return f"""
        <div id="applications" class="tab-content">
            <h2>应用场景分析</h2>

            <div class="traits-grid">
                <div class="trait-item">
                    <h4>💪 核心优势</h4>
                    <ul>{strength_html}</ul>
                </div>

                <div class="trait-item">
                    <h4>⚠️ 发展领域</h4>
                    <ul>{challenges_html}</ul>
                </div>

                <div class="trait-item">
                    <h4>💼 适合角色</h4>
                    <ul>{roles_html}</ul>
                </div>

                <div class="trait-item">
                    <h4>👥 团队角色</h4>
                    <p><strong>主要角色：</strong>{belbin_roles.get('primary_role_name', '未确定')}</p>
                    <p><strong>匹配度：</strong>{belbin_roles.get('primary_role_score', 0):.1f}</p>
                </div>
            </div>

            <div class="score-card">
                <h3>职业发展建议</h3>
                <p>基于您的{mbti_type}人格类型，建议在职业选择中考虑以下因素：</p>
                <ul>
                    <li>选择能够发挥您核心优势的工作环境</li>
                    <li>寻找与您价值观相匹配的组织文化</li>
                    <li>在需要发展特质的领域适当挑战自己</li>
                    <li>建立能够支持您特质的工作习惯</li>
                    <li>寻找能够互补的合作伙伴</li>
                </ul>
            </div>

            <div class="score-card">
                <h3>人际关系建议</h3>
                <p>在人际交往中，建议您：</p>
                <ul>
                    <li>发挥您的{mbti_desc.get('strengths', [''])[0] if mbti_desc.get('strengths') else '优势'}来建立良好关系</li>
                    <li>意识到并管理您的{mbti_desc.get('challenges', [''])[0] if mbti_desc.get('challenges') else '挑战'}</li>
                    <li>选择与您性格相匹配的社交环境</li>
                    <li>学习有效的沟通和冲突解决技巧</li>
                </ul>
            </div>
        </div>"""

    def _build_comparison_tab(self, data: Dict) -> str:
        """构建对比分析标签页"""

        final_scores = data.get("big_five_results", {}).get("final_scores", {})

        # 构建与常模的对比
        norm_comparison = """
        <div class="score-card">
            <h3>与常模群体对比</h3>
            <p>您的评分与普通人群的对比：</p>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px;">维度</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">您的分数</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">人群平均</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">相对位置</th>
                </tr>"""

        avg_scores = {"O": 3.0, "C": 3.0, "E": 3.0, "A": 3.5, "N": 2.8}  # 假设的常模平均值

        for dimension in ["O", "C", "E", "A", "N"]:
            your_score = final_scores.get(dimension, 3.0)
            avg_score = avg_scores.get(dimension, 3.0)
            difference = your_score - avg_score

            if difference > 0.5:
                position = "显著高于平均"
                color = "#2ecc71"
            elif difference < -0.5:
                position = "显著低于平均"
                color = "#e74c3c"
            else:
                position = "接近平均水平"
                color = "#f39c12"

            norm_comparison += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">{self._get_dimension_name(dimension)}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{your_score:.1f}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{avg_score:.1f}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; color: {color};">{position}</td>
                </tr>"""

        norm_comparison += "</table></div>"

        return f"""
        <div id="comparison" class="tab-content">
            <h2>对比分析</h2>

            {norm_comparison}

            <div class="score-card">
                <h3>人格特征平衡性分析</h3>
                <p>您的人格特征在以下方面的平衡性：</p>
                <ul>
                    <li><strong>理性vs感性：</strong>{'偏向理性' if final_scores.get('A', 3.0) < 3.0 else '偏向感性'}</li>
                    <li><strong>内向vs外向：</strong>{'偏向外向' if final_scores.get('E', 3.0) > 3.0 else '偏向内向'}</li>
                    <li><strong>创新vs传统：</strong>{'偏向创新' if final_scores.get('O', 3.0) > 3.0 else '偏向传统'}</li>
                    <li><strong>灵活vs有序：</strong>{'偏向灵活' if final_scores.get('C', 3.0) < 3.0 else '偏向有序'}</li>
                    <li><strong>稳定vs敏感：</strong>{'偏向稳定' if final_scores.get('N', 3.0) < 3.0 else '偏向敏感'}</li>
                </ul>
            </div>
        </div>"""

    def _build_recommendations_tab(self, recommendations: List) -> str:
        """构建建议标签页"""

        rec_html = ""
        for rec in recommendations:
            category = rec.get('category', '建议')
            title = rec.get('title', '')
            content = rec.get('content', '')

            rec_html += f"""
            <div class="recommendation-card">
                <span class="category">{category}</span>
                <h4>{title}</h4>
                <p>{content}</p>
            </div>"""

        return f"""
        <div id="recommendations" class="tab-content">
            <h2>结论与建议</h2>

            <div class="score-card">
                <h3>总体评估</h3>
                <p>基于完整的心理评估分析，我们为您提供了以下专业建议，帮助您更好地了解自己并发挥潜力。</p>
            </div>

            {rec_html}

            <div class="score-card">
                <h3>后续发展建议</h3>
                <ol>
                    <li>定期进行自我反思，关注个人成长</li>
                    <li>在优势领域继续深化发展</li>
                    <li>有意识地改进需要发展的方面</li>
                    <li>寻找合适的导师和成长环境</li>
                    <li>保持开放和成长的心态</li>
                </ol>
            </div>
        </div>"""

    def _build_footer(self) -> str:
        """构建页面底部"""

        return """
        <div class="footer">
            <p>© 2025 AI人格实验室 - 专业心理评估系统</p>
            <p>本报告基于科学的心理学理论和方法生成，仅供个人参考和发展使用</p>
            <div class="links">
                <a href="https://cn.agentpsy.com" target="_blank">AI人格实验室</a>
                <a href="#" onclick="window.print()">打印报告</a>
                <a href="#" onclick="alert('报告导出功能开发中')">导出PDF</a>
            </div>
        </div>"""

    def _get_dimension_name(self, dimension: str) -> str:
        """获取维度中文名称"""

        dimension_names = {
            "O": "开放性",
            "C": "尽责性",
            "E": "外向性",
            "A": "宜人性",
            "N": "神经质"
        }

        return dimension_names.get(dimension.upper(), dimension)

    def save_report_html(self, html_content: str, output_file: str) -> bool:
        """保存HTML报告"""

        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return True

        except Exception as e:
            print(f"保存HTML报告失败: {e}")
            return False


def main():
    """主函数 - 命令行接口"""

    if len(sys.argv) < 3:
        print("用法: python skill.py <命令> <参数...>")
        print("命令:")
        print("  generate <评估数据文件> - 生成HTML报告")
        print("  help - 显示帮助信息")
        return

    command = sys.argv[1]
    generator = EvaluationReportGenerator()

    if command == "generate":
        try:
            data_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            template_style = sys.argv[4] if len(sys.argv) > 4 else "professional"

            with open(data_file, 'r', encoding='utf-8') as f:
                evaluation_data = json.load(f)

            result_file = generator.generate_comprehensive_report(
                evaluation_data,
                output_file,
                template_style
            )

            print(f"✅ HTML报告生成完成")
            print(f"📄 报告文件: {result_file}")

        except Exception as e:
            print(f"❌ 生成失败: {e}")

    elif command == "help":
        print("""
评估报告生成器技能使用说明：

1. 生成HTML报告：
   python skill.py generate <评估数据.json> [输出文件.html] [模板风格]

2. 支持的模板风格：
   - professional: 专业风格（默认）
   - modern: 现代风格
   - minimal: 简约风格

3. 评估数据格式要求：
   - session_info: 会话信息
   - big_five_results: 大五人格结果
   - mbti_analysis: MBTI分析结果
   - belbin_team_roles: 贝尔宾团队角色
   - recommendations: 建议列表
   - question_details: 问答详情

示例：
python skill.py generate evaluation_result.json report.html professional
        """)

    else:
        print(f"❌ 未知命令: {command}")


if __name__ == "__main__":
    main()