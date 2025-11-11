# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentPsyAssessment is a portable, comprehensive psychological assessment framework that combines various psychometric models (Big Five, MBTI, cognitive functions) with AI-powered analysis. The system supports both traditional LLM-based assessment and modern Claude Code skills-based approaches.

## ⚠️ Critical System Separation: 评测 vs 评估

### 📝 Assessment Component (评测系统) - 生成答卷
- **Location**: `llm_assessment/` directory
- **Function**: Uses LLMs to **generate responses** to psychological questionnaires
- **Characteristic**: Single model creative generation, no consensus algorithm needed
- **Entry Point**: `llm_assessment/run_assessment_unified.py`

### 🎯 Evaluation Component (评估系统) - 评分分析
- **Location**: `production_pipelines/local_batch_production/single_report_pipeline/`
- **Function**: **Evaluates generated responses** to generate personality profiles and recommendations
- **Characteristic**: Multi-model evaluation, requires adaptive consensus algorithm for consistency
- **Entry Point**: `production_pipelines/local_batch_production/single_report_pipeline/transparent_pipeline.py`

### 🤖 Skills-Based Assessment System (技能评测系统) - Claude Code专用
- **Location**: `.claude/skills/` directory
- **Function**: Uses Claude Code skills to **generate responses** under various stress conditions
- **Characteristic**: Independent context building, role-playing, stress injection, targeted for Claude's default model
- **Entry Points**:
  - `.claude/skills/questionnaire-answerer/skill.py` - Automated questionnaire answering
  - `.claude/skills/interactive-questionnaire/skill.py` - Interactive assessment

### 🔄 Complete Workflow
1. **Traditional Path**: Generate questionnaire responses using Assessment System → Evaluate responses using Evaluation System
2. **Skills Path**: Use Claude Code skills for direct assessment → Use evaluation skills for scoring
3. **Hybrid Path**: Skills-based generation → Traditional evaluation system

**DO NOT CONFUSE**: These are separate systems with different purposes and target audiences!

## Core Architecture

### Main Entry Points

#### Traditional System
- **`production_pipelines/local_batch_production/cli.py`** - Primary CLI interface with `assess`, `analyze`, and `batch` commands
- **`llm_assessment/run_assessment_unified.py`** - Core assessment engine for individual evaluations
- **`production_pipelines/local_batch_production/run_batch_suite.py`** - Batch processing for multiple assessments

#### Skills-Based System (Claude Code)
- **Natural Language Activation**: Use skills through natural language commands in Claude Code
- **`questionnaire-answerer`**: Automated questionnaire answering under stress conditions
- **`interactive-questionnaire`**: Direct interactive assessment with Claude
- **`psychological-analyzer`**: Response evaluation and scoring (under development)

### Key Architectural Components

#### LLM Service Layer (`llm_assessment/services/`)
- **LLMClient** (`llm_client.py`) - Unified interface for multiple LLM providers (OpenAI, Anthropic, Ollama, Together AI)
- **ModelManager** (`model_manager.py`) - Centralized model management and service creation
- **Model Service Factory** - Abstract factory pattern for provider-agnostic model handling

#### Assessment Engine
- **Questionnaire System** (`test_files/`) - Big Five 50-item assessment, customer service scenarios, cognitive bias tests
- **Role System** (`llm_assessment/roles/`) - Personality role-playing profiles (a1-a10, b1-b10)
- **Prompt Builder** (`prompt_builder.py`) - Dynamic context-aware prompt generation

#### Analysis Engine
- **Big Five Analysis** (`shared_analysis/analyze_big5_results.py`) - OCEAN trait scoring and MBTI mapping
- **Batch Analysis** (`shared_analysis/batch_analysis.py`) - Multi-assessment aggregation and consistency analysis
- **Report Generation** - JSON exports, Markdown reports, statistical summaries

#### Production Pipelines
- **Local Batch Production** (`production_pipelines/local_batch_production/`) - High-throughput batch processing with error recovery
- **Cloud Fallback Enterprise** (`production_pipelines/cloud_fallback_enterprise/`) - Cloud-based processing with local fallback and multi-model consensus

#### Skills-Based Components (`.claude/skills/`)
- **questionnaire-answerer**: Independent questionnaire answering with stress injection
  - Role-playing system (MBTI-based personalities from llm_assessment/roles/)
  - Three-factor stress system (emotional stress, cognitive traps, context filling)
  - Independent context building for each question
  - Comparative stress testing capabilities
