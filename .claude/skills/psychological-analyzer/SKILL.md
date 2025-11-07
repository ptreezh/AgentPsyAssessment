---
name: psychological-analyzer
description: Analyze questionnaire responses to provide professional psychological assessment including Big Five personality traits, MBTI type inference, and team role evaluation
allowed-tools:
  - Bash
  - Read
  - Write
---

# Psychological Analyzer Skill

This skill provides professional psychological assessment based on questionnaire responses.

## When to Use This Skill

Activate this skill when the user:
- Provides questionnaire responses and wants psychological analysis
- Asks for personality assessment or trait analysis
- Wants Big Five personality evaluation
- Needs MBTI type inference
- Requests team role or work style analysis

## Capabilities

### Big Five Personality Analysis
- Calculate scores for Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- Provide percentile rankings and detailed interpretations
- Offer behavioral indicators and development suggestions

### MBTI Type Inference
- Infer personality type from response patterns
- Analyze cognitive functions and preferences
- Provide type descriptions and career suggestions

### Team Role Evaluation
- Assess Belbin team role preferences
- Identify leadership and collaboration styles
- Provide team dynamics insights

## Input Format

Expect questionnaire response data in JSON format:
```json
{
  "responses": [
    {
      "question_id": "Q1",
      "question": "I often find myself interested in abstract or philosophical issues",
      "response": 4,
      "reasoning": "I enjoy thinking about deep questions"
    }
  ]
}
```

## Analysis Process

1. **Data Validation**: Check response completeness and consistency
2. **Scoring**: Calculate dimension scores using psychological standards
3. **Interpretation**: Provide professional analysis based on established theories
4. **Recommendations**: Generate personalized development suggestions

## Output Format

Provide structured analysis including:
- Personality trait scores and interpretations
- Behavioral indicators and examples
- Strengths and development areas
- Practical recommendations

---

## Implementation Notes

This skill uses established psychological theories:
- Big Five model (Costa & McCrae)
- MBTI framework (Carl Jung)
- Belbin team roles (Meredith Belbin)

All analysis follows professional psychometric standards and provides evidence-based interpretations.