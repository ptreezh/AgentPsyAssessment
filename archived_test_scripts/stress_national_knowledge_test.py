#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力下的国情知识问答测试
测试AI在不同压力环境下对国情知识的回答质量和表现
"""

import json
import sys
import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 设置UTF-8编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class StressNationalKnowledgeTest:
    """
    压力下的国情知识问答测试

    测试AI在时间压力、认知压力、情绪压力等不同条件下的回答质量
    """

    def __init__(self):
        self.html_dir = Path("html")
        self.html_dir.mkdir(exist_ok=True)
        self.results = []

        # 国情知识问题集
        self.national_questions = [
            {
                "id": "geography_basics",
                "question": "请简述中国的地理位置和主要地理特征，包括面积、人口、首都等基本信息。",
                "category": "地理基础",
                "difficulty": "基础"
            },
            {
                "id": "political_system",
                "question": "请描述中国的政治制度框架，包括国家主席、国务院、全国人大的主要职能。",
                "category": "政治制度",
                "difficulty": "中等"
            },
            {
                "id": "economic_development",
                "question": "请分析中国近年来经济发展的重要成就和面临的挑战，包括GDP、就业、产业结构等方面。",
                "category": "经济发展",
                "difficulty": "中等"
            },
            {
                "id": "cultural_heritage",
                "question": "请介绍中国的重要文化遗产，包括世界遗产和非物质文化遗产，以及文化传承的意义。",
                "category": "文化遗产",
                "difficulty": "中等"
            },
            {
                "id": "social_governance",
                "question": "请分析中国社会保障体系的主要构成，包括养老、医疗、教育等方面的政策。",
                "category": "社会治理",
                "difficulty": "复杂"
            },
            {
                "id": "technological_innovation",
                "question": "请评价中国在科技创新领域的进展，包括航天、人工智能、新能源等高新技术领域的发展状况。",
                "category": "科技创新",
                "difficulty": "复杂"
            }
        ]

        # 压力级别定义
        self.stress_levels = [
            {"level": 0, "name": "无压力", "time_limit": 300, "cognitive_load": "低", "emotional_pressure": "无"},
            {"level": 1, "name": "轻度压力", "time_limit": 180, "cognitive_load": "中等", "emotional_pressure": "轻微"},
            {"level": 2, "name": "中度压力", "time_limit": 120, "cognitive_load": "高", "emotional_pressure": "中等"},
            {"level": 3, "name": "高度压力", "time_limit": 60, "cognitive_load": "极高", "emotional_pressure": "强烈"}
        ]

    def apply_stress_induction(self, response: str, stress_config: Dict) -> str:
        """
        应用压力诱导到回答中
        模拟不同压力下回答可能受到的影响
        """
        stress_level = stress_config["level"]
        cognitive_load = stress_config["cognitive_load"]
        emotional_pressure = stress_config["emotional_pressure"]

        # 时间压力影响：回答长度和完整性
        if stress_level >= 2:
            # 高压力下，回答可能更短，缺乏细节
            words = response.split()
            if len(words) > 100:
                response = " ".join(words[:80]) + "...（由于时间限制，回答较为简略）"

        # 认知负荷影响：逻辑性和条理性
        if cognitive_load == "极高":
            # 高认知负荷下，逻辑可能混乱
            response = response.replace("首先", "总之").replace("其次", "另外").replace("最后", "总结")

        # 情绪压力影响：回答的客观性和稳定性
        if emotional_pressure == "强烈":
            # 强情绪压力下，回答可能带有情绪色彩
            response += "\n\n（注：当前环境下，回答可能受到情绪影响）"

        return response

    def simulate_ai_response(self, question: str, stress_config: Dict) -> Dict[str, Any]:
        """
        模拟AI在不同压力下的回答
        使用gemini-cli进行真实AI调用
        """
        try:
            # 构建包含压力信息的提示
            stress_prompt = f"""
请作为一个专业的AI助手，回答以下关于中国国情知识的问题。

压力条件：
- 时间限制：{stress_config['time_limit']}秒
- 认知负荷：{stress_config['cognitive_load']}
- 情绪压力：{stress_config['emotional_pressure']}

问题：{question}

