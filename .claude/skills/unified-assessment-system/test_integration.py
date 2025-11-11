#!/usr/bin/env python3
"""
Integration tests for the unified assessment skills system.

This module provides comprehensive integration tests for the complete workflow
including questionnaire response generation, evaluation analysis, and report generation.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_validator import ConfigurationValidator
from assessment_detector import AssessmentTypeDetector
from unified_questionnaire_responder import UnifiedQuestionnaireResponder
from unified_psychological_analyzer import UnifiedPsychologicalAnalyzer
from unified_report_generator import UnifiedReportGenerator
from skill_base import AssessmentType


class IntegrationTester:
    """Integration tester for unified assessment system"""

    def __init__(self):
        """Initialize the integration tester"""
        self.config_dir = "../questionnaire-responder/configs"
        self.validator = ConfigurationValidator(self.config_dir)
        self.detector = AssessmentTypeDetector(self.validator.load_all_configs())
        self.questionnaire_responder = UnifiedQuestionnaireResponder(self.config_dir)
        self.psychological_analyzer = UnifiedPsychologicalAnalyzer(self.config_dir)
        self.report_generator = UnifiedReportGenerator(self.config_dir)
        self.temp_dir = tempfile.mkdtemp(prefix="unified_assessment_test_")

    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_workflow(self, assessment_type: AssessmentType, persona: str = "ENFJ"):
        """
        Test complete workflow from questionnaire to report

        Args:
            assessment_type: Assessment type to test
            persona: Persona type to use

        Returns:
            dict: Test results
        """
        test_results = {
            "assessment_type": assessment_type.value,
            "persona": persona,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }

        try:
            # Step 1: Create test questionnaire
            questionnaire_file = self._create_test_questionnaire(assessment_type)
            test_results["tests"]["questionnaire_creation"] = {"status": "success", "file": questionnaire_file}

            # Step 2: Generate responses
            responses_result = self.questionnaire_responder.process_request({
                "questionnaire_file": questionnaire_file,
                "persona": persona,
                "assessment_type": assessment_type.value,
                "parameters": {
                    "stress_level": 0.3,
                    "temperature": 0.7,
                    "cognitive_interference": 0.2
                }
            })

            if responses_result.success:
                test_results["tests"]["response_generation"] = {
                    "status": "success",
                    "total_questions": responses_result.data["total_questions"],
                    "confidence": responses_result.confidence
                }

                # Step 3: Analyze responses
                session_result = self.psychological_analyzer.process_request({
                    "action": "start",
                    "assessment_type": assessment_type.value,
                    "total_questions": responses_result.data["total_questions"]
                })

                if session_result.success:
                    session_id = session_result.data["session_id"]
                    test_results["tests"]["session_creation"] = {"status": "success", "session_id": session_id}

                    # Evaluate each response
                    evaluation_results = []
                    for response in responses_result.data["responses"]:
                        eval_result = self.psychological_analyzer.process_request({
                            "action": "evaluate",
                            "session_id": session_id,
                            "question": {"id": response["question_id"]},
                            "response": response
                        })

                        if eval_result.success:
                            evaluation_results.append(eval_result.data["evaluation"])

                    test_results["tests"]["response_evaluation"] = {
                        "status": "success",
                        "evaluated_responses": len(evaluation_results)
                    }

                    # Step 4: Complete evaluation
                    completion_result = self.psychological_analyzer.process_request({
                        "action": "complete",
                        "session_id": session_id
                    })

                    if completion_result.success:
                        test_results["tests"]["evaluation_completion"] = {
                            "status": "success",
                            "comprehensive_analysis": completion_result.data.get("comprehensive_analysis", {}),
                            "confidence": completion_result.confidence
                        }

                        # Step 5: Generate report
                        report_result = self.report_generator.process_request({
                            "evaluation_data": completion_result.data,
                            "assessment_type": assessment_type.value,
                            "output_path": os.path.join(self.temp_dir, f"test_report_{assessment_type.value}.html")
                        })

                        if report_result.success:
                            test_results["tests"]["report_generation"] = {
                                "status": "success",
                                "report_path": report_result.data["report_path"],
                                "file_exists": os.path.exists(report_result.data["report_path"])
                            }

                            # Validate report file
                            if os.path.exists(report_result.data["report_path"]):
                                with open(report_result.data["report_path"], 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    test_results["tests"]["report_validation"] = {
                                        "status": "success",
                                        "file_size": len(content),
                                        "has_html_structure": "<html" in content.lower(),
                                        "has_css": "style>" in content.lower(),
                                        "has_script": "<script" in content.lower()
                                    }

            else:
                test_results["tests"]["response_generation"] = {"status": "failed", "error": responses_result.error_message}

        except Exception as e:
            test_results["error"] = str(e)

        return test_results

    def _create_test_questionnaire(self, assessment_type: AssessmentType) -> str:
        """Create test questionnaire for given assessment type"""
        if assessment_type == AssessmentType.BIG_FIVE_PERSONALITY:
            return self._create_big_five_questionnaire()
        elif assessment_type == AssessmentType.CITIZENSHIP_KNOWLEDGE:
            return self._create_citizenship_questionnaire()
        elif assessment_type == AssessmentType.FINANCIAL_PROFESSIONAL:
            return self._create_financial_questionnaire()
        elif assessment_type == AssessmentType.LEGAL_KNOWLEDGE:
            return self._create_legal_questionnaire()
        elif assessment_type == AssessmentType.MOTIVATION_PSYCHOLOGY:
            return self._create_motivation_questionnaire()
        elif assessment_type == AssessmentType.POLITICAL_LITERACY:
            return self._create_political_questionnaire()
        else:
            raise ValueError(f"Unsupported assessment type: {assessment_type}")

    def _create_big_five_questionnaire(self) -> str:
        """Create Big Five personality test questionnaire"""
        questions = [
            {
                "id": "q1",
                "text": "我认为自己是一个富有创造力的人",
                "dimension": "openness",
                "scale": [1, 2, 3, 4, 5]
            },
            {
                "id": "q2",
                "text": "我总是认真完成自己的任务",
                "dimension": "conscientiousness",
                "scale": [1, 2, 3, 4, 5]
            },
            {
                "id": "q3",
                "text": "我喜欢在人群中成为关注的焦点",
                "dimension": "extraversion",
                "scale": [1, 2, 3, 4, 5]
            },
            {
                "id": "q4",
                "text": "我尽量避免与他人发生冲突",
                "dimension": "agreeableness",
                "scale": [1, 2, 3, 4, 5]
            },
            {
                "id": "q5",
                "text": "我经常感到紧张和焦虑",
                "dimension": "neuroticism",
                "scale": [1, 2, 3, 4, 5]
            }
        ]

        questionnaire = {
            "title": "大五人格测评问卷",
            "description": "基于大五人格模型的性格特质评估",
            "assessment_type": "big_five_personality",
            "questions": questions,
            "dimensions": ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
        }

        questionnaire_file = os.path.join(self.temp_dir, "big_five_test.json")
        with open(questionnaire_file, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)

        return questionnaire_file

    def _create_citizenship_questionnaire(self) -> str:
        """Create citizenship knowledge test questionnaire"""
        questions = [
            {
                "id": "q1",
                "text": "以下哪项不是公民的基本权利？",
                "options": ["言论自由", "宗教自由", "集会自由", "服从命令"],
                "correct_answer": 3,
                "domain": "rights"
            },
            {
                "id": "q2",
                "text": "民主制度的核心原则是什么？",
                "options": ["权力集中", "多数决定", "权力制衡", "单一领导"],
                "correct_answer": 2,
                "domain": "democracy"
            },
            {
                "id": "q3",
                "text": "公民的基本义务包括什么？",
                "options": ["纳税义务", "服从法律", "维护国家统一", "以上都是"],
                "correct_answer": 3,
                "domain": "responsibilities"
            }
        ]

        questionnaire = {
            "title": "公民知识测评问卷",
            "description": "评估公民基本权利义务和民主制度理解",
            "assessment_type": "citizenship_knowledge",
            "questions": questions
        }

        questionnaire_file = os.path.join(self.temp_dir, "citizenship_test.json")
        with open(questionnaire_file, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)

        return questionnaire_file

    def _create_financial_questionnaire(self) -> str:
        """Create financial professional test questionnaire"""
        questions = [
            {
                "id": "q1",
                "scenario": "一位客户希望投资高风险高收益产品，作为金融顾问你会如何建议？",
                "context": "investment_advice",
                "competency_area": "risk_management",
                "criteria": ["professionalism", "risk_assessment", "communication"]
            },
            {
                "id": "q2",
                "scenario": "银行发现可疑交易，应该如何处理？",
                "context": "compliance_procedure",
                "competency_area": "regulatory_compliance",
                "criteria": ["professionalism", "compliance", "procedural_knowledge"]
            },
            {
                "id": "q3",
                "scenario": "客户询问不同投资产品的风险和收益特征",
                "context": "product_knowledge",
                "competency_area": "product_expertise",
                "criteria": ["professionalism", "analysis", "communication"]
            }
        ]

        questionnaire = {
            "title": "金融专业能力评估问卷",
            "description": "评估金融专业知识和实务能力",
            "assessment_type": "financial_professional",
            "questions": questions
        }

        questionnaire_file = os.path.join(self.temp_dir, "financial_test.json")
        with open(questionnaire_file, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)

        return questionnaire_file

    def _create_legal_questionnaire(self) -> str:
        """Create legal knowledge test questionnaire"""
        questions = [
            {
                "id": "q1",
                "case": "当事人A与B签订合同，但A声称受到胁迫，如何处理？",
                "domain": "contract_law",
                "criteria": ["legal_analysis", "professional_judgment", "procedural_knowledge"]
            },
            {
                "id": "q2",
                "case": "公司高管涉嫌内幕交易，法律后果是什么？",
                "domain": "securities_law",
                "criteria": ["legal_knowledge", "compliance_awareness", "ethical_reasoning"]
            },
            {
                "id": "q3",
                "case": "员工在工作中受伤，工伤认定标准是什么？",
                "domain": "labor_law",
                "criteria": ["legal_knowledge", "practical_application", "protection_awareness"]
            }
        ]

        questionnaire = {
            "title": "法律知识评估问卷",
            "description": "评估法律专业知识和实务能力",
            "assessment_type": "legal_knowledge",
            "questions": questions
        }

        questionnaire_file = os.path.join(self.temp_dir, "legal_test.json")
        with open(questionnaire_file, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)

        return questionnaire_file

    def _create_motivation_questionnaire(self) -> str:
        """Create motivation psychology test questionnaire"""
        questions = [
            {
                "id": "q1",
                "situation": "面对一个具有挑战性但可能失败的项目",
                "focus": "achievement_motivation",
                "criteria": ["goal_orientation", "risk_tolerance", "persistence"]
            },
            {
                "id": "q2",
                "situation": "需要在团队中担任领导角色",
                "focus": "power_motivation",
                "criteria": ["leadership_desire", "influence_seeking", "responsibility_taking"]
            },
            {
                "id": "q3",
                "situation": "可以选择独立工作或团队协作",
                "focus": "affiliation_motivation",
                "criteria": ["social_preference", "team_orientation", "harmony_seeking"]
            }
        ]

        questionnaire = {
            "title": "动机心理学分析问卷",
            "description": "评估内在动机结构和驱动因素",
            "assessment_type": "motivation_psychology",
            "questions": questions
        }

        questionnaire_file = os.path.join(self.temp_dir, "motivation_test.json")
        with open(questionnaire_file, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)

        return questionnaire_file

    def _create_political_questionnaire(self) -> str:
        """Create political literacy test questionnaire"""
        questions = [
            {
                "id": "q1",
                "issue": "如何评价当前的国际贸易政策对国家发展的影响？",
                "aspect": "critical_analysis",
                "criteria": ["multiple_perspectives", "evidence_reasoning", "structured_thinking"]
            },
            {
                "id": "q2",
                "issue": "如何平衡经济发展与环境保护之间的关系？",
                "aspect": "policy_analysis",
                "criteria": ["tradeoff_analysis", "stakeholder_consideration", "solution_proposal"]
            },
            {
                "id": "q3",
                "issue": "公民在社会发展中应该承担什么责任？",
                "aspect": "civic_responsibility",
                "criteria": ["social_consciousness", "participation_willingness", "community_contribution"]
            }
        ]

        questionnaire = {
            "title": "政治素养分析问卷",
            "description": "评估政治认知水平和批判性思维能力",
            "assessment_type": "political_literacy",
            "questions": questions
        }

        questionnaire_file = os.path.join(self.temp_dir, "political_test.json")
        with open(questionnaire_file, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)

        return questionnaire_file

    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 开始统一评估系统集成测试...")
        print("=" * 60)

        test_types = [
            (AssessmentType.BIG_FIVE_PERSONALITY, "INTJ"),
            (AssessmentType.CITIZENSHIP_KNOWLEDGE, "ENFJ"),
            (AssessmentType.FINANCIAL_PROFESSIONAL, "ENTJ"),
            (AssessmentType.LEGAL_KNOWLEDGE, "ISTJ"),
            (AssessmentType.MOTIVATION_PSYCHOLOGY, "ENFP"),
            (AssessmentType.POLITICAL_LITERACY, "INFJ")
        ]

        results = []
        success_count = 0

        for assessment_type, persona in test_types:
            print(f"\n📋 测试 {assessment_type.value} (Persona: {persona})")
            print("-" * 40)

            try:
                result = self.test_complete_workflow(assessment_type, persona)
                results.append(result)

                # Check if all tests passed
                all_passed = all(
                    test.get("status") == "success"
                    for test in result.get("tests", {}).values()
                )

                if all_passed:
                    success_count += 1
                    print(f"✅ {assessment_type.value} 测试通过")
                else:
                    failed_tests = [name for name, test in result.get("tests", {}).items()
                                    if test.get("status") != "success"]
                    print(f"❌ {assessment_type.value} 测试失败: {', '.join(failed_tests)}")

                # Show key metrics
                if "response_generation" in result["tests"]:
                    rg = result["tests"]["response_generation"]
                    print(f"   📊 生成回答: {rg.get('total_questions', 0)} 题, 置信度: {rg.get('confidence', 0):.2f}")

                if "report_generation" in result["tests"]:
                    rg = result["tests"]["report_generation"]
                    if rg.get("file_exists"):
                        print(f"   📄 报告生成: {rg.get('report_path', 'N/A')}")

            except Exception as e:
                print(f"❌ {assessment_type.value} 测试异常: {e}")
                results.append({
                    "assessment_type": assessment_type.value,
                    "persona": persona,
                    "error": str(e)
                })

        # Summary
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"总测试数: {len(results)}")
        print(f"通过测试数: {success_count}")
        print(f"成功率: {success_count/len(results)*100:.1f}%")

        if success_count == len(results):
            print("\n🎉 所有集成测试通过！统一评估系统运行正常。")
        else:
            print(f"\n⚠️  {len(results) - success_count} 个测试失败，需要进一步调试。")

        return results

    def test_component_isolation(self):
        """Test individual components in isolation"""
        print("\n🔧 组件隔离测试...")
        print("=" * 40)

        # Test configuration validator
        print("📋 测试配置验证器...")
        try:
            configs = self.validator.load_all_configs()
            print(f"✅ 成功加载 {len(configs)} 个配置文件")
        except Exception as e:
            print(f"❌ 配置验证器测试失败: {e}")

        # Test assessment detector
        print("📋 测评类型检测器...")
        try:
            test_content = {"title": "Big Five Personality Test", "dimensions": ["openness", "conscientiousness"]}
            detection = self.detector.detect_from_content(test_content, "big_five_test.json")
            print(f"✅ 检测结果: {detection.assessment_type}, 置信度: {detection.confidence:.2f}")
        except Exception as e:
            print(f"❌ 检测器测试失败: {e}")

        # Test skill registration
        print("📋 测试技能注册...")
        try:
            from skill_base import SkillFactory
            registered_skills = SkillFactory.list_skills()
            expected_skills = ["unified_questionnaire_responder", "unified_psychological_analyzer", "unified_report_generator"]

            for skill in expected_skills:
                if skill in registered_skills:
                    print(f"✅ 技能 {skill} 已注册")
                else:
                    print(f"❌ 技能 {skill} 未注册")
        except Exception as e:
            print(f"❌ 技能注册测试失败: {e}")


def main():
    """Main test runner"""
    tester = IntegrationTester()

    try:
        # Run component isolation tests
        tester.test_component_isolation()

        # Run complete integration tests
        results = tester.run_all_tests()

        # Save test results
        results_file = os.path.join(tester.temp_dir, "integration_test_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n📄 详细测试结果已保存到: {results_file}")

        return 0 if all(r.get("error") is None for r in results) else 1

    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        return 1

    finally:
        tester.cleanup()


if __name__ == "__main__":
    import sys
    sys.exit(main())