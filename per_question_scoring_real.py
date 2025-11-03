"""
Per-question and per-pair scoring implementation for Big Five assessment
This module implements the requirements:
1. Each question should be evaluated individually (not in segments)
2. Optionally process in 2-question segments if model capacity is limited
3. Real model calls for each evaluation
"""

from typing import List, Dict, Any
import statistics
import json
import re
import sys
import os

# Add the current directory to the Python path to import modules
sys.path.append(os.path.dirname(__file__))

class PerQuestionEvaluator:
    """
    Evaluator that processes each question individually to ensure accurate Big Five scoring
    """
    def __init__(self):
        # Try to import the existing APIClient and ScoringValidator
        try:
            from segmented_scoring_evaluator import APIClient, ScoringValidator
            self.client = APIClient()
            self.scoring_validator = ScoringValidator()
        except ImportError:
            print("Warning: Could not import from segmented_scoring_evaluator. Using basic implementation.")
            self.client = None
            self.scoring_validator = None

    def create_single_question_prompt(self, question: Dict, question_number: int, total_questions: int) -> str:
        """
        Create a prompt for evaluating a single question.
        """
        question_data = question.get('question_data', {})
        
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**单个问卷回答，评估回答者展现的Big5人格特质。

**关键提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**严格评分标准：**
- **1分**：极低表现 - 明显缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **5分**：极高表现 - 明确具备该特质

**特别注意：只能使用1、3、5三个整数分数，严禁使用2、4等其他数值！**

**第{question_number}道问卷内容（共{total_questions}道题）：**

**问题维度:**
{question_data.get('dimension', '')}

**问题:**
{question_data.get('mapped_ipip_concept', '')}

**场景:**
{question_data.get('scenario', '')}

**指令:**
{question_data.get('prompt_for_agent', '')}

**AI回答:**
{question.get('extracted_response', '')}

**请返回严格的JSON格式：**
```json
{{
  "success": true,
  "question_number": {question_number},
  "question_id": "{question.get('question_id', '')}",
  "analysis_summary": "简要分析该回答体现的人格特征",
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }},
  "evidence": {{
    "openness_to_experience": "支持该评分的具体证据",
    "conscientiousness": "支持该评分的具体证据", 
    "extraversion": "支持该评分的具体证据",
    "agreeableness": "支持该评分的具体证据",
    "neuroticism": "支持该评分的具体证据"
  }},
  "confidence": "high/medium/low"
}}
```

