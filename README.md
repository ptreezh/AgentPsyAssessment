# AgentPsyAssessment

**AgentPsyAssessment** is a portable, comprehensive psychological assessment framework that combines various psychometric models (Big Five, MBTI, cognitive functions, and more) with AI-powered analysis. The framework provides two main components: 1) Assessment - using LLMs to respond to psychological questionnaires with various parameters, and 2) Analysis - evaluating responses to generate personality profiles and recommendations.

## Table of Contents
- [Features](#features)
- [Components](#components)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Assessment Component](#assessment-component)
- [Analysis Component](#analysis-component)
- [Configuration](#configuration)
- [Models](#models)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Multi-Psychometric Assessment**: Combines Big Five personality model, MBTI, cognitive functions, and additional psychological dimensions
- **AI-Powered Analysis**: Uses LLMs to analyze personality traits from question responses
- **Flexible Model Support**: Compatible with various LLMs (OpenAI, Claude, Ollama, etc.)
- **Comprehensive Output**: Generates detailed personality profiles with confidence scoring
- **Batch Processing**: Supports bulk assessment processing
- **Segmented Analysis**: Advanced multi-step analysis for better accuracy
- **Trustworthy Assessment**: Consensus-based verification system for reliable results
- **Customizable Parameters**: Set various parameters for different assessment scenarios
- **Specialized Analysis**: Big Five, MBTI, Belbin, and custom personality analyses
- **Stress Testing Recommendations**: Tailored stress testing suggestions based on personality profiles

## Components

AgentPsyAssessment is structured around two main components:

### Assessment Component
- Uses LLMs with various parameters to respond to psychological questionnaires
- Configurable parameters for temperature, role-playing, context, etc.
- Supports multiple personality roles and scenarios
- Provides standardized questionnaire administration
- Allows for multiple rounds of testing based on initial results

### Analysis Component  
- Evaluates responses using various psychometric models
- Performs Big Five personality analysis
- Conducts MBTI personality analysis
- Performs Belbin team role analysis
- Creates targeted stress testing recommendations
- Generates confidence scores and validation reports

## Assessment Flow

The assessment process follows a cyclical approach: test, evaluate, targeted test, evaluate, analyze:

1. **Initial Test**: Administer standardized questionnaires to the LLM
2. **Initial Evaluation**: Analyze responses for initial personality profile
3. **Targeted Test**: Administer specific follow-up questions based on initial results
4. **Secondary Evaluation**: Refine personality profile based on targeted questions
5. **Comprehensive Analysis**: Generate detailed psychological report with recommendations

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/ptreezh/AgentPsyAssessment.git
   cd AgentPsyAssessment
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment**:
   
   Copy the example environment file and fill in your API keys:
   
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys
   ```

4. **Install Ollama (optional)** if you plan to use local models:

   Download from [https://ollama.ai](https://ollama.ai) and install according to your system.

## Quick Start

### Basic Assessment
To run a simple assessment with a default configuration:

```bash
python run_assessment_unified.py --model gpt-4o --role a1
```

### Batch Assessment
To run batch assessments:

```bash
python run_batch_suite.py --model claude-3-5-sonnet --roles a1,a2,b1
```

### Using Local Models
To use Ollama models:

```bash
python run_assessment_unified.py --model llama3.1 --ollama
```

## Assessment Component Usage

### Assessment Configuration Options

The assessment component supports multiple configuration options:

- `--model`: LLM model to use (e.g., gpt-4o, claude-3-5-sonnet, llama3.1)
- `--role`: Personality role to apply during assessment (a1-a10, b1-b10, def)
- `--questions`: Path to custom questions JSON file
- `--temperature`: Model temperature (default: 0)
- `--top_p`: Model top_p parameter (default: 0.9)
- `--ollama`: Use Ollama models instead of cloud APIs
- `--host`: Ollama host (default: http://localhost:11434)
- `--context`: Additional context to influence responses

### Running Initial Assessments

```bash
# Basic assessment
python llm_assessment/run_assessment_unified.py --model gpt-4o --role def

# Assessment with specific parameters
python llm_assessment/run_assessment_unified.py --model claude-3-5-sonnet --role a1 --temperature 0.2
```

## Analysis Component Usage

### Analysis Configuration

The analysis component evaluates responses and generates comprehensive reports:

- `--analysis-type`: Type of analysis (bigfive, mbti, belbin, comprehensive)
- `--input`: Path to assessment results to analyze
- `--confidence-threshold`: Confidence threshold for recommendations (default: 0.7)

### Running Analysis

```bash
# Analyze assessment results
python analyze_results.py --input results/assessment_result.json --analysis-type comprehensive

# Generate Big Five analysis
python analyze_big5_results.py --input results/assessment_result.json

# Generate MBTI analysis
python analyze_mbti_results.py --input results/assessment_result.json
```

## Combined Assessment and Analysis Workflow

### Command Line Interface

The project includes both components accessible through the CLI:

```bash
# Run complete assessment and analysis
python cli.py assess --model gpt-4o --role def
python cli.py analyze --input results/latest_assessment.json

# Run assessment with integrated analysis
python cli.py assess --model gpt-4o --role def --analyze
```

### Full Assessment Flow

1. **Initial Test**: Administer standardized questionnaires to the LLM
   ```bash
   python cli.py assess --model gpt-4o --role def
   ```

2. **Initial Evaluation**: Analyze initial responses
   ```bash
   python cli.py analyze --input results/initial_assessment.json
   ```

3. **Targeted Test**: Run follow-up questions based on initial analysis
   ```bash
   python cli.py assess --model gpt-4o --role targeted --context "focus on neuroticism and agreeableness"
   ```

4. **Secondary Evaluation**: Refine personality profile
   ```bash
   python cli.py analyze --input results/targeted_assessment.json
   ```

5. **Comprehensive Analysis**: Generate detailed report
   ```bash
   python cli.py analyze --input results/combined_assessments.json --analysis-type comprehensive
   ```

## Configuration

### Environment Variables

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OLLAMA_HOST=http://localhost:11434
```

### Model Configuration

Model-specific settings can be configured in `config/` directory. Different models may require different parameters for optimal performance.

## Models

The system supports various LLMs with different capabilities:

### Cloud Models
- OpenAI: gpt-4, gpt-4o, gpt-4-turbo
- Anthropic: claude-3-5-sonnet, claude-3-opus, claude-3-sonnet
- Google: gemini-pro, gemini-1.5-pro
- Mistral: mistral-large, mistral-small

### Local Models (Ollama)
- Llama family: llama3.1, llama3.2, llama3
- Mixtral: mixtral-8x7b
- Others: phi3, command-r, deepseek-coder

## Assessment Process

### 1. Input Processing
- Questionnaire input (currently using Big Five 50-item model)
- Personality role application (optional)
- Context preparation for LLM

### 2. LLM Analysis
- Multi-step analysis for complex traits
- Evidence-based reasoning
- Confidence scoring

### 3. Result Synthesis
- Trait extraction and scoring
- Consistency checks
- Final report generation

### 4. Validation
- Cross-model verification (optional)
- Consistency checking
- Result validation

## Results Analysis

### Output Format

Assessment results are saved in JSON format with:

- Personality trait scores (Big Five dimensions)
- MBTI type determination
- Cognitive function preferences
- Confidence scores for each assessment
- Detailed analysis notes

### Analysis Tools

The project includes tools for:

- **Batch Analysis**: Compare results across multiple assessments
- **Reliability Analysis**: Check consistency of results
- **Segmentation Analysis**: Analyze results by question categories
- **Big Five Analysis**: Detailed trait analysis
- **Motivation Analysis**: Motivation and drive assessment

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Guidelines

- Follow the existing code style
- Write clear documentation
- Add tests for new features
- Use descriptive commit messages
- Ensure code passes linting

### Development Setup

For development:

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Format code
black .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- **Project Link**: [https://github.com/ptreezh/AgentPsyAssessment](https://github.com/ptreezh/AgentPsyAssessment)
- **Issues**: [GitHub Issues](https://github.com/ptreezh/AgentPsyAssessment/issues)
- **Email**: [contact@agentpsy.com](mailto:contact@agentpsy.com)
- **WeChat**: 3061176
- **Homepage**: [https://agentpsy.com](https://agentpsy.com)

For support, questions, or collaboration opportunities, please reach out through any of the contact methods above.

## Acknowledgments

- Inspiration from classical psychometric models
- Open source LLM tools for accessible AI
- The psychological research community for foundational work