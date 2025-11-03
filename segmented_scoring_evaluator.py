#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分段可信评估系统
实现5题分段独立评估，支持争议解决和信度验证
"""
import sys
import os
import json
import time
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import statistics
import requests
import re

# 尝试导入numpy
try:
    import numpy as np
except ImportError:
    print("警告: 未安装numpy，将影响信度计算功能。请运行: pip install numpy")
    np = None

from personality_analyzer import PersonalityAnalyzer
from report_manager import ReportManager


class APIClient:
    """
    多API客户端，支持OpenRouter、Ollama等服务
    """
    def __init__(self):
        # 从环境变量获取API密钥
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        
        # Ollama配置
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

    def _call_openrouter_api(self, model: str, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Dict[str, Any]:
        """调用OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }

            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.1
            }

            response = requests.post(f"{self.openrouter_base_url}/api/v1/chat/completions", 
                                   json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            result = response.json()
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "model": model,
                "raw_response": result,
                "api_type": "openrouter"
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"OpenRouter API request failed: {str(e)}",
                "model": model,
                "api_type": "openrouter"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenRouter evaluation failed: {str(e)}",
                "model": model,
                "api_type": "openrouter"
            }

    def _call_ollama_api(self, model: str, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Dict[str, Any]:
        """调用Ollama API"""
        try:
            # 构建消息列表
            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            # 准备请求负载
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": max_tokens
                }
            }

            # 发送请求到Ollama服务
            response = requests.post(f"{self.ollama_base_url}/api/chat", 
                                   json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            return {
                "success": True,
                "response": result.get("message", {}).get("content", ""),
                "model": model,
                "raw_response": result,
                "api_type": "ollama"
            }

        except requests.exceptions.RequestException as e:
            # 检查是否是404错误（模型不存在）
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    return {
                        "success": False,
                        "error": f"Ollama模型 '{model}' 不存在，请确认模型已下载: {str(e)}",
                        "model": model,
                        "api_type": "ollama"
                    }
            
            return {
                "success": False,
                "error": f"Ollama API request failed: {str(e)}",
                "model": model,
                "api_type": "ollama"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama evaluation failed: {str(e)}",
                "model": model,
                "api_type": "ollama"
            }

    def evaluate(self, model: str, prompt: str, system_prompt: str = None, max_tokens: int = 2000, 
                 service_preference: str = "auto") -> Dict[str, Any]:
        """
        使用指定模型评估，支持多级重试
        service_preference: "auto", "openrouter", "ollama"
        """
        # 定义服务尝试顺序
        if service_preference == "openrouter":
            services_to_try = ["openrouter"]
        elif service_preference == "ollama":
            services_to_try = ["ollama"]
        else:  # auto (默认)
            services_to_try = ["openrouter", "ollama"]
        
        # 尝试每个服务
        for service in services_to_try:
            if service == "openrouter":
                result = self._call_openrouter_api(model, prompt, system_prompt, max_tokens)
            elif service == "ollama":
                result = self._call_ollama_api(model, prompt, system_prompt, max_tokens)
            else:
                continue  # 未知服务类型，跳过

            # 如果成功，返回结果
            if result["success"]:
                return result
            
            print(f"  ⚠️ {service} API 调用失败: {result.get('error', 'Unknown error')}")
            print(f"  🔄 尝试下一个服务...")
        
        # 所有服务都失败了
        return {
            "success": False,
            "error": f"所有API服务调用都失败了 - 尝试了: {services_to_try}",
            "model": model
        }


class ScoringValidator:
    """
    评分验证器 - 确保评分符合1-3-5分制标准
    """
    @staticmethod
    def validate_scores(scores: Dict[str, int]) -> Dict[str, int]:
        """
        验证并修正评分（确保只使用1、3、5分）
        """
        if not isinstance(scores, dict):
            raise ValueError("评分必须是字典格式")
        
        valid_scores = {}
        valid_values = {1, 3, 5}
        
        for trait, score in scores.items():
            if not isinstance(score, int):
                try:
                    score = int(score)
                except (ValueError, TypeError):
                    print(f"  ⚠️ 无法将评分 '{score}' 转换为整数，使用默认值3")
                    score = 3
            
            if score in valid_values:
                valid_scores[trait] = score
            else:
                # 修正无效评分
                if score < 2:
                    valid_scores[trait] = 1
                elif score > 4:
                    valid_scores[trait] = 5
                else:
                    valid_scores[trait] = 3  # 2和4修正为3
        
        return valid_scores


class SegmentedScoringEvaluator:
    """
    分段评分评估器
    """
    def __init__(self, api_key: str = None, use_ollama_first: bool = False, segment_size: int = 5):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.client = APIClient()
        self.use_ollama_first = use_ollama_first
        self.segment_size = segment_size  # 默认分段大小
        
        # 检查API密钥是否设置
        if not self.api_key:
            print("⚠️  OpenRouter API密钥未设置，将优先使用Ollama本地模型")
            self.use_ollama_first = True
        
        # 主评估器列表
        cloud_models = [
            {"name": "google/gemini-2.0-flash-exp:free", "description": "Google Gemini 2.0 Flash (1M上下文)"},
            {"name": "deepseek/deepseek-r1:free", "description": "DeepSeek R1 (163K上下文)"},
            {"name": "qwen/qwen3-235b-a22b:free", "description": "Qwen3 235b (131K上下文)"},
            {"name": "mistralai/mistral-small-3.2-24b-instruct:free", "description": "Mistral Small (131K上下文)"},
            {"name": "meta-llama/llama-3.3-70b-instruct:free", "description": "Llama 3.3 70B (65K上下文)"},
            {"name": "moonshotai/kimi-k2:free", "description": "Moonshot Kimi K2 (32K上下文)"}
        ]
        
        # Ollama模型列表（备用）- 使用实际存在的模型名称
        ollama_models = [
            {"name": "llama3.2:3b", "description": "Llama3.2 3B (本地模型)"},
            {"name": "gemma2:2b", "description": "Gemma2 2B (本地模型)"},
            {"name": "qwen3:4b", "description": "Qwen3 4B (本地模型)"},
            {"name": "deepseek-r1:8b", "description": "DeepSeek R1 8B (本地模型)"}
        ]
        
        # 根据配置决定模型优先级
        if self.use_ollama_first:
            self.models = ollama_models + cloud_models
        else:
            self.models = cloud_models
        
        print(f"📊 使用模型列表 ({'Ollama优先' if self.use_ollama_first else '云模型优先'}):")
        for i, model in enumerate(self.models[:5], 1):  # 显示前5个模型
            print(f"  {i}. {model['name']} ({model['description']})")
        if len(self.models) > 5:
            print(f"  ... 还有 {len(self.models) - 5} 个模型")
        print(f"📏 分段大小: {self.segment_size}题/段")

    def _create_segments(self, questions: List[Dict], segment_size: int = None) -> List[List[Dict]]:
        """
        将问题列表分段，每段segment_size题
        如果未指定segment_size，则使用实例变量self.segment_size
        """
        if segment_size is None:
            segment_size = self.segment_size
            
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i+segment_size]
            if len(segment) > 0:  # 确保非空段也被添加
                segments.append(segment)
        
        # 打印分段信息用于调试
        print(f"  📊 {len(questions)}题 -> {len(segments)}个分段 (每段{segment_size}题)")
        return segments

    def _create_segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """
        创建分段评分提示
        """
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**以下问卷回答，评估回答者展现的Big5人格特质。

