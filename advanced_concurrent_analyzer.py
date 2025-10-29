#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级并发分析器 - 5题分段 + 1秒延迟 + 智能并发优化
"""

import sys
import os
import json
import asyncio
import hashlib
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
import queue

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class AdvancedConcurrentAnalyzer:
    def __init__(self, models: List[str] = None, cache_dir: str = "advanced_cache"):
        self.models = models or ["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 高级优化参数
        self.segment_size = 5  # 5题每段
        self.delay_between_batches = 1  # 1秒延迟
        self.max_concurrent_per_model = 4  # 每个模型最大并发
        self.max_total_concurrent = 8  # 总最大并发
        self.adaptive_batch_size = True  # 自适应批量大小

        # 性能统计
        self.stats = {
            'cache_hits': 0,
            'api_calls': 0,
            'total_segments': 0,
            'concurrent_batches': 0,
            'adaptive_adjustments': 0,
            'processing_time': 0,
            'avg_response_time': 0
        }

        # 动态调整参数
        self.current_concurrent_limit = self.max_concurrent_per_model
        self.response_times = queue.Queue(maxsize=10)

    def _get_smart_cache_key(self, questions: List[Dict], model: str) -> str:
        """智能缓存键 - 考虑问题顺序和内容"""
        # 标准化问题内容
        normalized_content = []
        for q in questions:
            normalized = f"{q['question'].strip()}_{q['answer'].strip()}"
            normalized_content.append(normalized)

        # 创建顺序敏感的哈希
        content_str = f"{model}_" + "_".join(normalized_content)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def _load_smart_cache(self, cache_key: str) -> Optional[Dict]:
        """加载智能缓存"""
        cache_file = self.cache_dir / f"smart_{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_entry = json.load(f)

                # 检查缓存时效性（7天）
                cache_time = datetime.fromisoformat(cache_entry.get('timestamp', '1970-01-01'))
                if (datetime.now() - cache_time).days > 7:
                    cache_file.unlink()
                    return None

                self.stats['cache_hits'] += 1
                return cache_entry['result']

            except Exception as e:
                print(f"缓存读取失败: {e}")
                try:
                    cache_file.unlink()
                except:
                    pass

        return None

    def _save_smart_cache(self, cache_key: str, result: Dict):
        """保存智能缓存"""
        cache_file = self.cache_dir / f"smart_{cache_key}.json"
        try:
            cache_entry = {
                'timestamp': datetime.now().isoformat(),
                'result': result
            }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"缓存保存失败: {e}")

    def _create_advanced_batch_prompt(self, questions: List[Dict], segment_num: int) -> str:
        """创建高级批量提示 - 5题分析"""
        prompt = f"""作为专业的人格分析专家，请同时分析以下{len(questions)}个问题并回答，评估Big5人格特质。

"""

        for i, q in enumerate(questions, 1):
            prompt += f"""
📋 问题 {i}:
问题: {q['question']}
回答: {q['answer']}
"""

        prompt += f"""

🎯 分析要求:
1. 对每个问题独立评分（1-5分制）
2. 考虑问题间的相互影响和一致性
3. 提供具体的分析证据
4. 计算5题的综合评分

📊 返回JSON格式:
{{
  "segment_number": {segment_num},
  "questions_count": {len(questions)},
  "individual_analysis": [
    {{
      "question_index": 1,
      "scores": {{
        "openness_to_experience": 1-5,
        "conscientiousness": 1-5,
        "extraversion": 1-5,
        "agreeableness": 1-5,
        "neuroticism": 1-5
      }},
      "confidence": 1-100,
      "evidence": {{
        "openness_to_experience": ["具体证据1", "具体证据2"],
        "conscientiousness": ["具体证据1", "具体证据2"],
        "extraversion": ["具体证据1", "具体证据2"],
        "agreeableness": ["具体证据1", "具体证据2"],
        "neuroticism": ["具体证据1", "具体证据2"]
      }}
    }}
  ],
  "segment_summary": {{
    "average_scores": {{
      "openness_to_experience": 1-5,
      "conscientiousness": 1-5,
      "extraversion": 1-5,
      "agreeableness": 1-5,
      "neuroticism": 1-5
    }},
    "overall_confidence": 1-100,
    "consistency_score": 1-100,
    "key_insights": ["关键洞察1", "关键洞察2", "关键洞察3"]
  }}
}}

