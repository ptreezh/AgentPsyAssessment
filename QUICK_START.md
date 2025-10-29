# Quick Start Guide

This guide will help you get started with AgentPsyAssessment quickly. Follow these steps to run your first psychological assessment using the two-component approach: Assessment and Analysis.

## Prerequisites

- Python 3.8 or higher
- An API key for your preferred LLM provider (OpenAI, Anthropic, etc.) or Ollama installed locally

## Step 1: Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ptreezh/AgentPsyAssessment.git
   cd AgentPsyAssessment
   ```

2. **Set up a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Configuration

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** to add your API keys:
   ```bash
   # Open the file in your preferred editor
   nano .env  # or use any text editor
   ```
   
   Add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OLLAMA_HOST=http://localhost:11434
   ```

3. **(Optional) Install and set up Ollama** if you want to use local models:
   - Download from [https://ollama.ai](https://ollama.ai)
   - Install following the instructions for your OS
   - Pull a model: `ollama pull llama3.1`

## Step 3: Run Your First Assessment (Test Component)

### Option A: Using a Cloud Model (OpenAI)

Run a basic assessment with GPT-4:
```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --role def
```

### Option B: Using a Local Model (Ollama)

Run an assessment with a local model:
```bash
python llm_assessment/run_assessment_unified.py --model llama3.1 --ollama
```

### Option C: Using Anthropic's Claude

Run an assessment with Claude:
```bash
python llm_assessment/run_assessment_unified.py --model claude-3-5-sonnet
```

## Step 4: Run Analysis (Analysis Component)

After running the assessment, analyze the results:

```bash
python analyze_results.py --input results/asses_gpt-4o_def_*.json --analysis-type comprehensive
```

Or run specific analyses:

```bash
# Big Five Analysis
python analyze_big5_results.py --input results/asses_gpt-4o_def_*.json

# MBTI Analysis
python analyze_mbti_results.py --input results/asses_gpt-4o_def_*.json

# Belbin Analysis
python analyze_belbin_results.py --input results/asses_gpt-4o_def_*.json

# Stress Recommendations
python generate_stress_recommendations.py --input results/asses_gpt-4o_def_*.json
```

## Step 5: Complete Assessment Flow

Follow the complete test → evaluate → targeted test → evaluate → analyze workflow:

### Step 1: Initial Test
```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --role def
```

### Step 2: Initial Evaluation
```bash
python analyze_results.py --input results/asses_gpt-4o_def_*.json
```

### Step 3: Targeted Test (based on initial results)
```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --role targeted --context "focus on neuroticism and openness"
```

### Step 4: Secondary Evaluation
```bash
python analyze_results.py --input results/asses_gpt-4o_targeted_*.json
```

### Step 5: Comprehensive Analysis
```bash
python analyze_results.py --input results/combined_assessments.json --analysis-type comprehensive
```

## Step 6: Understanding the Output

After running both components, you'll see:

1. **Assessment output** in the terminal and `results/` directory
2. **Analysis results** in the `results/` directory as JSON files
3. **Detailed reports** explaining the personality traits and recommendations

The assessment files will contain raw responses, and the analysis files will contain:
- Big Five personality scores (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
- MBTI type determination
- Belbin team role analysis
- Cognitive function preferences
- Stress testing recommendations
- Confidence scores for each assessment

## Step 7: Try Advanced Features

### Run Batch Assessments
Process multiple roles at once:
```bash
python llm_assessment/run_batch_suite.py --model gpt-4o --roles a1,a2,b1
```

### Use Personality Roles
Apply different personality lenses to the assessment:
```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --role a1
```

Available roles: `a1` through `a10`, `b1` through `b10`, `def` (default)

### Segmented Analysis
For more detailed analysis:
```bash
python llm_assessment/batch_analysis_final.py --model gpt-4o
```

## Troubleshooting Quick Fixes

### API Key Error
If you see an authentication error, verify your API keys in the `.env` file.

### Model Not Found (Ollama)
For local models, ensure you've downloaded the model:
```bash
ollama pull llama3.1
```

### Timeout Error
Increase the timeout or check your internet connection:
```bash
python llm_assessment/run_assessment_unified.py --model gpt-4o --timeout 600
```

## Next Steps

Now that you've run your first complete assessment and analysis, you can:

1. **Explore different models**: Try various LLMs to compare results
2. **Use different roles**: Experiment with personality roles (a1, a2, etc.)
3. **Run batch assessments**: Process multiple assessments efficiently
4. **Customize analysis types**: Run specific types of analysis (Big Five, MBTI, Belbin)
5. **Read the full documentation**: Check the USER_MANUAL.md for advanced usage

## Need Help?

- Check the full [User Manual](USER_MANUAL.md) for detailed instructions
- Look at the [README](README.md) for complete feature overview
- Create an issue on the [GitHub repository](https://github.com/ptreezh/AgentPsyAssessment) for support