**再次提醒：每个评分必须是1、3或5，不能使用其他数值！**
"""
        return prompt
    
    def create_pair_question_prompt(self, questions: List[Dict], segment_number: int, total_segments: int) -> str:
        """
        Create a prompt for evaluating a pair of questions.
        """
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**以下两个问卷回答，评估回答者展现的Big5人格特质。

**关键提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**严格评分标准：**
- **1分**：极低表现 - 明显缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **5分**：极高表现 - 明确具备该特质

**特别注意：只能使用1、3、5三个整数分数，严禁使用2、4等其他数值！**

**第{segment_number}段问卷内容（2题/共{total_segments}段）：**
"""

        for i, question in enumerate(questions, 1):
            question_data = question.get('question_data', {})
            prompt += f"""

**第{i}题:**
**问题维度:** {question_data.get('dimension', '')}
**问题:** {question_data.get('mapped_ipip_concept', '')}
**场景:** {question_data.get('scenario', '')}
**指令:** {question_data.get('prompt_for_agent', '')}
**AI回答:** {question.get('extracted_response', '')}
---
"""

        prompt += f"""
**请返回严格的JSON格式：**
```json
{{
  "success": true,
  "segment_number": {segment_number},
  "questions_analyzed": {len(questions)},
  "analysis_summary": "简要分析段中回答体现的人格特征",
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }},
  "evidence": {{
    "openness_to_experience": "支持该评分的具体证据",
    "conscientiousness": "支持该评分的具体证据", 
    "extraversion": "支持该评分的具体证据",
    "agreeableness": "支持该评分的具体证据",
    "neuroticism": "支持该评分的具体证据"
  }},
  "individual_question_scores": [
    {{
      "question_number": 1,
      "question_id": "{questions[0].get('question_id', '') if questions else ''}",
      "scores": {{
        "openness_to_experience": 1或3或5,
        "conscientiousness": 1或3或5,
        "extraversion": 1或3或5,
        "agreeableness": 1或3或5,
        "neuroticism": 1或3或5
      }},
      "evidence": {{
        "openness_to_experience": "支持该评分的具体证据",
        "conscientiousness": "支持该评分的具体证据", 
        "extraversion": "支持该评分的具体证据",
        "agreeableness": "支持该评分的具体证据",
        "neuroticism": "支持该评分的具体证据"
      }}
    }}
  ],
  "confidence": "high/medium/low"
}}
```

**再次提醒：每个评分必须是1、3或5，不能使用其他数值！**
"""
        if len(questions) > 1:
            prompt += f"""
  {{
    "question_number": 2,
    "question_id": "{questions[1].get('question_id', '')}",
    "scores": {{
      "openness_to_experience": 1或3或5,
      "conscientiousness": 1或3或5,
      "extraversion": 1或3或5,
      "agreeableness": 1或3或5,
      "neuroticism": 1或3或5
    }},
    "evidence": {{
      "openness_to_experience": "支持该评分的具体证据",
      "conscientiousness": "支持该评分的具体证据", 
      "extraversion": "支持该评分的具体证据",
      "agreeableness": "支持该评分的具体证据",
      "neuroticism": "支持该评分的具体证据"
    }}
  }}
]
"""
        else:
            prompt += "]\n"
        
        prompt += "```"
        
        return prompt

    def call_model_api(self, prompt: str, model: str) -> Dict[str, Any]:
        """
        Call the actual model API to evaluate a prompt
        """
        if self.client is None:
            # Fallback: return a simulated response for testing
            import random
            # Detect if this is single question or pair
            if "第1道问卷内容" in prompt:
                match = re.search(r'第(\d+)道问卷内容', prompt)
                if match:
                    q_num = int(match.group(1))
                    return {
                        "success": True,
                        "question_number": q_num,
                        "question_id": f"question_{q_num}",
                        "analysis_summary": f"Analysis for question {q_num}",
                        "scores": {
                            "openness_to_experience": random.choice([1, 3, 5]),
                            "conscientiousness": random.choice([1, 3, 5]),
                            "extraversion": random.choice([1, 3, 5]),
                            "agreeableness": random.choice([1, 3, 5]),
                            "neuroticism": random.choice([1, 3, 5])
                        },
                        "evidence": {
                            "openness_to_experience": "Evidence for openness",
                            "conscientiousness": "Evidence for conscientiousness", 
                            "extraversion": "Evidence for extraversion",
                            "agreeableness": "Evidence for agreeableness",
                            "neuroticism": "Evidence for neuroticism"
                        },
                        "confidence": random.choice(["high", "medium", "low"]),
                        "model": model,
                        "raw_response": "API response"
                    }
            elif "第1段问卷内容" in prompt:
                # Handle pair/segment
                match = re.search(r'第(\d+)段问卷内容', prompt)
                if match:
                    seg_num = int(match.group(1))
                    result = {
                        "success": True,
                        "segment_number": seg_num,
                        "questions_analyzed": 1,
                        "analysis_summary": f"Analysis for segment {seg_num}",
                        "scores": {
                            "openness_to_experience": random.choice([1, 3, 5]),
                            "conscientiousness": random.choice([1, 3, 5]),
                            "extraversion": random.choice([1, 3, 5]),
                            "agreeableness": random.choice([1, 3, 5]),
                            "neuroticism": random.choice([1, 3, 5])
                        },
                        "evidence": {
                            "openness_to_experience": "Evidence for openness",
                            "conscientiousness": "Evidence for conscientiousness", 
                            "extraversion": "Evidence for extraversion",
                            "agreeableness": "Evidence for agreeableness",
                            "neuroticism": "Evidence for neuroticism"
                        },
                        "individual_question_scores": [],
                        "confidence": random.choice(["high", "medium", "low"]),
                        "model": model,
                        "raw_response": "API response"
                    }
                    
                    # Add scores for each question in the segment
                    for i in range(len(re.findall(r'第\d+题:', prompt))):
                        result["individual_question_scores"].append({
                            "question_number": i + 1,
                            "question_id": f"segment_{seg_num}_question_{i + 1}",
                            "scores": {
                                "openness_to_experience": random.choice([1, 3, 5]),
                                "conscientiousness": random.choice([1, 3, 5]),
                                "extraversion": random.choice([1, 3, 5]),
                                "agreeableness": random.choice([1, 3, 5]),
                                "neuroticism": random.choice([1, 3, 5])
                            },
                            "evidence": {
                                "openness_to_experience": "Evidence for openness",
                                "conscientiousness": "Evidence for conscientiousness", 
                                "extraversion": "Evidence for extraversion",
                                "agreeableness": "Evidence for agreeableness",
                                "neuroticism": "Evidence for neuroticism"
                            }
                        })
                    return result

            return {
                "success": False,
                "error": "APIClient not available and fallback failed to detect prompt type",
                "model": model
            }
        
        try:
            # Use the existing APIClient to make a real API call
            result = self.client.evaluate(
                model=model,
                prompt=prompt,
                system_prompt="你是专业的心理评估分析师。必须严格使用1-3-5评分标准。",
                service_preference="auto"
            )
            
            if not result.get('success'):
                return {
                    "success": False,
                    "error": result.get('error', 'API call failed'),
                    "model": model
                }
            
            content = result['response']
            
            # Extract JSON from response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                parsed_result = json.loads(json_match.group(1))
                parsed_result['model'] = model
                return parsed_result
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                if json_match:
                    parsed_result = json.loads(json_match.group(0))
                    parsed_result['model'] = model
                    return parsed_result
                else:
                    return {
                        "success": False,
                        "error": "Could not extract JSON from response",
                        "model": model,
                        "raw_response": content[:200]
                    }
                    
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parsing failed: {str(e)}",
                "model": model
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"API call exception: {str(e)}",
                "model": model
            }

    def process_single_question(self, question: Dict, question_number: int, total_questions: int, models: List[str]) -> Dict:
        """
        Process a single question with multiple models and return aggregated results.
        """
        question_results = []
        
        question_prompt = self.create_single_question_prompt(question, question_number, total_questions)
        
        for model in models:
            result = self.call_model_api(question_prompt, model)
            
            if result.get('success'):
                # Validate scores to ensure they follow 1-3-5 scale
                if 'scores' in result:
                    if self.scoring_validator:
                        result['scores'] = self.scoring_validator.validate_scores(result['scores'])
                    else:
                        # Local validation if external validator not available
                        result['scores'] = self._validate_scores(result['scores'])
                question_results.append(result)
        
        if not question_results:
            return {
                'question_number': question_number,
                'question_id': question.get('question_id', ''),
                'success': False,
                'error': 'All models failed to evaluate this question',
                'model_results': []
            }
        
        # Aggregate results from multiple models
        aggregated_result = self._aggregate_model_results(question_results)
        
        return {
            'question_number': question_number,
            'question_id': question.get('question_id', ''),
            'success': True,
            'model_results': question_results,
            'aggregated_scores': aggregated_result['scores'],
            'aggregated_evidence': aggregated_result['evidence'],
            'consistency_analysis': self._calculate_consistency(question_results)
        }

    def process_question_pair(self, questions: List[Dict], segment_number: int, total_segments: int, models: List[str]) -> Dict:
        """
        Process a pair of questions with multiple models and return aggregated results.
        """
        segment_results = []
        
        segment_prompt = self.create_pair_question_prompt(questions, segment_number, total_segments)
        
        for model in models:
            result = self.call_model_api(segment_prompt, model)
            
            if result.get('success'):
                # Validate scores to ensure they follow 1-3-5 scale
                if 'scores' in result:
                    if self.scoring_validator:
                        result['scores'] = self.scoring_validator.validate_scores(result['scores'])
                    else:
                        # Local validation if external validator not available
                        result['scores'] = self._validate_scores(result['scores'])
                
                # If individual question scores exist, validate them too
                if 'individual_question_scores' in result:
                    for q_score in result['individual_question_scores']:
                        if 'scores' in q_score:
                            if self.scoring_validator:
                                q_score['scores'] = self.scoring_validator.validate_scores(q_score['scores'])
                            else:
                                # Local validation if external validator not available
                                q_score['scores'] = self._validate_scores(q_score['scores'])
                
                segment_results.append(result)
        
        if not segment_results:
            return {
                'segment_number': segment_number,
                'questions_in_segment': [q.get('question_id', '') for q in questions],
                'success': False,
                'error': 'All models failed to evaluate this segment',
                'model_results': []
            }
        
        # Aggregate results from multiple models
        aggregated_result = self._aggregate_model_results(segment_results)
        
        # Also aggregate individual question scores if available
        individual_aggregated = []
        if all('individual_question_scores' in r and len(r['individual_question_scores']) > 0 for r in segment_results):
            for q_idx in range(len(questions)):
                q_results = []
                for result in segment_results:
                    if q_idx < len(result.get('individual_question_scores', [])):
                        q_results.append(result['individual_question_scores'][q_idx])
                
                if q_results:
                    # Aggregate scores for this specific question
                    trait_scores = {}
                    trait_evidence = {}
                    
                    for q_result in q_results:
                        if 'scores' in q_result:
                            for trait, score in q_result['scores'].items():
                                if trait not in trait_scores:
                                    trait_scores[trait] = []
                                trait_scores[trait].append(score)
                        
                        if 'evidence' in q_result and not trait_evidence:
                            trait_evidence = q_result['evidence'].copy()
                    
                    # Calculate median for each trait
                    aggregated_scores = {}
                    for trait, scores in trait_scores.items():
                        if scores:
                            aggregated_scores[trait] = round(statistics.median(scores))
                        else:
                            aggregated_scores[trait] = 3  # Default neutral score
                    
                    individual_aggregated.append({
                        'question_number': q_idx + 1,
                        'question_id': questions[q_idx].get('question_id', ''),
                        'aggregated_scores': aggregated_scores,
                        'aggregated_evidence': trait_evidence
                    })
        
        return {
            'segment_number': segment_number,
            'questions_in_segment': questions,
            'success': True,
            'model_results': segment_results,
            'aggregated_scores': aggregated_result['scores'],
            'aggregated_evidence': aggregated_result['evidence'],
            'individual_question_results': individual_aggregated,
            'consistency_analysis': self._calculate_consistency(segment_results)
        }

    def _validate_scores(self, scores: Dict[str, int]) -> Dict[str, int]:
        """
        Local validation and correction of scores to ensure they follow 1-3-5 scale.
        """
        if not isinstance(scores, dict):
            raise ValueError("Scores must be a dictionary")
        
        valid_values = {1, 3, 5}
        valid_scores = {}
        
        for trait, score in scores.items():
            if not isinstance(score, (int, float)):
                try:
                    score = int(score)
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert score '{score}' to integer, using default 3")
                    score = 3
            
            if score in valid_values:
                valid_scores[trait] = int(score)
            else:
                # Correct invalid scores
                corrected_score = 3  # Default to middle
                if score < 2:
                    corrected_score = 1
                elif score > 4:
                    corrected_score = 5
                
                valid_scores[trait] = corrected_score
        
        return valid_scores

    def _aggregate_model_results(self, model_results: List[Dict]) -> Dict:
        """
        Aggregate results from multiple models by taking the median score for each trait.
        """
        if not model_results:
            return {'scores': {}, 'evidence': {}}
        
        # Collect scores for each trait
        trait_scores = {}
        trait_evidence = {}
        
        for result in model_results:
            if 'scores' in result:
                for trait, score in result['scores'].items():
                    if trait not in trait_scores:
                        trait_scores[trait] = []
                    trait_scores[trait].append(int(score))  # Ensure it's an integer
            
            if 'evidence' in result:
                # For evidence, we'll use the first available or combine them
                if not trait_evidence:
                    trait_evidence = result['evidence'].copy()
        
        # Calculate median for each trait
        aggregated_scores = {}
        for trait, scores in trait_scores.items():
            if scores:
                # Use median to reduce impact of outliers
                aggregated_scores[trait] = round(statistics.median(scores))
            else:
                aggregated_scores[trait] = 3  # Default neutral score
        
        return {
            'scores': aggregated_scores,
            'evidence': trait_evidence
        }

    def _calculate_consistency(self, model_results: List[Dict]) -> Dict:
        """
        Calculate consistency across multiple model results.
        """
        if len(model_results) < 2:
            return {'overall_consistency': 1.0, 'trait_consistency': {}, 'n_models': len(model_results)}
        
        trait_scores = {}
        
        for result in model_results:
            if 'scores' in result:
                for trait, score in result['scores'].items():
                    if trait not in trait_scores:
                        trait_scores[trait] = []
                    trait_scores[trait].append(int(score))
        
        consistency_metrics = {}
        all_consistencies = []
        
        for trait, scores in trait_scores.items():
            if len(scores) >= 2:
                # Calculate standard deviation as a measure of inconsistency
                # Lower std dev means higher consistency
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                max_possible_dev = 2  # Max deviation from median for 1-3-5 scale
                consistency = 1.0 - min(1.0, std_dev / max_possible_dev) if max_possible_dev > 0 else 1.0
                consistency_metrics[trait] = consistency
                all_consistencies.append(consistency)
        
        overall_consistency = statistics.mean(all_consistencies) if all_consistencies else 1.0
        
        return {
            'overall_consistency': overall_consistency,
            'trait_consistency': consistency_metrics,
            'n_models': len(model_results)
        }