✅ 质量要求:
- 所有评分必须在1-5范围内
- 提供具体的分析证据
- 评估问题间的一致性
- 计算准确的平均分"""

        return prompt

    async def _call_api_with_monitoring(self, prompt: str, model: str) -> Tuple[str, float]:
        """带监控的API调用"""
        start_time = time.time()

        try:
            # 使用线程池执行同步API调用
            from enhanced_cloud_analyzer import EnhancedCloudAnalyzer
            analyzer = EnhancedCloudAnalyzer(model=model)

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                response = await loop.run_in_executor(
                    executor,
                    analyzer._call_api,
                    prompt
                )

            response_time = time.time() - start_time

            # 更新响应时间统计
            try:
                self.response_times.put(response_time, block=False)
                if self.response_times.qsize() > 10:
                    self.response_times.get(block=False)  # 移除最旧的
            except queue.Full:
                pass

            self.stats['avg_response_time'] = response_time
            self.stats['api_calls'] += 1

            return response, response_time

        except Exception as e:
            response_time = time.time() - start_time
            print(f"API调用失败 ({model}): {e}")
            return "", response_time

    def _adaptive_adjust_concurrency(self, avg_response_time: float):
        """自适应调整并发数"""
        if not self.adaptive_batch_size:
            return

        # 根据响应时间调整并发数
        if avg_response_time < 20:  # 响应很快，增加并发
            new_limit = min(self.max_concurrent_per_model + 1, 6)
            if new_limit != self.current_concurrent_limit:
                self.current_concurrent_limit = new_limit
                self.stats['adaptive_adjustments'] += 1
                print(f"📈 自适应调整: 并发数提升到 {self.current_concurrent_limit}")

        elif avg_response_time > 60:  # 响应较慢，减少并发
            new_limit = max(self.current_concurrent_limit - 1, 2)
            if new_limit != self.current_concurrent_limit:
                self.current_concurrent_limit = new_limit
                self.stats['adaptive_adjustments'] += 1
                print(f"📉 自适应调整: 并发数降低到 {self.current_concurrent_limit}")

    async def _analyze_segment_advanced(self, questions: List[Dict], segment_num: int, model: str) -> Dict:
        """高级分段分析"""
        self.stats['total_segments'] += 1

        # 检查智能缓存
        cache_key = self._get_smart_cache_key(questions, model)
        cached_result = self._load_smart_cache(cache_key)

        if cached_result:
            print(f"  📦 智能缓存命中: {model} 段 {segment_num}")
            return cached_result

        # 执行API调用
        print(f"  🔍 高级分析: {model} 段 {segment_num} ({len(questions)} 题)")

        try:
            # 创建高级提示
            prompt = self._create_advanced_batch_prompt(questions, segment_num)

            # 调用API
            response, response_time = await self._call_api_with_monitoring(prompt, model)

            # 解析响应
            result = self._parse_advanced_response(response, segment_num, len(questions))

            # 自适应调整并发数
            if len(self.response_times.queue) >= 5:
                recent_times = list(self.response_times.queue)
                avg_time = sum(recent_times) / len(recent_times)
                self._adaptive_adjust_concurrency(avg_time)

            # 保存缓存
            if result.get('success', False):
                self._save_smart_cache(cache_key, result)

            result['response_time'] = response_time
            return result

        except Exception as e:
            return {
                'success': False,
                'segment_number': segment_num,
                'model': model,
                'error': str(e),
                'questions_count': len(questions)
            }

    def _parse_advanced_response(self, response: str, segment_num: int, questions_count: int) -> Dict:
        """解析高级响应"""
        try:
            import re

            # 尝试提取JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)

                # 验证关键字段
                if 'segment_summary' in result and 'average_scores' in result['segment_summary']:
                    result['segment_number'] = segment_num
                    result['questions_count'] = questions_count
                    result['success'] = True

                    # 验证并修复评分
                    for trait, score in result['segment_summary']['average_scores'].items():
                        result['segment_summary']['average_scores'][trait] = max(1, min(5, int(score)))

                    return result

        except Exception as e:
            print(f"高级响应解析失败: {e}")

        return {
            'success': False,
            'segment_number': segment_num,
            'questions_count': questions_count,
            'error': '响应解析失败'
        }

    def _create_adaptive_segments(self, questions: List[Dict]) -> List[List[Dict]]:
        """创建自适应分段"""
        segments = []
        total_questions = len(questions)

        # 标准分段（5题一段）
        for i in range(0, total_questions, self.segment_size):
            segment_questions = questions[i:i + self.segment_size]
            segments.append(segment_questions)

        # 处理剩余问题（如果不够5题，合并到前一段）
        if len(segments) > 1 and len(segments[-1]) < 3:
            last_segment = segments.pop()
            segments[-1].extend(last_segment)

        return segments

    async def _process_model_concurrent(self, questions: List[Dict], model: str) -> List[Dict]:
        """并发处理单个模型的所有分段"""
        segments = self._create_adaptive_segments(questions)
        print(f"🤖 处理模型 {model}: {len(segments)} 个分段")

        # 创建异步任务
        tasks = []
        for i, segment_questions in enumerate(segments, 1):
            task = self._analyze_segment_advanced(segment_questions, i, model)
            tasks.append(task)

        # 控制并发数量
        results = []
        semaphore = asyncio.Semaphore(self.current_concurrent_limit)

        async def controlled_task(task):
            async with semaphore:
                return await task

        # 分批处理任务
        batch_size = self.max_total_concurrent // len(self.models)
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*[controlled_task(task) for task in batch_tasks])
            results.extend(batch_results)

            # 批次间延迟
            if i + batch_size < len(tasks):
                await asyncio.sleep(self.delay_between_batches)

        # 统计成功分段
        success_count = len([r for r in results if r.get('success', False)])
        print(f"  ✅ {model}: {success_count}/{len(segments)} 分段成功")

        return results

    async def analyze_file_advanced(self, file_path: Path, output_dir: Path) -> Dict:
        """高级文件分析"""
        start_time = time.time()
        print(f"🚀 高级并发分析: {file_path.name}")
        print(f"📊 配置: {self.segment_size}题/段, {self.delay_between_scores}秒延迟, 自适应并发")

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取问题
            questions = []
            for item in data:
                if 'question' in item and 'answer' in item:
                    questions.append({
                        'question': item['question'],
                        'answer': item['answer']
                    })

            if not questions:
                return {
                    'success': False,
                    'error': '没有找到有效问题',
                    'file': str(file_path)
                }

            # 创建自适应分段
            segments = self._create_adaptive_segments(questions)
            print(f"📊 {len(questions)} 个问题分为 {len(segments)} 个分段")

            # 并发处理所有模型
            all_model_results = {}
            model_tasks = []

            for model in self.models:
                task = self._process_model_concurrent(questions, model)
                model_tasks.append((model, task))

            # 等待所有模型完成
            for model, task in model_tasks:
                all_model_results[model] = await task

            # 计算最终结果
            final_scores = self._calculate_advanced_final_scores(all_model_results)
            mbti_type = self._calculate_mbti(final_scores)
            model_consistency = self._calculate_advanced_consistency(all_model_results)

            # 生成结果
            processing_time = time.time() - start_time
            self.stats['processing_time'] += processing_time

            result = {
                'success': True,
                'file': str(file_path),
                'processing_time': processing_time,
                'advanced_config': {
                    'segment_size': self.segment_size,
                    'segments_count': len(segments),
                    'models_count': len(self.models),
                    'initial_concurrent': self.max_concurrent_per_model,
                    'final_concurrent': self.current_concurrent_limit,
                    'adaptive_adjustments': self.stats['adaptive_adjustments'],
                    'delay_between_batches': self.delay_between_batches
                },
                'file_info': {
                    'filename': file_path.name,
                    'total_questions': len(questions),
                    'segments': len(segments),
                    'original_segments': len(questions) // 2,  # 原来2题分段
                    'segment_reduction': (len(questions) // 2) / len(segments)
                },
                'final_scores': final_scores,
                'mbti_type': mbti_type,
                'model_consistency': model_consistency,
                'model_results': all_model_results,
                'performance_stats': {
                    'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['total_segments']) * 100,
                    'api_calls': self.stats['api_calls'],
                    'api_calls_saved': self.stats['cache_hits'],
                    'avg_response_time': self.stats['avg_response_time'],
                    'segments_per_second': (self.stats['total_segments'] * len(self.models)) / processing_time,
                    'concurrent_efficiency': self.current_concurrent_limit / self.max_concurrent_per_model
                }
            }

            # 保存结果
            output_file = output_dir / f"{file_path.stem}_advanced_concurrent.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 高级并发分析完成: {output_file}")
            print(f"⏱️  处理时间: {processing_time:.1f} 秒")
            print(f"📊 分段优化: {result['file_info']['original_segments']} → {len(segments)} (减少 {result['file_info']['segment_reduction']:.1f}倍)")
            print(f"🚀 处理速度: {result['performance_stats']['segments_per_second']:.2f} 段/秒")
            print(f"🎯 最终评分: {final_scores}")
            print(f"🧠 MBTI: {mbti_type}")
            print(f"🔧 自适应调整: {self.stats['adaptive_adjustments']} 次")

            return result

        except Exception as e:
            return {
                'success': False,
                'file': str(file_path),
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def _calculate_advanced_final_scores(self, all_model_results: Dict) -> Dict:
        """计算高级最终评分"""
        trait_scores = {}

        for model, results in all_model_results.items():
            model_trait_scores = {}

            for result in results:
                if result.get('success', False) and 'segment_summary' in result:
                    for trait, score in result['segment_summary']['average_scores'].items():
                        if trait not in model_trait_scores:
                            model_trait_scores[trait] = []
                        model_trait_scores[trait].append(score)

            # 计算模型平均分
            for trait, scores in model_trait_scores.items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    if trait not in trait_scores:
                        trait_scores[trait] = []
                    trait_scores[trait].append(avg_score)

        # 计算跨模型平均分
        final_scores = {}
        for trait, scores in trait_scores.items():
            if scores:
                final_scores[trait] = round(sum(scores) / len(scores))
            else:
                final_scores[trait] = 3

        return final_scores

    def _calculate_mbti(self, scores: Dict) -> str:
        """计算MBTI类型"""
        try:
            e_i = "E" if scores.get('extraversion', 3) > 3 else "I"
            s_n = "S" if scores.get('openness_to_experience', 3) < 4 else "N"
            t_f = "T" if scores.get('agreeableness', 3) < 3 else "F"
            j_p = "J" if scores.get('conscientiousness', 3) > 3 else "P"

            return f"{e_i}{s_n}{t_f}{j_p}"
        except:
            return "UNKNOWN"

    def _calculate_advanced_consistency(self, all_model_results: Dict) -> Dict:
        """计算高级一致性"""
        consistency = {}

        for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            model_scores = []

            for model, results in all_model_results.items():
                trait_scores = []
                for result in results:
                    if result.get('success', False) and 'segment_summary' in result:
                        score = result['segment_summary']['average_scores'].get(trait, 3)
                        trait_scores.append(score)

                if trait_scores:
                    model_avg = sum(trait_scores) / len(trait_scores)
                    model_scores.append(model_avg)

            if len(model_scores) >= 2:
                max_score = max(model_scores)
                min_score = min(model_scores)
                consistency[trait] = max(0, 100 - (max_score - min_score) * 20)
            else:
                consistency[trait] = 100

        return consistency

async def test_advanced_concurrent():
    print("🚀 测试高级并发分析器...")

    try:
        analyzer = AdvancedConcurrentAnalyzer()

        # 查找测试文件
        results_dir = Path("results/results")
        json_files = list(results_dir.glob("*.json"))

        if not json_files:
            print("❌ 没有找到测试文件")
            return

        # 选择测试文件
        test_file = json_files[25] if len(json_files) > 25 else json_files[0]
        print(f"📁 测试文件: {test_file.name}")

        # 创建输出目录
        output_dir = Path("advanced_concurrent_results")
        output_dir.mkdir(exist_ok=True)

        # 执行高级并发分析
        result = await analyzer.analyze_file_advanced(test_file, output_dir)

        if result['success']:
            print(f"\n✅ 高级并发测试成功!")

            config = result['advanced_config']
            perf = result['performance_stats']

            print(f"📊 高级配置:")
            print(f"   分段大小: {config['segment_size']}题/段")
            print(f"   并发数: {config['initial_concurrent']} → {config['final_concurrent']}")
            print(f"   自适应调整: {config['adaptive_adjustments']} 次")

            print(f"🚀 性能统计:")
            print(f"   处理时间: {result['processing_time']:.1f} 秒")
            print(f"   分段减少: {result['file_info']['segment_reduction']:.1f}倍")
            print(f"   缓存命中率: {perf['cache_hit_rate']:.1f}%")
            print(f"   处理速度: {perf['segments_per_second']:.2f} 段/秒")
            print(f"   并发效率: {perf['concurrent_efficiency']:.1%}")

            # 估算总体提升
            original_segments = result['file_info']['original_segments']
            new_segments = result['file_info']['segments']
            speedup = (original_segments * 3) / (new_segments * len(analyzer.models) / 8)  # 考虑8总并发
            print(f"   🎯 预估整体加速: {speedup:.1f}倍")

        else:
            print(f"❌ 测试失败: {result['error']}")

    except Exception as e:
        print(f"💥 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_advanced_concurrent())