- **interactive-questionnaire**: Direct Claude interaction for assessments
  - Real-time conversation with Claude
  - Session management and response collection
  - Role-based personality testing
- **psychological-analyzer**: Response evaluation and scoring (planned)
  - Big Five trait analysis
  - Cognitive bias detection
  - Performance metrics under stress

## Common Development Commands

### Environment Setup
```bash
# Set provider (local or cloud)
export PROVIDER=local  # or cloud

# For local models (Ollama)
export LOCAL_API_BASE=http://localhost:11434
export LOCAL_MODEL_ID=llama3.1

# For cloud models
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

### Skills-Based Assessment (Claude Code)

#### Natural Language Commands
```bash
# Basic questionnaire answering
"请使用问卷答题技能回答中文版agent-citizenship-test-expanded问卷，使用默认角色"

# Stress testing
"请用问卷答题技能在不同压力条件下回答国情问卷的全部题目"

# Interactive assessment
"我想用交互式问卷答题技能进行银行客服Big5人格测试，使用a3角色"
```

#### Advanced Stress Testing
```bash
# Comparative stress analysis
"请生成无压力、中等压力、高压力条件下的完整国情问卷答案对比"

# Role-based stress testing
"请用INTJ人格角色在高认知压力环境下回答历史知识问卷"
```

#### Skills Configuration
- **Emotional Stress**: 0-4 levels (0=none, 1=light, 2=moderate, 3=high, 4=extreme)
- **Cognitive Traps**:
  - 'p' = Paradox traps (逻辑悖论)
  - 'c' = Circular reasoning (循环论证)
  - 's' = Semantic fallacies (语义谬误)
  - 'r' = Procedural traps (程序陷阱)
- **Context Tokens**: 0-5000 tokens for information overload testing

### Single Assessment
```bash
# Local model assessment
python llm_assessment/run_assessment_unified.py --model llama3.1 --role a1

# Cloud model assessment
python llm_assessment/run_assessment_unified.py --model gpt-4o --role def --provider cloud

# With specific parameters
python llm_assessment/run_assessment_unified.py --model claude-3-5-sonnet --role a1 --temperature 0.2
```

### Batch Processing
```bash
# Batch suite with multiple roles
python production_pipelines/local_batch_production/run_batch_suite.py --model llama3.1 --roles a1,a2,b1

# Enhanced batch processing
python batch_processor.py --input-dir results/readonly-original --output-dir results/filtered-results --enhanced

# Optimized batch with limits
python optimized_batch_processor.py --input-dir results/readonly-original --output-dir results/optimized --max-questions 10 --enhanced
```

### Analysis Operations
```bash
# Analyze single assessment
python shared_analysis/analyze_big5_results.py --input results/assessment_result.json

# Batch analysis
python shared_analysis/batch_analysis.py --input-dir results/batch_results --output-dir results/analysis

# Comprehensive analysis
python cli.py analyze --input results/latest_assessment.json --analysis-type comprehensive
```

### Production Pipeline Commands
```bash
# Main CLI operations
python production_pipelines/local_batch_production/cli.py assess --model gpt-4o --role def
python production_pipelines/local_batch_production/cli.py analyze --input results/assessment.json
python production_pipelines/local_batch_production/cli.py batch --model llama3.1 --roles a1,a2,b1

# End-to-end testing
python test_end_to_end_complete.py
python test_optimized_processor.py
```

### Cloud Pipeline Testing
```bash
# Quick cloud test
python quick_cloud_test.py

# Full cloud pipeline test
python test_cloud_pipeline.py

