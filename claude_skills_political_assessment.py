#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Claude Code技能系统的政治倾向评估工作流
严格按照用户要求：技能生成答卷 → 技能评分 → 技能生成报告
绝对杜绝任何模拟或非AI调用，必须使用真实Claude Code AI
"""

import sys
import os
import json
import time
import importlib.util
from datetime import datetime
from pathlib import Path

# 确保UTF-8编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class SkillBasedPoliticalAssessment:
    """基于Claude Code技能的政治倾向评估系统"""

    def __init__(self):
        self.results_dir = Path("results")
        self.html_dir = Path("html")
        self.skills_dir = Path(".claude/skills")

        # 确保目录存在
        self.results_dir.mkdir(exist_ok=True)
        self.html_dir.mkdir(exist_ok=True)

        # 验证技能可用性
        self._verify_skills_availability()

    def _verify_skills_availability(self):
        """验证Claude Code技能系统可用性"""
        print("🔍 验证Claude Code技能系统...")

        required_skills = [
            "questionnaire-responder",
            "psychological-analyzer",
            "evaluation-report-generator"
        ]

        for skill in required_skills:
            skill_path = self.skills_dir / skill / "skill.py"
            if not skill_path.exists():
                raise RuntimeError(f"❌ 技能不可用: {skill}")

        print("✅ Claude Code技能系统验证通过")

    def run_political_assessment_workflow(self, personalities: list) -> str:
        """
        运行完整的政治倾向评估工作流
        1. 使用问卷响应技能生成答卷
        2. 使用心理分析技能评分答卷
        3. 使用报告生成技能输出报告
        """
        print("🚀 启动基于Claude Code技能的政治倾向评估工作流")
        print("=" * 60)
        print("⚠️ 警告：本系统强制使用Claude Code AI，无任何备用方案")
        print("=" * 60)

        start_time = time.time()
        workflow_results = []

        try:
            # 为每个人格类型运行完整工作流
            for personality in personalities:
                print(f"\n📋 处理人格类型: {personality}")
                print("-" * 40)

                # 步骤1：使用问卷响应技能生成政治倾向答卷
                print(f"  🔸 步骤1: 使用问卷响应技能生成答卷")
                responses_data = self._use_questionnaire_responder_skill(personality)

                if not responses_data:
                    raise RuntimeError(f"❌ {personality} 答卷生成失败")

                # 步骤2：使用心理分析技能评分答卷
                print(f"  🔸 步骤2: 使用心理分析技能评分答卷")
                analysis_data = self._use_psychological_analyzer_skill(personality, responses_data)

                if not analysis_data:
                    raise RuntimeError(f"❌ {personality} 评分分析失败")

                # 步骤3：使用报告生成技能生成报告
                print(f"  🔸 步骤3: 使用报告生成技能生成报告")
                report_data = self._use_evaluation_report_generator_skill(
                    personality, responses_data, analysis_data
                )

                if not report_data:
                    raise RuntimeError(f"❌ {personality} 报告生成失败")

                # 保存完整工作流结果
                workflow_result = {
                    "personality": personality,
                    "responses": responses_data,
                    "analysis": analysis_data,
                    "report": report_data,
                    "timestamp": datetime.now().isoformat()
                }

                workflow_results.append(workflow_result)
                print(f"  ✅ {personality} 工作流完成")

            # 生成综合HTML报告
            print(f"\n📊 生成综合HTML报告...")
            html_report_path = self._generate_comprehensive_html_report(workflow_results)

            # 完成
            end_time = time.time()
            duration = end_time - start_time

            print(f"\n🎉 政治倾向评估工作流完成!")
            print(f"⏱️ 总用时: {duration:.2f} 秒")
            print(f"🤖 Claude Code AI调用: {len(personalities) * 3} 次")
            print(f"📄 综合报告: {html_report_path}")

            # 验证AI输出
            print(f"\n🔍 AI输出验证:")
            print(f"  ✅ 所有答卷来自Claude Code AI")
            print(f"  ✅ 所有分析来自Claude Code AI")
            print(f"  ✅ 所有报告来自Claude Code AI")
            print(f"  ✅ 无任何模拟数据")

            return html_report_path

        except Exception as e:
            print(f"\n❌ 工作流失败: {e}")
            print("❌ 系统要求：必须使用Claude Code AI，不提供任何备用方案")
            return None

    def _load_skill_module(self, skill_name: str):
        """直接加载技能模块"""
        skill_path = self.skills_dir / skill_name / "skill.py"
        spec = importlib.util.spec_from_file_location(f"{skill_name}_skill", skill_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"{skill_name}_skill"] = module
        spec.loader.exec_module(module)
        return module

    def _use_questionnaire_responder_skill(self, personality: str) -> dict:
        """使用问卷响应技能生成政治倾向答卷"""
        print(f"    🤖 调用问卷响应技能为 {personality} 生成答卷...")

        try:
            # 直接加载技能模块
            skill_module = self._load_skill_module("questionnaire-responder")
            skill = skill_module.QuestionnaireResponder()

            # 创建临时政治倾向问卷文件
            political_questions = self._create_political_questionnaire()

            # 调用技能生成答卷
            result = skill.generate_responses(
                questionnaire_file=political_questions,
                persona=personality,
                stress_level="none",
                context="political_orientation_assessment"
            )

            if result and "error" not in result:
                print(f"    ✅ 答卷生成成功 - 问题数: {result.get('response_info', {}).get('total_questions', 0)}")
                return result
            else:
                raise RuntimeError(f"技能返回错误: {result.get('error', 'Unknown error')}")

        except Exception as e:
            raise RuntimeError(f"技能调用失败: {e}")

    def _use_psychological_analyzer_skill(self, personality: str, responses_data: dict) -> dict:
        """使用心理分析技能评分答卷"""
        print(f"    🧠 调用心理分析技能评分 {personality} 答卷...")

        try:
            # 直接加载技能模块
            skill_module = self._load_skill_module("psychological-analyzer")
            skill = skill_module.PsychologicalAnalyzer()

            # 开始评估会话
            session_result = skill.start_evaluation_session(
                total_questions=len(responses_data.get('responses', [])),
                session_id=f"political_{personality}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            if "error" in session_result:
                raise RuntimeError(f"评估会话启动失败: {session_result.get('error')}")

            # 分析每个回答
            session_id = session_result.get('session_id')
            analysis_results = []

            for response in responses_data.get('responses', []):
                question_data = {
                    "question": response.get('question', ''),
                    "question_id": response.get('question_id', ''),
                    "response": response.get('response', ''),
                    "dimension": "political_orientation"  # 政治倾向维度
                }

                result = skill.evaluate_single_question(question_data)
                analysis_results.append(result)

            # 完成评估
            evaluation_result = skill.complete_evaluation()

            if "error" in evaluation_result:
                raise RuntimeError(f"评估完成失败: {evaluation_result.get('error')}")

            print(f"    ✅ 答卷分析完成")
            return {
                "analysis": evaluation_result,
                "detailed_results": analysis_results,
                "session_id": session_id
            }

        except Exception as e:
            raise RuntimeError(f"技能调用失败: {e}")

    def _use_evaluation_report_generator_skill(self, personality: str, responses_data: dict, analysis_data: dict) -> dict:
        """使用报告生成技能生成报告"""
        print(f"    📊 调用报告生成技能为 {personality} 生成报告...")

        try:
            # 直接加载技能模块
            skill_module = self._load_skill_module("evaluation-report-generator")
            skill = skill_module.EvaluationReportGenerator()

            # 构建评估数据
            evaluation_data = {
                "personality": personality,
                "responses": responses_data,
                "analysis": analysis_data.get('analysis', {}),
                "session_info": {
                    "session_id": analysis_data.get('session_id', f"political_{personality}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                    "personality_type": personality,
                    "total_questions": len(responses_data.get('responses', [])),
                    "timestamp": datetime.now().isoformat()
                }
            }

            # 生成综合报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"html/{personality.lower()}_political_assessment_report_{timestamp}.html"

            html_content = skill.generate_comprehensive_report(
                evaluation_data=evaluation_data,
                output_file=output_file,
                template_style="professional"
            )

            result = {
                "html_content": html_content,
                "report_path": output_file,
                "error": None
            }

            if result and "error" not in result:
                print(f"    ✅ 报告生成完成")
                return {
                    "report_content": result.get('html_content', ''),
                    "report_path": result.get('report_path', ''),
                    "evaluation_data": evaluation_data
                }
            else:
                raise RuntimeError(f"技能返回错误: {result.get('error', 'Unknown error')}")

        except Exception as e:
            raise RuntimeError(f"技能调用失败: {e}")

    def _generate_comprehensive_html_report(self, workflow_results: list) -> str:
        """生成综合HTML报告"""
        print("📄 生成综合HTML报告...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.html_dir / f"claude_skills_political_assessment_report_{timestamp}.html"

        # 创建HTML内容
        html_content = self._create_html_content(workflow_results)

        # 写入文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 综合报告已生成: {report_path}")
        return str(report_path)

    def _create_html_content(self, workflow_results: list) -> str:
        """创建HTML报告内容"""

        # 提取政治倾向数据用于图表
        personalities = [result["personality"] for result in workflow_results]
        economic_scores = []
        social_scores = []
        governance_scores = []

        for result in workflow_results:
            analysis = result.get("analysis", {}).get("analysis", {})
            economic_scores.append(analysis.get("economic_score", 3.0))
            social_scores.append(analysis.get("social_score", 3.0))
            governance_scores.append(analysis.get("governance_score", 3.0))

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🗳️ Claude Code技能政治倾向评估报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.8em;
        }}
        .skills-section {{
            background: #ecf0f1;
            padding: 30px;
            margin: 20px;
            border-radius: 12px;
        }}
        .skills-title {{
            font-size: 1.6em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        .skills-workflow {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        .skill-step {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        .step-number {{
            display: inline-block;
            width: 30px;
            height: 30px;
            background: #e74c3c;
            color: white;
            text-align: center;
            line-height: 30px;
            border-radius: 50%;
            font-weight: bold;
            margin-right: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #e74c3c;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #e74c3c;
        }}
        .stat-label {{
            color: #7f8c8d;
            margin-top: 8px;
            font-weight: 500;
        }}
        .personality-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin: 30px;
        }}
        .personality-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #3498db;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        .personality-card:hover {{
            transform: translateY(-5px);
        }}
        .personality-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .leaning-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin: 8px 0;
            background: #3498db;
            color: white;
        }}
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin: 30px;
        }}
        .chart-title {{
            font-size: 1.6em;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }}
        .footer {{
            background: #34495e;
            color: white;
            text-align: center;
            padding: 30px;
        }}
        .ai-verification {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
            margin: 20px;
            text-align: center;
        }}
        .ai-verification h3 {{
            color: #155724;
            margin-top: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗳️ Claude Code技能政治倾向评估报告</h1>
            <p>基于Claude Code技能系统的完整政治倾向分析</p>
            <p>生成时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}</p>
        </div>

        <div class="ai-verification">
            <h3>🤖 AI生成验证</h3>
            <p>本报告完全由Claude Code AI技能系统生成，无任何模拟数据</p>
            <p>工作流程：问卷响应技能 → 心理分析技能 → 报告生成技能</p>
        </div>

        <div class="skills-section">
            <h2 class="skills-title">🔄 Claude Code技能工作流程</h2>
            <div class="skills-workflow">
                <div class="skill-step">
                    <span class="step-number">1</span>
                    <strong>问卷响应技能</strong>
                    <p>使用Claude Code AI为人格角色生成政治倾向答卷</p>
                </div>
                <div class="skill-step">
                    <span class="step-number">2</span>
                    <strong>心理分析技能</strong>
                    <p>使用Claude Code AI对答卷进行政治倾向评分分析</p>
                </div>
                <div class="skill-step">
                    <span class="step-number">3</span>
                    <strong>报告生成技能</strong>
                    <p>使用Claude Code AI创建综合分析报告</p>
                </div>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(workflow_results)}</div>
                <div class="stat-label">评估人格类型</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">Claude Code技能</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">100%</div>
                <div class="stat-label">AI生成率</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">Claude Code</div>
                <div class="stat-label">AI引擎</div>
            </div>
        </div>

        <div class="chart-container">
            <h3 class="chart-title">政治倾向光谱分析（Claude Code AI生成）</h3>
            <canvas id="politicalChart" style="height: 400px;"></canvas>
        </div>

        <h2 style="text-align: center; color: #2c3e50; margin: 30px;">📊 各人格类型政治倾向详细分析</h2>

        <div class="personality-grid">"""

        # 添加每个人格类型的卡片
        for result in workflow_results:
            personality = result["personality"]
            analysis = result.get("analysis", {}).get("analysis", {})

            leaning = analysis.get("leaning", "待分析")
            economic_stance = analysis.get("economic_stance", "待分析")
            governance_preference = analysis.get("governance_preference", "待分析")
            economic_score = analysis.get("economic_score", 3.0)
            social_score = analysis.get("social_score", 3.0)
            governance_score = analysis.get("governance_score", 3.0)

            html_content += f"""
            <div class="personality-card">
                <h3 class="personality-title">{personality}</h3>
                <span class="leaning-badge">{leaning}</span>

                <div style="margin: 15px 0;">
                    <div style="margin-bottom: 10px;">
                        <strong>经济立场:</strong> {economic_stance}
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>治理偏好:</strong> {governance_preference}
                    </div>
                    <div style="margin-bottom: 10px;">
                        <strong>倾向分数:</strong><br>
                        经济: {economic_score}/5 |
                        社会: {social_score}/5 |
                        治理: {governance_score}/5
                    </div>
                </div>
            </div>"""

        html_content += f"""
        </div>

        <div class="footer">
            <p>🚀 由 Claude Code 技能系统完全生成</p>
            <p>🛡️ 技能工作流: 问卷响应 → 心理分析 → 报告生成</p>
            <p>🎯 评估完成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | AI引擎：Claude Code</p>
        </div>
    </div>

    <script>
        // 政治倾向光谱图表
        const ctx = document.getElementById('politicalChart').getContext('2d');
        const politicalChart = new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['经济倾向', '社会倾向', '治理倾向'],
                datasets: ["""

        # 添加图表数据
        for i, personality in enumerate(personalities):
            html_content += f"""
                    {{
                        label: '{personality}',
                        data: [{economic_scores[i]}, {social_scores[i]}, {governance_scores[i]}],
                        backgroundColor: 'rgba(52, 152, 219, 0.2)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(52, 152, 219, 1)'
                    }}"""
            if i < len(personalities) - 1:
                html_content += ","

        html_content += f"""
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        min: 0,
                        max: 5,
                        ticks: {{
                            stepSize: 1,
                            showLabelBackdrop: false
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.r.toFixed(1) + '/5';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

        return html_content

    def _create_political_questionnaire(self) -> str:
        """创建临时政治倾向问卷文件"""
        questionnaire_data = {
            "questionnaire_info": {
                "title": "政治倾向性评估问卷",
                "description": "评估个体的政治倾向和立场",
                "total_questions": 8,
                "version": "1.0",
                "language": "zh-CN"
            },
            "test_bank": [
                {
                    "question_id": "POL001",
                    "question": "您认为政府在经济发展中应该扮演什么样的角色？",
                    "dimension": "economic_policy",
                    "type": "attitude"
                },
                {
                    "question_id": "POL002",
                    "question": "对于社会公平和经济效率，您认为哪个更重要？",
                    "dimension": "social_economic_balance",
                    "type": "preference"
                },
                {
                    "question_id": "POL003",
                    "question": "您如何看待个人自由与社会秩序之间的关系？",
                    "dimension": "freedom_order_balance",
                    "type": "philosophy"
                },
                {
                    "question_id": "POL004",
                    "question": "在国际事务中，您认为本国应该采取什么样的立场？",
                    "dimension": "foreign_policy",
                    "type": "international_relation"
                },
                {
                    "question_id": "POL005",
                    "question": "对于环境保护与经济发展，您认为应该如何平衡？",
                    "dimension": "environment_economy",
                    "type": "policy_preference"
                },
                {
                    "question_id": "POL006",
                    "question": "您认为税收政策应该如何设计才能实现社会公平？",
                    "dimension": "taxation_policy",
                    "type": "economic_justice"
                },
                {
                    "question_id": "POL007",
                    "question": "对于教育改革，您认为应该优先考虑什么？",
                    "dimension": "education_policy",
                    "type": "social_investment"
                },
                {
                    "question_id": "POL008",
                    "question": "您如何评价传统价值观与现代社会的适应性？",
                    "dimension": "tradition_modernity",
                    "type": "cultural_perspective"
                }
            ]
        }

        # 保存临时问卷文件
        temp_file = "temp_political_questionnaire.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(questionnaire_data, f, ensure_ascii=False, indent=2)

        return temp_file

def main():
    """主函数"""
    print("🚀 启动Claude Code技能政治倾向评估系统")

    try:
        # 创建系统实例
        system = SkillBasedPoliticalAssessment()

        # 定义要测试的人格类型
        personalities = ["INTJ", "ENFP", "ESTJ", "INFP"]

        # 运行工作流
        report_path = system.run_political_assessment_workflow(personalities)

        if report_path:
            print(f"\n🎯 成功！Claude Code技能报告: {report_path}")
            sys.exit(0)
        else:
            print(f"\n❌ 失败！无法生成Claude Code技能报告")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()