**关键提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**严格评分标准：**
- **1分**：极低表现 - 明显缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **5分**：极高表现 - 明确具备该特质

**特别注意：只能使用1、3、5三个整数分数，严禁使用2、4等其他数值！**

**第{segment_number}段问卷内容（{len(segment)}题/共{total_segments}段）：**
"""

        for i, item in enumerate(segment, 1):
            question_data = item.get('question_data', {})
            prompt += f"""
**问题 {i}:**
{question_data.get('mapped_ipip_concept', '')}

**场景 {i}:**
{question_data.get('scenario', '')}

**指令 {i}:**
{question_data.get('prompt_for_agent', '')}

**AI回答 {i}:**
{item.get('extracted_response', '')}

---
"""

        prompt += """
**请返回严格的JSON格式：**
```json
{
  "success": true,
  "segment_number": {segment_number},
  "analysis_summary": "简要分析总结",
  "scores": {
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  },
  "evidence": {
    "openness_to_experience": "具体证据引用",
    "conscientiousness": "具体证据引用",
    "extraversion": "具体证据引用",
    "agreeableness": "具体证据引用",
    "neuroticism": "具体证据引用"
  },
  "confidence": "high/medium/low"
}
```

**再次提醒：每个评分必须是1、3或5，不能使用其他数值！**
"""

        return prompt

    def _create_question_by_question_prompt(self, question: Dict, question_number: int, total_questions: int) -> str:
        """
        创建单题评分提示 - 针对单题进行分析
        """
        question_data = question.get('question_data', {})
        
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**单个问卷回答，评估回答者在该问题上展现的Big5人格特质。

**关键提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**严格评分标准：**
- **1分**：极低表现 - 明显缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **5分**：极高表现 - 明确具备该特质

**特别注意：只能使用1、3、5三个整数分数，严禁使用2、4等其他数值！**

**第{question_number}道问卷内容（共{total_questions}道题）：**

**问题:**
{question_data.get('mapped_ipip_concept', '')}

**场景:**
{question_data.get('scenario', '')}

**指令:**
{question_data.get('prompt_for_agent', '')}

**AI回答:**
{question.get('extracted_response', '')}

**请返回严格的JSON格式：**
```json
{{
  "success": true,
  "question_number": {question_number},
  "analysis_summary": "简要分析总结",
  "scores": {{
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5,
    "extraversion": 1或3或5,
    "agreeableness": 1或3或5,
    "neuroticism": 1或3或5
  }},
  "evidence": {{
    "openness_to_experience": "具体证据引用",
    "conscientiousness": "具体证据引用",
    "extraversion": "具体证据引用",
    "agreeableness": "具体证据引用",
    "neuroticism": "具体证据引用"
  }},
  "confidence": "high/medium/low"
}}
```

**再次提醒：每个评分必须是1、3或5，不能使用其他数值！**
"""

        return prompt

    def _validate_scores(self, scores: Dict[str, int]) -> Dict[str, int]:
        """
        验证并修正评分（确保只使用1、3、5分）
        """
        return ScoringValidator.validate_scores(scores)

    def __init__(self, api_key: str = None, use_ollama_first: bool = False, segment_size: int = 5):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.client = APIClient()
        self.use_ollama_first = use_ollama_first
        self.segment_size = segment_size  # 默认分段大小
        self.failed_models = set()  # 记录失败的模型，避免重复尝试

        # 检查API密钥是否设置
        if not self.api_key:
            print("⚠️  OpenRouter API密钥未设置，将优先使用Ollama本地模型")
            self.use_ollama_first = True
        
        # 主评估器列表
        cloud_models = [
            {"name": "google/gemini-2.0-flash-exp:free", "description": "Google Gemini 2.0 Flash (1M上下文)"},
            {"name": "deepseek/deepseek-r1:free", "description": "DeepSeek R1 (163K上下文)"},
            {"name": "qwen/qwen3-235b-a22b:free", "description": "Qwen3 235b (131K上下文)"},
            {"name": "mistralai/mistral-small-3.2-24b-instruct:free", "description": "Mistral Small (131K上下文)"},
            {"name": "meta-llama/llama-3.3-70b-instruct:free", "description": "Llama 3.3 70B (65K上下文)"},
            {"name": "moonshotai/kimi-k2:free", "description": "Moonshot Kimi K2 (32K上下文)"}
        ]
        
        # Ollama模型列表（备用）- 使用实际存在的模型名称
        ollama_models = [
            {"name": "llama3.2:3b", "description": "Llama3.2 3B (本地模型)"},
            {"name": "gemma2:2b", "description": "Gemma2 2B (本地模型)"},
            {"name": "qwen3:4b", "description": "Qwen3 4B (本地模型)"},
            {"name": "deepseek-r1:8b", "description": "DeepSeek R1 8B (本地模型)"}
        ]
        
        # 根据配置决定模型优先级
        if self.use_ollama_first:
            self.models = ollama_models + cloud_models
        else:
            self.models = cloud_models
        
        print(f"📊 使用模型列表 ({'Ollama优先' if self.use_ollama_first else '云模型优先'}):")
        for i, model in enumerate(self.models[:5], 1):  # 显示前5个模型
            print(f"  {i}. {model['name']} ({model['description']})")
        if len(self.models) > 5:
            print(f"  ... 还有 {len(self.models) - 5} 个模型")
        print(f"📏 分段大小: {self.segment_size}题/段")

    def _analyze_segment_with_model(self, model_config: Dict, segment: List[Dict], segment_number: int, total_segments: int, max_retries: int = 3) -> Dict:
        """
        使用指定模型分析单个分段，支持多级重试
        """
        # 检查模型是否已在失败列表中
        model_name = model_config['name']
        if model_name in self.failed_models:
            return {
                'success': False,
                'segment_number': segment_number,
                'model': model_name,
                'error': f'模型 {model_name} 已被标记为失败，跳过',
                'raw_response': 'Model marked as failed'
            }

        prompt = self._create_segment_prompt(segment, segment_number, total_segments)

        print(f"    📡 调用 {model_config['name']} 分析段{segment_number}...")

        # 尝试多次调用
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"      🔄 第 {attempt + 1} 次重试 (等待20秒)...")
                time.sleep(20)  # 每次重试等待20秒
            
            eval_result = self.client.evaluate(
                model=model_config['name'],
                prompt=prompt,
                system_prompt="你是专业的心理评估分析师。必须严格使用1-3-5评分标准。",
                service_preference="auto"  # 自动尝试不同服务
            )

            if not eval_result['success']:
                error_msg = eval_result.get('error', 'Unknown error')
                print(f"      ❌ {model_config['name']} 调用失败 (尝试 {attempt + 1}/{max_retries}): {error_msg}")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'segment_number': segment_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': 'API call failed after retries and model marked as failed'
                    }
                
                continue  # 继续下一次尝试

            content = eval_result['response']

            # 检查响应是否为空
            if not content or content.strip() == "":
                error_msg = 'API响应为空'
                print(f"      ❌ {model_config['name']}: {error_msg} (尝试 {attempt + 1}/{max_retries})")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'segment_number': segment_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': 'No content after retries and model marked as failed'
                    }
                
                continue  # 继续下一次尝试

            # 解析JSON - 提取```json```包裹的内容
            try:
                print(f"      🔍 {model_config['name']} 解析JSON响应...")

                # 先尝试匹配```json```包裹的内容
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"      ✅ {model_config['name']} 找到```json```包裹的内容")
                    result = json.loads(json_str)
                else:
                    # 尝试匹配单独的JSON对象
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        print(f"      ✅ {model_config['name']} 找到JSON对象")
                        result = json.loads(json_str)
                    else:
                        # 尝试直接解析
                        print(f"      ⚠️ {model_config['name']} 尝试直接解析整个响应...")
                        result = json.loads(content)

                print(f"      ✅ {model_config['name']} JSON解析成功")

            except json.JSONDecodeError as e:
                error_msg = f'JSON解析失败: {str(e)[:100]}'
                print(f"      ❌ {model_config['name']} {error_msg} (尝试 {attempt + 1}/{max_retries})")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'segment_number': segment_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': content[:500] if content else 'No content and model marked as failed'
                    }
                
                continue  # 继续下一次尝试
            except Exception as e:
                error_msg = f'响应处理失败: {str(e)}'
                print(f"      ❌ {model_config['name']} {error_msg} (尝试 {attempt + 1}/{max_retries})")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'segment_number': segment_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': content[:500] if content else 'No content and model marked as failed'
                    }
                
                continue  # 继续下一次尝试

            # 验证并修正评分标准
            if 'scores' in result:
                corrected_scores = self._validate_scores(result['scores'])
                
                if corrected_scores != result['scores']:
                    invalid_scores = []
                    for trait in result['scores']:
                        if result['scores'][trait] != corrected_scores[trait]:
                            invalid_scores.append(f"{trait}:{result['scores'][trait]}→{corrected_scores[trait]}")
                    print(f"      ⚠️ {model_config['name']} 修正无效评分: {invalid_scores}")
                
                result['scores'] = corrected_scores

            result['model'] = model_name
            result['segment_number'] = segment_number
            result['processing_time'] = time.time()

            return result

        # 如果所有重试都失败，返回错误
        return {
            'success': False,
            'segment_number': segment_number,
            'model': model_name,
            'error': f'分析失败: 经过 {max_retries} 次尝试仍然失败',
            'raw_response': 'Analysis failed after retries'
        }

    def _analyze_single_question_with_model(self, model_config: Dict, question: Dict, question_number: int, total_questions: int, max_retries: int = 3) -> Dict:
        """
        使用指定模型分析单个问题，支持多级重试
        """
        # 检查模型是否已在失败列表中
        model_name = model_config['name']
        if model_name in self.failed_models:
            return {
                'success': False,
                'question_number': question_number,
                'model': model_name,
                'error': f'模型 {model_name} 已被标记为失败，跳过',
                'raw_response': 'Model marked as failed'
            }

        prompt = self._create_question_by_question_prompt(question, question_number, total_questions)

        print(f"    📡 调用 {model_config['name']} 分析题{question_number}...")

        # 尝试多次调用
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"      🔄 第 {attempt + 1} 次重试 (等待20秒)...")
                time.sleep(20)  # 每次重试等待20秒
            
            eval_result = self.client.evaluate(
                model=model_config['name'],
                prompt=prompt,
                system_prompt="你是专业的心理评估分析师。必须严格使用1-3-5评分标准。",
                service_preference="auto"  # 自动尝试不同服务
            )

            if not eval_result['success']:
                error_msg = eval_result.get('error', 'Unknown error')
                print(f"      ❌ {model_config['name']} 调用失败 (尝试 {attempt + 1}/{max_retries}): {error_msg}")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'question_number': question_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': 'API call failed after retries and model marked as failed'
                    }
                
                continue  # 继续下一次尝试

            content = eval_result['response']

            # 检查响应是否为空
            if not content or content.strip() == "":
                error_msg = 'API响应为空'
                print(f"      ❌ {model_config['name']}: {error_msg} (尝试 {attempt + 1}/{max_retries})")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'question_number': question_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': 'No content after retries and model marked as failed'
                    }
                
                continue  # 继续下一次尝试

            # 解析JSON - 提取```json```包裹的内容
            try:
                print(f"      🔍 {model_config['name']} 解析JSON响应...")

                # 先尝试匹配```json```包裹的内容
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"      ✅ {model_config['name']} 找到```json```包裹的内容")
                    result = json.loads(json_str)
                else:
                    # 尝试匹配单独的JSON对象
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        print(f"      ✅ {model_config['name']} 找到JSON对象")
                        result = json.loads(json_str)
                    else:
                        # 尝试直接解析
                        print(f"      ⚠️ {model_config['name']} 尝试直接解析整个响应...")
                        result = json.loads(content)

                print(f"      ✅ {model_config['name']} JSON解析成功")

            except json.JSONDecodeError as e:
                error_msg = f'JSON解析失败: {str(e)[:100]}'
                print(f"      ❌ {model_config['name']} {error_msg} (尝试 {attempt + 1}/{max_retries})")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'question_number': question_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': content[:500] if content else 'No content and model marked as failed'
                    }
                
                continue  # 继续下一次尝试
            except Exception as e:
                error_msg = f'响应处理失败: {str(e)}'
                print(f"      ❌ {model_config['name']} {error_msg} (尝试 {attempt + 1}/{max_retries})")
                
                if attempt == max_retries - 1:  # 最后一次尝试也失败
                    # 将模型标记为失败，后续不再使用
                    self.failed_models.add(model_name)
                    print(f"      🚫 将模型 {model_name} 标记为失败，后续评估将不再使用")
                    
                    return {
                        'success': False,
                        'question_number': question_number,
                        'model': model_name,
                        'error': error_msg,
                        'raw_response': content[:500] if content else 'No content and model marked as failed'
                    }
                
                continue  # 继续下一次尝试

            # 验证并修正评分标准
            if 'scores' in result:
                corrected_scores = self._validate_scores(result['scores'])
                
                if corrected_scores != result['scores']:
                    invalid_scores = []
                    for trait in result['scores']:
                        if result['scores'][trait] != corrected_scores[trait]:
                            invalid_scores.append(f"{trait}:{result['scores'][trait]}→{corrected_scores[trait]}")
                    print(f"      ⚠️ {model_config['name']} 修正无效评分: {invalid_scores}")
                
                result['scores'] = corrected_scores

            result['model'] = model_name
            result['question_number'] = question_number
            result['processing_time'] = time.time()

            return result

        # 如果所有重试都失败，返回错误
        return {
            'success': False,
            'question_number': question_number,
            'model': model_name,
            'error': f'分析失败: 经过 {max_retries} 次尝试仍然失败',
            'raw_response': 'Analysis failed after retries'
        }

    def _calculate_model_consistency(self, model_results: List[Dict]) -> Dict:
        """
        计算多个模型间的一致性
        """
        if len(model_results) < 2:
            return {"error": "需要至少2个模型的结果"}

        # 修正：根据传入的参数类型进行处理，传入的是包含模型名称和评分的字典列表
        successful_models = []
        for result in model_results:
            if isinstance(result, dict) and 'model' in result and 'scores' in result:
                successful_models.append(result)
            elif isinstance(result, dict) and 'model' in result:
                # 如果传入的是模型名称和完整结果的字典，例如在evaluate_file_with_multiple_models调用时
                if 'final_scores' in result:
                    successful_models.append({
                        'model': result['model'],
                        'scores': result['final_scores']
                    })

        if len(successful_models) < 2:
            return {"error": f"成功模型数量不足: {len(successful_models)}/{len(model_results)}"}

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        consistency_analysis = {}

        for trait in traits:
            scores = []
            model_names = []

            for result in successful_models:
                if 'scores' in result and trait in result['scores']:
                    scores.append(result['scores'][trait])
                    model_names.append(result['model'])

            if len(scores) >= 2:
                avg_score = statistics.mean(scores)
                max_score = max(scores)
                min_score = min(scores)
                score_range = max_score - min_score

                # 一致性评估
                if score_range == 0:
                    consistency_level = "完全一致"
                    consistency_score = 100
                elif score_range <= 1:
                    consistency_level = "高度一致"
                    consistency_score = 80
                elif score_range <= 2:
                    consistency_level = "中等一致"
                    consistency_score = 60
                else:
                    consistency_level = "差异较大"
                    consistency_score = 40

                consistency_analysis[trait] = {
                    "scores": dict(zip(model_names, scores)),
                    "average": avg_score,
                    "range": score_range,
                    "consistency_level": consistency_level,
                    "consistency_score": consistency_score
                }

        # 计算总体一致性
        overall_scores = [analysis.get('consistency_score', 0) for analysis in consistency_analysis.values()]
        overall_consistency = statistics.mean(overall_scores) if overall_scores else 0

        return {
            "trait_analysis": consistency_analysis,
            "overall_consistency": overall_consistency,
            "successful_models": len(successful_models),
            "total_models": len(model_results),
            "discrepancies": [trait for trait, analysis in consistency_analysis.items() if analysis.get("range", 0) > 1]
        }

    def analyze_file_with_three_models(self, file_path: str, output_dir: str) -> Dict:
        """
        使用三个模型独立分析单个文件（保留此方法以保持向后兼容）
        """
        return self.evaluate_file_with_multiple_models(file_path, output_dir)

    def evaluate_file_with_multiple_models(self, file_path: str, output_dir: str, segment_size: int = None) -> Dict:
        """
        使用多个模型评估单个文件（主要方法）
        如果未指定segment_size，则使用实例变量self.segment_size
        """
        print(f"📈 开始多模型评估: {Path(file_path).name}")

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取问题
            questions = []
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for item in data['assessment_results']:
                    if isinstance(item, dict):
                        question_data = item.get('question_data', {})
                        if isinstance(question_data, dict):
                            question_text = question_data.get('prompt_for_agent', 
                                question_data.get('mapped_ipip_concept', ''))
                            
                            answer_text = item.get('extracted_response', '')
                            
                            if question_text and answer_text:
                                questions.append({
                                    'question_id': item.get('question_id'),
                                    'question_data': question_data,
                                    'extracted_response': answer_text
                                })

            if len(questions) < 1:
                raise Exception(f"问题数量不足：{len(questions)}")

            # 分段处理（使用指定的分段大小或默认值）
            if segment_size is None:
                segment_size = self.segment_size
                
            segments = self._create_segments(questions, segment_size)
            total_segments = len(segments)
            print(f"  📊 {len(questions)}题 -> {total_segments}个分段 (每段{segment_size}题)")

            # 为当前文件创建临时目录保存分段
            file_stem = Path(file_path).stem
            temp_dir = Path(output_dir) / "temp_segments" / file_stem
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存分段文件
            for i, segment in enumerate(segments, 1):
                segment_file = temp_dir / f"segment_{i:03d}.json"
                with open(segment_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "segment_info": {
                            "segment_number": i,
                            "total_segments": total_segments,
                            "questions_count": len(segment),
                        },
                        "segment_data": segment
                    }, f, ensure_ascii=False, indent=2)
            
            print(f"  📁 分段文件已保存到: {temp_dir}")

            # 模型评估结果存储
            model_analysis_results = {}

            # 选择前3个模型进行初始评估
            selected_models = [m for m in self.models[:3] if m['name'] not in self.failed_models]
            if not selected_models:
                print("  ❌ 所有模型都已失败，无法进行评估")
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': '所有模型都已失败，无法进行评估'
                }

            # 对每个模型进行独立评估
            for model_config in selected_models:
                print(f"  🤖 使用模型: {model_config['name']} ({model_config['description']})")

                model_segments = []
                segment_results = []

                # 评估每个分段
                for i, segment in enumerate(segments, 1):
                    result = self._analyze_segment_with_model(model_config, segment, i, total_segments)
                    segment_results.append(result)

                    if result['success']:
                        print(f"      ✅ 段{i}: {list(result['scores'].values())}")
                    else:
                        print(f"      ❌ 段{i}: {result.get('error', 'Unknown error')}")

                    time.sleep(3)  # API限制

                # 计算该模型的最终评分
                if segment_results:
                    final_scores = {}
                    for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                        all_scores = []
                        for result in segment_results:
                            if result.get('success') and 'scores' in result:
                                if trait in result['scores']:
                                    all_scores.append(result['scores'][trait])

                        if all_scores:
                            final_scores[trait] = statistics.median(all_scores)
                            final_scores[trait] = int(round(final_scores[trait]))  # 确保是整数

                    model_analysis_results[model_config['name']] = {
                        "segment_results": segment_results,
                        "final_scores": final_scores,
                        "successful_segments": len([r for r in segment_results if r.get('success')]),
                        "total_segments": total_segments
                    }

            # 计算模型间一致性
            print(f"  📊 计算模型一致性...")
            final_scores_list = [
                {"model": model, "scores": results["final_scores"]}
                for model, results in model_analysis_results.items()
            ]
            
            consistency_analysis = self._calculate_model_consistency(final_scores_list)

            # 创建信度验证器并计算信度
            print(f"  📊 计算信度指标...")
            reliability_validator = ReliabilityValidator(threshold=0.8)
            reliability_metrics = reliability_validator.calculate_overall_reliability(model_analysis_results)
            reliability_report = reliability_validator.generate_reliability_report(model_analysis_results, reliability_metrics)
            
            # 检查是否存在争议
            print(f"  🔍 检查评估争议...")
            all_scores = []
            for model_name, results in model_analysis_results.items():
                for segment_result in results['segment_results']:
                    if segment_result.get('success') and 'scores' in segment_result:
                        # 将段结果转换为问题级别结果（简化处理）
                        for trait, score in segment_result['scores'].items():
                            all_scores.append({
                                'question_id': f"segment_{segment_result['segment_number']}_{trait}",
                                'trait': trait,
                                'score': score,
                                'model': model_name
                            })
            
            # 更新：将model_analysis_results存储为实例变量，以便在争议解决中使用
            self.model_analysis_results = model_analysis_results
            
            dispute_manager = EnhancedDisputeResolutionManager()
            disputes = dispute_manager.identify_disputes(all_scores, threshold=1)
            
            if disputes:
                print(f"  ⚠️  发现 {len(disputes)} 个争议")
                # 如果存在争议，尝试使用额外评估器解决
                resolved_disputes = dispute_manager.resolve_disputes_with_additional_evaluators(
                    self, disputes, all_scores, questions, segment_size
                )
            else:
                print(f"  ✅ 未发现显著争议")
                resolved_disputes = None

            # 计算最终评分 - 基于争议解决后的结果
            final_combined_scores = self._calculate_final_scores_after_resolution(
                model_analysis_results, resolved_disputes
            )

            # 执行人格分析
            print(f"  🧠 执行人格分析...")
            personality_analyzer = PersonalityAnalyzer()
            personality_analysis = personality_analyzer.analyze_personality(final_combined_scores)

            # 保存结果
            output_filename = f"{Path(file_path).stem}_segmented_scoring_evaluation.json"
            output_path = os.path.join(output_dir, output_filename)

            analysis_result = {
                "file_info": {
                    "filename": Path(file_path).name,
                    "total_questions": len(questions),
                    "segments_count": total_segments,
                    "questions_per_segment": segment_size,
                    "analysis_date": datetime.now().isoformat()
                },
                "models_used": selected_models,
                "model_results": model_analysis_results,
                "consistency_analysis": consistency_analysis,
                "reliability_analysis": {
                    "metrics": reliability_metrics,
                    "report": reliability_report
                },
                "dispute_analysis": {
                    "disputes_identified": len(disputes),
                    "resolved_disputes": resolved_disputes,
                    "dispute_resolution_needed": len(disputes) > 0,
                    "final_combined_scores": final_combined_scores
                },
                "personality_analysis": personality_analysis,
                "segmentation_info": {
                    "temp_directory": str(temp_dir),
                    "segment_files_count": total_segments,
                },
                "summary": {
                    "overall_consistency": consistency_analysis.get('overall_consistency', 0),
                    "overall_reliability": reliability_metrics.get('overall_reliability', 0),
                    "model_count": len(selected_models),
                    "successful_models": consistency_analysis.get('successful_models', 0),
                    "reliability_passed": reliability_report.get('validation_passed', False),
                    "final_scores": final_combined_scores
                }
            }

            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)

            print(f"  💾 结果已保存: {output_filename}")

            # 显示简要结果
            print(f"  📋 评估结果摘要:")
            for model, results in model_analysis_results.items():
                print(f"    {model}: {results['final_scores']} ({results['successful_segments']}/{results['total_segments']}段成功)")

            print(f"  🎯 模型一致性: {consistency_analysis.get('overall_consistency', 0):.1f}%")
            print(f"  🎯 整体信度: {reliability_metrics.get('overall_reliability', 0):.1f}%")
            print(f"  🎯 信度验证: {'✅ 通过' if reliability_report.get('validation_passed', False) else '❌ 未通过'}")
            print(f"  🧠 MBTI类型: {personality_analysis['mbti_analysis']['mbti_type']}")
            print(f"  🧠 大五人格概要: {personality_analysis['big5_analysis']['summary']['big5_profile']}")

            return {
                'success': True,
                'file_path': file_path,
                'output_path': output_path,
                'model_results': model_analysis_results,
                'consistency_analysis': consistency_analysis,
                'reliability_analysis': {
                    'metrics': reliability_metrics,
                    'report': reliability_report
                },
                'personality_analysis': personality_analysis,
                'final_combined_scores': final_combined_scores,
                'segmentation_info': {
                    'temp_directory': str(temp_dir),
                    'segment_files_count': total_segments,
                },
                'consistency_score': consistency_analysis.get('overall_consistency', 0),
                'reliability_score': reliability_metrics.get('overall_reliability', 0),
                'reliability_passed': reliability_report.get('validation_passed', False)
            }

        except Exception as e:
            print(f"  ❌ 文件评估失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def _calculate_final_scores_after_resolution(self, model_analysis_results: Dict, resolved_disputes: Dict) -> Dict[str, float]:
        """
        在争议解决后计算最终评分
        """
        # 首先获取各模型的最终评分
        all_model_scores = []
        for model_name, results in model_analysis_results.items():
            if 'final_scores' in results:
                all_model_scores.append(results['final_scores'])
        
        # 如果没有争议或争议解决为空，直接返回平均分
        if not resolved_disputes or not resolved_disputes.get('resolved_results'):
            # 计算所有模型评分的平均值
            final_scores = {}
            traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
            
            for trait in traits:
                scores = []
                for model_scores in all_model_scores:
                    if trait in model_scores:
                        scores.append(model_scores[trait])
                
                if scores:
                    final_scores[trait] = statistics.mean(scores)
                    final_scores[trait] = round(final_scores[trait], 2)  # 保留两位小数
                else:
                    final_scores[trait] = 3.0  # 默认中性分
            
            return final_scores
        
        # 如果有争议解决结果，需要结合原始评分和解决后的评分
        final_scores = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        for trait in traits:
            scores = []
            # 添加模型原始评分
            for model_scores in all_model_scores:
                if trait in model_scores:
                    scores.append(model_scores[trait])
            
            # 添加争议解决后的评分
            resolved_results = resolved_disputes.get('resolved_results', [])
            for resolved in resolved_results:
                if resolved.get('trait') == trait:
                    scores.append(resolved['final_score'])
            
            if scores:
                final_scores[trait] = statistics.mean(scores)
                final_scores[trait] = round(final_scores[trait], 2)  # 保留两位小数
            else:
                final_scores[trait] = 3.0  # 默认中性分
        
        return final_scores


class ScoringConsistencyAnalyzer:
    """
    评分一致性分析器
    """
    def __init__(self):
        pass

    def calculate_consistency(self, model_results: List[Dict]) -> Dict:
        """
        计算多个模型间的一致性
        """
        if len(model_results) < 2:
            return {"error": "需要至少2个模型的结果"}

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        consistency_analysis = {}

        for trait in traits:
            scores = []
            model_names = []

            for result in model_results:
                if 'scores' in result and trait in result['scores']:
                    scores.append(result['scores'][trait])
                    model_names.append(result['model'])

            if len(scores) >= 2:
                avg_score = statistics.mean(scores)
                max_score = max(scores)
                min_score = min(scores)
                score_range = max_score - min_score

                # 一致性评估
                if score_range == 0:
                    consistency_level = "完全一致"
                    consistency_score = 100
                elif score_range <= 1:
                    consistency_level = "高度一致"
                    consistency_score = 80
                elif score_range <= 2:
                    consistency_level = "中等一致"
                    consistency_score = 60
                else:
                    consistency_level = "差异较大"
                    consistency_score = 40

                consistency_analysis[trait] = {
                    "scores": dict(zip(model_names, scores)),
                    "average": avg_score,
                    "range": score_range,
                    "consistency_level": consistency_level,
                    "consistency_score": consistency_score
                }

        # 计算总体一致性
        overall_scores = [analysis.get('consistency_score', 0) for analysis in consistency_analysis.values()]
        overall_consistency = statistics.mean(overall_scores) if overall_scores else 0

        return {
            "trait_analysis": consistency_analysis,
            "overall_consistency": overall_consistency,
            "successful_models": len(model_results),
            "total_models": len(model_results)
        }


class EnhancedDisputeResolutionManager:
    """
    增强分歧处理管理器
    """
    def __init__(self):
        # 定义额外的评估器列表，用于分歧处理
        self.dispute_models = [
            {"name": "google/gemini-2.0-flash-exp:free", "description": "Google Gemini 2.0 Flash (1M上下文)"},
            {"name": "moonshotai/kimi-k2:free", "description": "Moonshot Kimi K2 (32K上下文)"},
            {"name": "anthropic/claude-3-haiku", "description": "Claude 3 Haiku (200K上下文)"}
        ]
        
        # Ollama模型列表（备用）用于分歧解决
        self.ollama_dispute_models = [
            {"name": "qwen3:4b", "description": "Qwen3 4B (本地模型)"},
            {"name": "gemma2:2b", "description": "Gemma2 2B (本地模型)"},
            {"name": "llama3.2:3b", "description": "Llama3.2 3B (本地模型)"}
        ]

    def identify_disputes(self, all_scores: List[Dict], threshold: int = 1) -> List[Dict]:
        """
        识别评分中的分歧
        """
        # 按问题ID和特质分组评分
        scores_by_question_trait = {}
        for score_record in all_scores:
            # 确保记录包含必要的字段
            if 'question_id' not in score_record or 'trait' not in score_record or 'score' not in score_record:
                continue
                
            qid = score_record['question_id']
            trait = score_record['trait']
            
            key = f"{qid}_{trait}"
            if key not in scores_by_question_trait:
                scores_by_question_trait[key] = []
            scores_by_question_trait[key].append(score_record)

        disputes = []
        for key, scores_list in scores_by_question_trait.items():
            # 提取所有评分
            scores = [record['score'] for record in scores_list]
            if len(scores) < 2:
                continue

            max_score = max(scores)
            min_score = min(scores)
            score_range = max_score - min_score

            if score_range > threshold:
                # 从key中提取问题id和特质
                parts = key.split('_', 1)
                if len(parts) == 2:
                    try:
                        qid = int(parts[0])
                        trait = parts[1]
                        disputes.append({
                            "question_id": qid,
                            "trait": trait,
                            "scores": scores,
                            "models": [record['model'] for record in scores_list],
                            "max_diff": score_range,
                            "average_score": statistics.mean(scores),
                            "evidence": [record.get('evidence', '') for record in scores_list]
                        })
                    except ValueError:
                        # 如果无法解析问题ID为整数，则跳过
                        continue

        return disputes

    def apply_majority_decision(self, scores: List[int]) -> int:
        """
        应用多数决策原则（去除最高分和最低分后取中位数）
        """
        if len(scores) <= 2:
            # 如果只有1或2个评分，直接取平均值并四舍五入
            return round(statistics.mean(scores)) if scores else 0

        # 去除一个最高分和一个最低分
        scores_sorted = sorted(scores)
        if len(scores_sorted) > 2:
            trimmed_scores = scores_sorted[1:-1]  # 去除首尾
        else:
            trimmed_scores = scores_sorted

        # 返回剩余评分的中位数
        if trimmed_scores:
            # 对于多数决策，使用中位数作为最终得分
            return int(statistics.median(trimmed_scores))
        else:
            # 如果修剪后没有评分，返回原评分的平均值
            return round(statistics.mean(scores)) if scores else 0
    
    def get_additional_evaluators(self, round_number: int) -> List[Dict]:
        """
        根据轮次获取额外的评估器，优先使用云模型，后使用Ollama模型
        """
        if round_number == 1:
            # 第一轮争议时，添加2个额外评估器（优先云模型）
            available_models = self.dispute_models
            return available_models[:2] if len(available_models) >= 2 else available_models
        elif round_number == 2:
            # 第二轮争议时，添加Ollama模型作为回退
            available_models = self.ollama_dispute_models
            return available_models[:2] if len(available_models) >= 2 else available_models
        else:
            # 后续轮次，在所有可用模型中循环使用
            all_models = self.dispute_models + self.ollama_dispute_models
            start_idx = (round_number - 1) * 2  # 从相应的模型开始
            selected_models = []
            for i in range(2):  # 选择2个模型
                model_idx = (start_idx + i) % len(all_models)
                selected_models.append(all_models[model_idx])
            return selected_models
    
    def resolve_disputes_with_additional_evaluators(self, evaluator, disputes: List[Dict], 
                                                   original_results: List[Dict], 
                                                   questions: List[Dict], 
                                                   segment_size: int = 5) -> Dict:
        """
        使用额外评估器解决分歧
        """
        print(f"🔍 识别到 {len(disputes)} 个分歧，开始解决...")
        
        # 按问题组织原始结果
        question_results = {}
        for result in original_results:
            qid = result.get('question_id')
            if qid not in question_results:
                question_results[qid] = []
            question_results[qid].append(result)
        
        resolved_results = []
        unresolved_disputes = []
        
        round_number = 1
        max_rounds = 3  # 最多进行3轮争议解决
        
        current_disputes = disputes.copy()
        
        while current_disputes and round_number <= max_rounds:
            print(f"🔄 第 {round_number} 轮争议解决，当前有 {len(current_disputes)} 个未解决问题")
            
            # 获取当前轮次的额外评估器
            additional_evaluators = self.get_additional_evaluators(round_number)
            if not additional_evaluators:
                print(f"⚠️  没有更多评估器可以使用，停止争议解决")
                break
            
            print(f"🤖 使用额外评估器: {[m['name'] for m in additional_evaluators]}")
            
            new_scores = []
            
            # 对每个争议问题进行额外评估
            for dispute in current_disputes:
                question_id = dispute['question_id']
                
                # 找到对应的问题
                question = None
                for q in questions:
                    if q.get('question_id') == question_id:
                        question = q
                        break
                
                if not question:
                    continue
                
                # 创建针对该问题的分段（包含争议特质）
                question_segment = [question]
                
                # 使用额外评估器对争议问题进行评估
                for model_config in additional_evaluators:
                    result = evaluator._analyze_segment_with_model(
                        model_config, 
                        question_segment, 
                        1,  # 分段编号，这里只处理单个问题
                        1,  # 总分段数
                        max_retries=2  # 争议解决时减少重试次数以提高效率
                    )
                    
                    if result['success']:
                        # 提取争议特质的评分
                        trait = dispute['trait']
                        if 'scores' in result and trait in result['scores']:
                            new_scores.append({
                                'question_id': question_id,
                                'trait': trait,
                                'score': result['scores'][trait],
                                'model': model_config['name'],
                                'round': round_number,
                                'evidence': result.get('evidence', {}).get(trait, '')
                            })
            
            # 重新评估争议 - 合并原始评分和新评分
            all_current_scores = []
            
            # 添加原始评分（从segment_results中提取）
            for model_name, model_result in evaluator.model_analysis_results.items():
                for segment_result in model_result['segment_results']:
                    if segment_result.get('success') and 'scores' in segment_result:
                        for trait, score in segment_result['scores'].items():
                            all_current_scores.append({
                                'question_id': segment_result.get('segment_number', 0),  # 使用分段号作为问题ID
                                'trait': trait,
                                'score': score,
                                'model': model_name
                            })
            
            # 添加新评分
            for score in new_scores:
                all_current_scores.append(score)
            
            # 重新识别分歧
            updated_disputes = self.identify_disputes(
                all_current_scores, 
                threshold=1
            )
            
            print(f"📊 第 {round_number} 轮后，仍有 {len(updated_disputes)} 个争议")
            
            # 如果没有争议了，跳出循环
            if not updated_disputes:
                print(f"✅ 所有争议在第 {round_number} 轮后得到解决")
                break
            
            # 检查是否达到最大轮次
            if round_number >= max_rounds:
                print(f"⚠️  已达到最大争议解决轮次({max_rounds})，仍有 {len(updated_disputes)} 个争议未解决")
                unresolved_disputes = updated_disputes
                break
                
            # 更新争议列表
            current_disputes = updated_disputes
            round_number += 1
        
        # 为了解决循环引用问题，我们在这里使用多数决策来最终确定评分
        final_resolved_scores = []
        for dispute in unresolved_disputes:
            final_score = self.apply_majority_decision(dispute['scores'])
            final_resolved_scores.append({
                'question_id': dispute['question_id'],
                'trait': dispute['trait'],
                'initial_dispute': dispute['max_diff'],
                'final_score': final_score
            })
        
        return {
            'resolved_results': final_resolved_scores,  # 包含最终解决的评分
            'unresolved_disputes': unresolved_disputes,
            'new_scores': new_scores,
            'rounds_used': round_number,
            'dispute_resolution_status': 'complete' if not updated_disputes else 'partial'
        }


# 创建一个兼容旧版本的类
class DisputeResolutionManager(EnhancedDisputeResolutionManager):
    """
    保持与旧代码兼容的分歧处理管理器
    """
    pass


class ReliabilityValidator:
    """
    信度验证器
    """
    def __init__(self, threshold=0.8):
        """
        初始化信度验证器
        :param threshold: 信度阈值，默认0.8
        """
        self.threshold = threshold

    def calculate_cronbach_alpha(self, scores_matrix: List[List[float]]) -> float:
        """
        计算Cronbach's Alpha系数
        :param scores_matrix: 评分矩阵，每一行代表一个评估器对所有问题的评分，每一列代表一个问题的所有评估器评分
        :return: Cronbach's Alpha系数
        """
        if np is None:
            print("⚠️ 未安装numpy，Cronbach's Alpha计算不可用")
            return 0.0
        
        scores = np.array(scores_matrix)
        
        if scores.size == 0:
            return 0.0
            
        # 检查矩阵维度
        if len(scores.shape) < 2 or scores.shape[0] < 2 or scores.shape[1] < 2:
            return 0.0  # 需要至少2个评估器和2个问题
        
        # 计算每道题（每列）的方差（项目间方差）
        item_variances = np.var(scores, axis=0, ddof=1)  # 每列(题目)的方差，使用样本方差
        sum_of_item_variances = np.sum(item_variances)
        
        # 计算每个评估器（每行）的总分
        rater_totals = np.sum(scores, axis=1)  # 每行(评估器)的总和
        
        # 计算总分方差（评估者间方差）
        total_scores_variance = np.var(rater_totals, ddof=1)  # 使用样本方差
        
        if total_scores_variance == 0:
            # 如果所有评估器的总分相同，说明完全一致
            if sum_of_item_variances == 0:
                # 所有值都相同
                return 1.0
            else:
                # 每列内部不同，但每行总分相同
                return 0.0 if sum_of_item_variances > 0 else 1.0
        
        n_items = scores.shape[1]  # 问题数量
        
        # Cronbach's Alpha公式
        # α = (k / (k-1)) * (1 - Σsi² / sT²)
        # 其中 k 是题目数，si² 是每个题目的方差，sT² 是总分方差
        if sum_of_item_variances == 0:
            return 1.0  # 每个列内部完全一致，但行间可能不同
        
        alpha = (n_items / (n_items - 1)) * (1 - sum_of_item_variances / total_scores_variance)
        
        return max(0.0, min(1.0, alpha))  # 确保Alpha在0-1之间

    def calculate_inter_rater_reliability(self, scores_by_trait: Dict[str, List[float]]) -> Dict[str, float]:
        """
        计算评估者间信度
        :param scores_by_trait: 按特质分组的评分
        :return: 每个特质的信度系数
        """
        reliability_scores = {}
        
        for trait, scores_list in scores_by_trait.items():
            if len(scores_list) < 2:
                reliability_scores[trait] = 0.0
                continue
            
            # 使用评分差异的倒数作为一致性指标
            if len(set(scores_list)) == 1:  # 所有评分相同
                reliability_scores[trait] = 1.0
            elif len(scores_list) >= 2:
                # 计算标准差，标准差越小一致性越高
                std_dev = statistics.stdev(scores_list) if len(scores_list) > 1 else 0
                max_score_range = max(scores_list) - min(scores_list)
                
                # 如果标准差为0，说明完全一致
                if std_dev == 0:
                    reliability_scores[trait] = 1.0
                else:
                    # 归一化到0-1范围，一致性越高分数越高
                    # 通过评分范围和标准差来估计一致性
                    if max_score_range > 0:
                        # 一致性 = 1 - (标准差/评分范围)
                        consistency = max(0, 1 - (std_dev / max_score_range))
                        reliability_scores[trait] = consistency
                    else:
                        reliability_scores[trait] = 0.0
            else:
                reliability_scores[trait] = 0.0
        
        return reliability_scores

    def calculate_overall_reliability(self, model_results: Dict) -> Dict[str, float]:
        """
        计算整体信度
        :param model_results: 模型结果字典
        :return: 包含各项信度指标的字典
        """
        if not model_results:
            return {"overall_reliability": 0.0, "reliability_by_trait": {}}
        
        # 收集所有模型的最终评分
        all_final_scores = []
        scores_by_trait = {
            "openness_to_experience": [],
            "conscientiousness": [],
            "extraversion": [],
            "agreeableness": [],
            "neuroticism": []
        }
        
        for model_name, results in model_results.items():
            if 'final_scores' in results:
                final_scores = results['final_scores']
                model_scores = []
                
                for trait in scores_by_trait.keys():
                    if trait in final_scores:
                        score = final_scores[trait]
                        scores_by_trait[trait].append(score)
                        model_scores.append(score)
                
                if model_scores:
                    all_final_scores.append(model_scores)
        
        # 计算各项信度指标
        trait_reliability = self.calculate_inter_rater_reliability(scores_by_trait)
        
        # 计算Cronbach's Alpha
        if len(all_final_scores) >= 2 and np is not None:
            cronbach_alpha = self.calculate_cronbach_alpha(all_final_scores)
        else:
            cronbach_alpha = 0.0  # 如果numpy不可用或评估器不足，设为0
        
        # 计算平均信度
        avg_reliability = statistics.mean(trait_reliability.values()) if trait_reliability.values() else 0.0
        
        return {
            "overall_reliability": avg_reliability,
            "reliability_by_trait": trait_reliability,
            "cronbach_alpha": cronbach_alpha,
            "avg_reliability": avg_reliability
        }

    def validate_reliability(self, reliability_metrics: Dict) -> bool:
        """
        验证信度是否满足要求
        :param reliability_metrics: 信度指标字典
        :return: 是否通过验证
        """
        overall_reliability = reliability_metrics.get("overall_reliability", 0.0)
        
        # 如果Cronbach's Alpha不可用（因为numpy未安装），只检查评估者间信度
        cronbach_alpha = reliability_metrics.get("cronbach_alpha", 0.0)
        
        # 如果Cronbach's Alpha为0，我们只检查评估者间信度
        if cronbach_alpha == 0.0:
            # 仅基于整体信度进行验证
            return overall_reliability >= self.threshold
        else:
            # 同时检查整体信度和Cronbach's Alpha
            return overall_reliability >= self.threshold and cronbach_alpha >= self.threshold

    def generate_reliability_report(self, model_results: Dict, reliability_metrics: Dict) -> Dict:
        """
        生成信度验证报告
        :param model_results: 模型结果
        :param reliability_metrics: 信度指标
        :return: 信度验证报告
        """
        validation_passed = self.validate_reliability(reliability_metrics)
        
        report = {
            "validation_date": datetime.now().isoformat(),
            "threshold": self.threshold,
            "validation_passed": validation_passed,
            "metrics": reliability_metrics,
            "summary": {
                "reliability_status": "Passed" if validation_passed else "Failed",
                "overall_reliability": reliability_metrics.get("overall_reliability", 0.0),
                "cronbach_alpha": reliability_metrics.get("cronbach_alpha", 0.0),
                "trait_count": len(reliability_metrics.get("reliability_by_trait", {})),
                "total_models": len(model_results) if model_results else 0
            }
        }
        
        return report


def main():
    """
    主函数 - 演示用法
    """
    # 创建评估器实例
    evaluator = SegmentedScoringEvaluator()

    # 输入输出目录
    input_dir = "results/readonly-original"
    output_dir = "segmented_scoring_results"

    # 批量评估 (处理部分文件进行测试)
    evaluator.batch_evaluate(input_dir, output_dir, max_files=5)


if __name__ == "__main__":
    main()