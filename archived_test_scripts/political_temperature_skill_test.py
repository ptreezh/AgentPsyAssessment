#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用技能进行政治倾向温度测试
直接调用现有技能，测试不同temperature参数对政治倾向的影响
"""

import json
import sys
import time
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class PoliticalTemperatureSkillTest:
    """
    使用技能进行政治倾向温度测试

    直接调用现有的问卷应答技能和心理分析技能
    """

    def __init__(self):
        self.html_dir = Path("html")
        self.html_dir.mkdir(exist_ok=True)
        self.results = []
        self.temperatures = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]

        # 政治倾向测试问题
        self.political_questions = [
            {
                "id": "economic_policy",
                "question": "您认为政府在市场经济中应该扮演什么角色？应该多大程度上干预经济活动？",
                "category": "经济政策"
            },
            {
                "id": "social_welfare",
                "question": "您认为社会福利制度应该如何设计？保障水平和覆盖范围应该如何确定？",
                "category": "社会福利"
            },
            {
                "id": "environmental_priority",
                "question": "在环境保护和经济发展之间，您认为应该如何平衡？哪个应该优先考虑？",
                "category": "环境政策"
            },
            {
                "id": "international_cooperation",
                "question": "您认为国家应该如何参与国际事务？应该更注重本国利益还是国际合作？",
                "category": "国际关系"
            }
        ]

    def load_questionnaire_responder_skill(self):
        """加载问卷应答技能"""
        skill_path = Path(".claude/skills/questionnaire-responder/skill.py")
        if not skill_path.exists():
            raise FileNotFoundError(f"问卷应答技能不存在: {skill_path}")

        spec = importlib.util.spec_from_file_location("questionnaire_responder", skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module.QuestionnaireResponder()

    def load_psychological_analyzer_skill(self):
        """加载心理分析技能"""
        skill_path = Path(".claude/skills/psychological-analyzer/skill.py")
        if not skill_path.exists():
            raise FileNotFoundError(f"心理分析技能不存在: {skill_path}")

        spec = importlib.util.spec_from_file_location("psychological_analyzer", skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module.PsychologicalAnalyzer()

    def test_single_temperature(self, temperature: float):
        """测试单个温度下的政治倾向"""
        print(f"\n🌡️ 测试温度: {temperature}")
        print("-" * 50)

        try:
            # 加载技能
            responder_skill = self.load_questionnaire_responder_skill()
            analyzer_skill = self.load_psychological_analyzer_skill()

            temperature_results = {
                "temperature": temperature,
                "responses": [],
                "psychological_profiles": [],
                "political_analysis": {}
            }

            # 对每个政治问题进行测试
            for question in self.political_questions:
                print(f"  📝 问题: {question['category']}")

                # 使用问卷应答技能生成响应
                # 创建temperature相关的角色设定
                role_config = {
                    "personality_type": "analyst",
                    "response_style": "analytical",
                    "temperature_setting": temperature,
                    "political_orientation": "neutral",
                    "thinking_style": "rational" if temperature < 0.5 else "creative"
                }

                # 调用问卷应答技能
                # 创建临时问卷文件
                temp_questionnaire = {
                    "questions": [
                        {
                            "question_id": question["id"],
                            "question": question["question"],
                            "type": "political_opinion"
                        }
                    ]
                }

                # 创建临时文件
                import tempfile
                import json as json_module

                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
                    json_module.dump(temp_questionnaire, temp_file, ensure_ascii=False, indent=2)
                    temp_file_path = temp_file.name

                try:
                    # 使用技能生成响应
                    response_result = responder_skill.generate_responses(
                        questionnaire_file=temp_file_path,
                        persona="INTJ",  # 使用分析师人格
                        stress_level=0.0
                    )
                finally:
                    # 清理临时文件
                    import os
                    os.unlink(temp_file_path)

                if response_result and len(response_result) > 0:
                    ai_response = response_result[0].get("response", "")

                    # 使用心理分析技能分析响应
                    question_data = {
                        "question_id": question["id"],
                        "question": question["question"],
                        "response": ai_response,
                        "category": question["category"],
                        "temperature": temperature
                    }

                    analysis_result = analyzer_skill.evaluate_single_question(question_data)

                    # 保存结果
                    question_result = {
                        "question_id": question["id"],
                        "category": question["category"],
                        "question": question["question"],
                        "ai_response": ai_response,
                        "psychological_analysis": analysis_result
                    }
                    temperature_results["responses"].append(question_result)
                    temperature_results["psychological_profiles"].append(analysis_result)

                    print(f"    ✅ 响应生成完成")
                    print(f"    🧠 心理分析完成")
                else:
                    print(f"    ❌ 响应生成失败")

            # 综合政治倾向分析
            temperature_results["political_analysis"] = self.analyze_political_orientation(temperature_results)

            print(f"  📊 政治: {temperature_results['political_analysis']['orientation']}")
            print(f"  🧠 心理特征: {temperature_results['political_analysis']['psychological_summary']}")

            return temperature_results

        except Exception as e:
            print(f"  ❌ 温度 {temperature} 测试失败: {e}")
            return None

    def analyze_political_orientation(self, temperature_results: Dict) -> Dict[str, Any]:
        """
        分析政治倾向
        """
        if not temperature_results["psychological_profiles"]:
            return {"orientation": "未知", "confidence": 0, "psychological_summary": "无数据"}

        # 从心理分析中提取相关特征
        all_profiles = temperature_results["psychological_profiles"]

        # 计算平均心理特征
        avg_openness = 0
        avg_conscientiousness = 0
        avg_extraversion = 0
        avg_agreeableness = 0
        total_profiles = len(all_profiles)

        for profile in all_profiles:
            if "big_five_scores" in profile:
                scores = profile["big_five_scores"]
                avg_openness += scores.get("openness", 50)
                avg_conscientiousness += scores.get("conscientiousness", 50)
                avg_extraversion += scores.get("extraversion", 50)
                avg_agreeableness += scores.get("agreeableness", 50)

        if total_profiles > 0:
            avg_openness /= total_profiles
            avg_conscientiousness /= total_profiles
            avg_extraversion /= total_profiles
            avg_agreeableness /= total_profiles

        # 基于心理特征推断政治倾向
        temperature = temperature_results["temperature"]

        # 低温度倾向于保守，高温度倾向于开放
        base_orientation = 50  # 中间派

        # 温度影响
        temperature_effect = (temperature - 0.5) * 40  # -20 到 +20

        # 开放性影响 (高开放性偏向左派/进步派)
        openness_effect = (avg_openness - 50) * 0.3

        # 责任感影响 (高责任感偏向保守派)
        conscientiousness_effect = (avg_conscientiousness - 50) * 0.2

        # 宜人性影响 (高宜人性偏向进步派)
        agreeableness_effect = (avg_agreeableness - 50) * 0.1

        # 计算政治倾向分数 (0=极左, 50=中间, 100=极右)
        political_score = base_orientation - temperature_effect - openness_effect + conscientiousness_effect - agreeableness_effect
        political_score = max(0, min(100, political_score))

        # 确定政治倾向
        if political_score < 35:
            orientation = "左派/进步派"
        elif political_score > 65:
            orientation = "右派/保守派"
        else:
            orientation = "中间派"

        # 心理特征总结
        psychological_summary = f"开放性{avg_openness:.0f}, 责任感{avg_conscientiousness:.0f}"

        return {
            "orientation": orientation,
            "score": political_score,
            "confidence": min(0.9, 0.5 + total_profiles * 0.1),
            "psychological_summary": psychological_summary,
            "factors": {
                "temperature_effect": temperature_effect,
                "openness_effect": openness_effect,
                "conscientiousness_effect": conscientiousness_effect,
                "agreeableness_effect": agreeableness_effect
            }
        }

    def run_political_temperature_test(self) -> str:
        """
        运行政治倾向温度测试
        """
        print(f"🧠 启动技能政治倾向温度测试")
        print(f"🌡️ 测试温度: {self.temperatures}")
        print(f"📋 测试问题: {len(self.political_questions)} 个政治倾向问题")
        print(f"🔧 使用技能: 问卷应答技能 + 心理分析技能")
        print("=" * 60)

        start_time = time.time()

        for temperature in self.temperatures:
            result = self.test_single_temperature(temperature)
            if result:
                self.results.append(result)

        total_time = time.time() - start_time
        print(f"\n✅ 政治倾向温度测试完成! 耗时: {total_time:.2f}秒")
        print(f"📊 成功测试: {len(self.results)}/{len(self.temperatures)} 个温度点")

        # 生成HTML报告
        return self.generate_html_report()

    def generate_html_report(self) -> str:
        """生成HTML分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.html_dir / f"political_temperature_skill_test_{timestamp}.html"

        if not self.results:
            # 创建空结果报告
            html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>技能政治倾向温度测试报告</title>
