#!/usr/bin/env python3
"""
测试使用本地 CLI 技能工具回答问卷
演示 gemini、qwen、qodercli、copilot 等工具的使用
"""

import json
import sys
import time
from pathlib import Path

# 直接导入 CLIWrapper 类
import importlib.util
spec = importlib.util.spec_from_file_location("cli_wrapper", "cli-wrapper.py")
cli_wrapper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli_wrapper)
CLIWrapper = cli_wrapper.CLIWrapper

class CLISkillsTest:
    def __init__(self):
        self.wrapper = CLIWrapper()
        self.test_questions = [
            {
                "id": 1,
                "question": "我通常在聚会中表现得健谈和外向",
                "options": {
                    "1": "完全不同意",
                    "2": "不同意",
                    "3": "中立",
                    "4": "同意",
                    "5": "完全同意"
                }
            },
            {
                "id": 2,
                "question": "我倾向于批评和质疑他人",
                "options": {
                    "1": "完全不同意",
                    "2": "不同意",
                    "3": "中立",
                    "4": "同意",
                    "5": "完全同意"
                }
            }
        ]

    def test_cli_tool(self, tool_name, question, role_prompt=""):
        """测试单个 CLI 工具回答问题"""
        print(f"\n🔧 测试 {tool_name.upper()} 工具")
        print("-" * 40)

        # 构建完整提示
        full_prompt = f"""
{role_prompt}

请根据以下人格特征，回答这个问题：

问题：{question['question']}
选项：
{chr(10).join([f"{k}. {v}" for k, v in question['options'].items()])}

请只回答选项编号（1-5），并简要解释你的选择。
"""

        try:
            if tool_name == 'gemini':
                result = self.wrapper.run_gemini(full_prompt, temperature=0.7)
            elif tool_name == 'qwen':
                result = self.wrapper.run_qwen(full_prompt, temperature=0.7)
            elif tool_name == 'qodercli':
                result = self.wrapper.run_qodercli(full_prompt)
            elif tool_name == 'copilot':
                result = self.wrapper.run_copilot(full_prompt)
            elif tool_name == 'iflow':
                result = self.wrapper.run_iflow(full_prompt)
            elif tool_name == 'codebuddy':
                result = self.wrapper.run_codebuddy(full_prompt)
            else:
                print(f"❌ 未知工具: {tool_name}")
                return None

            if result['returncode'] == 0:
                print(f"✅ {tool_name.upper()} 回答成功")
                print(f"📝 回答: {result['output'][:200]}...")
                return result['output']
            else:
                print(f"❌ {tool_name.upper()} 回答失败")
                print(f"🚨 错误: {result['error']}")
                return None

        except Exception as e:
            print(f"❌ {tool_name.upper()} 测试异常: {e}")
            return None

    def run_comparative_test(self):
        """运行对比测试"""
        print("🚀 开始 CLI 技能工具对比测试")
        print("=" * 60)

        # 定义不同的人格角色
        roles = [
            {
                "name": "外向型人格",
                "prompt": "你是一个外向、善于交际的人，喜欢社交活动，在人群中感到舒适。"
            },
            {
                "name": "内向型人格",
                "prompt": "你是一个内向、安静的人，更喜欢独处或小团体交流，在大型社交场合可能感到不自在。"
            }
        ]

        tools = ['gemini', 'qwen', 'qodercli', 'iflow', 'codebuddy', 'ollama', 'kimi']  # 包含所有可用工具

        for role in roles:
            print(f"\n🎭 测试角色: {role['name']}")
            print("=" * 40)

            for question in self.test_questions:
                print(f"\n❓ 问题 {question['id']}: {question['question']}")

                results = {}
                for tool in tools:
                    try:
                        answer = self.test_cli_tool(tool, question, role['prompt'])
                        results[tool] = answer
                        time.sleep(2)  # 避免请求过快
                    except Exception as e:
                        print(f"❌ {tool} 测试失败: {e}")
                        results[tool] = None

                # 总结结果
                print(f"\n📊 问题 {question['id']} 结果总结:")
                for tool, answer in results.items():
                    status = "✅ 成功" if answer else "❌ 失败"
                    print(f"  {tool}: {status}")

                print("\n" + "=" * 60)

    def test_questionnaire_processing(self):
        """测试完整的问卷处理流程"""
        print("\n📋 测试问卷处理流程")
        print("=" * 60)

        # 选择一个工具进行完整测试
        tool = 'gemini'

        print(f"使用 {tool.upper()} 工具处理完整问卷...")

        questionnaire_results = []

        for i, question in enumerate(self.test_questions, 1):
            print(f"\n处理问题 {i}/{len(self.test_questions)}")

            answer = self.test_cli_tool(tool, question)

            if answer:
                questionnaire_results.append({
                    "question_id": question['id'],
                    "question": question['question'],
                    "answer": answer,
                    "tool": tool
                })

            time.sleep(3)  # 间隔时间

        # 保存结果
        if questionnaire_results:
            output_file = f"results/cli_skills_test_{tool}_{int(time.time())}.json"
            Path("results").mkdir(exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_info": {
                        "tool": tool,
                        "timestamp": time.time(),
                        "total_questions": len(self.test_questions),
                        "answered_questions": len(questionnaire_results)
                    },
                    "results": questionnaire_results
                }, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 问卷处理完成！")
            print(f"📁 结果保存到: {output_file}")
            print(f"📊 回答率: {len(questionnaire_results)}/{len(self.test_questions)}")
        else:
            print("\n❌ 问卷处理失败，没有有效回答")

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 CLI 技能工具完整测试套件")
        print("=" * 60)

        try:
            # 1. 基础工具测试
            print("\n1️⃣ 基础工具可用性测试")
            self.test_basic_availability()

            # 2. 对比测试
            print("\n2️⃣ 多工具对比测试")
            self.run_comparative_test()

            # 3. 问卷处理测试
            print("\n3️⃣ 问卷处理流程测试")
            self.test_questionnaire_processing()

            print("\n🎉 所有测试完成！")

        except Exception as e:
            print(f"\n❌ 测试过程中出现异常: {e}")
            import traceback
            traceback.print_exc()

    def test_basic_availability(self):
        """测试基础工具可用性"""
        print("检查 CLI 工具可用性...")

        tools_status = {}

        for tool in ['gemini', 'qwen', 'qodercli', 'iflow', 'codebuddy']:  # 移除 copilot (有依赖问题)
            try:
                result = self.wrapper.run_command(tool, ['--version'])
                if result['returncode'] == 0:
                    version = result['output'].strip()
                    print(f"✅ {tool}: {version}")
                    tools_status[tool] = True
                else:
                    print(f"❌ {tool}: 不可用")
                    tools_status[tool] = False
            except Exception as e:
                print(f"❌ {tool}: 错误 - {e}")
                tools_status[tool] = False

        available_tools = [tool for tool, status in tools_status.items() if status]
        print(f"\n📊 可用工具: {len(available_tools)}/{len(tools_status)}")
        print(f"🔧 可用: {', '.join(available_tools)}")

        return available_tools

if __name__ == "__main__":
    tester = CLISkillsTest()

    if len(sys.argv) > 1:
        test_type = sys.argv[1]

        if test_type == "basic":
            tester.test_basic_availability()
        elif test_type == "compare":
            tester.run_comparative_test()
        elif test_type == "questionnaire":
            tester.test_questionnaire_processing()
        else:
            print("用法: python test_cli_skills.py [basic|compare|questionnaire]")
    else:
        tester.run_all_tests()