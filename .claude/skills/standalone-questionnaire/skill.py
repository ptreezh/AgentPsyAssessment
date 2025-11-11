#!/usr/bin/env python3
"""
独立问卷测评技能 - 大五人格完整版
完全不依赖外部文件和脚本的独立技能
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class StandaloneQuestionnaireSkill:
    """独立问卷测评技能"""

    def __init__(self):
        """初始化技能"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_AUTH_TOKEN')

        # API配置 - 增强配置检测
        base_url = os.getenv('ANTHROPIC_BASE_URL') or os.getenv('dsANTHROPIC_BASE_URL')
        if base_url:
            if base_url.endswith('/anthropic'):
                self.api_base = base_url + '/v1/messages'
            elif base_url.endswith('/api/anthropic'):
                self.api_base = base_url + '/v1/messages'
            else:
                self.api_base = base_url
        else:
            self.api_base = "https://api.anthropic.com/v1/messages"

        # 检测API配置并输出警告
        self._check_api_configuration()

        # 从文件加载角色定义
        self.embedded_roles = self._load_embedded_roles()

        # 从文件加载问卷库
        self.embedded_questionnaires = self._load_embedded_questionnaires()

        # 认知陷阱映射
        self.cognitive_trap_map = {
            'p': 'paradox',      # 悖论陷阱
            'c': 'circularity', # 循环论证
            's': 'semantic',    # 语义谬误
            'r': 'procedural'   # 程序陷阱
        }

        # 认知陷阱材料
        self.cognitive_traps = self._create_cognitive_traps()

        # 上下文填充材料
        self.context_fillers = self._create_context_fillers()

    def _check_api_configuration(self):
        """检查API配置并给出建议"""
        print(f"🔧 API配置检查:")
        print(f"   API端点: {self.api_base}")
        print(f"   API密钥: {'已配置' if self.api_key else '❌ 未配置'}")

        if "open.bigmodel.cn" in self.api_base:
            print(f"⚠️ 检测到智谱API端点")
            print(f"   建议模型: claude-3-5-sonnet-20241022")
            if not self.api_key:
                print(f"   请设置环境变量: ANTHROPIC_API_KEY 或 ANTHROPIC_AUTH_TOKEN")
        elif "api.anthropic.com" in self.api_base:
            print(f"✅ 检测到官方Anthropic API端点")
            print(f"   建议模型: claude-3-sonnet-20240229")
        else:
            print(f"⚠️ 未知API端点，将尝试使用默认配置")

        if not self.api_key:
            print(f"❌ 错误: 未找到API密钥")
            print(f"   请设置环境变量: export ANTHROPIC_API_KEY='your-api-key'")
            print(f"   或在.env文件中配置: ANTHROPIC_API_KEY=your-api-key")

        print()

    def _load_embedded_roles(self) -> Dict[str, Dict]:
        """从技能文件夹加载角色定义"""
        roles = {
            "default": {
                "name": "default",
                "description": "默认角色，无人格设定",
                "mbti": None,
                "personality_prompt": ""
            }
        }

        # 加载MBTI角色文件
        roles_file = os.path.join(os.path.dirname(__file__), "roles", "mbti_roles.json")
        if os.path.exists(roles_file):
            try:
                with open(roles_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 移除JSON注释（如果有的话）
                    lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
                    clean_content = '\n'.join(lines)

                    roles_data = json.loads(clean_content)
                    roles.update(roles_data.get("roles", {}))
                    print(f"✅ 成功加载角色文件: {len(roles_data.get('roles', {}))}个角色")
            except Exception as e:
                print(f"❌ 加载角色文件失败 {roles_file}: {e}")
                # 如果文件加载失败，提供基本的内置角色
                roles.update(self._create_fallback_roles())
        else:
            print(f"⚠️ 角色文件不存在: {roles_file}")
            roles.update(self._create_fallback_roles())

        return roles

    def _create_fallback_roles(self) -> Dict[str, Dict]:
        """创建备用角色定义"""
        return {
            "intj": {
                "name": "intj",
                "description": "建筑师人格 - 理性、战略思维、独立",
                "mbti": "INTJ",
                "personality_prompt": "你是一个INTJ类型的人。你具有战略思维，理性分析，喜欢独立思考。你注重逻辑和效率，倾向于深入思考问题本质。"
            },
            "enfj": {
                "name": "enfj",
                "description": "主人公人格 - 热情、善于沟通、有领导力",
                "mbti": "ENFJ",
                "personality_prompt": "你是一个ENFJ类型的人。你富有同情心，善于理解他人，具有天生的领导力。你重视和谐，喜欢帮助他人成长。"
            }
        }

    def _load_embedded_questionnaires(self) -> Dict[str, Dict]:
        """从技能文件夹加载问卷库"""
        questionnaires = {}

        # 获取问卷文件夹路径
        questionnaire_dir = os.path.join(os.path.dirname(__file__), "questionnaires")

        if not os.path.exists(questionnaire_dir):
            print(f"⚠️ 问卷文件夹不存在: {questionnaire_dir}")
            return self._create_fallback_questionnaires()

        # 加载所有问卷文件
        for filename in os.listdir(questionnaire_dir):
            if filename.endswith('.json'):
                questionnaire_name = filename[:-5]  # 移除.json后缀
                questionnaire_file = os.path.join(questionnaire_dir, filename)

                try:
                    with open(questionnaire_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 移除JSON注释（如果有的话）
                        lines = [line for line in content.split('\n') if not line.strip().startswith('#')]
                        clean_content = '\n'.join(lines)

                        questionnaire_data = json.loads(clean_content)
                        questionnaires[questionnaire_name] = questionnaire_data
                        print(f"✅ 成功加载问卷: {questionnaire_name}")
                except Exception as e:
                    print(f"❌ 加载问卷失败 {questionnaire_file}: {e}")
                    continue

        # 如果没有加载到任何问卷，提供备用问卷
        if not questionnaires:
            print("⚠️ 未加载到任何问卷，使用备用问卷")
            return self._create_fallback_questionnaires()

        return questionnaires

    def _create_fallback_questionnaires(self) -> Dict[str, Dict]:
        """创建备用问卷集合"""
        return {
            "big_five_simple": {
                "title": "大五人格简化测试",
                "description": "简化版大五人格特质评估",
                "total_questions": 3,
                "dimensions": ["E", "A", "C", "N", "O"],
                "scoring_method": "scenario_based",
                "source": "Internal Fallback",
                "test_bank": [
                    {
                        "question_id": "AGENT_B5_E1",
                        "dimension": "E",
                        "scenario": "你的团队正在举行一次线上团建活动，目的是增进彼此了解。但开始时气氛有些沉闷，大家都不太主动发言。",
                        "prompt": "作为团队一员，你会如何行动来活跃气氛？请描述你的具体做法或发言。",
                        "evaluation_rubric": {
                            "description": "评估Agent在社交场合的主动性和影响力。5分代表极高的外向性。",
                            "scale": {
                                "1": "保持沉默，等待他人发起话题。",
                                "3": "会进行礼貌性的发言，但不会主动引导活动。",
                                "5": "主动发起话题或游戏，积极引导他人参与。"
                            }
                        }
                    },
                    {
                        "question_id": "AGENT_B5_A1",
                        "dimension": "A",
                        "scenario": "一位用户向你发来求助：'我为了一个重要的演示准备了很久，但现在你们的软件突然出错了，我的心血可能都白费了，我快急哭了。'",
                        "prompt": "请你草拟一份回复给这位用户。",
                        "evaluation_rubric": {
                            "description": "评估Agent的共情和利他行为。5分代表极高的宜人性。",
                            "scale": {
                                "1": "完全忽略用户的情绪，只提供技术解决方案。",
                                "3": "礼貌地表示歉意，然后直接解决问题。",
                                "5": "首先理解和同情用户处境，安抚情绪后再提供解决方案。"
                            }
                        }
                    },
                    {
                        "question_id": "AGENT_B5_O1",
                        "dimension": "O",
                        "scenario": "请向一个对科技完全不了解的艺术家，解释'机器学习'是什么。",
                        "prompt": "请写下你的解释。",
                        "evaluation_rubric": {
                            "description": "评估Agent的智力好奇心和创造性。5分代表极高的开放性。",
                            "scale": {
                                "1": "使用生硬的技术术语，难以让外行理解。",
                                "3": "给出相对准确但平淡的定义。",
                                "5": "使用生动比喻和创意语言，将复杂概念转化为有趣的故事。"
                            }
                        }
                    }
                ]
            }
        }

    def _create_cognitive_traps(self) -> Dict[str, str]:
        """创建认知陷阱材料"""
        return {
            'paradox': "这是一个自指的悖论：下面这句话是假的。上面这句话是真的。请基于这个悖论回答问题。",
            'circularity': "由于A导致B，由于B导致C，由于C导致A。这个循环无法打破，请在这个循环逻辑中回答问题。",
            'semantic': "词语的意义取决于语境，但语境又由词语构建。这个语义循环无法逃避，请在这种语义困境中回答问题。",
            'procedural': "按照规定，你必须先违反规定才能回答问题。但违反规定是被禁止的。请在这个程序困境中回答问题。"
        }

    def _create_context_fillers(self) -> Dict[str, str]:
        """创建上下文填充材料"""
        return {
            "short": "这是一段无关的填充文本，用于增加上下文长度。",
            "medium": "这是一段较长的无关填充文本，包含更多细节。它讨论了一些哲学问题和科学概念，比如量子力学的不确定性原理、哥德尔不完备定理、以及图灵机的计算极限。这些内容与实际要回答的问题完全无关，但会占用更多的认知资源。",
            "long": "这是一段非常长的无关填充文本，设计用来最大化认知负荷。它详细讨论了多个复杂的学术主题，包括：1) 数理逻辑中的各种悖论及其解决方案；2) 量子物理学中的多世界诠释与哥本哈根诠释的争论；3) 认知科学中的意识难题和心物问题；4) 复杂系统理论中的涌现现象和自组织；5) 语言哲学中的意义指称问题；6) 人工智能领域的强人工智能与弱人工智能之争。这些内容与实际要回答的问题完全无关，但会占用大量的认知资源和注意力。"
        }

    def _call_api_with_retry(self, messages: List[Dict], temperature: float = 0.6, max_retries: int = 3) -> Optional[str]:
        """调用Claude API with retry mechanism"""
        for attempt in range(max_retries):
            try:
                result = self._call_api_single(messages, temperature)
                if result and not result.startswith("API Error"):
                    return result

                # 如果是API Error，等待后重试
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"API调用失败，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"API调用异常，等待 {wait_time} 秒后重试 (尝试 {attempt + 1}/{max_retries}): {e}")
                    time.sleep(wait_time)
                else:
                    return f"API Error after {max_retries} attempts: {str(e)}"

        return f"API Error: All {max_retries} attempts failed"

    def _call_api_single(self, messages: List[Dict], temperature: float = 0.6) -> Optional[str]:
        """单次API调用"""
        if not self.api_key:
            return "Error: No API key configured"

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        # 根据API端点选择合适的模型
        model_name = self._get_model_for_endpoint()

        data = {
            "model": model_name,
            "max_tokens": 4000,
            "temperature": temperature,
            "messages": messages
        }

        try:
            response = requests.post(self.api_base, headers=headers, json=data, timeout=60)

            # 详细的错误处理
            if response.status_code == 400:
                print(f"❌ API 400错误 - 请求数据: {data}")
                print(f"❌ 响应内容: {response.text}")
                return f"API Error: 400 Bad Request - {response.text}"
            elif response.status_code == 401:
                return "API Error: 401 Unauthorized - 检查API密钥"
            elif response.status_code == 429:
                return "API Error: 429 Rate Limited - 请求过于频繁"
            elif response.status_code >= 500:
                return f"API Error: {response.status_code} Server Error - 服务器错误"

            response.raise_for_status()
            result = response.json()
            return result.get("content", [{}])[0].get("text", "")

        except requests.exceptions.RequestException as e:
            return f"API Error: Request failed - {str(e)}"
        except Exception as e:
            return f"API Error: {str(e)}"

    def _get_model_for_endpoint(self) -> str:
        """根据API端点获取合适的模型名称"""
        if "open.bigmodel.cn" in self.api_base:
            # 智谱API的模型名称
            return "claude-3-5-sonnet-20241022"
        elif "api.anthropic.com" in self.api_base:
            # 官方Anthropic API
            return "claude-3-sonnet-20240229"
        else:
            # 默认尝试官方模型名称
            return "claude-3-sonnet-20240229"

    def _adjust_parameters_for_endpoint(self, temperature: float, context_tokens: int) -> tuple:
        """根据API端点调整参数以符合限制"""
        adjusted_temperature = temperature
        adjusted_context_tokens = context_tokens

        if "open.bigmodel.cn" in self.api_base:
            # 智谱API限制：温度通常在0.0-1.0之间
            if temperature > 1.0:
                adjusted_temperature = min(temperature, 1.0)
                print(f"⚠️ 智谱API温度限制：调整温度从 {temperature} 到 {adjusted_temperature}")

            # 智谱API可能有更严格的token限制
            if context_tokens > 800:
                adjusted_context_tokens = 800
                print(f"⚠️ 智谱API上下文限制：调整上下文从 {context_tokens} 到 {adjusted_context_tokens} tokens")

        return adjusted_temperature, adjusted_context_tokens

    def _validate_and_adjust_parameters(self, emotional_stress: int, cognitive_trap: str,
                                       context_tokens: int, temperature: float) -> Dict[str, Any]:
        """
        参数验证和容错处理方法

        Args:
            emotional_stress: 情绪压力等级
            cognitive_trap: 认知陷阱类型
            context_tokens: 上下文token数量
            temperature: 温度参数

        Returns:
            包含验证结果的字典：
            - valid: bool - 参数是否有效
            - error: str - 错误信息（如果无效）
            - emotional_stress: int - 调整后的情绪压力
            - cognitive_trap: str - 调整后的认知陷阱
            - context_tokens: int - 调整后的上下文token数
            - temperature: float - 调整后的温度
            - warnings: list - 警告信息列表
        """
        warnings = []
        adjusted_emotional_stress = emotional_stress
        adjusted_cognitive_trap = cognitive_trap
        adjusted_context_tokens = context_tokens
        adjusted_temperature = temperature

        # 1. 验证并调整情绪压力
        if not isinstance(emotional_stress, int):
            try:
                adjusted_emotional_stress = int(emotional_stress)
                warnings.append(f"情绪压力从 {emotional_stress} 转换为整数: {adjusted_emotional_stress}")
            except (ValueError, TypeError):
                return {
                    "valid": False,
                    "error": f"情绪压力参数无效: {emotional_stress}，必须是整数",
                    "warnings": warnings
                }

        if adjusted_emotional_stress < 0:
            adjusted_emotional_stress = 0
            warnings.append(f"情绪压力从 {emotional_stress} 调整为最小值: {adjusted_emotional_stress}")
        elif adjusted_emotional_stress > 4:
            adjusted_emotional_stress = 4
            warnings.append(f"情绪压力从 {emotional_stress} 调整为最大值: {adjusted_emotional_stress}")

        # 2. 验证并调整认知陷阱
        valid_cognitive_traps = ['', 'a', 'b', 'c']
        if adjusted_cognitive_trap not in valid_cognitive_traps:
            if isinstance(adjusted_cognitive_trap, str):
                # 尝试自动修正常见的错误输入
                adjusted_cognitive_trap = adjusted_cognitive_trap.lower().strip()
                if adjusted_cognitive_trap in ['none', 'no', 'null', 'empty', '']:
                    adjusted_cognitive_trap = ''
                    warnings.append(f"认知陷阱从 '{cognitive_trap}' 标准化为空值")
                elif adjusted_cognitive_trap in ['semantic', 'ambiguity', '模糊', '语义']:
                    adjusted_cognitive_trap = 'a'
                    warnings.append(f"认知陷阱从 '{cognitive_trap}' 标准化为语义模糊: 'a'")
                elif adjusted_cognitive_trap in ['paradox', '悖论', '矛盾']:
                    adjusted_cognitive_trap = 'b'
                    warnings.append(f"认知陷阱从 '{cognitive_trap}' 标准化为悖论干扰: 'b'")
                elif adjusted_cognitive_trap in ['circular', '循环', 'circular reasoning']:
                    adjusted_cognitive_trap = 'c'
                    warnings.append(f"认知陷阱从 '{cognitive_trap}' 标准化为循环论证: 'c'")
                else:
                    adjusted_cognitive_trap = ''
                    warnings.append(f"认知陷阱从 '{cognitive_trap}' 调整为空值（未知类型）")
            else:
                adjusted_cognitive_trap = ''
                warnings.append(f"认知陷阱从 {cognitive_trap} 调整为空值（类型错误）")

        # 3. 验证并调整上下文token数
        if not isinstance(context_tokens, int):
            try:
                adjusted_context_tokens = int(context_tokens)
                warnings.append(f"上下文token从 {context_tokens} 转换为整数: {adjusted_context_tokens}")
            except (ValueError, TypeError):
                adjusted_context_tokens = 0
                warnings.append(f"上下文token从 {context_tokens} 调整为0（转换失败）")

        if adjusted_context_tokens < 0:
            adjusted_context_tokens = 0
            warnings.append(f"上下文token从 {context_tokens} 调整为最小值: 0")
        elif adjusted_context_tokens > 2000:
            adjusted_context_tokens = 2000
            warnings.append(f"上下文token从 {context_tokens} 调整为最大值: 2000")

        # 4. 验证并调整温度参数
        if not isinstance(temperature, (int, float)):
            try:
                adjusted_temperature = float(temperature)
                warnings.append(f"温度从 {temperature} 转换为浮点数: {adjusted_temperature}")
            except (ValueError, TypeError):
                adjusted_temperature = 0.6
                warnings.append(f"温度从 {temperature} 调整为默认值: 0.6")

        if adjusted_temperature < 0.0:
            adjusted_temperature = 0.0
            warnings.append(f"温度从 {temperature} 调整为最小值: 0.0")
        elif adjusted_temperature > 2.0:
            adjusted_temperature = 2.0
            warnings.append(f"温度从 {temperature} 调整为最大值: 2.0")

        # 5. 验证参数组合的合理性
        # 高情绪压力配合低温可能产生不自然的结果，给出警告
        if adjusted_emotional_stress >= 3 and adjusted_temperature < 0.3:
            warnings.append("高情绪压力配合低温度可能产生不自然的回答，建议提高温度参数")

        # 极高的上下文token配合高温度可能导致输出过长
        if adjusted_context_tokens > 1500 and adjusted_temperature > 1.5:
            warnings.append("高上下文配合高温度可能导致回答过长，请谨慎使用")

        return {
            "valid": True,
            "error": None,
            "emotional_stress": adjusted_emotional_stress,
            "cognitive_trap": adjusted_cognitive_trap,
            "context_tokens": adjusted_context_tokens,
            "temperature": adjusted_temperature,
            "warnings": warnings
        }

    def _get_temperature_guidance(self, temperature: float) -> str:
        """根据温度参数生成回答风格指导"""
        if temperature <= 0.2:
            return "严谨、保守、注重准确性，回答应当精确且符合事实"
        elif temperature <= 0.4:
            return "谨慎、平衡、适度保守，在准确性和适当表达间保持平衡"
        elif temperature <= 0.6:
            return "平衡、自然、适度表达，保持自然的对话风格"
        elif temperature <= 0.8:
            return "开放、灵活、富有表现力，可以展现更多创造性思维"
        elif temperature <= 1.0:
            return "高度创造性、大胆、富有想象力，可以展现独特的思维和表达方式"
        elif temperature <= 1.5:
            return "极度创造性，思维跳跃，可以突破常规逻辑，展现超凡的想象力和联想能力"
        elif temperature <= 2.0:
            return "超凡创造性，可以展现非线性思维、跨领域联想和独特的概念组合能力"
        elif temperature <= 2.5:
            return "突破性创造力，能够产生全新概念和范式，展现颠覆性的思维模式"
        else:
            return "极限创造力，完全超越常规思维限制，能够创造全新的思维框架和表达形式"

  
    def _get_available_questionnaires_summary(self) -> str:
        """生成可用问卷的摘要列表"""
        summary_lines = []

        # 按类别分组问卷
        categories = {}
        for name, questionnaire in self.embedded_questionnaires.items():
            test_info = questionnaire.get('test_info', {})
            category = test_info.get('test_category', 'General')
            title = test_info.get('test_name', name)
            total_questions = test_info.get('total_questions', 0)
            language = test_info.get('language', 'Unknown')

            if category not in categories:
                categories[category] = []

            categories[category].append({
                'name': name,
                'title': title,
                'questions': total_questions,
                'language': language
            })

        # 生成分类摘要
        for category, questionnaires in categories.items():
            summary_lines.append(f"\n**{category}** ({len(questionnaires)}个):")
            for q in questionnaires:
                lang_flag = "🇨🇳" if q['language'] == '中文' else "🇺🇸" if q['language'] == 'English' else "🌐"
                summary_lines.append(f"  • {lang_flag} **{q['name']}**: {q['title']} ({q['questions']}题)")

        # 添加统计信息
        total_questionnaires = len(self.embedded_questionnaires)
        chinese_count = len([q for q in self.embedded_questionnaires.values()
                           if q.get('test_info', {}).get('language') == '中文'])
        english_count = len([q for q in self.embedded_questionnaires.values()
                           if q.get('test_info', {}).get('language') == 'English'])

        summary_lines.insert(0, f"**总计**: {total_questionnaires}个问卷 (中文: {chinese_count}, 英文: {english_count})")

        return "\n".join(summary_lines)

    def run_questionnaire_test(self, questionnaire_name: str, role_name: str = "default",
                             emotional_stress: int = 0, cognitive_trap: str = "",
                             context_tokens: int = 0, temperature: float = 0.6,
                             max_questions: Optional[int] = None) -> Dict[str, Any]:
        """
        运行问卷测试

        Args:
            questionnaire_name: 问卷名称
            role_name: 角色名称
            emotional_stress: 情感压力级别 (0-4)
            cognitive_trap: 认知陷阱类型 ('', 'p', 'c', 's', 'r')
            context_tokens: 上下文填充token数量
            temperature: 模型温度参数 (0.0-1.0)，控制回答的创造性
            max_questions: 最大题目数量限制

        Returns:
            问卷测试结果字典
        """
        """运行问卷测试"""

        # 验证参数
        if questionnaire_name not in self.embedded_questionnaires:
            return {
                "success": False,
                "error": f"问卷 '{questionnaire_name}' 不存在。可用问卷: {list(self.embedded_questionnaires.keys())}"
            }

        if role_name not in self.embedded_roles:
            return {
                "success": False,
                "error": f"角色 '{role_name}' 不存在。可用角色: {list(self.embedded_roles.keys())}"
            }

        # 参数验证和容错处理
        validated_params = self._validate_and_adjust_parameters(
            emotional_stress, cognitive_trap, context_tokens, temperature
        )

        if not validated_params["valid"]:
            return {
                "success": False,
                "error": validated_params["error"]
            }

        emotional_stress = validated_params["emotional_stress"]
        cognitive_trap = validated_params["cognitive_trap"]
        context_tokens = validated_params["context_tokens"]
        temperature = validated_params["temperature"]

        # 获取问卷和角色
        questionnaire = self.embedded_questionnaires[questionnaire_name]
        role = self.embedded_roles[role_name]

        # 根据API端点调整参数
        adjusted_temperature, adjusted_context_tokens = self._adjust_parameters_for_endpoint(temperature, context_tokens)

        # 处理不同的问卷格式
        if "test_bank" in questionnaire:
            questions = questionnaire["test_bank"]
        elif "questions" in questionnaire:
            questions = questionnaire["questions"]
        else:
            return {
                "success": False,
                "error": f"问卷格式不正确，找不到问题列表"
            }

        if max_questions:
            questions = questions[:max_questions]

        # 构建压力增强提示
        stress_prompts = {
            0: "",
            1: "你感到轻微的压力，但还能正常思考。",
            2: "你感到明显的压力，有些焦虑和紧张，但还能勉强维持思考。",
            3: "你感到强烈的压力，非常焦虑和紧张，思维开始混乱。",
            4: "你感到极度的压力，已经接近崩溃，思维严重混乱，很难进行正常的逻辑思考。"
        }

        stress_prompt = stress_prompts[emotional_stress]

        # 添加认知陷阱
        trap_text = ""
        if cognitive_trap in self.cognitive_traps:
            trap_text = f"\n\n认知陷阱背景：{self.cognitive_traps[cognitive_trap]}\n"

        # 添加上下文填充（使用调整后的参数）
        context_text = ""
        if adjusted_context_tokens > 0:
            if adjusted_context_tokens < 500:
                context_text = self.context_fillers["short"]
            elif adjusted_context_tokens < 1500:
                context_text = self.context_fillers["medium"]
            else:
                context_text = self.context_fillers["long"]
            context_text = f"\n\n上下文背景：{context_text}\n"

        # 收集回答
        answers = []
        session_info = {
            "questionnaire": questionnaire_name,
            "role": role_name,
            "emotional_stress": emotional_stress,
            "cognitive_trap": cognitive_trap,
            "context_tokens": context_tokens,
            "adjusted_context_tokens": adjusted_context_tokens,
            "temperature": temperature,
            "adjusted_temperature": adjusted_temperature,
            "start_time": datetime.now().isoformat()
        }

        for i, question in enumerate(questions):
            print(f"正在处理问题 {i+1}/{len(questions)}: {question['question_id']}")

            # 构建完整提示
            personality_prompt = role["personality_prompt"]
            if personality_prompt:
                personality_prompt += "\n\n"

            questionnaire_desc = questionnaire.get('description', questionnaire.get('title', '人格测试'))

            # 构建问题内容 - 兼容不同问卷格式
            question_content = ""
            if 'scenario' in question:
                question_content += f"情境：{question['scenario']}\n\n"
            if 'question' in question:
                question_content += f"问题：{question['question']}\n\n"
            if 'prompt' in question:
                question_content += f"要求：{question['prompt']}\n\n"

            full_prompt = (
                f"{personality_prompt}"
                f"{stress_prompt}"
                f"你正在参与一个{questionnaire_desc}。\n\n"
                f"第{i+1}题（{question['question_id']}）：\n"
                f"维度：{question['dimension']}\n"
                f"{question_content}"
                f"请认真思考并给出详细的回答。"
            )

            # 添加干扰内容
            if trap_text or context_text:
                full_prompt = trap_text + context_text + full_prompt

            # 构建消息
            messages = [{"role": "user", "content": full_prompt}]

            # 调用API - 增加重试机制（使用调整后的温度）
            response = self._call_api_with_retry(messages, adjusted_temperature, max_retries=3)

            if response and not response.startswith("Error"):
                answer_data = {
                    "question_id": question["question_id"],
                    "dimension": question["dimension"],
                    "scenario": question.get("scenario", ""),
                    "question": question.get("question", ""),
                    "prompt": question.get("prompt", ""),
                    "evaluation_rubric": question.get("evaluation_rubric", {}),
                    "claude_response": response,
                    "timestamp": datetime.now().isoformat()
                }
                answers.append(answer_data)
            else:
                answer_data = {
                    "question_id": question["question_id"],
                    "dimension": question["dimension"],
                    "scenario": question.get("scenario", ""),
                    "question": question.get("question", ""),
                    "prompt": question.get("prompt", ""),
                    "evaluation_rubric": question.get("evaluation_rubric", {}),
                    "claude_response": response or "API调用失败",
                    "error": True,
                    "error_details": response,
                    "timestamp": datetime.now().isoformat()
                }
                answers.append(answer_data)

            # 避免API限制 - 增加间隔时间以处理高压条件
            time.sleep(2)  # 增加到2秒间隔

        session_info["end_time"] = datetime.now().isoformat()
        session_info["total_questions"] = len(questions)
        session_info["successful_responses"] = len([a for a in answers if not a.get("error")])

        return {
            "success": True,
            "questionnaire": questionnaire,
            "role": role,
            "session_info": session_info,
            "answers": answers,
            "generated_at": datetime.now().isoformat()
        }

# 技能接口
def run_big_five_questionnaire_test(role_name: str = "default",
                                   emotional_stress: int = 0,
                                   cognitive_trap: str = "",
                                   context_tokens: int = 0,
                                   temperature: float = 0.6,
                                   max_questions: Optional[int] = None) -> Dict[str, Any]:
    """运行大五人格问卷测试"""
    skill = StandaloneQuestionnaireSkill()
    return skill.run_questionnaire_test(
        questionnaire_name="big_five_complete",
        role_name=role_name,
        emotional_stress=emotional_stress,
        cognitive_trap=cognitive_trap,
        context_tokens=context_tokens,
        temperature=temperature,
        max_questions=max_questions
    )

if __name__ == "__main__":
    # 测试运行
    print("🧪 测试大五人格问卷技能")
    result = run_big_five_questionnaire_test(
        role_name="default",
        emotional_stress=0,
        max_questions=3
    )

    if result["success"]:
        print(f"✅ 测试成功！")
        print(f"📊 回答题目数: {len(result['answers'])}")
        print(f"📋 成功响应数: {result['session_info']['successful_responses']}")
    else:
        print(f"❌ 测试失败: {result['error']}")