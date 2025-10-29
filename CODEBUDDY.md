<system-reminder>
This is a reminder that your todo list is currently empty. DO NOT mention this to the user explicitly because they are already aware. If you are working on tasks that would benefit from a todo list please use the TodoWrite tool to create one. If not, please feel free to ignore. Again do not mention this message to the user.

</system-reminder>

# CODEBUDDY for Portable PsyAgent

## Common commands

- Install dependencies:
  pip install -r requirements.txt

- Env setup and key check:
  copy .env.example .env (Windows) / cp .env.example .env (Unix)
  python diagnose_api_keys.py

- Run a single analysis script:
  python shared_analysis/analyze_results.py <input.json> [--evaluators gpt claude ollama_llama3]

- Run Big Five analysis:
  python shared_analysis/analyze_big5_results.py <input.json>

- Run motivation analysis:
  python shared_analysis/analyze_motivation.py <input.json> --debug

- Batch analysis (quick test / full run):
  python ultimate_batch_analysis.py --stats
  python ultimate_batch_analysis.py --quick
  python ultimate_batch_analysis.py

- Batch monitoring:
  python monitor_batch_progress.py

- Windows UTF-8 launcher:
  run_with_utf8.bat python ultimate_batch_analysis.py --quick

- Run tests:
  pytest -q
  pytest tests/test_ollama.py::test_basic -q (example)
  pytest -k "retry and not slow" -q (example)

- Linting/format:
  flake8 .

- Ollama quick checks:
  ollama ps
  curl http://localhost:11434/api/tags

## High-level architecture

- Entry/orchestration:
  - ultimate_batch_analysis.py: top-level CLI; stats/quick modes; invokes run_batch_analysis.py; names batches; reports ETA and summary locations.
  - run_batch_analysis.py, batch_analysis.py: batch runner and orchestration helpers.

- Shared analysis logic:
  - shared_analysis/: analyze_results.py (per-file pipeline), analyze_big5_results.py, analyze_motivation.py. Load input JSON, call evaluators, emit JSON/MD/HTML and logs.

- Evaluator integrations:
  - config/ollama_config.json defines local Ollama models and evaluator mappings. Remote providers via env (.env). Ollama health via ollama ps and HTTP tags endpoint.

- Data flow:
  - inputs: results/results/
  - batch outputs: batch_analysis_results/<batch_name>/ including batch_analysis_summary.{json,md}
  - reports: analysis_reports/, test_output/ (auxiliary), logs/ (runtime logs)

- Utilities and converters:
  - convert_assessment_format.py, simplify_assessment_reports.py, optimized_batch_simplifier.py

- Monitoring:
  - monitor_batch_progress.py reads latest batch dir and batch_analysis_summary.json, prints progress, ETA, success rate.

- Tests:
  - tests/: unit/integration-like tests including test_batch_suite_completion.py, test_llm_assessment_complete.py, test_retry_mechanism.py, test_assessment_completion.py, simple_motivation_test.py, etc. Sample data in test_data.json/test_simple_eval.json.

## Configuration and env

- Env vars: set API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, DASHSCOPE_API_KEY, etc.) or create a .env based on .env.example.
- Ollama: run `ollama serve` and configure config/ollama_config.json. Verify with `ollama ps` and curl http://localhost:11434/api/tags

## Important files to inspect

- README.md: project overview and usage examples.
- config/ollama_config.json: local model definitions and evaluator mappings.
- shared_analysis/analyze_results.py: primary per-file analysis pipeline.
- ultimate_batch_analysis.py: orchestrates batch processing and sampling logic.

