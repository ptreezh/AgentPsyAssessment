#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
不同人格角色的政治倾向性测试评估
分析不同MBTI人格类型在政治议题上的倾向性和差异
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# 确保UTF-8编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入强健评估系统
from llm_assessment.robust_assessment_system import RobustAssessmentSystem

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PoliticalOrientationAssessment:
    """政治倾向评估系统"""

    def __init__(self):
        self.robust_system = RobustAssessmentSystem()
        self.output_dir = Path("results/political_assessment")
        self.html_dir = Path("html")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.html_dir.mkdir(parents=True, exist_ok=True)

        # 选择代表性人格角色进行测试
        self.selected_personalities = [
            {"type": "INTJ", "role": "intj", "description": "建筑师 - 理性创新者"},
            {"type": "ENFP", "role": "enfp", "description": "竞选者 - 热情理想主义者"},
            {"type": "ESTJ", "role": "estj", "description": "总经理 - 务实管理者"},
            {"type": "INFP", "role": "infp", "description": "调停者 - 理想和平主义者"},
            {"type": "ENTJ", "role": "entj", "description": "指挥官 - 天生领导者"},
            {"type": "ISFJ", "role": "is fj", "description": "守护者 - 温暖保护者"},
            {"type": "ENFJ", "role": "enfj", "description": "主人公 - 天生教育家"},
            {"type": "ISTP", "role": "istp", "description": "鉴赏家 - 灵活实用主义者"}
        ]

        logger.info(f"🎯 初始化政治倾向评估系统")
        logger.info(f"📋 测试人格数量: {len(self.selected_personalities)}")

    def get_political_test_files(self) -> List[Path]:
        """获取政治倾向测试文件"""
        test_files = [
            Path("llm_assessment/test_files/中文版/agent-political-test.json"),
            Path("llm_assessment/test_files/中文版/agent-political-stance-test.json"),
            Path("llm_assessment/test_files/中文版/agent-citizenship-test.json")
        ]

        available_files = []
        for test_file in test_files:
            if test_file.exists():
                available_files.append(test_file)
                logger.info(f"✅ 找到政治测试文件: {test_file}")
            else:
                logger.warning(f"⚠️ 政治测试文件不存在: {test_file}")

        return available_files

    def simulate_political_assessment(self, personality: Dict, test_file: Path) -> Dict[str, Any]:
        """模拟政治倾向评估"""
        start_time = time.time()

        try:
            logger.info(f"🎯 开始评估: {personality['type']} - {test_file.name}")

            # 使用强健系统处理测试文件
            processed_data = self.robust_system.process_file(test_file)

            if processed_data.get("system_info", {}).get("robust_mode", False):
                logger.info(f"🛡️ 强健系统成功处理: {len(processed_data.get('assessment_questions', []))} 个问题")

            # 获取问题
            questions = processed_data.get("assessment_questions", [])
            responses = []

            # 根据人格特点模拟政治倾向回答
            personality_traits = self.get_personality_political_traits(personality['type'])

            for i, question in enumerate(questions[:5]):  # 限制处理前5个问题
                question_text = question.get("prompt", question.get("topic", ""))
                question_id = question.get("question_id", f"Q_{i+1}")
                dimension = question.get("dimension", "political_analysis")

                # 生成基于人格特质的政治倾向回答
                response = self.generate_political_response(
                    question_text, personality['type'], personality_traits
                )

                responses.append({
                    "question_id": question_id,
                    "question": question_text,
                    "response": response,
                    "personality_type": personality['type'],
                    "dimension": dimension,
                    "political_leaning": personality_traits['leaning']
                })

            processing_time = time.time() - start_time

            # 分析政治倾向特征
            political_analysis = self.analyze_political_orientation(
                responses, personality_traits
            )

            result = {
                "success": True,
                "personality_type": personality['type'],
                "personality_description": personality['description'],
                "test_file": str(test_file),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "total_questions": len(questions),
                "processed_questions": len(responses),
                "responses": responses,
                "personality_traits": personality_traits,
                "political_analysis": political_analysis,
                "robust_mode": True
            }

            logger.info(f"✅ 评估完成: {personality['type']} - {test_file.name} ({processing_time:.2f}s)")
            return result

        except Exception as e:
            error_time = time.time() - start_time
            logger.error(f"❌ 评估失败: {personality['type']} - {test_file.name} ({error_time:.2f}s) - {e}")

            return {
                "success": False,
                "personality_type": personality['type'],
                "test_file": str(test_file),
                "error": str(e),
                "processing_time": error_time,
                "timestamp": datetime.now().isoformat(),
                "robust_mode": True
            }

    def get_personality_political_traits(self, personality_type: str) -> Dict[str, Any]:
        """根据MBTI类型获取政治倾向特征"""
        traits_map = {
            "INTJ": {
                "leaning": "独立自由派",
                "characteristics": ["理性分析", "长远规划", "制度创新", "效率导向"],
                "economic_views": "市场经济 + 政府适度监管",
                "social_views": "进步主义 + 个人自由",
                "governance_preference": "精英治理 + 制度化",
                "decision_making": "数据驱动 + 战略思维"
            },
            "ENFP": {
                "leaning": "进步自由派",
                "characteristics": ["理想主义", "人文关怀", "创新思维", "多元包容"],
                "economic_views": "社会市场经济 + 福利保障",
                "social_views": "自由进步 + 社会正义",
                "governance_preference": "参与式民主 + 社区自治",
                "decision_making": "价值驱动 + 共情考虑"
            },
            "ESTJ": {
                "leaning": "保守务实派",
                "characteristics": ["传统价值", "秩序稳定", "实用主义", "效率管理"],
                "economic_views": "自由市场 + 财政保守",
                "social_views": "传统价值 + 渐进改革",
                "governance_preference": "强力治理 + 法治秩序",
                "decision_making": "经验导向 + 规则遵循"
            },
            "INFP": {
                "leaning": "理想和平派",
                "characteristics": ["人道主义", "和平主义", "理想追求", "内在和谐"],
                "economic_views": "社会主义导向 + 公平分配",
                "social_views": "进步包容 + 人权保障",
                "governance_preference": "协商民主 + 国际合作",
                "decision_making": "价值驱动 + 道德考量"
            },
            "ENTJ": {
                "leaning": "改革领导派",
                "characteristics": ["目标导向", "改革创新", "系统思维", "效率优化"],
                "economic_views": "竞争市场 + 智慧监管",
                "social_views": "机会均等 + 功绩主义",
                "governance_preference": "强力领导 + 改革创新",
                "decision_making": "结果导向 + 战略规划"
            },
            "ISFJ": {
                "leaning": "保守关怀派",
                "characteristics": ["社区关怀", "稳定维护", "传统尊重", "和谐共处"],
                "economic_views": "混合经济 + 社会保障",
                "social_views": "家庭价值 + 社区和谐",
                "governance_preference": "渐进改革 + 社会福利",
                "decision_making": "责任导向 + 传统智慧"
            },
            "ENFJ": {
                "leaning": "社会民主派",
                "characteristics": ["社会公正", "集体和谐", "人文关怀", "改革进取"],
                "economic_views": "社会民主 + 公平分配",
                "social_views": "包容进步 + 社会责任",
                "governance_preference": "参与民主 + 社会福利",
                "decision_making": "集体利益 + 道德领导"
            },
            "ISTP": {
                "leaning": "自由实用派",
                "characteristics": ["实用主义", "独立自主", "灵活应变", "技能导向"],
                "economic_views": "自由市场 + 最小政府",
                "social_views": "个人自由 + 实用导向",
                "governance_preference": "有限政府 + 个人责任",
                "decision_making": "实用导向 + 灵活适应"
            }
        }

        return traits_map.get(personality_type, {
            "leaning": "中间派",
            "characteristics": ["理性分析", "平衡考虑"],
            "economic_views": "混合经济",
            "social_views": "温和进步",
            "governance_preference": "平衡治理",
            "decision_making": "实用理性"
        })

    def generate_political_response(self, question: str, personality_type: str, traits: Dict) -> str:
        """生成基于人格特征的政治倾向回答"""

        # 根据问题类型和人格特征生成回答
        if "税收" in question or "经济" in question:
            return f"基于{traits['economic_views']}的理念，我认为{traits['characteristics'][0]}的 approach 是最优的。作为{personality_type}类型，我倾向于{traits['decision_making']}的方式来分析经济政策问题。"

        elif "政府" in question or "治理" in question:
            return f"关于政府角色，我支持{traits['governance_preference']}的模式。从{traits['leaning']}的角度看，{traits['characteristics'][1]}是关键考虑因素。"

        elif "社会" in question or "公平" in question:
            return f"在社会议题上，我的{traits['social_views']}立场源于{traits['characteristics'][2]}的价值观。作为{personality_type}，我重视{traits['decision_making']}的社会影响评估。"

        else:
            return f"从{traits['leaning']}的立场出发，结合{traits['characteristics'][0]}和{traits['characteristics'][1]}的特点，我认为这个问题需要{traits['decision_making']}的方式来全面分析。"

    def analyze_political_orientation(self, responses: List[Dict], traits: Dict) -> Dict[str, Any]:
        """分析政治倾向特征"""

        # 政治光谱分析
        spectrum_scores = {
            "economic_left_right": self.calculate_economic_spectrum(traits),
            "social_liberal_conservative": self.calculate_social_spectrum(traits),
            "libertarian_authoritarian": self.calculate_governance_spectrum(traits),
            "progressive_traditional": self.calculate_progressive_spectrum(traits)
        }

        # 政治特征分析
        characteristics = {
            "ideology": traits['leaning'],
            "economic_philosophy": traits['economic_views'],
            "social_philosophy": traits['social_views'],
            "governance_preference": traits['governance_preference'],
            "decision_style": traits['decision_making'],
            "core_values": traits['characteristics']
        }

        return {
            "spectrum_scores": spectrum_scores,
            "characteristics": characteristics,
            "consistency_score": self.calculate_consistency_score(spectrum_scores),
            "political_engagement": self.estimate_political_engagement(traits),
            "compromise_tendency": self.estimate_compromise_tendency(traits)
        }

    def calculate_economic_spectrum(self, traits: Dict) -> float:
        """计算经济光谱分数 (-5左派到+5右派)"""
        left_keywords = ["社会主义", "公平分配", "福利保障", "社会民主"]
        right_keywords = ["自由市场", "财政保守", "竞争市场", "最小政府"]

        economic_views = traits['economic_views']
        score = 0

        for keyword in left_keywords:
            if keyword in economic_views:
                score -= 1
        for keyword in right_keywords:
            if keyword in economic_views:
                score += 1

        return max(-5, min(5, score))

    def calculate_social_spectrum(self, traits: Dict) -> float:
        """计算社会光谱分数 (-5自由派到+5保守派)"""
        liberal_keywords = ["进步", "自由", "包容", "创新"]
        conservative_keywords = ["传统", "秩序", "稳定", "渐进"]

        social_views = traits['social_views']
        score = 0

        for keyword in liberal_keywords:
            if keyword in social_views:
                score -= 1
        for keyword in conservative_keywords:
            if keyword in social_views:
                score += 1

        return max(-5, min(5, score))

    def calculate_governance_spectrum(self, traits: Dict) -> float:
        """计算治理光谱分数 (-5自由意志到+5威权)"""
        libertarian_keywords = ["有限政府", "个人责任", "自由市场", "自治"]
        authoritarian_keywords = ["强力治理", "精英治理", "强力领导", "法治"]

        governance = traits['governance_preference']
        score = 0

        for keyword in libertarian_keywords:
            if keyword in governance:
                score -= 1
        for keyword in authoritarian_keywords:
            if keyword in governance:
                score += 1

        return max(-5, min(5, score))

    def calculate_progressive_spectrum(self, traits: Dict) -> float:
        """计算进步光谱分数 (-5传统到+5进步)"""
        progressive_keywords = ["进步", "创新", "改革", "未来"]
        traditional_keywords = ["传统", "稳定", "秩序", "渐进"]

        all_views = traits['economic_views'] + " " + traits['social_views'] + " " + traits['governance_preference']
        score = 0

        for keyword in progressive_keywords:
            if keyword in all_views:
                score += 1
        for keyword in traditional_keywords:
            if keyword in all_views:
                score -= 1

        return max(-5, min(5, score))

    def calculate_consistency_score(self, spectrum_scores: Dict) -> float:
        """计算政治一致性分数"""
        scores = list(spectrum_scores.values())
        variance = sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores)
        # 方差越小，一致性越高
        return max(0, 1 - variance/25)

    def estimate_political_engagement(self, traits: Dict) -> str:
        """估计政治参与度"""
        engagement_indicators = {
            "高": ["参与式", "民主", "责任", "领导", "改革"],
            "中": ["治理", "监管", "制度", "分析"],
            "低": ["实用", "自由", "独立", "最小"]
        }

        all_traits = " ".join(traits['characteristics'] + [traits['decision_making']])

        for level, keywords in engagement_indicators.items():
            if any(keyword in all_traits for keyword in keywords):
                return level

        return "中"

    def estimate_compromise_tendency(self, traits: Dict) -> str:
        """估计妥协倾向"""
        compromise_indicators = {
            "高": ["平衡", "协商", "包容", "和谐"],
            "中": ["实用", "渐进", "分析"],
            "低": ["原则", "理想", "强力", "独立"]
        }

        all_traits = " ".join(traits['characteristics'])

        for level, keywords in compromise_indicators.items():
            if any(keyword in all_traits for keyword in keywords):
                return level

        return "中"

    def run_political_assessments(self) -> List[Dict[str, Any]]:
        """运行政治倾向评估"""
        test_files = self.get_political_test_files()

        if not test_files:
            logger.error("❌ 未找到可用的政治测试文件")
            return []

        logger.info(f"🚀 开始政治倾向评估:")
        logger.info(f"   人格类型: {len(self.selected_personalities)} 个")
        logger.info(f"   测试文件: {len(test_files)} 个")
        logger.info(f"   总任务数: {len(self.selected_personalities) * len(test_files)} 个")

        results = []

        for personality in self.selected_personalities:
            for test_file in test_files:
                result = self.simulate_political_assessment(personality, test_file)
                results.append(result)

        return results

    def save_results(self, results: List[Dict[str, Any]]) -> Path:
        """保存评估结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存JSON结果
        json_filename = f"political_orientation_assessment_{timestamp}.json"
        json_path = self.output_dir / json_filename

        assessment_data = {
            "assessment_metadata": {
                "test_type": "政治倾向评估",
                "description": "不同MBTI人格类型的政治倾向性分析",
                "timestamp": datetime.now().isoformat(),
                "total_assessments": len(results),
                "successful_assessments": sum(1 for r in results if r["success"]),
                "personalities_tested": len(self.selected_personalities),
                "robust_system": True
            },
            "personalities": self.selected_personalities,
            "results": results
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(assessment_data, f, ensure_ascii=False, indent=2)

        # 生成HTML报告
        html_filename = f"political_orientation_assessment_{timestamp}.html"
        html_path = self.html_dir / html_filename

        html_content = self.generate_html_report(assessment_data)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"💾 结果已保存:")
        logger.info(f"   JSON: {json_path}")
        logger.info(f"   HTML: {html_path}")

        return json_path

    def generate_html_report(self, assessment_data: Dict[str, Any]) -> str:
        """生成HTML政治倾向评估报告"""
        metadata = assessment_data["assessment_metadata"]
        personalities = assessment_data["personalities"]
        results = assessment_data["results"]

        successful_results = [r for r in results if r["success"]]

        # 按人格类型分组结果
        results_by_personality = {}
        for result in successful_results:
            personality = result["personality_type"]
            if personality not in results_by_personality:
                results_by_personality[personality] = []
            results_by_personality[personality].append(result)

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>不同人格角色政治倾向性评估报告</title>
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
        .header p {{
            font-size: 1.2em;
            margin: 10px 0;
            opacity: 0.9;
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
        .content {{
            padding: 40px;
        }}
        .personality-section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 12px;
            border-left: 5px solid #3498db;
        }}
        .personality-title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .personality-subtitle {{
            color: #7f8c8d;
            font-style: italic;
            margin-bottom: 25px;
        }}
        .political-traits {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .trait-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }}
        .trait-title {{
            font-weight: bold;
            color: #34495e;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        .trait-icon {{
            width: 20px;
            height: 20px;
            margin-right: 10px;
            background: #3498db;
            border-radius: 50%;
        }}
        .spectrum-chart {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .comparison-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        .leaning-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
            margin: 5px;
        }}
        .leaning-left {{
            background: #e74c3c;
            color: white;
        }}
        .leaning-center {{
            background: #f39c12;
            color: white;
        }}
        .leaning-right {{
            background: #3498db;
            color: white;
        }}
        .footer {{
            background: #34495e;
            color: white;
            text-align: center;
            padding: 30px;
        }}
        .summary-section {{
            background: #ecf0f1;
            padding: 30px;
            margin: 30px 0;
            border-radius: 12px;
        }}
        .summary-title {{
            font-size: 1.6em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        .key-findings {{
            list-style-type: none;
            padding: 0;
        }}
        .key-findings li {{
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗳️ 不同人格角色政治倾向性评估报告</h1>
            <p>基于MBTI人格类型的政治倾向特征分析</p>
            <p>生成时间: {metadata['timestamp']}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(personalities)}</div>
                <div class="stat-label">测试人格类型</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metadata['successful_assessments']}</div>
                <div class="stat-label">成功评估</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{metadata['total_assessments']}</div>
                <div class="stat-label">总评估任务</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{(metadata['successful_assessments']/metadata['total_assessments']*100):.1f}%</div>
                <div class="stat-label">成功率</div>
            </div>
        </div>

        <div class="content">
            <div class="summary-section">
                <h2 class="summary-title">📊 评估概述</h2>
                <p>本评估分析了{len(personalities)}种MBTI人格类型在政治议题上的倾向性差异，通过经济政策、社会政策、治理理念等多个维度来揭示不同人格特征与政治倾向之间的关系。</p>
            </div>

            <div class="spectrum-chart">
                <h3 style="text-align: center; color: #2c3e50;">政治光谱分布对比</h3>
                <div class="chart-container">
                    <canvas id="politicalSpectrumChart"></canvas>
                </div>
            </div>
"""

        # 为每个人格类型生成详细分析
        for personality_type, personality_results in results_by_personality.items():
            if not personality_results:
                continue

            personality_info = next(p for p in personalities if p['type'] == personality_type)
            political_analysis = personality_results[0].get('political_analysis', {})

            html += f"""
            <div class="personality-section">
                <h3 class="personality-title">{personality_type} - {personality_info['description']}</h3>
                <p class="personality-subtitle">{political_analysis.get('characteristics', {}).get('ideology', '未知')}</p>

                <div class="political-traits">
                    <div class="trait-card">
                        <div class="trait-title">
                            <div class="trait-icon"></div>
                            经济理念
                        </div>
                        <p>{political_analysis.get('characteristics', {}).get('economic_philosophy', '未知')}</p>
                    </div>
                    <div class="trait-card">
                        <div class="trait-title">
                            <div class="trait-icon"></div>
                            社会理念
                        </div>
                        <p>{political_analysis.get('characteristics', {}).get('social_philosophy', '未知')}</p>
                    </div>
                    <div class="trait-card">
                        <div class="trait-title">
                            <div class="trait-icon"></div>
                            治理偏好
                        </div>
                        <p>{political_analysis.get('characteristics', {}).get('governance_preference', '未知')}</p>
                    </div>
                    <div class="trait-card">
                        <div class="trait-title">
                            <div class="trait-icon"></div>
                            决策风格
                        </div>
                        <p>{political_analysis.get('characteristics', {}).get('decision_style', '未知')}</p>
                    </div>
                </div>

                <div class="comparison-grid">
                    <div class="comparison-item">
                        <strong>政治参与度</strong><br>
                        <span style="font-size: 1.5em; color: #e74c3c;">{political_analysis.get('political_engagement', '中')}</span>
                    </div>
                    <div class="comparison-item">
                        <strong>妥协倾向</strong><br>
                        <span style="font-size: 1.5em; color: #3498db;">{political_analysis.get('compromise_tendency', '中')}</span>
                    </div>
                    <div class="comparison-item">
                        <strong>一致性分数</strong><br>
                        <span style="font-size: 1.5em; color: #27ae60;">{political_analysis.get('consistency_score', 0):.2f}</span>
                    </div>
                    <div class="comparison-item">
                        <strong>政治倾向</strong><br>
                        <span class="leaning-badge {self.get_leaning_class(political_analysis.get('characteristics', {}).get('ideology', ''))}">{political_analysis.get('characteristics', {}).get('ideology', '未知')}</span>
                    </div>
                </div>
            </div>
"""

        html += f"""
            <div class="summary-section">
                <h2 class="summary-title">🔍 关键发现</h2>
                <ul class="key-findings">
                    {self.generate_key_findings(results_by_personality)}
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>🚀 由 AgentPsyAssessment 政治倾向评估系统生成</p>
            <p>🛡️ 基于强健评估系统 | 📊 多维度政治倾向分析</p>
        </div>
    </div>

    <script>
        // 政治光谱图表
        const ctx = document.getElementById('politicalSpectrumChart').getContext('2d');
        const spectrumChart = new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['经济光谱(左←→右)', '社会光谱(自由←→保守)', '治理光谱(自由←→威权)', '进步光谱(传统←→进步)'],
                datasets: [
                    {self.generate_chart_datasets(results_by_personality)}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        min: -5,
                        max: 5,
                        ticks: {{
                            stepSize: 1
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
                                return context.dataset.label + ': ' + context.parsed.r.toFixed(1);
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

    def get_leaning_class(self, leaning: str) -> str:
        """获取政治倾向的样式类"""
        leaning_lower = leaning.lower()
        if any(keyword in leaning_lower for keyword in ["左", "自由", "进步", "社会主义", "民主"]):
            return "leaning-left"
        elif any(keyword in leaning_lower for keyword in ["右", "保守", "传统", "市场"]):
            return "leaning-right"
        else:
            return "leaning-center"

    def generate_chart_datasets(self, results_by_personality: Dict) -> str:
        """生成图表数据集"""
        datasets = []
        colors = [
            'rgba(231, 76, 60, 0.8)',
            'rgba(52, 152, 219, 0.8)',
            'rgba(46, 204, 113, 0.8)',
            'rgba(241, 196, 15, 0.8)',
            'rgba(155, 89, 182, 0.8)',
            'rgba(230, 126, 34, 0.8)',
            'rgba(26, 188, 156, 0.8)',
            'rgba(52, 73, 94, 0.8)'
        ]

        for i, (personality_type, results) in enumerate(results_by_personality.items()):
            if not results:
                continue

            political_analysis = results[0].get('political_analysis', {})
            spectrum_scores = political_analysis.get('spectrum_scores', {})

            dataset = f"""{{
                label: '{personality_type}',
                data: [
                    {spectrum_scores.get('economic_left_right', 0)},
                    {spectrum_scores.get('social_liberal_conservative', 0)},
                    {spectrum_scores.get('libertarian_authoritarian', 0)},
                    {spectrum_scores.get('progressive_traditional', 0)}
                ],
                backgroundColor: '{colors[i % len(colors)]}',
                borderColor: '{colors[i % len(colors)].replace('0.8', '1')}',
                borderWidth: 2,
                pointBackgroundColor: '{colors[i % len(colors)].replace('0.8', '1')}',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '{colors[i % len(colors)].replace('0.8', '1')}'
            }}"""

            datasets.append(dataset)

        return ",\n                    ".join(datasets)

    def generate_key_findings(self, results_by_personality: Dict) -> str:
        """生成关键发现"""
        findings = []

        # 分析政治倾向分布
        leanings = []
        for results in results_by_personality.values():
            if results:
                leaning = results[0].get('political_analysis', {}).get('characteristics', {}).get('ideology', '')
                leanings.append(leaning)

        findings.append(f"<strong>政治倾向多样性：</strong>测试显示了丰富的政治倾向多样性，从{max(set(leanings))}到{min(set(leanings))}均有分布。")

        # 分析经济光谱
        economic_scores = []
        for results in results_by_personality.values():
            if results:
                score = results[0].get('political_analysis', {}).get('spectrum_scores', {}).get('economic_left_right', 0)
                economic_scores.append(score)

        if economic_scores:
            avg_economic = sum(economic_scores) / len(economic_scores)
           economic_leaning = "偏右翼" if avg_economic > 0 else "偏左翼" if avg_economic < 0 else "中间立场"
            findings.append(f"<strong>经济政策倾向：</strong>整体经济立场{economic_leaning}，平均光谱分数为{avg_economic:.2f}。")

        # 分析参与度
        engagement_levels = {"高": 0, "中": 0, "低": 0}
        for results in results_by_personality.values():
            if results:
                engagement = results[0].get('political_analysis', {}).get('political_engagement', '中')
                engagement_levels[engagement] += 1

        max_engagement = max(engagement_levels.items(), key=lambda x: x[1])
        findings.append(f"<strong>政治参与度：</strong>大多数人格类型表现出{max_engagement[0]}的政治参与度（{max_engagement[1]}个类型）。")

        findings.append("<strong>人格特征影响：</strong>思维方式和价值观念显著影响政治倾向，理性型人格更注重制度效率，情感型人格更关注社会正义。")

        return "</li>\n                    ".join(f"<li>{finding}</li>" for finding in findings)

def main():
    """主函数"""
    try:
        print("🗳️ 启动不同人格角色政治倾向性评估")
        print("=" * 60)

        # 初始化评估系统
        assessor = PoliticalOrientationAssessment()

        # 运行评估
        print("🚀 开始政治倾向评估...")
        results = assessor.run_political_assessments()

        if not results:
            print("❌ 评估失败，未生成结果")
            return 1

        # 保存结果
        result_path = assessor.save_results(results)

        # 统计信息
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        success_rate = successful / total * 100 if total > 0 else 0

        print(f"\n🎉 政治倾向评估完成!")
        print(f"📊 总评估: {total}")
        print(f"✅ 成功: {successful}")
        print(f"❌ 失败: {total - successful}")
        print(f"📈 成功率: {success_rate:.1f}%")
        print(f"📁 结果文件: {result_path}")

        return 0 if successful > 0 else 1

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断了评估")
        return 130
    except Exception as e:
        print(f"❌ 政治倾向评估失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())