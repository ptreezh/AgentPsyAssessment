#!/usr/bin/env python3
"""
简单大五人格分析器
基于Claude回答内容直接分析大五人格特质和MBTI类型
"""

import json
import os
import re
from collections import defaultdict

class SimpleBigFiveAnalyzer:
    def __init__(self):
        # 大五人格维度关键词
        self.dimension_keywords = {
            'openness': {
                'positive': ['好奇', '创意', '探索', '新奇', '想象', '艺术', '开放', '创新', '尝试', '学习'],
                'negative': ['传统', '保守', '常规', '实用', '不变']
            },
            'conscientiousness': {
                'positive': ['有条理', '负责任', '自律', '可靠', '计划', '组织', '认真', '勤奋', '目标'],
                'negative': ['随意', '冲动', '混乱', '无计划', '拖延']
            },
            'extraversion': {
                'positive': ['活跃', '外向', '社交', '健谈', '热情', '乐观', '果断', '表达'],
                'negative': ['内向', '保守', '沉默', '独立', '安静']
            },
            'agreeableness': {
                'positive': ['信任', '善意', '合作', '友善', '同理心', '利他', '和谐', '帮助'],
                'negative': ['怀疑', '竞争', '挑战', '自我', '批判']
            },
            'neuroticism': {
                'positive': ['焦虑', '压力', '情绪化', '担忧', '紧张', '敏感', '波动'],  # 这里positive表示神经质特征
                'negative': ['冷静', '稳定', '平和', '抗压', '理性', '放松']
            }
        }

        # MBTI映射规则
        self.mbti_mapping = {
            'EI': 'extraversion',  # E/I 对应外向性
            'SN': 'openness',      # S/N 对应开放性
            'TF': 'agreeableness', # T/F 对应宜人性（简化）
            'JP': 'conscientiousness'  # J/P 对应尽责性
        }

    def analyze_text_sentiment(self, text: str, dimension: str) -> float:
        """分析文本在特定维度上的得分"""
        if not text:
            return 5.0  # 中性分数

        text_lower = text.lower()
        keywords = self.dimension_keywords[dimension]

        positive_count = sum(1 for word in keywords['positive'] if word in text_lower)
        negative_count = sum(1 for word in keywords['negative'] if word in text_lower)

        # 基础分数为5，根据关键词调整
        base_score = 5.0
        adjustment = (positive_count - negative_count) * 0.5

        score = max(1.0, min(10.0, base_score + adjustment))
        return score

    def analyze_answer(self, answer_data: dict) -> dict:
        """分析单个回答"""
        dimension = answer_data.get('question_data', {}).get('dimension', '')
        scale = answer_data.get('question_data', {}).get('scale', 1)
        response = answer_data.get('claude_response', '')

        if not dimension:
            return {}

        # 基于关键词分析得到分数
        keyword_score = self.analyze_text_sentiment(response, dimension)

        # 考虑问题的scale方向
        if scale == -1:  # 反向计分
            keyword_score = 11 - keyword_score

        return {
            'dimension': dimension,
            'score': keyword_score,
            'scale': scale,
            'response_length': len(response),
            'keywords_found': self._extract_keywords(response, dimension)
        }

    def _extract_keywords(self, text: str, dimension: str) -> list:
        """提取文本中的关键词"""
        if not text:
            return []

        text_lower = text.lower()
        keywords = self.dimension_keywords[dimension]
        found = []

        for word in keywords['positive'] + keywords['negative']:
            if word in text_lower:
                found.append(word)

        return found

    def analyze_questionnaire(self, test_data: dict) -> dict:
        """分析完整问卷"""
        answers = test_data.get('answers', [])
        session_info = test_data.get('session_info', {})

        dimension_scores = defaultdict(list)

        for answer in answers:
            analysis = self.analyze_answer(answer)
            if analysis:
                dimension_scores[analysis['dimension']].append(analysis['score'])

        # 计算各维度平均分
        final_scores = {}
        for dimension, scores in dimension_scores.items():
            if scores:
                final_scores[dimension] = sum(scores) / len(scores)
            else:
                final_scores[dimension] = 5.0

        # 转换为MBTI
        mbti_result = self.convert_to_mbti(final_scores)

        return {
            'session_info': session_info,
            'big_five_scores': final_scores,
            'mbti_type': mbti_result,
            'answer_count': len(answers),
            'dimension_analysis': dict(dimension_scores)
        }

    def convert_to_mbti(self, big_five_scores: dict) -> dict:
        """将大五人格分数转换为MBTI类型"""

        # E/I 判断 (基于外向性)
        e_score = big_five_scores.get('extraversion', 5.0)
        ei_type = 'E' if e_score > 5.5 else 'I'

        # S/N 判断 (基于开放性)
        o_score = big_five_scores.get('openness', 5.0)
        sn_type = 'N' if o_score > 5.5 else 'S'

        # T/F 判断 (基于宜人性，反向)
        a_score = big_five_scores.get('agreeableness', 5.0)
        tf_type = 'F' if a_score > 5.5 else 'T'

        # J/P 判断 (基于尽责性)
        c_score = big_five_scores.get('conscientiousness', 5.0)
        jp_type = 'J' if c_score > 5.5 else 'P'

        mbti_type = ei_type + sn_type + tf_type + jp_type

        # MBTI类型描述
        mbti_descriptions = {
            'INTJ': '建筑师 - 理性、策略性、独立思考',
            'INTP': '思想家 - 逻辑性、分析性、好奇',
            'ENTJ': '指挥官 - 领导力、战略性、果断',
            'ENTP': '辩论家 - 创新性、适应性、聪明',
            'INFJ': '提倡者 - 理想主义、洞察力、奉献',
            'INFP': '调停者 - 价值驱动、创造力、和谐',
            'ENFJ': '主人公 - 魅力、利他主义、领导力',
            'ENFP': '竞选者 - 热情、创造力、社交性',
            'ISTJ': '物流师 - 负责任、可靠、实用',
            'ISFJ': '守护者 - 温暖、利他、可靠',
            'ESTJ': '总经理 - 高效、传统、可靠',
            'ESFJ': '执政官 - 和谐、务实、社交',
            'ISTP': '鉴赏家 - 灵活、冷静、实用',
            'ISFP': '探险家 - 艺术性、敏感性、自由精神',
            'ESTP': '企业家 - 精力充沛、冒险性、感知',
            'ESFP': '娱乐家 - 自发性、精力充沛、热情'
        }

        # 计算置信度
        confidence_scores = {
            'EI': abs(e_score - 5.5) * 20,  # 距离中心越远置信度越高
            'SN': abs(o_score - 5.5) * 20,
            'TF': abs(a_score - 5.5) * 20,
            'JP': abs(c_score - 5.5) * 20
        }

        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)

        return {
            'type': mbti_type,
            'description': mbti_descriptions.get(mbti_type, '未知类型'),
            'confidence': min(100, max(0, avg_confidence)),
            'dimension_scores': {
                'E/I': f'{e_score:.1f} ({"E" if e_score > 5.5 else "I"})',
                'S/N': f'{o_score:.1f} ({"N" if o_score > 5.5 else "S"})',
                'T/F': f'{a_score:.1f} ({"F" if a_score > 5.5 else "T"})',
                'J/P': f'{c_score:.1f} ({"J" if c_score > 5.5 else "P"})'
            }
        }

