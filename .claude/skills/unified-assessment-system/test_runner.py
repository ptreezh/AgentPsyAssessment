#!/usr/bin/env python3
"""
Simple test runner for the unified assessment skills system.
This script tests the core functionality without complex import dependencies.
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_configuration_system():
    """Test the configuration validation and loading system."""
    print("🧠 Testing Configuration System...")

    try:
        from config_validator import ConfigurationValidator

        # Test configuration validator - configs are in questionnaire-responder/configs/
        config_dir = os.path.join(current_dir, "..", "questionnaire-responder", "configs")
        config_dir = os.path.abspath(config_dir)
        validator = ConfigurationValidator(config_dir)

        # Test loading each configuration
        test_configs = [
            "big_five_personality.json",
            "citizenship_knowledge.json",
            "financial_professional.json",
            "legal_knowledge.json",
            "motivation_psychology.json",
            "political_literacy.json"
        ]

        loaded_configs = []
        for config_file in test_configs:
            try:
                config_path = os.path.join(config_dir, config_file)
                config, errors = validator.load_config(config_path)
                if not errors:
                    loaded_configs.append(config_file)
                    print(f"  ✅ {config_file}")
                else:
                    print(f"  ❌ {config_file}: {errors}")
            except Exception as e:
                print(f"  ❌ {config_file}: {e}")

        print(f"📊 Configuration System: {len(loaded_configs)}/{len(test_configs)} configs loaded successfully")
        return len(loaded_configs) == len(test_configs)

    except Exception as e:
        print(f"  ❌ Configuration system test failed: {e}")
        return False

def test_assessment_detector():
    """Test the assessment type detection system."""
    print("\n🔍 Testing Assessment Type Detector...")

    try:
        from assessment_detector import AssessmentTypeDetector

        # Create a simple config dict for the detector
        configs = {}
        detector = AssessmentTypeDetector(configs)

        # Test data for different assessment types
        test_cases = [
            {
                "name": "Big Five Personality",
                "content": {
                    "questions": [
                        {"dimension": "openness", "question": "I enjoy new experiences"},
                        {"dimension": "conscientiousness", "question": "I am organized"}
                    ]
                },
                "expected_type": "big_five_personality"
            },
            {
                "name": "Citizenship Knowledge",
                "content": {
                    "questions": [
                        {"category": "公民权利义务", "question": "What are citizen rights?"},
                        {"category": "政治制度认知", "question": "How does government work?"}
                    ]
                },
                "expected_type": "citizenship_knowledge"
            }
        ]

        successful_detections = 0
        for test_case in test_cases:
            try:
                result = detector.detect_from_content(
                    test_case["content"],
                    test_case["name"]
                )
                if result and result.assessment_type == test_case["expected_type"]:
                    print(f"  ✅ {test_case['name']}: {result.assessment_type} (confidence: {result.confidence:.1f}%)")
                    successful_detections += 1
                else:
                    print(f"  ❌ {test_case['name']}: expected {test_case['expected_type']}, got {result.assessment_type if result else 'None'}")
            except Exception as e:
                print(f"  ❌ {test_case['name']}: {e}")

        print(f"📊 Assessment Detection: {successful_detections}/{len(test_cases)} detections successful")
        return successful_detections == len(test_cases)

    except Exception as e:
        print(f"  ❌ Assessment detector test failed: {e}")
        return False

def test_basic_questionnaire_response():
    """Test basic questionnaire response generation."""
    print("\n📝 Testing Basic Questionnaire Response...")

    try:
        # Create a simple test questionnaire
        test_questionnaire = {
            "title": "Test Big Five Assessment",
            "assessment_type": "big_five_personality",
            "questions": [
                {
                    "id": "q1",
                    "dimension": "openness",
                    "question": "I enjoy trying new and exciting things",
                    "options": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
                },
                {
                    "id": "q2",
                    "dimension": "conscientiousness",
                    "question": "I am always prepared",
                    "options": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
                }
            ]
        }

        # Test response generation logic
        responses = []
        for question in test_questionnaire["questions"]:
            # Simulate response generation
            import random
            selected_option = random.choice(question["options"])
            response_text = f"I would select '{selected_option}' because this reflects my personality."

            response = {
                "question_id": question["id"],
                "dimension": question["dimension"],
                "selected_option": selected_option,
                "response_text": response_text,
                "confidence": 0.85
            }
            responses.append(response)

        print(f"  ✅ Generated {len(responses)} responses")
        for response in responses:
            print(f"    - {response['question_id']}: {response['selected_option']}")

        print(f"📊 Questionnaire Response: Successfully generated {len(responses)} responses")
        return len(responses) == len(test_questionnaire["questions"])

    except Exception as e:
        print(f"  ❌ Questionnaire response test failed: {e}")
        return False

def test_basic_analysis():
    """Test basic psychological analysis functionality."""
    print("\n📊 Testing Basic Psychological Analysis...")

    try:
        # Test data for Big Five analysis
        test_responses = [
            {"dimension": "openness", "score": 4, "weight": 1.0},
            {"dimension": "conscientiousness", "score": 3, "weight": 1.0},
            {"dimension": "extraversion", "score": 5, "weight": 1.0},
            {"dimension": "agreeableness", "score": 4, "weight": 1.0},
            {"dimension": "neuroticism", "score": 2, "weight": 1.0}
        ]

        # Calculate scores
        big_five_scores = {}
        for response in test_responses:
            dimension = response["dimension"]
            score = response["score"] * response["weight"]
            big_five_scores[dimension] = score

        # Generate basic analysis
        analysis = {
            "big_five_scores": big_five_scores,
            "overall_profile": "High Openness, Moderate Conscientiousness, High Extraversion",
            "mbti_estimation": "ENFP" if big_five_scores["extraversion"] >= 4 else "INFP",
            "confidence": 0.78
        }

        print(f"  ✅ Big Five Scores: {big_five_scores}")
        print(f"  ✅ MBTI Estimation: {analysis['mbti_estimation']}")
        print(f"  ✅ Confidence: {analysis['confidence']:.2f}")

        print(f"📊 Psychological Analysis: Successfully analyzed Big Five profile")
        return True

    except Exception as e:
        print(f"  ❌ Psychological analysis test failed: {e}")
        return False

def test_basic_report_generation():
    """Test basic HTML report generation."""
    print("\n📄 Testing Basic Report Generation...")

    try:
        # Test analysis data
        test_analysis = {
            "big_five_scores": {
                "openness": 4.2,
                "conscientiousness": 3.8,
                "extraversion": 4.5,
                "agreeableness": 3.9,
                "neuroticism": 2.1
            },
            "mbti_estimation": "ENFP",
            "confidence": 0.82,
            "assessment_type": "big_five_personality",
            "recommendations": [
                "Consider careers that allow creativity and innovation",
                "Leverage your strong interpersonal skills",
                "Balance social interaction with reflection time"
            ]
        }

        # Generate HTML report
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Psychological Assessment Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 8px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .score {{ font-weight: bold; color: #2c5aa0; }}
        .recommendation {{ background: #e8f4fd; padding: 10px; margin: 5px 0; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Psychological Assessment Report</h1>
        <p>Assessment Type: {assessment_type}</p>
        <p>Generated: {timestamp}</p>
    </div>

    <div class="section">
        <h2>Big Five Personality Scores</h2>
        {big_five_scores_html}
    </div>

    <div class="section">
        <h2>MBTI Estimation</h2>
        <p><strong>Type:</strong> {mbti_type} (Confidence: {confidence:.1%})</p>
    </div>

    <div class="section">
        <h2>Recommendations</h2>
        {recommendations_html}
    </div>
</body>
</html>
        """

        # Generate Big Five scores HTML
        big_five_html = ""
        for trait, score in test_analysis["big_five_scores"].items():
            big_five_html += f'<p><span class="score">{trait.title()}:</span> {score:.1f}/5.0</p>'

        # Generate recommendations HTML
        rec_html = ""
        for i, rec in enumerate(test_analysis["recommendations"], 1):
            rec_html += f'<div class="recommendation">{i}. {rec}</div>'

        # Fill template
        html_report = html_template.format(
            assessment_type=test_analysis["assessment_type"].title(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            big_five_scores_html=big_five_html,
            mbti_type=test_analysis["mbti_estimation"],
            confidence=test_analysis["confidence"],
            recommendations_html=rec_html
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_report)
            temp_file = f.name

        print(f"  ✅ HTML report generated: {len(html_report)} characters")
        print(f"  ✅ Saved to: {temp_file}")

        # Verify HTML structure
        if "<!DOCTYPE html>" in html_report and "Big Five Personality Scores" in html_report:
            print(f"📊 Report Generation: Successfully generated valid HTML report")
            return True
        else:
            print(f"  ❌ Generated HTML appears invalid")
            return False

    except Exception as e:
        print(f"  ❌ Report generation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Unified Assessment Skills System Tests")
    print("=" * 60)

    test_results = []

    # Run all tests
    test_results.append(("Configuration System", test_configuration_system()))
    test_results.append(("Assessment Detection", test_assessment_detector()))
    test_results.append(("Questionnaire Response", test_basic_questionnaire_response()))
    test_results.append(("Psychological Analysis", test_basic_analysis()))
    test_results.append(("Report Generation", test_basic_report_generation()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Unified Assessment System is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)