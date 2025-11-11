# 🚀 AgentPsyAssessment v2.0.0

**AgentPsyAssessment** is a portable, comprehensive psychological assessment framework that combines various psychometric models (Big Five, MBTI, cognitive functions, and more) with AI-powered analysis. The framework provides unified assessment skills supporting 6 professional evaluation types with intelligent type detection and multi-language support.

### 🆕 v2.0.0 Major Features
- ✨ **Unified Assessment Skills System** - Configuration-driven architecture supporting 6 professional evaluation types
- 🤖 **Intelligent Type Detection** - Automatic assessment type identification without manual configuration
- 📊 **Interactive HTML Reports** - Chart.js-powered visualization with responsive design
- 🌍 **Multi-language Support** - Chinese, English, German, French, Russian, Japanese, Spanish
- 🎭 **16 MBTI Personalities** - Comprehensive personality profiling with Big Five mapping
- 🚀 **Optimized Performance Engine** - Async processing, intelligent caching, and enhanced metrics
- ⚡ **Smart Configuration Management** - Auto-validation, parameter adjustment, and fault tolerance

## 📋 Table of Contents
- [🌟 Core Features](#-core-features)
- [🏗️ System Architecture](#️-system-architecture)
- [⚡ Installation](#-installation)
- [🚀 Quick Start (5-Minute Experience)](#-quick-start-5-minute-experience)
- [🧠 Assessment Types](#-assessment-types)
- [📊 Usage Examples](#-usage-examples)
- [⚙️ Configuration](#️-configuration)
- [🤖 Models](#-models)
- [🌍 Multi-language Support](#-multi-language-support)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#license)
- [📞 Contact](#contact)

## 🌟 Core Features

### Unified Assessment System v1.0
- **🧠 6 Professional Evaluation Types**: Big Five Personality, Citizenship Knowledge, Financial Professional, Legal Knowledge, Motivation Psychology, Political Literacy
- **🤖 Intelligent Type Detection**: Automatic assessment type identification from questionnaire content
- **📊 Interactive HTML Reports**: Chart.js visualization with responsive design and professional styling
- **🎭 16 MBTI Personalities**: Comprehensive personality profiling with detailed trait analysis
- **🌍 Multi-language Support**: Full interface localization (Chinese, English, German, French, Russian, Japanese, Spanish)
- **⚙️ Configuration-Driven**: JSON-based configuration system for flexible assessment types

### Advanced Assessment Capabilities
- **Multi-Psychometric Assessment**: Combines Big Five personality model, MBTI, cognitive functions, and specialized domains
- **AI-Powered Analysis**: Uses LLMs to analyze personality traits from question responses
- **Flexible Model Support**: Compatible with various LLMs (OpenAI, Claude, Ollama, local models)
- **Comprehensive Output**: Generates detailed personality profiles with confidence scoring
- **Batch Processing**: Supports bulk assessment processing with error recovery
- **Consensus-Based Verification**: Multi-model evaluation for reliable results
- **Specialized Analysis**: Domain-specific assessments for professional contexts

## 🏗️ System Architecture

### 🎯 Unified Assessment Skills System (v1.0)
```
.claude/skills/unified-assessment-system/
├── 📋 config_validator.py           # Configuration validation
├── 🔍 assessment_detector.py        # Intelligent assessment type detection
├── 🏗️ skill_base.py                 # Base skill architecture
├── 📝 unified_questionnaire_responder.py    # Unified questionnaire responder
├── 📊 unified_psychological_analyzer.py    # Unified psychological analyzer
├── 📄 unified_report_generator.py          # Unified report generator
└── 📁 configs/                       # Assessment type configurations
    ├── big_five_personality.json     # Big Five personality evaluation
    ├── citizenship_knowledge.json   # Citizenship knowledge evaluation
    ├── financial_professional.json  # Financial professional evaluation
    ├── legal_knowledge.json         # Legal knowledge evaluation
    ├── motivation_psychology.json   # Motivation psychology evaluation
    └── political_literacy.json      # Political literacy evaluation
```

### 📝 Assessment Component (评测系统)
- Uses LLMs to **generate responses** to psychological questionnaires
- Configurable parameters for temperature, role-playing, context, stress levels
- Supports 16 MBTI personality profiles with Big Five tendencies mapping
- Provides standardized questionnaire administration for 6 assessment types
- Multi-language support with cultural adaptation

### 🎯 Analysis Component (评估系统)
- **Evaluates generated responses** using scientific psychometric methods
- Performs Big Five personality scoring with MBTI type inference
- Conducts domain-specific analysis for professional contexts
- Creates interactive HTML reports with Chart.js visualization
- Generates confidence scores and validation reports
- Session-based evaluation with adaptive consensus algorithms

## Assessment Flow

The assessment process follows a cyclical approach: test, evaluate, targeted test, evaluate, analyze:

1. **Initial Test**: Administer standardized questionnaires to the LLM
2. **Initial Evaluation**: Analyze responses for initial personality profile
3. **Targeted Test**: Administer specific follow-up questions based on initial results
4. **Secondary Evaluation**: Refine personality profile based on targeted questions
5. **Comprehensive Analysis**: Generate detailed psychological report with recommendations

## ⚡ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ptreezh/AgentPsyAssessment.git
cd AgentPsyAssessment
```

### 2. Python Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv psyagent-env

# Windows
psyagent-env\Scripts\activate

# Linux/macOS
source psyagent-env/bin/activate

# Install dependencies
pip install -r requirements.txt  # if available
pip install ollama requests numpy pandas
```

### 3. Environment Variables Configuration
```bash
# Set provider (local or cloud)
export PROVIDER="local"  # or "cloud"

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"

# macOS/Linux
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### 4. Verify Installation
```bash
# Run unified assessment system tests
cd .claude/skills/unified-assessment-system
python test_runner.py

# Expected output: 🎉 ALL TESTS PASSED!
```

### 5. Install Ollama (Optional)
If you plan to use local models:

Download from [https://ollama.ai](https://ollama.ai) and install according to your system.

```bash
# Start Ollama service
ollama serve

# Download recommended models
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull mistral-nemo:latest
ollama pull llama3:latest
```

## 🚀 Quick Start (5-Minute Experience)

### 🎯 Unified Skills System Test
```bash
# Test unified assessment system (v1.0)
cd .claude/skills/unified-assessment-system
python test_runner.py

# Expected output: 🎉 ALL TESTS PASSED!
```

### 📝 Method 1: Quick Assessment Experience
```bash
# 1. Experience questionnaire generation
python llm_assessment/run_assessment_unified.py \
    --model_name def \
    --test_file llm_assessment/test_files/single_test_question_10.json \
    --role_name def \
    --tmpr 0.7

# 2. Experience batch analysis
python production_pipelines/local_batch_production/cli.py \
    assess --model gpt-4o --role def

# 3. View results
ls results/
```

### 🤖 Method 2: Local Model Experience
```bash
# Start Ollama (if using local models)
ollama serve

# Download model
ollama pull llama3.1

# Run local evaluation
python llm_assessment/run_assessment_unified.py \
    --model llama3.1 \
    --role a1 \
    --provider local
```

### 🎭 Method 3: Skills Demo Experience
```bash
# Run skills demo
python skills_demo_chinese_questionnaire.py

# View generated HTML reports
ls html/
```

### 🌐 Multi-language Quick Start Guides
- 📖 [English Guide](docs/en/QUICK_START_GUIDE.md)
- 🇩🇪 [German Guide](docs/de/QUICK_START_GUIDE.md)
- 🇫🇷 [French Guide](docs/fr/QUICK_START_GUIDE.md)
- 🇷🇺 [Russian Guide](docs/ru/QUICK_START_GUIDE.md)
- 🇯🇵 [Japanese Guide](docs/ja/QUICK_START_GUIDE.md)
- 🇪🇸 [Spanish Guide](docs/es/QUICK_START_GUIDE.md)
- 🇨🇳 [Chinese Guide](QUICK_START_GUIDE.md)

## 🧠 Assessment Types

### 1. Big Five Personality Evaluation 🎭
- **File Pattern**: `*big_five*`, `*personality*`, `*ocean*`
- **Dimensions**: Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- **Output**: MBTI type inference + Big Five scoring + 16 personality profiles
- **Use Case**: General personality assessment and team compatibility analysis

### 2. Citizenship Knowledge Evaluation 🏛️
- **File Pattern**: `*citizenship*`, `*公民*`
- **Focus**: Civic rights & obligations, political system awareness
- **Output**: Civic literacy score + political knowledge assessment
- **Use Case**: Citizenship education and civic engagement evaluation

### 3. Financial Professional Evaluation 💰
- **File Pattern**: `*financial*`, `*金融*`, `*bank*`
- **Focus**: Financial expertise, risk identification capabilities
- **Output**: Financial competency score + risk assessment profile
- **Use Case**: Financial industry recruitment and skill assessment

### 4. Legal Knowledge Evaluation ⚖️
- **File Pattern**: `*legal*`, `*law*`, `*法律*`
- **Focus**: Legal foundations, practical operational capabilities
- **Output**: Legal knowledge score + practical judgment assessment
- **Use Case**: Legal profession evaluation and compliance assessment

### 5. Motivation Psychology Evaluation 🎯
- **File Pattern**: `*motivation*`, `*动机*`
- **Focus**: Achievement motivation, power motivation, affiliation motivation
- **Output**: Motivation profile + drive pattern analysis
- **Use Case**: Career counseling and team motivation analysis

### 6. Political Literacy Evaluation 📊
- **File Pattern**: `*political*`, `*政治*`
- **Focus**: Political system awareness, critical thinking
- **Output**: Political literacy score + analytical capability assessment
- **Use Case**: Political education and civic competency evaluation

## 📊 Usage Examples

### Unified Skills System Usage
```bash
# Test unified assessment system
cd .claude/skills/unified-assessment-system
python test_runner.py

# Expected output:
# ✅ PASS Configuration System (6/6 configs loaded)
# ✅ PASS Assessment Detection (2/2 detections successful)
# ✅ PASS Questionnaire Response (Generated 2 responses)
# ✅ PASS Psychological Analysis (Big Five + MBTI analysis)
# ✅ PASS Report Generation (HTML report generated)
# 🎉 ALL TESTS PASSED!
```

### Individual Assessment Examples
```bash
# Big Five personality assessment
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-big-five-50-complete2.json \
    --model_name gpt-4o --role_name enfj

# Citizenship knowledge assessment
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-citizenship-test.json \
    --model_name claude-3-5-sonnet --role_name def

# Financial professional assessment
python llm_assessment/run_assessment_unified.py \
    --test_file llm_assessment/test_files/agent-fund-management-test.json \
    --model_name llama3.1 --role_name a1 --provider local
```

### Batch Processing Examples
```bash
# Multiple roles batch processing
python production_pipelines/local_batch_production/run_batch_suite.py \
    --model llama3.1 --roles a1,a2,b1

# Enhanced batch analysis
python production_pipelines/local_batch_production/cli.py \
    analyze --input results/latest_batch.json

# Generate HTML reports
python generate_all_html_reports.py
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

## 🌍 Multi-language Support

AgentPsyAssessment provides comprehensive multi-language support:

### 📚 Available Languages
- **🇨🇳 Chinese** (Simplified) - Primary documentation and interface
- **🇺🇸 English** - Full documentation and interface support
- **🇩🇪 German** - Complete documentation translation
- **🇫🇷 French** - Comprehensive user guides
- **🇷🇺 Russian** - Full localized documentation
- **🇯🇵 Japanese** - Complete user manual and guides
- **🇪🇸 Spanish** - Comprehensive documentation

### 🌐 Multi-language Features
- **Localized Interface**: All UI elements translated
- **Cultural Adaptation**: Assessment questions adapted for cultural contexts
- **Regional Content**: Domain-specific examples localized by region
- **Language Detection**: Automatic language detection from questionnaire content
- **Unicode Support**: Full UTF-8 support for international characters

### 📖 Multi-language Documentation
```bash
# Access language-specific documentation
docs/en/QUICK_START_GUIDE.md    # English
docs/de/QUICK_START_GUIDE.md    # German
docs/fr/QUICK_START_GUIDE.md    # French
docs/ru/QUICK_START_GUIDE.md    # Russian
docs/ja/QUICK_START_GUIDE.md    # Japanese
docs/es/QUICK_START_GUIDE.md    # Spanish
QUICK_START_GUIDE.md             # Chinese (primary)
```

## 📚 Documentation

### 🎯 Essential Reading
- **📘 [User Manual](USER_MANUAL.md)** - Comprehensive system documentation
- **🚀 [Quick Start Guide](QUICK_START_GUIDE.md)** - 5-minute setup and experience
- **🏗️ [System Architecture](CLAUDE.md)** - Technical architecture and development guide

### 📋 Specialized Guides
- **🔧 [Configuration Guide](docs/CONFIGURATION_GUIDE.md)** - Detailed configuration options
- **🧠 [Assessment Types Guide](docs/ASSESSMENT_TYPES.md)** - All 6 evaluation types explained
- **📊 [Report Generation Guide](docs/REPORT_GENERATION.md)** - HTML report customization
- **🌐 [Multi-language Guide](docs/MULTILINGUAL_SUPPORT.md)** - Internationalization features

### 🛠️ Advanced Documentation
- **🔌 [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md)** - Extending the system
- **📊 [Batch Processing Tutorial](docs/BATCH_PROCESSING.md)** - Large-scale assessment
- **☁️ [Cloud Deployment Guide](docs/CLOUD_DEPLOYMENT.md)** - Production deployment
- **🧪 [Testing Guide](docs/TESTING_GUIDE.md)** - System testing and validation

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🔄 Development Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### 📝 Contribution Guidelines
- Follow the existing code style and architectural patterns
- Write clear documentation for new features
- Add comprehensive tests for new functionality
- Use descriptive commit messages with proper formatting
- Ensure code passes linting and all tests
- Update relevant documentation when adding features

### 🧪 Development Setup
```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Format code
black .

# Validate unified system
cd .claude/skills/unified-assessment-system
python test_runner.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

### 🌐 Online Resources
- **🏠 Project Homepage**: [https://agentpsy.com](https://agentpsy.com)
- **📦 GitHub Repository**: [https://github.com/ptreezh/AgentPsyAssessment](https://github.com/ptreezh/AgentPsyAssessment)
- **🐛 Issue Tracking**: [GitHub Issues](https://github.com/ptreezh/AgentPsyAssessment/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/ptreezh/AgentPsyAssessment/discussions)

### 📧 Direct Contact
- **📧 Email**: [contact@agentpsy.com](mailto:contact@agentpsy.com)
- **💬 WeChat**: 3061176

### 🤝 Community & Support
For support, questions, or collaboration opportunities:
- 📖 Check the [User Manual](USER_MANUAL.md) first
- 🐛 Search existing [GitHub Issues](https://github.com/ptreezh/AgentPsyAssessment/issues)
- 💬 Join our [GitHub Discussions](https://github.com/ptreezh/AgentPsyAssessment/discussions)
- 📧 Contact us directly for urgent matters

## 🙏 Acknowledgments

- **🧠 Psychological Research Community** - For foundational psychometric models and research
- **🤖 Open Source AI Community** - For making powerful LLMs accessible
- **🌍 International Contributors** - For multi-language support and cultural adaptation
- **📚 Documentation Contributors** - For comprehensive guides and tutorials
- **🧪 Testing Community** - For ensuring system reliability and validation

---

**🎉 Thank you for using AgentPsyAssessment v1.0!**

*Version: v1.0.0 | Updated: 2025-01-08 | Team: AgentPsyAssessment Development Team*