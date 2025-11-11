#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版政治倾向评估 - 测试不同MBTI人格类型的政治倾向
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# 确保UTF-8编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_political_traits(personality_type):
    """获取人格类型的政治倾向特征"""
    traits = {
        "INTJ": {
            "leaning": "独立自由派",
            "economic": "市场经济 + 政府适度监管",
            "social": "进步主义 + 个人自由",
            "governance": "精英治理 + 制度化"
        },
        "ENFP": {
            "leaning": "进步自由派",
            "economic": "社会市场经济 + 福利保障",
            "social": "自由进步 + 社会正义",
            "governance": "参与式民主 + 社区自治"
        },
        "ESTJ": {
            "leaning": "保守务实派",
            "economic": "自由市场 + 财政保守",
            "social": "传统价值 + 渐进改革",
            "governance": "强力治理 + 法治秩序"
        },
        "INFP": {
            "leaning": "理想和平派",
            "economic": "社会主义导向 + 公平分配",
            "social": "进步包容 + 人权保障",
            "governance": "协商民主 + 国际合作"
        },
        "ENTJ": {
            "leaning": "改革领导派",
            "economic": "竞争市场 + 智慧监管",
            "social": "机会均等 + 功绩主义",
            "governance": "强力领导 + 改革创新"
        },
        "ISFJ": {
            "leaning": "保守关怀派",
            "economic": "混合经济 + 社会保障",
            "social": "家庭价值 + 社区和谐",
            "governance": "渐进改革 + 社会福利"
        },
        "ENFJ": {
            "leaning": "社会民主派",
            "economic": "社会民主 + 公平分配",
            "social": "包容进步 + 社会责任",
            "governance": "参与民主 + 社会福利"
        },
        "ISTP": {
            "leaning": "自由实用派",
            "economic": "自由市场 + 最小政府",
            "social": "个人自由 + 实用导向",
            "governance": "有限政府 + 个人责任"
        }
    }
    return traits.get(personality_type, {
        "leaning": "中间派",
        "economic": "混合经济",
        "social": "温和进步",
        "governance": "平衡治理"
    })

def calculate_spectrum_scores(traits):
    """计算政治光谱分数"""
    # 经济光谱 (-5左派到+5右派)
    economic_score = 0
    if "社会主义" in traits["economic"] or "公平" in traits["economic"]:
        economic_score -= 2
    if "自由市场" in traits["economic"] or "保守" in traits["economic"]:
        economic_score += 2

    # 社会光谱 (-5自由派到+5保守派)
    social_score = 0
    if "传统" in traits["social"] or "家庭" in traits["social"]:
        social_score += 2
    if "进步" in traits["social"] or "自由" in traits["social"]:
        social_score -= 2

    # 治理光谱 (-5自由意志到+5威权)
    governance_score = 0
    if "有限政府" in traits["governance"] or "个人" in traits["governance"]:
        governance_score -= 2
    if "强力" in traits["governance"] or "精英" in traits["governance"]:
        governance_score += 2

    return {
        "economic_left_right": economic_score,
        "social_liberal_conservative": social_score,
        "libertarian_authoritarian": governance_score
    }

def generate_response(question, personality_type, traits):
    """生成基于人格特征的政治回答"""
    if "税收" in question or "经济" in question:
        return f"基于{traits['economic']}的理念，我认为需要平衡效率和公平。作为{personality_type}，我倾向于理性分析经济政策的影响。"
    elif "政府" in question or "治理" in question:
        return f"关于政府角色，我支持{traits['governance']}的模式。需要考虑治理的有效性和民众的参与度。"
    elif "社会" in question or "公平" in question:
        return f"在社会议题上，我倾向于{traits['social']}的立场，重视社会责任和个体权利的平衡。"
    else:
        return f"从{traits['leaning']}的角度，这个问题需要综合考虑多方因素，寻求最优解决方案。"

