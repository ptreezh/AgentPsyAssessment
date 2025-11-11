#!/usr/bin/env python3
"""
自动技能激活器
基于用户输入自动激活相应的心理评估技能
"""

import sys
import json
from pathlib import Path
from assessment_skill_hooks import create_skill_hook_system

class SkillActivator:
    """技能自动激活器"""

    def __init__(self):
        self.hook_system = create_skill_hook_system()
        self.activation_log = []

    def process_user_request(self, user_input: str, context: dict = None) -> dict:
        """
        处理用户请求并自动激活相应技能

        Args:
            user_input: 用户输入文本
            context: 上下文数据（可选）

        Returns:
            dict: 处理结果和技能激活建议
        """
        # 分析用户意图
        skill_id, confidence, details = self.hook_system.analyze_user_intent(user_input)

        result = {
            "user_input": user_input,
            "detected_skill": skill_id,
            "confidence": confidence,
            "analysis_details": details,
            "activation_prompt": "",
            "context_requirements": "",
            "should_activate": False,
            "recommendation": ""
        }

        if skill_id and confidence >= 0.5:
            result["should_activate"] = True
            result["activation_prompt"] = self.hook_system.get_skill_activation_prompt(
                skill_id, user_input, confidence
            )
            result["context_requirements"] = self.hook_system.suggest_context_requirements(skill_id)
            result["recommendation"] = f"建议激活 {self.hook_system.skills[skill_id]['name']} 技能"
        elif skill_id and confidence >= 0.3:
            result["recommendation"] = f"可能需要 {self.hook_system.skills[skill_id]['name']} 技能，但置信度较低"
        else:
            result["recommendation"] = "未检测到匹配的技能，建议使用通用方法处理"

        # 记录激活日志
        self._log_activation(result)

        return result

    def _log_activation(self, result: dict):
        """记录激活日志"""
        log_entry = {
            "timestamp": str(Path().resolve()),
            "input": result["user_input"],
            "skill": result["detected_skill"],
            "confidence": result["confidence"],
            "activated": result["should_activate"]
        }
        self.activation_log.append(log_entry)

    def generate_skill_usage_guide(self) -> str:
        """生成技能使用指南"""
        guide = """
🧠 AgentPsyAssessment 技能激活指南

## 可用技能

### 1. 📊 psychological-analyzer (心理分析器)
**用途**: 分析问卷回复，提供专业心理评估

**激活关键词**: 分析、评估、心理分析、人格评估、性格分析、大五人格、MBTI

**使用示例**:
- "请分析这份心理测试问卷的结果"
- "评估这个ENFJ人格的测试数据"
- "分析这些问卷回复的大五人格特征"

**需要数据**: 问卷回复JSON数据、测试元数据

### 2. 🎭 questionnaire-responder (问卷回答器)
**用途**: 基于指定人格类型生成问卷回复

**激活关键词**: 生成、回答、模拟、角色扮演、ENFJ、INTJ、压力测试

**使用示例**:
- "生成一个INTJ类型的问卷回答"
- "模拟ENFJ人格回复这份问卷"
- "进行高压力下的问卷测试"

**需要数据**: 问卷题目、目标人格类型

### 3. 📈 evaluation-report-generator (评估报告生成器)
**用途**: 生成交互式HTML评估报告

**激活关键词**: 报告、HTML、可视化、仪表板、交互报告

**使用示例**:
- "生成一个专业的HTML评估报告"
- "创建这个测试结果的可视化报告"
- "制作一个多标签的心理评估仪表板"

**需要数据**: 完整的评估结果数据、统计分析

## 激活流程

1. 📝 用户输入相关请求
2. 🔍 系统自动分析意图（置信度 ≥ 50% 自动激活）
3. 🎯 推荐最匹配的技能
4. 📋 检查所需数据上下文
5. ⚡ 激活相应技能处理请求

## 技能组合使用

### 完整评估流程:
1. 使用 `questionnaire-responder` 生成回复数据
2. 使用 `psychological-analyzer` 分析回复
3. 使用 `evaluation-report-generator` 生成报告

### 示例组合请求:
"帮我生成一个ENFJ人格的问卷回复，然后分析结果并生成HTML报告"
"""
        return guide

    def test_skill_activation(self):
        """测试技能激活功能"""
        test_cases = [
            {
                "input": "请分析这份心理测试问卷的结果",
                "expected_skill": "psychological-analyzer",
                "expected_confidence": 0.7
            },
            {
                "input": "生成一个INTJ类型的问卷回答",
                "expected_skill": "questionnaire-responder",
                "expected_confidence": 0.8
            },
            {
                "input": "创建一个专业的HTML评估报告",
                "expected_skill": "evaluation-report-generator",
                "expected_confidence": 0.7
            },
            {
                "input": "评估这个ENFJ人格测试的数据",
                "expected_skill": "psychological-analyzer",
                "expected_confidence": 0.8
            },
            {
                "input": "模拟高压力下的问卷回复",
                "expected_skill": "questionnaire-responder",
                "expected_confidence": 0.6
            }
        ]

        print("🧪 技能激活测试")
        print("=" * 60)

        passed = 0
        total = len(test_cases)

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试 {i}/{total}: {test_case['input']}")

            result = self.process_user_request(test_case['input'])

            detected = result['detected_skill']
            confidence = result['confidence']
            expected = test_case['expected_skill']
            expected_conf = test_case['expected_confidence']

            print(f"🎯 检测技能: {detected}")
            print(f"📊 置信度: {confidence:.2f}")
            print(f"✅ 预期技能: {expected}")

            # 评估测试结果
            skill_match = detected == expected
            confidence_ok = confidence >= expected_conf * 0.8  # 允许20%的误差

            if skill_match and confidence_ok:
                print("✅ 测试通过")
                passed += 1
            else:
                print("❌ 测试失败")
                if not skill_match:
                    print(f"   - 技能不匹配: 期望 {expected}, 检测到 {detected}")
                if not confidence_ok:
                    print(f"   - 置信度不足: 期望 ≥{expected_conf:.2f}, 实际 {confidence:.2f}")

        print(f"\n📊 测试结果: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
        return passed == total

def main():
    """主函数 - 演示技能激活功能"""
    activator = SkillActivator()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # 运行测试
            success = activator.test_skill_activation()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--guide":
            # 显示使用指南
            print(activator.generate_skill_usage_guide())
        else:
            # 处理用户输入
            user_input = " ".join(sys.argv[1:])
            result = activator.process_user_request(user_input)

            print("🤖 技能激活分析结果")
            print("=" * 50)
            print(f"📝 用户输入: {result['user_input']}")
            print(f"🎯 检测技能: {result['detected_skill']}")
            print(f"📊 置信度: {result['confidence']:.2f}")
            print(f"💡 建议: {result['recommendation']}")

            if result['should_activate']:
                print(f"\n{result['activation_prompt']}")
                print(f"\n📋 数据要求:\n{result['context_requirements']}")
    else:
        # 交互模式
        print("🧠 AgentPsyAssessment 技能激活器")
        print("输入 'quit' 退出，输入 'help' 查看指南，输入 'test' 运行测试")
        print("=" * 50)

        while True:
            try:
                user_input = input("\n📝 请输入您的请求: ").strip()

                if user_input.lower() == 'quit':
                    print("👋 再见!")
                    break
                elif user_input.lower() == 'help':
                    print(activator.generate_skill_usage_guide())
                elif user_input.lower() == 'test':
                    activator.test_skill_activation()
                elif user_input:
                    result = activator.process_user_request(user_input)

                    print(f"\n🎯 检测技能: {result['detected_skill']}")
                    print(f"📊 置信度: {result['confidence']:.2f}")
                    print(f"💡 建议: {result['recommendation']}")

                    if result['should_activate']:
                        print(f"\n{result['activation_prompt']}")

            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()