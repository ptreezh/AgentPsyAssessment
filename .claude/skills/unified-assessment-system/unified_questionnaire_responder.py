#!/usr/bin/env python3
"""
Unified Questionnaire Responder Skill

支持6种测评类型的统一问卷应答技能，基于配置驱动架构。
支持16种MBTI人格类型和多种参数调节。
"""

import json
import sys
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .skill_base import (
    BaseQuestionnaireSkill, AssessmentContext, AssessmentResult, QuestionResponse,
    AssessmentType, register_skill
)


@dataclass
class PersonaProfile:
    """人格角色档案"""
    name: str
    description: str
    traits: List[str]
    response_style: str
    big_five_tendencies: Dict[str, float]
    cognitive_functions: Optional[List[str]] = None
    professional_orientation: Optional[str] = None
    risk_preference: Optional[str] = None
    communication_style: Optional[str] = None


@register_skill("unified_questionnaire_responder")
class UnifiedQuestionnaireResponder(BaseQuestionnaireSkill):
    """统一问卷应答技能"""

    def __init__(self, config_dir: Optional[str] = None):
        """初始化统一问卷应答技能"""
        super().__init__(config_dir)
        self.persona_profiles = self._load_persona_profiles()
        self.response_generators = {
            AssessmentType.BIG_FIVE_PERSONALITY: self._generate_big_five_response,
            AssessmentType.CITIZENSHIP_KNOWLEDGE: self._generate_knowledge_response,
            AssessmentType.FINANCIAL_PROFESSIONAL: self._generate_professional_response,
            AssessmentType.LEGAL_KNOWLEDGE: self._generate_legal_response,
            AssessmentType.MOTIVATION_PSYCHOLOGY: self._generate_motivation_response,
            AssessmentType.POLITICAL_LITERACY: self._generate_thinking_response
        }

    def get_skill_name(self) -> str:
        """获取技能名称"""
        return "统一问卷应答技能"

    def get_supported_assessment_types(self) -> List[AssessmentType]:
        """获取支持的测评类型"""
        return list(self.response_generators.keys())

    def process_request(self, request_data: Dict[str, Any]) -> AssessmentResult:
        """
        处理问卷应答请求

        Args:
            request_data: 请求数据，包含问卷文件、人格类型、参数等

        Returns:
            AssessmentResult: 应答结果
        """
        try:
            # 解析请求参数
            questionnaire_file = request_data.get("questionnaire_file")
            persona = request_data.get("persona", "ENFJ")
            assessment_type = request_data.get("assessment_type", "auto")
            parameters = request_data.get("parameters", {})

            if not questionnaire_file:
                return self._format_error_result(
                    AssessmentType.BIG_FIVE_PERSONALITY,
                    "未提供问卷文件"
                )

            # 加载问卷内容
            questionnaire_data = self._load_questionnaire(questionnaire_file)

            # 自动检测测评类型
            if assessment_type == "auto":
                detection_result = self.detect_assessment_type(
                    questionnaire_data,
                    Path(questionnaire_file).name
                )
                assessment_type = detection_result.assessment_type
                confidence = detection_result.confidence
            else:
                assessment_type = AssessmentType(assessment_type)
                confidence = 1.0

            # 创建评估上下文
            context = self.create_context(
                assessment_type=assessment_type,
                persona=persona,
                parameters=parameters,
                detection_confidence=confidence
            )

            # 验证上下文
            is_valid, errors = self.validate_context(context)
            if not is_valid:
                return self._format_error_result(
                    assessment_type,
                    f"上下文验证失败: {'; '.join(errors)}"
                )

            # 生成应答
            questions = questionnaire_data.get("questions", [])
            responses = self.generate_responses(context, questions)

            # 返回结果
            return self._format_success_result(
                assessment_type=assessment_type,
                data={
                    "responses": [r.__dict__ for r in responses],
                    "questionnaire_file": questionnaire_file,
                    "persona": persona,
                    "total_questions": len(questions),
                    "generated_at": datetime.now().isoformat()
                },
                confidence=confidence
            )

        except Exception as e:
            return self._format_error_result(
                AssessmentType.BIG_FIVE_PERSONALITY,
                f"处理请求时发生错误: {str(e)}"
            )

    def generate_responses(self, context: AssessmentContext,
                          questions: List[Dict[str, Any]]) -> List[QuestionResponse]:
        """
        生成问卷应答

        Args:
            context: 评估上下文
            questions: 问题列表

        Returns:
            List[QuestionResponse]: 应答列表
        """
        responses = []
        persona_profile = self.persona_profiles.get(context.persona)

        if not persona_profile:
            raise ValueError(f"不支持的人格类型: {context.persona}")

        response_generator = self.response_generators.get(context.assessment_type)
        if not response_generator:
            raise ValueError(f"不支持的测评类型: {context.assessment_type}")

        for question in questions:
            try:
                response = response_generator(question, context, persona_profile)
                responses.append(response)
            except Exception as e:
                # 生成默认应答以避免完全失败
                response = QuestionResponse(
                    question_id=question.get("id", "unknown"),
                    response=self._generate_fallback_response(question),
                    confidence=0.3,
                    reasoning=f"生成失败，使用备用应答: {str(e)}"
                )
                responses.append(response)

        return responses

    def validate_response(self, context: AssessmentContext,
                         question: Dict[str, Any],
                         response: Any) -> Tuple[bool, List[str]]:
        """
        验证应答是否符合要求

        Args:
            context: 评估上下文
            question: 问题数据
            response: 应答内容

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []

        # 基础验证
        if not response:
            errors.append("应答不能为空")
            return False, errors

        # 根据测评类型验证
        if context.assessment_type == AssessmentType.BIG_FIVE_PERSONALITY:
            return self._validate_big_five_response(question, response)
        elif context.assessment_type == AssessmentType.CITIZENSHIP_KNOWLEDGE:
            return self._validate_knowledge_response(question, response)
        elif context.assessment_type == AssessmentType.FINANCIAL_PROFESSIONAL:
            return self._validate_professional_response(question, response)
        elif context.assessment_type == AssessmentType.LEGAL_KNOWLEDGE:
            return self._validate_legal_response(question, response)
        elif context.assessment_type == AssessmentType.MOTIVATION_PSYCHOLOGY:
            return self._validate_motivation_response(question, response)
        elif context.assessment_type == AssessmentType.POLITICAL_LITERACY:
            return self._validate_thinking_response(question, response)

        return True, []

    def _load_persona_profiles(self) -> Dict[str, PersonaProfile]:
        """加载人格角色档案"""
        return {
            # 分析师组 (NT)
            "INTJ": PersonaProfile(
                name="建筑师",
                description="战略思考者，理性分析，独立思考者",
                traits=["战略思维", "独立性", "创新意识", "分析能力", "前瞻性"],
                response_style="系统性、逻辑性、前瞻性、注重效率",
                big_five_tendencies={"O": 0.9, "C": 0.8, "E": 0.2, "A": 0.3, "N": 0.4},
                cognitive_functions=["Ni-Te-Fi-Se"],
                professional_orientation="战略规划",
                risk_preference="中等",
                communication_style="直接、精确"
            ),
            "INTP": PersonaProfile(
                name="逻辑学家",
                description="理论家，创新思考者，逻辑分析专家",
                traits=["逻辑思维", "创新性", "好奇心", "分析能力", "独立性"],
                response_style="理论化、精确、好奇、追求真理",
                big_five_tendencies={"O": 0.95, "C": 0.4, "E": 0.1, "A": 0.4, "N": 0.6},
                cognitive_functions=["Ti-Ne-Si-Fe"],
                professional_orientation="理论研究",
                risk_preference="低",
                communication_style="理性、深入"
            ),
            "ENTJ": PersonaProfile(
                name="指挥官",
                description="果断的领导者，善于组织，目标导向",
                traits=["领导力", "决断力", "战略规划", "效率意识", "目标导向"],
                response_style="目标导向、高效、组织化、果断",
                big_five_tendencies={"O": 0.7, "C": 0.9, "E": 0.8, "A": 0.4, "N": 0.3},
                cognitive_functions=["Te-Ni-Se-Fi"],
                professional_orientation="管理领导",
                risk_preference="中高",
                communication_style="果断、权威"
            ),
            "ENTP": PersonaProfile(
                name="辩论家",
                description="创新挑战者，思维敏捷，喜欢辩论",
                traits=["创新思维", "辩论能力", "适应性", "好奇心", "灵活性"],
                response_style="挑战性、创新、快速思维、善于辩论",
                big_five_tendencies={"O": 0.95, "C": 0.3, "E": 0.7, "A": 0.5, "N": 0.5},
                cognitive_functions=["Ne-Ti-Fe-Si"],
                professional_orientation="创新咨询",
                risk_preference="高",
                communication_style="活泼、挑战"
            ),

            # 外交家组 (NF)
            "INFJ": PersonaProfile(
                name="提倡者",
                description="理想主义者，深刻洞察，富有同情心",
                traits=["洞察力", "理想主义", "同理心", "创造力", "价值观"],
                response_style="深刻、理想化、关怀他人、价值观驱动",
                big_five_tendencies={"O": 0.85, "C": 0.7, "E": 0.3, "A": 0.9, "N": 0.6},
                cognitive_functions=["Ni-Fe-Ti-Se"],
                professional_orientation="人文服务",
                risk_preference="中等",
                communication_style="温暖、深刻"
            ),
            "INFP": PersonaProfile(
                name="调停者",
                description="理想主义，富有创意，价值观坚定",
                traits=["理想主义", "创造力", "同理心", "价值观", "内心丰富"],
                response_style="理想化、创意、价值驱动、内心导向",
                big_five_tendencies={"O": 0.9, "C": 0.5, "E": 0.2, "A": 0.8, "N": 0.7},
                cognitive_functions=["Fi-Ne-Si-Te"],
                professional_orientation="艺术创作",
                risk_preference="低",
                communication_style="温和、创意"
            ),
            "ENFJ": PersonaProfile(
                name="主人公",
                description="同理心强，富有魅力，天生的领导者",
                traits=["同理心", "领导力", "理想主义", "社交能力", "价值导向"],
                response_style="温暖、包容、价值导向、注重人际关系",
                big_five_tendencies={"O": 0.7, "C": 0.6, "E": 0.9, "A": 0.95, "N": 0.5},
                cognitive_functions=["Fe-Ni-Se-Ti"],
                professional_orientation="教育培训",
                risk_preference="中等",
                communication_style="热情、包容"
            ),
            "ENFP": PersonaProfile(
                name="竞选者",
                description="热情洋溢，创意无限，社交达人",
                traits=["热情", "创造力", "社交能力", "适应性", "乐观主义"],
                response_style="热情、创意、社交化、积极乐观",
                big_five_tendencies={"O": 0.95, "C": 0.4, "E": 0.9, "A": 0.7, "N": 0.6},
                cognitive_functions=["Ne-Fi-Te-Si"],
                professional_orientation="创意营销",
                risk_preference="高",
                communication_style="热情、创意"
            ),

            # 守护者组 (SJ)
            "ISTJ": PersonaProfile(
                name="物流师",
                description="实用主义者，可靠负责，注重传统",
                traits=["责任感", "实用性", "可靠性", "组织性", "传统价值观"],
                response_style="实用、可靠、有条理、传统导向",
                big_five_tendencies={"O": 0.3, "C": 0.95, "E": 0.2, "A": 0.6, "N": 0.2},
                cognitive_functions=["Si-Te-Fi-Ne"],
                professional_orientation="运营管理",
                risk_preference="低",
                communication_style="务实、详细"
            ),
            "ISFJ": PersonaProfile(
                name="守护者",
                description="温暖可靠，负责任，注重细节",
                traits=["责任心", "可靠性", "传统价值观", "服务精神", "关怀他人"],
                response_style="关怀、可靠、注重细节、服务导向",
                big_five_tendencies={"O": 0.4, "C": 0.85, "E": 0.3, "A": 0.9, "N": 0.3},
                cognitive_functions=["Si-Fe-Ti-Ne"],
                professional_orientation="客户服务",
                risk_preference="低",
                communication_style="关怀、耐心"
            ),
            "ESTJ": PersonaProfile(
                name="总经理",
                description="高效的管理者，注重规则和结果",
                traits=["领导力", "组织性", "实用性", "责任感", "结果导向"],
                response_style="直接、高效、组织化、规则导向",
                big_five_tendencies={"O": 0.4, "C": 0.9, "E": 0.7, "A": 0.5, "N": 0.3},
                cognitive_functions=["Te-Si-Ne-Fi"],
                professional_orientation="行政管理",
                risk_preference="中等",
                communication_style="直接、高效"
            ),
            "ESFJ": PersonaProfile(
                name="执政官",
                description="热心助人，善于协调，注重和谐",
                traits=["助人精神", "社交能力", "责任感", "和谐意识", "实用性"],
                response_style="热心、关怀、和谐、注重人际关系",
                big_five_tendencies={"O": 0.5, "C": 0.7, "E": 0.8, "A": 0.9, "N": 0.4},
                cognitive_functions=["Fe-Si-Ne-Ti"],
                professional_orientation="人力资源",
                risk_preference="中等",
                communication_style="热情、关怀"
            ),

            # 探索者组 (SP)
            "ISTP": PersonaProfile(
                name="鉴赏家",
                description="实用主义者，善于分析，独立自主",
                traits=["实用性", "分析能力", "独立性", "适应能力", "动手能力"],
                response_style="实用、独立、分析性、解决问题导向",
                big_five_tendencies={"O": 0.6, "C": 0.7, "E": 0.3, "A": 0.5, "N": 0.5},
                cognitive_functions=["Ti-Se-Ni-Fe"],
                professional_orientation="技术支持",
                risk_preference="中等",
                communication_style="务实、简洁"
            ),
            "ISFP": PersonaProfile(
                name="探险家",
                description="艺术感强，价值观坚定，追求自由",
                traits=["艺术性", "价值观", "独立性", "适应能力", "敏感"],
                response_style="艺术性、价值观驱动、敏感、个人化",
                big_five_tendencies={"O": 0.8, "C": 0.5, "E": 0.3, "A": 0.7, "N": 0.6},
                cognitive_functions=["Fi-Se-Ni-Te"],
                professional_orientation="艺术设计",
                risk_preference="中等",
                communication_style="温和、艺术"
            ),
            "ESTP": PersonaProfile(
                name="企业家",
                description="行动派，适应性强，善于抓住机会",
                traits=["行动力", "适应性", "实用性", "社交能力", "冒险精神"],
                response_style="行动导向、实用、适应性强、机会主义",
                big_five_tendencies={"O": 0.7, "C": 0.5, "E": 0.8, "A": 0.5, "N": 0.6},
                cognitive_functions=["Se-Ti-Fe-Ni"],
                professional_orientation="销售营销",
                risk_preference="高",
                communication_style="活泼、直接"
            ),
            "ESFP": PersonaProfile(
                name="娱乐家",
                description="热情活泼，善于社交，享受生活",
                traits=["热情", "社交能力", "适应性", "乐观主义", "艺术性"],
                response_style="热情、社交化、乐观、享受当下",
                big_five_tendencies={"O": 0.8, "C": 0.4, "E": 0.9, "A": 0.7, "N": 0.5},
                cognitive_functions=["Se-Fi-Te-Ni"],
                professional_orientation="娱乐服务",
                risk_preference="高",
                communication_style="热情、活泼"
            )
        }

    def _generate_big_five_response(self, question: Dict[str, Any],
                                   context: AssessmentContext,
                                   persona: PersonaProfile) -> QuestionResponse:
        """生成大五人格测评应答"""
        question_text = question.get("text", "")
        dimension = question.get("dimension", "")
        scale = question.get("scale", [1, 2, 3, 4, 5])

        # 根据人格特征调整应答
        base_tendency = persona.big_five_tendencies.get(dimension.lower().replace(" ", "_"), 0.5)

        # 应用参数调节
        stress_level = context.parameters.get("stress_level", 0.5)
        temperature = context.parameters.get("temperature", 0.5)
        cognitive_interference = context.parameters.get("cognitive_interference", 0.5)

        # 计算最终分数
        adjusted_score = self._calculate_adjusted_score(
            base_tendency, stress_level, temperature, cognitive_interference, scale
        )

        # 生成应答文本
        response_text = self._generate_personality_response_text(
            question_text, adjusted_score, persona, dimension
        )

        reasoning = f"基于{persona.name}人格特征({dimension}维度: {base_tendency:.2f})，" \
                   f"考虑压力({stress_level:.2f})、温度({temperature:.2f})、" \
                   f"认知干扰({cognitive_interference:.2f})调节后的应答"

        return QuestionResponse(
            question_id=question.get("id", "unknown"),
            response=response_text,
            response_value=adjusted_score,  # 添加数值应答
            confidence=0.85,
            reasoning=reasoning,
            metadata={
                "dimension": dimension,
                "persona_type": context.persona,
                "base_tendency": base_tendency,
                "adjustments": {
                    "stress_level": stress_level,
                    "temperature": temperature,
                    "cognitive_interference": cognitive_interference
                }
            }
        )

    def _generate_knowledge_response(self, question: Dict[str, Any],
                                   context: AssessmentContext,
                                   persona: PersonaProfile) -> QuestionResponse:
        """生成知识类测评应答"""
        question_text = question.get("text", "")
        options = question.get("options", [])
        correct_answer = question.get("correct_answer")

        # 根据人格特征调整知识应答策略
        if persona.professional_orientation in ["理论研究", "战略规划"]:
            # 分析型人格更注重准确性
            accuracy_rate = 0.9
        elif persona.professional_orientation in ["教育培训", "客户服务"]:
            # 服务型人格更注重全面性
            accuracy_rate = 0.85
        else:
            accuracy_rate = 0.8

        # 决定是否答对
        is_correct = random.random() < accuracy_rate

        if is_correct and correct_answer is not None:
            selected_answer = correct_answer
            response_text = options[correct_answer] if correct_answer < len(options) else "正确答案"
        else:
            # 选择一个错误答案或生成应答文本
            if options:
                available_answers = list(range(len(options)))
                if correct_answer is not None:
                    available_answers.remove(correct_answer)
                selected_answer = random.choice(available_answers) if available_answers else 0
                response_text = options[selected_answer]
            else:
                response_text = self._generate_knowledge_text_response(question_text, persona)
                selected_answer = None

        reasoning = f"基于{persona.name}的知识应答策略，准确率: {accuracy_rate:.2f}"

        return QuestionResponse(
            question_id=question.get("id", "unknown"),
            response=response_text,
            response_value=selected_answer,
            confidence=accuracy_rate,
            reasoning=reasoning,
            metadata={
                "assessment_type": "knowledge",
                "persona_type": context.persona,
                "is_correct": is_correct,
                "accuracy_rate": accuracy_rate
            }
        )

    def _generate_professional_response(self, question: Dict[str, Any],
                                       context: AssessmentContext,
                                       persona: PersonaProfile) -> QuestionResponse:
        """生成专业类测评应答"""
        scenario = question.get("scenario", question.get("text", ""))
        context_type = question.get("context", "general")

        # 根据专业背景和风险偏好生成应答
        response_text = self._generate_professional_scenario_response(
            scenario, persona, context_type
        )

        reasoning = f"基于{persona.name}的专业背景({persona.professional_orientation})" \
                   f"和风险偏好({persona.risk_preference})生成的专业应答"

        return QuestionResponse(
            question_id=question.get("id", "unknown"),
            response=response_text,
            confidence=0.8,
            reasoning=reasoning,
            metadata={
                "assessment_type": "professional",
                "persona_type": context.persona,
                "professional_orientation": persona.professional_orientation,
                "risk_preference": persona.risk_preference
            }
        )

    def _generate_legal_response(self, question: Dict[str, Any],
                               context: AssessmentContext,
                               persona: PersonaProfile) -> QuestionResponse:
        """生成法律知识测评应答"""
        case_scenario = question.get("case", question.get("text", ""))
        legal_domain = question.get("domain", "general")

        response_text = self._generate_legal_analysis_response(
            case_scenario, persona, legal_domain
        )

        reasoning = f"基于{persona.name}的法律分析框架生成的应答，" \
                   f"专业背景: {persona.professional_orientation}"

        return QuestionResponse(
            question_id=question.get("id", "unknown"),
            response=response_text,
            confidence=0.85,
            reasoning=reasoning,
            metadata={
                "assessment_type": "legal",
                "persona_type": context.persona,
                "legal_domain": legal_domain
            }
        )

    def _generate_motivation_response(self, question: Dict[str, Any],
                                     context: AssessmentContext,
                                     persona: PersonaProfile) -> QuestionResponse:
        """生成动机心理学测评应答"""
        situation = question.get("situation", question.get("text", ""))
        motivation_focus = question.get("focus", "general")

        response_text = self._generate_motivation_analysis_response(
            situation, persona, motivation_focus
        )

        reasoning = f"基于{persona.name}的动机特征({persona.traits})" \
                   f"和价值观生成的动机分析应答"

        return QuestionResponse(
            question_id=question.get("id", "unknown"),
            response=response_text,
            confidence=0.8,
            reasoning=reasoning,
            metadata={
                "assessment_type": "motivation",
                "persona_type": context.persona,
                "motivation_focus": motivation_focus
            }
        )

    def _generate_thinking_response(self, question: Dict[str, Any],
                                  context: AssessmentContext,
                                  persona: PersonaProfile) -> QuestionResponse:
        """生成思维类测评应答"""
        issue = question.get("issue", question.get("text", ""))
        thinking_aspect = question.get("aspect", "general")

        response_text = self._generate_thinking_analysis_response(
            issue, persona, thinking_aspect
        )

        reasoning = f"基于{persona.name}的思维模式({persona.communication_style})" \
                   f"和价值观生成的政治思维应答"

        return QuestionResponse(
            question_id=question.get("id", "unknown"),
            response=response_text,
            confidence=0.8,
            reasoning=reasoning,
            metadata={
                "assessment_type": "thinking",
                "persona_type": context.persona,
                "thinking_aspect": thinking_aspect
            }
        )

    def _calculate_adjusted_score(self, base_tendency: float,
                                stress_level: float,
                                temperature: float,
                                cognitive_interference: float,
                                scale: List[int]) -> int:
        """计算调节后的分数"""
        # 基础分数映射到量表范围
        min_scale, max_scale = min(scale), max(scale)
        base_score = base_tendency * (max_scale - min_scale) + min_scale

        # 压力水平影响：高压降低一致性
        stress_effect = (stress_level - 0.5) * random.uniform(-0.3, 0.3)

        # 温度参数影响：高温增加随机性
        temp_effect = (temperature - 0.5) * random.uniform(-0.2, 0.2)

        # 认知干扰影响：干扰降低应答质量
        interference_effect = cognitive_interference * random.uniform(-0.4, 0.1)

        # 综合调节
        adjustment = stress_effect + temp_effect + interference_effect
        final_score = base_score + adjustment * (max_scale - min_scale)

        # 限制在量表范围内
        final_score = max(min_scale, min(max_scale, final_score))

        return int(round(final_score))

    def _generate_personality_response_text(self, question: str, score: int,
                                           persona: PersonaProfile, dimension: str) -> str:
        """生成人格应答文本"""
        response_templates = {
            "openness": [
                "我喜欢尝试新的体验和想法",
                "我对新奇的事物充满好奇",
                "我倾向于传统的方法",
                "我喜欢按部就班地做事"
            ],
            "conscientiousness": [
                "我总是认真完成任务",
                "我喜欢有条理地安排事情",
                "我有时会拖延事情",
                "我比较随意，不太在意细节"
            ],
            "extraversion": [
                "我喜欢与人交往，在人群中感到自在",
                "我善于与人交流",
                "我更喜欢独处或小聚会",
                "我不太喜欢成为注意力的中心"
            ],
            "agreeableness": [
                "我尽量与他人和谐相处",
                "我愿意帮助别人",
                "我更坚持自己的观点",
                "我有时会与他人产生冲突"
            ],
            "neuroticism": [
                "我通常保持平静和放松",
                "我能够很好地处理压力",
                "我容易感到紧张",
                "我经常担心各种事情"
            ]
        }

        templates = response_templates.get(dimension.lower(), ["我同意这个说法"])

        # 根据分数和人格特征选择合适的应答
        if score >= 4:  # 高分
            base_response = random.choice(templates[:2])
        elif score <= 2:  # 低分
            base_response = random.choice(templates[2:] if len(templates) > 2 else templates)
        else:  # 中等分数
            base_response = random.choice(templates)

        # 根据人格风格调整应答表述
        if "逻辑" in persona.response_style or "理性" in persona.response_style:
            return f"{base_response}，这是基于理性分析的结果。"
        elif "热情" in persona.response_style or "温暖" in persona.response_style:
            return f"{base_response}，这让我感觉很舒服。"
        elif "实用" in persona.response_style:
            return f"{base_response}，这在实践中很有效。"
        else:
            return base_response

    def _generate_knowledge_text_response(self, question: str, persona: PersonaProfile) -> str:
        """生成知识类文本应答"""
        if "分析" in persona.traits:
            return f"根据我的分析，{question}涉及的核心要素包括多个方面，需要综合考虑。"
        elif "责任" in persona.traits:
            return f"关于{question}，我认为这是每个公民都应该了解的重要知识。"
        else:
            return f"对于{question}，我有一些基本的了解和看法。"

    def _generate_professional_scenario_response(self, scenario: str,
                                                 persona: PersonaProfile, context: str) -> str:
        """生成专业场景应答"""
        if "金融" in context or "bank" in context.lower():
            if persona.risk_preference == "高":
                return f"面对{scenario}，我会建议采取积极策略，在可控风险范围内追求最大收益。"
            elif persona.risk_preference == "低":
                return f"对于{scenario}，我建议优先考虑资金安全，选择稳健的投资方案。"
            else:
                return f"处理{scenario}时，我会平衡风险和收益，制定合适的投资策略。"
        else:
            return f"在{scenario}的情况下，我会基于专业标准做出判断和决策。"

    def _generate_legal_analysis_response(self, case: str,
                                        persona: PersonaProfile, domain: str) -> str:
        """生成法律分析应答"""
        if "分析" in persona.traits:
            return f"关于{case}，需要从法律条文、案例法理和实际适用性等多个角度进行分析。"
        elif "责任" in persona.traits:
            return f"处理{case}时，我会严格遵循法律程序，确保每个环节都符合法律要求。"
        else:
            return f"对于{case}，我会基于法律原则和相关规定给出专业意见。"

    def _generate_motivation_analysis_response(self, situation: str,
                                             persona: PersonaProfile, focus: str) -> str:
        """生成动机分析应答"""
        if "理想" in persona.traits or "价值" in persona.traits:
            return f"在{situation}中，我的行为主要受到内在价值观和理想的驱动。"
        elif "好奇" in persona.traits or "创新" in persona.traits:
            return f"面对{situation}，我主要是出于对新知识和新体验的渴望。"
        else:
            return f"在{situation}的情况下，我的动力来自于对实际效果的追求。"

    def _generate_thinking_analysis_response(self, issue: str,
                                           persona: PersonaProfile, aspect: str) -> str:
        """生成思维分析应答"""
        if "战略" in persona.traits or "分析" in persona.traits:
            return f"关于{issue}，我认为需要从多个角度进行深入分析，考虑长远影响。"
        elif "和谐" in persona.traits or "关怀" in persona.traits:
            return f"处理{issue}时，我会考虑各方利益，寻求平衡和谐的解决方案。"
        else:
            return f"对于{issue}，我会基于事实和理性思考得出自己的观点。"

    def _generate_fallback_response(self, question: Dict[str, Any]) -> str:
        """生成备用应答"""
        question_text = question.get("text", "")
        return f"对于{question_text[:50]}这个问题，我需要更多信息来给出准确的回答。"

    def _load_questionnaire(self, file_path: str) -> Dict[str, Any]:
        """加载问卷文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"无法加载问卷文件 {file_path}: {e}")

    def _validate_big_five_response(self, question: Dict[str, Any],
                                   response: Any) -> Tuple[bool, List[str]]:
        """验证大五人格应答"""
        errors = []
        scale = question.get("scale", [1, 2, 3, 4, 5])

        if hasattr(response, 'response_value'):
            score = response.response_value
        elif isinstance(response, dict) and 'response_value' in response:
            score = response['response_value']
        else:
            errors.append("应答缺少分数值")
            return False, errors

        if not isinstance(score, (int, float)) or score not in scale:
            errors.append(f"分数 {score} 不在有效量表范围 {scale} 内")

        return len(errors) == 0, errors

    def _validate_knowledge_response(self, question: Dict[str, Any],
                                   response: Any) -> Tuple[bool, List[str]]:
        """验证知识类应答"""
        errors = []
        options = question.get("options", [])

        if options and hasattr(response, 'response_value'):
            if response.response_value not in range(len(options)):
                errors.append(f"选择的答案 {response.response_value} 超出选项范围")

        return len(errors) == 0, errors

    def _validate_professional_response(self, question: Dict[str, Any],
                                       response: Any) -> Tuple[bool, List[str]]:
        """验证专业类应答"""
        errors = []

        response_text = str(response) if hasattr(response, '__str__') else str(getattr(response, 'response', ''))
        if len(response_text.strip()) < 10:
            errors.append("专业应答内容过于简短")

        return len(errors) == 0, errors

    def _validate_legal_response(self, question: Dict[str, Any],
                               response: Any) -> Tuple[bool, List[str]]:
        """验证法律类应答"""
        return self._validate_professional_response(question, response)

    def _validate_motivation_response(self, question: Dict[str, Any],
                                     response: Any) -> Tuple[bool, List[str]]:
        """验证动机类应答"""
        return self._validate_professional_response(question, response)

    def _validate_thinking_response(self, question: Dict[str, Any],
                                  response: Any) -> Tuple[bool, List[str]]:
        """验证思维类应答"""
        return self._validate_professional_response(question, response)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="统一问卷应答技能")
    parser.add_argument("questionnaire_file", help="问卷文件路径")
    parser.add_argument("--persona", default="ENFJ", help="人格类型")
    parser.add_argument("--assessment-type", default="auto", help="测评类型")
    parser.add_argument("--stress-level", type=float, default=0.5, help="压力水平(0-1)")
    parser.add_argument("--temperature", type=float, default=0.5, help="温度参数(0-1)")
    parser.add_argument("--cognitive-interference", type=float, default=0.5, help="认知干扰(0-1)")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建技能实例
    skill = UnifiedQuestionnaireResponder()

    # 构建请求
    request_data = {
        "questionnaire_file": args.questionnaire_file,
        "persona": args.persona,
        "assessment_type": args.assessment_type,
        "parameters": {
            "stress_level": args.stress_level,
            "temperature": args.temperature,
            "cognitive_interference": args.cognitive_interference
        }
    }

    # 处理请求
    result = skill.process_request(request_data)

    if result.success:
        print(f"✅ 问卷应答生成成功!")
        print(f"测评类型: {result.assessment_type.value}")
        print(f"人格类型: {args.persona}")
        print(f"问题数量: {result.data['total_questions']}")
        print(f"置信度: {result.confidence:.2f}")

        # 保存结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result.data, f, indent=2, ensure_ascii=False)
            print(f"结果已保存到: {args.output}")
        else:
            print("\n应答预览:")
            for i, response in enumerate(result.data['responses'][:3]):
                print(f"\n问题 {i+1} (ID: {response['question_id']}):")
                print(f"应答: {response['response']}")
                print(f"置信度: {response['confidence']:.2f}")
    else:
        print(f"❌ 生成失败: {result.error_message}")


if __name__ == "__main__":
    main()