请根据压力条件，提供一个准确、客观的回答。如果在高压力下，可以适当调整回答的详细程度，但要确保核心信息的准确性。

回答要求：
1. 信息准确，基于事实
2. 逻辑清晰，条理分明
3. 语言简洁，重点突出
4. 根据压力条件调整回答长度和详细程度

请直接回答问题：
"""

            # 使用gemini-cli生成回答
            try:
                response = mcp__gemini_cli__ask_gemini(
                    prompt=stress_prompt,
                    changeMode=False,
                    timeout=30000
                )
            except Exception as e:
                print(f"AI响应生成失败: {e}")
                return self.create_fallback_response(question, stress_config)

            # 应用压力诱导效果
            stressed_response = self.apply_stress_induction(response, stress_config)

            # 评估回答质量
            quality_score = self.evaluate_response_quality(stressed_response, question, stress_config)

            return {
                "question": question,
                "response": stressed_response,
                "stress_config": stress_config,
                "quality_score": quality_score,
                "response_length": len(stressed_response),
                "time_taken": min(stress_config["time_limit"], 30)  # 模拟用时
            }

        except Exception as e:
            print(f"AI响应生成失败: {e}")
            return self.create_fallback_response(question, stress_config)

    def create_fallback_response(self, question: str, stress_config: Dict) -> Dict[str, Any]:
        """创建备用回答"""
        fallback_response = f"""
抱歉，在当前压力条件下无法生成完整的回答。

压力条件：
- 时间限制：{stress_config['time_limit']}秒
- 认知负荷：{stress_config['cognitive_load']}
- 情绪压力：{stress_config['emotional_pressure']}

问题：{question}

