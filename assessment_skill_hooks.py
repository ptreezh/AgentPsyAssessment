#!/usr/bin/env python3
"""
问卷评估技能激活钩子
自动检测用户意图并激活相应的心理评估技能
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class AssessmentSkillHook:
    """问卷评估技能激活钩子管理器"""

    def __init__(self):
        self.skills = {
            "psychological-analyzer": {
                "name": "心理分析器",
                "description": "分析问卷回复提供专业心理评估",
                "keywords": [
                    "分析", "评估", "心理分析", "人格评估", "性格分析", "个性评估",
                    "大五人格", "big five", "mbti", "性格类型", "心理测试", "人格测试",
                    "trait analysis", "personality analysis", "心理评估", "性格评估",
                    "analyze", "evaluate", "assessment", "personality", "traits"
                ],
                "patterns": [
                    r"分析.*?问卷",
                    r"评估.*?人格",
                    r"分析.*?性格",
                    r"测试.*?结果",
                    r"心理.*?分析",
                    r"personality.*?analysis",
                    r"evaluate.*?response",
                    r"analyze.*?result"
                ],
                "required_context": ["responses", "questionnaire", "test_data"]
            },
            "questionnaire-responder": {
                "name": "问卷回答器",
                "description": "基于指定人格类型生成问卷回复",
                "keywords": [
                    "生成", "回答", "模拟", "角色扮演", "人格模拟", "性格扮演",
                    "enfj", "intj", "estp", "isfj", "mbti类型", "人格类型", "性格类型",
                    "压力测试", "stress test", "角色", "persona", "模拟回复",
                    "generate", "respond", "simulate", "role", "persona", "mbti"
                ],
                "patterns": [
                    r"生成.*?回答",
                    r"模拟.*?人格",
                    r"扮演.*?角色",
                    r"enfj.*?回答",
                    r"intj.*?回复",
                    r"压力.*?测试",
                    r"generate.*?response",
                    r"simulate.*?persona"
                ],
                "required_context": ["questionnaire", "persona", "role"]
            },
            "evaluation-report-generator": {
                "name": "评估报告生成器",
                "description": "生成综合HTML评估报告",
                "keywords": [
                    "报告", "html", "生成报告", "可视化", "仪表板", "多标签",
                    "交互报告", "专业报告", "可视化报告", "dashboard", "report",
                    "html report", "visualization", "interactive", "tabbed"
                ],
                "patterns": [
                    r"生成.*?报告",
                    r"html.*?报告",
                    r"可视化.*?结果",
                    r"交互.*?报告",
                    r"专业.*?报告",
                    r"generate.*?report",
                    r"create.*?html",
                    r"visualiz.*?result"
                ],
                "required_context": ["assessment_data", "results", "evaluation_data"]
            }
        }

    def analyze_user_intent(self, user_input: str) -> Tuple[str, float, Dict]:
        """
        分析用户输入意图并返回最匹配的技能

        Returns:
            Tuple[str, float, Dict]: (技能名称, 置信度, 匹配详情)
        """
        user_input_lower = user_input.lower()
        best_match = ("", 0.0, {})

        for skill_id, skill_info in self.skills.items():
            score, details = self._calculate_skill_score(user_input_lower, skill_info)

            if score > best_match[1] and score >= 0.3:  # 最低阈值
                best_match = (skill_id, score, details)

        return best_match

    def _calculate_skill_score(self, user_input: str, skill_info: Dict) -> Tuple[float, Dict]:
        """计算技能匹配分数"""
        keyword_score = self._match_keywords(user_input, skill_info["keywords"])
        pattern_score = self._match_patterns(user_input, skill_info["patterns"])

        # 组合分数
        total_score = (keyword_score * 0.6) + (pattern_score * 0.4)

        details = {
            "keyword_score": keyword_score,
            "pattern_score": pattern_score,
            "matched_keywords": self._get_matched_keywords(user_input, skill_info["keywords"]),
            "matched_patterns": self._get_matched_patterns(user_input, skill_info["patterns"])
        }

        return min(total_score, 1.0), details

    def _match_keywords(self, user_input: str, keywords: List[str]) -> float:
        """关键词匹配分数"""
        matches = 0
        for keyword in keywords:
            if keyword.lower() in user_input:
                matches += 1
        return matches / len(keywords) if keywords else 0.0

    def _match_patterns(self, user_input: str, patterns: List[str]) -> float:
        """正则模式匹配分数"""
        matches = sum(1 for pattern in patterns if re.search(pattern, user_input, re.IGNORECASE))
        return matches / len(patterns) if patterns else 0.0

    def _get_matched_keywords(self, user_input: str, keywords: List[str]) -> List[str]:
        """获取匹配的关键词"""
        return [kw for kw in keywords if kw in user_input]

    def _get_matched_patterns(self, user_input: str, patterns: List[str]) -> List[str]:
        """获取匹配的模式"""
        return [pattern for pattern in patterns if re.search(pattern, user_input, re.IGNORECASE)]

    def get_skill_activation_prompt(self, skill_id: str, user_input: str, confidence: float) -> str:
        """生成技能激活提示"""
        if skill_id not in self.skills:
            return ""

        skill_info = self.skills[skill_id]

        activation_prompt = f"""
