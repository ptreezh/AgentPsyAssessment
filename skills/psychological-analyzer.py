#!/usr/bin/env python3
"""
Psychological Assessment Skill for Claude Code

A simple, practical skill implementation that analyzes psychological assessment data
and generates personality insights based on Big Five and MBTI models.

Author: ptreezh <3061176@qq.com>
License: MIT License
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics


class PsychologicalAnalyzer:
    """Simple psychological assessment analyzer for Claude Code"""

    def __init__(self):
        self.big_five_questions = {
            'O': ['openness', 'creativity', 'intellectual_curiosity'],
            'C': ['conscientiousness', 'organization', 'discipline'],
            'E': ['extraversion', 'social_activity', 'assertiveness'],
            'A': ['agreeableness', 'cooperation', 'empathy'],
            'N': ['neuroticism', 'anxiety', 'emotional_stability']
        }

    def analyze_responses(self, responses: List[Dict]) -> Dict[str, float]:
        """Calculate Big Five scores from responses"""
        scores = {'O': [], 'C': [], 'E': [], 'A': [], 'N': []}

        for response in responses:
            question_id = response.get('question_id', '')
            answer = response.get('answer', 0)

            # Determine which dimension this question belongs to
            dimension = self._get_question_dimension(question_id)
            if dimension:
                scores[dimension].append(answer)

        # Calculate average scores for each dimension
        final_scores = {}
        for dim, values in scores.items():
            if values:
                final_scores[dim] = round(statistics.mean(values), 2)
            else:
                final_scores[dim] = 3.0  # Default to neutral

        return final_scores

    def _get_question_dimension(self, question_id: str) -> Optional[str]:
        """Determine which Big Five dimension a question belongs to"""
        # Simple mapping based on question ID patterns
        if question_id.startswith(('O', 'Openness')):
            return 'O'
        elif question_id.startswith(('C', 'Conscientious')):
            return 'C'
        elif question_id.startswith(('E', 'Extraversion')):
            return 'E'
        elif question_id.startswith(('A', 'Agreeableness')):
            return 'A'
        elif question_id.startswith(('N', 'Neuroticism')):
            return 'N'
        return None

    def infer_mbti_type(self, big_five_scores: Dict[str, float]) -> str:
        """Simple MBTI type inference from Big Five scores"""
        # E/I from Extraversion
        ei = 'E' if big_five_scores.get('E', 3.0) > 3.5 else 'I'

        # S/N from Openness (higher openness suggests N)
        sn = 'N' if big_five_scores.get('O', 3.0) > 3.5 else 'S'

        # T/F from Agreeableness (higher agreeableness suggests F)
        tf = 'F' if big_five_scores.get('A', 3.0) > 3.5 else 'T'

        # J/P from Conscientiousness (higher conscientiousness suggests J)
        jp = 'J' if big_five_scores.get('C', 3.0) > 3.5 else 'P'

        return f"{ei}{sn}{tf}{jp}"

    def generate_insights(self, big_five_scores: Dict[str, float], mbti_type: str) -> List[str]:
        """Generate personality insights from scores"""
        insights = []

        # Openness insights
        if big_five_scores.get('O', 0) > 4.0:
            insights.append("高开放性表明富有创造力和好奇心，喜欢尝试新事物")
        elif big_five_scores.get('O', 0) < 2.5:
            insights.append("较低开放性表明偏好传统和实用，喜欢熟悉的环境")

        # Conscientiousness insights
        if big_five_scores.get('C', 0) > 4.0:
            insights.append("高尽责性表明有组织性和可靠性，适合需要计划性的工作")
        elif big_five_scores.get('C', 0) < 2.5:
            insights.append("较低尽责性表明更灵活适应性，但可能需要提升组织能力")

        # Extraversion insights
        if big_five_scores.get('E', 0) > 4.0:
            insights.append("高外向性表明善于社交，在团队环境中表现良好")
        elif big_five_scores.get('E', 0) < 2.5:
            insights.append("较低外向性表明偏好独立工作，深度思考能力强")

        # Add MBTI-specific insight
        mbti_descriptions = {
            'ENFJ': '天生的领导者和导师，善于激励他人',
            'INTJ': '战略性思考者，追求效率和改进',
            'ESFP': '充满活力的表演者，享受当下',
            'ISTJ': '可靠的组织者，重视传统和责任'
        }

        if mbti_type in mbti_descriptions:
            insights.append(f"MBTI类型 {mbti_type}: {mbti_descriptions[mbti_type]}")

        return insights

    def calculate_confidence(self, responses: List[Dict]) -> float:
        """Calculate confidence score based on data quality"""
        if not responses:
            return 0.0

        # Basic confidence based on number of responses
        response_count = len(responses)
        if response_count >= 50:
            return 0.9
        elif response_count >= 30:
            return 0.8
        elif response_count >= 10:
            return 0.7
        else:
            return 0.5

    def analyze_assessment(self, data: Dict) -> Dict:
        """Main analysis function"""
        responses = data.get('responses', [])
        respondent_id = data.get('respondent_id', 'unknown')

        # Calculate scores
        big_five_scores = self.analyze_responses(responses)

        # Map dimension codes to full names
        dimension_names = {
            'O': 'openness',
            'C': 'conscientiousness',
            'E': 'extraversion',
            'A': 'agreeableness',
            'N': 'neuroticism'
        }

        # Create full score mapping
        full_scores = {}
        for code, score in big_five_scores.items():
            full_scores[dimension_names[code]] = score

        # Infer MBTI type
        mbti_type = self.infer_mbti_type(big_five_scores)

        # Generate insights
        insights = self.generate_insights(big_five_scores, mbti_type)

        # Calculate confidence
        confidence = self.calculate_confidence(responses)

        return {
            'respondent_id': respondent_id,
            'big_five_scores': full_scores,
            'mbti_type': mbti_type,
            'confidence_score': round(confidence, 2),
            'key_insights': insights,
            'analysis_summary': {
                'total_responses': len(responses),
                'analysis_date': str(Path.cwd()),
                'data_quality': 'good' if confidence > 0.7 else 'limited'
            }
        }


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Psychological Assessment Analyzer')
    parser.add_argument('input_file', help='JSON file containing assessment data')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        # Read input file
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Analyze data
        analyzer = PsychologicalAnalyzer()
        results = analyzer.analyze_assessment(data)

        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            if args.verbose:
                print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2, ensure_ascii=False))

    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in input file")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()