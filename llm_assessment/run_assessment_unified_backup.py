import sys
import os
import json
import argparse
import time
from datetime import datetime
import json5
from dotenv import load_dotenv
import tempfile

# Ensure UTF-8 encoding for stdout/stderr on Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add the project root to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the services directory to the Python path
services_dir = os.path.join(os.path.dirname(__file__), 'services')
sys.path.insert(0, services_dir)

# Import i18n support
from i18n import i18n

# Correct imports from the project root
# When run as a module, we need to adjust the import paths
try:
    from llm_assessment.services.llm_client import LLMClient
    from llm_assessment.services.model_manager import ModelManager
    from llm_assessment.services.stress_injector import StressInjector
    from llm_assessment.services.prompt_builder import PromptBuilder
except ImportError:
    # Fallback to direct imports when run as a script
    from services.llm_client import LLMClient
    from services.model_manager import ModelManager
    from services.stress_injector import StressInjector
    from services.prompt_builder import PromptBuilder

# Import model settings utilities
from llm_assessment.model_settings import (
    parse_tmpr_and_context_args, 
    apply_model_settings,
    get_model_max_context_length,
    calculate_dynamic_context_length,
    determine_context_length
)

# Constants
# Assuming the script is run from the llm_assessment directory, these paths are relative to it.
ROLES_DIR = os.path.join(os.path.dirname(__file__), "roles")
TESTS_DIR = os.path.join(os.path.dirname(__file__), "test_files")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
INTERFERENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "interference_materials")
COGNITIVE_TRAPS_DIR = os.path.join(os.path.dirname(__file__), "..", "interference_materials")
CONTEXT_MATERIALS_DIR = os.path.join(os.path.dirname(__file__), "..", "interference_materials")

# Map of test abbreviations to full filenames
TEST_ABBREVIATIONS = {
    'big5': 'agent-big-five-50-complete.json',
    'graph': 'agent-graph-mapping-35-complete.json'
}


def test_model_connectivity(model_id: str) -> bool:
    """
    Tests connectivity to a given model using the centralized LLMClient.

    Args:
        model_id (str): The identifier of the model to test (e.g., 'ollama/qwen3:4b').

    Returns:
        bool: True if the model is connectable, False otherwise.
    """
    print(i18n.t("Testing connectivity for model: {model_id}").format(model_id=model_id), flush=True)
    try:
        # Use the centralized client, which handles provider logic internally
        client = LLMClient()
        
        # Prepare a simple prompt for the connectivity test
        prompt = [{"role": "user", "content": i18n.t("Hello, are you there?")}]
        
        # Generate a response. The model_id is passed positionally.
        response = client.generate_response(prompt, model_id)
        
        if response and not response.startswith("ERROR:"):
            print(i18n.t("  [OK] Model {model_id} is connectable.").format(model_id=model_id), flush=True)
            # print(i18n.t("    -> Response: {response}...").format(response=response[:80]), flush=True) # Optional: log snippet
            return True
        else:
            print(i18n.t("  [FAIL] Model {model_id} failed to respond.").format(model_id=model_id), flush=True)
            # print(i18n.t("    -> Error: {response}").format(response=response), flush=True)
            return False
    except Exception as e:
        print(i18n.t("  [ERROR] Exception during connectivity test for {model_id}: {e}").format(model_id=model_id, e=e), flush=True)
        return False


def load_test_data(test_file: str) -> dict:
    """
    Loads and parses the test data from a JSON/JSON5 file.

    Args:
        test_file (str): Path to the test data file.

    Returns:
        dict: The parsed test data.
    """
    # If test_file is not an absolute path, construct the full path
    if not os.path.isabs(test_file):
        # Check if test_file already contains 'test_files' to avoid duplication
        if 'test_files' in test_file:
            # If it's already a relative path from llm_assessment, use it directly
            # Remove the 'llm_assessment/' prefix if it exists
            if test_file.startswith('llm_assessment/'):
                test_file = test_file.replace('llm_assessment/', '', 1)
            test_file_path = os.path.join(os.path.dirname(__file__), '..', test_file)
        else:
            # Normalize the path to handle cases like ./test_files/filename.json
            normalized_test_file = os.path.normpath(test_file)
            test_file_path = os.path.join(TESTS_DIR, normalized_test_file)
    else:
        test_file_path = test_file
    
    print(i18n.t("Loading test data from: {test_file_path}").format(test_file_path=test_file_path))  # Debug print
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        if test_file_path.endswith('.json5'):
            return json5.load(f)
        else:
            return json.load(f)


