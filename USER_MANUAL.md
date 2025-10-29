# AgentPsyAssessment User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Quick Start Guide](#quick-start-guide)
6. [Assessment Component](#assessment-component)
7. [Analysis Component](#analysis-component)
8. [Assessment Flow: Test, Evaluate, Targeted Test, Evaluate, Analyze](#assessment-flow)
9. [Advanced Usage](#advanced-usage)
10. [Understanding Results](#understanding-results)
11. [Analysis Tools](#analysis-tools)
12. [Troubleshooting](#troubleshooting)
13. [API Reference](#api-reference)
14. [FAQ](#faq)

## Introduction

AgentPsyAssessment is a comprehensive psychological assessment framework with two main components: 
1) Assessment - using LLMs with various parameters to respond to psychological questionnaires
2) Analysis - evaluating responses to generate personality profiles and recommendations

The system combines traditional psychometric models with modern AI technologies. The assessment component uses large language models (LLMs) to respond to questionnaires with various parameters, while the analysis component evaluates these responses using various models, including the Big Five, MBTI, and cognitive functions, to generate detailed psychological profiles.

### What You Can Do With This Tool

- Run individual psychological assessments
- Batch process multiple assessments
- Compare personality traits across different conditions
- Analyze results using multiple psychometric models
- Generate detailed personality reports
- Use local or cloud-based LLMs

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- At least 4GB of RAM (8GB+ recommended for local models)
- 500MB of free disk space
- Stable internet connection (for cloud models)

### Recommended Requirements
- Python 3.9 or higher
- 8GB+ of RAM (16GB+ for large local models)
- 1GB+ of free disk space
- High-speed internet connection

### Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, CentOS 8+)

## Installation

### Prerequisites

1. Install Python 3.8+
2. Install pip package manager
3. For local models (optional), install Ollama from [https://ollama.ai](https://ollama.ai)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ptreezh/AgentPsyAssessment.git
   cd AgentPsyAssessment
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -c "import openai; print('Dependencies installed successfully')"
   ```

## Configuration

### Environment Setup

1. **Copy the environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** to add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OLLAMA_HOST=http://localhost:11434
   ```

3. **Select and pull models** (for Ollama users):
   ```bash
   ollama pull llama3.1
   ollama pull phi3
   ```

### Model Configuration

The framework supports various LLMs. You can configure which models to use in:

- `config/ollama_config.json` - For Ollama models
- `llm_assessment/config.json` - For general configuration

## Assessment Component

The Assessment Component uses LLMs with various parameters to respond to psychological questionnaires.

### Quick Start with Assessment Component

1. **Run a basic assessment**:
   ```bash
   python llm_assessment/run_assessment_unified.py --model gpt-4o --role def
   ```

2. **Use a specific personality role** (optional):
   ```bash
   python llm_assessment/run_assessment_unified.py --model claude-3-5-sonnet --role a1
   ```

3. **Use a local model**:
   ```bash
   python llm_assessment/run_assessment_unified.py --model llama3.1 --ollama
   ```

4. **Customize parameters**:
   ```bash
   python llm_assessment/run_assessment_unified.py --model gpt-4o --temperature 0.3 --top_p 0.8
   ```

### Assessment Parameters

- `--model`: LLM model to use (e.g., gpt-4o, claude-3-5-sonnet, llama3.1)
- `--role`: Personality role to apply during assessment (a1-a10, b1-b10, def)
- `--questions`: Path to custom questions JSON file
- `--temperature`: Model temperature (default: 0)
- `--top_p`: Model top_p parameter (default: 0.9)
- `--context`: Additional context for the assessment
- `--ollama`: Use Ollama models instead of cloud APIs
- `--host`: Ollama host (default: http://localhost:11434)

## Analysis Component

The Analysis Component evaluates responses to generate personality profiles and recommendations.

### Running Analysis

1. **Analyze assessment results**:
   ```bash
   python analyze_results.py --input results/assessment_result.json
   ```

2. **Generate Big Five analysis**:
   ```bash
   python analyze_big5_results.py --input results/assessment_result.json
   ```

3. **Generate MBTI analysis**:
   ```bash
   python analyze_mbti_results.py --input results/assessment_result.json
   ```

4. **Generate Belbin analysis**:
   ```bash
   python analyze_belbin_results.py --input results/assessment_result.json
   ```

### Analysis Parameters

- `--input`: Path to assessment results file to analyze
- `--analysis-type`: Type of analysis (bigfive, mbti, belbin, comprehensive)
- `--output`: Output path for analysis results (default: results/)
- `--confidence-threshold`: Confidence threshold for recommendations (default: 0.7)

## Assessment Flow

The assessment follows a cyclical process: Test → Evaluate → Targeted Test → Evaluate → Analyze

### Step 1: Initial Test
Run an initial assessment to get baseline personality scores:
```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --role def
```

### Step 2: Initial Evaluation
Analyze the initial results:
```bash
python analyze_results.py --input results/initial_assessment.json
```

### Step 3: Targeted Test
Based on the initial evaluation, run targeted questions focusing on specific traits:
```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --role targeted --context "focus on neuroticism"
```

### Step 4: Secondary Evaluation
Analyze the targeted test results:
```bash
python analyze_results.py --input results/targeted_assessment.json
```

### Step 5: Comprehensive Analysis
Generate a comprehensive analysis integrating all results:
```bash
python analyze_results.py --input results/combined_assessments.json --analysis-type comprehensive
```

### Understanding Assessment Output

Results from the Assessment Component will be saved in the `results/` directory in JSON format. The main assessment file will contain:

- Raw LLM responses to questions
- Model parameters used
- Response confidence
- Processing metadata

## Running Assessments

### Basic Assessment

Run a basic assessment with default settings:

```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o
```

### Advanced Assessment Options

```bash
# Use specific role and temperature
python llm_assessment/run_assessment_unified.py --model claude-3-5-sonnet --role a2 --temperature 0.2

# Use local model with custom host
python llm_assessment/run_assessment_unified.py --model llama3.1 --ollama --host http://localhost:11434

# Save to custom directory
python llm_assessment/run_assessment_unified.py --model gpt-4o --output-dir custom_results
```

### Batch Assessments

Run multiple assessments at once:

```bash
# Assess multiple roles with one model
python llm_assessment/run_batch_suite.py --model gpt-4o --roles a1,a2,b1

# Run comprehensive batch
python llm_assessment/run_batch_suite.py --model claude-3-5-sonnet --roles a1,a2,a3,a4,a5
```

### Personality Roles

The system includes several pre-defined personality roles:

- `a1-a10`: Different analytical personality types
- `b1-b10`: Different behavioral personality types  
- `def`: Default baseline assessment

Each role applies different framing to the assessment questions.

## Advanced Usage

### Using Custom Questions

To use your own questions, create a JSON file in the same format as the default questions and use:

```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --questions path/to/your/questions.json
```

### Segmented Analysis

For more detailed analysis, use segmented approach:

```bash
python llm_assessment/batch_analysis_final.py --model gpt-4o
```

### Trustworthy Assessment

Run a multi-evaluator assessment for more reliable results:

```bash
python run_evaluator.py --model gpt-4o --evaluators 3
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--model` | LLM model name | gpt-4o |
| `--role` | Personality role | def |
| `--temperature` | Model temperature (0-1) | 0 |
| `--top_p` | Top-p sampling (0-1) | 0.9 |
| `--ollama` | Use Ollama models | False |
| `--host` | Ollama host | http://localhost:11434 |
| `--max_tokens` | Max tokens in response | 4096 |
| `--timeout` | Request timeout in seconds | 300 |

## Understanding Results

### Assessment Component Output

Results from the Assessment Component are stored in JSON format in the `results/` directory:

```
results/
├── asses_[model]_[role]_[timestamp].json
├── [assessment_id]_raw_responses.json
└── assessment_stats_[timestamp].json
```

The Assessment Component output contains:

- Raw LLM responses to questions
- Model parameters used
- Response confidence
- Processing metadata

### Analysis Component Output

Results from the Analysis Component are stored in JSON format in the `results/` directory:

```
results/
├── analysis_[model]_[type]_[timestamp].json
├── bigfive_analysis_[timestamp].json
├── mbti_analysis_[timestamp].json
├── belbin_analysis_[timestamp].json
├── stress_recommendations_[timestamp].json
└── analysis_report_[timestamp].json
```

### Analysis Component JSON Output Format

```json
{
  "id": "analysis_model_type_12345",
  "model": "gpt-4o",
  "analysis_type": "comprehensive",
  "timestamp": "2025-01-01T00:00:00",
  "input_assessment_id": "asses_model_role_12345",
  "big_five": {
    "openness": {"raw_score": 45, "percentile": 0.67, "analysis": "...", "confidence": 0.85},
    "conscientiousness": {"raw_score": 38, "percentile": 0.45, "analysis": "...", "confidence": 0.78},
    "extraversion": {"raw_score": 42, "percentile": 0.58, "analysis": "...", "confidence": 0.82},
    "agreeableness": {"raw_score": 48, "percentile": 0.72, "analysis": "...", "confidence": 0.90},
    "neuroticism": {"raw_score": 35, "percentile": 0.28, "analysis": "...", "confidence": 0.75}
  },
  "mbti": {
    "type": "ENFJ",
    "e_i": {"score": 0.7, "confidence": 0.85, "analysis": "..."},
    "s_n": {"score": 0.4, "confidence": 0.7, "analysis": "..."},
    "t_f": {"score": 0.3, "confidence": 0.75, "analysis": "..."},
    "j_p": {"score": 0.8, "confidence": 0.9, "analysis": "..."}
  },
  "belbin": {
    "coordinator": {"score": 0.8, "confidence": 0.82, "analysis": "..."},
    "shaper": {"score": 0.6, "confidence": 0.75, "analysis": "..."},
    "plant": {"score": 0.9, "confidence": 0.88, "analysis": "..."},
    "resource_investigator": {"score": 0.7, "confidence": 0.80, "analysis": "..."},
    "monitor_evaluator": {"score": 0.8, "confidence": 0.85, "analysis": "..."},
    "implementer": {"score": 0.5, "confidence": 0.70, "analysis": "..."},
    "completer_finisher": {"score": 0.6, "confidence": 0.72, "analysis": "..."},
    "teamworker": {"score": 0.9, "confidence": 0.90, "analysis": "..."},
    "specialist": {"score": 0.7, "confidence": 0.78, "analysis": "..."}
  },
  "stress_recommendations": [
    {
      "dimension": "neuroticism",
      "risk_level": "medium",
      "recommendation": "Suggested stress-reduction techniques for medium neuroticism scores...",
      "confidence": 0.85
    }
  ],
  "confidence_overall": 0.82,
  "methodology": "Comprehensive psychometric analysis using multiple validated models",
  "notes": "Additional insights from the analysis process"
}
```

### Interpreting Analysis Scores

- **Raw Score**: Scale-specific score (varies by assessment type)
- **Percentile**: How the score compares to the general population
- **Confidence**: Model's confidence in the assessment (0.0-1.0)
- **Type**: Categorical classifications (MBTI, Belbin roles, etc.)
- **Recommendations**: Tailored suggestions based on the profile

## Analysis Tools

### Batch Analysis

To analyze multiple assessment results:

```bash
python analyze_results.py --input-dir results --output analysis_report.json
```

### Reliability Analysis

Check consistency across multiple runs:

```bash
python validate_5segment_reliability.py --assessment-id asses_12345
```

### Big Five Analysis

Detailed analysis of Big Five dimensions:

```bash
python analyze_big5_results.py --input results/asses_12345.json
```

### MBTI Analysis

Detailed MBTI personality analysis:

```bash
python analyze_mbti_results.py --input results/asses_12345.json
```

### Belbin Analysis

Team role analysis based on Belbin model:

```bash
python analyze_belbin_results.py --input results/asses_12345.json
```

### Stress Testing Recommendations

Generate targeted stress testing recommendations:

```bash
python generate_stress_recommendations.py --input results/asses_12345.json
```

### Visualization Tools

Some analysis scripts generate visual outputs:

```bash
python visualize_results.py --input results/ --output plots/
```

## Troubleshooting

### Common Issues

**Issue**: API key error
```
AuthenticationError: Incorrect API key provided
```
**Solution**: Check your `.env` file has the correct API keys and format.

**Issue**: Model not found
```
ModelNotFoundError: Model 'llama3.2' not found
```
**Solution**: Download the model with `ollama pull llama3.2` (for Ollama users).

**Issue**: Timeout error
```
TimeoutError: Request timeout after 300s
```
**Solution**: Increase timeout value with `--timeout 600` or check your network connection.

**Issue**: Out of memory (with local models)
```
MemoryError: Unable to allocate memory
```
**Solution**: Use smaller models or increase system memory.

### Performance Tips

- Use smaller models for faster processing
- Set appropriate temperature (0.0-0.3) for more consistent results
- Use local models for privacy and cost control
- Batch process multiple assessments to reduce API overhead

## API Reference

### Command Line Interface

Most tools are accessible via command line:

```bash
python script_name.py --help
```

### Python API

You can also use the tools programmatically:

#### Assessment Component API

```python
from llm_assessment.services.model_service import ModelService
from llm_assessment.run_assessment_unified import run_assessment

# Run assessment programmatically
result = run_assessment(
    model="gpt-4o",
    role="def",
    temperature=0.1
)

# Run assessment with context
result = run_assessment(
    model="gpt-4o",
    role="targeted",
    context="focus on neuroticism and openness dimensions",
    temperature=0.2
)
```

#### Analysis Component API

```python
from llm_assessment.analyze_results import run_analysis

# Run comprehensive analysis
analysis_result = run_analysis(
    input_file="results/asses_gpt-4o_def_*.json",
    analysis_type="comprehensive",
    confidence_threshold=0.7
)

# Run specific analysis
bigfive_result = run_analysis(
    input_file="results/asses_gpt-4o_def_*.json",
    analysis_type="bigfive",
    confidence_threshold=0.75
)

mbti_result = run_analysis(
    input_file="results/asses_gpt-4o_def_*.json",
    analysis_type="mbti",
    confidence_threshold=0.75
)

belbin_result = run_analysis(
    input_file="results/asses_gpt-4o_def_*.json",
    analysis_type="belbin",
    confidence_threshold=0.75
)
```

#### Complete Assessment Flow API

```python
from llm_assessment.run_assessment_unified import run_assessment
from llm_assessment.analyze_results import run_analysis

# Step 1: Initial Test
initial_result = run_assessment(model="gpt-4o", role="def")

# Step 2: Initial Evaluation
initial_analysis = run_analysis(
    input_file=initial_result.output_file,
    analysis_type="comprehensive"
)

# Step 3: Targeted Test based on initial results
targeted_result = run_assessment(
    model="gpt-4o",
    role="targeted",
    context=f"focus on {initial_analysis.focus_areas}"
)

# Step 4: Secondary Evaluation
targeted_analysis = run_analysis(
    input_file=targeted_result.output_file,
    analysis_type="comprehensive"
)

# Step 5: Comprehensive Analysis
final_report = run_analysis(
    input_file=[initial_result.output_file, targeted_result.output_file],
    analysis_type="comprehensive"
)
```

## FAQ

**Q: How accurate are the assessments?**
A: The assessments are AI-generated and should be used as a starting point for understanding personality, not as clinical diagnoses. Results may vary between different models and settings.

**Q: Can I use this for clinical purposes?**
A: No, these assessments are for research and educational purposes only. They are not validated for clinical use.

**Q: How can I improve the accuracy of results?**
A: Using multiple models and comparing results, setting lower temperatures, and using the consensus verification system can help improve reliability.

**Q: What personality models are supported?**
A: The system currently supports Big Five, MBTI, and cognitive functions. More models can be added through configuration.

**Q: Can I run this without internet?**
A: Yes, if you use local models like those from Ollama. You'll need to download and configure the models beforehand.

## Support

For questions not covered in this manual:

1. Check the [GitHub Issues](https://github.com/ptreezh/AgentPsyAssessment/issues) for known problems
2. Read the source code documentation in the [docs/](docs/) directory
3. Create a new issue in the repository if you encounter a new problem

For general questions, feel free to reach out through the GitHub repository.