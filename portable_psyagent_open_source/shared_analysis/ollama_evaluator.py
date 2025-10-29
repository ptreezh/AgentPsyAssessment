#!/usr/bin/env python3
"""
Ollama本地大模型评估器
支持本地Ollama服务的大模型评估
"""

import json
import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime
import re


class OllamaEvaluator:
    """Ollama评估器类"""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 120):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def check_connection(self) -> bool:
        """检查Ollama服务连接"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama连接检查失败: {e}")
            return False
    
    def list_models(self) -> Dict[str, Any]:
        """获取可用模型列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"models": []}
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return {"models": []}
    
    def chat(self, model_name: str, messages: list, 
             temperature: float = 0.1, max_tokens: int = 1024) -> Dict[str, Any]:
        """使用聊天API生成响应"""
        
        # 构建请求体
        request_data = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "format": "json",  # 强制JSON格式
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            print(f"    [DEBUG] Calling Ollama Chat API with model: {model_name}")
            print(f"    [DEBUG] Messages count: {len(messages)}")
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("message", {}).get("content", "")
                print(f"    [DEBUG] Ollama Chat API response length: {len(response_text)} chars")
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": model_name,
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "eval_count": result.get("eval_count", 0)
                }
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                print(f"    !! Ollama Chat API Error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            print(f"    !! Ollama Chat API Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        except requests.exceptions.ConnectionError:
            error_msg = "连接失败，请确认Ollama服务正在运行"
            print(f"    !! Ollama Chat API Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"    !! Ollama Chat API Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def generate(self, model_name: str, prompt: str, system_prompt: str = None, 
                temperature: float = 0.1, max_tokens: int = 1024) -> Dict[str, Any]:
        """使用生成API生成响应"""
        
        # 构建请求体
        request_data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # 如果有系统提示，添加到请求中
        if system_prompt:
            request_data["system"] = system_prompt
        
        try:
            print(f"    [DEBUG] Calling Ollama Generate API with model: {model_name}")
            print(f"    [DEBUG] System prompt length: {len(system_prompt) if system_prompt else 0} chars")
            print(f"    [DEBUG] User prompt length: {len(prompt)} chars")
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                print(f"    [DEBUG] Ollama Generate API response length: {len(response_text)} chars")
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": model_name,
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "eval_count": result.get("eval_count", 0)
                }
            else:
                error_msg = f"API请求失败: {response.status_code} - {response.text}"
                print(f"    !! Ollama Generate API Error: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            print(f"    !! Ollama Generate API Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        except requests.exceptions.ConnectionError:
            error_msg = "连接失败，请确认Ollama服务正在运行"
            print(f"    !! Ollama Generate API Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"    !! Ollama Generate API Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def repair_json(self, json_text: str) -> str:
        """修复常见的JSON格式错误"""
        try:
            # 首先尝试直接解析
            json.loads(json_text)
            return json_text
        except json.JSONDecodeError:
            pass

        # 保存原始文本用于调试
        original_text = json_text[:500] + "..." if len(json_text) > 500 else json_text
        print(f"    [DEBUG] 原始JSON文本: {original_text}")

        # 1. 修复中文字段名问题
        json_text = re.sub(r'"([^"]*?)":\s*"([^"]*?)"', lambda m: self._fix_chinese_field_names(m), json_text)

        # 2. 修复缺少逗号的问题
        json_text = re.sub(r'}\s*{', '},{', json_text)  # 在对象之间添加逗号
        json_text = re.sub(r']\s*{', '],{', json_text)   # 在数组后添加对象前添加逗号
        json_text = re.sub(r'}\s*\[', '},[', json_text)   # 在对象后添加数组前添加逗号
        json_text = re.sub(r'"([^"]*)"\s*}', r'"\1"}', json_text)  # 确保最后一个字段有逗号

        # 3. 修复引号不匹配问题
        json_text = re.sub(r"'([^']*)'", r'"\1"', json_text)  # 单引号转双引号

        # 4. 修复缺少引号的问题
        json_text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_text)

        # 5. 移除多余的逗号
        json_text = re.sub(r',\s*([}\]])', r'\1', json_text)

        # 6. 修复缺失的逗号（特别针对Phi3 Mini的问题）
        # 修复对象字段之间缺少逗号的问题
        json_text = re.sub(r'("[^"]+":\s*\{[^}]*\})(\s*"[^"]+":)', r'\1,\2', json_text)
        # 修复数组元素之间缺少逗号的问题
        json_text = re.sub(r'(\})\s*(\{)', r'\1,\2', json_text)
        
        # 7. 特别处理Phi3 Mini的JSON格式问题
        # 修复嵌套对象中的引号问题
        json_text = re.sub(r'(\{[^}]*?)"([^}]*?)"([^}]*?\})', r'\1\2\3', json_text)
        
        # 8. 修复截断的JSON
        if not json_text.strip().endswith('}'):
            json_text = json_text.rstrip() + '}'
        if not json_text.strip().endswith(']') and 'question_scores' in json_text:
            if 'question_scores": [' in json_text and not json_text.strip().endswith(']'):
                json_text = json_text.rstrip() + ']'

        # 9. 修复嵌套对象的逗号问题
        json_text = re.sub(r'(\})\s*("[^"]+":)', r'\1,\2', json_text)
        
        # 10. 最后清理：移除多余的空格
        json_text = re.sub(r'\s+', ' ', json_text)
        
        print(f"    [DEBUG] 修复后的JSON文本: {json_text[:500]}...")
        
        return json_text

    def _fix_chinese_field_names(self, match):
        """修复中文字段名为英文"""
        field_name = match.group(1)
        field_value = match.group(2)

        chinese_to_english = {
            '证据': 'evidence',
            '分数': 'score',
            '问题ID': 'question_id',
            '维度': 'dimension',
            '问题分数': 'question_scores',
            '大五分数': 'big_five_scores'
        }

        if field_name in chinese_to_english:
            field_name = chinese_to_english[field_name]

        return f'"{field_name}": "{field_value}"'

    def validate_and_fix_json_structure(self, json_text: str) -> str:
        """验证并修复JSON结构"""
        try:
            data = json.loads(json_text)

            # 确保顶层是字典
            if not isinstance(data, dict):
                print(f"警告: JSON顶层不是字典类型: {type(data)}")
                data = {}

            # 确保必需的字段存在
            if 'question_scores' not in data:
                data['question_scores'] = []

            # 确保question_scores是列表
            if not isinstance(data['question_scores'], list):
                print(f"警告: question_scores不是列表类型: {type(data['question_scores'])}")
                data['question_scores'] = []

            # 修复每个question_score的结构
            valid_question_scores = []
            for i, qs in enumerate(data['question_scores']):
                if not isinstance(qs, dict):
                    print(f"警告: question_scores[{i}]不是字典类型: {type(qs)}")
                    continue

                # 确保必需字段
                if 'question_id' not in qs:
                    qs['question_id'] = f'Q{i+1}'
                if 'dimension' not in qs:
                    qs['dimension'] = 'unknown'
                if 'big_five_scores' not in qs:
                    qs['big_five_scores'] = {}

                # 修复big_five_scores结构
                bfs = qs['big_five_scores']
                if not isinstance(bfs, dict):
                    print(f"警告: question {qs['question_id']}的big_five_scores不是字典类型: {type(bfs)}")
                    qs['big_five_scores'] = {}
                    bfs = qs['big_five_scores']

                # 确保每个Big Five trait都有正确的结构
                for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    if trait not in bfs:
                        bfs[trait] = {'score': 5.0, 'evidence': 'Default evidence'}
                    elif not isinstance(bfs[trait], dict):
                        print(f"警告: question {qs['question_id']}的trait '{trait}'不是字典类型: {type(bfs[trait])}")
                        bfs[trait] = {'score': 5.0, 'evidence': str(bfs[trait])}
                    else:
                        if 'score' not in bfs[trait]:
                            bfs[trait]['score'] = 5.0
                        elif not isinstance(bfs[trait]['score'], (int, float)):
                            try:
                                bfs[trait]['score'] = float(bfs[trait]['score'])
                            except (ValueError, TypeError):
                                bfs[trait]['score'] = 5.0

                        if 'evidence' not in bfs[trait]:
                            bfs[trait]['evidence'] = 'Default evidence'

                valid_question_scores.append(qs)

            data['question_scores'] = valid_question_scores

            return json.dumps(data, ensure_ascii=False)

        except json.JSONDecodeError as e:
            print(f"警告: JSON解析验证失败: {e}")
            # 尝试更强大的修复方法
            repaired_text = self._advanced_json_repair(json_text)
            try:
                json.loads(repaired_text)
                print("    [DEBUG] 高级修复成功")
                return repaired_text
            except json.JSONDecodeError:
                print("    [DEBUG] 高级修复仍失败")
                return json_text

    def _advanced_json_repair(self, json_text: str) -> str:
        """更强大的JSON修复方法"""
        print(f"    [DEBUG] 高级修复输入: {json_text[:200]}...")
        
        # 移除所有注释
        json_text = re.sub(r'//.*?\n', '\n', json_text)
        json_text = re.sub(r'/\*.*?\*/', '', json_text, flags=re.DOTALL)
        
        # 修复常见的格式问题
        # 修复多余的逗号
        json_text = re.sub(r',\s*([}\]])', r'\1', json_text)
        
        # 修复缺少逗号
        json_text = re.sub(r'(\})\s*(\{)', r'\1,\2', json_text)
        json_text = re.sub(r'(\})\s*("[^"]+":)', r'\1,\2', json_text)
        
        # 特别处理Phi3 Mini的引号问题
        # 修复嵌套引号问题
        json_text = re.sub(r'"\s*([^"]*?)\s*"\s*"\s*([^"]*?)\s*"', r'"\1 \2"', json_text)
        
        # 修复中文引号问题
        json_text = re.sub(r'"\s*([^"]*?)"([^"]*?)"\s*', r'"\1\2"', json_text)
        
        # 修复转义字符问题
        json_text = re.sub(r'"', '"', json_text)
        json_text = re.sub(r'\\', '\\\\', json_text)
        
        # 修复引号问题
        json_text = re.sub(r"([^\\])'", r'\1"', json_text)
        
        # 确保字符串正确闭合
        # 这是一个简化的修复，实际应用中可能需要更复杂的逻辑
        
        print(f"    [DEBUG] 高级修复输出: {json_text[:200]}...")
        return json_text

    def evaluate_json_response(self, model_name: str, system_prompt: str, user_prompt: str,
                            temperature: float = 0.1, max_tokens: int = 1024) -> Dict[str, Any]:
        """生成JSON格式响应"""
        
        # 使用聊天API而不是生成API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = self.chat(model_name, messages, temperature, max_tokens)
        
        if not result["success"]:
            return {
                "success": False,
                "error": result["error"],
                "raw_response": None
            }
        
        # 尝试解析JSON响应
        response_text = result["response"]
        
        # 清理响应文本 - 更强大的JSON提取
        response_text = response_text.strip()
        
        # 方法1: 提取 ```json ``` 代码块
        import re
        json_block_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_block_match:
            response_text = json_block_match.group(1)
        else:
            # 方法2: 提取任何 ``` ``` 代码块
            code_block_match = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if code_block_match:
                response_text = code_block_match.group(1)
            else:
                # 方法3: 查找JSON对象起始和结束
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    response_text = response_text[json_start:json_end]
        
        response_text = response_text.strip()

        print(f"    [DEBUG] 清理后的响应文本: {response_text[:500]}...")

        # 尝试修复JSON
        repaired_json = self.repair_json(response_text)
        if repaired_json != response_text:
            print(f"    [DEBUG] 尝试修复JSON格式...")

        # 验证和修复JSON结构
        validated_json = self.validate_and_fix_json_structure(repaired_json)

        try:
            json_response = json.loads(validated_json)
            print(f"    [DEBUG] JSON解析成功: {json_response}")
            return {
                "success": True,
                "response": json_response,
                "raw_response": validated_json,
                "model_info": {
                    "model": model_name,
                    "duration": result.get("total_duration", 0),
                    "eval_count": result.get("eval_count", 0)
                }
            }
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {e}"
            print(f"    !! {error_msg}")
            print(f"    !! 修复后的JSON: {validated_json[:300]}...")
            return {
                "success": False,
                "error": error_msg,
                "raw_response": validated_json
            }


def load_ollama_config(config_path: str = "config/ollama_config.json") -> Dict[str, Any]:
    """加载Ollama配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件未找到: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"配置文件解析失败: {e}")
        return {}


def get_ollama_evaluators() -> Dict[str, Dict[str, Any]]:
    """获取配置的Ollama评估器"""
    config = load_ollama_config()
    return config.get("evaluators", {})


def get_ollama_model_config(model_name: str) -> Dict[str, Any]:
    """获取Ollama模型配置"""
    config = load_ollama_config()
    return config.get("ollama", {}).get("models", {}).get(model_name, {})


def create_ollama_evaluator(evaluator_name: str) -> Optional[OllamaEvaluator]:
    """创建Ollama评估器实例"""
    config = load_ollama_config()
    evaluator_config = config.get("evaluators", {}).get(evaluator_name)

    if not evaluator_config:
        print(f"未找到评估器配置: {evaluator_name}")
        return None

    if evaluator_config.get("provider") != "ollama":
        print(f"评估器不是Ollama类型: {evaluator_name}")
        return None

    model_name = evaluator_config.get("model")
    if not model_name:
        print(f"评估器未配置模型: {evaluator_name}")
        return None

    ollama_config = config.get("ollama", {})
    base_url = ollama_config.get("base_url", "http://localhost:11434")

    # 获取模型特定的超时配置，如果没有则使用默认值
    model_config = get_ollama_model_config(model_name)
    timeout = model_config.get("timeout", ollama_config.get("timeout", 120))

    print(f"创建评估器 {evaluator_name}，模型 {model_name}，超时 {timeout}秒")

    evaluator = OllamaEvaluator(base_url, timeout)
    
    # 检查连接
    if not evaluator.check_connection():
        print(f"无法连接到Ollama服务: {base_url}")
        return None
    
    # 检查模型是否存在
    models_info = evaluator.list_models()
    available_models = [model["name"] for model in models_info.get("models", [])]
    
    model_config = get_ollama_model_config(model_name)
    actual_model_name = model_config.get("name", model_name)
    
    if actual_model_name not in available_models:
        print(f"模型未在Ollama中找到: {actual_model_name}")
        print(f"可用模型: {', '.join(available_models)}")
        return None
    
    return evaluator


def test_ollama_setup():
    """测试Ollama设置"""
    print("=== 测试Ollama设置 ===")
    
    # 加载配置
    config = load_ollama_config()
    if not config:
        print("❌ 配置文件加载失败")
        return False
    
    # 创建评估器
    evaluator = OllamaEvaluator()
    
    # 检查连接
    if not evaluator.check_connection():
        print("❌ 无法连接到Ollama服务")
        print("请确保Ollama已启动: ollama serve")
        return False
    
    print("✅ Ollama服务连接成功")
    
    # 获取模型列表
    models_info = evaluator.list_models()
    available_models = [model["name"] for model in models_info.get("models", [])]
    print(f"可用模型: {', '.join(available_models)}")
    
    # 测试配置的评估器
    evaluators = get_ollama_evaluators()
    print(f"\n配置的评估器: {len(evaluators)}个")
    
    for eval_name, eval_config in evaluators.items():
        model_name = eval_config.get("model")
        model_config = get_ollama_model_config(model_name)
        actual_model = model_config.get("name", model_name)
        
        if actual_model in available_models:
            print(f"✅ {eval_name}: {actual_model}")
        else:
            print(f"❌ {eval_name}: {actual_model} (未找到)")
    
    return True


if __name__ == "__main__":
    test_ollama_setup()