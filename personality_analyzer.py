#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人格分析器
提供大五人格和MBTI分析功能
"""

import sys
import os
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any


class BigFiveAnalyzer:
    """
    大五人格分析器
    """
    def __init__(self):
        self.trait_descriptions = {
            "openness_to_experience": {
                "low": "较低的开放性：倾向于传统、实际和具体的思维方式，偏好熟悉的环境和已知的事物。",
                "high": "较高的开放性：倾向于创新、好奇和富有想象力，欣赏艺术、情感和新颖的想法。"
            },
            "conscientiousness": {
                "low": "较低的尽责性：倾向于灵活、自发，不太受规则限制，偏好宽松的环境和即兴的活动。",
                "high": "较高的尽责性：倾向于自律、组织和可靠，有强烈的责任感和目标导向。"
            },
            "extraversion": {
                "low": "较低的外向性：倾向于安静、谨慎和内省，偏好独处或与少数亲密朋友相处。",
                "high": "较高的外向性：倾向于社交、外向和精力充沛，从与他人互动中获得能量。"
            },
            "agreeableness": {
                "low": "较低的宜人性：倾向于直接、质疑和竞争，更关注自身利益而非合作。",
                "high": "较高的宜人性：倾向于合作、信任和利他，关注他人福祉和和谐关系。"
            },
            "neuroticism": {
                "low": "较低的神经质（情绪稳定）：倾向于平静、冷静和自信，能有效应对压力。",
                "high": "较高的神经质（情绪不稳定）：倾向于焦虑、紧张和情绪波动，对压力敏感。"
            }
        }

    def analyze_big5(self, raw_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        分析大五人格
        :param raw_scores: 原始评分字典
        :return: 大五人格分析结果
        """
        # 确保所有特质都在1-5分范围内
        normalized_scores = {}
        for trait, score in raw_scores.items():
            normalized_scores[trait] = max(1, min(5, float(score)))
        
        # 生成分析结果
        analysis_result = {
            "raw_scores": normalized_scores,
            "trait_analysis": {},
            "summary": {
                "big5_profile": self._generate_profile_summary(normalized_scores),
                "strengths": self._identify_strengths(normalized_scores),
                "development_areas": self._identify_development_areas(normalized_scores),
                "overall_description": self._generate_overall_description(normalized_scores)
            },
            "analysis_date": datetime.now().isoformat()
        }
        
        # 为每个特质生成详细分析
        for trait, score in normalized_scores.items():
            is_high = score >= 4
            trait_analysis = {
                "score": score,
                "level": "High" if is_high else "Low",
                "description": self.trait_descriptions[trait]["high" if is_high else "low"],
                "implications": self._generate_trait_implications(trait, score)
            }
            analysis_result["trait_analysis"][trait] = trait_analysis
        
        return analysis_result

    def _generate_profile_summary(self, scores: Dict[str, float]) -> str:
        """生成大五人格概要"""
        trait_labels = {
            "openness_to_experience": "开放性",
            "conscientiousness": "尽责性", 
            "extraversion": "外向性",
            "agreeableness": "宜人性",
            "neuroticism": "神经质"
        }
        
        profile_parts = []
        for trait, score in scores.items():
            label = trait_labels.get(trait, trait)
            level = "高" if score >= 4 else "低" if score <= 2 else "中等"
            profile_parts.append(f"{label}{level}")
        
        return f"大五人格特征: {', '.join(profile_parts)}"

    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """识别优势领域"""
        strengths = []
        for trait, score in scores.items():
            if score >= 4:  # 高分特质视为优势
                trait_name = self._get_trait_chinese_name(trait)
                strengths.append(f"{trait_name} - 高水平的{trait_name}表现")
        return strengths

    def _identify_development_areas(self, scores: Dict[str, float]) -> List[str]:
        """识别发展领域"""
        areas = []
        for trait, score in scores.items():
            if score <= 2:  # 低分特质视为发展领域
                trait_name = self._get_trait_chinese_name(trait)
                areas.append(f"{trait_name} - 可以在{trait_name}方面进一步提升")
        return areas

    def _generate_overall_description(self, scores: Dict[str, float]) -> str:
        """生成总体描述"""
        # 根据主要特征生成描述
        high_traits = [trait for trait, score in scores.items() if score >= 4]
        low_traits = [trait for trait, score in scores.items() if score <= 2]
        
        if len(high_traits) >= 3:
            return "整体表现出较强的个性特征，各个维度相对均衡或偏向高分端。"
        elif len(low_traits) >= 3:
            return "整体表现出相对保守的个性特征，各个维度相对均衡或偏向低分端。"
        else:
            return "个性特征相对均衡，各维度分数分布较为平均。"

    def _generate_trait_implications(self, trait: str, score: float) -> str:
        """生成特质影响分析"""
        implications = {
            "openness_to_experience": {
                "high": "倾向于接受新体验，富有创造力，在艺术和学术领域可能表现突出。",
                "low": "倾向于传统和实际，在熟悉和结构化的环境中表现更佳。"
            },
            "conscientiousness": {
                "high": "倾向于自律和计划，适合需要持久专注和高度组织的任务。",
                "low": "倾向于灵活和自发，适合需要创新能力的动态环境。"
            },
            "extraversion": {
                "high": "倾向于社交活跃，在团队合作和领导角色中表现突出。",
                "low": "倾向于独立工作，在需要深度思考和专注的任务中表现更佳。"
            },
            "agreeableness": {
                "high": "倾向于合作和谐，适合团队工作和人际交往密集的角色。",
                "low": "倾向于直接和竞争，适合需要客观判断和决策的角色。"
            },
            "neuroticism": {
                "high": "倾向于情绪敏感，可能需要额外的压力管理支持。",
                "low": "倾向于情绪稳定，适合高压和变化频繁的环境。"
            }
        }
        
        level_key = "high" if score >= 4 else "low"
        return implications.get(trait, {}).get(level_key, "未定义的特质影响")

    def _get_trait_chinese_name(self, trait: str) -> str:
        """获取特质中文名称"""
        names = {
            "openness_to_experience": "开放性",
            "conscientiousness": "尽责性",
            "extraversion": "外向性",
            "agreeableness": "宜人性",
            "neuroticism": "神经质"
        }
        return names.get(trait, trait)


