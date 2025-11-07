---
name: questionnaire-responder
description: Generate questionnaire responses based on specified personality types, roles, or contexts for psychological assessment testing
allowed-tools:
  - Bash
  - Read
  - Write
---

# Questionnaire Responder Skill

This skill generates realistic questionnaire responses based on specified personality types, professional roles, or environmental contexts.

## When to Use This Skill

Activate this skill when the user:
- Needs questionnaire responses for personality testing
- Wants to simulate responses based on MBTI types
- Requires role-based questionnaire completion
- Needs stress testing or context-specific responses
- Wants to generate test data for psychological assessments

## Capabilities

### MBTI Personality Simulation
- Generate responses for all 16 MBTI personality types
- Maintain consistent personality traits across responses
- Provide reasoning that reflects cognitive functions
- Support ENFJ, INTJ, ESTP, ISFJ and all other types

### Professional Role Simulation
- Career-specific response patterns
- Industry-appropriate reasoning
- Role-consistent decision making
- Context-aware answer selection

### Environmental Context Adaptation
- Stress level simulation (none to extreme)
- Work environment contexts
- Social situation adaptation
- Cultural consideration integration

## Usage Examples

### MBTI-Based Responses
```bash
claude code --print "Generate ENFJ personality questionnaire responses" \
  --file questionnaire.json \
  --persona ENFJ \
  --save enfj_responses.json
```

### Stress Testing
```bash
claude code --print "Generate responses under high stress" \
  --file stress_questionnaire.json \
  --stress-level high \
  --save stress_responses.json
```

### Professional Role
```bash
claude code --print "Generate software engineer responses" \
  --file career_questionnaire.json \
  --role software_engineer \
  --save engineer_responses.json
```

## Input Format

### Questionnaire Format
```json
{
  "questionnaire_info": {
    "title": "Big Five Personality Assessment",
    "scale": "1-5 (1=Strongly Disagree, 5=Strongly Agree)"
  },
  "questions": [
    {
      "id": "Q1",
      "question": "I often find myself interested in abstract or philosophical issues",
      "category": "openness",
      "reverse_scored": false
    }
  ]
}
```

## Response Generation Process

1. **Persona Analysis**: Understand specified personality type or role
2. **Question Interpretation**: Analyze question meaning and implications
3. **Trait Consistency**: Ensure responses align with specified persona
4. **Reasoning Generation**: Provide authentic justification for choices
5. **Quality Validation**: Check response coherence and consistency

## Output Format

```json
{
  "response_info": {
    "persona": "ENFJ",
    "context": "standard",
    "timestamp": "2025-01-07T16:30:00Z"
  },
  "responses": [
    {
      "question_id": "Q1",
      "question": "I often find myself interested in abstract or philosophical issues",
      "response": 4,
      "reasoning": "As an ENFJ, I'm naturally drawn to understanding human motivations and deeper meanings in life",
      "adjusted_score": 4.0
    }
  ]
}
```

## Supported Personas

### MBTI Types
- **ENFJ**: Protagonist - Empathetic, charismatic, natural leaders
- **INTJ**: Architect - Strategic, analytical, independent thinkers
- **ESTP**: Entrepreneur - Energetic, perceptive, risk-takers
- **ISFJ**: Defender - Warm, responsible, conscientious
- All other 16 types supported

### Stress Levels
- **none**: Normal, relaxed state
- **low**: Mild pressure, manageable stress
- **moderate**: Significant stress, noticeable impact
- **high**: High pressure, substantial impact
- **extreme**: Overwhelming stress, crisis mode

### Professional Roles
- **software_engineer**: Technical, analytical, problem-solving focused
- **teacher**: Educational, nurturing, knowledge-sharing
- **manager**: Leadership, coordination, results-oriented
- **healthcare_provider**: Caring, detail-oriented, service-focused

## Implementation Notes

This skill maintains:
- **Psychological Accuracy**: Responses based on established personality theory
- **Consistency**: Coherent trait expression across all responses
- **Authenticity**: Realistic reasoning and justification
- **Flexibility**: Adaptable to various contexts and requirements

All generated responses are designed for testing, educational, and development purposes only.