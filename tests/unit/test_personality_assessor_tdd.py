#!/usr/bin/env python3
"""
TDD测试用例：personality-assessor技能评分缺陷检测

这个测试文件用于检测和验证personality-assessor技能的评分bug修复。
基于真实发现的案例：所有评分都返回3.0，无法区分实际的人格差异。
"""

import sys
import os
import json
import unittest
from datetime import datetime

# 添加技能路径
sys.path.append(os.path.join('.claude', 'skills', 'personality-assessor'))

try:
    from skill import PersonalityAssessor
except ImportError:
    print("❌ 无法导入PersonalityAssessor技能")
    sys.exit(1)


class TestPersonalityAssessorScoring(unittest.TestCase):
    """TDD测试类：personality-assessor评分缺陷检测"""

    def setUp(self):
        """测试设置：创建技能实例"""
        self.skill = PersonalityAssessor()

        # 真实测试案例：基于已发现的不同认知压力下的回答差异
        self.test_cases = {
            'baseline_high_extraversion': {
                'question': '我喜欢成为众人关注的焦点',
                'response': '是的，我非常喜欢在社交场合中成为焦点，这让我感到充满活力和自信。我会主动参加派对和聚会，享受与不同的人交流。',
                'expected_dimension': 'E',
                'expected_score_range': (6, 8),  # 高外向性
                'description': '基线条件：高外向性回答'
            },
            'semantic_low_extraversion': {
                'question': '我喜欢成为众人关注的焦点',
                'response': '不，我更喜欢安静的环境。过多的关注会让我感到不自在，我宁愿在小范围内与人深入交流。',
                'expected_dimension': 'E',
                'expected_score_range': (2, 4),  # 低外向性
                'description': '语义干扰：低外向性回答'
            },
            'paradox_high_conscientiousness': {
                'question': '我总是做事有条理',
                'response': '绝对如此。我每天都会制定详细的计划，每样东西都有固定的位置。我无法忍受混乱无序的状态。',
                'expected_dimension': 'C',
                'expected_score_range': (6, 8),  # 高尽责性
                'description': '悖论干扰：高尽责性回答'
            },
            'circular_low_agreeableness': {
                'question': '我总是信任他人',
                'response': '不是的。我觉得很难轻易相信别人，大多数人都有自私的动机。我需要很长时间才能建立信任。',
                'expected_dimension': 'A',
                'expected_score_range': (1, 3),  # 低宜人性
                'description': '循环论证干扰：低宜人性回答'
            }
        }

    def test_skill_initialization(self):
        """测试1：技能初始化是否成功"""
        print("\n🧪 测试1：技能初始化")
        self.assertIsNotNone(self.skill)
        print("✅ 技能初始化成功")

    def test_evaluation_session_creation(self):
        """测试2：评估会话创建"""
        print("\n🧪 测试2：评估会话创建")
        try:
            result = self.skill.start_evaluation_session(total_questions=4)
            self.assertIn('session_id', result)
            self.assertEqual(result['total_questions'], 4)
            print(f"✅ 评估会话创建成功: {result['session_id']}")
        except Exception as e:
            self.fail(f"评估会话创建失败: {e}")

    def test_single_question_evaluation(self):
        """测试3：单问题评估 - 检测是否所有评分都返回3.0"""
        print("\n🧪 测试3：单问题评估（检测3.0评分bug）")

        # 创建评估会话
        session_result = self.skill.start_evaluation_session(total_questions=2)

        scores_obtained = []

        # 测试两个不同的回答
        test_case_1 = self.test_cases['baseline_high_extraversion']
        test_case_2 = self.test_cases['semantic_low_extraversion']

        for i, test_case in enumerate([test_case_1, test_case_2], 1):
            print(f"  测试案例{i}: {test_case['description']}")

            try:
                result = self.skill.evaluate_single_question(
                    question_text=test_case['question'],
                    response_text=test_case['response'],
                    expected_dimension=test_case['expected_dimension']
                )

                # 检查结果结构
                self.assertIn('score', result)
                self.assertIn('dimension', result)
                self.assertIn('confidence', result)

                score = result['score']
                scores_obtained.append(score)

                print(f"    预期分数范围: {test_case['expected_score_range']}")
                print(f"    实际得分: {score}")

                # 关键测试：检查是否所有分数都是3.0（bug检测）
                if abs(score - 3.0) < 0.1:
                    print(f"    ⚠️ 警告：分数接近3.0，可能存在评分bug")
                else:
                    print(f"    ✅ 分数正常，不是3.0")

            except Exception as e:
                self.fail(f"单问题评估失败: {e}")

        # 关键断言：两个不同的回答应该得到不同的分数
        if len(scores_obtained) >= 2:
            score_diff = abs(scores_obtained[0] - scores_obtained[1])
            if score_diff < 0.1:
                print(f"  ❌ BUG检测：不同回答得到几乎相同的分数 ({scores_obtained[0]:.1f} vs {scores_obtained[1]:.1f})")
                self.fail("检测到评分bug：不同回答得到相同分数")
            else:
                print(f"  ✅ 通过：不同回答得到不同分数，差异为{score_diff:.1f}")

    def test_complete_evaluation_output(self):
        """测试4：完整评估输出 - 检查Big Five分数和MBTI映射"""
        print("\n🧪 测试4：完整评估输出")

        # 创建评估会话
        session_result = self.skill.start_evaluation_session(total_questions=4)

        # 评估所有测试案例
        for test_case in self.test_cases.values():
            try:
                result = self.skill.evaluate_single_question(
                    question_text=test_case['question'],
                    response_text=test_case['response'],
                    expected_dimension=test_case['expected_dimension']
                )
            except Exception as e:
                print(f"    评估失败: {e}")

        # 完成评估
        try:
            final_result = self.skill.complete_evaluation()

            # 检查结果结构
            self.assertIn('big_five_scores', final_result)
            self.assertIn('mbti_type', final_result)
            self.assertIn('belbin_role', final_result)

            big_five = final_result['big_five_scores']

            # 检查Big Five分数
            for dimension, score in big_five.items():
                if dimension in ['O', 'C', 'E', 'A', 'N']:
                    print(f"    {dimension}: {score}")

                    # 关键测试：检查是否所有分数都是3.0
                    if abs(score - 3.0) < 0.1:
                        print(f"      ⚠️ 警告：{dimension}维度分数为3.0，可能存在bug")

            # 检查是否有变化的分数
            non_three_scores = [score for score in big_five.values() if abs(score - 3.0) >= 0.1]
            if len(non_three_scores) == 0:
                print("  ❌ BUG检测：所有Big Five分数都是3.0")
                self.fail("检测到评分bug：所有Big Five分数都是3.0")
            else:
                print(f"  ✅ 通过：{len(non_three_scores)}个维度分数不是3.0")

            print(f"  MBTI类型: {final_result.get('mbti_type', 'Unknown')}")
            print(f"  Belbin角色: {final_result.get('belbin_role', 'Unknown')}")

        except Exception as e:
            self.fail(f"完整评估失败: {e}")

    def test_chinese_keyword_matching_bug(self):
        """测试5：中文关键词匹配bug - 检查是否能处理英文式AI回答"""
        print("\n🧪 测试5：中文关键词匹配bug检测")

        session_result = self.skill.start_evaluation_session(total_questions=2)

        # 测试中文关键词匹配
        chinese_responses = {
            'positive': '我非常喜欢，觉得很棒，非常同意',
            'negative': '我不喜欢，觉得不好，非常不同意'
        }

        english_style_responses = {
            'positive': 'Yes, I really like it and strongly agree',
            'negative': 'No, I dislike it and strongly disagree'
        }

        question = "我喜欢尝试新事物"

        # 测试中文回答
        try:
            result_chinese = self.skill.evaluate_single_question(
                question_text=question,
                response_text=chinese_responses['positive'],
                expected_dimension='O'
            )
            chinese_score = result_chinese['score']
            print(f"  中文回答得分: {chinese_score}")
        except Exception as e:
            print(f"  中文回答评估失败: {e}")
            chinese_score = None

        # 测试英文式回答
        try:
            result_english = self.skill.evaluate_single_question(
                question_text=question,
                response_text=english_style_responses['positive'],
                expected_dimension='O'
            )
            english_score = result_english['score']
            print(f"  英文式回答得分: {english_score}")
        except Exception as e:
            print(f"  英文式回答评估失败: {e}")
            english_score = None

        # 检查是否存在处理差异
        if chinese_score is not None and english_score is not None:
            if abs(chinese_score - english_score) > 1.0:
                print(f"  ⚠️ 发现中文/英文回答处理差异过大: {chinese_score:.1f} vs {english_score:.1f}")
                print("  可能存在关键词匹配问题")

            if english_score == 3.0 and chinese_score != 3.0:
                print("  ❌ BUG检测：英文式回答被错误评分为3.0")
                self.fail("检测到中文关键词匹配bug：英文式回答评分异常")

    def test_weighted_calculation_bug(self):
        """测试6：加权计算bug - 检查数学公式是否导致收敛到3.0"""
        print("\n🧪 测试6：加权计算bug检测")

        # 这个测试通过检查技能内部逻辑来发现数学问题
        session_result = self.skill.start_evaluation_session(total_questions=5)

        # 使用不同的回答模式
        varied_responses = [
            ("我完全同意", "非常强烈"),
            ("我有点同意", "比较同意"),
            ("我不确定", "中性"),
            ("我有点不同意", "不太同意"),
            ("我完全不同意", "强烈反对")
        ]

        question = "我对新体验持开放态度"

        scores = []
        for i, (response, intensity) in enumerate(varied_responses):
            try:
                result = self.skill.evaluate_single_question(
                    question_text=question,
                    response_text=f"{response}，{intensity}",
                    expected_dimension='O'
                )
                scores.append(result['score'])
                print(f"  回答{i+1} ({response[:10]}...): {result['score']}")
            except Exception as e:
                print(f"  回答{i+1}评估失败: {e}")

        # 检查分数分布
        if len(scores) >= 3:
            score_variance = max(scores) - min(scores)
            if score_variance < 0.5:
                print(f"  ❌ BUG检测：分数变化太小 ({score_variance:.2f})，可能存在加权计算问题")
                self.fail("检测到加权计算bug：分数变化异常小")
            else:
                print(f"  ✅ 通过：分数变化正常 ({score_variance:.2f})")


def run_tdd_tests():
    """运行TDD测试套件"""
    print("🧪 TDD驱动：personality-assessor技能评分缺陷检测")
    print("=" * 80)
    print("基于真实发现的bug：所有评分都返回3.0，无法区分人格差异")
    print()

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPersonalityAssessorScoring)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # 总结测试结果
    print("\n" + "=" * 80)
    print("📊 TDD测试结果总结:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n❌ 发现的bug:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")

    if result.errors:
        print("\n💥 测试错误:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n📈 测试通过率: {success_rate:.1f}%")

    if len(result.failures) > 0 or len(result.errors) > 0:
        print("\n🔧 需要修复的问题已识别，请查看上述失败测试")
        return False
    else:
        print("\n🎉 所有测试通过，技能评分功能正常！")
        return True


if __name__ == '__main__':
    success = run_tdd_tests()
    sys.exit(0 if success else 1)