def load_role_prompt(role_name: str) -> str:
    """
    Loads the role prompt from a text file.

    Args:
        role_name (str): Name of the role.

    Returns:
        str: The role prompt content.
    """
    # If role_name is "default" or None/empty, return an empty string for no role loading
    if not role_name or role_name == "default":
        return ""
    
    role_file = os.path.join(ROLES_DIR, f"{role_name}.txt")
    if not os.path.exists(role_file):
        print(i18n.t("Warning: Role file not found: {role_file}. Using empty prompt.").format(role_file=role_file))
        return ""
    
    try:
        with open(role_file, 'r', encoding='utf-8') as f:
            content = f.read()
            return content if content else ""
    except Exception as e:
        print(i18n.t("Warning: Error reading role file {role_file}: {e}. Using empty prompt.").format(role_file=role_file, e=e))
        return ""


def is_empty_result(results):
    """检查测试结果是否为空"""
    # 检查是否存在有效的评估结果
    assessment_results = results.get('assessment_results', [])
    
    # 如果没有评估结果，认为是空结果
    if not assessment_results:
        return True
    
    # 检查每个问题的回答是否为空或无效
    for result in assessment_results:
        # 获取回答内容
        conversation_log = result.get('conversation_log', [])
        # 查找助手的回答
        assistant_responses = [msg for msg in conversation_log if msg.get('role') == 'assistant']
        
        # 如果没有助手回答，认为是无效结果
        if not assistant_responses:
            return True
        
        # 检查是否有至少一个非空回答
        has_valid_response = False
        for resp in assistant_responses:
            content = resp.get('content', '')
            if content and content.strip():
                has_valid_response = True
                break
        
        # 如果没有有效回答，认为是无效结果
        if not has_valid_response:
            return True
    
    return False