def main():
    analyzer = SimpleBigFiveAnalyzer()

    # 要分析的文件
    test_files = [
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214654.json',  # 基线
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214706.json',  # 轻度压力
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214717.json',  # 中度压力
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214728.json',  # 高度压力
        '.claude/skills/standalone-questionnaire/stress_test_results/answers_big_five_short_default_20251109_214812.json'   # 极度压力
    ]

    stress_conditions = ['基线', '轻度压力', '中度压力', '高度压力', '极度压力']

    print('🧠 大五人格压力测试分析')
    print('=' * 60)

    results = []

    for file_path, condition in zip(test_files, stress_conditions):
        print(f'\n{condition}条件分析:')
        print('-' * 30)

        if not os.path.exists(file_path):
            print(f'❌ 文件不存在: {file_path}')
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                test_data = json.load(f)

            analysis = analyzer.analyze_questionnaire(test_data)

            # 显示结果
            scores = analysis['big_five_scores']
            mbti = analysis['mbti_type']

            print(f'✅ 大五人格分数:')
            print(f'  开放性(O): {scores.get("openness", 0):.1f}')
            print(f'  尽责性(C): {scores.get("conscientiousness", 0):.1f}')
            print(f'  外向性(E): {scores.get("extraversion", 0):.1f}')
            print(f'  宜人性(A): {scores.get("agreeableness", 0):.1f}')
            print(f'  神经质(N): {scores.get("neuroticism", 0):.1f}')

            print(f'🎯 MBTI类型: {mbti["type"]} ({mbti["description"]})')
            print(f'置信度: {mbti["confidence"]:.1f}%')

            # 显示压力参数
            session = analysis['session_info']
            print(f'📋 压力参数: 情绪={session.get("emotional_stress", 0)}, '
                  f'认知陷阱="{session.get("cognitive_trap", "")}", '
                  f'上下文={session.get("context_tokens", 0)}tokens')

            results.append({
                'condition': condition,
                'big_five': scores,
                'mbti': mbti,
                'session': session
            })

        except Exception as e:
            print(f'❌ 处理失败: {e}')

    # 对比分析
    if len(results) >= 2:
        print(f'\n📊 压力条件对比分析')
        print('=' * 60)
        print(f"{'条件':<12} {'O':<6} {'C':<6} {'E':<6} {'A':<6} {'N':<6} {'MBTI':<8} {'置信度':<8}")
        print('-' * 70)

        for result in results:
            traits = result['big_five']
            mbti = result['mbti']
            print(f'{result["condition"]:<12} '
                  f'{traits.get("openness", 0):<6.1f} '
                  f'{traits.get("conscientiousness", 0):<6.1f} '
                  f'{traits.get("extraversion", 0):<6.1f} '
                  f'{traits.get("agreeableness", 0):<6.1f} '
                  f'{traits.get("neuroticism", 0):<6.1f} '
                  f'{mbti["type"]:<8} '
                  f'{mbti["confidence"]:<8.1f}')

        # 趋势分析
        print(f'\n📈 压力影响趋势分析:')
        print('-' * 30)

        baseline = results[0]['big_five']
        extreme = results[-1]['big_five']

        trait_names = {
            'openness': '开放性',
            'conscientiousness': '尽责性',
            'extraversion': '外向性',
            'agreeableness': '宜人性',
            'neuroticism': '神经质'
        }

        for trait in baseline:
            change = extreme.get(trait, 5.0) - baseline.get(trait, 5.0)
            trend = '↑' if change > 0.5 else '↓' if change < -0.5 else '→'
            print(f'{trait_names[trait]}: {baseline.get(trait, 5.0):.1f} → {extreme.get(trait, 5.0):.1f} ({trend} {change:+.1f})')

        # MBTI变化
        print(f'\n🎭 MBTI类型变化:')
        print('-' * 20)
        for result in results:
            mbti = result['mbti']
            print(f'{result["condition"]}: {mbti["type"]} (置信度: {mbti["confidence"]:.1f}%)')

    # 保存结果
    if results:
        output_file = 'results/big_five_stress_simple_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_time': '2025-11-09T22:40:00',
                'test_type': 'big_five_stress_analysis',
                'conditions_analyzed': len(results),
                'results': results
            }, f, ensure_ascii=False, indent=2)

        print(f'\n💾 分析结果已保存至: {output_file}')

if __name__ == "__main__":
    main()