import os
import json
import subprocess
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import i18n support
from i18n import i18n

# Import the test_model_connectivity function from run_assessment_unified
# Use absolute import with the correct module path
from llm_assessment.run_assessment_unified import test_model_connectivity

# Load config.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        app_config = json.load(f)
    TEST_FILES_CONFIG = app_config.get("test_files", {})
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(i18n.t("Error loading {config_file}: {e}").format(config_file=CONFIG_FILE, e=e), flush=True)
    TEST_FILES_CONFIG = {}


def main():
    """Main function to run the batch test suite based on the new config format."""
    args = sys.argv[1:]
    debug_mode = "--debug" in args
    config_file = next((arg for arg in args if not arg.startswith('--')), "batch_config.json")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(i18n.t("Error loading {config_file}: {e}").format(config_file=config_file, e=e), flush=True)
        sys.exit(1)

    models = {m["name"]: m for m in config.get("models", [])}
    model_name_to_id = {m["name"]: m.get("path", m["name"]) for m in config.get("models", [])}
    test_suites = config.get("test_suites", [])

    print(i18n.t("--- Starting Batch Processing Suite (v2) ---"), flush=True)
    if debug_mode:
        print(i18n.t("*** DEBUG MODE ENABLED ***"), flush=True)

    start_time = datetime.now()
    all_run_results = []
    unavailable_models = set()

    for suite in test_suites:
        suite_name = suite.get("suite_name", i18n.t("Unnamed Suite"))
        print(f"\n===== {i18n.t('Running Test Suite')}: {suite_name} =====\n", flush=True)
        
        suite_output_dir = os.path.join("results", suite_name.replace(' ', '_'))

        for model_name in suite.get("models_to_run", []):
            if model_name not in models:
                print(i18n.t("Warning: Model '{model_name}' not found in config. Skipping.").format(model_name=model_name), flush=True)
                continue
            
            if model_name in unavailable_models:
                print(i18n.t("--- Skipping model {model_name} (previously failed connectivity test) ---").format(model_name=model_name), flush=True)
                continue

            model_config = models[model_name]
            actual_model_id = model_name_to_id[model_name]
            
            print(i18n.t("--- Checking connectivity for model: {model_id} ---").format(model_id=actual_model_id), flush=True)
            if not test_model_connectivity(actual_model_id):
                print(i18n.t("!!! Connectivity test failed for {model_id}. Skipping all tasks for this model. !!!").format(model_id=actual_model_id), flush=True)
                unavailable_models.add(model_name)
                all_run_results.append({"status": "SKIPPED (UNAVAILABLE)", "model": actual_model_id, "task_name": "ALL", "report_path": "N/A"})
                continue
            print(i18n.t("--- Connectivity OK for {model_id} ---").format(model_id=actual_model_id), flush=True)

            model_config["name"] = actual_model_id
            
            for task in suite.get("tasks", []):
                result_summary = run_task(task, model_config, suite_output_dir, debug=debug_mode)
                all_run_results.append(result_summary)
    
    aggregate_results(all_run_results, start_time)

    end_time = datetime.now()
    print(i18n.t("\n--- Batch Processing Suite Finished ---"), flush=True)
    print(i18n.t("**Total execution time:** {duration}").format(duration=end_time - start_time), flush=True)


def normalize_task_config(task_config):
    """Ensures all task parameters have appropriate default values."""
    normalized = task_config.copy()
    
    # Set default values for missing parameters
    if "emotional_stress_level" not in normalized:
        normalized["emotional_stress_level"] = None
        
    if "cognitive_trap_type" not in normalized:
        normalized["cognitive_trap_type"] = None
        
    if "tmpr" not in normalized:
        normalized["tmpr"] = 0.7
        
    if "context_length_mode" not in normalized:
        normalized["context_length_mode"] = "auto"
        
    return normalized