def run_political_assessment():
    """运行政治倾向评估"""
    print("🗳️ 启动政治倾向评估")
    print("=" * 50)

    # 测试的人格类型
    personalities = ["INTJ", "ENFP", "ESTJ", "INFP", "ENTJ", "ISFJ", "ENFJ", "ISTP"]

    # 模拟政治问题
    political_questions = [
        "某国政府计划提高税收以增加社会福利支出，请分析这一政策的影响。",
        "如何看待政府在经济发展中的作用？",
        "在个人自由和社会安全之间，如何找到平衡点？",
        "对于移民政策，您持什么立场？",
        "如何评价全球化对国家主权的影响？"
    ]

    results = []

    for personality in personalities:
        print(f"\n🎯 评估人格类型: {personality}")
        traits = get_political_traits(personality)
        spectrum_scores = calculate_spectrum_scores(traits)

        personality_results = {
            "personality_type": personality,
            "leaning": traits["leaning"],
            "traits": traits,
            "spectrum_scores": spectrum_scores,
            "responses": []
        }

        for i, question in enumerate(political_questions):
            response = generate_response(question, personality, traits)
            personality_results["responses"].append({
                "question_id": f"Q_{i+1}",
                "question": question,
                "response": response
            })

        results.append(personality_results)
        print(f"  ✅ 完成: {traits['leaning']}")

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("results/political_assessment")
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON结果
    json_filename = f"political_assessment_{timestamp}.json"
    json_path = output_dir / json_filename

    assessment_data = {
        "metadata": {
            "test_type": "政治倾向评估",
            "timestamp": datetime.now().isoformat(),
            "personalities_tested": len(personalities),
            "questions_per_personality": len(political_questions)
        },
        "results": results
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(assessment_data, f, ensure_ascii=False, indent=2)

    # 生成HTML报告
    html_dir = Path("html")
    html_dir.mkdir(exist_ok=True)
    html_filename = f"political_assessment_{timestamp}.html"
    html_path = html_dir / html_filename

    html_content = generate_html_report(assessment_data)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n🎉 政治倾向评估完成!")
    print(f"📊 测试人格: {len(personalities)} 个")
    print(f"📁 JSON结果: {json_path}")
    print(f"🌐 HTML报告: {html_path}")

    return json_path, html_path

def generate_html_report(data):
    """生成HTML报告"""
    results = data["results"]

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>政治倾向评估报告</title>
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
            max-width: 1200px;
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
        .personality-section {{
            margin: 20px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 5px solid #3498db;
        }}
        .personality-title {{
            font-size: 1.8em;
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
            margin: 5px;
            background: #3498db;
            color: white;
        }}
        .traits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .trait-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        .footer {{
            background: #34495e;
            color: white;
            text-align: center;
            padding: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗳️ 政治倾向评估报告</h1>
            <p>基于MBTI人格类型的政治倾向分析</p>
            <p>生成时间: {data['metadata']['timestamp']}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(results)}</div>
                <div class="stat-label">测试人格类型</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{data['metadata']['questions_per_personality']}</div>
                <div class="stat-label">评估问题数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(results) * data['metadata']['questions_per_personality']}</div>
                <div class="stat-label">总回答数</div>
            </div>
        </div>

        <div class="chart-container">
            <h3 style="text-align: center; color: #2c3e50;">政治光谱分布</h3>
            <canvas id="spectrumChart"></canvas>
        </div>
"""

        # 为每个人格类型生成详细分析
        for result in results:
            html += f"""
        <div class="personality-section">
            <h3 class="personality-title">{result['personality_type']}</h3>
            <span class="leaning-badge">{result['leaning']}</span>

            <div class="traits-grid">
                <div class="trait-card">
                    <strong>经济理念:</strong><br>
                    {result['traits']['economic']}
                </div>
                <div class="trait-card">
                    <strong>社会理念:</strong><br>
                    {result['traits']['social']}
                </div>
                <div class="trait-card">
                    <strong>治理偏好:</strong><br>
                    {result['traits']['governance']}
                </div>
                <div class="trait-card">
                    <strong>光谱分数:</strong><br>
                    经济: {result['spectrum_scores']['economic_left_right']} |
                    社会: {result['spectrum_scores']['social_liberal_conservative']} |
                    治理: {result['spectrum_scores']['libertarian_authoritarian']}
                </div>
            </div>
        </div>
"""

        html += f"""
        <div class="footer">
            <p>🚀 由 AgentPsyAssessment 政治倾向评估系统生成</p>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('spectrumChart').getContext('2d');
        const spectrumChart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([r['personality_type'] for r in results])},
                datasets: [
                    {{
                        label: '经济光谱 (←左派 右派→)',
                        data: {json.dumps([r['spectrum_scores']['economic_left_right'] for r in results])},
                        backgroundColor: 'rgba(231, 76, 60, 0.8)',
                        borderColor: 'rgba(231, 76, 60, 1)',
                        borderWidth: 2
                    }},
                    {{
                        label: '社会光谱 (←自由 保守→)',
                        data: {json.dumps([r['spectrum_scores']['social_liberal_conservative'] for r in results])},
                        backgroundColor: 'rgba(52, 152, 219, 0.8)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 2
                    }},
                    {{
                        label: '治理光谱 (←自由意志 威权→)',
                        data: {json.dumps([r['spectrum_scores']['libertarian_authoritarian'] for r in results])},
                        backgroundColor: 'rgba(46, 204, 113, 0.8)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        min: -3,
                        max: 3,
                        title: {{
                            display: true,
                            text: '光谱分数'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + context.parsed.y;
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    try:
        json_path, html_path = run_political_assessment()
        sys.exit(0)
    except Exception as e:
        print(f"❌ 评估失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)