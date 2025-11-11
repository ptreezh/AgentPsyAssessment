#!/usr/bin/env python3
"""
Test script for the assessment type detector.
"""

import json
from config_validator import ConfigurationValidator
from assessment_detector import AssessmentTypeDetector


def test_assessment_detector():
    """Test the assessment type detector with sample data."""

    # Load configurations
    config_validator = ConfigurationValidator("../questionnaire-responder/configs")
    configs = config_validator.load_all_configs()

    print(f"Loaded {len(configs)} configurations:")
    for key in configs.keys():
        print(f"  - {key}")
    print()

    # Create detector
    detector = AssessmentTypeDetector(configs)

    # Test with Big Five personality sample
    big_five_sample = {
        "title": "Big Five Personality Assessment",
        "questions": [
            {
                "id": "q1",
                "text": "I see myself as someone who is talkative",
                "dimension": "extraversion",
                "scale": [1, 2, 3, 4, 5]
            },
            {
                "id": "q2",
                "text": "I see myself as someone who is depressed, blue",
                "dimension": "neuroticism",
                "scale": [1, 2, 3, 4, 5]
            }
        ],
        "dimensions": ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"],
        "scoring_method": "rating_scale"
    }

    result = detector.detect_from_content(big_five_sample, "big_five_personality_test.json")
    print("Big Five Test Detection:")
    print(f"  Type: {result.assessment_type}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Method: {result.method}")
    print(f"  Details: {result.details}")
    print()

    # Test with citizenship knowledge sample
    citizenship_sample = {
        "title": "公民知识测评",
        "questions": [
            {
                "id": "q1",
                "text": "公民的基本权利包括哪些？",
                "options": ["言论自由", "宗教自由", "集会自由", "以上都是"],
                "correct_answer": 3
            },
            {
                "id": "q2",
                "text": "民主制度的核心原则是什么？",
                "options": ["权力制衡", "多数决定", "少数服从多数", "以上都重要"],
                "correct_answer": 3
            }
        ],
        "assessment_focus": ["citizenship_rights", "democratic_participation", "civic_responsibilities"]
    }

    result = detector.detect_from_content(citizenship_sample, "citizenship_test.json")
    print("Citizenship Knowledge Detection:")
    print(f"  Type: {result.assessment_type}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Method: {result.method}")
    print(f"  Details: {result.details}")
    print()

    # Test with financial professional sample
    financial_sample = {
        "title": "金融专业能力评估",
        "scenarios": [
            {
                "id": "s1",
                "description": "客户希望投资高风险高收益产品，作为金融顾问你会如何建议？",
                "context": "investment_advice",
                "risk_factors": ["market_risk", "liquidity_risk", "concentration_risk"]
            },
            {
                "id": "s2",
                "description": "银行发现可疑交易，应该如何处理？",
                "context": "compliance_procedure",
                "regulations": ["AML", "KYC", "reporting_requirements"]
            }
        ],
        "competency_areas": ["risk_management", "compliance", "investment_analysis", "customer_service"]
    }

    result = detector.detect_from_content(financial_sample, "financial_assessment.json")
    print("Financial Professional Detection:")
    print(f"  Type: {result.assessment_type}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Method: {result.method}")
    print(f"  Details: {result.details}")
    print()

    print("✅ Assessment type detector test completed successfully!")


if __name__ == "__main__":
    test_assessment_detector()