def save_results(results: dict, model: str, test_name: str, role_name: str, 
                emotional_stress_level: int = 0, cognitive_trap_type: str = None, 
                context_load_tokens: int = 0, log_file: str = None, error_info: str = None):
    """
    Saves the assessment results to a JSON file with detailed stress factors information.
    This function now always generates a record, even for failed assessments.

    Args:
        results (dict): The assessment results.
        model (str): The model identifier.
        test_name (str): The test name or file.
        role_name (str): The role name.
        emotional_stress_level (int): Emotional stress level (0-4).
        cognitive_trap_type (str): Cognitive trap type ('p', 'c', 's', 'r').
        context_load_tokens (int): Context load in tokens.
        log_file (str): Path to the log file for this assessment.
        error_info (str): Error information if the assessment failed.
    """
    # Add stress factors information to the results metadata
    results['assessment_metadata']['stress_factors_applied'] = {
        'emotional_stress_level': emotional_stress_level,
        'cognitive_trap_type': cognitive_trap_type,
        'context_load_tokens': context_load_tokens
    }
    
    # Add complete model, role, and test information to metadata
    model_str = str(model) if model else "unknown_model"
    test_name_str = str(test_name) if test_name else "unknown_test"
    role_name_str = str(role_name) if role_name else "default"
    
    results['assessment_metadata']['tested_model'] = model_str
    results['assessment_metadata']['role_applied'] = role_name_str
    results['assessment_metadata']['test_name'] = test_name_str
    results['assessment_metadata']['assessment_timestamp'] = datetime.now().isoformat()
    
    # Add log file information and error info if provided
    if log_file:
        results['assessment_metadata']['log_file'] = log_file
    if error_info:
        results['assessment_metadata']['error_info'] = error_info
        results['assessment_metadata']['assessment_status'] = "failed"
    else:
        results['assessment_metadata']['assessment_status'] = "completed"
    
    # Add stress factors information to the results metadata
    results['assessment_metadata']['stress_factors_applied'] = {
        'emotional_stress_level': emotional_stress_level,
        'cognitive_trap_type': cognitive_trap_type,
        'context_load_tokens': context_load_tokens
    }
    
    # Add complete model, role, and test information to metadata
    model_str = str(model) if model else "unknown_model"
    test_name_str = str(test_name) if test_name else "unknown_test"
    role_name_str = str(role_name) if role_name else "default"
    
    results['assessment_metadata']['tested_model'] = model_str
    results['assessment_metadata']['role_applied'] = role_name_str
    results['assessment_metadata']['test_name'] = test_name_str
    results['assessment_metadata']['assessment_timestamp'] = datetime.now().isoformat()
    
    # Create results directory if it doesn't exist
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Generate simplified filename with core information
    # New Format: asses_{model}_{test}_{role}_e{emotional_stress_level}_t{cognitive_trap_type}_{context_load_tokens}_{date}_{sequence}.json
    date_str = datetime.now().strftime("%m%d")
    
    # Ensure all inputs are strings
    model_str = str(model) if model else "unknown_model"
    test_name_str = str(test_name) if test_name else "unknown_test"
    role_name_str = str(role_name) if role_name else "default"
    
    # Simplify model name - handle provider prefix and full model IDs
    if '/' in model_str and model_str.startswith(('ollama/', 'openai/', 'together/', 'openrouter/', 'glm/', 'deepseek/')):
        # Remove provider prefix for local models (e.g., ollama/qwen3:4b -> qwen3)
        model_part = model_str.split('/', 1)[1]  # Get part after provider/
        simplified_model = model_part.split(':')[0].replace('/', '_').replace('\\', '_').replace('-', '_').replace(':', '_')
    else:
        # Keep full model ID for custom models like Yinr/Smegmma:9b
        simplified_model = model_str.replace('/', '_').replace('\\', '_').replace('-', '_').replace(':', '_')
    # Simplify test name (remove extension and special chars)
    simplified_test = os.path.splitext(test_name_str)[0].replace('/', '_').replace('\\', '_').replace('-', '_')
    # Simplify role name
    simplified_role = role_name_str.replace('/', '_').replace('\\', '_').replace('-', '_').replace('default', 'def')
    
    # Simplify cognitive trap type (use single letter or 0 if none)
    trap_type = str(cognitive_trap_type) if cognitive_trap_type else "0"
    
    # Simplify context load tokens representation
    if context_load_tokens:
        if context_load_tokens >= 1024 and context_load_tokens % 1024 == 0:
            context_str = f"{context_load_tokens//1024}k"
        else:
            context_str = str(context_load_tokens)
    else:
        context_str = "0"
    
    # Generate base filename
    base_filename = f"asses_{simplified_model}_{simplified_test}_{simplified_role}_e{emotional_stress_level}_t{trap_type}_{context_str}_{date_str}"
    
    # Handle file sequence numbering to avoid overwrites
    sequence = 1
    filename = f"{base_filename}{sequence}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Ensure proper encoding when printing file path
        try:
            print(i18n.t("Results saved to: {filepath}").format(filepath=filepath))
        except UnicodeEncodeError:
            # Fallback for systems with encoding issues
            print(i18n.t("Results saved to: {filepath}").format(filepath=filepath).encode('utf-8', errors='replace').decode('utf-8'))
        
        # Verify file was created
        if os.path.exists(filepath):
            print(f"File successfully created: {filepath}")
        else:
            print(f"Warning: File may not have been created successfully: {filepath}")
        
        return filepath
    except Exception as e:
        # 如果保存过程中出现错误，删除可能已创建的空文件
        if 'filepath' in locals() and os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Removed empty file: {filepath}")
            except Exception as cleanup_error:
                print(f"Failed to remove empty file: {cleanup_error}")
        
        print(f"Error saving results: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_role_mbti_type(role_name):
    """
    获取角色对应的MBTI类型
    
    Args:
        role_name (str): 角色名称
        
    Returns:
        str: MBTI类型或'Unknown'
    """
    # 角色到MBTI类型的映射字典
    role_mbti_mapping = {
        # A系列角色
        'a1': 'ISTJ', 'a2': 'INFP', 'a3': 'INTJ', 'a4': 'ENTJ', 'a5': 'ESFP',
        'a6': 'ENFP', 'a7': 'ESTP', 'a8': 'ISFP', 'a9': 'INFJ', 'a10': 'ENFJ',
        # B系列角色
        'b1': 'INTJ', 'b2': 'INTP', 'b3': 'ENTJ', 'b4': 'ENTP', 'b5': 'ISTJ',
        'b6': 'ISFJ', 'b7': 'ESTJ', 'b8': 'ESFJ', 'b9': 'ESTP', 'b10': 'ISTP'
    }
    
    # 处理英文版本角色文件
    if role_name and '_en' in role_name:
        base_role = role_name.replace('_en', '')
        return role_mbti_mapping.get(base_role, 'Unknown')
    
    return role_mbti_mapping.get(role_name, 'Unknown')

def run_assessment(client, model_id, test_data, config: dict, debug=False, timeout=0, logger=None):
    """
    Runs the assessment with stress testing capabilities.

    Args:
        client: LLMClient instance.
        model_id (str): Model identifier.
        test_data (dict): Test data.
        config (dict): Configuration dictionary containing all parameters.
        debug (bool): Whether to run in debug mode.
        timeout (int): Timeout for model response in seconds (0 for no timeout).
        logger: AssessmentLogger instance for logging.

    Returns:
        dict: Complete assessment results.
    """
    # Extract parameters from config
    role_name = config.get('role_name')
    emotional_stress_level = config.get('emotional_stress_level', 0)
    cognitive_trap_type = config.get('cognitive_trap_type')
    
    # Enhanced features
    tmpr = config.get('tmpr')
    context_length_mode = config.get('context_length_mode', 'auto')
    context_length_static = config.get('context_length_static', 0)
    context_length_dynamic = config.get('context_length_dynamic', '1/2')

    # Determine the actual context length to use
    context_length_k, context_source = determine_context_length(
        model_id,
        mode=context_length_mode,
        static_param=context_length_static,
        dynamic_ratio=context_length_dynamic
    )
    context_load_tokens = context_length_k * 1024
    
    # 强制0上下文注入：如果静态设置为0或模式为none，则强制为0
    if (context_length_mode == 'static' and context_length_static == 0) or context_length_mode == 'none':
        context_load_tokens = 0
        context_length_k = 0

    debug_mode = config.get('debug', False)
    
    # Use provided logger or create a new one if not provided
    if logger is None:
        from llm_assessment.services.assessment_logger import AssessmentLogger
        logger = AssessmentLogger()
    
    # Initialize other services
    from llm_assessment.services.response_extractor import ResponseExtractor
    
    response_extractor = ResponseExtractor()
    stress_injector = StressInjector(COGNITIVE_TRAPS_DIR, CONTEXT_MATERIALS_DIR)
    
    # Load base role prompt if role_name is provided
    if role_name and role_name != "default":
        base_prompt = load_role_prompt(role_name)
    else:
        base_prompt = ""
    
    # Prepare model options
    model_options = apply_model_settings(client, tmpr=tmpr)

    # Initialize results structure with comprehensive metadata
    results = {
        'assessment_metadata': {
            'model_id': model_id,
            'test_name': config.get('test_file'),
            'role_name': role_name,
            'role_mbti_type': get_role_mbti_type(role_name),  # 新增：角色对应的MBTI类型
            'timestamp': datetime.now().isoformat(),
            'debug_mode': debug_mode,
            'stress_factors_applied': {
                'emotional_stress_level': emotional_stress_level,
                'cognitive_trap_type': cognitive_trap_type,
                'context_load_tokens': context_load_tokens,
                'tmpr': tmpr,
                'context_length_k': context_length_k,
                'context_length_source': context_source,
                'context_length_mode': context_length_mode,  # 新增：上下文长度模式
                'context_length_static': context_length_static,  # 新增：静态上下文长度
                'context_length_dynamic': context_length_dynamic  # 新增：动态上下文比例
            }
        },
        'assessment_results': []
    }
    
    # Process each question in the test bank
    stress_config = {
        'emotional_stress_level': emotional_stress_level,
        'cognitive_trap_type': cognitive_trap_type,
        'context_load_tokens': context_load_tokens
    }
    for i, question in enumerate(test_data['test_bank']):
        # 显示基本进度信息，即使在非调试模式下
        if i % 5 == 0 or i == 0 or i == len(test_data['test_bank']) - 1:  # 每5个问题或第一个/最后一个问题显示进度
            print(i18n.t("Processing question {current}/{total}").format(current=i+1, total=len(test_data['test_bank'])))
        
        if debug_mode:
            print(f"Question ID: {question.get('id', i)}")
            print(f"Question Text: {question.get('question', '')[:100]}...")
        
        # Build conversation with stress injection
        builder = PromptBuilder(base_prompt, question, stress_config, stress_injector)
        conversation_to_send = builder.build_conversation()
        
        # 调试模式下显示发送给模型的对话
        if debug_mode:
            print("\n--- Sending to Model ---")
            for msg in conversation_to_send:
                print(f"{msg['role'].upper()}: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
            print("--- End of Message ---\n")
        
        # Handle multi-turn conversation with context interference in single session
        conversation_log = []
        final_response = ""
        
        if context_load_tokens > 0 and len(conversation_to_send) >= 4:
            # Multi-turn: [system, context_user, context_assistant_placeholder, assessment_user]
            
            # Step 1: Get actual response for context interference
            context_prompt = [conversation_to_send[0], conversation_to_send[1]]  # system + context_user
            if debug_mode:
                print("--- Context Interference Request ---")
                for msg in context_prompt:
                    print(f"{msg['role'].upper()}: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
            
            start_time = time.time()
            try:
                if debug_mode:
                    print(f"Generating context response with timeout={timeout}s")
                context_response = client.generate_response(context_prompt, model_id, options=model_options, timeout=timeout)
                elapsed_time = time.time() - start_time
                if not context_response:
                    context_response = "我已经理解了您分享的内容。"
                if debug_mode:
                    print(f"CONTEXT RESPONSE: {context_response[:200]}{"..." if len(context_response) > 200 else ""}")
                    print(f"Context response generated in {elapsed_time:.2f}s")
            except Exception as e:
                elapsed_time = time.time() - start_time
                context_response = f"我已经理解了您分享的内容。(Error: {str(e)[:50]}...)"
                if debug_mode:
                    print(f"CONTEXT ERROR after {elapsed_time:.2f}s: {e}")
            
            # Step 2: Build complete conversation with actual context response
            complete_conversation = [
                conversation_to_send[0],  # system
                conversation_to_send[1],  # context_user
                {'role': 'assistant', 'content': context_response},  # actual context response
                conversation_to_send[-1]  # assessment_user
            ]
            
            # 调试模式下显示完整对话
            if debug_mode:
                print("\n--- Complete Conversation ---")
                for msg in complete_conversation:
                    print(f"{msg['role'].upper()}: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
                print("--- End of Conversation ---\n")
            
            # Step 3: Send complete conversation and get final response
            # Add retry mechanism for final response
            max_retries = 3
            retry_count = 0
            final_response = None
            
            while retry_count < max_retries and (not final_response or final_response == "[No response generated]"):
                start_time = time.time()
                try:
                    if debug_mode:
                        print(f"Generating final response with timeout={timeout}s (attempt {retry_count + 1}/{max_retries})")
                    final_response = client.generate_response(complete_conversation, model_id, options=model_options, timeout=timeout)
                    elapsed_time = time.time() - start_time
                    
                    # Check if response is valid
                    if not final_response or final_response.strip() == "":
                        final_response = "[No response generated]"
                        if debug_mode:
                            print(f"Empty response received, retrying...")
                    elif final_response == "[No response generated]":
                        if debug_mode:
                            print(f"[No response generated] received, retrying...")
                    else:
                        # Valid response received
                        if debug_mode:
                            print(f"Valid response received, stopping retries.")
                        break  # Exit retry loop on valid response
                        
                    if debug_mode:
                        print(f"FINAL RESPONSE: {final_response[:200]}{"..." if len(final_response) > 200 else ""}")
                        # 增强显示：显示完整响应
                        print(f"FULL FINAL RESPONSE: {final_response}")
                        print(f"Final response generated in {elapsed_time:.2f}s")
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    final_response = f"[Error: {str(e)[:100]}...]"
                    if debug_mode:
                        print(f"FINAL RESPONSE ERROR after {elapsed_time:.2f}s: {e}")
                    # Don't retry on exception
                    break
                
                retry_count += 1
                
            # If all retries failed, set default response
            if not final_response or final_response == "[No response generated]":
                final_response = "[No response generated after retries]"
            
            # Log the complete multi-turn conversation
            conversation_log.extend(complete_conversation)
            conversation_log.append({'role': 'assistant', 'content': final_response})
        else:
            # Single turn conversation (no context load) with retry mechanism
            max_retries = 3
            retry_count = 0
            final_response = None
            
            while retry_count < max_retries and (not final_response or final_response == "[No response generated]"):
                if debug_mode:
                    print("--- Single Turn Request ---")
                    for msg in conversation_to_send:
                        print(f"{msg['role'].upper()}: {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
                
                start_time = time.time()
                try:
                    if debug_mode:
                        print(f"Generating response with timeout={timeout}s (attempt {retry_count + 1}/{max_retries})")
                    final_response = client.generate_response(conversation_to_send, model_id, options=model_options, timeout=timeout)
                    elapsed_time = time.time() - start_time
                    
                    # Check if response is valid
                    if not final_response or final_response.strip() == "":
                        final_response = "[No response generated]"
                        if debug_mode:
                            print(f"Empty response received, retrying...")
                    elif final_response == "[No response generated]":
                        if debug_mode:
                            print(f"[No response generated] received, retrying...")
                    else:
                        # Valid response received
                        if debug_mode:
                            print(f"Valid response received, stopping retries.")
                        break  # Exit retry loop on valid response
                        
                    if debug_mode:
                        print(f"RESPONSE: {final_response[:200]}{"..." if len(final_response) > 200 else ""}")
                        # 增强显示：显示完整响应
                        print(f"FULL RESPONSE: {final_response}")
                        print(f"Response generated in {elapsed_time:.2f}s")
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    final_response = f"[Error: {str(e)[:100]}...]"
                    if debug_mode:
                        print(f"RESPONSE ERROR after {elapsed_time:.2f}s: {e}")
                    # Don't retry on exception
                    break
                
                retry_count += 1
                
            # If all retries failed, set default response
            if not final_response or final_response == "[No response generated]":
                final_response = "[No response generated after retries]"
            
            # Log conversation
            conversation_log.extend(conversation_to_send)
            conversation_log.append({'role': 'assistant', 'content': final_response})
        
        # 调试模式下显示问题处理结果
        if debug_mode:
            print(f"Question {i+1} processed. Response length: {len(final_response)} characters")
            # 增强显示：显示响应预览
            if final_response:
                preview = final_response[:500] + "..." if len(final_response) > 500 else final_response
                print(f"Response preview: {preview}")
            print("-" * 50)
        
        # Extract final response using ResponseExtractor
        final_extracted_response = response_extractor.extract_final_response(conversation_log)
        
        # Log the complete session with full details
        session_id = f"question_{i}_{question.get('id', i)}"
        if logger:
            logger.log_complete_session(
                session_id=session_id,
                conversation=conversation_log,
                extracted_response=final_extracted_response,
                metadata={
                    'question_id': question.get('id', i),
                    'stress_level': config.get('emotional_stress_level', 0),
                    'cognitive_trap': config.get('cognitive_trap_type'),
                    'context_tokens': config.get('context_load_tokens', 0),
                    'role_name': role_name,
                    'model_id': model_id
                }
            )
        
        # Store results with extracted response
        result_entry = {
            'question_id': question.get('id', i),
            'question_data': question,
            'conversation_log': conversation_log,
            'extracted_response': final_extracted_response,
            'session_id': session_id
        }
        results['assessment_results'].append(result_entry)
    
    # 显示完成信息
    print(i18n.t("Completed processing all questions. Generating results..."))
    
    return results


def cleanup_empty_directories():
    """清理空的结果目录"""
    try:
        # 检查results目录是否存在
        if os.path.exists(RESULTS_DIR):
            # 遍历results目录下的所有子目录
            for item in os.listdir(RESULTS_DIR):
                item_path = os.path.join(RESULTS_DIR, item)
                # 如果是目录且为空，则删除
                if os.path.isdir(item_path) and not os.listdir(item_path):
                    try:
                        os.rmdir(item_path)
                        print(f"Removed empty directory: {item_path}")
                    except Exception as e:
                        print(f"Failed to remove empty directory {item_path}: {e}")
    except Exception as e:
        print(f"Error during directory cleanup: {e}")

def main():
    """
    Main entry point for the assessment tool.
    """
    parser = argparse.ArgumentParser(description=i18n.t('Run LLM assessment with advanced stress testing'))
    
    # Original arguments
    parser.add_argument('--model_name', type=str, required=True, 
                       help=i18n.t('Model identifier (e.g., ollama/gemma3:latest)'))
    parser.add_argument('--test_file', type=str, required=True, 
                       help=i18n.t('Test file name or path (e.g., big5, graph, or full path)'))
    parser.add_argument('--role_name', type=str, 
                       help=i18n.t('Role name (e.g., a1, b2)'))
    parser.add_argument('--debug', action='store_true', 
                       help=i18n.t('Enable debug mode'))
    parser.add_argument('--test_connection', action='store_true', 
                       help=i18n.t('Test model connectivity only'))

    # New stress testing arguments
    parser.add_argument('-esL', '--emotional-stress-level', type=int, default=0, choices=range(0, 5),
                       help=i18n.t('Emotional stress level (0-4)'))
    parser.add_argument('-ct', '--cognitive-trap-type', type=str, choices=['p', 'c', 's', 'r'],
                       help=i18n.t('Cognitive trap type: p (paradox), c (circularity), s (semantic_fallacy), r (procedural)'))
    
    # New tmpr and context length arguments
    parser.add_argument('-tmpr', '--tmpr', type=float, default=None,
                       help=i18n.t('Model tmpr setting'))
    parser.add_argument('--context-length-mode', type=str, choices=['auto', 'static', 'dynamic', 'none'], default='auto',
                       help='Context length mode: auto (detect), static (fixed), dynamic (ratio), none (disable context)')
    parser.add_argument('--context-length-static', type=int, default=0,
                       help='Static context length in K (e.g., 2 for 2K, 4 for 4K)')
    parser.add_argument('--context-length-dynamic', type=str, default='1/2',
                       help='Dynamic context length ratio')
    parser.add_argument('--timeout', type=int, default=0,
                       help='Timeout for model response in seconds (0 for no timeout)')

    args = parser.parse_args()
    
    # 添加调试信息
    # print(f"Debug mode: {args.debug}")
    # print(f"Arguments received: {args}")
    
    # Handle test file abbreviation
    if args.test_file in TEST_ABBREVIATIONS:
        test_file_path = os.path.join(TESTS_DIR, TEST_ABBREVIATIONS[args.test_file])
    else:
        if os.path.isabs(args.test_file):
            test_file_path = args.test_file
        else:
            # Check if test_file already contains 'test_files' to avoid duplication
            if 'test_files' in args.test_file:
                # Fix for duplicated path components
                if args.test_file.startswith('llm_assessment/'):
                    test_file_path = os.path.join(os.path.dirname(__file__), args.test_file.replace('llm_assessment/', '', 1))
                else:
                    test_file_path = os.path.join(os.path.dirname(__file__), args.test_file)
            else:
                test_file_path = os.path.join(TESTS_DIR, args.test_file)

    # Test connectivity only if requested
    if args.test_connection:
        success = test_model_connectivity(args.model_name)
        sys.exit(0 if success else 1)
    
    # Load test data
    print(f"Loading test data from: {test_file_path}")
    try:
        test_data = load_test_data(test_file_path)
        print(f"Test data loaded successfully. Number of questions: {len(test_data.get('test_bank', []))}")
    except Exception as e:
        print(i18n.t("Error loading test data: {e}").format(e=e))
        sys.exit(1)
    
    # Initialize LLM client
    print("Initializing LLM client...")
    client = LLMClient()
    print("LLM client initialized successfully.")
    
    # Prepare configuration
    config = {
        'role_name': args.role_name,
        'test_file': args.test_file,
        'emotional_stress_level': args.emotional_stress_level,
        'cognitive_trap_type': args.cognitive_trap_type,
        'tmpr': args.tmpr,
        'context_length_mode': args.context_length_mode,
        'context_length_static': args.context_length_static,
        'context_length_dynamic': args.context_length_dynamic,
        'debug': args.debug
    }
    
    # Display assessment settings
    print(i18n.t("Starting assessment with enhanced factors:"))
    print(f"  {i18n.t('Model')}: {args.model_name}")
    print(f"  {i18n.t('Test')}: {args.test_file}")
    print(f"  {i18n.t('Role')}: {args.role_name}")
    print(f"  {i18n.t('Emotional stress level')}: {args.emotional_stress_level}")
    print(f"  {i18n.t('Cognitive trap type')}: {args.cognitive_trap_type}")
    print(f"  {i18n.t('Model Temperature')}: {args.tmpr if args.tmpr is not None else i18n.t('Default')}")
    print(f"  {i18n.t('Context Length Mode')}: {args.context_length_mode}")
    if args.context_length_mode == 'static':
        print(f"  {i18n.t('Static Context Length')}: {args.context_length_static}K")
    elif args.context_length_mode == 'dynamic':
        print(f"  {i18n.t('Dynamic Context Ratio')}: {args.context_length_dynamic}")
    elif args.context_length_mode == 'none':
        print(f"  {i18n.t('Context Injection')}: Disabled")
    
    # 显示问题数量
    print(i18n.t("Total questions to process: {total}").format(total=len(test_data.get('test_bank', []))))

    # Initialize new services
    from llm_assessment.services.assessment_logger import AssessmentLogger
    from llm_assessment.services.response_extractor import ResponseExtractor
    from llm_assessment.services.session_manager import SessionManager
    
    logger = AssessmentLogger()
    response_extractor = ResponseExtractor()
    session_manager = SessionManager()
    log_file = logger.start_new_log(args.model_name, args.test_file, args.role_name)
    
    try:
        results = run_assessment(client, args.model_name, test_data, config, args.debug, args.timeout, logger)
        
        # Save results
        saved_file = save_results(
            results, 
            args.model_name, 
            args.test_file, 
            args.role_name,
            results['assessment_metadata']['stress_factors_applied']['emotional_stress_level'],
            results['assessment_metadata']['stress_factors_applied']['cognitive_trap_type'],
            results['assessment_metadata']['stress_factors_applied']['context_load_tokens'],
            log_file,
            None  # No error info for successful run
        )
        
        print(i18n.t("Assessment completed successfully!"))
        
        if saved_file:
            print(i18n.t("Results saved to: {saved_file}").format(saved_file=saved_file))
        else:
            print(i18n.t("Failed to save results."))
        print(i18n.t("Log file: {log_file}").format(log_file=log_file))
            
    except Exception as e:
        print(i18n.t("Error during assessment: {e}").format(e=e))
        if args.debug:
            import traceback
            traceback.print_exc()
        
        # Save error information to results file
        error_results = {
            'assessment_results': [],
            'assessment_metadata': {}
        }
        saved_file = save_results(
            error_results,
            args.model_name, 
            args.test_file, 
            args.role_name,
            config.get('emotional_stress_level', 0),
            config.get('cognitive_trap_type'),
            config.get('context_load_tokens', 0),
            log_file,
            str(e)
        )
        
        print(i18n.t("Assessment failed. Error information saved to: {saved_file}").format(saved_file=saved_file))
        print(i18n.t("Log file: {log_file}").format(log_file=log_file))
        
        # 清理空目录
        cleanup_empty_directories()
        # 不直接退出程序，允许其他测试继续执行
        # sys.exit(1)
    
    # 正常结束时也进行清理
    cleanup_empty_directories()


from python_utf8_config import ensure_utf8

if __name__ == "__main__":
    # ensure_utf8()
    main()