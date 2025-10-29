#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强评估器 - 集成所有修复的稳定评估器
"""

import sys
import os
import json
import time
import subprocess
import re
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import Counter
import concurrent.futures

# 导入修复模块
from resilient_json_serializer import safe_json_dumps, safe_json_loads, EnhancedJSONFileHandler
from intelligent_error_handler import handle_errors, ErrorCategory, RetryConfig
from intelligent_api_manager import global_api_manager, get_api_key, mark_api_error

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class EnhancedEvaluator:
    """增强评估器 - 集成所有技术修复"""

    def __init__(self):
        """初始化增强评估器"""
        self.models = [
            {
                "name": "deepseek-v3.1:671b-cloud",
                "description": "DeepSeek 671B云模型"
            },
            {
                "name": "gpt-oss:20b-cloud",
                "description": "GPT OSS 20B云模型"
            },
            {
                "name": "qwen3-coder:480b-cloud",
                "description": "Qwen3 Coder 480B云模型"
            }
        ]

        # 质量控制设置 - 90%最低成功率阈值
        self.min_success_rate = 0.9
        self.quality_stats = {
            'total_evaluated': 0,
            'passed_quality_threshold': 0,
            'failed_quality_threshold': 0,
            'average_success_rate': 0.0
        }

        # 增强的统计信息
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_segments': 0,
            'successful_segments': 0,
            'high_confidence_files': 0,
            'medium_confidence_files': 0,
            'low_confidence_files': 0,
            'processing_start': None,
            'processing_end': None,
            'error_summary': {}
        }

        # 文件处理器
        self.file_handler = EnhancedJSONFileHandler()

    @handle_errors(ErrorCategory.NETWORK, RetryConfig(max_attempts=3, base_delay=2.0))
    def check_ollama_availability(self) -> Dict[str, bool]:
        """检查三个模型在Ollama中的可用性"""
        print("🔍 检查Ollama模型可用性...")
        availability = {}

        try:
            # 获取Ollama模型列表
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                available_models = result.stdout

                for model in self.models:
                    model_name = model["name"]
                    if model_name in available_models:
                        availability[model_name] = True
                        print(f"  ✅ {model_name} - 可用")
                    else:
                        availability[model_name] = False
                        print(f"  ❌ {model_name} - 不可用")
            else:
                print(f"  ❌ 无法获取Ollama模型列表: {result.stderr}")
                for model in self.models:
                    availability[model["name"]] = False

        except Exception as e:
            print(f"  ❌ Ollama检查失败: {e}")
            for model in self.models:
                availability[model["name"]] = False

        return availability

    @handle_errors(ErrorCategory.NETWORK, RetryConfig(max_attempts=3, base_delay=2.0))
    def execute_ollama_command(self, model_name: str, prompt: str, timeout: int = 300) -> Tuple[bool, str, float]:
        """执行Ollama命令"""
        try:
            cmd = ['ollama', 'run', model_name, prompt, '--format', 'json']

            start_time = time.time()

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )

            end_time = time.time()
            processing_time = end_time - start_time

            if result.returncode == 0:
                cleaned_response = self.clean_terminal_output(result.stdout)
                return True, cleaned_response, processing_time
            else:
                return False, f"命令失败: {result.stderr}", processing_time

        except subprocess.TimeoutExpired:
            return False, "请求超时", timeout
        except Exception as e:
            return False, f"执行错误: {str(e)}", 0

    def clean_terminal_output(self, text: str) -> str:
        """清理终端输出中的控制字符"""
        if not text:
            return ""

        # 移除ANSI转义序列
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', text)

        # 移除其他控制字符
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)

        return cleaned.strip()

    @handle_errors(ErrorCategory.JSON_PARSE, RetryConfig(max_attempts=2, base_delay=0.5))
    def parse_json_response(self, response_text: str) -> Dict:
        """多策略JSON解析器"""
        if not response_text:
            return {"success": False, "error": "响应为空"}

        # 清理响应文本
        response_text = self.clean_terminal_output(response_text)

        # 解析策略 - 优先代码块提取（专门处理gpt-oss:20b-cloud的问题）
        strategies = [
            ("代码块提取", self.extract_json_from_codeblock),
            ("直接解析", self.direct_json_parse),
            ("正则提取", self.extract_json_with_regex),
            ("智能修复", self.smart_json_fix),
            ("模糊匹配", self.fuzzy_score_extract)
        ]

        for strategy_name, strategy_func in strategies:
            try:
                result = strategy_func(response_text)
                if result and self.validate_json_structure(result):
                    return {"success": True, "method": strategy_name, "data": result}
            except Exception:
                continue

        return {
            "success": False,
            "error": "所有解析策略失败",
            "raw_response": response_text[:500] if response_text else "空响应"
        }

    def direct_json_parse(self, text: str) -> Optional[Dict]:
        """直接JSON解析"""
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return json.loads(text)
        return None

    def extract_json_from_codeblock(self, text: str) -> Optional[Dict]:
        """从代码块提取JSON - 专门处理gpt-oss:20b-cloud的Thinking...格式"""
        # 首先尝试标准代码块提取
        patterns = [
            r'```json\s*\n?(\{.*?\})\s*```',
            r'```\s*\n?(\{.*?\})\s*```',
            r'`(\{.*?\})`'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except:
                    continue

        # 如果没有代码块，尝试查找Thinking...后的JSON
        # gpt-oss:20b-cloud经常输出Thinking...然后直接跟JSON
        thinking_patterns = [
            r'Thinking\.\.\.[\s\S]*?(\{[^}]*\{[^}]*\}[^}]*\})',
            r'Thinking\.\.\.[\s\S]*?(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
        ]

        for pattern in thinking_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                try:
                    json_str = match.group(1)
                    # 确保JSON对象完整
                    if json_str.count('{') == json_str.count('}'):
                        return json.loads(json_str.strip())
                except:
                    continue

        # 最后尝试查找完整的JSON对象
        json_start = text.find('{')
        if json_start != -1:
            brace_count = 0
            for i in range(json_start, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = text[json_start:i+1]
                        try:
                            return json.loads(json_str.strip())
                        except:
                            continue
                        break

        return None

    def extract_json_with_regex(self, text: str) -> Optional[Dict]:
        """使用正则表达式提取JSON"""
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            r'\{(?:[^{}"]|"[^"]*")*\}',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        return None

    def smart_json_fix(self, text: str) -> Optional[Dict]:
        """智能修复JSON格式问题"""
        try:
            text = text.lstrip('\ufeff').strip()

            if '{' in text and '}' in text:
                start = text.find('{')
                brace_count = 0
                end = start
                for i, char in enumerate(text[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break

                text = text[start:end]

            # 修复常见问题
            text = re.sub(r'(\w+):', r'"\1":', text)
            text = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)', r': "\1"', text)
            text = re.sub(r'//.*?\n', '', text)
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)

            return json.loads(text)
        except:
            return None

    def fuzzy_score_extract(self, text: str) -> Optional[Dict]:
        """模糊提取评分信息"""
        scores = {}

        patterns = [
            (r'openness_to_experience["\s]*:["\s]*([1-5])', 'openness_to_experience'),
            (r'conscientiousness["\s]*:["\s]*([1-5])', 'conscientiousness'),
            (r'extraversion["\s]*:["\s]*([1-5])', 'extraversion'),
            (r'agreeableness["\s]*:["\s]*([1-5])', 'agreeableness'),
            (r'neuroticism["\s]*:["\s]*([1-5])', 'neuroticism')
        ]

        for pattern, trait in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scores[trait] = int(match.group(1))

        if scores:
            return {
                "success": True,
                "scores": scores,
                "extraction_method": "fuzzy",
                "confidence": "medium"
            }

        return None

    def validate_json_structure(self, data: Dict) -> bool:
        """验证JSON数据结构"""
        if not isinstance(data, dict):
            return False

        if 'success' not in data:
            return False

        if 'scores' in data:
            scores = data['scores']
            if not isinstance(scores, dict):
                return False

            for trait, score in scores.items():
                if not isinstance(score, int) or score not in [1, 3, 5]:
                    return False

        return True

    def create_5segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """创建5题分段分析提示"""
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
- **5分**：极高表现 - 明显具备该特质

**特别注意：只能使用1、3、5三个整数分数，禁止使用2、4等其他数值！**

**第{segment_number}段问卷内容（{len(segment)}题/共{total_segments}段）：**
"""

        for i, item in enumerate(segment, 1):
            prompt += f"""
**问题 {i}：**
{item['question']}

**回答 {i}：**
{item['answer']}

---
"""

        prompt += """
**请返回严格的JSON格式：**
```json
{
  "success": true,
  "segment_number": """ + str(segment_number) + """,
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

    def analyze_segment_with_model(self, model_name: str, segment: List[Dict], segment_number: int, total_segments: int) -> Dict:
        """使用指定模型分析单个分段"""
        prompt = self.create_5segment_prompt(segment, segment_number, total_segments)

        success, response, processing_time = self.execute_ollama_command(model_name, prompt)

        if not success:
            return {
                'success': False,
                'model': model_name,
                'segment_number': segment_number,
                'error': response,
                'processing_time': processing_time
            }

        # 解析JSON响应
        parse_result = self.parse_json_response(response)

        if not parse_result['success']:
            return {
                'success': False,
                'model': model_name,
                'segment_number': segment_number,
                'error': f"JSON解析失败: {parse_result['error']}",
                'raw_response': response[:500] if response else '',
                'processing_time': processing_time
            }

        # 验证评分标准
        data = parse_result['data']
        if 'scores' in data:
            invalid_scores = []
            for trait, score in data['scores'].items():
                if score not in [1, 3, 5]:
                    invalid_scores.append(f"{trait}:{score}")
                    # 修正无效评分
                    if score < 2:
                        data['scores'][trait] = 1
                    elif score > 4:
                        data['scores'][trait] = 5
                    else:
                        data['scores'][trait] = 3

            if invalid_scores:
                print(f"      ⚠️ {model_name} 修正无效评分: {invalid_scores}")

        result = {
            'success': True,
            'model': model_name,
            'segment_number': segment_number,
            'data': data,
            'parsing_method': parse_result['method'],
            'processing_time': processing_time
        }

        return result

    def calculate_mbti_type(self, scores: Dict) -> str:
        """根据Big5评分计算MBTI类型"""
        try:
            openness = scores.get('openness_to_experience', 3)
            conscientiousness = scores.get('conscientiousness', 3)
            extraversion = scores.get('extraversion', 3)
            agreeableness = scores.get('agreeableness', 3)
            neuroticism = scores.get('neuroticism', 3)

            # I/E维度
            I_E = 'I' if extraversion <= 3 else 'E'

            # S/N维度
            S_N = 'N' if openness >= 4 else 'S'

            # T/F维度
            T_F = 'F' if agreeableness >= 4 else 'T'

            # J/P维度
            J_P = 'J' if conscientiousness >= 4 else 'P'

            return f"{I_E}{S_N}{T_F}{J_P}"
        except Exception:
            return "UNKNOWN"

    def extract_questions_from_file(self, file_path: str) -> List[Dict]:
        """从评估文件中提取问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            questions = []
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for item in data['assessment_results']:
                    if isinstance(item, dict) and 'question_data' in item:
                        question_data = item['question_data']
                        if isinstance(question_data, dict):
                            question_text = question_data.get('prompt_for_agent', question_data.get('mapped_ipip_concept', ''))

                            answer_text = ''
                            if 'extracted_response' in item and item['extracted_response']:
                                answer_text = item['extracted_response']
                            elif 'conversation_log' in item and isinstance(item['conversation_log'], list):
                                for msg in item['conversation_log']:
                                    if isinstance(msg, dict) and msg.get('role') == 'assistant':
                                        answer_text = msg.get('content', '')
                                        break

                            if question_text and answer_text:
                                questions.append({
                                    'question': question_text,
                                    'answer': answer_text
                                })

            return questions

        except Exception as e:
            print(f"  ❌ 提取问题失败: {e}")
            return []

    def calculate_three_model_consistency(self, model_results: Dict) -> Dict:
        """计算三个模型间的一致性作为可信度"""
        if len(model_results) < 2:
            return {"error": "需要至少2个模型结果进行一致性分析"}

        # 收集MBTI类型
        mbti_types = []
        scores_data = {}

        for model, results in model_results.items():
            if 'mbti_type' in results and results['mbti_type'] != 'UNKNOWN':
                mbti_types.append(results['mbti_type'])

            if 'final_scores' in results:
                for trait, score in results['final_scores'].items():
                    if trait not in scores_data:
                        scores_data[trait] = []
                    scores_data[trait].append(score)

        # 计算MBTI一致性
        mbti_consensus = "UNKNOWN"
        high_confidence_consensus = False

        if mbti_types:
            mbti_counts = Counter(mbti_types)
            most_common_mbti, count = mbti_counts.most_common(1)

            if count == len(mbti_types):  # 所有模型一致
                mbti_consensus = most_common_mbti
                high_confidence_consensus = True
            elif count >= 2:  # 多数模型一致
                mbti_consensus = most_common_mbti
                high_confidence_consensus = False

        # 计算评分一致性
        trait_consistency = {}
        total_consistency_score = 0

        for trait, scores in scores_data.items():
            if len(scores) >= 2:
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                mean_score = statistics.mean(scores)

                # 一致性评分：标准差越小，一致性越高
                if std_dev == 0:
                    consistency_score = 100  # 完全一致
                    consistency_level = "完美"
                elif std_dev <= 0.5:
                    consistency_score = 90  # 高度一致
                    consistency_level = "高"
                elif std_dev <= 1.0:
                    consistency_score = 70  # 中等一致
                    consistency_level = "中"
                elif std_dev <= 1.5:
                    consistency_score = 40  # 低度一致
                    consistency_level = "低"
                else:
                    consistency_score = 10  # 不一致
                    consistency_level = "极低"

                trait_consistency[trait] = {
                    "mean_score": mean_score,
                    "std_deviation": std_dev,
                    "consistency_level": consistency_level,
                    "consistency_score": consistency_score,
                    "scores": scores
                }

                total_consistency_score += consistency_score

        # 计算总体可信度
        if trait_consistency:
            average_consistency_score = total_consistency_score / len(trait_consistency)

            if average_consistency_score >= 85:
                overall_confidence = "高"
                confidence_score = min(100, average_consistency_score)
            elif average_consistency_score >= 60:
                overall_confidence = "中"
                confidence_score = average_consistency_score
            else:
                overall_confidence = "低"
                confidence_score = average_consistency_score
        else:
            overall_confidence = "极低"
            confidence_score = 0

        return {
            "consensus_mbti": mbti_consensus,
            "high_confidence_consensus": high_confidence_consensus,
            "mbti_distribution": dict(Counter(mbti_types)) if mbti_types else {},
            "trait_consistency": trait_consistency,
            "overall_confidence": overall_confidence,
            "confidence_score": round(confidence_score, 1),
            "models_analyzed": len(model_results),
            "analysis_timestamp": datetime.now().isoformat()
        }

    def analyze_file_with_enhanced_features(self, file_path: str, output_dir: str) -> Dict:
        """使用增强功能分析单个文件"""
        print(f"📈 开始增强分析: {Path(file_path).name}")

        try:
            # 提取问题
            questions = self.extract_questions_from_file(file_path)

            if len(questions) < 5:
                raise Exception(f"问题数量不足：{len(questions)}")

            # 分段处理（每段5题，取前50题）
            segment_size = 5
            questions_to_process = questions[:50]  # 取前50题
            segments = []

            for i in range(0, len(questions_to_process), segment_size):
                segment = questions_to_process[i:i+segment_size]
                if len(segment) == segment_size:
                    segments.append(segment)

            total_segments = len(segments)
            print(f"  📊 {len(questions)}题 -> {total_segments}段 (每段5题)")

            # 三模型并发分析
            model_analysis_results = {}
            total_start_time = time.time()

            # 降低并发数以提高稳定性
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_to_model = {}

                for model in self.models:
                    model_name = model["name"]
                    print(f"  🌐 启动模型: {model_name}")

                    # 为该模型的所有分段创建任务
                    model_futures = []
                    for i, segment in enumerate(segments, 1):
                        future = executor.submit(
                            self.analyze_segment_with_model,
                            model_name,
                            segment,
                            i,
                            total_segments
                        )
                        model_futures.append(future)

                    future_to_model[model_name] = model_futures

                # 收集结果
                for model_name, futures in future_to_model.items():
                    print(f"  🔍 收集 {model_name} 结果...")

                    segment_results = []
                    successful_segments = 0
                    total_model_time = 0

                    for future in futures:
                        try:
                            result = future.result(timeout=300)
                            segment_results.append(result)

                            if result['success']:
                                successful_segments += 1
                                print(f"      ✅ 段{result['segment_number']}: {list(result['data']['scores'].values())} ({result.get('processing_time', 0):.1f}s)")
                                self.stats['successful_segments'] += 1
                            else:
                                print(f"      ❌ 段{result['segment_number']}: {result.get('error', 'Unknown error')}")

                            total_model_time += result.get('processing_time', 0)
                            self.stats['total_segments'] += 1

                        except Exception as e:
                            print(f"      ⚠️ 段处理异常: {e}")

                    # 计算该模型的最终评分
                    if segment_results:
                        final_scores = {}
                        for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                            all_scores = []
                            for result in segment_results:
                                if result['success'] and 'data' in result and 'scores' in result['data']:
                                    all_scores.append(result['data']['scores'][trait])

                            if all_scores:
                                final_scores[trait] = int(statistics.median(all_scores))

                        # 生成MBTI类型
                        mbti_type = self.calculate_mbti_type(final_scores)

                        model_analysis_results[model_name] = {
                            "segment_results": segment_results,
                            "final_scores": final_scores,
                            "mbti_type": mbti_type,
                            "successful_segments": successful_segments,
                            "total_segments": total_segments,
                            "success_rate": successful_segments / total_segments,
                            "total_processing_time": total_model_time,
                            "average_time_per_segment": total_model_time / total_segments if total_segments > 0 else 0
                        }

            total_time = time.time() - total_start_time

            # 计算三模型一致性（可信度验证）
            consistency_analysis = self.calculate_three_model_consistency(model_analysis_results)

            # 更新统计信息
            confidence_level = consistency_analysis.get('overall_confidence', '极低')
            if confidence_level == '高':
                self.stats['high_confidence_files'] += 1
            elif confidence_level == '中':
                self.stats['medium_confidence_files'] += 1
            else:
                self.stats['low_confidence_files'] += 1

            # 创建增强分析结果
            analysis_result = {
                "file_info": {
                    "filename": Path(file_path).name,
                    "total_questions": len(questions),
                    "segments_analyzed": total_segments,
                    "questions_per_segment": segment_size,
                    "analysis_date": datetime.now().isoformat(),
                    "analysis_method": "5题分段，三模型独立评估 + 90%质量阈值控制"
                },
                "models_used": [{"name": m["name"], "description": m["description"]} for m in self.models],
                "model_results": model_analysis_results,
                "consistency_analysis": consistency_analysis,
                "performance_metrics": {
                    "total_processing_time": total_time,
                    "models_count": len(model_analysis_results),
                    "average_time_per_model": sum(r.get('total_processing_time', 0) for r in model_analysis_results.values()) / len(model_analysis_results) if model_analysis_results else 0
                },
                "summary": {
                    "successful_models": len([r for r in model_analysis_results.values() if r.get('success_rate', 0) > 0]),
                    "average_success_rate": sum(r.get('success_rate', 0) for r in model_analysis_results.values()) / len(model_analysis_results) if model_analysis_results else 0,
                    "consensus_mbti": consistency_analysis.get('consensus_mbti', 'UNKNOWN'),
                    "confidence_score": consistency_analysis.get('confidence_score', 0),
                    "overall_confidence": consistency_analysis.get('overall_confidence', '极低')
                }
            }

            # 应用质量控制
            analysis_result = self.enhance_result_with_quality_control(analysis_result)

            # 保存结果
            output_filename = f"{Path(file_path).stem}_enhanced_analysis.json"
            output_path = os.path.join(output_dir, output_filename)

            # 使用增强文件处理器保存
            save_success = self.file_handler.save_json(analysis_result, output_path, backup=True)

            if save_success:
                print(f"  💾 结果已保存: {output_filename}")
            else:
                print(f"  ❌ 结果保存失败: {output_filename}")

            # 显示简要结果
            print(f"  📋 分析结果摘要:")
            for model, results in model_analysis_results.items():
                print(f"    {model}: {results['final_scores']} -> {results['mbti_type']} ({results['successful_segments']}/{results['total_segments']}段成功)")

            print(f"  🎯 一致性分析: {consistency_analysis.get('consensus_mbti', 'UNKNOWN')}")
            print(f"  📊 可信度: {consistency_analysis.get('overall_confidence', '极低')} ({consistency_analysis.get('confidence_score', 0)}分)")

            # 显示质量控制结果
            if 'quality_assessment' in analysis_result:
                qa = analysis_result['quality_assessment']
                print(f"  🔍 质量控制:")
                print(f"     成功率: {qa['average_success_rate']:.1%}")
                print(f"     质量分数: {qa['quality_score']}")
                print(f"     质量等级: {qa['quality_level']}")
                print(f"     {'✅' if qa['meets_90_percent_threshold'] else '❌'} 90%阈值: {'通过' if qa['meets_90_percent_threshold'] else '未通过'}")

                if qa['recommendations']:
                    print(f"     ⚠️ 建议:")
                    for rec in qa['recommendations']:
                        print(f"        - {rec}")

            return {
                'success': True,
                'file_path': file_path,
                'output_path': output_path,
                'model_results': model_analysis_results,
                'consistency_analysis': consistency_analysis,
                'total_time': total_time
            }

        except Exception as e:
            print(f"  ❌ 文件分析失败: {e}")
            self.stats['failed_files'] += 1
            self._record_error(str(e))
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def check_data_quality(self, model_results: Dict) -> Tuple[bool, float]:
        """检查数据质量是否达到90%阈值"""
        if not model_results:
            return False, 0.0

        success_rates = []
        for model_name, result in model_results.items():
            if 'success_rate' in result:
                success_rates.append(result['success_rate'])

        if not success_rates:
            return False, 0.0

        avg_success_rate = sum(success_rates) / len(success_rates)
        meets_threshold = avg_success_rate >= self.min_success_rate

        return meets_threshold, avg_success_rate

    def calculate_quality_score(self, success_rate: float, consistency_score: float = 0) -> float:
        """计算质量分数 (成功率70% + 一致性30%)"""
        quality_score = (success_rate * 70) + (consistency_score * 0.3)
        return round(quality_score, 1)

    def enhance_result_with_quality_control(self, result: Dict) -> Dict:
        """为结果添加质量控制信息"""
        if 'model_results' not in result:
            return result

        # 检查数据质量
        meets_threshold, success_rate = self.check_data_quality(result['model_results'])

        # 获取一致性分数
        consistency_score = result.get('consistency_analysis', {}).get('confidence_score', 0)

        # 计算质量分数
        quality_score = self.calculate_quality_score(success_rate, consistency_score)

        # 确定质量等级
        if success_rate >= 0.95:
            quality_level = 'high'
        elif success_rate >= self.min_success_rate:  # 90%
            quality_level = 'medium'
        else:
            quality_level = 'low'

        # 创建质量评估
        quality_assessment = {
            'meets_90_percent_threshold': meets_threshold,
            'average_success_rate': success_rate,
            'quality_score': quality_score,
            'quality_level': quality_level,
            'consistency_score': consistency_score,
            'quality_threshold': self.min_success_rate,
            'recommendations': []
        }

        # 生成建议
        if not meets_threshold:
            quality_assessment['recommendations'].append(f"成功率{success_rate:.1%}低于90%阈值，结果不可信")
        if success_rate < 0.7:
            quality_assessment['recommendations'].append("成功率过低，建议重新评估")
        if consistency_score < 50:
            quality_assessment['recommendations'].append("模型一致性不足")

        # 更新质量统计
        self.quality_stats['total_evaluated'] += 1
        self.quality_stats['average_success_rate'] = (
            (self.quality_stats['average_success_rate'] * (self.quality_stats['total_evaluated'] - 1) + success_rate) /
            self.quality_stats['total_evaluated']
        )

        if meets_threshold:
            self.quality_stats['passed_quality_threshold'] += 1
        else:
            self.quality_stats['failed_quality_threshold'] += 1

        # 添加质量信息到结果
        result['quality_assessment'] = quality_assessment
        result['meets_minimum_quality'] = meets_threshold
        result['quality_score'] = quality_score

        return result

    def _record_error(self, error_message: str):
        """记录错误统计"""
        error_type = type(error_message).__name__
        if error_type not in self.stats['error_summary']:
            self.stats['error_summary'][error_type] = 0
        self.stats['error_summary'][error_type] += 1

    def batch_analyze(self, input_dir: str, output_dir: str = "enhanced_results", max_files: int = 5):
        """批量分析多个文件 - 限制文件数量以提高稳定性"""
        print("🚀 增强评估器")
        print("=" * 80)
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {', '.join([m['name'] for m in self.models])}")
        print(f"📊 分段方式: 5题分段")
        print(f"🎯 可信度验证: 三模型一致性分析 + 90%质量阈值")
        print(f"⚡ 稳定性优化: 降低并发数，增强错误处理")
        print()

        # 检查模型可用性
        availability = self.check_ollama_availability()
        available_models = [name for name, available in availability.items() if available]

        if len(available_models) < 3:
            print(f"❌ 可用模型不足3个 ({len(available_models)}/3)")
            print("请确保所有三个模型都已下载到Ollama")
            return

        print(f"✅ 所有3个模型都可用")
        print()

        self.stats['processing_start'] = datetime.now()

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 查找输入文件
        input_path = Path(input_dir)
        if input_path.is_file():
            files = [input_path]
        elif input_path.is_dir():
            files = list(input_path.glob("*.json"))
        else:
            print(f"❌ 输入路径不存在: {input_dir}")
            return

        # 限制文件数量以提高稳定性
        if max_files:
            files = files[:max_files]
        else:
            files = files[:10]  # 默认最多处理10个文件

        self.stats['total_files'] = len(files)
        print(f"📊 找到 {len(files)} 个文件 (为稳定性限制为{max_files or '全部'})")

        if not files:
            print("❌ 未找到符合条件的文件")
            return

        # 批量处理
        batch_results = []

        for i, file_path in enumerate(files, 1):
            print(f"📈 [{i}/{len(files)}] 处理: {file_path.name}")

            result = self.analyze_file_with_enhanced_features(str(file_path), output_dir)
            batch_results.append(result)

            if result['success']:
                self.stats['processed_files'] += 1
            else:
                self.stats['failed_files'] += 1

            # 显示进度
            successful = len([r for r in batch_results if r.get('success', False)])
            print(f"   进度: {successful}/{len(batch_results)} 成功")
            print()

        # 完成统计
        self.stats['processing_end'] = datetime.now()
        if self.stats['processing_start'] and self.stats['processing_end']:
            processing_time = (self.stats['processing_end'] - self.stats['processing_start']).total_seconds()
        else:
            processing_time = 0

        print("📊 批量处理完成")
        print("=" * 80)
        print(f"📁 总文件数: {self.stats['total_files']}")
        print(f"✅ 处理成功: {self.stats['processed_files']}")
        print(f"❌ 处理失败: {self.stats['failed_files']}")
        print(f"📊 总分段数: {self.stats['total_segments']}")
        print(f"✅ 成功分段: {self.stats['successful_segments']}")
        print(f"📈 成功率: {self.stats['successful_segments']/max(1, self.stats['total_segments'])*100:.1f}%")
        print()
        print(f"🎯 可信度分布:")
        print(f"   高可信度: {self.stats['high_confidence_files']} 个文件")
        print(f"   中可信度: {self.stats['medium_confidence_files']} 个文件")
        print(f"   低可信度: {self.stats['low_confidence_files']} 个文件")
        print()
        print(f"🔍 质量控制统计 (90%阈值):")
        print(f"   总评估数: {self.quality_stats['total_evaluated']}")
        print(f"   ✅ 通过质量阈值: {self.quality_stats['passed_quality_threshold']}")
        print(f"   ❌ 未通过质量阈值: {self.quality_stats['failed_quality_threshold']}")
        print(f"   平均成功率: {self.quality_stats['average_success_rate']:.1%}")

        if self.quality_stats['total_evaluated'] > 0:
            quality_pass_rate = self.quality_stats['passed_quality_threshold'] / self.quality_stats['total_evaluated'] * 100
            print(f"   质量通过率: {quality_pass_rate:.1f}%")
        print(f"⏱️ 处理时间: {processing_time:.1f}秒")

        # 保存批量处理报告
        batch_report = {
            "batch_info": {
                "models_used": [{"name": m["name"], "description": m["description"]} for m in self.models],
                "segment_size": 5,
                "processing_date": datetime.now().isoformat(),
                "processing_time": processing_time,
                "analysis_method": "5题分段，三模型独立评估 + 90%质量阈值控制 + 增强稳定性"
            },
            "input_files": [str(f) for f in files],
            "results": batch_results,
            "statistics": self.stats,
            "quality_control": {
                "min_success_rate_threshold": self.min_success_rate,
                "quality_stats": self.quality_stats,
                "quality_pass_rate": (self.quality_stats['passed_quality_threshold'] / max(1, self.quality_stats['total_evaluated']) * 100)
            },
            "summary": {
                "total_files": self.stats['total_files'],
                "successful_files": self.stats['processed_files'],
                "failed_files": self.stats['failed_files'],
                "success_rate": self.stats['processed_files']/max(1, self.stats['total_files'])*100,
                "high_confidence_files": self.stats['high_confidence_files'],
                "medium_confidence_files": self.stats['medium_confidence_files'],
                "low_confidence_files": self.stats['low_confidence_files'],
                "average_confidence_score": sum(r.get('consistency_analysis', {}).get('confidence_score', 0) for r in batch_results if r.get('success')) / max(1, len([r for r in batch_results if r.get('success')])),
                "quality_threshold_passed": self.quality_stats['passed_quality_threshold'],
                "quality_threshold_failed": self.quality_stats['failed_quality_threshold'],
                "average_success_rate": self.quality_stats['average_success_rate']
            }
        }

        # 使用增强文件处理器保存批量报告
        batch_report_path = os.path.join(output_dir, "enhanced_batch_report.json")
        save_success = self.file_handler.save_json(batch_report, batch_report_path, backup=True)

        if save_success:
            print(f"📄 批量报告已保存: enhanced_batch_report.json")

        print(f"\n✅ 增强批量分析完成!")
        print(f"🎯 关键改进:")
        print(f"   ✅ 修复JSON序列化错误")
        print(f"   ✅ 增强错误处理机制")
        print(f"   ✅ 降低并发提高稳定性")
        print(f"   ✅ 90%质量控制阈值")
        print(f"   ✅ 智能重试和降级")

        return batch_report

def main():
    """主函数"""
    evaluator = EnhancedEvaluator()

    # 输入输出目录
    input_dir = "results/results"  # 可根据实际情况修改
    output_dir = "enhanced_results"

    # 批量分析 - 限制文件数量以提高稳定性
    evaluator.batch_analyze(input_dir, output_dir, max_files=5)  # 限制为5个文件

if __name__ == "__main__":
    main()