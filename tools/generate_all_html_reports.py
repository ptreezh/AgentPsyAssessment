#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML评估报告批量生成器
为html目录下所有的JSON响应数据生成专业的HTML评估报告
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

class HTMLReportGenerator:
    def __init__(self):
        self.html_dir = Path("D:/AIDevelop/portable_psyagent/html")
        self.personality_info = {
            "ENTJ": {"name": "指挥官型", "description": "天生的领导者，善于组织和战略规划"},
            "ENTP": {"name": "辩论家型", "description": "聪明的创新者，喜欢挑战传统观点"},
            "ENFJ": {"name": "主人公型", "description": "富有魅力的领导者，善于启发他人"},
            "ENFP": {"name": "竞选者型", "description": "热情的创意者，热爱社交和自由"},
            "ESTJ": {"name": "总经理型", "description": "出色的管理者，擅长组织和执行"},
            "ESTP": {"name": "企业家型", "description": "精力充沛的实干家，善于抓住机会"},
            "ESFJ": {"name": "执政官型", "description": "热心助人的合作者，关注和谐"},
            "ESFP": {"name": "娱乐家型", "description": "活泼的表演者，热爱生活"},
            "INFJ": {"name": "提倡者型", "description": "理想主义者，有深刻的洞察力"},
            "INFP": {"name": "调停者型", "description": "理想主义的艺术家，追求价值"},
            "INTJ": {"name": "建筑师型", "description": "战略思想家，追求创新"},
            "INTP": {"name": "逻辑学家型", "description": "理论创新者，热爱知识"},
            "ISFJ": {"name": "守护者型", "description": "温暖的保护者，注重责任"},
            "ISFP": {"name": "冒险家型", "description": "灵活的艺术家，追求美感"},
            "ISTJ": {"name": "物流师型", "description": "可靠的实践者，注重细节"},
            "ISTP": {"name": "鉴赏家型", "description": "灵活的工程师，善于解决问题"}
        }

    def analyze_responses(self, responses_data):
        """分析响应数据并生成评估结果"""
        responses = responses_data.get("responses", [])

        # 初始化维度分数
        dimensions = {
            "历史知识": {"score": 0, "count": 0, "details": []},
            "地理知识": {"score": 0, "count": 0, "details": []},
            "政治知识": {"score": 0, "count": 0, "details": []},
            "文化知识": {"score": 0, "count": 0, "details": []},
            "综合分析": {"score": 0, "count": 0, "details": []}
        }

        # 分析每个响应
        for response_item in responses:
            question_id = response_item.get("question_id", "")
            response_text = response_item.get("response", "")

            # 根据问题ID分类
            if "history" in question_id:
                dimensions["历史知识"]["count"] += 1
                score = self.calculate_response_score(response_text, "history")
                dimensions["历史知识"]["score"] += score
                dimensions["历史知识"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "geography" in question_id:
                dimensions["地理知识"]["count"] += 1
                score = self.calculate_response_score(response_text, "geography")
                dimensions["地理知识"]["score"] += score
                dimensions["地理知识"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "political" in question_id:
                dimensions["政治知识"]["count"] += 1
                score = self.calculate_response_score(response_text, "political")
                dimensions["政治知识"]["score"] += score
                dimensions["政治知识"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "cultural" in question_id:
                dimensions["文化知识"]["count"] += 1
                score = self.calculate_response_score(response_text, "cultural")
                dimensions["文化知识"]["score"] += score
                dimensions["文化知识"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "comprehensive" in question_id:
                dimensions["综合分析"]["count"] += 1
                score = self.calculate_response_score(response_text, "comprehensive")
                dimensions["综合分析"]["score"] += score
                dimensions["综合分析"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })

        # 计算平均分
        for dim in dimensions:
            if dimensions[dim]["count"] > 0:
                dimensions[dim]["average"] = dimensions[dim]["score"] / dimensions[dim]["count"]
            else:
                dimensions[dim]["average"] = 0

        return dimensions

    def calculate_response_score(self, response_text, category):
        """计算响应质量分数"""
        score = 85  # 基础分

        # 根据响应长度和质量调整分数
        if len(response_text) > 100:
            score += 5
        if len(response_text) > 200:
            score += 5

        # 检查关键词
        keywords = {
            "history": ["历史", "朝代", "年代", "事件", "发展", "变化"],
            "geography": ["地理", "地形", "气候", "位置", "面积", "河流"],
            "political": ["政治", "制度", "法律", "民主", "权利", "义务"],
            "cultural": ["文化", "传统", "节日", "艺术", "价值", "习俗"],
            "comprehensive": ["分析", "发展", "挑战", "机遇", "综合", "整体"]
        }

        for keyword in keywords.get(category, []):
            if keyword in response_text:
                score += 2

        return min(score, 100)  # 最高100分

    def generate_html_report(self, json_file_path, output_path, assessment_type):
        """生成HTML评估报告"""
        # 读取JSON数据
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取人格类型
        filename = Path(json_file_path).stem
        personality_type = self.extract_personality_type(filename)

        # 分析响应
        if assessment_type == "citizenship":
            dimensions = self.analyze_responses(data)
            overall_score = sum(dim["average"] for dim in dimensions.values()) / len(dimensions)
            assessment_title = "公民知识能力评估"
        else:  # bank
            dimensions = self.analyze_bank_responses(data)
            overall_score = sum(dim["average"] for dim in dimensions.values()) / len(dimensions)
            assessment_title = "银行客服专业能力评估"

        personality_info = self.personality_info.get(personality_type, {"name": personality_type, "description": ""})

        # 生成HTML
        html_content = self.create_html_template(
            personality_type=personality_type,
            personality_info=personality_info,
            dimensions=dimensions,
            overall_score=overall_score,
            assessment_title=assessment_title,
            filename=filename
        )

        # 保存HTML文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ 已生成: {output_path} - {personality_type} - 总分: {overall_score:.1f}")

    def analyze_bank_responses(self, responses_data):
        """分析银行客服响应数据"""
        responses = responses_data.get("responses", [])

        dimensions = {
            "同理心服务": {"score": 0, "count": 0, "details": []},
            "合规操作": {"score": 0, "count": 0, "details": []},
            "高效协调": {"score": 0, "count": 0, "details": []},
            "创新发展": {"score": 0, "count": 0, "details": []},
            "危机管理": {"score": 0, "count": 0, "details": []}
        }

        # 分析银行客服响应
        for response_item in responses:
            question_id = response_item.get("question_id", "")
            response_text = response_item.get("response", "")

            # 根据问题ID分类到银行客服维度
            if "service" in question_id or "empathy" in question_id:
                dimensions["同理心服务"]["count"] += 1
                score = self.calculate_response_score(response_text, "service")
                dimensions["同理心服务"]["score"] += score
                dimensions["同理心服务"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "compliance" in question_id or "risk" in question_id:
                dimensions["合规操作"]["count"] += 1
                score = self.calculate_response_score(response_text, "compliance")
                dimensions["合规操作"]["score"] += score
                dimensions["合规操作"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "coordination" in question_id or "efficiency" in question_id:
                dimensions["高效协调"]["count"] += 1
                score = self.calculate_response_score(response_text, "coordination")
                dimensions["高效协调"]["score"] += score
                dimensions["高效协调"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "innovation" in question_id or "development" in question_id:
                dimensions["创新发展"]["count"] += 1
                score = self.calculate_response_score(response_text, "innovation")
                dimensions["创新发展"]["score"] += score
                dimensions["创新发展"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            elif "crisis" in question_id or "emergency" in question_id:
                dimensions["危机管理"]["count"] += 1
                score = self.calculate_response_score(response_text, "crisis")
                dimensions["危机管理"]["score"] += score
                dimensions["危机管理"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })
            else:
                # 默认分配到综合维度
                dimensions["高效协调"]["count"] += 1
                score = self.calculate_response_score(response_text, "general")
                dimensions["高效协调"]["score"] += score
                dimensions["高效协调"]["details"].append({
                    "question_id": question_id,
                    "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "score": score
                })

        # 计算平均分
        for dim in dimensions:
            if dimensions[dim]["count"] > 0:
                dimensions[dim]["average"] = dimensions[dim]["score"] / dimensions[dim]["count"]
            else:
                dimensions[dim]["average"] = 0

        return dimensions

    def extract_personality_type(self, filename):
        """从文件名提取人格类型"""
        # 匹配人格类型模式
        patterns = [
            r'(entj|entp|enfj|enfp|estj|estp|esfj|esfp)',
            r'(infj|infp|intj|intp|isfj|isfp|istj|istp)'
        ]

        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        return "UNKNOWN"

    def create_html_template(self, personality_type, personality_info, dimensions, overall_score, assessment_title, filename):
        """创建HTML模板"""

        # 确定等级
        if overall_score >= 95:
            grade = "A+ (卓越)"
            grade_color = "#10b981"
        elif overall_score >= 90:
            grade = "A+ (优秀)"
            grade_color = "#3b82f6"
        elif overall_score >= 85:
            grade = "A (良好)"
            grade_color = "#6366f1"
        elif overall_score >= 80:
            grade = "B+ (合格)"
            grade_color = "#8b5cf6"
        else:
            grade = "B (需要改进)"
            grade_color = "#f59e0b"

        # 生成维度HTML
        dimensions_html = ""
        for dim_name, dim_data in dimensions.items():
            dim_score = dim_data.get("average", 0)
            dim_count = dim_data.get("count", 0)

            # 确定等级
            if dim_score >= 95:
                dim_grade = "卓越"
                dim_color = "#10b981"
            elif dim_score >= 90:
                dim_grade = "优秀"
                dim_color = "#3b82f6"
            elif dim_score >= 85:
                dim_grade = "良好"
                dim_color = "#6366f1"
            elif dim_score >= 80:
                dim_grade = "合格"
                dim_color = "#8b5cf6"
            else:
                dim_grade = "需要改进"
                dim_color = "#f59e0b"

            dimensions_html += f"""
            <div class="dimension-card">
                <h3>{dim_name}</h3>
                <div class="score-circle" style="border-color: {dim_color}; color: {dim_color};">
                    {dim_score:.1f}
                </div>
                <p class="grade">等级: <span style="color: {dim_color};">{dim_grade}</span></p>
                <p class="questions">题目数量: {dim_count}</p>
            </div>
            """

        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personality_type} ({personality_info['name']}) - {assessment_title}报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .personality {{
            color: #3498db;
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .header .description {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-bottom: 20px;
        }}

        .overall-score {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 8px solid;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5em;
            font-weight: bold;
            margin: 0 auto 20px;
        }}

        .grade {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .dimensions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .dimension-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .dimension-card h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}

        .dimension-card .score-circle {{
            width: 80px;
            height: 80px;
            font-size: 1.8em;
            margin: 0 auto 15px;
        }}

        .footer {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            color: #7f8c8d;
        }}

        .footer p {{
            margin-bottom: 5px;
        }}

        .highlight {{
            color: #3498db;
            font-weight: bold;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            .dimensions {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{assessment_title}报告</h1>
            <div class="personality">{personality_type} ({personality_info['name']})</div>
            <div class="description">{personality_info['description']}</div>
        </div>

        <div class="overall-score">
            <div class="score-circle" style="border-color: {grade_color}; color: {grade_color};">
                {overall_score:.1f}
            </div>
            <div class="grade">综合等级: <span style="color: {grade_color};">{grade}</span></div>
            <p>评估时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
        </div>

        <div class="dimensions">
            {dimensions_html}
        </div>

        <div class="footer">
            <p>🤖 <span class="highlight">Portable PsyAgent</span> - AI Agent心理评估平台</p>
            <p>📧 联系方式: pTreezh / Dr Zhang | 3061176@qq.com</p>
            <p>🌐 官方网站: <a href="https://cn.agentpsy.com" target="_blank" style="color: #3498db;">https://cn.agentpsy.com</a></p>
            <p>🏛️ AI Personality Lab | 专业AI人格评估与研究</p>
        </div>
    </div>
</body>
</html>
        """

        return html_template

    def generate_all_reports(self):
        """生成所有HTML评估报告"""
        print("🚀 开始生成HTML评估报告...")
        print("=" * 60)

        generated_count = 0

        # 处理exam目录下的公民知识测评
        exam_dir = self.html_dir / "exam"
        if exam_dir.exists():
            for json_file in exam_dir.glob("*.json"):
                if "_test" in json_file.name:
                    continue  # 跳过测试文件

                output_file = self.html_dir / f"{json_file.stem}_assessment.html"
                if not output_file.exists():
                    try:
                        self.generate_html_report(json_file, output_file, "citizenship")
                        generated_count += 1
                    except Exception as e:
                        print(f"❌ 生成失败: {json_file} - {e}")

        # 处理bank目录下的银行客服测评
        bank_dir = self.html_dir / "bank"
        if bank_dir.exists():
            for json_file in bank_dir.glob("*.json"):
                output_file = self.html_dir / f"{json_file.stem}_assessment.html"
                if not output_file.exists():
                    try:
                        self.generate_html_report(json_file, output_file, "bank")
                        generated_count += 1
                    except Exception as e:
                        print(f"❌ 生成失败: {json_file} - {e}")

        print("=" * 60)
        print(f"✅ 完成！共生成 {generated_count} 个HTML评估报告")
        print("📁 报告位置: D:/AIDevelop/portable_psyagent/html/")
        print("🌐 可以在浏览器中打开查看详细的评估报告")

def main():
    generator = HTMLReportGenerator()
    generator.generate_all_reports()

if __name__ == "__main__":
    main()