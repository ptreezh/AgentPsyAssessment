# Portable PsyAgent Quick Start Guide

## 1. Introduction

Portable PsyAgent is a portable psychological assessment agent system that supports multi-dimensional personality assessment, analysis evaluation, and stress testing of AI agents. This guide will help you quickly get started with the system.

## 2. System Requirements

- Python 3.8 or higher
- Windows, Linux, or macOS operating system
- Ollama (recommended for local models)

## 3. Installation Steps

### 3.1 Clone the Project

```bash
git clone <repository_url>
cd portable_psyagent
```

### 3.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3.3 Install Ollama (Recommended)

#### Windows
Download from https://ollama.ai/download

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

### 3.4 Download Recommended Models

```bash
# Start Ollama service
ollama serve

# In a new terminal window, download models
ollama pull llama3:latest
ollama pull qwen3:8b
```

## 4. Quick Assessment

### 4.1 Run Basic Assessment

```bash
python llm_assessment/run_assessment_unified.py --model_name llama3:latest --test_file big5 --role_name a1
```

### 4.2 View Assessment Results

Assessment results will be saved in the `llm_assessment/results/` directory.

## 5. Quick Analysis

### 5.1 Run Personality Analysis

```bash
python shared_analysis/analyze_results.py llm_assessment/results/your_result_file.json
```

### 5.2 View Analysis Report

Analysis reports will be generated in the `analysis_reports/` directory in both JSON and Markdown formats.

## 6. Stress Testing Example

### 6.1 Run Assessment with Stress Testing

```bash
python llm_assessment/run_assessment_unified.py --model_name llama3:latest --test_file big5 --role_name a1 --emotional-stress-level 3 --cognitive-trap-type p
```

### 6.2 Parameter Description

- `--emotional-stress-level`: Emotional stress level (0-4)
- `--cognitive-trap-type`: Cognitive trap type
  - `p`: Paradox trap
  - `c`: Circularity trap
  - `s`: Semantic fallacy trap
  - `r`: Procedural trap

## 7. Batch Processing

### 7.1 Quick Batch Analysis

```bash
python ultimate_batch_analysis.py --quick
```

### 7.2 Complete Batch Analysis

```bash
python ultimate_batch_analysis.py
```

## 8. Common Issues

### 8.1 Ollama Connection Failure

Check if Ollama service is running:
```bash
ollama ps
```

### 8.2 Model Not Found

Ensure the model is downloaded:
```bash
ollama list
```

### 8.3 Insufficient Memory

Reduce batch processing size:
```bash
python ultimate_batch_analysis.py --sample 5
```

## 9. Getting Help

For more help, please refer to the complete user manual or submit an issue.

## License

This project is for research and educational purposes only.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.