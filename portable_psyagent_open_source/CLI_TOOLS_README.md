# Portable PsyAgent - Open Source Release

This is the open source release of the Portable PsyAgent system for conducting psychological assessments using AI models.

## Main Scripts

### Interactive CLI
- `interactive_cli_runner.py` - Interactive command-line interface for running assessments
- `psy2-ha-cli.py` - Main entry point for the Psy2 Human Assessment CLI
- `psy2_cli_demo.py` - CLI demonstration script

### Batch Assessment Scripts
- `batch_analysis.py` - Core batch analysis functionality
- `interactive_batch.py` - Interactive batch processing with user configuration
- `interactive_batch_runner.py` - Interactive batch processing with user feedback
- `interactive_config_generator.py` - Interactive configuration generator for assessments
- `quick_batch.py` - Quick batch processing script
- `run_batch_suite.py` - Batch suite runner for comprehensive analysis

### Assessment Scripts
- `run_assessment_unified.py` - Unified assessment runner
- `run_assessment_config.py` - Configurable assessment runner
- `run_robust_assessment.py` - Robust assessment runner with error handling
- `analyze_results.py` - Core analysis functionality
- `analyze_big5_results.py` - Big Five personality analysis
- `segmented_analysis.py` - Segmented analysis for large datasets

### Configuration
- `config/ollama_config.json` - Ollama model configuration
- `llm_assessment/roles/` - Role definitions for assessments
- `llm_assessment/test_files/` - Sample test files

## Usage

### Interactive Mode
```bash
python interactive_cli_runner.py
```

### Batch Processing
```bash
python run_batch_suite.py
```

### Quick Assessment
```bash
python run_assessment_unified.py --model ollama_mistral --test-file agent-big-five-50-complete2.json
```

## Prerequisites

- Python 3.8+
- Required packages in requirements.txt
- For local Ollama models: Ollama service running with models installed

## Configuration

Before using the tools, configure your Ollama models in `config/ollama_config.json` or set environment variables for cloud models.

## Important Notes

- This system is designed for research and educational purposes only
- Always validate results with professional expertise
- Be mindful of privacy and ethical considerations when using psychological assessment tools