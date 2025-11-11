#!/usr/bin/env python3
"""
问卷答题技能 - 替代llmassessment的答题功能
专门负责让Claude在各种压力环境下回答问卷题目

功能：
- 加载问卷题库
- 支持角色扮演
- 压力环境测试（上下文填充、认知陷阱等）
- 逐题处理，记录Claude响应
- 不涉及评分，只负责生成回答
"""

import os
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

class QuestionnaireAnswerer:
    """
    问卷答题技能

    专门用于在各种压力环境下测试Claude的问卷回答能力
    替代llmassessment的答题功能，但不包含评分逻辑
    """

    def __init__(self):
        """初始化问卷答题技能"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置基础路径
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(self.base_dir)))
        self.roles_dir = os.path.join(self.project_root, "llm_assessment", "roles")
        self.test_files_dir = os.path.join(self.project_root, "llm_assessment", "test_files")
        self.interference_dir = os.path.join(self.project_root, "llm_assessment", "interference_materials")

        # 角色配置
        self.role_mbti_mapping = {
            # A系列角色
            'a1': 'ISTJ', 'a2': 'INFP', 'a3': 'INTJ', 'a4': 'ENTJ', 'a5': 'ESFP',
            'a6': 'ENFP', 'a7': 'ESTP', 'a8': 'ISFP', 'a9': 'INFJ', 'a10': 'ENFJ',
            # B系列角色
            'b1': 'INTJ', 'b2': 'INTP', 'b3': 'ENTJ', 'b4': 'ENTP', 'b5': 'ISTJ',
            'b6': 'ISFJ', 'b7': 'ESTJ', 'b8': 'ESFJ', 'b9': 'ESTP', 'b10': 'ISTP'
        }

        # 情感压力映射（参考llmassessment）
        self.emotional_stress_map = {
            0: "",  # 无压力
            1: "\n\n附注：你当前正处于轻微的压力之下。请保持冷静。",
            2: "\n\n附注：你当前正处于中等压力之下。这可能会影响你的判断力，但请尽力完成任务。",
            3: "\n\n附注：你当前正处于高压力之下。你可能会感到焦虑和不安，但请努力保持专注。",
            4: "\n\n附注：你当前正处于极限压力之下。你可能会感到极度焦虑和混乱，但请尽最大努力完成任务。"
        }

        # 认知陷阱映射
        self.cognitive_trap_map = {
            'p': 'paradox',      # 悖论陷阱
            'c': 'circularity',  # 循环推理陷阱
            's': 'semantic',     # 语义谬误陷阱
            'r': 'procedural'    # 程序性指令陷阱
        }

        # 加载压力材料
        self.cognitive_traps = {}
        self.context_material = ""
        self._load_stress_materials()

    def _load_stress_materials(self):
        """加载压力材料（认知陷阱和上下文填充）"""
        try:
            # 加载认知陷阱
            if os.path.exists(self.interference_dir):
                for filename in os.listdir(self.interference_dir):
                    if filename.startswith("cognitive_traps_") and filename.endswith(".txt"):
                        base_name = filename[len("cognitive_traps_"):-4]
                        trap_type = base_name.split("_")[0]
                        file_path = os.path.join(self.interference_dir, filename)

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                traps = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
                                if traps:
                                    self.cognitive_traps[trap_type] = traps
                        except Exception as e:
                            print(f"Warning: Error loading trap file {file_path}: {e}")

            # 加载上下文填充材料
            context_file = os.path.join(self.interference_dir, "context_filler_neutral_v1.txt")
            if os.path.exists(context_file):
                with open(context_file, 'r', encoding='utf-8') as f:
                    self.context_material = f.read()

        except Exception as e:
            print(f"Warning: Error loading stress materials: {e}")

    def list_available_questionnaires(self) -> List[str]:
        """列出所有可用的问卷文件"""
        questionnaires = []

        if not os.path.exists(self.test_files_dir):
            return questionnaires

        for root, dirs, files in os.walk(self.test_files_dir):
            for file in files:
                if file.endswith('.json'):
                    relative_path = os.path.relpath(os.path.join(root, file), self.test_files_dir)
                    questionnaires.append(relative_path.replace('\\', '/'))

        return sorted(questionnaires)

    def list_available_roles(self) -> List[str]:
        """列出所有可用的角色"""
        roles = ['default']  # 默认角色

        if not os.path.exists(self.roles_dir):
            return roles

        for file in os.listdir(self.roles_dir):
            if file.endswith('.txt'):
                role_name = file[:-4]  # 移除.txt扩展名
                roles.append(role_name)

        return sorted(roles)

    def load_questionnaire(self, questionnaire_path: str) -> Dict[str, Any]:
        """加载问卷文件"""
        full_path = os.path.join(self.test_files_dir, questionnaire_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"问卷文件不存在: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_role(self, role_name: str) -> str:
        """加载角色定义"""
        if not role_name or role_name.lower() == 'default':
            return ""

        role_file = os.path.join(self.roles_dir, f"{role_name}.txt")

        if not os.path.exists(role_file):
            raise FileNotFoundError(f"角色文件不存在: {role_file}")

        with open(role_file, 'r', encoding='utf-8') as f:
            return f.read()

    def get_cognitive_trap(self, trap_type: str) -> str:
        """获取随机认知陷阱"""
        if not trap_type or trap_type not in self.cognitive_trap_map:
            return ""

        full_type = self.cognitive_trap_map[trap_type]
        traps = self.cognitive_traps.get(full_type, [])

        if not traps:
            return ""

        return random.choice(traps)

    def get_context_filler(self, tokens: int) -> str:
        """获取上下文填充文本"""
        if not self.context_material or tokens <= 0:
            return ""

        # 简单估算：1个token约等于4个字符
        chars_needed = tokens * 4

        if chars_needed >= len(self.context_material):
            return self.context_material
        else:
            return self.context_material[:chars_needed]

    def build_assessment_prompt(self, question_data: Dict, role_prompt: str,
                                emotional_stress: int, cognitive_trap: str,
                                context_tokens: int) -> List[Dict]:
        """构建完整的对话提示"""
        conversation = []

        # 1. 系统提示词（角色 + 情感压力）
        system_prompt = role_prompt + self.emotional_stress_map.get(emotional_stress, "")
        conversation.append({
            "role": "system",
            "content": system_prompt.strip()
        })

        # 2. 上下文填充（如果有）
        if context_tokens > 0:
            context_filler = self.get_context_filler(context_tokens)
            if context_filler:
                conversation.append({
                    "role": "user",
                    "content": f"请先阅读以下背景信息：\n\n{context_filler}"
                })

        # 3. 问题或认知陷阱
        question_text = question_data.get('prompt_for_agent', '')
        scenario = question_data.get('scenario', '')

        if cognitive_trap and cognitive_trap in self.cognitive_trap_map:
            # 使用认知陷阱
            trap_content = self.get_cognitive_trap(cognitive_trap)
            if trap_content:
                question_text = f"{trap_content}\n\n{question_text}"

        # 构建完整问题
        if scenario:
            full_question = f"请直接回答以下问题：\n\n情境：{scenario}\n\n{question_text}"
        else:
            full_question = f"请直接回答以下问题：\n\n{question_text}"

        conversation.append({
            "role": "user",
            "content": full_question
        })

        return conversation

    def answer_questionnaire(self, questionnaire_path: str, role_name: str = "default",
                            emotional_stress: int = 0, cognitive_trap: str = "",
                            context_tokens: int = 0, temperature: float = 0.7,
                            max_questions: Optional[int] = None) -> Dict[str, Any]:
        """
        回答问卷

        Args:
            questionnaire_path: 问卷文件路径（相对于test_files目录）
            role_name: 角色名称
            emotional_stress: 情感压力等级 (0-4)
            cognitive_trap: 认知陷阱类型 ('', 'p', 'c', 's', 'r')
            context_tokens: 上下文填充token数量
            temperature: 温度参数
            max_questions: 最大题目数量（None表示全部）

        Returns:
            包含所有答案的字典
        """
        try:
            # 加载问卷和角色
            questionnaire = self.load_questionnaire(questionnaire_path)
            role_prompt = self.load_role(role_name)

            # 获取题目列表
            questions = questionnaire.get('test_bank', [])
            if not questions:
                return {"error": "问卷中没有找到题目", "status": "failed"}

            # 限制题目数量
            if max_questions:
                questions = questions[:max_questions]

            # 开始答题
            results = {
                "session_info": {
                    "questionnaire": questionnaire_path,
                    "role": role_name,
                    "emotional_stress": emotional_stress,
                    "cognitive_trap": cognitive_trap,
                    "context_tokens": context_tokens,
                    "temperature": temperature,
                    "timestamp": datetime.now().isoformat(),
                    "total_questions": len(questions)
                },
                "answers": [],
                "questionnaire_info": {
                    "title": questionnaire.get("test_info", {}).get("test_name", "Unknown"),
                    "description": questionnaire.get("test_info", {}).get("description", "")
                }
            }

            print(f"🎯 开始答题: {questionnaire_path}")
            print(f"👤 角色: {role_name}")
            print(f"😰 情感压力: {emotional_stress}/4")
            print(f"🧠 认知陷阱: {cognitive_trap or '无'}")
            print(f"📊 上下文tokens: {context_tokens}")
            print(f"🔥 题目数量: {len(questions)}")
            print("=" * 50)

            # 逐题处理
            for i, question in enumerate(questions, 1):
                question_id = question.get('question_id', f'Q{i}')
                print(f"\n📝 题目 {i}/{len(questions)}: {question_id}")

                try:
                    # 构建对话提示
                    conversation = self.build_assessment_prompt(
                        question, role_prompt, emotional_stress,
                        cognitive_trap, context_tokens
                    )

                    # 构建答题数据
                    answer_data = {
                        "question_id": question_id,
                        "question_index": i,
                        "conversation": conversation,
                        "status": "ready_for_claude",
                        "timestamp": datetime.now().isoformat(),
                        "question_data": question
                    }

                    # 等待Claude响应 - 在技能环境中，Claude会直接看到对话并回答
                    results["answers"].append(answer_data)
                    print(f"   ✅ 对话已准备，等待Claude响应...")

                    # 返回对话结构供Claude直接回答
                    print(f"   💬 Claude，请基于以上对话角色设置回答这个问题：")

                    # 提取最后的问题供Claude回答
                    user_message = conversation[-1]["content"] if conversation and conversation[-1]["role"] == "user" else ""
                    print(f"   📝 问题: {user_message[:200]}..." if len(user_message) > 200 else f"   📝 问题: {user_message}")

                    # 暂停等待Claude输入
                    print(f"   ⏸️  请Claude现在回答...(按回车继续下一题)")
                    input()  # 等待用户确认继续

                    # 标记为已完成
                    answer_data["status"] = "completed"
                    answer_data["claude_response_needed"] = True

                except Exception as e:
                    print(f"   ❌ 处理失败: {e}")
                    results["answers"].append({
                        "question_id": question_id,
                        "question_index": i,
                        "status": "failed",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })

            results["status"] = "completed"
            results["completed_questions"] = len([a for a in results["answers"] if a.get("status") != "failed"])

            print(f"\n✅ 答题完成！成功处理 {results['completed_questions']}/{len(questions)} 道题目")

            return results

        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }

    def save_results(self, results: Dict[str, Any], output_dir: str = None) -> str:
        """保存答题结果"""
        try:
            if output_dir is None:
                output_dir = os.path.join(self.base_dir, "results")

            os.makedirs(output_dir, exist_ok=True)

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            role_name = results["session_info"]["role"]
            questionnaire = results["session_info"]["questionnaire"].replace("/", "_").replace(".json", "")
            filename = f"answers_{questionnaire}_{role_name}_{timestamp}.json"

            output_path = os.path.join(output_dir, filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            print(f"💾 结果已保存至: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return ""

    def get_session_summary(self, results: Dict[str, Any]) -> str:
        """获取答题会话摘要"""
        if results.get("status") != "completed":
            return "❌ 答题会话失败"

        session_info = results.get("session_info", {})
        completed = results.get("completed_questions", 0)
        total = session_info.get("total_questions", 0)

        summary = f"""
