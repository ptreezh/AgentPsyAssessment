#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云模型5题分段评估器 - OpenRouter版本
使用指定的云模型进行5题分段评估，动态增加模型以提高一致性
评分策略：剔除最高分和最低分后计算均分
"""

import sys
import os
import json
import time
import requests
import re
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import Counter
import concurrent.futures
from dotenv import load_dotenv

# 导入弹性JSON序列化器
from resilient_json_serializer import safe_json_dumps, safe_json_loads

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 加载.env文件
load_dotenv()

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class CloudModelSegmentEvaluator:
    def __init__(self):
        """初始化云模型分段评估器"""
        # 读取OpenRouter配置
        self.read_openrouter_config()

        # 主要三个模型
        self.primary_models = [
            {
                "name": "alibaba/tongyi-deepresearch-30b-a3b",
                "description": "Tongyi DeepResearch 30B A3B"
            },
            {
                "name": "deepseek/deepseek-chat-v3.1",
                "description": "DeepSeek Chat V3.1"
            },
            {
                "name": "openai/gpt-oss-20b",
                "description": "OpenAI GPT-OSS 20B"
            }
        ]

        # 备用模型（分歧大时使用）
        self.backup_models = [
            {
                "name": "moonshotai/kimi-k2",
                "description": "Moonshot Kimi K2"
            },
            {
                "name": "google/gemma-3-27b-it",
                "description": "Google Gemma 3 27B"
            }
        ]

        # 统计信息
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
            'processing_end': None
        }

    def read_openrouter_config(self):
        """从.env文件读取OpenRouter配置"""
        try:
            self.api_key = os.getenv('OPENROUTER_API_KEY')
            self.base_url = os.getenv('OPENROUTER_BASE_URL')

            if self.api_key and self.base_url:
                print(f"✅ 已从.env读取OpenRouter配置: {self.base_url}")
            else:
                print(f"❌ .env文件中缺少OpenRouter配置")
                self.api_key = None
                self.base_url = None

        except Exception as e:
            print(f"❌ 读取.env配置失败: {e}")
            self.api_key = None
            self.base_url = None

    def create_api_headers(self) -> Dict:
        """创建API请求头"""
        return {
            "HTTP-Referer": "https://localhost",
            "X-Title": "Portable PsyAgent Evaluator",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def call_cloud_model(self, model_name: str, prompt: str, timeout: int = 120) -> Tuple[bool, str, float]:
        """调用云模型API"""
        if not self.api_key or not self.base_url:
            return False, "API配置缺失", 0

        try:
            url = f"{self.base_url}/chat/completions"

            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"}
            }

            headers = self.create_api_headers()
            start_time = time.time()

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout
            )

            end_time = time.time()
            processing_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    return True, content, processing_time
                else:
                    return False, "响应格式错误", processing_time
            else:
                error_msg = f"API错误 ({response.status_code}): {response.text}"
                return False, error_msg, processing_time

        except requests.exceptions.Timeout:
            return False, "请求超时", timeout
        except Exception as e:
            return False, f"请求异常: {str(e)}", 0

    def parse_json_response(self, response_text: str) -> Dict:
        """多策略JSON解析器"""
        if not response_text:
            return {"success": False, "error": "响应为空"}

        # 解析策略
        strategies = [
            ("直接解析", self.direct_json_parse),
            ("代码块提取", self.extract_json_from_codeblock),
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
            return safe_json_loads(text)
        return None

    def extract_json_from_codeblock(self, text: str) -> Optional[Dict]:
        """从代码块提取JSON"""
        patterns = [
            r'```json\s*\n?(\{.*?\})\s*```',
            r'```\s*\n?(\{.*?\})\s*```',
            r'`(\{.*?\})`'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return safe_json_loads(match.strip())
                except:
                    continue
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
                    return safe_json_loads(match)
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

            return safe_json_loads(text)
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
                if not isinstance(score, int) or score not in [1, 2, 3, 4, 5]:
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
- **2分**：低表现 - 倾向缺乏该特质
- **3分**：中等表现 - 平衡或不确定，有该特质也有反例
- **4分**：高表现 - 明显具备该特质
- **5分**：极高表现 - 强烈具备该特质

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
    "openness_to_experience": 1或2或3或4或5,
    "conscientiousness": 1或2或3或4或5,
    "extraversion": 1或2或3或4或5,
    "agreeableness": 1或2或3或4或5,
    "neuroticism": 1或2或3或4或5
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

**再次提醒：每个评分必须是1-5的整数！**
"""

        return prompt

    def analyze_segment_with_model(self, model_name: str, segment: List[Dict], segment_number: int, total_segments: int) -> Dict:
        """使用指定模型分析单个分段"""
        prompt = self.create_5segment_prompt(segment, segment_number, total_segments)

        success, response, processing_time = self.call_cloud_model(model_name, prompt)

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
                if score not in [1, 2, 3, 4, 5]:
                    invalid_scores.append(f"{trait}:{score}")
                    # 修正无效评分到最近的有效值
                    if score < 1:
                        data['scores'][trait] = 1
                    elif score > 5:
                        data['scores'][trait] = 5

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

    def calculate_trimmed_mean_scores(self, all_model_results: List[Dict]) -> Dict:
        """计算剔除最高分和最低分后的均分"""
        if not all_model_results:
            return {}

        # 收集所有模型对每个特质的评分
        trait_scores = {}
        for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            scores = []
            for result in all_model_results:
                if result['success'] and 'data' in result and 'scores' in result['data']:
                    score = result['data']['scores'].get(trait)
                    if score is not None:
                        scores.append(score)

            if scores:
                trait_scores[trait] = scores

        # 计算剔除最高分和最低分后的均分
        final_scores = {}
        for trait, scores in trait_scores.items():
            if len(scores) >= 3:
                # 剔除最高分和最低分
                scores_sorted = sorted(scores)
                trimmed_scores = scores_sorted[1:-1]  # 去掉第一个和最后一个
                final_scores[trait] = int(statistics.mean(trimmed_scores))
            elif len(scores) >= 2:
                # 如果只有2个评分，取平均值
                final_scores[trait] = int(statistics.mean(scores))
            elif len(scores) == 1:
                # 如果只有1个评分，直接使用
                final_scores[trait] = scores[0]

        return final_scores

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

    def check_model_divergence(self, model_results: List[Dict]) -> Dict:
        """检查模型间的分歧程度"""
        if len(model_results) < 2:
            return {"divergence_level": "low", "need_backup": False}

        # 计算每个特质的标准差
        trait_std_devs = []
        for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            scores = []
            for result in model_results:
                if result['success'] and 'data' in result and 'scores' in result['data']:
                    score = result['data']['scores'].get(trait)
                    if score is not None:
                        scores.append(score)

            if len(scores) >= 2:
                std_dev = statistics.stdev(scores)
                trait_std_devs.append(std_dev)

        if trait_std_devs:
            avg_std_dev = statistics.mean(trait_std_devs)

            # 判断分歧程度
            if avg_std_dev >= 1.5:
                return {"divergence_level": "high", "need_backup": True, "avg_std_dev": avg_std_dev}
            elif avg_std_dev >= 1.0:
                return {"divergence_level": "medium", "need_backup": False, "avg_std_dev": avg_std_dev}
            else:
                return {"divergence_level": "low", "need_backup": False, "avg_std_dev": avg_std_dev}

        return {"divergence_level": "unknown", "need_backup": False}

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

    def analyze_file_with_cloud_models(self, file_path: str, output_dir: str) -> Dict:
        """使用云模型分析单个文件"""
        print(f"📈 开始云模型分段分析: {Path(file_path).name}")

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

            # 分析所有分段
            all_segment_results = []
            total_start_time = time.time()

            for i, segment in enumerate(segments, 1):
                print(f"  🔍 分析第{i}/{total_segments}段...")

                # 先用主要三个模型分析
                primary_results = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_model = {}

                    for model in self.primary_models:
                        model_name = model["name"]
                        print(f"    🌐 调用模型: {model_name}")

                        future = executor.submit(
                            self.analyze_segment_with_model,
                            model_name,
                            segment,
                            i,
                            total_segments
                        )
                        future_to_model[future] = model_name

                    # 收集主要模型结果
                    for future in concurrent.futures.as_completed(future_to_model, timeout=300):
                        model_name = future_to_model[future]
                        try:
                            result = future.result()
                            primary_results.append(result)

                            if result['success']:
                                scores = result['data']['scores']
                                print(f"      ✅ {model_name}: {list(scores.values())} ({result.get('processing_time', 0):.1f}s)")
                            else:
                                print(f"      ❌ {model_name}: {result.get('error', 'Unknown error')}")

                        except Exception as e:
                            print(f"      ⚠️ {model_name}: 处理异常 - {e}")

                # 检查分歧程度
                successful_primary = [r for r in primary_results if r['success']]
                divergence_info = self.check_model_divergence(successful_primary)

                all_results_for_segment = successful_primary.copy()

                # 如果分歧太大，添加备用模型
                if divergence_info['need_backup'] and len(successful_primary) >= 2:
                    print(f"    🔄 分歧较大(标准差={divergence_info['avg_std_dev']:.2f})，添加备用模型...")

                    backup_results = []
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        future_to_model = {}

                        for model in self.backup_models:
                            model_name = model["name"]
                            print(f"    🌐 调用备用模型: {model_name}")

                            future = executor.submit(
                                self.analyze_segment_with_model,
                                model_name,
                                segment,
                                i,
                                total_segments
                            )
                            future_to_model[future] = model_name

                        # 收集备用模型结果
                        for future in concurrent.futures.as_completed(future_to_model, timeout=300):
                            model_name = future_to_model[future]
                            try:
                                result = future.result()
                                backup_results.append(result)

                                if result['success']:
                                    scores = result['data']['scores']
                                    print(f"      ✅ {model_name}: {list(scores.values())} ({result.get('processing_time', 0):.1f}s)")
                                else:
                                    print(f"      ❌ {model_name}: {result.get('error', 'Unknown error')}")

                            except Exception as e:
                                print(f"      ⚠️ {model_name}: 处理异常 - {e}")

                    # 添加成功的备用模型结果
                    successful_backup = [r for r in backup_results if r['success']]
                    all_results_for_segment.extend(successful_backup)

                # 计算剔除最高最低分后的均分
                if len(all_results_for_segment) >= 2:
                    final_scores = self.calculate_trimmed_mean_scores(all_results_for_segment)
                    print(f"      📊 最终评分(剔除极值): {list(final_scores.values())}")
                else:
                    # 如果只有一个成功结果，直接使用
                    if all_results_for_segment:
                        final_scores = all_results_for_segment[0]['data']['scores']
                        print(f"      📊 使用单一模型评分: {list(final_scores.values())}")
                    else:
                        final_scores = {}
                        print(f"      ❌ 该段无有效评分")

                # 生成分段结果
                segment_result = {
                    'segment_number': i,
                    'primary_results': primary_results,
                    'backup_results': backup_results if 'backup_results' in locals() else [],
                    'divergence_info': divergence_info,
                    'all_successful_results': all_results_for_segment,
                    'final_scores': final_scores,
                    'models_used': len(all_results_for_segment)
                }

                all_segment_results.append(segment_result)
                self.stats['successful_segments'] += 1
                self.stats['total_segments'] += 1

            # 计算文件总体评分
            if all_segment_results:
                # 聚合所有分段的最终评分
                file_final_scores = {}
                for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    all_scores = []
                    for segment_result in all_segment_results:
                        if segment_result['final_scores'] and trait in segment_result['final_scores']:
                            all_scores.append(segment_result['final_scores'][trait])

                    if all_scores:
                        file_final_scores[trait] = int(statistics.median(all_scores))

                # 生成MBTI类型
                mbti_type = self.calculate_mbti_type(file_final_scores)

                # 计算一致性指标
                avg_models_per_segment = sum(r['models_used'] for r in all_segment_results) / len(all_segment_results)
                segments_with_backup = sum(1 for r in all_segment_results if r['divergence_info']['need_backup'])

                total_time = time.time() - total_start_time

                # 保存结果
                output_filename = f"{Path(file_path).stem}_cloud_segment_analysis.json"
                output_path = os.path.join(output_dir, output_filename)

                analysis_result = {
                    "file_info": {
                        "filename": Path(file_path).name,
                        "total_questions": len(questions),
                        "segments_analyzed": total_segments,
                        "questions_per_segment": segment_size,
                        "analysis_date": datetime.now().isoformat(),
                        "analysis_method": "5题分段，云模型评估，剔除极值均分"
                    },
                    "models_config": {
                        "primary_models": [{"name": m["name"], "description": m["description"]} for m in self.primary_models],
                        "backup_models": [{"name": m["name"], "description": m["description"]} for m in self.backup_models]
                    },
                    "segment_results": all_segment_results,
                    "file_summary": {
                        "final_scores": file_final_scores,
                        "mbti_type": mbti_type,
                        "total_segments": total_segments,
                        "successful_segments": len(all_segment_results),
                        "avg_models_per_segment": round(avg_models_per_segment, 1),
                        "segments_needed_backup": segments_with_backup,
                        "backup_usage_rate": round(segments_with_backup / total_segments * 100, 1) if total_segments > 0 else 0
                    },
                    "performance_metrics": {
                        "total_processing_time": total_time,
                        "avg_time_per_segment": total_time / total_segments if total_segments > 0 else 0
                    }
                }

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(safe_json_dumps(analysis_result, indent=2))

                print(f"  💾 结果已保存: {output_filename}")
                print(f"  📋 分析结果摘要:")
                print(f"    最终评分: {file_final_scores}")
                print(f"    MBTI类型: {mbti_type}")
                print(f"    平均使用模型数: {avg_models_per_segment:.1f}")
                print(f"    备用模型使用率: {segments_with_backup/total_segments*100:.1f}%")

                return {
                    'success': True,
                    'file_path': file_path,
                    'output_path': output_path,
                    'final_scores': file_final_scores,
                    'mbti_type': mbti_type,
                    'total_segments': total_segments,
                    'successful_segments': len(all_segment_results),
                    'avg_models_per_segment': avg_models_per_segment,
                    'backup_usage_rate': segments_with_backup / total_segments if total_segments > 0 else 0,
                    'total_time': total_time
                }

            else:
                raise Exception("没有成功的分段分析结果")

        except Exception as e:
            print(f"  ❌ 文件分析失败: {e}")
            self.stats['failed_files'] += 1
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def batch_analyze(self, input_dir: str, output_dir: str = "cloud_segment_results", max_files: int = None):
        """批量分析多个文件"""
        print("🚀 云模型5题分段评估器")
        print("=" * 50)
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 主要模型: {', '.join([m['name'] for m in self.primary_models])}")
        print(f"🔄 备用模型: {', '.join([m['name'] for m in self.backup_models])}")
        print(f"📊 分段方式: 5题分段")
        print(f"📈 评分策略: 剔除最高分和最低分后计算均分")
        print(f"🎯 分分歧检测: 自动增加备用模型")
        print()

        # 检查配置
        if not self.api_key or not self.base_url:
            print("❌ OpenRouter配置缺失，请检查openrouter.txt文件")
            return

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

        if max_files:
            files = files[:max_files]

        self.stats['total_files'] = len(files)
        print(f"📊 找到 {len(files)} 个文件")

        if not files:
            print("❌ 未找到符合条件的文件")
            return

        # 批量处理
        batch_results = []

        for i, file_path in enumerate(files, 1):
            print(f"📈 [{i}/{len(files)}] 处理: {file_path.name}")

            result = self.analyze_file_with_cloud_models(str(file_path), output_dir)
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
        print("=" * 50)
        print(f"📁 总文件数: {self.stats['total_files']}")
        print(f"✅ 处理成功: {self.stats['processed_files']}")
        print(f"❌ 处理失败: {self.stats['failed_files']}")
        print(f"📊 总分段数: {self.stats['total_segments']}")
        print(f"✅ 成功分段: {self.stats['successful_segments']}")
        print(f"📈 成功率: {self.stats['successful_segments']/max(1, self.stats['total_segments'])*100:.1f}%")
        print(f"⏱️ 处理时间: {processing_time:.1f}秒")

        # 准备统计数据（转换datetime对象为ISO字符串）
        safe_stats = self.stats.copy()
        if safe_stats.get('processing_start'):
            safe_stats['processing_start'] = safe_stats['processing_start'].isoformat()
        if safe_stats.get('processing_end'):
            safe_stats['processing_end'] = safe_stats['processing_end'].isoformat()

        # 保存批量处理报告
        batch_report = {
            "batch_info": {
                "primary_models": [{"name": m["name"], "description": m["description"]} for m in self.primary_models],
                "backup_models": [{"name": m["name"], "description": m["description"]} for m in self.backup_models],
                "segment_size": 5,
                "scoring_strategy": "trimmed_mean_remove_extremes",
                "processing_date": datetime.now().isoformat(),
                "processing_time": processing_time,
                "analysis_method": "5题分段，云模型评估，分歧检测，剔除极值均分"
            },
            "input_files": [str(f) for f in files],
            "results": batch_results,
            "statistics": safe_stats,
            "summary": {
                "total_files": self.stats['total_files'],
                "successful_files": self.stats['processed_files'],
                "failed_files": self.stats['failed_files'],
                "success_rate": self.stats['processed_files']/max(1, self.stats['total_files'])*100,
                "avg_backup_usage_rate": sum(r.get('backup_usage_rate', 0) for r in batch_results if r.get('success')) / max(1, len([r for r in batch_results if r.get('success')])) * 100
            }
        }

        with open(os.path.join(output_dir, "cloud_segment_batch_report.json"), 'w', encoding='utf-8') as f:
            f.write(safe_json_dumps(batch_report, indent=2))

        print(f"📄 批量报告已保存: cloud_segment_batch_report.json")

        return batch_report

def main():
    """主函数"""
    evaluator = CloudModelSegmentEvaluator()

    # 输入输出目录
    input_dir = "results/results"  # 可根据实际情况修改
    output_dir = "cloud_segment_results"

    # 批量分析 - 处理全部文件
    evaluator.batch_analyze(input_dir, output_dir, max_files=None)  # 处理所有文件

if __name__ == "__main__":
    main()