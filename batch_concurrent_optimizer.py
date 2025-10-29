#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量并发优化器 - 4题分段 + 并发处理
"""

import sys
import os
import json
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class BatchConcurrentOptimizer:
    def __init__(self, models: List[str] = None, cache_dir: str = "batch_cache",
                 segment_size: int = 4, max_concurrent: int = 3):
        self.models = models or ["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 优化参数
        self.segment_size = segment_size  # 每段问题数量（从2增加到4）
        self.max_concurrent = max_concurrent  # 最大并发数

        # 性能统计
        self.stats = {
            'cache_hits': 0,
            'api_calls': 0,
            'total_segments': 0,
            'segments_per_file': 0,
            'processing_time': 0
        }

    def _create_segment_cache_key(self, questions: List[Dict], model: str) -> str:
        """创建分段缓存键"""
        # 基于问题内容的哈希
        content = f"{model}_" + "_".join([q['question'] + q['answer'] for q in questions])
        return hashlib.sha256(content.encode()).hexdigest()

    def _load_segment_cache(self, cache_key: str) -> Optional[Dict]:
        """加载分段缓存"""
        cache_file = self.cache_dir / f"segment_{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def _save_segment_cache(self, cache_key: str, result: Dict):
        """保存分段缓存"""
        cache_file = self.cache_dir / f"segment_{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"缓存保存失败: {e}")

    def _create_batch_prompt(self, questions: List[Dict], segment_num: int) -> str:
        """创建批量分析提示 - 4题一段"""
        prompt = f"""请同时分析以下{len(questions)}个问题和回答，评估Big5人格特质。请为每个问题提供独立的评分，然后计算该分段的整体平均分。

"""

        for i, q in enumerate(questions, 1):
            prompt += f"\n=== 问题 {i} ===\n"
            prompt += f"问题: {q['question']}\n"
            prompt += f"回答: {q['answer']}\n"

        prompt += f"""

请返回JSON格式：
{{
  "segment_number": {segment_num},
  "questions_count": {len(questions)},
  "individual_scores": [
    {{
      "question_index": 1,
      "scores": {{
        "openness_to_experience": 1-5,
        "conscientiousness": 1-5,
        "extraversion": 1-5,
        "agreeableness": 1-5,
        "neuroticism": 1-5
      }},
      "evidence": {{
        "openness_to_experience": ["具体证据"],
        ...
      }}
    }},
    ...
  ],
  "segment_average_scores": {{
    "openness_to_experience": 1-5,
    "conscientiousness": 1-5,
    "extraversion": 1-5,
    "agreeableness": 1-5,
    "neuroticism": 1-5
  }},
  "segment_evidence": {{
    "openness_to_experience": ["综合证据"],
    ...
  }}
}}