def run_task(task_config, model_config, suite_output_dir, debug=False):
    """Dispatches a single test task to the appropriate runner based on its type."""
    # Normalize task config to ensure default values
    task_config = normalize_task_config(task_config)
    
    task_type = task_config.get("type")
    task_name = task_config.get("task_name", i18n.t("Unnamed Task"))
    test_file = task_config.get("test_file")
    role_file = task_config.get("role_file")
    model_name = model_config.get("name")

    print(i18n.t("--- Running Task: '{task_name}' for Model: '{model_name}' ---").format(task_name=task_name, model_name=model_name), flush=True)

    if not test_file or not model_name:
        print(i18n.t("Error: Task '{task_name}' is missing 'test_file' or model is invalid. Skipping.").format(task_name=task_name), flush=True)
        return {"status": "SKIPPED", "model": model_name, "task_name": task_name, "report_path": "N/A"}

    safe_model_name = model_name.replace("/", "_").replace(":", "_")
    safe_task_name = task_name.replace("/", "_").replace(":", "_").replace(" ", "_")
    run_output_dir = os.path.join(suite_output_dir, f"{safe_model_name}_{safe_task_name}")
    os.makedirs(run_output_dir, exist_ok=True)

    # Instead of using -m, let's call the script directly to avoid module import issues
    command = [sys.executable, os.path.join(os.path.dirname(__file__), "run_assessment_unified.py")]
    
    # Resolve test file path from config if it exists
    if test_file in TEST_FILES_CONFIG:
        resolved_test_file = TEST_FILES_CONFIG[test_file]
    else:
        resolved_test_file = test_file
    
    if task_type == "questionnaire":
        command.extend([
            "--test_file", resolved_test_file,
            "--model_name", model_name
        ])
        if role_file:
            role_name = os.path.splitext(os.path.basename(role_file))[0]
            command.extend(["--role_name", role_name])
    else:
        print(i18n.t("Warning: Unknown task type '{task_type}'. Skipping.").format(task_type=task_type), flush=True)
        return {"status": "SKIPPED", "model": model_name, "task_name": task_name, "report_path": "N/A"}

    # Handle stress testing parameters
    emotional_stress_level = task_config.get("emotional_stress_level")
    if emotional_stress_level is not None:
        command.extend(["-esL", str(emotional_stress_level)])

    cognitive_trap_type = task_config.get("cognitive_trap_type")
    if cognitive_trap_type is not None:
        command.extend(["-ct", cognitive_trap_type])

    context_load_tokens = task_config.get("context_load_tokens")
    if context_load_tokens is not None:
        command.extend(["--context-length-static", str(context_load_tokens // 1024)])

    # Handle enhanced parameters (temperature and context length)
    tmpr = task_config.get("tmpr")
    if tmpr is not None:
        command.extend(["-tmpr", str(tmpr)])

    # Only add context length mode if it's not the default 'auto' value
    context_length_mode = task_config.get("context_length_mode")
    if context_length_mode is not None and context_length_mode != "auto":
        command.extend(["--context-length-mode", str(context_length_mode)])

    context_length_static = task_config.get("context_length_static")
    if context_length_static is not None:
        command.extend(["--context-length-static", str(context_length_static)])

    context_length_dynamic = task_config.get("context_length_dynamic")
    if context_length_dynamic is not None:
        command.extend(["--context-length-dynamic", str(context_length_dynamic)])

    if debug:
        command.append("--debug")

    # 添加重试机制
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(i18n.t("    -> Executing command: {command}").format(command=' '.join(command)), flush=True)
            if retry_count > 0:
                print(i18n.t("    -> Retry attempt {retry_count}/{max_retries}").format(retry_count=retry_count, max_retries=max_retries-1), flush=True)
            # 移除超时限制，允许测评完整执行
            # 实时显示子进程输出
            print(i18n.t("    -> Starting task execution..."), flush=True)
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True, encoding='utf-8', errors='replace')
            
            # 实时输出子进程的stdout
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"      {output.strip()}", flush=True)
            
            # 等待进程结束
            return_code = process.poll()
            
            if return_code == 0:
                print(i18n.t("Task '{task_name}' completed successfully for '{model_name}'.").format(task_name=task_name, model_name=model_name), flush=True)
            else:
                # 读取剩余输出
                remaining_output, _ = process.communicate()
                if remaining_output:
                    print(f"      {remaining_output.strip()}", flush=True)
                raise subprocess.CalledProcessError(return_code, command)
            
            # Point to the directory containing the results
            report_path_placeholder = run_output_dir
            
            return {"status": "SUCCESS", "model": model_name, "task_name": task_name, "report_path": report_path_placeholder}
        except subprocess.CalledProcessError as e:
            retry_count += 1
            print(i18n.t("  !! ERROR running task '{task_name}' for '{model_name}'.").format(task_name=task_name, model_name=model_name), flush=True)
            print(i18n.t("  !! Return Code: {returncode}").format(returncode=e.returncode), flush=True)
            # 错误信息已经在实时输出中显示了，这里不再重复显示
            
            if retry_count < max_retries:
                print(i18n.t("  -> Retrying in 5 seconds..."), flush=True)
                import time
                time.sleep(5)
            else:
                # Clean up empty directory created for this failed test
                try:
                    if os.path.exists(run_output_dir) and not os.listdir(run_output_dir):
                        os.rmdir(run_output_dir)
                        print(i18n.t("  -> Cleaned up empty directory: {dir}").format(dir=run_output_dir), flush=True)
                except OSError as cleanup_error:
                    print(i18n.t("  !! Warning: Could not clean up directory {dir}: {error}").format(dir=run_output_dir, error=cleanup_error), flush=True)
                
                return {"status": "FAILED", "model": model_name, "task_name": task_name, "report_path": "N/A"}
        except Exception as e:
            retry_count += 1
            print(i18n.t("  !! Unexpected ERROR running task '{task_name}' for '{model_name}': {error}").format(task_name=task_name, model_name=model_name, error=str(e)), flush=True)
            
            if retry_count < max_retries:
                print(i18n.t("  -> Retrying in 5 seconds..."), flush=True)
                import time
                time.sleep(5)
            else:
                # Clean up empty directory created for this failed test
                try:
                    if os.path.exists(run_output_dir) and not os.listdir(run_output_dir):
                        os.rmdir(run_output_dir)
                        print(i18n.t("  -> Cleaned up empty directory: {dir}").format(dir=run_output_dir), flush=True)
                except OSError as cleanup_error:
                    print(i18n.t("  !! Warning: Could not clean up directory {dir}: {error}").format(dir=run_output_dir, error=cleanup_error), flush=True)
                
                return {"status": "FAILED", "model": model_name, "task_name": task_name, "report_path": "N/A"}


def aggregate_results(all_run_results, start_time):
    """Aggregates results from all test runs and generates a summary report."""
    end_time = datetime.now()
    print(i18n.t("\n--- Generating Summary Report ---"), flush=True)
    
    lines = []
    lines.append("# " + i18n.t("Batch Suite Summary Report"))
    lines.append("**" + i18n.t("Execution Date:") + "** " + end_time.strftime('%Y-%m-%d %H:%M:%S'))
    lines.append("**" + i18n.t("Total Execution Time:") + "** " + str(end_time - start_time))
    lines.append("\n## " + i18n.t("Run Details") + "\n")
    lines.append("| " + i18n.t("Model") + " | " + i18n.t("Task Name") + " | " + i18n.t("Status") + " | " + i18n.t("Report Link") + " |")
    lines.append("|-------|-----------|--------|-------------|")

    for result in all_run_results:
        status_text = result["status"]
        report_link = result["report_path"]
        # Ensure report_link is a string before calling replace
        report_link_str = str(report_link) if report_link else ""
        display_link = f"[{i18n.t('View Report')}]({report_link_str.replace(os.sep, '/')})" if status_text == "SUCCESS" else "N/A"
        lines.append(f"| {result['model']} | {result['task_name']} | {status_text} | {display_link} |")

    try:
        # Ensure the results directory exists
        os.makedirs("results", exist_ok=True)
        report_path = os.path.join("results", "SUMMARY_REPORT.md")
        with open(report_path, "w", encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(i18n.t("  -> Successfully generated {report_path}").format(report_path=report_path), flush=True)
    except Exception as e:
        print(i18n.t("  !! ERROR: Failed to generate summary report: {e}").format(e=e), flush=True)


if __name__ == "__main__":
    main()