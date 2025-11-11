#!/usr/bin/env python3
"""
Unified Psychological Analyzer Skill

支持6种测评类型的统一评估分析技能，提供专业的评分、分析和建议。
基于配置驱动的评分算法和会话管理系统。
"""

import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

from .skill_base import (
    BaseAnalyzerSkill, AssessmentContext, AssessmentResult, EvaluationResult,
    AssessmentType, register_skill
)


@dataclass
class SessionData:
    """评估会话数据"""
    session_id: str
    context: AssessmentContext
    questions: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    evaluations: List[EvaluationResult]
    created_at: str
    updated_at: str
    total_questions: int
    completed_questions: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@register_skill("unified_psychological_analyzer")
class UnifiedPsychologicalAnalyzer(BaseAnalyzerSkill):
    """统一心理评估分析技能"""

    def __init__(self, config_dir: Optional[str] = None):
        """初始化统一心理评估分析技能"""
        super().__init__(config_dir)
        self.sessions: Dict[str, SessionData] = {}
        self.evaluation_algorithms = {
            AssessmentType.BIG_FIVE_PERSONALITY: self._evaluate_big_five,
            AssessmentType.CITIZENSHIP_KNOWLEDGE: self._evaluate_knowledge,
            AssessmentType.FINANCIAL_PROFESSIONAL: self._evaluate_professional,
            AssessmentType.LEGAL_KNOWLEDGE: self._evaluate_legal,
            AssessmentType.MOTIVATION_PSYCHOLOGY: self._evaluate_motivation,
            AssessmentType.POLITICAL_LITERACY: self._evaluate_thinking
        }

    def get_skill_name(self) -> str:
        """获取技能名称"""
        return "统一心理评估分析技能"

    def get_supported_assessment_types(self) -> List[AssessmentType]:
        """获取支持的测评类型"""
        return list(self.evaluation_algorithms.keys())

    def process_request(self, request_data: Dict[str, Any]) -> AssessmentResult:
        """
        处理评估分析请求

        Args:
            request_data: 请求数据

        Returns:
            AssessmentResult: 分析结果
        """
        try:
            action = request_data.get("action", "evaluate")

            if action == "start":
                return self._handle_start_session(request_data)
            elif action == "evaluate":
                return self._handle_evaluate_response(request_data)
            elif action == "complete":
                return self._handle_complete_evaluation(request_data)
            else:
                return self._format_error_result(
                    AssessmentType.BIG_FIVE_PERSONALITY,
                    f"不支持的操作: {action}"
                )

        except Exception as e:
            return self._format_error_result(
                AssessmentType.BIG_FIVE_PERSONALITY,
                f"处理请求时发生错误: {str(e)}"
            )

    def start_evaluation_session(self, context: AssessmentContext,
                               total_questions: int) -> str:
        """
        开始评估会话

        Args:
            context: 评估上下文
            total_questions: 总题目数量

        Returns:
            str: 会话ID
        """
        session_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()

        session_data = SessionData(
            session_id=session_id,
            context=context,
            questions=[],
            responses=[],
            evaluations=[],
            created_at=current_time,
            updated_at=current_time,
            total_questions=total_questions
        )

        self.sessions[session_id] = session_data
        self._sessions[session_id] = {
            "context": context.__dict__,
            "created_at": current_time,
            "data": {},
            "metadata": {"total_questions": total_questions}
        }

        return session_id

    def evaluate_response(self, session_id: str,
                         question: Dict[str, Any],
                         response: Any) -> EvaluationResult:
        """
        评估单个回答

        Args:
            session_id: 会话ID
            question: 问题数据
            response: 回答内容

        Returns:
            EvaluationResult: 评估结果
        """
        if session_id not in self.sessions:
            raise ValueError(f"会话不存在: {session_id}")

        session = self.sessions[session_id]
        context = session.context

        # 获取评估算法
        evaluator = self.evaluation_algorithms.get(context.assessment_type)
        if not evaluator:
            raise ValueError(f"不支持的测评类型: {context.assessment_type}")

        # 执行评估
        evaluation_result = evaluator(question, response, context)

        # 更新会话数据
        session.questions.append(question)
        session.responses.append({"response": response, "timestamp": datetime.now().isoformat()})
        session.evaluations.append(evaluation_result)
        session.completed_questions += 1
        session.updated_at = datetime.now().isoformat()

        # 更新基类会话
        self.update_session(session_id, {
            "completed_questions": session.completed_questions,
            "last_evaluation": evaluation_result.__dict__
        })

        return evaluation_result

    def complete_evaluation(self, session_id: str) -> AssessmentResult:
        """
        完成评估并生成最终结果

        Args:
            session_id: 会话ID

        Returns:
            AssessmentResult: 最终评估结果
        """
        if session_id not in self.sessions:
            raise ValueError(f"会话不存在: {session_id}")

        session = self.sessions[session_id]
        context = session.context

        # 生成综合分析结果
        comprehensive_result = self._generate_comprehensive_analysis(session)

        # 生成建议和报告
        recommendations = self._generate_recommendations(session)
        quality_metrics = self._calculate_quality_metrics(session)

        # 构建最终结果
        final_result_data = {
            "session_id": session_id,
            "assessment_type": context.assessment_type.value,
            "total_questions": session.total_questions,
            "completed_questions": session.completed_questions,
            "completion_rate": session.completed_questions / session.total_questions,
            "comprehensive_analysis": comprehensive_result,
            "recommendations": recommendations,
            "quality_metrics": quality_metrics,
            "detailed_evaluations": [eval_result.__dict__ for eval_result in session.evaluations],
            "evaluation_summary": self._generate_evaluation_summary(session),
            "completed_at": datetime.now().isoformat()
        }

        # 删除会话
        self.delete_session(session_id)

        return self._format_success_result(
            assessment_type=context.assessment_type,
            data=final_result_data,
            confidence=quality_metrics.get("overall_confidence", 0.8)
        )

    def _handle_start_session(self, request_data: Dict[str, Any]) -> AssessmentResult:
        """处理开始会话请求"""
        assessment_type = request_data.get("assessment_type", "big_five_personality")
        total_questions = request_data.get("total_questions", 50)
        parameters = request_data.get("parameters", {})

        # 创建上下文
        context = self.create_context(
            assessment_type=AssessmentType(assessment_type),
            parameters=parameters
        )

        # 开始会话
        session_id = self.start_evaluation_session(context, total_questions)

        return self._format_success_result(
            assessment_type=context.assessment_type,
            data={
                "session_id": session_id,
                "total_questions": total_questions,
                "assessment_type": assessment_type,
                "started_at": datetime.now().isoformat()
            }
        )

    def _handle_evaluate_response(self, request_data: Dict[str, Any]) -> AssessmentResult:
        """处理评估回答请求"""
        session_id = request_data.get("session_id")
        question = request_data.get("question", {})
        response = request_data.get("response")

        if not session_id:
            return self._format_error_result(
                AssessmentType.BIG_FIVE_PERSONALITY,
                "缺少会话ID"
            )

        try:
            evaluation_result = self.evaluate_response(session_id, question, response)

            return self._format_success_result(
                assessment_type=self.sessions[session_id].context.assessment_type,
                data={
                    "session_id": session_id,
                    "evaluation": evaluation_result.__dict__,
                    "completed_questions": self.sessions[session_id].completed_questions,
                    "remaining_questions": self.sessions[session_id].total_questions - self.sessions[session_id].completed_questions
                }
            )
        except Exception as e:
            return self._format_error_result(
                AssessmentType.BIG_FIVE_PERSONALITY,
                f"评估回答时发生错误: {str(e)}"
            )

    def _handle_complete_evaluation(self, request_data: Dict[str, Any]) -> AssessmentResult:
        """处理完成评估请求"""
        session_id = request_data.get("session_id")

        if not session_id:
            return self._format_error_result(
                AssessmentType.BIG_FIVE_PERSONALITY,
                "缺少会话ID"
            )

        return self.complete_evaluation(session_id)

    def _evaluate_big_five(self, question: Dict[str, Any], response: Any,
                          context: AssessmentContext) -> EvaluationResult:
        """评估大五人格回答"""
        dimension = question.get("dimension", "")
        scale = question.get("scale", [1, 2, 3, 4, 5])

        # 提取回答分数
        if hasattr(response, 'response_value'):
            score = response.response_value
        elif isinstance(response, dict) and 'response_value' in response:
            score = response['response_value']
        else:
            # 从文本回答中提取分数
            score = self._extract_score_from_text_response(str(response), scale)

        # 计算维度分数
        dimension_scores = {dimension: score}

        # 计算总分
        total_score = score

        # 计算置信度
        confidence = self._calculate_confidence(score, scale)

        # 生成反馈
        feedback = self._generate_big_five_feedback(dimension, score, scale)

        return EvaluationResult(
            question_id=question.get("id", "unknown"),
            score=total_score,
            dimension_scores=dimension_scores,
            feedback=feedback,
            confidence=confidence,
            metadata={
                "dimension": dimension,
                "scale": scale,
                "assessment_type": "big_five"
            }
        )

    def _evaluate_knowledge(self, question: Dict[str, Any], response: Any,
                           context: AssessmentContext) -> EvaluationResult:
        """评估知识类回答"""
        options = question.get("options", [])
        correct_answer = question.get("correct_answer")
        knowledge_domain = question.get("domain", "general")

        # 提取回答
        if hasattr(response, 'response_value'):
            selected_answer = response.response_value
        elif isinstance(response, dict) and 'response_value' in response:
            selected_answer = response['response_value']
        else:
            # 从文本回答中判断正确性
            selected_answer = self._extract_answer_from_text_response(
                str(response), options, correct_answer
            )

        # 计算分数
        score = 1.0 if selected_answer == correct_answer else 0.0

        # 维度分数
        dimension_scores = {
            "accuracy": score,
            "knowledge_domain": score
        }

        # 置信度
        confidence = 0.9 if options else 0.7

        # 反馈
        feedback = self._generate_knowledge_feedback(
            selected_answer, correct_answer, knowledge_domain
        )

        return EvaluationResult(
            question_id=question.get("id", "unknown"),
            score=score,
            dimension_scores=dimension_scores,
            feedback=feedback,
            confidence=confidence,
            metadata={
                "knowledge_domain": knowledge_domain,
                "correct_answer": correct_answer,
                "selected_answer": selected_answer,
                "assessment_type": "knowledge"
            }
        )

    def _evaluate_professional(self, question: Dict[str, Any], response: Any,
                             context: AssessmentContext) -> EvaluationResult:
        """评估专业类回答"""
        scenario = question.get("scenario", "")
        competency_area = question.get("competency_area", "general")
        evaluation_criteria = question.get("criteria", ["professionalism", "analysis", "risk_management"])

        # 分析回答文本
        response_text = str(response) if hasattr(response, '__str__') else str(getattr(response, 'response', response))

        # 评估各个方面
        scores = {}
        for criterion in evaluation_criteria:
            scores[criterion] = self._evaluate_professional_criterion(
                response_text, criterion, scenario
            )

        # 计算总分
        total_score = sum(scores.values()) / len(scores) if scores else 0.5

        # 置信度
        confidence = min(0.9, 0.5 + len(response_text) / 1000)

        # 反馈
        feedback = self._generate_professional_feedback(scores, competency_area)

        return EvaluationResult(
            question_id=question.get("id", "unknown"),
            score=total_score,
            dimension_scores=scores,
            feedback=feedback,
            confidence=confidence,
            metadata={
                "competency_area": competency_area,
                "evaluation_criteria": evaluation_criteria,
                "response_length": len(response_text),
                "assessment_type": "professional"
            }
        )

    def _evaluate_legal(self, question: Dict[str, Any], response: Any,
                       context: AssessmentContext) -> EvaluationResult:
        """评估法律类回答"""
        case = question.get("case", "")
        legal_domain = question.get("domain", "general")

        # 复用专业评估逻辑
        return self._evaluate_professional(question, response, context)

    def _evaluate_motivation(self, question: Dict[str, Any], response: Any,
                             context: AssessmentContext) -> EvaluationResult:
        """评估动机类回答"""
        situation = question.get("situation", "")
        motivation_focus = question.get("focus", "general")

        # 复用专业评估逻辑，使用特定的动机评估标准
        return self._evaluate_professional(question, response, context)

    def _evaluate_thinking(self, question: Dict[str, Any], response: Any,
                          context: AssessmentContext) -> EvaluationResult:
        """评估思维类回答"""
        issue = question.get("issue", "")
        thinking_aspect = question.get("aspect", "general")

        # 复用专业评估逻辑，使用特定的思维评估标准
        return self._evaluate_professional(question, response, context)

    def _extract_score_from_text_response(self, response_text: str, scale: List[int]) -> int:
        """从文本回答中提取分数"""
        response_text = response_text.lower()

        # 寻找数字
        import re
        numbers = re.findall(r'\d+', response_text)
        if numbers:
            score = int(numbers[0])
            if score in scale:
                return score

        # 基于关键词判断
        positive_words = ["同意", "非常", "总是", "经常", "喜欢", "是的"]
        negative_words = ["不同意", "很少", "从不", "不喜欢", "不是"]

        positive_count = sum(1 for word in positive_words if word in response_text)
        negative_count = sum(1 for word in negative_words if word in response_text)

        if positive_count > negative_count:
            return max(scale)
        elif negative_count > positive_count:
            return min(scale)
        else:
            return (min(scale) + max(scale)) // 2

    def _extract_answer_from_text_response(self, response_text: str, options: List[str],
                                          correct_answer: int) -> int:
        """从文本回答中提取选择的答案"""
        if not options or correct_answer is None:
            return 0

        response_text = response_text.lower()
        correct_text = options[correct_answer].lower()

        # 简单的关键词匹配
        if any(word in response_text for word in correct_text.split()[:3]):
            return correct_answer

        # 随机选择（在实际应用中应该使用更复杂的NLP）
        import random
        return random.randint(0, len(options) - 1)

    def _evaluate_professional_criterion(self, response_text: str, criterion: str,
                                        scenario: str) -> float:
        """评估专业标准"""
        criterion_keywords = {
            "professionalism": ["专业", "标准", "规范", "责任", "道德"],
            "analysis": ["分析", "考虑", "因素", "影响", "原因"],
            "risk_management": ["风险", "控制", "预防", "安全", "合规"],
            "communication": ["沟通", "表达", "清晰", "解释", "说明"],
            "problem_solving": ["解决", "方案", "建议", "方法", "策略"]
        }

        keywords = criterion_keywords.get(criterion, [])
        if not keywords:
            return 0.7  # 默认分数

        keyword_count = sum(1 for keyword in keywords if keyword in response_text)
        score = min(1.0, keyword_count / 3)  # 最多3个关键词就能得满分

        return score

    def _calculate_confidence(self, score: float, scale: List[int]) -> float:
        """计算置信度"""
        # 分数在量表中间位置时置信度较低
        min_score, max_score = min(scale), max(scale)
        mid_score = (min_score + max_score) / 2

        distance_from_middle = abs(score - mid_score)
        max_distance = max(abs(min_score - mid_score), abs(max_score - mid_score))

        # 距离中间越远，置信度越高
        confidence = 0.5 + (distance_from_middle / max_distance) * 0.4

        return round(confidence, 2)

    def _generate_big_five_feedback(self, dimension: str, score: int, scale: List[int]) -> str:
        """生成大五人格反馈"""
        min_score, max_score = min(scale), max(scale)
        mid_score = (min_score + max_score) / 2

        if score > mid_score:
            return f"在{dimension}维度上表现出较高水平，显示了该方面的积极特质。"
        elif score < mid_score:
            return f"在{dimension}维度上表现相对较低，这在某些情况下可能是优势。"
        else:
            return f"在{dimension}维度上表现适中，显示了平衡的特征。"

    def _generate_knowledge_feedback(self, selected_answer: int, correct_answer: int,
                                     domain: str) -> str:
        """生成知识类反馈"""
        if selected_answer == correct_answer:
            return f"回答正确！这显示了对{domain}领域知识的良好掌握。"
        else:
            return f"回答有误。建议加强对{domain}领域相关知识的学习。"

    def _generate_professional_feedback(self, scores: Dict[str, float], area: str) -> str:
        """生成专业类反馈"""
        avg_score = sum(scores.values()) / len(scores) if scores else 0

        if avg_score >= 0.8:
            return f"在{area}方面表现出色，展现了优秀的专业能力。"
        elif avg_score >= 0.6:
            return f"在{area}方面表现良好，有进一步提升的空间。"
        else:
            return f"在{area}方面需要加强学习和实践。"

    def _generate_comprehensive_analysis(self, session: SessionData) -> Dict[str, Any]:
        """生成综合分析结果"""
        if not session.evaluations:
            return {}

        context = session.context
        evaluations = session.evaluations

        if context.assessment_type == AssessmentType.BIG_FIVE_PERSONALITY:
            return self._analyze_big_five_comprehensive(evaluations)
        elif context.assessment_type == AssessmentType.CITIZENSHIP_KNOWLEDGE:
            return self._analyze_knowledge_comprehensive(evaluations)
        else:
            return self._analyze_professional_comprehensive(evaluations)

    def _analyze_big_five_comprehensive(self, evaluations: List[EvaluationResult]) -> Dict[str, Any]:
        """综合分析大五人格结果"""
        dimension_scores = {}

        for eval_result in evaluations:
            for dimension, score in eval_result.dimension_scores.items():
                if dimension not in dimension_scores:
                    dimension_scores[dimension] = []
                dimension_scores[dimension].append(score)

        # 计算平均分
        final_scores = {}
        for dimension, scores in dimension_scores.items():
            final_scores[dimension] = sum(scores) / len(scores)

        # 推断MBTI类型
        mbti_type = self._infer_mbti_type(final_scores)

        # 贝尔宾团队角色
        belbin_roles = self._map_belbin_roles(final_scores)

        return {
            "final_scores": final_scores,
            "mbti_inference": mbti_type,
            "belbin_roles": belbin_roles,
            "personality_summary": self._generate_personality_summary(final_scores)
        }

    def _analyze_knowledge_comprehensive(self, evaluations: List[EvaluationResult]) -> Dict[str, Any]:
        """综合分析知识测评结果"""
        total_score = sum(eval.score for eval in evaluations) / len(evaluations)
        domain_scores = {}

        for eval_result in evaluations:
            domain = eval_result.metadata.get("knowledge_domain", "general")
            if domain not in domain_scores:
                domain_scores[domain] = []
            domain_scores[domain].append(eval_result.score)

        # 计算各领域平均分
        final_domain_scores = {}
        for domain, scores in domain_scores.items():
            final_domain_scores[domain] = sum(scores) / len(scores)

        return {
            "total_score": total_score,
            "domain_scores": final_domain_scores,
            "knowledge_level": self._determine_knowledge_level(total_score),
            "improvement_areas": self._identify_improvement_areas(final_domain_scores)
        }

    def _analyze_professional_comprehensive(self, evaluations: List[EvaluationResult]) -> Dict[str, Any]:
        """综合分析专业测评结果"""
        competency_scores = {}

        for eval_result in evaluations:
            for competency, score in eval_result.dimension_scores.items():
                if competency not in competency_scores:
                    competency_scores[competency] = []
                competency_scores[competency].append(score)

        # 计算各胜任力平均分
        final_competency_scores = {}
        for competency, scores in competency_scores.items():
            final_competency_scores[competency] = sum(scores) / len(scores)

        # 总体专业水平
        overall_score = sum(final_competency_scores.values()) / len(final_competency_scores)

        return {
            "overall_score": overall_score,
            "competency_scores": final_competency_scores,
            "professional_level": self._determine_professional_level(overall_score),
            "strengths": self._identify_strengths(final_competency_scores),
            "development_areas": self._identify_development_areas(final_competency_scores)
        }

    def _infer_mbti_type(self, big_five_scores: Dict[str, float]) -> str:
        """基于大五分数推断MBTI类型"""
        # 简化的MBTI推断逻辑
        e_i = "E" if big_five_scores.get("extraversion", 0.5) > 0.5 else "I"
        s_n = "N" if big_five_scores.get("openness", 0.5) > 0.5 else "S"
        t_f = "F" if big_five_scores.get("agreeableness", 0.5) > 0.5 else "T"
        j_p = "J" if big_five_scores.get("conscientiousness", 0.5) > 0.5 else "P"

        return f"{e_i}{s_n}{t_f}{j_p}"

    def _map_belbin_roles(self, big_five_scores: Dict[str, float]) -> List[str]:
        """映射贝尔宾团队角色"""
        roles = []

        if big_five_scores.get("openness", 0) > 0.7:
            roles.append("智多星")
        if big_five_scores.get("conscientiousness", 0) > 0.7:
            roles.append("完成者")
        if big_five_scores.get("extraversion", 0) > 0.7:
            roles.append("协调者")
        if big_five_scores.get("agreeableness", 0) > 0.7:
            roles.append("凝聚者")

        return roles if roles else ["团队成员"]

    def _generate_personality_summary(self, scores: Dict[str, float]) -> str:
        """生成人格特质总结"""
        high_traits = [trait for trait, score in scores.items() if score > 0.6]
        low_traits = [trait for trait, score in scores.items() if score < 0.4]

        summary_parts = []
        if high_traits:
            summary_parts.append(f"在{', '.join(high_traits)}方面表现突出")
        if low_traits:
            summary_parts.append(f"在{', '.join(low_traits)}方面相对较低")

        return "；".join(summary_parts) if summary_parts else "各方面表现均衡"

    def _determine_knowledge_level(self, score: float) -> str:
        """确定知识水平"""
        if score >= 0.9:
            return "优秀"
        elif score >= 0.8:
            return "良好"
        elif score >= 0.7:
            return "合格"
        elif score >= 0.6:
            return "需要改进"
        else:
            return "不足"

    def _identify_improvement_areas(self, domain_scores: Dict[str, float]) -> List[str]:
        """识别需要改进的领域"""
        return [domain for domain, score in domain_scores.items() if score < 0.7]

    def _determine_professional_level(self, score: float) -> str:
        """确定专业水平"""
        if score >= 0.9:
            return "专家级"
        elif score >= 0.8:
            return "熟练级"
        elif score >= 0.7:
            return "胜任级"
        elif score >= 0.6:
            return "发展中"
        else:
            return "初级"

    def _identify_strengths(self, competency_scores: Dict[str, float]) -> List[str]:
        """识别优势领域"""
        return [comp for comp, score in competency_scores.items() if score > 0.8]

    def _identify_development_areas(self, competency_scores: Dict[str, float]) -> List[str]:
        """识别发展领域"""
        return [comp for comp, score in competency_scores.items() if score < 0.7]

    def _generate_recommendations(self, session: SessionData) -> List[str]:
        """生成建议"""
        context = session.context
        comprehensive_result = self._generate_comprehensive_analysis(session)

        if context.assessment_type == AssessmentType.BIG_FIVE_PERSONALITY:
            return self._generate_big_five_recommendations(comprehensive_result)
        elif context.assessment_type == AssessmentType.CITIZENSHIP_KNOWLEDGE:
            return self._generate_knowledge_recommendations(comprehensive_result)
        else:
            return self._generate_professional_recommendations(comprehensive_result)

    def _generate_big_five_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成大五人格建议"""
        recommendations = []

        scores = analysis.get("final_scores", {})
        mbti_type = analysis.get("mbti_inference", "UNKNOWN")

        # 基于分数给出建议
        if scores.get("openness", 0) < 0.5:
            recommendations.append("建议尝试新的事物和体验，培养创新思维")
        if scores.get("conscientiousness", 0) < 0.5:
            recommendations.append("建议加强时间管理和目标设定能力")
        if scores.get("extraversion", 0) < 0.5:
            recommendations.append("建议适当参与社交活动，提升人际交往能力")
        if scores.get("agreeableness", 0) < 0.5:
            recommendations.append("建议培养同理心，加强团队协作意识")
        if scores.get("neuroticism", 0) > 0.5:
            recommendations.append("建议学习压力管理技巧，提升情绪调节能力")

        return recommendations if recommendations else ["继续保持良好的人格特质平衡"]

    def _generate_knowledge_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成知识类建议"""
        recommendations = []
        improvement_areas = analysis.get("improvement_areas", [])

        if improvement_areas:
            recommendations.extend([f"加强对{area}领域的学习" for area in improvement_areas])
        else:
            recommendations.append("继续保持在各个知识领域的优秀表现")

        return recommendations

    def _generate_professional_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成专业类建议"""
        recommendations = []
        development_areas = analysis.get("development_areas", [])

        if development_areas:
            recommendations.extend([f"提升{area}方面的专业能力" for area in development_areas])
        else:
            recommendations.append("继续发挥专业优势，追求更高成就")

        return recommendations

    def _calculate_quality_metrics(self, session: SessionData) -> Dict[str, Any]:
        """计算质量指标"""
        evaluations = session.evaluations

        if not evaluations:
            return {"overall_confidence": 0.0}

        # 平均置信度
        avg_confidence = sum(eval.confidence for eval in evaluations) / len(evaluations)

        # 完成率
        completion_rate = session.completed_questions / session.total_questions

        # 一致性指标（分数方差）
        scores = [eval.score for eval in evaluations]
        if scores:
            variance = sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores)
            consistency = max(0, 1 - variance)  # 方差越小，一致性越高
        else:
            consistency = 0

        return {
            "overall_confidence": round(avg_confidence, 2),
            "completion_rate": round(completion_rate, 2),
            "consistency": round(consistency, 2),
            "total_evaluations": len(evaluations)
        }

    def _generate_evaluation_summary(self, session: SessionData) -> Dict[str, Any]:
        """生成评估摘要"""
        return {
            "session_duration": {
                "start": session.created_at,
                "end": session.updated_at,
                "duration_minutes": self._calculate_duration(session.created_at, session.updated_at)
            },
            "response_statistics": {
                "total_responses": len(session.responses),
                "average_response_length": self._calculate_avg_response_length(session.responses)
            },
            "performance_summary": {
                "highest_score": max([eval.score for eval in session.evaluations]) if session.evaluations else 0,
                "lowest_score": min([eval.score for eval in session.evaluations]) if session.evaluations else 0,
                "average_score": sum([eval.score for eval in session.evaluations]) / len(session.evaluations) if session.evaluations else 0
            }
        }

    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """计算持续时间（分钟）"""
        try:
            from datetime import datetime
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return (end - start).total_seconds() / 60
        except:
            return 0

    def _calculate_avg_response_length(self, responses: List[Dict[str, Any]]) -> float:
        """计算平均回答长度"""
        if not responses:
            return 0

        total_length = 0
        for response in responses:
            response_text = str(response.get("response", ""))
            total_length += len(response_text)

        return total_length / len(responses)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="统一心理评估分析技能")
    parser.add_argument("action", choices=["start", "evaluate", "complete"], help="操作类型")
    parser.add_argument("--session-id", help="会话ID")
    parser.add_argument("--assessment-type", default="big_five_personality", help="测评类型")
    parser.add_argument("--total-questions", type=int, default=50, help="总题目数")
    parser.add_argument("--question-file", help="问题文件路径")
    parser.add_argument("--response-file", help="回答文件路径")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    # 创建技能实例
    skill = UnifiedPsychologicalAnalyzer()

    if args.action == "start":
        result = skill.process_request({
            "action": "start",
            "assessment_type": args.assessment_type,
            "total_questions": args.total_questions
        })

    elif args.action == "evaluate":
        if not args.session_id or not args.question_file:
            print("❌ 评估操作需要 --session-id 和 --question-file")
            return

        # 加载问题和回答
        with open(args.question_file, 'r', encoding='utf-8') as f:
            question = json.load(f)

        response = None
        if args.response_file:
            with open(args.response_file, 'r', encoding='utf-8') as f:
                response = json.load(f)

        result = skill.process_request({
            "action": "evaluate",
            "session_id": args.session_id,
            "question": question,
            "response": response
        })

    elif args.action == "complete":
        if not args.session_id:
            print("❌ 完成操作需要 --session-id")
            return

        result = skill.process_request({
            "action": "complete",
            "session_id": args.session_id
        })

    # 输出结果
    if result.success:
        print(f"✅ {args.action} 操作成功!")
        print(f"置信度: {result.confidence:.2f}")

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result.data, f, indent=2, ensure_ascii=False)
            print(f"结果已保存到: {args.output}")
        else:
            print("\n结果摘要:")
            print(json.dumps(result.data, indent=2, ensure_ascii=False)[:500] + "...")
    else:
        print(f"❌ 操作失败: {result.error_message}")


if __name__ == "__main__":
    main()