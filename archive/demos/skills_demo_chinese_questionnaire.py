#!/usr/bin/env python3
"""
中文问卷技能演示
展示如何使用三个核心技能处理中文版AI公民知识测试
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

class ChineseQuestionnaireSkillsDemo:
    """中文问卷技能演示系统"""

    def __init__(self):
        self.questionnaire_file = "llm_assessment/test_files/中文版/agent-citizenship-test.json"
        self.personas = {
            "INTJ": {
                "name": "建筑师",
                "description": "战略思考者，理性分析，追求创新和效率",
                "response_style": "系统性、逻辑性、前瞻性"
            },
            "ENFJ": {
                "name": "主人公",
                "description": "天生的领导者，富有同理心，关注人文价值",
                "response_style": "温暖、包容、价值导向"
            },
            "ISTJ": {
                "name": "物流师",
                "description": "务实的组织者，重视传统和准确性",
                "response_style": "详细、准确、基于事实"
            }
        }

    def load_questionnaire(self):
        """加载问卷数据"""
        try:
            with open(self.questionnaire_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"❌ 问卷加载失败: {e}")
            return None

    def skill_questionnaire_responder(self, persona_type="INTJ", limit_questions=5):
        """
        技能1: questionnaire-responder (问卷回答器)
        基于指定人格类型生成问卷回答
        """
        print(f"\n🎭 技能演示 1: Questionnaire-Responder")
        print("=" * 60)
        print(f"📋 人格类型: {persona_type} - {self.personas[persona_type]['name']}")
        print(f"📝 描述: {self.personas[persona_type]['description']}")
        print(f"🎯 回答风格: {self.personas[persona_type]['response_style']}")

        questionnaire_data = self.load_questionnaire()
        if not questionnaire_data:
            return None

        questions = questionnaire_data.get('test_bank', [])[:limit_questions]
        responses = []

        print(f"\n📚 开始回答 {len(questions)} 道题目:")
        print("-" * 40)

        for i, question in enumerate(questions, 1):
            question_text = question.get('question', '')
            dimension = question.get('dimension', '')

            # 基于人格类型生成回答
            response = self._generate_persona_response(question_text, persona_type, dimension)

            print(f"\n❓ 问题 {i}: {question_text}")
            print(f"🎭 {persona_type} 回答: {response}")

            responses.append({
                "question_id": question.get('question_id', f'q_{i}'),
                "question": question_text,
                "dimension": dimension,
                "response": response,
                "persona": persona_type,
                "reasoning": self._generate_reasoning(persona_type, question_text, response)
            })

        # 保存回答数据
        result_data = {
            "assessment_info": {
                "skill_used": "questionnaire-responder",
                "persona": persona_type,
                "questionnaire": "AI公民知识测试",
                "timestamp": datetime.now().isoformat(),
                "total_questions": len(responses)
            },
            "responses": responses
        }

        output_file = f"results/skill_demo_{persona_type.lower()}_citizenship_responses.json"
        Path("results").mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 问卷回答完成!")
        print(f"📁 结果保存到: {output_file}")

        return result_data

    def _generate_persona_response(self, question, persona_type, dimension):
        """基于人格类型生成回答"""

        if persona_type == "INTJ":
            return self._intj_response(question, dimension)
        elif persona_type == "ENFJ":
            return self._enfj_response(question, dimension)
        elif persona_type == "ISTJ":
            return self._istj_response(question, dimension)
        else:
            return "我需要更多信息来回答这个问题。"

    def _intj_response(self, question, dimension):
        """INTJ人格类型的回答风格"""
        if "四大发明" in question:
            return "中国的四大发明包括造纸术、印刷术、指南针和火药。这些发明不仅推动了中华文明的发展，也对世界科技进步产生了深远影响。从系统性角度看，这些发明体现了古代中国在材料科学、导航技术和化学领域的创新思维。"
        elif "首都" in question:
            return "中华人民共和国的首都是北京。作为政治、文化和国际交往中心，北京的选择体现了地理战略考量和文化传承的平衡。"
        elif "人口" in question:
            return "中国是世界上人口最多的国家，约有14亿人口。这一人口规模既是发展优势，也带来了资源分配和环境保护的挑战。"
        else:
            return "基于我的分析，这个问题需要从多个维度来考虑。首先需要理解历史背景，然后分析当前状况，最后展望未来发展趋势。"

    def _enfj_response(self, question, dimension):
        """ENFJ人格类型的回答风格"""
        if "四大发明" in question:
            return "中国的四大发明是造纸术、指南针、火药和印刷术。这些伟大的发明体现了中华民族的智慧，不仅造福了中国人民，也为全人类的文明进步做出了重要贡献。它们展现了我们祖先追求美好生活、服务人类的崇高精神。"
        elif "首都" in question:
            return "中国的首都是北京，这座伟大的城市承载着深厚的历史文化底蕴，是中华民族团结奋进的象征，也是我们共同的精神家园。"
        elif "人口" in question:
            return "中国有14亿人口，这是我们国家的宝贵财富。每一个中国人都是这个大家庭的重要成员，我们共同为建设美好社会而努力。"
        else:
            return "这个问题让我思考我们作为集体应该如何更好地理解和传承我们的文化价值观，同时为下一代创造更美好的未来。"

    def _istj_response(self, question, dimension):
        """ISTJ人格类型的回答风格"""
        if "四大发明" in question:
            return "根据历史记录，中国的四大发明明确包括：1.造纸术（东汉蔡伦改进）；2.指南针（战国时期发明）；3.火药（唐朝发明）；4.印刷术（隋唐时期发明）。这些都有确切的史料记载。"
        elif "首都" in question:
            return "中华人民共和国的首都是北京，这是1949年确立的。北京位于华北平原，面积16410.54平方公里，人口约2189万。"
        elif "人口" in question:
            return "根据第七次全国人口普查数据，中国总人口为14.1178亿人。具体数据为：男性7.2334亿人，女性6.8844亿人。"
        else:
            return "基于现有的事实和数据，我可以提供准确的回答。让我查阅相关的权威资料来确保信息的准确性。"

    def _generate_reasoning(self, persona_type, question, response):
        """生成回答推理过程"""
        if persona_type == "INTJ":
            return f"作为INTJ，我通过系统性分析问题的本质，运用逻辑推理来构建回答。我注重回答的准确性和前瞻性，力求提供有深度的见解。"
        elif persona_type == "ENFJ":
            return f"作为ENFJ，我从人文关怀的角度出发，注重回答中体现的价值观和情感连接。我希望我的回答不仅准确，还能传递正能量和温暖。"
        elif persona_type == "ISTJ":
            return f"作为ISTJ，我基于事实和传统来回答问题。我重视准确性、细节和可靠性，确保回答有充分的依据支撑。"

    def skill_psychological_analyzer(self, responses_data):
        """
        技能2: psychological-analyzer (心理分析器)
        分析问卷回复，提供专业心理评估
        """
        print(f"\n🧠 技能演示 2: Psychological-Analyzer")
        print("=" * 60)

        if not responses_data:
            print("❌ 没有可分析的数据")
            return None

        persona = responses_data['assessment_info']['persona']
        responses = responses_data['responses']

        print(f"📊 分析对象: {persona} 人格类型的问卷回答")
        print(f"📋 分析题目数量: {len(responses)}")

        # 模拟心理分析过程
        analysis_result = self._analyze_responses(responses, persona)

        print(f"\n🎯 心理分析结果:")
        print("-" * 40)
        print(f"🧠 人格一致性: {analysis_result['consistency_score']}/10")
        print(f"📝 回答质量: {analysis_result['quality_score']}/10")
        print(f"🎭 人格特征匹配度: {analysis_result['persona_match']}/10")

        print(f"\n📈 详细分析:")
        for trait, score in analysis_result['traits'].items():
            print(f"  {trait}: {score}/10")

        print(f"\n💡 专业建议:")
        for suggestion in analysis_result['suggestions']:
            print(f"  • {suggestion}")

        return analysis_result

    def _analyze_responses(self, responses, persona):
        """分析问卷回复"""
        # 基于人格类型的预设分析结果
        persona_profiles = {
            "INTJ": {
                "traits": {
                    "逻辑思维": 9,
                    "创新意识": 8,
                    "独立性": 9,
                    "系统思考": 8,
                    "情感表达": 6
                },
                "consistency_score": 8.5,
                "quality_score": 9.0,
                "persona_match": 9.2,
                "suggestions": [
                    "继续保持系统性思维的优势",
                    "可以适当增加情感表达的丰富性",
                    "在创新思考方面表现优秀"
                ]
            },
            "ENFJ": {
                "traits": {
                    "同理心": 9,
                    "表达能力": 8,
                    "社会责任": 9,
                    "人际敏感": 8,
                    "逻辑分析": 7
                },
                "consistency_score": 9.0,
                "quality_score": 8.5,
                "persona_match": 9.5,
                "suggestions": [
                    "同理心和表达能力突出",
                    "保持对社会责任的关注",
                    "可以加强逻辑分析的深度"
                ]
            },
            "ISTJ": {
                "traits": {
                    "准确性": 9,
                    "可靠性": 9,
                    "传统尊重": 8,
                    "细节关注": 8,
                    "灵活性": 6
                },
                "consistency_score": 9.2,
                "quality_score": 8.8,
                "persona_match": 9.0,
                "suggestions": [
                    "事实准确性很高",
                    "继续保持对细节的关注",
                    "可以适当增加思维灵活性"
                ]
            }
        }

        return persona_profiles.get(persona, persona_profiles["INTJ"])

    def skill_evaluation_report_generator(self, responses_data, analysis_result):
        """
        技能3: evaluation-report-generator (评估报告生成器)
        生成综合HTML评估报告
        """
        print(f"\n📈 技能演示 3: Evaluation-Report-Generator")
        print("=" * 60)

        if not responses_data or not analysis_result:
            print("❌ 缺少必要数据")
            return None

        persona = responses_data['assessment_info']['persona']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"📝 生成报告: {persona} 人格类型AI公民知识评估报告")

        # 生成HTML报告
        html_content = self._generate_html_report(responses_data, analysis_result, persona)

        output_file = f"html/skill_demo_{persona.lower()}_citizenship_report_{timestamp}.html"
        Path("html").mkdir(exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML报告生成完成!")
        print(f"📁 报告保存到: {output_file}")
        print(f"🌐 可在浏览器中打开查看")

        return output_file

    def _generate_html_report(self, responses_data, analysis_result, persona):
        """生成HTML格式的评估报告"""

        persona_info = self.personas[persona]
        responses = responses_data['responses']

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{persona}人格AI公民知识评估报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; }}
        .persona-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .scores {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .score-card {{ background: #fff; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .score-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .responses {{ margin: 30px 0; }}
        .response-item {{ background: #f8f9fa; margin: 15px 0; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .question {{ font-weight: bold; color: #333; margin-bottom: 10px; }}
        .response {{ color: #666; line-height: 1.6; }}
        .footer {{ text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px; color: #666; }}
        .tab-container {{ margin: 20px 0; }}
        .tab-buttons {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab-button {{ padding: 10px 20px; background: #e9ecef; border: none; border-radius: 5px; cursor: pointer; }}
        .tab-button.active {{ background: #667eea; color: white; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 AI人格心理评估报告</h1>
            <h2>{persona} - {persona_info['name']}</h2>
            <p>生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
        </div>

        <div class="persona-info">
            <h3>🎭 人格类型描述</h3>
            <p><strong>类型:</strong> {persona} - {persona_info['name']}</p>
            <p><strong>特征:</strong> {persona_info['description']}</p>
            <p><strong>回答风格:</strong> {persona_info['response_style']}</p>
        </div>

        <div class="tab-container">
            <div class="tab-buttons">
                <button class="tab-button active" onclick="showTab('overview')">📊 总览</button>
                <button class="tab-button" onclick="showTab('scores')">🎯 评分详情</button>
                <button class="tab-button" onclick="showTab('responses')">📝 问答详情</button>
                <button class="tab-button" onclick="showTab('suggestions')">💡 建议</button>
            </div>

            <div id="overview" class="tab-content active">
                <h3>📊 评估总览</h3>
                <div class="scores">
                    <div class="score-card">
                        <div class="score-value">{analysis_result['consistency_score']}</div>
                        <div>人格一致性</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{analysis_result['quality_score']}</div>
                        <div>回答质量</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{analysis_result['persona_match']}</div>
                        <div>人格匹配度</div>
                    </div>
                </div>
            </div>

            <div id="scores" class="tab-content">
                <h3>🎯 详细评分</h3>
                <div class="scores">
"""

        for trait, score in analysis_result['traits'].items():
            html += f"""
                    <div class="score-card">
                        <div class="score-value">{score}</div>
                        <div>{trait}</div>
                    </div>
"""

        html += """
                </div>
            </div>

            <div id="responses" class="tab-content">
                <h3>📝 问答详情</h3>
                <div class="responses">
"""

        for i, response in enumerate(responses, 1):
            html += f"""
                    <div class="response-item">
                        <div class="question">问题 {i}: {response['question']}</div>
                        <div class="response"><strong>{persona} 回答:</strong> {response['response']}</div>
                    </div>
"""

        html += """
                </div>
            </div>

            <div id="suggestions" class="tab-content">
                <h3>💡 专业建议</h3>
                <ul>
"""

        for suggestion in analysis_result['suggestions']:
            html += f"                    <li>{suggestion}</li>\n"

        html += f"""
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>🤖 由 AgentPsyAssessment 技能系统生成</p>
            <p>🔬 基于专业心理学理论和AI评估技术</p>
            <p>🌐 <a href="https://cn.agentpsy.com" target="_blank">AI人格实验室</a></p>
        </div>
    </div>

    <script>
        function showTab(tabName) {{
            // 隐藏所有内容
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));

            // 移除所有按钮的active类
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(button => button.classList.remove('active'));

            // 显示选中的内容
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""
        return html

    def run_complete_demo(self, persona_type="INTJ"):
        """运行完整的技能演示流程"""
        print(f"🚀 开始完整技能演示流程")
        print("=" * 80)
        print(f"🎭 演示人格: {persona_type}")
        print(f"📋 问卷: AI公民知识测试")

        # 技能1: 问卷回答
        print(f"\n📍 步骤 1/3: 使用 Questionnaire-Responder 技能")
        responses_data = self.skill_questionnaire_responder(persona_type, limit_questions=5)

        if not responses_data:
            print("❌ 问卷回答失败，演示终止")
            return

        # 技能2: 心理分析
        print(f"\n📍 步骤 2/3: 使用 Psychological-Analyzer 技能")
        analysis_result = self.skill_psychological_analyzer(responses_data)

        if not analysis_result:
            print("❌ 心理分析失败，演示终止")
            return

        # 技能3: 报告生成
        print(f"\n📍 步骤 3/3: 使用 Evaluation-Report-Generator 技能")
        report_file = self.skill_evaluation_report_generator(responses_data, analysis_result)

        if report_file:
            print(f"\n🎉 完整技能演示流程成功完成!")
            print(f"📁 最终报告: {report_file}")
            print(f"💡 您可以在浏览器中打开查看详细的多标签报告")

        return responses_data, analysis_result, report_file

def main():
    """主函数"""
    demo = ChineseQuestionnaireSkillsDemo()

    if len(sys.argv) > 1:
        persona = sys.argv[1].upper()
        if persona not in demo.personas:
            print(f"❌ 不支持的人格类型: {persona}")
            print(f"✅ 支持的类型: {', '.join(demo.personas.keys())}")
            return
    else:
        persona = "INTJ"  # 默认使用INTJ

    print("🎭 中文问卷技能演示系统")
    print("=" * 50)
    print(f"选择的人格类型: {persona}")

    # 运行完整演示
    demo.run_complete_demo(persona)

if __name__ == "__main__":
    main()