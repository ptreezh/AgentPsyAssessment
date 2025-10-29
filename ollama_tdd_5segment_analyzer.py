#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama TDD驱动的5题分段三模型并行分析器
保证5题分段（每段5题，每个测评报告分10段），三个Ollama模型独立并行评估
基于测试驱动开发方法，确保高置信度和一致性
"""

import sys
import os
import json
import subprocess
import re
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import statistics
import concurrent.futures

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class OllamaTDD5SegmentAnalyzer:
    def __init__(self):
        # 三个Ollama云模型配置
        self.models = [
            {"name": "deepseek-v3.1:671b-cloud", "description": "DeepSeek 671B云模型"},
            {"name": "gpt-oss:120b-cloud", "description": "GPT OSS 120B云模型"},
            {"name": "qwen3-coder:480b-cloud", "description": "Qwen3 Coder 480B云模型"}
        ]

        # 测试用例定义
        self.test_cases = self._define_test_cases()

        # 验证结果缓存
        self.validation_cache = {}

    def _define_test_cases(self) -> Dict:
        """定义TDD测试用例"""
        return {
            "simple_json": {
                "prompt": "请返回JSON格式：{\"score\": 3}",
                "expected_structure": {"score": int},
                "description": "基础JSON响应测试"
            },
            "big5_simple": {
                "prompt": """分析回答并返回JSON：
问题：我喜欢尝试新事物
回答：是的，我经常尝试新的餐厅

返回格式：
{
  "success": true,
  "scores": {
    "openness_to_experience": 1或3或5
  }
}""",
                "expected_structure": {
                    "success": bool,
                    "scores": {"openness_to_experience": int}
                },
                "description": "Big5简单评分测试"
            },
            "big5_complete": {
                "prompt": """作为心理评估分析师，分析以下回答：

问题1：我喜欢尝试新事物
回答：是的，我经常尝试新的餐厅和活动

问题2：我做事很有条理
回答：我总是制定详细计划并按时完成

