#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的批量分段式心理评估分析器
该脚本包含所有必要的功能，可在其他服务器上独立运行
支持多种Ollama模型进行批量评估分析
"""

import json
import sys
import os
import requests
import time
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# 确保在Windows上使用UTF-8编码
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class OllamaEvaluator:
    """Ollama评估器类"""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 300):
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

        # 6. 修复截断的JSON
        if not json_text.strip().endswith('}'):
            json_text = json_text.rstrip() + '}'
        if not json_text.strip().endswith(']') and 'question_scores' in json_text:
            if 'question_scores": [' in json_text and not json_text.strip().endswith(']'):
                json_text = json_text.rstrip() + ']'

        # 7. 修复嵌套对象的逗号问题
        json_text = re.sub(r'(\})\s*("[^"]+":)', r'\1,\2', json_text)
        
        # 8. 最后清理：移除多余的空格
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
        
        # 修复转义字符问题
        json_text = re.sub(r'"', '"', json_text)
        json_text = re.sub(r'\\', '\\\\', json_text)
        
        # 修复引号问题
        json_text = re.sub(r"([^\\])'", r'\1"', json_text)
        
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


class BatchSegmentedPersonalityAnalyzer:
    """批量分段式人格分析器"""

    def __init__(self, max_questions_per_segment: int = 2, max_segment_size: int = 50000, 
                 evaluator_name: str = "ollama_mistral", base_url: str = "http://localhost:11434"):
        self.max_questions_per_segment = max_questions_per_segment
        self.max_segment_size = max_segment_size  # 50K大小限制，适应128K上下文
        self.evaluator_name = evaluator_name
        self.base_url = base_url
        self.evaluator = None
        self.big_five_traits = {
            'openness_to_experience': {'score': 0, 'evidence': [], 'weight': 0},
            'conscientiousness': {'score': 0, 'evidence': [], 'weight': 0},
            'extraversion': {'score': 0, 'evidence': [], 'weight': 0},
            'agreeableness': {'score': 0, 'evidence': [], 'weight': 0},
            'neuroticism': {'score': 0, 'evidence': [], 'weight': 0}
        }
        self.analysis_log = []
        self.per_question_scores = []
        
        # 初始化评估器
        self.evaluator = OllamaEvaluator(base_url, timeout=300)
        if self.evaluator:
            print(f"成功初始化评估器: {evaluator_name}")
        else:
            raise Exception(f"无法初始化评估器: {evaluator_name}")

    def extract_questions(self, assessment_data: Dict) -> List[Dict]:
        """从评估数据中提取问题列表"""

        # 处理新的简化格式
        if 'assessment_data' in assessment_data:
            assessment_data = assessment_data['assessment_data']

        if 'assessment_results' in assessment_data:
            assessment_results = assessment_data['assessment_results']

            if isinstance(assessment_results, list):
                # 检查是否是问题对象列表（每个对象包含question_data）
                if len(assessment_results) > 0 and isinstance(assessment_results[0], dict):
                    if 'question_data' in assessment_results[0]:
                        # 从question_data中提取问题
                        questions = []
                        for result in assessment_results:
                            if 'question_data' in result:
                                question_data = result['question_data'].copy()
                                # 添加agent_response从conversation_log中提取
                                if 'conversation_log' in result:
                                    for msg in result['conversation_log']:
                                        if msg.get('role') == 'assistant':
                                            question_data['agent_response'] = msg['content']
                                            break
                                questions.append(question_data)
                        return questions
                    elif 'question_id' in assessment_results[0] and 'agent_response' in assessment_results[0]:
                        # 新的简化格式：直接包含问题字段
                        return assessment_results

            elif isinstance(assessment_results, dict) and 'questions' in assessment_results:
                return assessment_results['questions']

        if 'questions' in assessment_data:
            return assessment_data['questions']

        # 如果都找不到，打印更多信息用于调试
        print(f"调试: assessment_data keys = {list(assessment_data.keys())}")
        if 'assessment_results' in assessment_data:
            results = assessment_data['assessment_results']
            print(f"调试: assessment_results type = {type(results)}")
            if isinstance(results, list):
                print(f"调试: assessment_results length = {len(results)}")
                if len(results) > 0:
                    print(f"调试: first result keys = {list(results[0].keys()) if isinstance(results[0], dict) else 'not dict'}")

        raise ValueError("无法从评估数据中提取问题")

    def create_segments(self, questions: List[Dict]) -> List[List[Dict]]:
        """将问题列表分段，考虑大小限制"""
        segments = []
        remaining_questions = questions.copy()

        while remaining_questions:
            segment = []
            current_size = 0

            # 按顺序添加问题，直到达到数量或大小限制
            while len(segment) < self.max_questions_per_segment and remaining_questions:
                question = remaining_questions[0]

                # 检查添加这个问题是否会超过大小限制
                test_segment = segment + [question]
                segment_size = len(json.dumps(test_segment, ensure_ascii=False).encode('utf-8'))

                if segment_size <= self.max_segment_size:
                    segment.append(question)
                    remaining_questions.pop(0)
                    current_size = segment_size
                else:
                    # 如果单个问题就超过限制，需要截断文本
                    single_question_size = len(json.dumps([question], ensure_ascii=False).encode('utf-8'))
                    if single_question_size > self.max_segment_size:
                        # 截断问题文本
                        truncated_question = self.truncate_question_to_size(question, self.max_segment_size - 1000)  # 留些余量
                        segment.append(truncated_question)
                        remaining_questions.pop(0)
                    break

            if segment:  # 确保段不为空
                segments.append(segment)

        return segments

    def truncate_question_to_size(self, question: Dict, max_size: int) -> Dict:
        """截断问题文本以适应大小限制"""
        truncated = question.copy()

        # 截断场景描述
        if 'scenario' in truncated and len(truncated['scenario']) > 200:
            truncated['scenario'] = truncated['scenario'][:200] + "..."

        # 截断回答
        if 'agent_response' in truncated and len(truncated['agent_response']) > 400:
            truncated['agent_response'] = truncated['agent_response'][:400] + "..."

        # 截断评分标准描述
        if 'evaluation_rubric' in truncated and isinstance(truncated['evaluation_rubric'], dict):
            if 'description' in truncated['evaluation_rubric'] and len(truncated['evaluation_rubric']['description']) > 100:
                truncated['evaluation_rubric']['description'] = truncated['evaluation_rubric']['description'][:100] + "..."

        return truncated

    def analyze_segment(self, segment: List[Dict], segment_number: int) -> Dict:
        """分析单个段并返回该段的评分"""
        segment_analysis = {
            'segment_number': segment_number,
            'question_count': len(segment),
            'dimensions_covered': list(set(q.get('dimension', 'Unknown') for q in segment))
        }

        # 构建段的分析提示 - 简化版本
        system_prompt = f"""You are a personality analyst. Analyze {len(segment)} questions and provide Big Five scores (1, 3, or 5) for each, strictly following the original assessment scoring standard.