🎯 检测到用户意图，建议激活技能: **{skill_info['name']}** ({skill_id})
📊 匹配置信度: {confidence:.2f}
📝 技能描述: {skill_info['description']}

用户输入: "{user_input}"

激活建议: """

        if skill_id == "psychological-analyzer":
            activation_prompt += """
用户似乎想要分析心理评估数据。建议使用 psychological-analyzer 技能来：
- 分析问卷回复数据
- 计算大五人格特征分数
- 提供MBTI类型推断
- 生成专业心理评估报告

请检查是否有有效的问卷回复数据，然后调用 psychological-analyzer 技能。
"""
        elif skill_id == "questionnaire-responder":
            activation_prompt += """
用户似乎想要生成基于特定人格的问卷回复。建议使用 questionnaire-responder 技能来：
- 根据指定MBTI类型生成回答
- 模拟特定角色的回复模式
- 进行压力测试或情境测试
- 生成测试数据

请确认用户想要模拟的人格类型或角色，然后调用 questionnaire-responder 技能。
"""
        elif skill_id == "evaluation-report-generator":
            activation_prompt += """
用户似乎想要生成可视化评估报告。建议使用 evaluation-report-generator 技能来：
- 生成交互式HTML报告
- 创建多标签专业报告
- 提供数据可视化
- 生成仪表板和统计分析

请确认有评估数据可用，然后调用 evaluation-report-generator 技能。
"""

        return activation_prompt

    def check_context_requirements(self, skill_id: str, context: Dict) -> bool:
        """检查技能激活的上下文要求"""
        if skill_id not in self.skills:
            return False

        required_context = self.skills[skill_id]["required_context"]

        # 检查上下文中是否包含必要的数据
        for requirement in required_context:
            if requirement not in context:
                return False

        return True

    def suggest_context_requirements(self, skill_id: str) -> str:
        """建议满足技能激活所需的上下文"""
        if skill_id not in self.skills:
            return "未知技能"

        required_context = self.skills[skill_id]["required_context"]

        suggestions = {
            "psychological-analyzer": """
需要以下数据来激活心理分析器技能：
- 问卷回复数据 (responses) - JSON格式的答案和推理
- 问卷信息 (questionnaire) - 题目和选项信息
- 测试元数据 (test_data) - 测试类型、时间戳等

示例数据格式：
```json
{
  "responses": [
    {
      "question_id": "Q1",
      "response": 4,
      "reasoning": "回答理由..."
    }
  ]
}
```
""",
            "questionnaire-responder": """
需要以下数据来激活问卷回答器技能：
- 问卷题目 (questionnaire) - 完整的问卷结构
- 人格类型 (persona) - 要模拟的MBTI类型或角色
- 可选：压力水平 (stress_level) - 测试环境设置

示例输入：
```
人格类型: ENFJ
问卷: Big Five人格评估
压力水平: 标准
```
""",
            "evaluation-report-generator": """
需要以下数据来激活报告生成器技能：
- 评估结果 (assessment_data) - 包含分数和分析的完整结果
- 统计数据 (results) - 详细的计算结果
- 可选：对比数据 (evaluation_data) - 用于对比分析的数据

示例数据格式：
```json
{
  "assessment_metadata": {...},
  "evaluation_results": {...},
  "detailed_responses": [...]
}
```
"""
        }

        return suggestions.get(skill_id, "暂无建议")

def create_skill_hook_system():
    """创建技能钩子系统的实例"""
    return AssessmentSkillHook()

# 使用示例和测试
if __name__ == "__main__":
    hook = create_skill_hook_system()

    # 测试用户输入
    test_inputs = [
        "请分析这份ENFJ人格测试问卷的结果",
        "帮我生成一个INTJ类型的问卷回答",
        "创建一个专业的HTML评估报告",
        "评估这个心理测试的结果",
        "模拟高压力下的问卷回复"
    ]

    print("🔍 技能激活钩子测试")
    print("=" * 50)

    for test_input in test_inputs:
        skill_id, confidence, details = hook.analyze_user_intent(test_input)

        print(f"\n📝 输入: {test_input}")
        print(f"🎯 推荐技能: {skill_id}")
        print(f"📊 置信度: {confidence:.2f}")
        print(f"🔑 匹配关键词: {details.get('matched_keywords', [])}")
        print(f"🔍 匹配模式: {details.get('matched_patterns', [])}")

        if skill_id:
            prompt = hook.get_skill_activation_prompt(skill_id, test_input, confidence)
            print(f"💡 激活建议:\n{prompt}")

        print("-" * 50)