请返回JSON格式：
{
  "success": true,
  "scores": {
    "openness_to_experience": 1或3或5,
    "conscientiousness": 1或3或5
  },
  "evidence": {
    "openness_to_experience": "具体证据",
    "conscientiousness": "具体证据"
  },
  "confidence": "high/medium/low"
}""",
                "expected_structure": {
                    "success": bool,
                    "scores": {
                        "openness_to_experience": int,
                        "conscientiousness": int
                    },
                    "evidence": {
                        "openness_to_experience": str,
                        "conscientiousness": str
                    },
                    "confidence": str
                },
                "description": "完整Big5分析测试"
            }
        }

    def _execute_ollama_command(self, model_name: str, prompt: str, timeout: int = 180) -> Tuple[bool, str, float]:
        """
        执行Ollama命令的健壮方法
        返回：(成功标志, 响应内容, 处理时间)
        """
        try:
            # 构建命令 - 使用正确的格式
            cmd = ['ollama', 'run', model_name, prompt, '--format', 'json']

            start_time = time.time()

            # 使用encoding='utf-8'和errors='ignore'来处理编码问题
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
                # 清理响应中的终端控制字符
                cleaned_response = self._clean_terminal_output(result.stdout)
                return True, cleaned_response, processing_time
            else:
                return False, f"命令失败: {result.stderr}", processing_time

        except subprocess.TimeoutExpired:
            return False, "请求超时", timeout
        except Exception as e:
            return False, f"执行错误: {str(e)}", 0

    def _clean_terminal_output(self, text: str) -> str:
        """清理终端输出中的控制字符"""
        if not text:
            return ""

        # 移除ANSI转义序列
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', text)

        # 移除其他控制字符，但保留JSON相关字符
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)

        return cleaned.strip()

    def _parse_json_response(self, response_text: str) -> Dict:
        """
        多策略JSON解析器
        """
        if not response_text:
            return {"success": False, "error": "响应为空"}

        # 清理响应文本
        response_text = self._clean_terminal_output(response_text)

        # 解析策略列表（按优先级排序）
        strategies = [
            ("直接解析", self._direct_json_parse),
            ("代码块提取", self._extract_json_from_codeblock),
            ("正则提取", self._extract_json_with_regex),
            ("智能修复", self._smart_json_fix),
            ("模糊匹配", self._fuzzy_score_extract)
        ]

        for strategy_name, strategy_func in strategies:
            try:
                result = strategy_func(response_text)
                if result and self._validate_json_structure(result):
                    return {"success": True, "method": strategy_name, "data": result}
            except Exception as e:
                continue

        return {
            "success": False,
            "error": "所有解析策略失败",
            "raw_response": response_text[:500] if response_text else "空响应"
        }

    def _direct_json_parse(self, text: str) -> Optional[Dict]:
        """直接JSON解析"""
        text = text.strip()
        if text.startswith('{') and text.endswith('}'):
            return json.loads(text)
        return None

    def _extract_json_from_codeblock(self, text: str) -> Optional[Dict]:
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
                    return json.loads(match.strip())
                except:
                    continue
        return None

    def _extract_json_with_regex(self, text: str) -> Optional[Dict]:
        """使用正则表达式提取JSON"""
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # 标准JSON对象
            r'\{(?:[^{}"]|"[^"]*")*\}',          # 包含字符串的JSON
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        return None

    def _smart_json_fix(self, text: str) -> Optional[Dict]:
        """智能修复JSON格式问题"""
        try:
            # 移除BOM
            text = text.lstrip('\ufeff').strip()

            # 找到JSON对象
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
            text = re.sub(r'(\w+):', r'"\1":', text)  # 键加引号
            text = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)', r': "\1"', text)  # 值加引号
            text = re.sub(r'//.*?\n', '', text)  # 移除注释
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)  # 移除块注释
            text = re.sub(r',\s*}', '}', text)  # 移除尾部逗号
            text = re.sub(r',\s*]', ']', text)  # 移除数组尾部逗号

            return json.loads(text)
        except:
            return None

    def _fuzzy_score_extract(self, text: str) -> Optional[Dict]:
        """模糊提取评分信息"""
        scores = {}

        # Big5维度评分提取模式
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

    def _validate_json_structure(self, data: Dict) -> bool:
        """验证JSON数据结构"""
        if not isinstance(data, dict):
            return False

        # 检查必需字段
        if 'success' not in data:
            return False

        # 如果有scores字段，验证其结构
        if 'scores' in data:
            scores = data['scores']
            if not isinstance(scores, dict):
                return False

            # 验证评分值
            for trait, score in scores.items():
                if not isinstance(score, int) or score not in [1, 3, 5]:
                    return False

        return True

    def _validate_model_with_test_case(self, model_name: str, test_case_name: str) -> Dict:
        """使用测试用例验证模型"""
        if test_case_name not in self.test_cases:
            return {"success": False, "error": f"未知测试用例: {test_case_name}"}

        test_case = self.test_cases[test_case_name]
        cache_key = f"{model_name}_{test_case_name}"

        # 检查缓存
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]

        print(f"  🧪 测试 {model_name} - {test_case['description']}")

        success, response, processing_time = self._execute_ollama_command(
            model_name,
            test_case["prompt"]
        )

        if not success:
            result = {
                "success": False,
                "error": response,
                "processing_time": processing_time
            }
        else:
            parse_result = self._parse_json_response(response)
            result = {
                "success": parse_result["success"],
                "data": parse_result.get("data"),
                "method": parse_result.get("method"),
                "processing_time": processing_time,
                "raw_response": response[:200] if response else ""
            }

        # 缓存结果
        self.validation_cache[cache_key] = result
        return result

    def run_model_validation(self) -> Dict:
        """运行完整的模型验证测试"""
        print("🔬 TDD模型验证测试开始")
        print("=" * 50)

        validation_results = {}

        for model in self.models:
            model_name = model["name"]
            print(f"\n📋 验证模型: {model_name}")

            model_results = {}

            # 运行所有测试用例
            for test_name in ["simple_json", "big5_simple", "big5_complete"]:
                test_result = self._validate_model_with_test_case(model_name, test_name)
                model_results[test_name] = test_result

                if test_result["success"]:
                    print(f"    ✅ {test_name}: 通过 ({test_result.get('method', '未知方法')})")
                else:
                    print(f"    ❌ {test_name}: 失败 - {test_result.get('error', '未知错误')}")

            validation_results[model_name] = model_results

        # 生成验证报告
        report = self._generate_validation_report(validation_results)

        # 保存验证结果
        report_file = f"ollama_tdd_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 验证报告已保存: {report_file}")
        return report

    def _generate_validation_report(self, validation_results: Dict) -> Dict:
        """生成验证报告"""
        report = {
            "validation_time": datetime.now().isoformat(),
            "models_tested": list(validation_results.keys()),
            "summary": {},
            "detailed_results": validation_results,
            "recommendations": []
        }

        # 计算成功率
        total_tests = 0
        passed_tests = 0

        for model_name, model_results in validation_results.items():
            model_passed = 0
            model_total = len(model_results)

            for test_name, test_result in model_results.items():
                total_tests += 1
                if test_result["success"]:
                    passed_tests += 1
                    model_passed += 1

            report["summary"][model_name] = {
                "tests_passed": model_passed,
                "tests_total": model_total,
                "success_rate": model_passed / model_total if model_total > 0 else 0
            }

        overall_success_rate = passed_tests / total_tests if total_tests > 0 else 0
        report["summary"]["overall"] = {
            "tests_passed": passed_tests,
            "tests_total": total_tests,
            "success_rate": overall_success_rate
        }

        # 生成建议
        if overall_success_rate >= 0.8:
            report["recommendations"].append("✅ 模型验证通过，可以开始5题分段分析")
        elif overall_success_rate >= 0.5:
            report["recommendations"].append("⚠️ 部分测试通过，建议优化解析逻辑")
        else:
            report["recommendations"].append("❌ 验证失败，需要重大修复")

        return report

    def create_5segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """创建5题分段分析提示"""
        prompt = """你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**以下问卷回答，评估回答者展现的Big5人格特质。

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