For each question, assess all 5 traits:
- openness_to_experience
- conscientiousness
- extraversion
- agreeableness
- neuroticism

Scoring guidelines (STRICTLY FOLLOW 1-3-5 scale):
- Score 1: Clearly lacks the trait (low level of trait)
- Score 3: Moderately demonstrates the trait (medium level of trait)
- Score 5: Clearly demonstrates the trait (high level of trait)

Use ONLY these three scores: 1, 3, or 5. DO NOT use any other scores.

REQUIRED JSON FORMAT:
{{
    "question_scores": [
        {{
            "question_id": "Q1",
            "dimension": "extraversion",
            "big_five_scores": {{
                "openness_to_experience": {{"score": 3, "evidence": "Evidence from response", "quality": "direct"}},
                "conscientiousness": {{"score": 5, "evidence": "Professional inference", "quality": "inferred"}},
                "extraversion": {{"score": 1, "evidence": "Direct evidence", "quality": "direct"}},
                "agreeableness": {{"score": 3, "evidence": "Inference from response", "quality": "inferred"}},
                "neuroticism": {{"score": 5, "evidence": "Evidence from response", "quality": "direct"}}
            }}
        }}
    ]
}}

Return ONLY valid JSON. All traits must have scores 1, 3, or 5 with evidence. No null values."""

        # 构建用户输入
        user_content = []
        for i, question in enumerate(segment):
            user_content.append(f"Question {i+1} ({question.get('dimension', 'Unknown')}):")
            user_content.append(f"Scenario: {question['scenario']}")
            user_content.append(f"Response: {question['agent_response'][:300]}...")
            user_content.append(f"Rubric: {question.get('evaluation_rubric', {}).get('description', 'N/A')}")
            user_content.append("---")

        user_prompt = "\n".join(user_content)

        # 使用真实的LLM调用
        print(f"  使用评估器 {self.evaluator_name} 分析段 {segment_number}")
        
        # 获取模型配置
        model_config = self.get_model_config(self.evaluator_name.replace("ollama_", ""))
        temperature = model_config.get("temperature", 0.1)
        max_tokens = model_config.get("max_tokens", 1024)
        model_name = model_config.get("name", "mistral:instruct")
        
        # 调用评估器
        result = self.evaluator.evaluate_json_response(
            model_name, 
            system_prompt, 
            user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if result["success"]:
            print(f"  段 {segment_number} 分析成功")
            return {
                'system_prompt': system_prompt,
                'user_prompt': user_prompt,
                'segment_info': segment_analysis,
                'llm_response': result["response"],
                'raw_response': result["raw_response"]
            }
        else:
            print(f"  段 {segment_number} 分析失败: {result['error']}")
            # 不再使用模拟数据，而是抛出异常
            raise Exception(f"评估器调用失败: {result['error']}")
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """获取模型配置"""
        # 尝试从配置文件读取配置
        config_file = "evaluator_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                model_config = config.get("ollama", {}).get("models", {}).get(model_name, {})
                if model_config:
                    print(f"从配置文件加载模型 {model_name} 的配置")
                    return model_config
            except Exception as e:
                print(f"读取配置文件失败: {e}")
        
        # 默认配置
        default_configs = {
            "mistral": {
                "name": "mistral:instruct",
                "temperature": 0.1,
                "max_tokens": 1024,
                "timeout": 300
            },
            "phi3_mini": {
                "name": "phi3:mini",
                "temperature": 0.1,
                "max_tokens": 1024,
                "timeout": 300
            },
            "qwen3_4b": {
                "name": "qwen3:4b",
                "temperature": 0.1,
                "max_tokens": 1024,
                "timeout": 300
            },
            "gemma3": {
                "name": "gemma3:latest",
                "temperature": 0.1,
                "max_tokens": 1024,
                "timeout": 300
            }
        }
        
        return default_configs.get(model_name, default_configs["mistral"])

    def accumulate_scores(self, segment_result: Dict) -> None:
        """累积问题级别的评分到总分"""
        if 'question_scores' not in segment_result:
            print(f"警告: segment_result中缺少'question_scores'字段: {list(segment_result.keys())}")
            return

        question_scores = segment_result['question_scores']
        if not isinstance(question_scores, list):
            print(f"警告: 'question_scores'不是列表类型: {type(question_scores)}")
            # 尝试修复：如果question_scores是字符串，尝试解析为JSON
            if isinstance(question_scores, str):
                try:
                    import json
                    question_scores = json.loads(question_scores)
                    print(f"成功解析question_scores字符串为JSON")
                except:
                    print(f"无法解析question_scores字符串: {question_scores[:100]}...")
                    return
            else:
                return

        # 累积每个问题的Big Five分数
        for i, question_score in enumerate(question_scores):
            # 处理question_score为字符串的情况
            if isinstance(question_score, str):
                try:
                    import json
                    question_score = json.loads(question_score)
                    print(f"成功解析question_score[{i}]字符串为JSON")
                except:
                    print(f"无法解析question_score[{i}]字符串: {question_score[:100]}...")
                    continue

            if not isinstance(question_score, dict):
                print(f"警告: question_scores[{i}]不是字典类型: {type(question_score)}")
                continue

            question_id = question_score.get('question_id', f'Q{i+1}')
            big_five_scores = question_score.get('big_five_scores', {})

            if not isinstance(big_five_scores, dict):
                print(f"警告: question {question_id}的'big_five_scores'不是字典类型: {type(big_five_scores)}")
                continue

            for trait, score_data in big_five_scores.items():
                if trait in self.big_five_traits:
                    if not isinstance(score_data, dict):
                        print(f"警告: question {question_id}的trait '{trait}'数据不是字典类型: {type(score_data)}")
                        continue

                    score = score_data.get('score')
                    evidence = score_data.get('evidence', f"Question {question_id}")
                    quality = score_data.get('quality', 'direct')  # 默认为直接证据

                    # 分层处理null值策略
                    if score is None:
                        print(f"警告: question {question_id}的trait '{trait}'分数为null，使用智能默认值")
                        score = 5.0  # 中性默认分数
                        evidence = f"Professional inference for {trait} - insufficient direct evidence in Question {question_id}"
                        quality = 'inferred'
                    else:
                        try:
                            score = float(score)
                        except (ValueError, TypeError):
                            print(f"警告: question {question_id}的trait '{trait}'分数类型错误: {score}，使用默认值")
                            score = 5.0
                            evidence = f"Professional inference for {trait} - invalid score format in Question {question_id}"
                            quality = 'inferred'

                    # 确保分数在有效范围内
                    score = max(1.0, min(10.0, score))

                    self.big_five_traits[trait]['score'] += score
                    self.big_five_traits[trait]['evidence'].append({
                        'text': evidence,
                        'quality': quality,
                        'question_id': question_id
                    })
                    self.big_five_traits[trait]['weight'] += 1

            # 记录问题级别的分析日志
            self.analysis_log.append({
                'type': 'question_score',
                'question_id': question_id,
                'big_five_scores': big_five_scores,
                'dimension': question_score.get('dimension', 'Unknown')
            })

            normalized_scores = {}
            for trait, data in big_five_scores.items():
                s = data.get('score')
                try:
                    s = float(s)
                except (ValueError, TypeError):
                    s = 5.0
                s = max(1.0, min(10.0, s))
                normalized_scores[trait] = {'score': s, 'evidence': data.get('evidence', ''), 'quality': data.get('quality', 'direct')}
            self.per_question_scores.append({'question_id': question_id, 'dimension': question_score.get('dimension', 'Unknown'), 'big_five_scores': normalized_scores})

    def calculate_final_scores(self) -> Dict:
        """计算最终分数"""
        final_scores = {
            'big_five': {},
            'mbti': {},
            'belbin': {},
            'per_question_scores': [],
            'analysis_summary': {
                'total_segments': 0,
                'total_questions': 0,
                'trait_coverage': {},
                'evidence_quality': {}
            }
        }

        # 计算Big Five最终分数（加权平均）
        for trait, data in self.big_five_traits.items():
            if data['weight'] > 0:
                # 将累积分数转换为1-10分制
                raw_score = data['score'] / data['weight']
                # 标准化到1-10范围
                normalized_score = max(1, min(10, 5 + raw_score))

                # 分析证据质量
                evidence_items = data['evidence']
                direct_evidence = [item for item in evidence_items if isinstance(item, dict) and item.get('quality') == 'direct']
                inferred_evidence = [item for item in evidence_items if isinstance(item, dict) and item.get('quality') == 'inferred']

                # 处理旧格式的证据（字符串）
                legacy_evidence = [item for item in evidence_items if isinstance(item, str)]

                evidence_quality = {
                    'direct_count': len(direct_evidence),
                    'inferred_count': len(inferred_evidence),
                    'legacy_count': len(legacy_evidence),
                    'direct_ratio': round(len(direct_evidence) / len(evidence_items), 2) if evidence_items else 0,
                    'quality_score': round((len(direct_evidence) + 0.5 * len(inferred_evidence)) / len(evidence_items), 2) if evidence_items else 0
                }

                final_scores['big_five'][trait] = {
                    'score': round(normalized_score, 1),
                    'raw_score': round(raw_score, 2),
                    'evidence_count': len(evidence_items),
                    'weight': data['weight'],
                    'evidence_quality': evidence_quality,
                    'key_evidence': evidence_items[:3]  # 前3个证据
                }

                # 添加到总体证据质量统计
                final_scores['analysis_summary']['evidence_quality'][trait] = evidence_quality
            else:
                final_scores['big_five'][trait] = {
                    'score': 5.0,
                    'raw_score': 0.0,
                    'evidence_count': 0,
                    'weight': 0,
                    'evidence_quality': {
                        'direct_count': 0,
                        'inferred_count': 0,
                        'legacy_count': 0,
                        'direct_ratio': 0,
                        'quality_score': 0
                    },
                    'key_evidence': []
                }

        # 基于Big Five分数计算MBTI类型
        mbti_type = self.convert_big_five_to_mbti(final_scores['big_five'])

        final_scores['mbti'] = {
            'type': mbti_type['type'],
            'confidence': mbti_type['confidence'],
            'big_five_basis': mbti_type['big_five_basis']
        }

        belbin = self.convert_big_five_to_belbin(final_scores['big_five'])
        final_scores['belbin'] = belbin
        
        # 添加A/T维度 (Assertive/Turbulent)
        neuroticism_score = final_scores['big_five']['neuroticism']['score']
        from at_dimension import neuroticism_to_at_type, get_at_description
        at_type = neuroticism_to_at_type(neuroticism_score)
        at_description = get_at_description(at_type)
        
        final_scores['at_type'] = {
            'type': at_type,
            'description': at_description,
            'neuroticism_score': neuroticism_score
        }
        
        final_scores['per_question_scores'] = self.per_question_scores
        final_scores['analysis_summary']['total_questions'] = len(self.per_question_scores)

        return final_scores

    def convert_big_five_to_mbti(self, big_five_scores: Dict) -> Dict:
        """基于Big Five分数转换为MBTI类型"""

        # 获取Big Five分数
        openness = big_five_scores.get('openness_to_experience', {}).get('score', 5.0)
        conscientiousness = big_five_scores.get('conscientiousness', {}).get('score', 5.0)
        extraversion = big_five_scores.get('extraversion', {}).get('score', 5.0)
        agreeableness = big_five_scores.get('agreeableness', {}).get('score', 5.0)
        neuroticism = big_five_scores.get('neuroticism', {}).get('score', 5.0)

        # E/I: 基于Extraversion和Neuroticism
        e_score = extraversion + (10 - neuroticism) / 2  # 高外向性+低神经质=更外向
        i_score = (10 - extraversion) + neuroticism / 2
        e_pref = 'E' if e_score > i_score else 'I'
        e_confidence = abs(e_score - i_score) / 10

        # S/N: 基于Openness
        s_score = 10 - openness
        n_score = openness
        s_pref = 'N' if n_score > s_score else 'S'
        n_confidence = abs(n_score - s_score) / 10

        # T/F: 基于Agreeableness
        t_score = 10 - agreeableness
        f_score = agreeableness
        t_pref = 'F' if f_score > t_score else 'T'
        t_confidence = abs(f_score - t_score) / 10

        # J/P: 基于Conscientiousness
        j_score = conscientiousness
        p_score = 10 - conscientiousness
        j_pref = 'J' if j_score > p_score else 'P'
        j_confidence = abs(j_score - p_score) / 10

        mbti_type = e_pref + s_pref + t_pref + j_pref
        overall_confidence = (e_confidence + n_confidence + t_confidence + j_confidence) / 4

        return {
            'type': mbti_type,
            'confidence': round(overall_confidence, 2),
            'big_five_basis': {
                'E/I': {'score': e_score, 'preference': e_pref, 'confidence': e_confidence},
                'S/N': {'score': n_score, 'preference': s_pref, 'confidence': n_confidence},
                'T/F': {'score': f_score, 'preference': t_pref, 'confidence': t_confidence},
                'J/P': {'score': j_score, 'preference': j_pref, 'confidence': j_confidence}
            }
        }

    def convert_big_five_to_belbin(self, big_five_scores: Dict) -> Dict:
        O = big_five_scores.get('openness_to_experience', {}).get('score', 5.0)
        C = big_five_scores.get('conscientiousness', {}).get('score', 5.0)
        E = big_five_scores.get('extraversion', {}).get('score', 5.0)
        A = big_five_scores.get('agreeableness', {}).get('score', 5.0)
        N = big_five_scores.get('neuroticism', {}).get('score', 5.0)
        roles = {
            'PL': O*0.5 + A*0.2 + (-C)*0.3,
            'RI': E*0.5 + O*0.4,
            'CO': E*0.4 + A*0.4,
            'SH': E*0.4 + (-A)*0.3 + (10-N)*0.2,
            'ME': C*0.5 + (-E)*0.3 + (10-N)*0.2,
            'TW': A*0.5 + E*0.2,
            'IMP': C*0.5 + (-O)*0.3,
            'CF': C*0.4 + N*0.3,
            'SP': C*0.3 + O*0.3
        }
        sorted_roles = sorted(roles.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_roles[0][0]
        secondary = sorted_roles[1][0]
        rationale = {'top_traits': {'O': O, 'C': C, 'E': E, 'A': A, 'N': N}, 'role_scores': roles}
        return {'primary_role': primary, 'secondary_role': secondary, 'rationale': rationale}


def batch_analyze_directory(input_directory: str, output_directory: str, evaluator_name: str = "ollama_mistral", 
                           base_url: str = "http://localhost:11434", max_questions_per_segment: int = 2):
    """批量分析目录中的所有JSON文件"""
    input_path = Path(input_directory)
    output_path = Path(output_directory)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 查找所有JSON文件
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"在目录 {input_directory} 中未找到JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个JSON文件进行分析")
    
    # 初始化分析器
    try:
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=max_questions_per_segment,
            evaluator_name=evaluator_name,
            base_url=base_url
        )
    except Exception as e:
        print(f"初始化分析器失败: {e}")
        return
    
    # 分析每个文件
    for i, json_file in enumerate(json_files):
        print(f"\n处理文件 {i+1}/{len(json_files)}: {json_file.name}")
        
        try:
            # 加载数据
            with open(json_file, 'r', encoding='utf-8') as f:
                assessment_data = json.load(f)
            
            # 提取问题
            questions = analyzer.extract_questions(assessment_data)
            print(f"  总问题数: {len(questions)}")
            
            # 创建分段
            segments = analyzer.create_segments(questions)
            print(f"  分段数: {len(segments)}")
            
            # 分析每个段并累积结果
            for j, segment in enumerate(segments):
                print(f"  分析段 {j+1}/{len(segments)}: {len(segment)} 个问题")
                dimensions = list(set(q.get('dimension', 'Unknown') for q in segment))
                print(f"    涵盖维度: {dimensions}")
                
                # 分析段
                segment_analysis = analyzer.analyze_segment(segment, j+1)
                
                # 累积分数
                if 'llm_response' in segment_analysis:
                    analyzer.accumulate_scores(segment_analysis['llm_response'])
                    print(f"    段 {j+1} 分析完成并累积分数")
                else:
                    print(f"    警告: 段 {j+1} 缺少分析结果")
            
            # 计算最终分数
            final_scores = analyzer.calculate_final_scores()
            
            # 保存结果到文件
            output_file = output_path / f"{json_file.stem}_segmented_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_scores, f, ensure_ascii=False, indent=2)
            print(f"  结果已保存到: {output_file}")
            
            # 重置分析器状态以准备下一个文件
            analyzer.big_five_traits = {
                'openness_to_experience': {'score': 0, 'evidence': [], 'weight': 0},
                'conscientiousness': {'score': 0, 'evidence': [], 'weight': 0},
                'extraversion': {'score': 0, 'evidence': [], 'weight': 0},
                'agreeableness': {'score': 0, 'evidence': [], 'weight': 0},
                'neuroticism': {'score': 0, 'evidence': [], 'weight': 0}
            }
            analyzer.analysis_log = []
            analyzer.per_question_scores = []
            
        except Exception as e:
            print(f"  处理文件 {json_file.name} 时出错: {e}")
            continue
    
    print(f"\n批量分析完成，结果保存在 {output_directory}")


def test_single_file(input_file: str, evaluator_name: str = "ollama_mistral", 
                    base_url: str = "http://localhost:11434", max_questions_per_segment: int = 2):
    """测试单个文件的分段分析"""
    # 检查文件是否存在
    if not Path(input_file).exists():
        print(f"错误: 文件不存在 - {input_file}")
        return

    # 初始化分析器
    try:
        analyzer = BatchSegmentedPersonalityAnalyzer(
            max_questions_per_segment=max_questions_per_segment,
            evaluator_name=evaluator_name,
            base_url=base_url
        )
    except Exception as e:
        print(f"初始化分析器失败: {e}")
        return

    # 加载测试数据
    assessment_data = None
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                assessment_data = json.load(f)
            print(f"成功使用 {encoding} 编码读取文件")
            break
        except UnicodeDecodeError:
            print(f"使用 {encoding} 编码读取文件失败，尝试其他编码...")
            continue
        except json.JSONDecodeError as e:
            print(f"使用 {encoding} 编码读取文件成功但JSON解析失败: {e}")
            continue
    
    if assessment_data is None:
        print("错误: 无法使用任何编码方式读取文件")
        return

    print("数据结构:", list(assessment_data.keys()))

    # 提取问题
    questions = analyzer.extract_questions(assessment_data)
    print(f"总问题数: {len(questions)}")

    # 创建分段
    segments = analyzer.create_segments(questions)
    print(f"分段数: {len(segments)}")

    # 分析每个段并累积结果
    for i, segment in enumerate(segments):
        print(f"分析段 {i+1}/{len(segments)}: {len(segment)} 个问题")
        dimensions = list(set(q.get('dimension', 'Unknown') for q in segment))
        print(f"  涵盖维度: {dimensions}")

        # 分析段
        segment_analysis = analyzer.analyze_segment(segment, i+1)
        
        # 累积分数
        if 'llm_response' in segment_analysis:
            analyzer.accumulate_scores(segment_analysis['llm_response'])
            print(f"  段 {i+1} 分析完成并累积分数")
        else:
            print(f"  警告: 段 {i+1} 缺少分析结果")

    # 计算最终分数
    final_scores = analyzer.calculate_final_scores()
    
    # 输出结果
    print("\n=== 最终分析结果 ===")
    print("Big Five 分数:")
    for trait, data in final_scores['big_five'].items():
        print(f"  {trait}: {data['score']}/10.0 (基于 {data['weight']} 个问题)")
    
    print(f"\nMBTI 类型: {final_scores['mbti']['type']} (置信度: {final_scores['mbti']['confidence']})")
    
    # 保存结果到文件
    output_file = input_file.replace(".json", "_segmented_analysis.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_scores, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到: {output_file}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  单文件分析: python batch_segmented_analysis.py <input_file> [evaluator_name] [base_url]")
        print("  批量分析: python batch_segmented_analysis.py batch <input_directory> <output_directory> [evaluator_name] [base_url]")
        print("\n参数说明:")
        print("  input_file: 输入的JSON评估文件路径")
        print("  input_directory: 包含JSON文件的输入目录")
        print("  output_directory: 输出结果的目录")
        print("  evaluator_name: 评估器名称 (默认: ollama_mistral)")
        print("  base_url: Ollama服务地址 (默认: http://localhost:11434)")
        print("\n支持的评估器:")
        print("  ollama_mistral (默认) - 使用Mistral模型")
        print("  phi3_mini - 使用Phi3 Mini模型")
        print("  qwen3_4b - 使用Qwen3 4B模型")
        return

    if sys.argv[1] == "batch":
        # 批量分析模式
        if len(sys.argv) < 4:
            print("批量分析需要输入目录和输出目录参数")
            return
        
        input_directory = sys.argv[2]
        output_directory = sys.argv[3]
        evaluator_name = sys.argv[4] if len(sys.argv) > 4 else "ollama_mistral"
        base_url = sys.argv[5] if len(sys.argv) > 5 else "http://localhost:11434"
        
        batch_analyze_directory(input_directory, output_directory, evaluator_name, base_url)
    else:
        # 单文件分析模式
        input_file = sys.argv[1]
        evaluator_name = sys.argv[2] if len(sys.argv) > 2 else "ollama_mistral"
        base_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:11434"
        
        test_single_file(input_file, evaluator_name, base_url)


if __name__ == "__main__":
    main()