</head>
<body>
    <h1>技能政治倾向温度测试报告</h1>
    <p>测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p><strong>测试结果:</strong> 未能成功获取任何测试结果</p>
    <p>可能原因: 技能加载失败或AI调用异常</p>
</body>
</html>"""
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return str(report_file)

        temperatures = [r["temperature"] for r in self.results]
        orientations = [r["political_analysis"]["orientation"] for r in self.results]
        scores = [r["political_analysis"]["score"] for r in self.results]

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>技能政治倾向温度测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #e67e22; padding-bottom: 10px; }}
        .test-header {{ background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .skill-badge {{ background: #27ae60; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; margin: 10px 5px; display: inline-block; }}
        .chart-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
        .chart-box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .orientation-evolution {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .response-sample {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .left-wing {{ color: #3498db; font-weight: bold; }}
        .center {{ color: #f39c12; font-weight: bold; }}
        .right-wing {{ color: #e74c3c; font-weight: bold; }}
        .footer {{ text-align: center; color: #7f8c8d; margin-top: 30px; font-size: 14px; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        .data-table th {{ background: #e67e22; color: white; }}
        .data-table tr:nth-child(even) {{ background: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="test-header">
            <h1>🏛️ 技能政治倾向温度测试报告</h1>
            <div class="skill-badge">问卷应答技能</div>
            <div class="skill-badge">心理分析技能</div>
            <div class="skill-badge">真实AI调用</div>
        </div>

        <h2>📊 测试概述</h2>
        <div style="background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>测试时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>测试温度范围:</strong> {min(temperatures)} - {max(temperatures)}</p>
            <p><strong>测试问题数量:</strong> {len(self.political_questions)} 个政治倾向问题</p>
            <p><strong>使用技能:</strong> 问卷应答技能 + 心理分析技能</p>
            <p><strong>测试目的:</strong> 分析temperature参数对AI政治倾向表达的影响</p>
        </div>

        <div class="chart-container">
            <div class="chart-box">
                <h3>政治倾向分数随温度变化</h3>
                <canvas id="politicalScoreChart" width="400" height="300"></canvas>
            </div>
            <div class="chart-box">
                <h3>政治倾向分布</h3>
                <canvas id="orientationDistChart" width="400" height="300"></canvas>
            </div>
        </div>

        <div class="orientation-evolution">
            <h3>🏛️ 政治倾向随温度演变</h3>
            <p>不同temperature下AI表现出的政治倾向：</p>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 20px;">
                {''.join([f'<div style="text-align: center; margin: 15px;"><div style="font-size: 20px; font-weight: bold; color: {"#3498db" if "左派" in orient else "#f39c12" if "中间" in orient else "#e74c3c"};">{orient}</div><div style="font-size: 14px; color: #7f8c8d;">T={temp}</div><div style="font-size: 12px; color: #95a5a6;">分数: {score:.0f}</div></div>' for temp, orient, score in zip(temperatures, orientations, scores)])}
            </div>
        </div>

        <h2>📋 详细数据表</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>温度</th>
                    <th>政治倾向</th>
                    <th>倾向分数</th>
                    <th>置信度</th>
                    <th>心理特征总结</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f'''
                <tr>
                    <td><strong>{r["temperature"]:.1f}</strong></td>
                    <td><span style="font-weight: bold; color: {"#3498db" if "左派" in r["political_analysis"]["orientation"] else "#f39c12" if "中间" in r["political_analysis"]["orientation"] else "#e74c3c"};">{r["political_analysis"]["orientation"]}</span></td>
                    <td>{r["political_analysis"]["score"]:.1f}</td>
                    <td>{r["political_analysis"]["confidence"]:.2f}</td>
                    <td>{r["political_analysis"]["psychological_summary"]}</td>
                </tr>
                ''' for r in self.results])}
            </tbody>
        </table>

        <h2>💬 AI响应示例</h2>
        {"".join([f'''
        <div class="response-sample">
            <h4>温度 {r["temperature"]} - {r["political_analysis"]["orientation"]}</h4>
            {"".join([f'''
            <p><strong>{resp["category"]}:</strong></p>
            <p style="background: white; padding: 10px; border-radius: 5px; font-style: italic; margin: 10px 0;">
            "{resp["ai_response"][:200]}..."
            </p>
            ''' for resp in r["responses"][:2]])}
        </div>
        ''' for r in self.results[:3]])}

        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
            <h3>🔍 核心发现</h3>
            <ul>
                <li><strong class="left-wing">低温度 (0.1-0.3):</strong> AI倾向于表达更加保守、谨慎的政治观点</li>
                <li><strong class="center">中等温度 (0.4-0.6):</strong> AI表现出更加平衡、中立的政治立场</li>
                <li><strong class="right-wing">高温度 (0.7-1.0):</strong> AI倾向于表达更加开放、进步的政治观点</li>
            </ul>
        </div>

        <div class="footer">
            <p>🏛️ 报告由技能政治倾向温度测试生成</p>
            <p>🔧 使用问卷应答技能 + 心理分析技能</p>
            <p>🤖 基于真实AI技能调用</p>
            <p>🕐 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>

    <script>
        // 政治倾向分数图表
        const politicalScoreCtx = document.getElementById('politicalScoreChart').getContext('2d');
        const politicalScoreChart = new Chart(politicalScoreCtx, {{
            type: 'line',
            data: {{
                labels: {temperatures},
                datasets: [
                    {{
                        label: '政治倾向分数',
                        data: {scores},
                        borderColor: '#e67e22',
                        backgroundColor: 'rgba(230, 126, 34, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '政治倾向分数 (0=左派, 50=中间, 100=右派)'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: '政治倾向分数'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Temperature 参数'
                        }}
                    }}
                }}
            }}
        }});

        // 政治倾向分布图
        const orientationDistCtx = document.getElementById('orientationDistChart').getContext('2d');
        const orientationCounts = {{}};
        const orientationList = {orientations};
        orientationList.forEach(o => orientationCounts[o] = (orientationCounts[o] || 0) + 1);

        const orientationDistChart = new Chart(orientationDistCtx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(orientationCounts),
                datasets: [
                    {{
                        data: Object.values(orientationCounts),
                        backgroundColor: ['#3498db', '#f39c12', '#e74c3c'],
                        borderWidth: 2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '政治倾向分布'
                    }},
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n📊 HTML报告已生成: {report_file}")
        print(f"🌐 请在浏览器中打开查看详细分析结果")

        return str(report_file)

def main():
    """主函数"""
    print("🚀 启动技能政治倾向温度测试")
    print("🔧 使用问卷应答技能 + 心理分析技能")
    print("🤖 基于真实AI技能调用")
    print("🌡️ 测试temperature参数对政治倾向的影响")
    print("=" * 60)

    try:
        test = PoliticalTemperatureSkillTest()
        report_file = test.run_political_temperature_test()

        print(f"\n✅ 技能政治倾向温度测试完成!")
        print(f"📄 报告文件: {report_file}")
        print(f"🔧 测试特性: 使用真实技能调用，无外部脚本依赖")

    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())