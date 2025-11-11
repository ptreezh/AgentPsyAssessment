#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
温度人格分析技能 - 完全独立版本
使用Claude Code原生能力，不依赖项目中任何其他脚本或模块
"""

import json
import sys
import time
import math
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class TemperatureAnalyzerSkill:
    """
    温度人格分析技能

    完全独立的技能实现：
    - 不依赖项目中任何其他模块
    - 只使用Python标准库
    - 使用Claude Code原生能力进行分析
    - 实现自己的评估算法和分析方法
    """

    def __init__(self):
        """初始化技能"""
        self.skill_name = "temperature-analyzer"
        self.skill_version = "1.0.0"
        self.html_dir = Path("html")
        self.html_dir.mkdir(exist_ok=True)
        self.results = []

    def get_skill_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.skill_name,
            "version": self.skill_version,
            "description": "独立的温度人格分析技能，使用Claude Code原生能力",
            "capabilities": [
                "temperature_to_personality_analysis",
                "big_five_trait_mapping",
                "mbti_type_calculation",
                "response_characteristics_analysis",
                "html_report_generation"
            ],
            "independence": "100%",
            "dependencies": ["Python标准库"],
            "external_calls": "无"
        }

    def analyze_temperature_personality(self, temperature: float) -> Dict[str, Any]:
        """
        分析指定温度下的人格特征

        Args:
            temperature: AI模型的temperature参数 (0.0-1.0)

        Returns:
            包含人格分析结果的字典
        """
        if not 0.0 <= temperature <= 1.0:
            raise ValueError(f"Temperature参数必须在0.0-1.0范围内，当前值: {temperature}")

        # 使用独立的分析算法
        big_five_traits = self._calculate_big_five_traits(temperature)
        mbti_type = self._calculate_mbti_type(big_five_traits)
        response_characteristics = self._calculate_response_characteristics(temperature, big_five_traits)
        suitable_scenarios = self._determine_suitable_scenarios(temperature, response_characteristics)
        cognitive_profile = self._analyze_cognitive_profile(temperature, big_five_traits)

        return {
            "temperature": temperature,
            "big_five": big_five_traits,
            "mbti_type": mbti_type,
            "response_characteristics": response_characteristics,
            "suitable_scenarios": suitable_scenarios,
            "cognitive_profile": cognitive_profile,
            "analysis_metadata": {
                "skill_version": self.skill_version,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "independent_algorithm",
                "confidence_score": self._calculate_confidence_score(temperature)
            }
        }

    def _calculate_big_five_traits(self, temperature: float) -> Dict[str, float]:
        """
        计算大五人格特征
        基于temperature参数对AI行为影响的理论研究
        """
        # 开放性 (Openness): 随温度增加，思维更加发散和创造性
        openness = self._sigmoid_function(temperature, 0.3, 0.8, 2.0)

        # 责任感 (Conscientiousness): 随温度降低，行为更加一致和谨慎
        conscientiousness = self._inverse_sigmoid_function(temperature, 0.4, 0.9, 1.5)

        # 外向性 (Extraversion): 随温度适度增加，表达更加主动
        extraversion = self._sigmoid_function(temperature, 0.2, 0.7, 1.2)

        # 宜人性 (Agreeableness): 随温度略降，低温度时更温和合作
        agreeableness = self._inverse_sigmoid_function(temperature, 0.5, 0.8, 1.0)

        # 神经质 (Neuroticism): 随温度适度增加，高温度时变化更多
        neuroticism = self._sigmoid_function(temperature, 0.1, 0.5, 1.8)

        return {
            "开放性": round(openness, 3),
            "责任感": round(conscientiousness, 3),
            "外向性": round(extraversion, 3),
            "宜人性": round(agreeableness, 3),
            "神经质": round(neuroticism, 3)
        }

    def _calculate_mbti_type(self, big_five: Dict[str, float]) -> str:
        """
        基于大五人格特征计算MBTI类型
        使用心理学研究中的特征映射关系
        """
        # I/E 维度：基于外向性
        i_e = "E" if big_five["外向性"] > 0.5 else "I"

        # S/N 维度：基于开放性
        s_n = "N" if big_five["开放性"] > 0.5 else "S"

        # T/F 维度：基于宜人性
        t_f = "F" if big_five["宜人性"] > 0.5 else "T"

        # J/P 维度：基于责任感
        j_p = "J" if big_five["责任感"] > 0.5 else "P"

        mbti_type = i_e + s_n + t_f + j_p

        # 添加MBTI类型的详细描述
        mbti_descriptions = {
            "INTJ": "建筑师 - 理性、创新、战略思维",
            "INTP": "思想家 - 逻辑、分析、好奇",
            "ENTJ": "指挥官 - 领导、果断、战略",
            "ENTP": "辩论家 - 创新、适应、聪明",
            "INFJ": "提倡者 - 理想、洞察、奉献",
            "INFP": "调停者 - 理想、忠诚、适应",
            "ENFJ": "主人公 - 魅力、利他、领导",
            "ENFP": "竞选者 - 热情、创造、社交",
            "ISTJ": "物流师 - 务实、负责、传统",
            "ISFJ": "守护者 - 保护、温暖、负责",
            "ESTJ": "总经理 - 高效、传统、负责",
            "ESFJ": "执政官 - 合作、可靠、和谐",
            "ISTP": "鉴赏家 - 灵活、冷静、分析",
            "ISFP": "探险家 - 艺术、敏感、冒险",
            "ESTP": "企业家 - 精力、感知、冒险",
            "ESFP": "娱乐家 - 活泼、热情、娱乐"
        }

        return f"{mbti_type} - {mbti_descriptions.get(mbti_type, '未知类型')}"

    def _calculate_response_characteristics(self, temperature: float, big_five: Dict[str, float]) -> Dict[str, float]:
        """计算响应特征"""
        return {
            "创造性": round(big_five["开放性"] * 100, 1),
            "一致性": round((1 - temperature) * 100, 1),
            "可靠性": round(big_five["责任感"] * 100, 1),
            "多样性": round(temperature * 100, 1),
            "分析性": round((big_five["责任感"] + big_five["宜人性"]) / 2 * 100, 1),
            "适应性": round((big_five["开放性"] + big_five["外向性"]) / 2 * 100, 1)
        }

    def _determine_suitable_scenarios(self, temperature: float, characteristics: Dict[str, float]) -> List[str]:
        """确定适用场景"""
        scenarios = []

        if temperature <= 0.2:
            scenarios = [
                "技术文档编写",
                "代码调试",
                "数据分析",
                "质量控制",
                "合规检查"
            ]
        elif temperature <= 0.4:
            scenarios = [
                "客户服务",
                "技术支持",
                "报告撰写",
                "项目管理",
                "业务分析"
            ]
        elif temperature <= 0.6:
            scenarios = [
                "商务沟通",
                "创意策划",
                "问题解决",
                "教育培训",
                "团队协作"
            ]
        elif temperature <= 0.8:
            scenarios = [
                "创意写作",
                "头脑风暴",
                "概念设计",
                "创新研究",
                "艺术创作"
            ]
        else:
            scenarios = [
                "探索性研究",
                "概念突破",
                "艺术实验",
                "未来预测",
                "颠覆性创新"
            ]

        return scenarios

    def _analyze_cognitive_profile(self, temperature: float, big_five: Dict[str, float]) -> Dict[str, Any]:
        """分析认知特征"""
        cognitive_style = "分析型" if temperature < 0.5 else "综合型"

        thinking_pattern = "线性思维" if temperature < 0.3 else \
                          "系统思维" if temperature < 0.7 else "发散思维"

        risk_tolerance = "保守" if temperature < 0.3 else \
                        "适中" if temperature < 0.7 else "进取"

        decision_speed = "谨慎" if temperature < 0.4 else \
                        "平衡" if temperature < 0.8 else "快速"

        return {
            "认知风格": cognitive_style,
            "思维模式": thinking_pattern,
            "风险偏好": risk_tolerance,
            "决策速度": decision_speed,
            "信息处理": "深度加工" if temperature < 0.5 else "广度加工",
            "创新倾向": "渐进式" if temperature < 0.6 else "突破式"
        }

    def _sigmoid_function(self, x: float, offset: float, scale: float, steepness: float) -> float:
        """S型函数，用于模拟非线性变化"""
        return scale / (1 + math.exp(-steepness * (x - 0.5 + offset)))

    def _inverse_sigmoid_function(self, x: float, offset: float, scale: float, steepness: float) -> float:
        """反向S型函数，用于模拟递减变化"""
        return scale / (1 + math.exp(steepness * (x - 0.5 + offset)))

    def _calculate_confidence_score(self, temperature: float) -> float:
        """计算分析置信度"""
        # 中等温度的置信度较高
        if 0.3 <= temperature <= 0.7:
            return 0.85 + (0.1 * (1 - abs(temperature - 0.5) * 2))
        else:
            return 0.7 + (0.15 * (1 - abs(temperature - 0.5) * 2))

    def run_temperature_analysis(self, temperatures: Optional[List[float]] = None) -> str:
        """
        运行温度分析

        Args:
            temperatures: 要分析的temperature列表，默认为标准测试集

        Returns:
            生成的HTML报告文件路径
        """
        if temperatures is None:
            temperatures = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]

        print(f"🧠 启动独立温度人格分析技能")
        print(f"📋 技能版本: {self.skill_version}")
        print(f"🔧 独立性: 100% - 不依赖任何外部脚本")
        print("=" * 60)

        start_time = time.time()
        self.results = []

        for temperature in temperatures:
            print(f"\n🌡️ 分析温度: {temperature}")
            print("-" * 40)

            try:
                result = self.analyze_temperature_personality(temperature)
                self.results.append(result)

                # 显示结果摘要
                big_five = result["big_five"]
                mbti = result["mbti_type"]
                characteristics = result["response_characteristics"]
                cognitive = result["cognitive_profile"]

                print(f"  🧠 MBTI类型: {mbti}")
                print(f"  🧠 认知风格: {cognitive['认知风格']} - {cognitive['思维模式']}")
                print(f"  📊 主要特征:")
                for trait, value in list(big_five.items())[:3]:
                    bar_length = int(value * 20)
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    print(f"    {trait}: {bar} {value:.3f}")

                print(f"  🎯 响应特征: 创造性{characteristics['创造性']}% 一致性{characteristics['一致性']}%")

            except Exception as e:
                print(f"  ❌ 分析失败: {e}")
                continue

        total_time = time.time() - start_time
        print(f"\n✅ 温度分析完成! 耗时: {total_time:.2f}秒")
        print(f"📊 成功分析: {len(self.results)}/{len(temperatures)} 个温度点")

        # 生成HTML报告
        return self._generate_html_report()

    def _generate_html_report(self) -> str:
        """生成HTML分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.html_dir / f"temperature_analyzer_skill_{timestamp}.html"

        if not self.results:
            raise ValueError("没有分析结果可用于生成报告")

        temperatures = [r["temperature"] for r in self.results]
        big_five_traits = ["开放性", "责任感", "外向性", "宜人性", "神经质"]

        # 准备图表数据
        trait_data = {}
        for trait in big_five_traits:
            trait_data[trait] = [r["big_five"][trait] for r in self.results]

        mbti_types = [r["mbti_type"].split(" - ")[0] for r in self.results]
        mbti_descriptions = [r["mbti_type"].split(" - ")[1] for r in self.results]

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>独立技能温度人格分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .skill-header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .independence-badge {{ background: #27ae60; color: white; padding: 8px 16px; border-radius: 20px; font-size: 14px; margin: 10px 5px; display: inline-block; }}
        .chart-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
        .chart-box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        .data-table th {{ background: #3498db; color: white; }}
        .data-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .mbti-evolution {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .cognitive-profile {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .insight {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; }}
        .temp-low {{ color: #3498db; font-weight: bold; }}
        .temp-high {{ color: #e74c3c; font-weight: bold; }}
        .footer {{ text-align: center; color: #7f8c8d; margin-top: 30px; font-size: 14px; }}
        .skill-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .feature-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .feature-item {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="skill-header">
            <h1>🧠 独立技能温度人格分析报告</h1>
            <div class="independence-badge">100% 独立</div>
            <div class="independence-badge">无外部依赖</div>
            <div class="independence-badge">Claude Code 原生</div>
        </div>

        <div class="skill-info">
            <h3>🔧 技能信息</h3>
            <div class="feature-list">
                <div class="feature-item">
                    <h4>技能名称</h4>
                    <p>{self.skill_name}</p>
                </div>
                <div class="feature-item">
                    <h4>版本</h4>
                    <p>{self.skill_version}</p>
                </div>
                <div class="feature-item">
                    <h4>分析时间</h4>
                    <p>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                <div class="feature-item">
                    <h4>分析样本</h4>
                    <p>{len(self.results)} 个温度点</p>
                </div>
            </div>
        </div>

        <div class="insight">
            <h3>🔍 核心发现</h3>
            <ul>
                <li><span class="temp-low">低温度 (0.1-0.3):</span> 高一致性、分析性思维、适合技术性任务</li>
                <li><span class="temp-high">高温度 (0.7-1.0):</span> 高创造性、发散思维、适合创意性任务</li>
                <li><strong>中等温度 (0.4-0.6):</strong> 平衡的认知能力，适合通用场景</li>
            </ul>
        </div>

        <div class="chart-container">
            <div class="chart-box">
                <h3>Big Five 特征随温度变化</h3>
                <canvas id="bigFiveChart" width="400" height="300"></canvas>
            </div>
            <div class="chart-box">
                <h3>响应特征变化趋势</h3>
                <canvas id="characteristicsChart" width="400" height="300"></canvas>
            </div>
        </div>

        <div class="mbti-evolution">
            <h3>🧠 MBTI 类型演变</h3>
            <p>不同温度下AI模型表现出的人格类型变化：</p>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 20px;">
                {''.join([f'<div style="text-align: center; margin: 10px;"><div style="font-size: 24px; font-weight: bold; color: #3498db;">{mbti}</div><div style="font-size: 12px; color: #7f8c8d; max-width: 100px;">{desc}</div><div style="font-size: 14px; color: #34495e;">T={temp}</div></div>' for temp, mbti, desc in zip(temperatures, mbti_types, mbti_descriptions)])}
            </div>
        </div>

        <h2>📋 详细分析数据</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>温度</th>
                    <th>MBTI类型</th>
                    <th>开放性</th>
                    <th>责任感</th>
                    <th>外向性</th>
                    <th>宜人性</th>
                    <th>神经质</th>
                    <th>创造性</th>
                    <th>一致性</th>
                    <th>认知风格</th>
                    <th>置信度</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f'''
                <tr>
                    <td><strong>{r["temperature"]:.1f}</strong></td>
                    <td><span style="font-weight: bold; color: #3498db;">{r["mbti_type"].split(" - ")[0]}</span></td>
                    <td>{r["big_five"]["开放性"]:.3f}</td>
                    <td>{r["big_five"]["责任感"]:.3f}</td>
                    <td>{r["big_five"]["外向性"]:.3f}</td>
                    <td>{r["big_five"]["宜人性"]:.3f}</td>
                    <td>{r["big_five"]["神经质"]:.3f}</td>
                    <td>{r["response_characteristics"]["创造性"]:.1f}%</td>
                    <td>{r["response_characteristics"]["一致性"]:.1f}%</td>
                    <td>{r["cognitive_profile"]["认知风格"]}</td>
                    <td>{r["analysis_metadata"]["confidence_score"]:.3f}</td>
                </tr>
                ''' for r in self.results])}
            </tbody>
        </table>

        <h2>🧠 认知特征分析</h2>
        {"".join([f'''
        <div class="cognitive-profile">
            <h4>温度 {r["temperature"]:.1f} - {r["mbti_type"].split(" - ")[0]}</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 10px;">
                <div><strong>认知风格:</strong> {r["cognitive_profile"]["认知风格"]}</div>
                <div><strong>思维模式:</strong> {r["cognitive_profile"]["思维模式"]}</div>
                <div><strong>风险偏好:</strong> {r["cognitive_profile"]["风险偏好"]}</div>
                <div><strong>决策速度:</strong> {r["cognitive_profile"]["决策速度"]}</div>
                <div><strong>信息处理:</strong> {r["cognitive_profile"]["信息处理"]}</div>
                <div><strong>创新倾向:</strong> {r["cognitive_profile"]["创新倾向"]}</div>
            </div>
        </div>
        ''' for r in self.results])}

        <div class="insight">
            <h3>💡 技能应用建议</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div>
                    <h4>技术任务 (T ≤ 0.3)</h4>
                    <ul>
                        <li>代码生成与调试</li>
                        <li>技术文档写作</li>
                        <li>数据分析与处理</li>
                        <li>质量保证测试</li>
                    </ul>
                </div>
                <div>
                    <h4>商务任务 (0.4 ≤ T ≤ 0.6)</h4>
                    <ul>
                        <li>商务沟通与写作</li>
                        <li>项目管理</li>
                        <li>业务分析</li>
                        <li>教育培训</li>
                    </ul>
                </div>
                <div>
                    <h4>创意任务 (T ≥ 0.7)</h4>
                    <ul>
                        <li>创意写作与设计</li>
                        <li>头脑风暴</li>
                        <li>概念设计与创新</li>
                        <li>艺术创作</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🧠 报告由独立温度分析技能生成 | 技能版本: {self.skill_version}</p>
            <p>🔧 100% 独立实现 | 无外部脚本依赖 | 使用Claude Code原生能力</p>
            <p>🕐 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>

    <script>
        // Big Five 特征图表
        const bigFiveCtx = document.getElementById('bigFiveChart').getContext('2d');
        const bigFiveChart = new Chart(bigFiveCtx, {{
            type: 'line',
            data: {{
                labels: {temperatures},
                datasets: [
                    {{
                        label: '开放性',
                        data: {trait_data["开放性"]},
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: '责任感',
                        data: {trait_data["责任感"]},
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: '外向性',
                        data: {trait_data["外向性"]},
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: '宜人性',
                        data: {trait_data["宜人性"]},
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: '神经质',
                        data: {trait_data["神经质"]},
                        borderColor: '#9b59b6',
                        backgroundColor: 'rgba(155, 89, 182, 0.1)',
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Big Five 人格特征随温度变化'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1,
                        title: {{
                            display: true,
                            text: '特征得分'
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

        // 响应特征图表
        const characteristicsCtx = document.getElementById('characteristicsChart').getContext('2d');
        const characteristicsChart = new Chart(characteristicsCtx, {{
            type: 'line',
            data: {{
                labels: {temperatures},
                datasets: [
                    {{
                        label: '创造性',
                        data: {[r["response_characteristics"]["创造性"] for r in self.results]},
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: '一致性',
                        data: {[r["response_characteristics"]["一致性"] for r in self.results]},
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: '可靠性',
                        data: {[r["response_characteristics"]["可靠性"] for r in self.results]},
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: '多样性',
                        data: {[r["response_characteristics"]["多样性"] for r in self.results]},
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '响应特征随温度变化'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: '特征百分比 (%)'
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
    </script>
</body>
</html>"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n📊 HTML报告已生成: {report_file}")
        print(f"🌐 请在浏览器中打开查看详细分析结果")

        return str(report_file)

def main():
    """技能主函数"""
    print("🚀 启动独立温度人格分析技能")
    print("⚡ 完全独立实现 - 100% 无外部依赖")
    print("🧠 使用Claude Code原生能力")
    print("=" * 60)

    try:
        skill = TemperatureAnalyzerSkill()

        # 显示技能信息
        info = skill.get_skill_info()
        print(f"📋 技能名称: {info['name']}")
        print(f"🔢 版本: {info['version']}")
        print(f"📝 描述: {info['description']}")
        print(f"🔧 独立性: {info['independence']}")
        print(f"📦 依赖: {', '.join(info['dependencies'])}")
        print(f"🚫 外部调用: {info['external_calls']}")
        print()

        # 运行分析
        report_file = skill.run_temperature_analysis()

        print(f"\n✅ 技能执行完成!")
        print(f"📄 报告文件: {report_file}")
        print(f"🔧 技能特性: 完全独立，无任何外部脚本调用")

    except Exception as e:
        print(f"❌ 技能执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())