请确保：
1. 每个评分都在1-5之间
2. 提供具体的分析证据
3. segment_average_scores是individual_scores的平均值
"""

        return prompt

    async def _analyze_segment_async(self, questions: List[Dict], segment_num: int, model: str) -> Dict:
        """异步分析分段"""
        self.stats['total_segments'] += 1

        # 检查缓存
        cache_key = self._create_segment_cache_key(questions, model)
        cached_result = self._load_segment_cache(cache_key)

        if cached_result:
            self.stats['cache_hits'] += 1
            print(f"  📦 缓存命中: 模型 {model} 段 {segment_num}")
            return cached_result

        # 执行API调用
        self.stats['api_calls'] += 1
        print(f"  🔍 分析段 {segment_num}: 模型 {model} ({len(questions)} 题)")

        try:
            # 创建批量提示
            prompt = self._create_batch_prompt(questions, segment_num)

            # 调用API（在线程池中执行同步调用）
            from enhanced_cloud_analyzer import EnhancedCloudAnalyzer
            analyzer = EnhancedCloudAnalyzer(model=model)

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                response = await loop.run_in_executor(
                    executor,
                    analyzer._call_api,
                    prompt
                )

            # 解析响应
            result = self._parse_batch_response(response, segment_num, len(questions))

            # 保存缓存
            if result.get('success', False):
                self._save_segment_cache(cache_key, result)

            return result

        except Exception as e:
            return {
                'success': False,
                'segment_number': segment_num,
                'model': model,
                'error': str(e),
                'questions_count': len(questions)
            }

    def _parse_batch_response(self, response: str, segment_num: int, questions_count: int) -> Dict:
        """解析批量响应"""
        try:
            import re

            # 尝试提取JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)

                # 验证结果格式
                if 'segment_average_scores' in result:
                    result['segment_number'] = segment_num
                    result['questions_count'] = questions_count
                    result['success'] = True

                    # 确保所有评分都在1-5范围内
                    for trait in result['segment_average_scores']:
                        score = result['segment_average_scores'][trait]
                        result['segment_average_scores'][trait] = max(1, min(5, int(score)))

                    return result

        except Exception as e:
            print(f"响应解析失败: {e}")

        return {
            'success': False,
            'segment_number': segment_num,
            'questions_count': questions_count,
            'error': '响应解析失败'
        }

    def _create_segments(self, questions: List[Dict]) -> List[List[Dict]]:
        """创建分段 - 每段4题"""
        segments = []

        for i in range(0, len(questions), self.segment_size):
            segment_questions = questions[i:i + self.segment_size]
            segments.append(segment_questions)

        self.stats['segments_per_file'] = len(segments)
        return segments

    async def analyze_file_optimized(self, file_path: Path, output_dir: Path) -> Dict:
        """优化文件分析"""
        start_time = time.time()
        print(f"🚀 批量并发优化分析: {file_path.name}")
        print(f"📊 分段大小: {self.segment_size}题/段, 并发数: {self.max_concurrent}")

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

            # 创建分段（4题一段）
            segments = self._create_segments(questions)
            print(f"📊 {len(questions)} 个问题分为 {len(segments)} 个分段")

            # 并发分析所有模型
            all_model_results = {}

            for model in self.models:
                print(f"\n🤖 处理模型: {model}")

                # 创建并发任务
                tasks = []
                for i, segment_questions in enumerate(segments, 1):
                    task = self._analyze_segment_async(segment_questions, i, model)
                    tasks.append(task)

                # 控制并发数量
                model_results = []
                for i in range(0, len(tasks), self.max_concurrent):
                    batch_tasks = tasks[i:i + self.max_concurrent]
                    batch_results = await asyncio.gather(*batch_tasks)
                    model_results.extend(batch_results)

                all_model_results[model] = model_results

                # 显示进度
                success_count = len([r for r in model_results if r.get('success', False)])
                print(f"  ✅ {model}: {success_count}/{len(segments)} 分段成功")

            # 计算最终评分
            final_scores = self._calculate_final_scores(all_model_results)
            mbti_type = self._calculate_mbti(final_scores)

            # 计算模型一致性
            model_consistency = self._calculate_model_consistency(all_model_results)

            # 生成结果
            processing_time = time.time() - start_time
            self.stats['processing_time'] += processing_time

            result = {
                'success': True,
                'file': str(file_path),
                'processing_time': processing_time,
                'optimization_info': {
                    'segment_size': self.segment_size,
                    'segments_count': len(segments),
                    'models_count': len(self.models),
                    'max_concurrent': self.max_concurrent,
                    'original_segments': len(questions) // 2,  # 原来2题一段的数量
                    'optimization_ratio': (len(questions) // 2) / len(segments)
                },
                'file_info': {
                    'filename': file_path.name,
                    'total_questions': len(questions),
                    'segments': len(segments),
                    'models': self.models
                },
                'final_scores': final_scores,
                'mbti_type': mbti_type,
                'model_consistency': model_consistency,
                'model_results': all_model_results,
                'performance_stats': {
                    'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['total_segments']) * 100,
                    'api_calls_saved': self.stats['cache_hits'],
                    'total_api_calls': self.stats['api_calls'],
                    'avg_time_per_segment': processing_time / (len(segments) * len(self.models)),
                    'segments_per_second': (len(segments) * len(self.models)) / processing_time
                }
            }

            # 保存结果
            output_file = output_dir / f"{file_path.stem}_batch_optimized.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 批量并发优化完成: {output_file}")
            print(f"⏱️  处理时间: {processing_time:.1f} 秒")
            print(f"📊 优化效果: API调用减少 {result['optimization_info']['optimization_ratio']:.1f}倍")
            print(f"🎯 最终评分: {final_scores}")
            print(f"🧠 MBTI: {mbti_type}")
            print(f"🚀 处理速度: {result['performance_stats']['segments_per_second']:.2f} 段/秒")

            return result

        except Exception as e:
            return {
                'success': False,
                'file': str(file_path),
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def _calculate_final_scores(self, all_model_results: Dict) -> Dict:
        """计算最终评分"""
        trait_scores = {}

        for model, results in all_model_results.items():
            model_trait_scores = {}

            for result in results:
                if result.get('success', False) and 'segment_average_scores' in result:
                    for trait, score in result['segment_average_scores'].items():
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

    def _calculate_model_consistency(self, all_model_results: Dict) -> Dict:
        """计算模型一致性"""
        consistency = {}

        for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            model_scores = []

            for model, results in all_model_results.items():
                trait_scores = []
                for result in results:
                    if result.get('success', False) and 'segment_average_scores' in result:
                        score = result['segment_average_scores'].get(trait, 3)
                        trait_scores.append(score)

                if trait_scores:
                    model_avg = sum(trait_scores) / len(trait_scores)
                    model_scores.append(model_avg)

            if len(model_scores) >= 2:
                # 计算一致性（100%表示完全一致）
                max_score = max(model_scores)
                min_score = min(model_scores)
                consistency[trait] = max(0, 100 - (max_score - min_score) * 20)
            else:
                consistency[trait] = 100

        return consistency

async def test_batch_concurrent_optimizer():
    print("🚀 测试批量并发优化器...")

    try:
        # 创建优化器
        optimizer = BatchConcurrentOptimizer(
            segment_size=4,  # 4题一段
            max_concurrent=3  # 最大3个并发
        )

        # 查找测试文件
        results_dir = Path("results/results")
        json_files = list(results_dir.glob("*.json"))

        if not json_files:
            print("❌ 没有找到测试文件")
            return

        # 选择测试文件
        test_file = json_files[20] if len(json_files) > 20 else json_files[0]
        print(f"📁 测试文件: {test_file.name}")

        # 创建输出目录
        output_dir = Path("batch_optimized_results")
        output_dir.mkdir(exist_ok=True)

        # 执行优化分析
        result = await optimizer.analyze_file_optimized(test_file, output_dir)

        if result['success']:
            print(f"\n✅ 批量并发优化测试成功!")

            opt_info = result['optimization_info']
            perf = result['performance_stats']

            print(f"📊 优化效果:")
            print(f"   分段数量: {opt_info['original_segments']} → {opt_info['segments_count']} (减少 {opt_info['optimization_ratio']:.1f}倍)")
            print(f"   处理时间: {result['processing_time']:.1f} 秒")
            print(f"   缓存命中率: {perf['cache_hit_rate']:.1f}%")
            print(f"   处理速度: {perf['segments_per_second']:.2f} 段/秒")
            print(f"   API调用节省: {perf['api_calls_saved']} 次")

            # 估算总体提升
            original_time = opt_info['original_segments'] * len(optimizer.models) * 30  # 假设原来每段30秒
            speedup = original_time / result['processing_time']
            print(f"   🚀 预估整体加速: {speedup:.1f}倍")

        else:
            print(f"❌ 测试失败: {result['error']}")

    except Exception as e:
        print(f"💥 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_batch_concurrent_optimizer())