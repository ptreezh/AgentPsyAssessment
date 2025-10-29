#!/usr/bin/env python3
"""
基于统一配置的LLM评估工具
实现默认无参数无注入优先原则
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入新的配置系统
from dataclasses import asdict
from llm_assessment.config.assessment_config import config_manager, AssessmentConfig
from llm_assessment.services.llm_client import LLMClient
from llm_assessment.services.model_manager import ModelManager
from llm_assessment.services.stress_injector import StressInjector
from llm_assessment.services.prompt_builder import PromptBuilder
from llm_assessment.services.assessment_logger import AssessmentLogger
from llm_assessment.services.response_extractor import ResponseExtractor
from llm_assessment.services.session_manager import SessionManager
from llm_assessment.model_settings import apply_model_settings

# 常量定义
RESULTS_DIR = project_root / "results"
TESTS_DIR = project_root / "test_files"
ROLES_DIR = project_root / "roles"
COGNITIVE_TRAPS_DIR = project_root / "interference_materials"
CONTEXT_MATERIALS_DIR = project_root / "interference_materials"

# 确保目录存在
RESULTS_DIR.mkdir(exist_ok=True)


def load_test_data(test_file: str) -> dict:
    """加载测试数据"""
    test_file_path = Path(test_file)
    
    # 处理相对路径
    if not test_file_path.is_absolute():
        # 检查是否是相对于项目根目录的路径
        if str(test_file_path).startswith('llm_assessment/'):
            test_file_path = project_root / test_file_path
        else:
            # 相对于test_files目录
            test_file_path = project_root / "llm_assessment" / "test_files" / test_file_path.name
    
    if not test_file_path.exists():
        # 尝试其他可能的路径
        alt_path = project_root / test_file_path
        if alt_path.exists():
            test_file_path = alt_path
        else:
            raise FileNotFoundError(f"测试文件不存在: {test_file_path}")
    
    with open(test_file_path, 'r', encoding='utf-8') as f:
        if test_file_path.suffix == '.json5':
            import json5
            return json5.load(f)
        else:
            return json.load(f)


def load_role_prompt(role_name: str) -> str:
    """加载角色提示"""
    if not role_name or role_name == "default":
        return ""
    
    role_file = ROLES_DIR / f"{role_name}.txt"
    if not role_file.exists():
        return ""
    
    try:
        with open(role_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def save_results(results: dict, config: AssessmentConfig) -> str:
    """保存结果"""
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    
    # 构建文件名
    model_name = config.model_name.replace(":", "_")
    test_name = Path(config.test_file).stem
    role_name = config.role_name
    
    filename = f"asses_{model_name}_{test_name}_{role_name}_e{config.emotional_stress_level}_t{config.tmpr or 0}_c{config.context_load_tokens}_{timestamp}.json"
    filepath = RESULTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return str(filepath)


def run_assessment_with_config(config: AssessmentConfig) -> dict:
    """使用配置运行评估"""
    
    # 初始化服务
    client = LLMClient()
    stress_injector = StressInjector(str(COGNITIVE_TRAPS_DIR), str(CONTEXT_MATERIALS_DIR))
    logger = AssessmentLogger()
    response_extractor = ResponseExtractor()
    session_manager = SessionManager()
    
    # 加载测试数据
    test_data = load_test_data(config.test_file)
    
    # 加载角色提示
    base_prompt = load_role_prompt(config.role_name)
    
    # 应用模型设置
    model_options = apply_model_settings(client, tmpr=config.tmpr)
    
    # 计算上下文长度
    context_length_k = config.context_load_tokens // 1024
    
    # 构建压力配置
    stress_config = {
        'emotional_stress_level': config.emotional_stress_level,
        'cognitive_trap_type': config.cognitive_trap_type,
        'context_load_tokens': config.context_load_tokens
    }
    
    # 初始化结果
    results = {
        'assessment_metadata': {
            'model_id': config.model_name,
            'test_name': config.test_file,
            'role_name': config.role_name,
            'config': asdict(config),
            'timestamp': datetime.now().isoformat(),
            'is_no_injection': config.is_no_injection()
        },
        'assessment_results': []
    }
    
    # 开始日志
    log_file = logger.start_new_log(config.model_name, config.test_file, config.role_name)
    
    try:
        # 处理每个问题
        for i, question in enumerate(test_data.get('test_bank', [])):
            print(f"处理问题 {i+1}/{len(test_data.get('test_bank', []))}")
            
            # 构建对话
            builder = PromptBuilder(base_prompt, question, stress_config, stress_injector)
            conversation_to_send = builder.build_conversation()
            
            # 记录会话
            conversation_log = []
            final_response = ""
            
            if config.context_load_tokens > 0:
                # 多轮会话（有上下文注入）
                context_prompt = [conversation_to_send[0], conversation_to_send[1]]
                context_response = client.generate_response(context_prompt, config.model_name, options=model_options)
                
                complete_conversation = [
                    conversation_to_send[0],
                    conversation_to_send[1],
                    {'role': 'assistant', 'content': context_response or "已理解内容"},
                    conversation_to_send[-1]
                ]
                
                final_response = client.generate_response(complete_conversation, config.model_name, options=model_options)
                conversation_log.extend(complete_conversation)
                
            else:
                # 单轮会话（无上下文注入）
                final_response = client.generate_response(conversation_to_send, config.model_name, options=model_options)
                conversation_log.extend(conversation_to_send)
            
            conversation_log.append({'role': 'assistant', 'content': final_response or "[无响应]"})
            
            # 提取最终响应
            extracted_response = response_extractor.extract_final_response(conversation_log)
            
            # 记录完整会话
            session_id = f"question_{i}_{question.get('id', i)}"
            logger.log_complete_session(
                session_id=session_id,
                conversation=conversation_log,
                extracted_response=extracted_response,
                metadata={
                    'question_id': question.get('id', i),
                    'config': asdict(config)
                }
            )
            
            # 保存结果
            results['assessment_results'].append({
                'question_id': question.get('id', i),
                'question_data': question,
                'conversation_log': conversation_log,
                'extracted_response': extracted_response,
                'session_id': session_id
            })
    
    except Exception as e:
        print(f"评估过程中出现错误: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()
    
    finally:
        pass
    
    return results


def main():
    """主函数"""
    try:
        # 解析CLI参数
        parser = config_manager.create_config_parser()
        args = parser.parse_args()
        
        # 获取最终配置
        cli_args = {k: v for k, v in vars(args).items() if v is not None}
        config = config_manager.get_final_config(cli_args)
        
        # 显示配置信息
        print("=" * 60)
        print("LLM心理评估工具 - 统一配置模式")
        print("=" * 60)
        print(f"模型: {config.model_name}")
        print(f"测试: {config.test_file}")
        print(f"角色: {config.role_name}")
        print(f"无注入模式: {config.is_no_injection()}")
        print(f"情绪压力: {config.emotional_stress_level}")
        print(f"上下文注入: {config.context_load_tokens} tokens")
        print("=" * 60)
        
        # 运行评估
        results = run_assessment_with_config(config)
        
        # 保存结果
        saved_file = save_results(results, config)
        print(f"评估完成！结果已保存到: {saved_file}")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()