**第""" + str(segment_number) + """段问卷内容（""" + str(len(segment)) + """题/共""" + str(total_segments) + """段）：**
"""

        for i, item in enumerate(segment, 1):
            prompt += """
**问题 """ + str(i) + """：**
""" + item['question'] + """

**回答 """ + str(i) + """：**
""" + item['answer'] + """

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

        success, response, processing_time = self._execute_ollama_command(model_name, prompt)

        if not success:
            return {
                'success': False,
                'model': model_name,
                'segment_number': segment_number,
                'error': response,
                'processing_time': processing_time
            }

        # 解析JSON响应
        parse_result = self._parse_json_response(response)

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

    def _calculate_mbti_type(self, scores: Dict) -> str:
        """根据Big5评分计算MBTI类型"""
        try:
            openness = scores.get('openness_to_experience', 3)
            conscientiousness = scores.get('conscientiousness', 3)
            extraversion = scores.get('extraversion', 3)
            agreeableness = scores.get('agreeableness', 3)
            neuroticism = scores.get('neuroticism', 3)

            I_E = 'I' if extraversion <= 3 else 'E'
            S_N = 'N' if openness >= 4 else 'S'
            T_F = 'F' if agreeableness >= 4 else 'T'
            J_P = 'J' if conscientiousness >= 4 else 'P'

            return f"{I_E}{S_N}{T_F}{J_P}"
        except Exception as e:
            return "UNKNOWN"

    def analyze_file_with_three_models(self, file_path: str, output_dir: str) -> Dict:
        """使用三个Ollama模型独立分析单个文件（5题分段，10段）"""
        print(f"📈 开始5题分段三模型分析: {Path(file_path).name}")

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取问题
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

            if len(questions) < 5:
                raise Exception(f"问题数量不足：{len(questions)}")

            # 分段处理（每段5题，确保10段）
            segment_size = 5
            segments = []

            # 取前50题，分成10段
            questions_to_process = questions[:50]
            for i in range(0, len(questions_to_process), segment_size):
                segment = questions_to_process[i:i+segment_size]
                if len(segment) == segment_size:
                    segments.append(segment)

            total_segments = len(segments)
            print(f"  📊 {len(questions)}题 -> {total_segments}段 (每段5题)")

            # 三模型并发分析
            model_analysis_results = {}
            total_start_time = time.time()

            # 使用线程池实现并发
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # 为每个模型创建分析任务
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
                            result = future.result(timeout=300)  # 5分钟超时
                            segment_results.append(result)

                            if result['success']:
                                successful_segments += 1
                                print(f"      ✅ 段{result['segment_number']}: {list(result['data']['scores'].values())} ({result.get('processing_time', 0):.1f}s)")
                            else:
                                print(f"      ❌ 段{result['segment_number']}: {result.get('error', 'Unknown error')}")

                            total_model_time += result.get('processing_time', 0)

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
                        mbti_type = self._calculate_mbti_type(final_scores)

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

            # 计算一致性分析
            consistency_analysis = self._calculate_model_consistency(model_analysis_results)

            # 保存结果
            output_filename = f"{Path(file_path).stem}_ollama_tdd_5segment_analysis.json"
            output_path = os.path.join(output_dir, output_filename)

            analysis_result = {
                "file_info": {
                    "filename": Path(file_path).name,
                    "total_questions": len(questions),
                    "segments_analyzed": total_segments,
                    "questions_per_segment": segment_size,
                    "analysis_date": datetime.now().isoformat(),
                    "analysis_method": "5题分段，三模型并行"
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
                    "high_confidence": consistency_analysis.get('high_confidence_consensus', False)
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)

            print(f"  💾 结果已保存: {output_filename}")

            # 显示简要结果
            print(f"  📋 分析结果摘要:")
            for model, results in model_analysis_results.items():
                print(f"    {model}: {results['final_scores']} -> {results['mbti_type']} ({results['successful_segments']}/{results['total_segments']}段成功, {results['success_rate']:.1%}成功率)")

            print(f"  🎯 一致性分析: {consistency_analysis.get('consensus_mbti', 'UNKNOWN')} ({'高置信度' if consistency_analysis.get('high_confidence_consensus', False) else '需要进一步验证'})")

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
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def _calculate_model_consistency(self, model_results: Dict) -> Dict:
        """计算三个模型间的一致性"""
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
            from collections import Counter
            mbti_counts = Counter(mbti_types)
            most_common_mbti, count = mbti_counts.most_common(1)[0]

            if count >= len(mbti_types):
                mbti_consensus = most_common_mbti
                high_confidence_consensus = True
            elif count >= 2:
                mbti_consensus = most_common_mbti
                high_confidence_consensus = False

        # 计算评分一致性
        trait_consistency = {}
        for trait, scores in scores_data.items():
            if len(scores) >= 2:
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                mean_score = statistics.mean(scores)

                if std_dev <= 0.8:
                    consistency_level = "高"
                elif std_dev <= 1.5:
                    consistency_level = "中"
                else:
                    consistency_level = "低"

                trait_consistency[trait] = {
                    "mean_score": mean_score,
                    "std_deviation": std_dev,
                    "consistency_level": consistency_level,
                    "scores": scores
                }

        # 计算整体一致性
        consistency_levels = [info["consistency_level"] for info in trait_consistency.values()]
        high_consistency_count = consistency_levels.count("高")

        if high_consistency_count >= 4:
            overall_consistency = "高"
        elif high_consistency_count >= 2:
            overall_consistency = "中"
        else:
            overall_consistency = "低"

        return {
            "consensus_mbti": mbti_consensus,
            "high_confidence_consensus": high_confidence_consensus,
            "mbti_distribution": dict(Counter(mbti_types)) if mbti_types else {},
            "trait_consistency": trait_consistency,
            "overall_consistency": overall_consistency,
            "models_analyzed": len(model_results),
            "analysis_timestamp": datetime.now().isoformat()
        }

def main():
    """主函数 - TDD驱动验证和5题分段分析"""
    print("🚀 Ollama TDD驱动的5题分段三模型并行分析器")
    print("=" * 60)

    analyzer = OllamaTDD5SegmentAnalyzer()

    # 步骤1: 运行TDD验证
    print("\n📋 步骤1: TDD模型验证")
    validation_report = analyzer.run_model_validation()

    # 检查Big5分析验证结果
    big5_success_rate = 0
    total_big5_tests = 0
    passed_big5_tests = 0

    for model_name, model_results in validation_report["detailed_results"].items():
        if "big5_complete" in model_results and model_results["big5_complete"]["success"]:
            passed_big5_tests += 1
        total_big5_tests += 1
        if "big5_simple" in model_results and model_results["big5_simple"]["success"]:
            passed_big5_tests += 1
        total_big5_tests += 1

    if total_big5_tests > 0:
        big5_success_rate = passed_big5_tests / total_big5_tests

    if big5_success_rate < 0.8:
        print(f"\n⚠️ Big5分析验证成功率较低 ({big5_success_rate:.1%})")
        print("建议先修复Big5分析问题再进行5题分段分析")
        return

    print(f"\n✅ Big5分析验证通过 ({big5_success_rate:.1%} 成功率)")
    print(f"   整体验证成功率: {validation_report['summary']['overall']['success_rate']:.1%}")

    # 步骤2: 5题分段分析测试
    print(f"\n📋 步骤2: 5题分段分析测试")

    # 查找测试文件
    results_dir = "results/results"
    test_files = list(Path(results_dir).glob("*.json"))[:1]  # 测试1个文件

    if not test_files:
        print("❌ 未找到测试文件")
        return

    # 创建输出目录
    output_dir = "ollama_tdd_5segment_results"
    os.makedirs(output_dir, exist_ok=True)

    # 分析测试文件
    test_file = test_files[0]
    result = analyzer.analyze_file_with_three_models(str(test_file), output_dir)

    if result['success']:
        print(f"\n🎉 5题分段分析测试成功!")
        print(f"   文件: {Path(test_file).name}")
        print(f"   处理时间: {result['total_time']:.1f}秒")
        print(f"   一致性: {result['consistency_analysis'].get('overall_consistency', '未知')}")

        if result['consistency_analysis'].get('high_confidence_consensus', False):
            print(f"   ✅ 高置信度一致: {result['consistency_analysis'].get('consensus_mbti', 'UNKNOWN')}")
        else:
            print(f"   ⚠️ 需要进一步验证")
    else:
        print(f"\n❌ 5题分段分析测试失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()