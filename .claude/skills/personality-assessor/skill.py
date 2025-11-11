#!/usr/bin/env python3
"""
Personality Assessor - 人格评估技能
专门对大五人格测评问卷进行评估分析的技能
逐题评估大五各维度的分数，最后按照题目的主要维度加权计算大五人格各个维度的平均分
再映射为不同的人格类型MBTI类型和贝尔宾人格类型
"""

import json
import statistics
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime


class PersonalityAssessor:
    """人格评估技能类"""

    def __init__(self):
        """初始化人格评估技能"""
        self.session_id = None
        self.session_start_time = None
        self.evaluation_results = []
        self.dimension_scores = {
            'O': [],  # 开放性 (Openness)
            'C': [],  # 尽责性 (Conscientiousness)
            'E': [],  # 外向性 (Extraversion)
            'A': [],  # 宜人性 (Agreeableness)
            'N': []   # 神经质 (Neuroticism)
        }

        # 加权计算权重配置
        self.scoring_weights = {
            'primary_dimension': 0.8,    # 主要维度权重
            'secondary_dimension': 0.05  # 次要维度权重
        }

        # 维度间影响关系配置
        self.dimension_influence = {
            'O': ['E', 'N'],    # 开放性影响外向性和神经质
            'C': ['E', 'N'],    # 尽责性影响外向性和神经质
            'E': ['O', 'A'],    # 外向性影响开放性和宜人性
            'A': ['N', 'E'],    # 宜人性影响神经质和外向性
            'N': ['E', 'C']     # 神经质影响外向性和尽责性
        }

        # MBTI类型映射规则
        self.mbti_mapping = {
            'EI_threshold': 3.5,  # E/I判断阈值
            'SN_threshold': 3.5,  # S/N判断阈值
            'TF_threshold': 3.5,  # T/F判断阈值（宜人性反向）
            'JP_threshold': 3.5   # J/P判断阈值
        }

        # 贝尔宾团队角色映射
        self.belbin_mapping = self._create_belbin_mapping()

        # 大五人格维度详细信息
        self.dimension_info = {
            'O': {'name': '开放性', 'description': '对新体验的开放程度，包括想象力、艺术兴趣、情感丰富、求知欲、创造力、思想开放等'},
            'C': {'name': '尽责性', 'description': '自律、条理性、责任心、成就导向、审慎、自我控制的程度'},
            'E': {'name': '外向性', 'description': '社交性、果断性、活跃度、积极情绪、寻求刺激的程度'},
            'A': {'name': '宜人性', 'description': '信任他人、直率、利他、顺从、谦逊、心软的程度'},
            'N': {'name': '神经质', 'description': '焦虑、愤怒、抑郁、自我意识、冲动、脆弱的程度'}
        }

    def _create_belbin_mapping(self) -> Dict:
        """创建贝尔宾团队角色映射"""
        return {
            '协调者': {
                'O': 3.5, 'C': 3.0, 'E': 3.0, 'A': 4.5, 'N': 2.0,
                'description': '成熟、自信，有明确的目标导向，能够 delegating 工作并促进团队协作'
            },
            '塑造者': {
                'O': 3.0, 'C': 4.0, 'E': 4.5, 'A': 2.5, 'N': 2.5,
                'description': '充满活力、挑战障碍、压力下保持动力'
            },
            '创新者': {
                'O': 4.5, 'C': 2.5, 'E': 3.0, 'A': 3.0, 'N': 3.5,
                'description': '有创造力、想象力、非传统思维，解决问题能力强'
            },
            '资源调查者': {
                'O': 4.0, 'C': 3.0, 'E': 4.0, 'A': 3.5, 'N': 2.5,
                'description': '外向、热情、善于交际，探索机会和开发联系'
            },
            '协作者': {
                'O': 3.5, 'C': 3.0, 'E': 3.5, 'A': 4.5, 'N': 2.0,
                'description': '温和、敏感、善于社交，避免冲突，促进团队和谐'
            },
            '执行者': {
                'O': 2.5, 'C': 4.5, 'E': 3.0, 'A': 3.5, 'N': 2.0,
                'description': '保守、尽责、可预测，高效完成工作'
            },
            '完成者': {
                'O': 3.0, 'C': 4.5, 'E': 2.5, 'A': 3.0, 'N': 3.0,
                'description': '认真尽责、寻找错误和疏漏、准时完成工作'
            },
            '专家': {
                'O': 3.5, 'C': 4.0, 'E': 2.0, 'A': 3.0, 'N': 3.0,
                'description': '专注、自主、专业知识和技能驱动'
            }
        }

    def start_evaluation_session(self, total_questions: int) -> Dict[str, Any]:
        """开始评估会话"""
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start_time = datetime.now()
        self.evaluation_results = []
        self.dimension_scores = {'O': [], 'C': [], 'E': [], 'A': [], 'N': []}

        return {
            'session_id': self.session_id,
            'session_timestamp': self.session_start_time.isoformat(),
            'total_questions': total_questions,
            'status': 'session_started'
        }

    def evaluate_single_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """评估单个问题的回答"""
        try:
            question = question_data.get('question', '')
            response = question_data.get('response', '')
            dimension = question_data.get('dimension', '')
            question_id = question_data.get('question_id', '')

            if not question or not response or not dimension:
                return {
                    'error': f'缺少必要数据: question={bool(question)}, response={bool(response)}, dimension={bool(dimension)}'
                }

            # 转换维度名称（例如: 'extraversion' -> 'E'）
            dimension_code = self._convert_dimension_name(dimension)

            # 基于流水线评估逻辑的单题评估
            scores = self._analyze_question_response(question, response, dimension_code)

            # 记录评估结果
            result = {
                'question_id': question_id,
                'question': question,
                'response': response,
                'dimension': dimension_code,
                'dimension_original': dimension,
                'scores': scores,
                'evaluation_time': datetime.now().isoformat()
            }

            self.evaluation_results.append(result)

            # 按维度记录分数
            for dim, score in scores.items():
                if dim in self.dimension_scores and 1 <= score <= 5:
                    self.dimension_scores[dim].append(score)

            return result

        except Exception as e:
            return {'error': f'评估失败: {str(e)}'}

    def _convert_dimension_name(self, dimension: str) -> str:
        """转换维度名称为标准代码"""
        dimension_mapping = {
            'openness': 'O',
            'conscientiousness': 'C',
            'extraversion': 'E',
            'agreeableness': 'A',
            'neuroticism': 'N',
            'O': 'O',
            'C': 'C',
            'E': 'E',
            'A': 'A',
            'N': 'N'
        }
        return dimension_mapping.get(dimension.lower(), dimension)

    def _analyze_question_response(self, question: str, response: str, dimension: str) -> Dict[str, float]:
        """分析问题回答，给出大五各维度分数（使用加权计算）"""
        # 默认中性分数
        default_scores = {'O': 3.0, 'C': 3.0, 'E': 3.0, 'A': 3.0, 'N': 3.0}

        # 根据题目维度和回答内容评估基础分数
        base_scores = default_scores.copy()

        # 主要维度基础评分
        primary_score = self._evaluate_dimension_score(question, response, dimension)
        base_scores[dimension] = float(primary_score)

        # 影响维度基础评分
        influence_scores = self._evaluate_influence_dimensions(question, response, dimension)
        for dim, score in influence_scores.items():
            if dim in base_scores:
                base_scores[dim] = float(score)

        # 应用加权计算
        weighted_scores = self._apply_weighted_calculation(base_scores, dimension)

        return weighted_scores

    def _apply_weighted_calculation(self, base_scores: Dict[str, float], primary_dimension: str) -> Dict[str, float]:
        """应用加权计算：主要维度0.8，次要维度0.05"""
        weighted_scores = {}

        for dim in ['O', 'C', 'E', 'A', 'N']:
            if dim == primary_dimension:
                # 主要维度，权重0.8
                weighted_scores[dim] = base_scores[dim] * self.scoring_weights['primary_dimension']
            elif dim in self.dimension_influence.get(primary_dimension, []):
                # 次要维度，权重0.05
                weighted_scores[dim] = base_scores[dim] * self.scoring_weights['secondary_dimension']
            else:
                # 无关维度，不参与加权计算
                weighted_scores[dim] = 0.0

        return weighted_scores

    def _evaluate_dimension_score(self, question: str, response: str, dimension: str) -> int:
        """评估特定维度的分数"""
        # 简化的评分逻辑，基于关键词和回答特征

        # 积极指标关键词
        positive_keywords = {
            'O': ['创新', '探索', '好奇', '创意', '艺术', '新', '尝试', '学习', '想象'],
            'C': ['负责', '计划', '组织', '认真', '努力', '目标', '按时', '仔细', '规则'],
            'E': ['社交', '外向', '活跃', '热情', '表达', '交流', '朋友', '群体', '开朗'],
            'A': ['合作', '帮助', '理解', '关心', '和谐', '友善', '信任', '支持', '体贴'],
            'N': ['担心', '紧张', '压力', '焦虑', '不安', '情绪', '敏感', '波动', '恐惧']
        }

        # 消极指标关键词
        negative_keywords = {
            'O': ['传统', '保守', '常规', '不变', '固定', '熟悉', '习惯'],
            'C': ['随意', '拖延', '混乱', '冲动', '放松', '灵活', '自由'],
            'E': ['安静', '内向', '独立', '独处', '思考', '谨慎', '保守'],
            'A': ['竞争', '挑战', '批评', '怀疑', '自我', '独立', '坚持'],
            'N': ['冷静', '稳定', '平和', '理性', '放松', '自信', '沉着']
        }

        response_lower = response.lower()
        question_lower = question.lower()

        positive_count = 0
        negative_count = 0

        # 统计积极关键词
        for keyword in positive_keywords.get(dimension, []):
            if keyword in response_lower or keyword in question_lower:
                positive_count += 1

        # 统计消极关键词
        for keyword in negative_keywords.get(dimension, []):
            if keyword in response_lower or keyword in question_lower:
                negative_count += 1

        # 计算分数
        if positive_count > negative_count:
            return 5 if positive_count >= 2 else 4
        elif negative_count > positive_count:
            return 1 if negative_count >= 2 else 2
        else:
            return 3

    def _evaluate_influence_dimensions(self, question: str, response: str, primary_dimension: str) -> Dict[str, int]:
        """评估其他受影响的维度分数"""
        influence_scores = {}

        # 维度间影响关系（简化版）
        influence_relations = {
            'O': {'E': 0.1, 'N': 0.1},  # 开放性轻微影响外向性和神经质
            'C': {'E': -0.1, 'N': -0.2}, # 尽责性轻微负向影响外向性和神经质
            'E': {'O': 0.1, 'A': 0.1},  # 外向性轻微影响开放性和宜人性
            'A': {'N': -0.2, 'E': 0.1}, # 宜人性负向影响神经质，正向影响外向性
            'N': {'E': -0.2, 'C': -0.1}  # 神经质负向影响外向性和尽责性
        }

        primary_score = self._evaluate_dimension_score(question, response, primary_dimension)

        for influenced_dim, influence in influence_relations.get(primary_dimension, {}).items():
            # 基于主要维度分数和影响系数计算
            adjusted_score = primary_score + (influence * 2)  # 放大影响效果
            influenced_score = max(1, min(5, round(adjusted_score)))
            influence_scores[influenced_dim] = influenced_score

        return influence_scores

    def complete_evaluation(self) -> Dict[str, Any]:
        """完成评估并生成完整报告（使用加权平均计算）"""
        try:
            # 使用加权计算系统计算各维度最终分数
            final_scores = self._calculate_weighted_final_scores()

            # 生成MBTI类型
            mbti_result = self._generate_mbti_type(final_scores)

            # 生成贝尔宾团队角色
            belbin_result = self._generate_belbin_role(final_scores)

            # 计算评估置信度
            confidence = self._calculate_confidence()

            # 生成加权计算详细信息
            weighted_details = self._generate_weighted_calculation_details()

            # 生成完整报告
            report = {
                'session_info': {
                    'session_id': self.session_id,
                    'start_time': self.session_start_time.isoformat() if self.session_start_time else None,
                    'end_time': datetime.now().isoformat(),
                    'total_questions': len(self.evaluation_results),
                    'successful_evaluations': len([r for r in self.evaluation_results if 'error' not in r])
                },
                'big_five_scores': final_scores,
                'mbti_assessment': mbti_result,
                'belbin_assessment': belbin_result,
                'evaluation_confidence': confidence,
                'weighted_calculation_details': weighted_details,
                'detailed_results': self.evaluation_results,
                'dimension_analysis': {
                    'score_counts': {dim: len(scores) for dim, scores in self.dimension_scores.items()},
                    'score_ranges': {
                        dim: {'min': min(scores), 'max': max(scores)} if scores else {'min': 3, 'max': 3}
                        for dim, scores in self.dimension_scores.items()
                    }
                },
                'success': True
            }

            return report

        except Exception as e:
            return {
                'success': False,
                'error': f'完成评估失败: {str(e)}',
                'session_info': {
                    'session_id': self.session_id,
                    'evaluated_questions': len(self.evaluation_results)
                }
            }

    def _calculate_weighted_final_scores(self) -> Dict[str, float]:
        """计算加权平均的最终分数"""
        # 初始化各维度的加权总分和权重总合
        weighted_sums = {'O': 0.0, 'C': 0.0, 'E': 0.0, 'A': 0.0, 'N': 0.0}
        weight_sums = {'O': 0.0, 'C': 0.0, 'E': 0.0, 'A': 0.0, 'N': 0.0}

        # 统计每个维度作为主要维度和次要维度的次数
        primary_counts = {'O': 0, 'C': 0, 'E': 0, 'A': 0, 'N': 0}
        secondary_counts = {'O': 0, 'C': 0, 'E': 0, 'A': 0, 'N': 0}

        for result in self.evaluation_results:
            if 'error' in result:
                continue

            scores = result.get('scores', {})
            dimension = result.get('dimension', '')

            if not dimension or dimension not in scores:
                continue

            # 主要维度加权
            if dimension in weighted_sums:
                primary_weight = self.scoring_weights['primary_dimension']
                weighted_sums[dimension] += scores[dimension] * primary_weight
                weight_sums[dimension] += primary_weight
                primary_counts[dimension] += 1

            # 次要维度加权
            influenced_dims = self.dimension_influence.get(dimension, [])
            for influenced_dim in influenced_dims:
                if influenced_dim in weighted_sums and influenced_dim in scores:
                    secondary_weight = self.scoring_weights['secondary_dimension']
                    weighted_sums[influenced_dim] += scores[influenced_dim] * secondary_weight
                    weight_sums[influenced_dim] += secondary_weight
                    secondary_counts[influenced_dim] += 1

        # 计算加权平均
        final_scores = {}
        for dim in ['O', 'C', 'E', 'A', 'N']:
            if weight_sums[dim] > 0:
                final_scores[dim] = round(weighted_sums[dim] / weight_sums[dim], 2)
            else:
                final_scores[dim] = 3.0  # 默认中性分数

        return final_scores

    def _generate_weighted_calculation_details(self) -> Dict[str, Any]:
        """生成加权计算详细信息"""
        # 统计各维度的题目数量
        dimension_question_counts = {'O': 0, 'C': 0, 'E': 0, 'A': 0, 'N': 0}

        for result in self.evaluation_results:
            if 'error' not in result:
                dimension = result.get('dimension', '')
                if dimension in dimension_question_counts:
                    dimension_question_counts[dimension] += 1

        return {
            'scoring_weights': self.scoring_weights,
            'dimension_influence': self.dimension_influence,
            'question_distribution': dimension_question_counts,
            'calculation_method': '主要维度权重0.8，次要维度权重0.05，按题目加权平均计算'
        }

    def _generate_mbti_type(self, big_five_scores: Dict[str, float]) -> Dict[str, Any]:
        """根据大五分数生成MBTI类型"""
        # E/I 判断（基于外向性）
        e_score = big_five_scores.get('E', 3.0)
        ei_type = 'E' if e_score > self.mbti_mapping['EI_threshold'] else 'I'
        ei_confidence = abs(e_score - self.mbti_mapping['EI_threshold']) * 20

        # S/N 判断（基于开放性）
        o_score = big_five_scores.get('O', 3.0)
        sn_type = 'N' if o_score > self.mbti_mapping['SN_threshold'] else 'S'
        sn_confidence = abs(o_score - self.mbti_mapping['SN_threshold']) * 20

        # T/F 判断（基于宜人性，反向）
        a_score = big_five_scores.get('A', 3.0)
        tf_type = 'F' if a_score > self.mbti_mapping['TF_threshold'] else 'T'
        tf_confidence = abs(a_score - self.mbti_mapping['TF_threshold']) * 20

        # J/P 判断（基于尽责性）
        c_score = big_five_scores.get('C', 3.0)
        jp_type = 'J' if c_score > self.mbti_mapping['JP_threshold'] else 'P'
        jp_confidence = abs(c_score - self.mbti_mapping['JP_threshold']) * 20

        mbti_type = ei_type + sn_type + tf_type + jp_type

        # MBTI类型描述
        mbti_descriptions = {
            'ISTJ': '物流师 - 务实、可靠、有条理的传统主义者',
            'ISFJ': '守护者 - 温暖、利他、尽责的守护者',
            'INFJ': '提倡者 - 理想主义、洞察力、奉献的引路人',
            'INTJ': '建筑师 - 战略性、独立思考的建筑师',
            'ISTP': '鉴赏家 - 灵活、冷静、实用的鉴赏家',
            'ISFP': '探险家 - 艺术性、敏感、自由的探险家',
            'INFP': '调停者 - 价值驱动、和谐的调停者',
            'INTP': '思想家 - 逻辑性、好奇心强的思想家',
            'ESTP': '企业家 - 精力充沛、冒险性的企业家',
            'ESFP': '娱乐家 - 热情、社交性强的娱乐家',
            'ESTJ': '总经理 - 高效、传统、可靠的总经理',
            'ESFJ': '执政官 - 和谐、利他、社交的执政官',
            'ENTP': '辩论家 - 创新性、适应性、聪明的辩论家',
            'ENTJ': '指挥官 - 领导力、战略性、果断的指挥官',
            'ENFP': '竞选者 - 热情、创造力、社交性的竞选者',
            'ENFJ': '主人公 - 魅力、利他主义、领导力的主人公'
        }

        overall_confidence = (ei_confidence + sn_confidence + tf_confidence + jp_confidence) / 4

        return {
            'type': mbti_type,
            'description': mbti_descriptions.get(mbti_type, '未知类型'),
            'confidence': min(100, max(0, overall_confidence)),
            'dimension_scores': {
                'E/I': f'{e_score:.1f} ({ei_type})',
                'S/N': f'{o_score:.1f} ({sn_type})',
                'T/F': f'{a_score:.1f} ({tf_type})',
                'J/P': f'{c_score:.1f} ({jp_type})'
            },
            'confidence_breakdown': {
                'EI': ei_confidence,
                'SN': sn_confidence,
                'TF': tf_confidence,
                'JP': jp_confidence
            }
        }

    def _generate_belbin_role(self, big_five_scores: Dict[str, float]) -> Dict[str, Any]:
        """根据大五分数生成贝尔宾团队角色"""
        best_match = None
        best_score = 0

        for role, profile in self.belbin_mapping.items():
            # 计算与角色的匹配度
            match_score = 0
            total_weight = 0

            for dim, target_score in profile.items():
                if dim in ['O', 'C', 'E', 'A', 'N']:
                    actual_score = big_five_scores.get(dim, 3.0)
                    # 使用负相关计算相似度
                    distance = abs(actual_score - target_score)
                    similarity = max(0, 5 - distance) / 5  # 0-1之间的相似度
                    match_score += similarity
                    total_weight += 1

            if total_weight > 0:
                avg_match = match_score / total_weight
                if avg_match > best_score:
                    best_score = avg_match
                    best_match = role

        if best_match:
            return {
                'primary_role': best_match,
                'description': self.belbin_mapping[best_match]['description'],
                'match_score': round(best_score * 100, 1),
                'profile_scores': {
                    dim: big_five_scores.get(dim, 3.0)
                    for dim in ['O', 'C', 'E', 'A', 'N']
                }
            }
        else:
            return {
                'primary_role': '未确定',
                'description': '无法确定明确的团队角色',
                'match_score': 0,
                'profile_scores': big_five_scores
            }

    def _calculate_confidence(self) -> float:
        """计算评估置信度"""
        if not self.evaluation_results:
            return 0.0

        # 基于成功评估的题目数量计算置信度
        successful_evaluations = len([r for r in self.evaluation_results if 'error' not in r])
        total_evaluations = len(self.evaluation_results)

        if total_evaluations == 0:
            return 0.0

        # 基础置信度
        base_confidence = (successful_evaluations / total_evaluations) * 80

        # 基于各维度分数分布的一致性调整
        consistency_bonus = 0
        for dim, scores in self.dimension_scores.items():
            if len(scores) >= 2:
                # 计算分数的标准差，标准差越小，一致性越高
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                consistency_bonus += max(0, 10 - std_dev * 2)

        total_confidence = base_confidence + (consistency_bonus / 5)  # 5个维度平均

        return min(100, max(0, total_confidence))


# 技能接口函数
def analyze_big_five_questionnaire(questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
    """分析大五人格问卷数据的主函数"""
    assessor = PersonalityAssessor()

    try:
        # 提取答案数据
        answers = questionnaire_data.get('answers', [])

        if not answers:
            return {
                'success': False,
                'error': '没有找到答案数据'
            }

        # 开始评估会话
        session_result = assessor.start_evaluation_session(len(answers))

        # 逐个评估问题
        for answer in answers:
            question_data = answer.get('question_data', {})
            claude_response = answer.get('claude_response', '')

            result = assessor.evaluate_single_question({
                'question': question_data.get('question', ''),
                'question_id': question_data.get('question_id', ''),
                'dimension': question_data.get('dimension', ''),
                'response': claude_response
            })

        # 完成评估
        final_report = assessor.complete_evaluation()

        return final_report

    except Exception as e:
        return {
            'success': False,
            'error': f'分析过程出错: {str(e)}'
        }


def skill_main(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """技能主入口函数"""
    return analyze_big_five_questionnaire(input_data)