class MBTIAnalyzer:
    """
    MBTI类型分析器
    """
    def __init__(self):
        self.mbti_types = {
            "INTJ": {"name": "建筑师", "description": "富有想象力和战略性思维，喜欢对知识和能力有深入掌握"},
            "INTP": {"name": "逻辑学家", "description": "富有想象力和分析能力，对知识的渴求永无止境"},
            "ENTJ": {"name": "指挥官", "description": "天生的领导者，意志坚强，富有想象力，组织能力强"},
            "ENTP": {"name": "辩论家", "description": "聪明，有魅力，喜欢挑战和创意，是天生的推销员"},
            "INFJ": {"name": "提倡者", "description": "安静而神秘，促使他人具有意义和目的"},
            "INFP": {"name": "调解者", "description": "诗意，善良，总是从深层的个人价值观帮助他人"},
            "ENFJ": {"name": "主人公", "description": "天生的组织者，温暖，富有同情心，鼓舞他人"},
            "ENFP": {"name": "竞选者", "description": "热情，富有创造力，善于社交，总是寻找生命中的最佳体验"},
            "ISTJ": {"name": "物流师", "description": "尽责，可靠，正直，有条理，注重细节"},
            "ISFJ": {"name": "守卫者", "description": "温暖，可靠，乐于奉献，关注他人实际需求"},
            "ESTJ": {"name": "总经理", "description": "务实，高效，逻辑清晰，重视传统和规则"},
            "ESFJ": {"name": "执政官", "description": "富有同情心，受欢迎，总是乐于帮助他人"},
            "ISTP": {"name": "鉴赏家", "description": "灵活，忍耐力强，实际，喜欢使用理论解决实际问题"},
            "ISFP": {"name": "探险家", "description": "温和灵活，敏感，享受当下，热爱自然和美"},
            "ESTP": {"name": "企业家", "description": "勇于实践，能量充沛，享受生活，喜欢冒险"},
            "ESFP": {"name": "表演者", "description": "自发，充满活力，热情，喜欢帮助他人享受生活"}
        }

    def map_to_mbti(self, big5_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        将大五人格评分映射到MBTI类型
        :param big5_scores: 大五人格评分
        :return: MBTI分析结果
        """
        # 将大五评分转换为MBTI维度
        mbti_dimensions = self._big5_to_mbti_dimensions(big5_scores)
        
        # 生成MBTI类型
        mbti_type = f"{mbti_dimensions['E_I']}{mbti_dimensions['S_N']}{mbti_dimensions['T_F']}{mbti_dimensions['J_P']}"
        
        # 获取MBTI类型描述
        type_info = self.mbti_types.get(mbti_type, {
            "name": "未知类型",
            "description": "无法确定具体的MBTI类型"
        })
        
        # 计算维度得分和确定性
        dimension_certainties = self._calculate_dimension_certainties(big5_scores)
        
        result = {
            "mbti_type": mbti_type,
            "type_name": type_info["name"],
            "type_description": type_info["description"],
            "dimensions": mbti_dimensions,
            "dimension_certainties": dimension_certainties,
            "mapping_confidence": self._calculate_mapping_confidence(dimension_certainties),
            "analysis_date": datetime.now().isoformat()
        }
        
        return result

    def _big5_to_mbti_dimensions(self, big5_scores: Dict[str, float]) -> Dict[str, str]:
        """
        将大五评分转换为MBTI维度
        """
        # 简化映射逻辑（实际应用中可能需要更复杂的算法）
        # 外向性(E)-内向性(I)
        e_i = 'E' if big5_scores.get('extraversion', 3) > 3 else 'I'
        
        # 感觉(S)-直觉(N) - 相对开放性
        s_n = 'N' if big5_scores.get('openness_to_experience', 3) > 3 else 'S'
        
        # 思考(T)-情感(F) - 相对宜人性(反向)
        t_f = 'F' if big5_scores.get('agreeableness', 3) > 3 else 'T'
        
        # 判断(J)-感知(P) - 相对尽责性
        j_p = 'J' if big5_scores.get('conscientiousness', 3) > 3 else 'P'
        
        return {
            "E_I": e_i,
            "S_N": s_n,
            "T_F": t_f,
            "J_P": j_p
        }

    def _calculate_dimension_certainties(self, big5_scores: Dict[str, float]) -> Dict[str, float]:
        """
        计算每个维度的确定性
        """
        # 基于原始大五评分与中间点的差距计算确定性
        certainties = {}
        
        # 外向性确定性
        extraversion_diff = abs(big5_scores.get('extraversion', 3) - 3)
        certainties['E_I'] = min(1.0, extraversion_diff / 2.0)
        
        # 直觉-感觉确定性
        openness_diff = abs(big5_scores.get('openness_to_experience', 3) - 3)
        certainties['S_N'] = min(1.0, openness_diff / 2.0)
        
        # 思考-情感确定性
        agreeableness_diff = abs(big5_scores.get('agreeableness', 3) - 3)
        certainties['T_F'] = min(1.0, agreeableness_diff / 2.0)
        
        # 判断-感知确定性
        conscientiousness_diff = abs(big5_scores.get('conscientiousness', 3) - 3)
        certainties['J_P'] = min(1.0, conscientiousness_diff / 2.0)
        
        return certainties

    def _calculate_mapping_confidence(self, certainties: Dict[str, float]) -> float:
        """
        计算整体映射置信度
        """
        if not certainties:
            return 0.0
        
        # 平均各维度的确定性
        return statistics.mean(certainties.values())


class PersonalityAnalyzer:
    """
    综合人格分析器
    """
    def __init__(self):
        self.big5_analyzer = BigFiveAnalyzer()
        self.mbti_analyzer = MBTIAnalyzer()

    def analyze_personality(self, final_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        执行完整的人格分析
        :param final_scores: 最终的大五人格评分
        :return: 完整的人格分析报告
        """
        # 执行大五分析
        big5_result = self.big5_analyzer.analyze_big5(final_scores)
        
        # 执行MBTI分析
        mbti_result = self.mbti_analyzer.map_to_mbti(final_scores)
        
        # 整合结果
        comprehensive_analysis = {
            "personality_analysis_date": datetime.now().isoformat(),
            "big5_analysis": big5_result,
            "mbti_analysis": mbti_result,
            "integrated_insights": self._generate_integrated_insights(big5_result, mbti_result),
            "recommendations": self._generate_recommendations(big5_result, mbti_result)
        }
        
        return comprehensive_analysis

    def _generate_integrated_insights(self, big5_result: Dict, mbti_result: Dict) -> List[str]:
        """
        生成综合洞察
        """
        insights = []
        
        # 基于大五和MBTI一致性生成洞察
        raw_scores = big5_result["raw_scores"]
        
        if raw_scores.get("extraversion", 3) > 3 and mbti_result["dimensions"]["E_I"] == "E":
            insights.append("外向性分析一致：倾向于社交活跃，从外部世界获取能量")
        
        if raw_scores.get("openness_to_experience", 3) > 3 and mbti_result["dimensions"]["S_N"] == "N":
            insights.append("开放性与直觉维度一致：倾向于创新思维，关注未来可能性")
        
        return insights

    def _generate_recommendations(self, big5_result: Dict, mbti_result: Dict) -> Dict[str, List[str]]:
        """
        生成建议
        """
        recommendations = {
            "career": [],
            "relationships": [],
            "development": []
        }
        
        # 基于分析结果生成建议
        raw_scores = big5_result["raw_scores"]
        
        # 职业建议
        if raw_scores.get("conscientiousness", 3) > 3:
            recommendations["career"].append("适合需要高度组织性和责任感的职业")
        
        # 关系建议
        if raw_scores.get("agreeableness", 3) > 3:
            recommendations["relationships"].append("在合作和和谐的环境中表现最佳")
        
        # 发展建议
        low_traits = [trait for trait, score in raw_scores.items() if score <= 2]
        if low_traits:
            low_trait_names = [self.big5_analyzer._get_trait_chinese_name(trait) for trait in low_traits]
            recommendations["development"].append(f"可考虑在{', '.join(low_trait_names)}方面进一步发展")
        
        return recommendations


def main():
    """
    主函数 - 演示用法
    """
    # 创建人格分析器实例
    analyzer = PersonalityAnalyzer()
    
    # 示例评分 (1-5分)
    example_scores = {
        "openness_to_experience": 4.2,
        "conscientiousness": 3.8,
        "extraversion": 2.9,
        "agreeableness": 4.1,
        "neuroticism": 2.5
    }
    
    # 执行分析
    result = analyzer.analyze_personality(example_scores)
    
    # 输出结果
    print("人格分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()