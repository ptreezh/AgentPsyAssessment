# Quick Start Guide

## Getting Started with Portable PsyAgent

This guide will help you quickly set up and run your first psychological assessment using Portable PsyAgent.

### Step 1: Installation

1. **Install Python 3.7+** if not already installed
2. **Clone the repository** or download the source code:
   ```bash
   git clone <repository-url>
   cd portable_psyagent_open_source
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Setup Local Models (Recommended)

For local evaluation without API keys:

1. **Install Ollama**:
   - Windows: Download from https://ollama.ai/download
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - macOS: `brew install ollama`

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

3. **Download recommended models**:
   ```bash
   ollama pull phi3:mini
   ollama pull qwen3:4b
   ```

### Step 3: Run Your First Assessment

1. **Prepare your assessment data** in JSON format (see example below)
2. **Run the analysis**:
   ```bash
   python shared_analysis/analyze_results.py path/to/your_assessment.json
   ```

### Step 4: View Results

After analysis completes, check the output files:
- `analysis_results.json` - Detailed scores and analysis
- `analysis_report.md` - Human-readable report
- Log files in `logs/` directory

## Example Assessment Data

Create a simple assessment file `my_assessment.json`:

```json
{
  "assessment_results": [
    {
      "question_id": "Q1",
      "dimension": "extraversion",
      "scenario": "You are at a team meeting and are asked to share your ideas.",
      "agent_response": "I would actively participate in the discussion, share my views, and listen to others' opinions.",
      "evaluation_rubric": {
        "description": "Assessing extraversion, including social confidence and expressive ability",
        "scale": {
          "1": "Rarely shares ideas, prefers to listen",
          "3": "Sometimes shares ideas when prompted",
          "5": "Actively shares ideas and encourages discussion"
        }
      }
    },
    {
      "question_id": "Q2", 
      "dimension": "conscientiousness",
      "scenario": "You need to complete an important project with a tight deadline.",
      "agent_response": "I would create a detailed plan, prioritize tasks, and ensure all work is completed on time.",
      "evaluation_rubric": {
        "description": "Assessing conscientiousness, including organizational skills and responsibility",
        "scale": {
          "1": "Works without planning, often misses deadlines",
          "3": "Makes basic plans but sometimes misses deadlines",
          "5": "Creates detailed plans and consistently meets deadlines"
        }
      }
    }
  ]
}
```

## Running Different Types of Analysis

### Basic Personality Analysis
```bash
python shared_analysis/analyze_results.py my_assessment.json
```

### Big Five Analysis Only
```bash
python shared_analysis/analyze_big5_results.py my_assessment.json
```

### Motivation Analysis (No API Required)
```bash
python shared_analysis/analyze_motivation.py my_assessment.json --debug
```

## Using Cloud Models

To use cloud-based models, configure your API keys in a `.env` file:

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_claude_key
```

Then run:
```bash
python shared_analysis/analyze_results.py my_assessment.json --evaluators gpt claude
```

## Batch Processing

To analyze multiple files:

```bash
# Using the standalone batch tool
python batchAnalysizeTools/batch_segmented_analysis.py batch input_directory output_directory
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**:
   - Ensure `ollama serve` is running
   - Check `http://localhost:11434/api/tags` in browser

2. **Module Not Found**:
   - Run `pip install -r requirements.txt`

3. **Analysis Fails**:
   - Check log files in `logs/` directory
   - Ensure input JSON format is correct

### Need Help?

- Check the full documentation in `USER_MANUAL.md`
- Review example files in the repository
- Contact: contact@agentpsy.com

## Next Steps

- Explore different assessment types in `llm_assessment/test_files/`
- Try role-based testing with files in `llm_assessment/roles/`
- Run pressure tests using `pressure_test_bank.json`
- Experiment with different models and configurations