# Transparent pipeline testing
python -c "
from single_report_pipeline.transparent_pipeline import TransparentPipeline
pipeline = TransparentPipeline(use_cloud=True)
# ... test individual components
"
```

## Configuration

### Model Configuration (`config/ollama_config.json`)
- **Local Models**: mistral, phi3_mini, qwen3_4b via Ollama
- **Cloud Models**: glm_4_6_cloud, deepseek_v3_1_cloud, qwen3_vl_cloud, gpt_oss_120b_cloud
- **Evaluators**: Multi-model consensus configuration with dispute resolution
- **Settings**: Temperature, max tokens, timeout configurations

### Role Configuration (`llm_assessment/roles/`)
- **Analytical Roles**: a1-a10 for different personality configurations
- **Behavioral Roles**: b1-b10 for behavioral patterns
- **Multilingual**: Chinese and English variants

### Environment Variables
- **PROVIDER**: `local` or `cloud`
- **LOCAL_API_BASE**: Ollama server URL (default: http://localhost:11434)
- **LOCAL_MODEL_ID**: Default local model identifier
- **Cloud API Keys**: OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.

## System Workflows

### Single Assessment Flow
```
CLI → Assessment Runner → LLM Client → Model Service → Questionnaire → Response Extraction → Result Storage
```

### Batch Processing Flow
```
CLI → Batch Suite → Concurrent Assessment Tasks → Result Collection → Analysis → Aggregation → Report Generation
```

### Multi-Model Evaluation Flow
```
Assessment → Multiple Model Evaluation → Consensus Building → Reliability Scoring → Final Report
```

## Data Processing and Results

### Input Formats
- **Assessment Results**: JSON files with questionnaire responses and metadata
- **Batch Directories**: Collections of assessment results for bulk processing
- **Configuration Files**: Model settings, role definitions, analysis parameters

### Output Formats
- **Evaluation Results**: JSON with Big Five scores, MBTI types, confidence metrics
- **Analysis Reports**: Comprehensive personality profiles with recommendations
- **Batch Summaries**: Statistical aggregations across multiple assessments

### Key Result Locations
- **Raw Results**: `results/readonly-original/` - Original assessment data
- **Processed Results**: `results/ok/evaluated/` - Analyzed evaluation results
- **Batch Analysis**: `results/final-*-batch-analysis/` - Batch processing outputs
- **Skills Results**: `.claude/skills/*/results/` - Skills-based assessment outputs
  - `questionnaire-answerer/results/` - Automated questionnaire responses
  - `interactive-questionnaire/results/` - Interactive session data
- **Stress Test Datasets**: Comparative data files with timestamps for analysis

## Development Notes

### Error Handling and Recovery
- **Retry Mechanisms**: Multiple retry attempts with exponential backoff
- **Fallback Systems**: Cloud models fallback to local models on failure
- **Checkpoint System**: Resume processing from intermediate states
- **Quality Validation**: Cross-model verification and reliability scoring

### Concurrent Processing
- **Multi-threading**: Concurrent assessment processing for batch operations
- **Resource Management**: Optimized model usage and API rate limiting
- **Memory Efficiency**: Streaming processing for large datasets

### Quality Assurance
- **Multi-Model Consensus**: Multiple models evaluate same responses for reliability
- **Statistical Validation**: Consistency checks and confidence scoring
- **Result Verification**: Cross-validation between different evaluation methods

## Testing and Validation

### Unit Testing
```bash
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_modular_integration.py
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_complete_flow.py
```

### Integration Testing
```bash
python test_end_to_end_complete.py
python test_optimized_processor.py
python test_cloud_pipeline.py
```

### Pipeline Validation
```bash
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/validate_complete_system.py
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/validate_enhanced_features.py
```

## Performance Optimization

### Batch Processing Optimization
- Use `--max-questions` to limit processing scope for testing
- Enable `--enhanced` mode for improved accuracy
- Configure appropriate concurrency limits based on API rate limits

### Memory Management
- Process large datasets in chunks
- Use streaming for file operations
- Monitor resource usage during batch operations

### Model Selection Guidelines
- **Local Models**: Faster processing, limited capabilities, suitable for testing
- **Cloud Models**: Higher accuracy, API costs, suitable for production
- **Hybrid Approach**: Cloud models with local fallback for reliability

## Troubleshooting

### Common Issues
- **Model Loading**: Check Ollama service status and model availability
- **API Authentication**: Verify environment variables and API keys
- **Memory Issues**: Reduce batch size or enable checkpoint processing
- **Network Timeouts**: Increase timeout values for large assessments

### Debug Commands
```bash
# Check model availability
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/test_available_models.py

# Debug individual components
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/debug_reverse_logic.py

# Validate pipeline integrity
python production_pipelines/cloud_fallback_enterprise/single_report_pipeline/validate_pipeline_real_data.py
```

### Log Analysis
- Assessment logs include detailed error information and retry attempts
- Batch processing logs provide progress tracking and performance metrics
- Cloud fallback logs help identify provider-specific issues

## Internationalization

The system supports both Chinese and English:
- **Multilingual Roles**: Role configurations available in both languages
- **Localized Prompts**: Context-aware prompts based on language preference
- **Unicode Support**: Full UTF-8 support for international characters
- **Cultural Adaptation**: Assessment questions adapted for different cultural contexts