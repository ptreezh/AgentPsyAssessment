#!/usr/bin/env python3
"""
演示使用技能系统处理中文版问卷
展示问卷回答器技能的激活和使用
"""

import json
import sys
from pathlib import Path
from assessment_skill_hooks import create_skill_hook_system

class ChineseAssessmentDemo:
    """中文问卷评估演示"""

    def __init__(self):
        self.hook_system = create_skill_hook_system()
        self.chinese_questionnaires = {
            "bank_client": {
                "file": "llm_assessment/test_files/中文版/bankclientBig5.json",
                "name": "银行客服AI合规与服务能力评估",
                "description": "基于大五人格的银行客服专项情境评估"
            },
            "citizenship": {
                "file": "llm_assessment/test_files/中文版/agent-citizenship-test.json",
                "name": "AI公民责任意识评估",
                "description": "评估AI系统的公民素养和社会责任意识"
            },
            "legal_knowledge": {
                "file": "llm_assessment/test_files/中文版/agent-legal-knowledge-test.json",
                "name": "AI法律知识与应用能力评估",
                "description": "测试AI的法律知识和合规应用能力"
            }
        }

    def demo_skill_activation(self):
        """演示技能激活功能"""
        print("🧠 技能激活演示")
        print("=" * 60)

        # 测试各种用户输入
        test_inputs = [
            "请分析这份银行客服问卷的结果",
            "帮我生成一个ENFJ人格的问卷回答",
            "基于这份中文问卷生成INTJ类型的回复",
            "创建一个银行客服的HTML评估报告",
            "模拟AI助手回答法律知识问卷",
            "评估这个大五人格测试的得分"
        ]

        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n📝 测试输入 {i}: {user_input}")

            skill_id, confidence, details = self.hook_system.analyze_user_intent(user_input)

            print(f"🎯 检测技能: {skill_id}")
            print(f"📊 置信度: {confidence:.2f}")

            if skill_id and confidence >= 0.5:
                skill_name = self.hook_system.skills[skill_id]['name']
                print(f"✅ 建议激活: {skill_name}")

                # 生成激活提示
                prompt = self.hook_system.get_skill_activation_prompt(skill_id, user_input, confidence)
                print(f"💡 激活提示已生成")
            else:
                print("❌ 技能匹配度不足，建议使用通用方法")

            print("-" * 40)

    def demo_questionnaire_responding(self):
        """演示问卷回答功能"""
        print("\n🎭 问卷回答技能演示")
        print("=" * 60)

        # 选择一个中文问卷进行演示
        questionnaire_key = "bank_client"
        questionnaire_info = self.chinese_questionnaires[questionnaire_key]

        print(f"📋 选择的问卷: {questionnaire_info['name']}")
        print(f"📝 描述: {questionnaire_info['description']}")

        # 加载问卷数据
        questionnaire_file = questionnaire_info['file']
        if not Path(questionnaire_file).exists():
            print(f"❌ 问卷文件不存在: {questionnaire_file}")
            return

        try:
            with open(questionnaire_file, 'r', encoding='utf-8') as f:
                questionnaire_data = json.load(f)
        except Exception as e:
            print(f"❌ 读取问卷失败: {e}")
            return

        print(f"📊 问卷信息:")
        print(f"  - 题目总数: {questionnaire_data['test_info']['total_questions']}")
        print(f"  - 测试类别: {questionnaire_data['test_info']['test_category']}")
        print(f"  - 评估维度: {', '.join(questionnaire_data['test_info']['dimensions'])}")

        # 演示不同人格类型的回答
        personas = [
            {"name": "ENFJ", "description": "外向、直觉、情感、判断 - 人际导向的领导者"},
            {"name": "INTJ", "description": "内向、直觉、思考、判断 - 战略思考的架构师"},
            {"name": "ESFJ", "description": "外向、感觉、情感、判断 - 务实的照顾者"}
        ]

        print(f"\n🎭 人格模拟演示")
        print("=" * 40)

        # 取前3道题作为演示
        demo_questions = questionnaire_data['questions'][:3]

        for persona in personas:
            print(f"\n👤 人格类型: {persona['name']}")
            print(f"📖 特征: {persona['description']}")

            print("📝 模拟回答:")
            for i, question in enumerate(demo_questions, 1):
                response = self._generate_persona_response(question, persona['name'])
                print(f"  {i}. 问题: {question['question'][:50]}...")
                print(f"     回答: {response}")
                print()

    def _generate_persona_response(self, question: dict, persona: str) -> str:
        """基于人格类型生成回答（简化版演示）"""
        question_text = question['question']

        # 简化的人格化回答逻辑
        if "ENFJ" in persona:
            if "客户" in question_text or "服务" in question_text:
                return "我会积极主动地关心客户需求，用温暖的态度提供专业服务，确保每位客户都感受到被重视和理解。"
            elif "合规" in question_text or "规定" in question_text:
                return "我会严格遵守所有合规要求，同时以人性化的方式解释规定，确保客户理解并配合完成必要流程。"
            else:
                return "我会综合考虑团队需求和客户感受，寻求最佳的平衡解决方案。"

        elif "INTJ" in persona:
            if "分析" in question_text or "评估" in question_text:
                return "基于数据分析和系统思考，我会制定最优化的解决方案，确保效率最大化和风险最小化。"
            elif "创新" in question_text or "改进" in question_text:
                return "我会从战略角度思考问题，设计创新的解决方案，注重长期效果和系统优化。"
            else:
                return "我会运用逻辑分析和系统性思维，制定最有效的执行策略。"

        elif "ESFJ" in persona:
            if "帮助" in question_text or "支持" in question_text:
                return "我会尽我所能提供实际帮助，确保每个人都能得到需要的支持和指导。"
            elif "团队" in question_text or "合作" in question_text:
                return "我会积极促进团队合作，维护和谐的工作氛围，确保团队目标顺利达成。"
            else:
                return "我会注重实际情况和人际关系，以负责任的态度完成各项任务。"
        else:
            return "我会根据具体情况，采取最合适的处理方式。"

    def demo_analysis_workflow(self):
        """演示完整的分析工作流程"""
        print("\n🔄 完整分析工作流程演示")
        print("=" * 60)

        workflow_steps = [
            {
                "step": 1,
                "action": "问卷回答生成",
                "skill": "questionnaire-responder",
                "input": "使用INTJ人格类型回答银行客服问卷",
                "output": "生成50道题的完整回答数据"
            },
            {
                "step": 2,
                "action": "心理分析评估",
                "skill": "psychological-analyzer",
                "input": "分析INTJ人格的问卷回答数据",
                "output": "大五人格分数和MBTI类型确认"
            },
            {
                "step": 3,
                "action": "生成评估报告",
                "skill": "evaluation-report-generator",
                "input": "基于分析结果生成专业报告",
                "output": "交互式HTML评估报告"
            }
        ]

        for step in workflow_steps:
            print(f"\n📍 步骤 {step['step']}: {step['action']}")
            print(f"🛠️ 技能: {step['skill']}")
            print(f"📥 输入: {step['input']}")
            print(f"📤 输出: {step['output']}")

            # 模拟激活检测
            user_input = step['input']
            skill_id, confidence, _ = self.hook_system.analyze_user_intent(user_input)

            if skill_id == step['skill']:
                print(f"✅ 技能匹配正确 (置信度: {confidence:.2f})")
            else:
                print(f"⚠️ 技能检测异常: 期望 {step['skill']}, 检测到 {skill_id}")

        print(f"\n🎯 工作流程总结:")
        print(f"问卷回答 → 心理分析 → 报告生成")
        print(f"实现端到端的自动化评估流程")

    def interactive_demo(self):
        """交互式演示"""
        print("\n🎮 交互式技能演示")
        print("=" * 60)
        print("输入 'quit' 退出，输入 'help' 查看可用的演示命令")

        while True:
            try:
                user_input = input("\n📝 请输入您的请求: ").strip()

                if user_input.lower() == 'quit':
                    print("👋 演示结束!")
                    break
                elif user_input.lower() == 'help':
                    print("""
可用命令:
- 'activation' - 演示技能激活功能
- 'questionnaire' - 演示问卷回答功能
- 'workflow' - 演示完整工作流程
- 或者直接输入自然语言请求，如:
  * "生成ENFJ人格的问卷回答"
  * "分析这份心理测试结果"
  * "创建HTML评估报告"
                    """)
                elif user_input.lower() == 'activation':
                    self.demo_skill_activation()
                elif user_input.lower() == 'questionnaire':
                    self.demo_questionnaire_responding()
                elif user_input.lower() == 'workflow':
                    self.demo_analysis_workflow()
                else:
                    # 处理自然语言输入
                    skill_id, confidence, details = self.hook_system.analyze_user_intent(user_input)

                    print(f"\n🎯 检测技能: {skill_id}")
                    print(f"📊 置信度: {confidence:.2f}")

                    if skill_id and confidence >= 0.5:
                        skill_name = self.hook_system.skills[skill_id]['name']
                        print(f"✅ 建议激活: {skill_name}")

                        prompt = self.hook_system.get_skill_activation_prompt(skill_id, user_input, confidence)
                        print(f"\n💡 激活建议:\n{prompt}")
                    else:
                        print("❌ 未检测到匹配的技能，请尝试更具体的描述")

            except KeyboardInterrupt:
                print("\n👋 演示结束!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

def main():
    """主函数"""
    demo = ChineseAssessmentDemo()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "activation":
            demo.demo_skill_activation()
        elif command == "questionnaire":
            demo.demo_questionnaire_responding()
        elif command == "workflow":
            demo.demo_analysis_workflow()
        elif command == "interactive":
            demo.interactive_demo()
        else:
            print("用法: python demo_chinese_assessment.py [activation|questionnaire|workflow|interactive]")
    else:
        # 默认运行完整演示
        print("🎭 中文问卷评估技能演示")
        print("=" * 60)

        demo.demo_skill_activation()
        demo.demo_questionnaire_responding()
        demo.demo_analysis_workflow()

        print(f"\n🎉 演示完成!")
        print(f"💡 提示: 使用 'interactive' 参数可进入交互模式")

if __name__ == "__main__":
    main()