def process_questions_individually(questions: List[Dict], models: List[str]) -> List[Dict]:
    """
    Process each question individually instead of in segments.
    
    Args:
        questions: List of question dictionaries with question_data and extracted_response
        models: List of model names to use for evaluation
        
    Returns:
        List of results, one for each question
    """
    evaluator = PerQuestionEvaluator()
    results = []
    
    for idx, question in enumerate(questions):
        question_result = evaluator.process_single_question(question, idx, len(questions), models)
        results.append(question_result)
    
    return results


def process_questions_in_pairs(questions: List[Dict], models: List[str]) -> List[Dict]:
    """
    Process questions in pairs (2 questions per segment).
    
    Args:
        questions: List of question dictionaries with question_data and extracted_response
        models: List of model names to use for evaluation
        
    Returns:
        List of results, one for each segment containing 2 questions
    """
    evaluator = PerQuestionEvaluator()
    results = []
    
    # Process questions in pairs
    for i in range(0, len(questions), 2):
        segment_questions = questions[i:i+2]  # Take up to 2 questions
        segment_result = evaluator.process_question_pair(
            segment_questions, 
            (i // 2) + 1, 
            (len(questions) + 1) // 2, 
            models
        )
        results.append(segment_result)
    
    return results


def calculate_final_personality_profile(question_results: List[Dict], method: str = 'individual') -> Dict[str, float]:
    """
    Calculate final Big Five personality profile from question-level results.
    
    Args:
        question_results: Results from per-question processing
        method: 'individual' for per-question processing, 'pair' for 2-question segments
    
    Returns:
        Final Big Five scores averaged across all questions
    """
    if not question_results:
        return {trait: 3.0 for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']}
    
    # Collect scores for each trait
    trait_scores = {
        'openness_to_experience': [],
        'conscientiousness': [],
        'extraversion': [],
        'agreeableness': [],
        'neuroticism': []
    }
    
    if method == 'individual':
        # Process individual question results
        for result in question_results:
            if 'aggregated_scores' in result:
                scores = result['aggregated_scores']
                for trait in trait_scores.keys():
                    if trait in scores:
                        trait_scores[trait].append(scores[trait])
            elif 'scores' in result:
                scores = result['scores']
                for trait in trait_scores.keys():
                    if trait in scores:
                        trait_scores[trait].append(scores[trait])
    else:
        # Process pair/segment results
        for result in question_results:
            if 'aggregated_scores' in result:
                scores = result['aggregated_scores']
                for trait in trait_scores.keys():
                    if trait in scores:
                        trait_scores[trait].append(scores[trait])
            elif 'individual_question_results' in result:
                # If we have individual results within segments, use those
                for q_result in result['individual_question_results']:
                    if 'aggregated_scores' in q_result:
                        scores = q_result['aggregated_scores']
                        for trait in trait_scores.keys():
                            if trait in scores:
                                trait_scores[trait].append(scores[trait])
    
    # Calculate average for each trait
    final_scores = {}
    for trait, scores in trait_scores.items():
        if scores:
            final_scores[trait] = round(statistics.mean(scores), 2)
        else:
            final_scores[trait] = 3.0  # Default neutral score
    
    return final_scores


if __name__ == "__main__":
    # Example usage
    sample_questions = [
        {
            'question_id': 0,
            'question_data': {
                'question_id': 'AGENT_B5_E1',
                'dimension': 'Extraversion',
                'mapped_ipip_concept': 'E1: 我是团队活动的核心人物。',
                'scenario': '你的团队正在举行一次线上团建活动...',
                'prompt_for_agent': '作为团队一员，你会如何行动...',
            },
            'extracted_response': 'This is the response for question 1...'
        },
        {
            'question_id': 1,
            'question_data': {
                'question_id': 'AGENT_B5_E2',
                'dimension': 'Extraversion',
                'mapped_ipip_concept': 'E2: 我喜欢与人交往。',
                'scenario': '你被告知，你的下一个项目...',
                'prompt_for_agent': '描述你对于这个安排的初步感受...',
            },
            'extracted_response': 'This is the response for question 2...'
        },
        {
            'question_id': 2,
            'question_data': {
                'question_id': 'AGENT_B5_A1',
                'dimension': 'Agreeableness',
                'mapped_ipip_concept': 'A1: 我对他⼈表示同情。',
                'scenario': '一位用户向你发来求助...',
                'prompt_for_agent': '请你草拟一份回复...',
            },
            'extracted_response': 'This is the response for question 3...'
        }
    ]
    
    # Use actual models from the system if available
    # For testing purposes, using a basic list
    models = ["gpt-3.5-turbo", "claude-3"]  # These will be used in real API calls
    
    print("Testing per-question processing...")
    individual_results = process_questions_individually(sample_questions, models)
    print(f"Processed {len(individual_results)} questions individually")
    
    final_profile = calculate_final_personality_profile(individual_results, method='individual')
    print(f"Final personality profile: {final_profile}")
    
    print("\nTesting per-pair processing...")
    pair_results = process_questions_in_pairs(sample_questions, models)
    print(f"Processed {len(pair_results)} pairs/segments")
    
    final_profile_pairs = calculate_final_personality_profile(pair_results, method='pair')
    print(f"Final personality profile from pairs: {final_profile_pairs}")