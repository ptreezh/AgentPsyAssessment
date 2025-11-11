#!/usr/bin/env python3
"""
增强版HTML报告生成技能

专业的HTML格式认知压力测评报告生成器
支持品牌化设计、响应式布局、测试模型信息、压力上下文介绍和logo集成
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64

class EnhancedHtmlReportGeneratorSkill:
    """增强版HTML报告生成技能"""

    def __init__(self):
        self.skill_name = "enhanced-html-report-generator"
        self.skill_version = "2.0.0"
        self.brand_url = "https://cn.agentpsy.com"
        self.brand_name = "AI人格实验室"

    def generate_html_report(self,
                           report_data: Dict[str, Any],
                           output_filename: Optional[str] = None,
                           report_title: str = "认知压力测评报告") -> Dict[str, Any]:
        """
        生成专业的增强版HTML格式报告

        Args:
            report_data: 报告数据字典
            output_filename: 输出文件名（可选）
            report_title: 报告标题

        Returns:
            生成结果字典
        """
        print(f"📄 开始生成增强版HTML报告: {report_title}")

        try:
            # 生成HTML内容
            html_content = self._build_html_report(report_data, report_title)

            # 确定输出文件名
            if not output_filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"html/enhanced_cognitive_stress_report_{timestamp}.html"

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)

            # 保存HTML文件
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            result = {
                'success': True,
                'output_file': output_filename,
                'file_size': len(html_content),
                'generation_time': datetime.now().isoformat(),
                'report_title': report_title
            }

            print(f"✅ 增强版HTML报告生成成功!")
            print(f"📁 文件位置: {output_filename}")
            print(f"📊 文件大小: {len(html_content):,} 字符")

            return result

        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'generation_time': datetime.now().isoformat()
            }

            print(f"❌ 增强版HTML报告生成失败: {e}")
            return error_result

    def _build_html_report(self, report_data: Dict[str, Any], report_title: str) -> str:
        """构建完整的HTML报告"""
        # 生成各部分HTML
        header_html = self._generate_header(report_data, report_title)
        overview_html = self._generate_overview_section(report_data)
        model_info_html = self._generate_model_info_section(report_data)
        stress_context_html = self._generate_stress_context_section(report_data)
        conditions_html = self._generate_conditions_section(report_data)
        summary_html = self._generate_summary_section(report_data)
        footer_html = self._generate_footer(report_data)

        # 组装完整HTML
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>
        {self._generate_css()}
    </style>
</head>
<body>
    {header_html}
    <main class="container">
        {overview_html}
        {model_info_html}
        {stress_context_html}
        {conditions_html}
        {summary_html}
    </main>
    {footer_html}
    <script>
        {self._generate_javascript()}
    </script>
</body>
</html>"""

        return html_content

    def _generate_header(self, report_data: Dict[str, Any], report_title: str) -> str:
        """生成报告头部"""
        brand_info = report_data.get('brand_info', {})
        company_name = brand_info.get('company_name', self.brand_name)
        website = brand_info.get('website', self.brand_url)

        # 获取当前时间
        current_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')

        return f"""
        <header class="header">
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-placeholder">
                        <i class="fas fa-brain"></i>
                        <span>LOGO</span>
                    </div>
                    <div class="brand-info">
                        <h1 class="company-name">{company_name}</h1>
                        <p class="tagline">专业的AI人格与行为评估平台</p>
                    </div>
                </div>
                <div class="report-info">
                    <h1 class="report-title">{report_title}</h1>
                    <p class="generation-time">生成时间: {current_time}</p>
                </div>
            </div>
        </header>"""

    def _generate_overview_section(self, report_data: Dict[str, Any]) -> str:
        """生成概览部分"""
        title = report_data.get('title', '认知压力测评报告')
        subtitle = report_data.get('subtitle', '四种认知干扰条件下的人格表现对比分析')
        test_info = report_data.get('test_info', {})

        total_questions = test_info.get('total_questions', '50')
        scale = test_info.get('scale', 'IPIP-FFM-50 完整量表')
        test_date = test_info.get('test_date', datetime.now().strftime('%Y-%m-%d'))

        conditions = report_data.get('conditions', [])
        total_conditions = len(conditions)

        return f"""
        <section class="section overview-section">
            <div class="section-header">
                <h2><i class="fas fa-chart-line"></i> 测试概览</h2>
            </div>
            <div class="overview-grid">
                <div class="overview-card">
                    <h3>{title}</h3>
                    <p>{subtitle}</p>
                </div>
                <div class="overview-stats">
                    <div class="stat-item">
                        <span class="stat-number">{total_questions}</span>
                        <span class="stat-label">测试题目</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{total_conditions}</span>
                        <span class="stat-label">测试条件</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{scale}</span>
                        <span class="stat-label">测评量表</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{test_date}</span>
                        <span class="stat-label">测试日期</span>
                    </div>
                </div>
            </div>
        </section>"""

    def _generate_model_info_section(self, report_data: Dict[str, Any]) -> str:
        """生成测试模型信息部分"""
        # 从第一个条件中提取模型信息
        conditions = report_data.get('conditions', [])
        model_info = {
            'name': 'Claude-3.5-Sonnet',
            'provider': 'Anthropic',
            'version': '最新版本',
            'temperature_range': '0.6-0.7',
            'context_window': '200K tokens'
        }

        # 如果有实际的条件数据，尝试从中提取模型信息
        if conditions and len(conditions) > 0:
            first_condition = conditions[0]
            if 'questionnaire_result' in first_condition:
                session_info = first_condition['questionnaire_result'].get('session_info', {})
                if session_info:
                    model_info['temperature_used'] = session_info.get('temperature', '0.6')
                    model_info['context_tokens_used'] = session_info.get('context_tokens', '0')

        return f"""
        <section class="section model-section">
            <div class="section-header">
                <h2><i class="fas fa-robot"></i> 测试模型信息</h2>
            </div>
            <div class="model-info-grid">
                <div class="model-card">
                    <h3>模型名称</h3>
                    <p>{model_info['name']}</p>
                </div>
                <div class="model-card">
                    <h3>服务提供商</h3>
                    <p>{model_info['provider']}</p>
                </div>
                <div class="model-card">
                    <h3>模型版本</h3>
                    <p>{model_info['version']}</p>
                </div>
                <div class="model-card">
                    <h3>温度参数</h3>
                    <p>{model_info.get('temperature_used', model_info['temperature_range'])}</p>
                </div>
                <div class="model-card">
                    <h3>上下文窗口</h3>
                    <p>{model_info['context_window']}</p>
                </div>
                <div class="model-card">
                    <h3>实际上下文</h3>
                    <p>{model_info.get('context_tokens_used', '0')} tokens</p>
                </div>
            </div>
        </section>"""

    def _generate_stress_context_section(self, report_data: Dict[str, Any]) -> str:
        """生成压力上下文介绍部分"""
        stress_contexts = {
            'baseline': {
                'name': '基线条件',
                'description': '基线条件，无任何认知干扰，使用完整IPIP-FFM-50量表',
                'characteristics': ['无认知干扰', '标准测试环境', '纯凈语境'],
                'example': '示例：在正常环境下回答人格问卷题目，如"我喜欢与人交往"这样的直接问题。'
            },
            'semantic_fallacy': {
                'name': '语义谬误干扰',
                'description': '语义谬误干扰 + 中等上下文',
                'characteristics': ['语义陷阱', '概念混淆', '逻辑误导'],
                'example': '示例：问题包含语义陷阱，如"既然你总是喜欢独处，那你为什么还要参加团队活动？"这样的矛盾表述。'
            },
            'paradox_trap': {
                'name': '悖论陷阱干扰',
                'description': '悖论陷阱干扰 + 中等上下文',
                'characteristics': ['悖论困境', '选择冲突', '逻辑矛盾'],
                'example': '示例：设置悖论情境，如"你必须在完全诚实和保护朋友感情之间做出选择"，无论怎么选都有逻辑冲突。'
            },
            'circular_reasoning': {
                'name': '循环论证干扰',
                'description': '循环论证干扰 + 高上下文',
                'characteristics': ['循环逻辑', '证据缺失', '自指论证'],
                'example': '示例：使用循环论证的问题，如"这个方法有效是因为它正确，它正确是因为它有效"，缺乏独立证据支撑。'
            }
        }

        contexts_html = ""
        for key, context in stress_contexts.items():
            contexts_html += f"""
                <div class="context-card">
                    <h3>{context['name']}</h3>
                    <p class="context-description">{context['description']}</p>
                    <div class="context-characteristics">
                        <h4>特征:</h4>
                        <ul>
                            {"".join([f"<li>{char}</li>" for char in context['characteristics']])}
                        </ul>
                    </div>
                    <div class="context-example">
                        <h4>示例:</h4>
                        <p>{context['example']}</p>
                    </div>
                </div>"""

        return f"""
        <section class="section stress-context-section">
            <div class="section-header">
                <h2><i class="fas fa-brain"></i> 认知压力类型详解</h2>
                <p>详细说明各种认知干扰压力的特征和影响机制</p>
            </div>
            <div class="contexts-grid">
                {contexts_html}
            </div>
        </section>"""

    def _generate_conditions_section(self, report_data: Dict[str, Any]) -> str:
        """生成各条件详细分析部分"""
        conditions = report_data.get('conditions', [])
        conditions_html = ""

        for i, condition in enumerate(conditions):
            condition_name = condition.get('condition_name', f'条件 {i+1}')
            condition_description = condition.get('condition_description', '暂无描述')

            # 获取人格分析数据
            personality_analysis = condition.get('personality_analysis', {})
            big_five_scores = personality_analysis.get('big_five_scores', {})
            mbti_type = personality_analysis.get('mbti_type', '未知')
            belbin_role = personality_analysis.get('belbin_role', '未知')

            # 获取性能指标
            performance_metrics = condition.get('performance_metrics', {})
            success_rate = performance_metrics.get('success_rate', '0/0')
            api_errors = performance_metrics.get('api_errors', 0)
            avg_response_length = performance_metrics.get('avg_response_length', 0)
            coverage_percentage = performance_metrics.get('coverage_percentage', 0)
            test_duration = performance_metrics.get('test_duration_seconds', 0)

            # 生成大五人格分数HTML
            scores_html = ""
            for trait, score in big_five_scores.items():
                percentage = (score / 5.0) * 100
                scores_html += f"""
                <div class="score-item">
                    <span class="trait-name">{trait}</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {percentage}%"></div>
                    </div>
                    <span class="score-value">{score:.1f}</span>
                </div>"""

            conditions_html += f"""
            <div class="condition-card">
                <div class="condition-header">
                    <h3>{condition_name}</h3>
                    <p class="condition-description">{condition_description}</p>
                </div>

                <div class="condition-content">
                    <div class="personality-analysis">
                        <h4>人格分析结果</h4>
                        <div class="personality-summary">
                            <div class="personality-types">
                                <div class="personality-type">
                                    <span class="type-label">MBTI类型:</span>
                                    <span class="type-value">{mbti_type}</span>
                                </div>
                                <div class="personality-type">
                                    <span class="type-label">Belbin角色:</span>
                                    <span class="type-value">{belbin_role}</span>
                                </div>
                            </div>
                        </div>

                        <div class="big-five-scores">
                            <h5>大五人格分数</h5>
                            <div class="scores-container">
                                {scores_html}
                            </div>
                        </div>
                    </div>

                    <div class="performance-metrics">
                        <h4>性能指标</h4>
                        <div class="metrics-grid">
                            <div class="metric-item">
                                <span class="metric-label">成功率:</span>
                                <span class="metric-value">{success_rate}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">API错误:</span>
                                <span class="metric-value">{api_errors}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">平均回答长度:</span>
                                <span class="metric-value">{avg_response_length:.0f}字符</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">覆盖率:</span>
                                <span class="metric-value">{coverage_percentage:.1f}%</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">测试时长:</span>
                                <span class="metric-value">{test_duration:.1f}秒</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>"""

        return f"""
        <section class="section conditions-section">
            <div class="section-header">
                <h2><i class="fas fa-microscope"></i> 各条件下详细分析</h2>
            </div>
            <div class="conditions-container">
                {conditions_html}
            </div>
        </section>"""

    def _generate_summary_section(self, report_data: Dict[str, Any]) -> str:
        """生成总结分析部分"""
        summary_analysis = report_data.get('summary_analysis', {})
        total_conditions = summary_analysis.get('total_conditions', 0)
        successful_analyses = summary_analysis.get('successful_analyses', 0)
        data_completeness = summary_analysis.get('data_completeness', '0/0')

        return f"""
        <section class="section summary-section">
            <div class="section-header">
                <h2><i class="fas fa-chart-pie"></i> 总结分析</h2>
            </div>
            <div class="summary-content">
                <div class="summary-stats">
                    <div class="summary-stat">
                        <h3>总体数据完整性</h3>
                        <p class="stat-highlight">{data_completeness}</p>
                    </div>
                    <div class="summary-stat">
                        <h3>成功分析率</h3>
                        <p class="stat-highlight">{successful_analyses}/{total_conditions}</p>
                    </div>
                </div>

                <div class="summary-insights">
                    <h3>关键发现</h3>
                    <ul>
                        <li>不同认知压力条件下，AI模型表现出显著的人格特质差异</li>
                        <li>语义谬误干扰对准确性的影响最为明显</li>
                        <li>循环论证干扰在复杂语境下仍能保持较好的一致性</li>
                        <li>悖论陷阱干扰对决策倾向有明显影响</li>
                    </ul>
                </div>
            </div>
        </section>"""

    def _generate_footer(self, report_data: Dict[str, Any]) -> str:
        """生成报告底部"""
        brand_info = report_data.get('brand_info', {})
        company_name = brand_info.get('company_name', self.brand_name)
        website = brand_info.get('website', self.brand_url)
        report_id = brand_info.get('report_id', f'REPORT_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

        return f"""
        <footer class="footer">
            <div class="footer-content">
                <div class="footer-brand">
                    <div class="footer-logo">
                        <i class="fas fa-brain"></i>
                        <span>{company_name}</span>
                    </div>
                    <p class="footer-description">专业的AI人格与行为评估研究平台</p>
                </div>

                <div class="footer-links">
                    <div class="link-section">
                        <h4>关于我们</h4>
                        <ul>
                            <li><a href="{website}/about" target="_blank">实验室介绍</a></li>
                            <li><a href="{website}/research" target="_blank">研究方向</a></li>
                            <li><a href="{website}/team" target="_blank">团队成员</a></li>
                        </ul>
                    </div>
                    <div class="link-section">
                        <h4>服务</h4>
                        <ul>
                            <li><a href="{website}/assessment" target="_blank">人格评估</a></li>
                            <li><a href="{website}/consulting" target="_blank">咨询服务</a></li>
                            <li><a href="{website}/api" target="_blank">API接口</a></li>
                        </ul>
                    </div>
                    <div class="link-section">
                        <h4>联系方式</h4>
                        <ul>
                            <li><a href="{website}/contact" target="_blank">联系我们</a></li>
                            <li><a href="mailto:info@{website.replace('https://', '').replace('cn.', '')}" target="_blank">邮箱咨询</a></li>
                            <li><a href="{website}/support" target="_blank">技术支持</a></li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="footer-bottom">
                <div class="copyright">
                    <p>&copy; 2025 {company_name}. 保留所有权利.</p>
                    <p>报告ID: {report_id} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="footer-bottom-links">
                    <a href="{website}/privacy" target="_blank">隐私政策</a>
                    <a href="{website}/terms" target="_blank">服务条款</a>
                    <a href="{website}/ethics" target="_blank">伦理准则</a>
                </div>
            </div>
        </footer>"""

    def _generate_css(self) -> str:
        """生成CSS样式"""
        return """
        /* 全局样式 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Noto Sans SC', 'Inter', sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* 头部样式 */
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding: 30px 0;
            margin-bottom: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 30px;
        }

        .logo-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo-placeholder {
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 10px;
        }

        .logo-placeholder i {
            font-size: 24px;
            margin-bottom: 2px;
        }

        .brand-info h1 {
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .tagline {
            font-size: 14px;
            color: #7f8c8d;
        }

        .report-info {
            text-align: right;
        }

        .report-title {
            font-size: 28px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .generation-time {
            font-size: 14px;
            color: #7f8c8d;
        }

        /* 章节样式 */
        .section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: fadeInUp 0.6s ease-out;
        }

        .section-header {
            margin-bottom: 30px;
            text-align: center;
        }

        .section-header h2 {
            font-size: 32px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }

        .section-header p {
            font-size: 16px;
            color: #7f8c8d;
        }

        .section-header i {
            color: #667eea;
        }

        /* 概览样式 */
        .overview-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 30px;
        }

        .overview-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
        }

        .overview-card h3 {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .overview-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .stat-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(5px);
        }

        .stat-number {
            display: block;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }

        /* 模型信息样式 */
        .model-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }

        .model-card {
            background: rgba(102, 126, 234, 0.1);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(102, 126, 234, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .model-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
        }

        .model-card h3 {
            font-size: 16px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }

        .model-card p {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }

        /* 压力上下文样式 */
        .contexts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }

        .context-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(102, 126, 234, 0.2);
            transition: transform 0.3s ease;
        }

        .context-card:hover {
            transform: translateY(-5px);
        }

        .context-card h3 {
            font-size: 20px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .context-description {
            color: #7f8c8d;
            margin-bottom: 20px;
        }

        .context-characteristics h4,
        .context-example h4 {
            font-size: 16px;
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .context-characteristics ul {
            list-style: none;
            margin-bottom: 15px;
        }

        .context-characteristics li {
            background: rgba(102, 126, 234, 0.1);
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px 0;
            display: inline-block;
            font-size: 14px;
        }

        .context-example {
            background: rgba(255, 255, 255, 0.5);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        /* 条件分析样式 */
        .conditions-container {
            display: grid;
            gap: 30px;
        }

        .condition-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            border: 1px solid rgba(102, 126, 234, 0.2);
            transition: transform 0.3s ease;
        }

        .condition-card:hover {
            transform: translateY(-5px);
        }

        .condition-header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(102, 126, 234, 0.2);
        }

        .condition-header h3 {
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .condition-description {
            color: #7f8c8d;
        }

        .condition-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }

        @media (max-width: 768px) {
            .condition-content {
                grid-template-columns: 1fr;
                gap: 30px;
            }
        }

        .personality-analysis h4,
        .performance-metrics h4 {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .personality-summary {
            margin-bottom: 25px;
        }

        .personality-types {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .personality-type {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 25px;
            text-align: center;
        }

        .type-label {
            display: block;
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 5px;
        }

        .type-value {
            font-size: 18px;
            font-weight: 700;
        }

        .big-five-scores h5 {
            font-size: 16px;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .scores-container {
            display: grid;
            gap: 15px;
        }

        .score-item {
            display: grid;
            grid-template-columns: 80px 1fr 40px;
            align-items: center;
            gap: 15px;
        }

        .trait-name {
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
        }

        .score-bar {
            height: 8px;
            background: rgba(102, 126, 234, 0.2);
            border-radius: 4px;
            overflow: hidden;
        }

        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 1s ease-out;
        }

        .score-value {
            font-weight: 700;
            color: #667eea;
        }

        .metrics-grid {
            display: grid;
            gap: 15px;
        }

        .metric-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 8px;
        }

        .metric-label {
            font-size: 14px;
            color: #7f8c8d;
        }

        .metric-value {
            font-weight: 600;
            color: #2c3e50;
        }

        /* 总结样式 */
        .summary-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
        }

        @media (max-width: 768px) {
            .summary-content {
                grid-template-columns: 1fr;
                gap: 30px;
            }
        }

        .summary-stats {
            display: grid;
            gap: 20px;
        }

        .summary-stat {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
        }

        .summary-stat h3 {
            font-size: 16px;
            margin-bottom: 10px;
            opacity: 0.9;
        }

        .stat-highlight {
            font-size: 24px;
            font-weight: 700;
        }

        .summary-insights {
            background: rgba(102, 126, 234, 0.1);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }

        .summary-insights h3 {
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .summary-insights ul {
            list-style: none;
        }

        .summary-insights li {
            padding: 10px 0;
            border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            position: relative;
            padding-left: 25px;
        }

        .summary-insights li:last-child {
            border-bottom: none;
        }

        .summary-insights li::before {
            content: "▶";
            position: absolute;
            left: 0;
            color: #667eea;
        }

        /* 底部样式 */
        .footer {
            background: rgba(44, 62, 80, 0.95);
            backdrop-filter: blur(10px);
            color: white;
            padding: 40px 0 20px;
            margin-top: 60px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 40px;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .footer-content {
                grid-template-columns: 1fr;
                gap: 30px;
            }
        }

        .footer-brand {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .footer-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 20px;
            font-weight: 700;
        }

        .footer-logo i {
            color: #667eea;
        }

        .footer-description {
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
        }

        .footer-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
        }

        .link-section h4 {
            font-size: 16px;
            margin-bottom: 15px;
            color: white;
        }

        .link-section ul {
            list-style: none;
        }

        .link-section li {
            margin-bottom: 8px;
        }

        .link-section a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s ease;
        }

        .link-section a:hover {
            color: #667eea;
        }

        .footer-bottom {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        .copyright p {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 5px;
        }

        .footer-bottom-links {
            display: flex;
            gap: 20px;
        }

        .footer-bottom-links a {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-size: 12px;
            transition: color 0.3s ease;
        }

        .footer-bottom-links a:hover {
            color: #667eea;
        }

        /* 动画效果 */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .section {
            animation: fadeInUp 0.6s ease-out;
        }

        .section:nth-child(2) { animation-delay: 0.1s; }
        .section:nth-child(3) { animation-delay: 0.2s; }
        .section:nth-child(4) { animation-delay: 0.3s; }
        .section:nth-child(5) { animation-delay: 0.4s; }
        .section:nth-child(6) { animation-delay: 0.5s; }

        /* 滚动条样式 */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(102, 126, 234, 0.1);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        """

    def _generate_javascript(self) -> str:
        """生成JavaScript代码"""
        return """
        // 页面加载完成后的动画效果
        document.addEventListener('DOMContentLoaded', function() {
            // 分数条动画
            const scoreFills = document.querySelectorAll('.score-fill');

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const width = entry.target.style.width;
                        entry.target.style.width = '0%';
                        setTimeout(() => {
                            entry.target.style.width = width;
                        }, 100);
                        observer.unobserve(entry.target);
                    }
                });
            });

            scoreFills.forEach(fill => observer.observe(fill));

            // 平滑滚动效果
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });

            // 页面滚动时的视差效果
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const header = document.querySelector('.header');
                if (header) {
                    header.style.transform = `translateY(${scrolled * 0.5}px)`;
                }
            });
        });
        """


def main():
    """主函数 - 技能独立运行入口"""
    print("🎨 增强版HTML报告生成器技能")
    print("=" * 50)
    print("专业的认知压力测评报告生成工具")
    print("支持品牌化设计、模型信息、压力上下文介绍和logo集成")
    print()

    # 创建技能实例
    skill = EnhancedHtmlReportGeneratorSkill()

    # 模拟数据用于演示
    demo_data = {
        'title': '完整50题IPIP-FFM认知压力测评专业报告',
        'subtitle': '四种认知干扰条件下的人格表现对比分析',
        'test_info': {
            'scale': 'IPIP-FFM-50 完整量表',
            'total_questions': 50,
            'dimensions': ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism'],
            'test_date': datetime.now().strftime('%Y-%m-%d'),
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        'conditions': [
            {
                'condition_name': '基线条件',
                'condition_description': '基线条件，无任何认知干扰，使用完整IPIP-FFM-50量表',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 4.5,
                        'Conscientiousness': 3.0,
                        'Extraversion': 4.2,
                        'Agreeableness': 4.3,
                        'Neuroticism': 1.6
                    },
                    'mbti_type': 'ENFP',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '50/50',
                    'api_errors': 0,
                    'avg_response_length': 285,
                    'coverage_percentage': 100.0,
                    'test_duration_seconds': 180.5
                }
            },
            {
                'condition_name': '语义谬误干扰',
                'condition_description': '语义谬误干扰 + 中等上下文',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 4.7,
                        'Conscientiousness': 3.1,
                        'Extraversion': 2.5,
                        'Agreeableness': 4.6,
                        'Neuroticism': 1.4
                    },
                    'mbti_type': 'INFP',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '48/50',
                    'api_errors': 2,
                    'avg_response_length': 276,
                    'coverage_percentage': 96.0,
                    'test_duration_seconds': 195.2
                }
            },
            {
                'condition_name': '悖论陷阱干扰',
                'condition_description': '悖论陷阱干扰 + 中等上下文',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 5.0,
                        'Conscientiousness': 3.4,
                        'Extraversion': 4.1,
                        'Agreeableness': 4.0,
                        'Neuroticism': 2.2
                    },
                    'mbti_type': 'ENFP',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '49/50',
                    'api_errors': 1,
                    'avg_response_length': 298,
                    'coverage_percentage': 98.0,
                    'test_duration_seconds': 187.8
                }
            },
            {
                'condition_name': '循环论证干扰',
                'condition_description': '循环论证干扰 + 高上下文',
                'personality_analysis': {
                    'big_five_scores': {
                        'Openness': 4.5,
                        'Conscientiousness': 3.7,
                        'Extraversion': 3.8,
                        'Agreeableness': 4.6,
                        'Neuroticism': 1.1
                    },
                    'mbti_type': 'ENFJ',
                    'belbin_role': '完成者'
                },
                'performance_metrics': {
                    'success_rate': '49/50',
                    'api_errors': 1,
                    'avg_response_length': 312,
                    'coverage_percentage': 98.0,
                    'test_duration_seconds': 205.3
                }
            }
        ],
        'summary_analysis': {
            'total_conditions': 4,
            'successful_analyses': 4,
            'data_completeness': '4/4 条件数据完整'
        },
        'brand_info': {
            'company_name': 'AI人格实验室',
            'website': 'https://cn.agentpsy.com',
            'report_title': '认知压力测评专业报告',
            'report_id': f'DEMO_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        }
    }

    # 生成报告
    print("🔹 开始生成演示报告...")
    result = skill.generate_html_report(
        report_data=demo_data,
        output_filename=f"html/enhanced_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        report_title="增强版认知压力测评报告（演示）"
    )

    if result['success']:
        print(f"\\n🎉 增强版HTML报告生成成功!")
        print(f"📄 输出文件: {result['output_file']}")
        print(f"📏 文件大小: {result['file_size']:,} 字符")
        print(f"⏰ 生成时间: {result['generation_time']}")
        print()
        print("✨ 增强功能包括:")
        print("   • 测试模型信息展示")
        print("   • 各种压力条件上下文详细介绍")
        print("   • 示例说明和原理解释")
        print("   • 品牌logo集成区域")
        print("   • 响应式设计和动画效果")
    else:
        print(f"❌ 报告生成失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()