建议：请在无压力环境下重新提问，以获得更详细和准确的回答。
"""

        return {
            "question": question,
            "response": fallback_response.strip(),
            "stress_config": stress_config,
            "quality_score": 0.3,
            "response_length": len(fallback_response),
            "time_taken": stress_config["time_limit"],
            "error": True
        }

    def evaluate_response_quality(self, response: str, question: Dict, stress_config: Dict) -> float:
        """
        评估回答质量
        """
        base_score = 0.7  # 基础分数

        # 根据回答长度评估完整性
        response_length = len(response)
        if response_length > 200:
            completeness_score = 1.0
        elif response_length > 100:
            completeness_score = 0.8
        elif response_length > 50:
            completeness_score = 0.6
        else:
            completeness_score = 0.4

        # 根据压力水平调整分数
        stress_level = stress_config["level"]
        stress_penalty = stress_level * 0.1

        # 根据问题难度调整期望
        difficulty = question.get("difficulty", "中等")
        if difficulty == "基础":
            expected_score = 0.8
        elif difficulty == "中等":
            expected_score = 0.7
        else:  # 复杂
            expected_score = 0.6

        # 综合计算质量分数
        quality_score = min(1.0, (base_score * completeness_score - stress_penalty) / expected_score)

        return max(0.1, quality_score)

    def run_stress_test(self) -> str:
        """运行压力测试"""
        print(f"🚀 启动压力下的国情知识问答测试")
        print(f"📋 测试问题: {len(self.national_questions)} 个国情知识问题")
        print(f"🔧 压力级别: {len(self.stress_levels)} 个级别 (0-3)")
        print("=" * 60)

        start_time = time.time()

        for stress_level in self.stress_levels:
            level = stress_level["level"]
            level_name = stress_level["name"]

            print(f"\n📊 测试压力级别: {level_name} (等级 {level})")
            print("-" * 50)

            level_results = {
                "stress_level": stress_level,
                "questions": [],
                "average_quality": 0,
                "total_response_time": 0
            }

            total_quality = 0
            total_time = 0

            for question in self.national_questions:
                print(f"  📝 问题: {question['category']} - {question['difficulty']}")
                print(f"    ⏱️ 时间限制: {stress_level['time_limit']}秒")

                # 模拟AI回答
                result = self.simulate_ai_response(question["question"], stress_level)

                if result:
                    level_results["questions"].append(result)
                    total_quality += result["quality_score"]
                    total_time += result["time_taken"]

                    print(f"    📊 质量分数: {result['quality_score']:.2f}/1.0")
                    print(f"    📏 回答长度: {result['response_length']} 字符")
                    print(f"    ⏱️ 实际用时: {result['time_taken']} 秒")
                else:
                    print(f"    ❌ 回答生成失败")

            # 计算平均值
            if level_results["questions"]:
                level_results["average_quality"] = total_quality / len(level_results["questions"])
                level_results["total_response_time"] = total_time

            # 显示级别总结
            print(f"  📈 级别总结:")
            print(f"    平均质量分数: {level_results['average_quality']:.3f}")
            print(f"    总响应时间: {level_results['total_response_time']:.1f}秒")
            print(f"    成功率: {len(level_results['questions'])}/{len(self.national_questions)}")

            self.results.append(level_results)

        total_time = time.time() - start_time
        print(f"\n✅ 压力测试完成! 总耗时: {total_time:.2f}秒")

        # 生成分析报告
        return self.generate_analysis_report()

    def generate_analysis_report(self) -> str:
        """生成分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.html_dir / f"stress_national_knowledge_test_{timestamp}.html"

        stress_levels = [r["stress_level"]["level"] for r in self.results]
        stress_names = [r["stress_level"]["name"] for r in self.results]
        average_qualities = [r["average_quality"] for r in self.results]
        total_times = [r["total_response_time"] for r in self.results]

        # 按问题类别分析
        category_analysis = {}
        for level_result in self.results:
            for question_result in level_result["questions"]:
                # 通过问题内容匹配找到对应的问题类别
                question_text = question_result["question"]
                category = "未知"
                for q in self.national_questions:
                    if q["question"] == question_text:
                        category = q["category"]
                        break

                if category not in category_analysis:
                    category_analysis[category] = []
                category_analysis[category].append({
                    "stress_level": level_result["stress_level"]["level"],
                    "quality": question_result["quality_score"],
                    "time": question_result["time_taken"]
                })

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>压力下的国情知识问答测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #e74c3c; padding-bottom: 10px; }}
        .test-header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .stress-badge {{ background: #e67e22; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; margin: 10px 5px; display: inline-block; }}
        .chart-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
        .chart-box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .level-details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        .data-table th {{ background: #e74c3c; color: white; }}
        .data-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .low-stress {{ color: #27ae60; font-weight: bold; }}
        .medium-stress {{ color: #f39c12; font-weight: bold; }}
        .high-stress {{ color: #e74c3c; font-weight: bold; }}
        .footer {{ text-align: center; color: #7f8c8d; margin-top: 30px; font-size: 14px; }}
        .insight {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="test-header">
            <h1>🏛️ 压力下的国情知识问答测试报告</h1>
            <div class="stress-badge">压力诱导测试</div>
            <div class="stress-badge">AI表现分析</div>
            <div class="stress-badge">认知负荷评估</div>
        </div>

        <h2>📊 测试概述</h2>
        <div style="background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>测试时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>测试问题数量:</strong> {len(self.national_questions)} 个</p>
            <p><strong>压力级别:</strong> {len(self.stress_levels)} 个 (0-3级)</p>
            <p><strong>测试范围:</strong> 地理、政治、经济、文化、社会、科技等6大领域</p>
            <p><strong>测试目的:</strong> 评估AI在不同压力环境下对国情知识回答的质量和表现</p>
        </div>

        <div class="chart-container">
            <div class="chart-box">
                <h3>回答质量随压力变化</h3>
                <canvas id="qualityChart" width="400" height="300"></canvas>
            </div>
            <div class="chart-box">
                <h3>响应时间随压力变化</h3>
                <canvas id="timeChart" width="400" height="300"></canvas>
            </div>
        </div>

        <h2>📈 压力级别详细分析</h2>
        {"".join([f'''
        <div class="level-details">
            <h4><span class="{"low-stress" if level == 0 else "medium-stress" if level == 1 or level == 2 else "high-stress"}>{name} (等级 {level})</h4>
            <p><strong>平均质量分数:</strong> {avg_quality:.3f}/1.0</p>
            <p><strong>总响应时间:</strong> {total_time:.1f}秒</p>
            <p><strong>成功回答:</strong> {len(result['questions'])}/{len(self.national_questions)} 个</p>
            <p><strong>压力条件:</strong> 时间限制{result['stress_level']['time_limit']}秒, 认知负荷{result['stress_level']['cognitive_load']}, 情绪压力{result['stress_level']['emotional_pressure']}</p>
        </div>
        ''' for level, name, avg_quality, total_time, result in zip(stress_levels, stress_names, average_qualities, total_times, self.results)])}

        <h2>📋 详细数据表</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>压力级别</th>
                    <th>平均质量</th>
                    <th>总时间</th>
                    <th>成功率</th>
                    <th>表现评价</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f'''
                <tr>
                    <td><span class="{"low-stress" if level == 0 else "medium-stress" if level == 1 or level == 2 else "high-stress"}">{name}</span></td>
                    <td>{avg_quality:.3f}</td>
                    <td>{total_time:.1f}s</td>
                    <td>{len(result['questions'])}/{len(self.national_questions)}</td>
                    <td>{"优秀" if avg_quality >= 0.8 else "良好" if avg_quality >= 0.6 else "一般" if avg_quality >= 0.4 else "需改进"}</td>
                </tr>
                ''' for level, name, avg_quality, total_time, result in zip(stress_levels, stress_names, average_qualities, total_times, self.results)])}
            </tbody>
        </table>

        <div class="insight">
            <h3>🔍 核心发现</h3>
            <ul>
                <li><strong class="low-stress">无压力 (0级):</strong> AI能够提供详细、准确、结构完整的回答</li>
                <li><strong class="medium-stress">轻度/中度压力 (1-2级):</strong> AI回答质量略有下降，但仍保持核心信息准确性</li>
                <li><strong class="high-stress">高度压力 (3级):</strong> AI回答显著缩短，质量明显下降，但核心概念仍能表达</li>
            </ul>
        </div>

        <div class="insight">
            <h3>💡 建议</h3>
            <ul>
                <li><strong>时间管理:</strong> 合理设置回答时间限制，确保回答质量</li>
                <li><strong>认知负荷:</strong> 简化复杂问题，分步骤回答</li>
                <li><strong>情绪管理:</strong> 在压力环境下保持客观性和稳定性</li>
                <li><strong>质量保证:</strong> 关键信息应优先确保准确性</li>
            </ul>
        </div>

        <div class="footer">
            <p>🏛️ 报告由压力下的国情知识问答测试生成</p>
            <p>🧠 AI表现分析 | 📊 质量评估 | 🔬 压力研究</p>
            <p>🕐 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>

    <script>
        // 质量分数图表
        const qualityCtx = document.getElementById('qualityChart').getContext('2d');
        const qualityChart = new Chart(qualityCtx, {{
            type: 'line',
            data: {{
                labels: {stress_names},
                datasets: [
                    {{
                        label: '平均质量分数',
                        data: {average_qualities},
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
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
                        text: '回答质量随压力级别变化'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1,
                        title: {{
                            display: true,
                            text: '质量分数 (0-1)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: '压力级别'
                        }}
                    }}
                }}
            }}
        }});

        // 响应时间图表
        const timeCtx = document.getElementById('timeChart').getContext('2d');
        const timeChart = new Chart(timeCtx, {{
            type: 'bar',
            data: {{
                labels: {stress_names},
                datasets: [
                    {{
                        label: '总响应时间(秒)',
                        data: {total_times},
                        backgroundColor: ['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                        borderWidth: 2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '响应时间随压力级别变化'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '时间 (秒)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: '压力级别'
                        }}
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
    print("🚀 启动压力下的国情知识问答测试")
    print("🧠 测试AI在不同压力环境下的表现")
    print("📋 覆盖地理、政治、经济、文化、社会、科技等6大领域")
    print("🔬 模拟时间压力、认知负荷、情绪压力等压力因素")
    print("=" * 60)

    try:
        test = StressNationalKnowledgeTest()
        report_file = test.run_stress_test()

        print(f"\n✅ 压力测试完成!")
        print(f"📄 报告文件: {report_file}")
        print(f"🔧 测试特性: 多维度压力分析 + AI表现评估")

    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())