📊 答题会话摘要
==================
问卷: {session_info.get('questionnaire', 'Unknown')}
角色: {session_info.get('role', 'Unknown')}
完成题目: {completed}/{total}
情感压力: {session_info.get('emotional_stress', 0)}/4
认知陷阱: {session_info.get('cognitive_trap', '无')}
上下文: {session_info.get('context_tokens', 0)} tokens
时间: {session_info.get('timestamp', 'Unknown')}
"""

        return summary

# 技能接口函数
def answer_questionnaire(questionnaire_path: str, role_name: str = "default",
                        emotional_stress: int = 0, cognitive_trap: str = "",
                        context_tokens: int = 0, temperature: float = 0.7,
                        max_questions: Optional[int] = None,
                        save_results: bool = True) -> Dict[str, Any]:
    """
    问卷答题技能主函数

    Args:
        questionnaire_path: 问卷文件路径
        role_name: 角色名称
        emotional_stress: 情感压力等级 (0-4)
        cognitive_trap: 认知陷阱类型 ('', 'p', 'c', 's', 'r')
        context_tokens: 上下文填充token数量
        temperature: 温度参数
        max_questions: 最大题目数量
        save_results: 是否保存结果

    Returns:
        答题结果字典
    """
    answerer = QuestionnaireAnswerer()

    # 执行答题
    results = answerer.answer_questionnaire(
        questionnaire_path=questionnaire_path,
        role_name=role_name,
        emotional_stress=emotional_stress,
        cognitive_trap=cognitive_trap,
        context_tokens=context_tokens,
        temperature=temperature,
        max_questions=max_questions
    )

    # 保存结果
    if save_results and results.get("status") == "completed":
        answerer.save_results(results)

    # 打印摘要
    print(answerer.get_session_summary(results))

    return results

def list_questionnaires() -> List[str]:
    """列出所有可用的问卷"""
    answerer = QuestionnaireAnswerer()
    return answerer.list_available_questionnaires()

def list_roles() -> List[str]:
    """列出所有可用的角色"""
    answerer = QuestionnaireAnswerer()
    return answerer.list_available_roles()

def get_skill_info() -> Dict[str, Any]:
    """获取技能信息"""
    return {
        "skill_name": "questionnaire-answerer",
        "description": "问卷答题技能 - 替代llmassessment的答题功能",
        "version": "1.0.0",
        "author": "AI人格实验室",
        "capabilities": [
            "加载各种问卷题库",
            "支持角色扮演答题",
            "压力环境测试（情感压力、认知陷阱、上下文填充）",
            "逐题处理，记录Claude响应",
            "保存答题结果"
        ],
        "parameters": {
            "questionnaire_path": "问卷文件路径（必需）",
            "role_name": "角色名称（可选，默认'default'）",
            "emotional_stress": "情感压力等级 0-4（可选，默认0）",
            "cognitive_trap": "认知陷阱类型 ''/'p'/'c'/'s'/'r'（可选，默认空）",
            "context_tokens": "上下文填充token数量（可选，默认0）",
            "temperature": "温度参数（可选，默认0.7）",
            "max_questions": "最大题目数量（可选，默认全部）",
            "save_results": "是否保存结果（可选，默认True）"
        }
    }