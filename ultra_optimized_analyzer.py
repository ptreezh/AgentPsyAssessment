#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级优化分析器 - 顶级LLM程序员优化方案
"""

import sys
import os
import json
import hashlib
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import time

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class UltraOptimizedAnalyzer:
    def __init__(self, models: List[str] = None, cache_dir: str = "smart_cache"):
        self.models = models or ["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 性能统计
        self.stats = {
            'cache_hits': 0,
            'api_calls': 0,
            'total_segments': 0,
            'processing_time': 0
        }

    def _get_smart_cache_key(self, question: str, answer: str, model: str) -> str:
        """智能缓存键 - 基于问题内容而非分段"""
        # 标准化文本
        normalized = f"{question.strip().lower()}_{answer.strip().lower()}_{model}"
        return hashlib.sha256(normalized.encode()).hexdigest()

    def _get_batch_cache_key(self, questions_answers: List[Tuple[str, str]], model: str) -> str:
        """批量缓存键"""
        content = f"{model}_{hash(str(questions_answers))}"
        return hashlib.md5(content.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """从缓存加载结果"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None

    def _save_to_cache(self, cache_key: str, result: Dict):
        """保存到缓存"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"缓存保存失败: {e}")

    async def _call_api_async(self, prompt: str, model: str) -> str:
        """异步API调用"""
        self.stats['api_calls'] += 1

        # 这里需要实现具体的异步API调用逻辑
        # 由于原始代码是同步的，这里用线程池模拟
        from enhanced_cloud_analyzer import EnhancedCloudAnalyzer
        analyzer = EnhancedCloudAnalyzer(model=model)

        # 在线程池中执行同步API调用
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = await loop.run_in_executor(
                executor,
                analyzer._call_api,
                prompt
            )
        return result

    def _create_batch_prompt(self, segments: List[str]) -> str:
        """创建批量分析提示"""
        prompt = """请同时分析以下多组问题，返回JSON数组格式的结果：

"""

        for i, segment in enumerate(segments, 1):
            prompt += f"\n=== 组 {i} ===\n{segment}\n"

        prompt += """

请返回格式：
[
  {
    "segment_number": 1,
    "scores": {
      "openness_to_experience": 1-5,
      "conscientiousness": 1-5,
      "extraversion": 1-5,
      "agreeableness": 1-5,
      "neuroticism": 1-5
    },
    "evidence": {
      "openness_to_experience": ["证据1", "证据2"],
      ...
    }
  },
  ...
]

确保每个组的评分都在1-5之间。"""

        return prompt

    async def _analyze_batch_segments(self, segments: List[str], model: str, batch_size: int = 3) -> List[Dict]:
        """批量分析分段"""
        results = []

        # 检查是否有批量缓存
        batch_cache_key = self._get_batch_cache_key(
            [(seg, "") for seg in segments], model
        )
        cached_batch = self._load_from_cache(batch_cache_key)
        if cached_batch:
            self.stats['cache_hits'] += len(segments)
            return cached_batch.get('results', [])

        # 分批处理
        for i in range(0, len(segments), batch_size):
            batch = segments[i:i+batch_size]

            # 创建批量提示
            batch_prompt = self._create_batch_prompt(batch)

            try:
                # 调用API
                response = await self._call_api_async(batch_prompt, model)

                # 解析批量响应
                batch_results = self._parse_batch_response(response, i + 1)
                results.extend(batch_results)

            except Exception as e:
                # 如果批量失败，降级为单个处理
                print(f"批量处理失败，降级为单个处理: {e}")
                for j, segment in enumerate(batch):
                    single_result = await self._analyze_single_segment_async(segment, i + j + 1, model)
                    results.append(single_result)

        # 保存批量缓存
        self._save_to_cache(batch_cache_key, {'results': results})

        return results

    async def _analyze_single_segment_async(self, segment_text: str, segment_num: int, model: str) -> Dict:
        """异步单个分段分析"""
        # 检查单个缓存
        cache_key = self._get_smart_cache_key(segment_text, "", model)
        cached_result = self._load_from_cache(cache_key)

        if cached_result:
            self.stats['cache_hits'] += 1
            return cached_result

        # 构建提示
        prompt = f"""请分析以下问题回答，评估Big5人格特质：

{segment_text}

请返回JSON格式：
{{
  "segment_number": {segment_num},
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
}}"""

        try:
            response = await self._call_api_async(prompt, model)
            result = self._parse_segment_response(response, segment_num)

            # 保存缓存
            self._save_to_cache(cache_key, result)

            return result

        except Exception as e:
            return {
                'success': False,
                'segment_number': segment_num,
                'error': str(e),
                'model': model
            }

    def _parse_batch_response(self, response: str, start_segment: int) -> List[Dict]:
        """解析批量响应"""
        try:
            # 尝试解析JSON数组
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                results = json.loads(json_str)

                # 验证和修复结果
                valid_results = []
                for i, result in enumerate(results):
                    if isinstance(result, dict) and 'scores' in result:
                        result['segment_number'] = start_segment + i
                        result['success'] = True
                        valid_results.append(result)

                return valid_results

        except Exception as e:
            print(f"批量响应解析失败: {e}")

        # 如果解析失败，返回空列表，让调用方降级处理
        return []

    def _parse_segment_response(self, response: str, segment_num: int) -> Dict:
        """解析单个分段响应"""
        try:
            # 使用原有的解析逻辑
            from enhanced_cloud_analyzer import EnhancedCloudAnalyzer
            analyzer = EnhancedCloudAnalyzer()
            return analyzer._parse_segment_response(response, segment_num)
        except Exception as e:
            return {
                'success': False,
                'segment_number': segment_num,
                'error': str(e)
            }

    def _extract_questions_smart(self, data: List[Dict]) -> List[Dict]:
        """智能提取问题"""
        questions = []

        for item in data:
            if 'question' in item and 'answer' in item:
                questions.append({
                    'question': item['question'],
                    'answer': item['answer'],
                    'text_hash': hashlib.md5(
                        f"{item['question']}_{item['answer']}".encode()
                    ).hexdigest()
                })

        return questions

    def _deduplicate_questions(self, questions: List[Dict]) -> List[Dict]:
        """去除重复问题"""
        seen_hashes = set()
        unique_questions = []

        for q in questions:
            if q['text_hash'] not in seen_hashes:
                seen_hashes.add(q['text_hash'])
                unique_questions.append(q)

        print(f"📊 问题去重: {len(questions)} -> {len(unique_questions)}")
        return unique_questions

    async def analyze_file_ultra_optimized(self, file_path: Path, output_dir: Path) -> Dict:
        """超级优化文件分析"""
        start_time = time.time()
        print(f"🚀 超级优化分析: {file_path.name}")

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 智能提取和去重问题
            questions = self._extract_questions_smart(data)
            unique_questions = self._deduplicate_questions(questions)

            if not unique_questions:
                return {
                    'success': False,
                    'error': '没有找到有效问题',
                    'file': str(file_path)
                }

            # 创建分段
            segments = []
            for i in range(0, len(unique_questions), 2):
                q1 = unique_questions[i]
                q2 = unique_questions[i+1] if i+1 < len(unique_questions) else None

                segment_text = f"分析以下问题和回答，评估Big5人格特质：\n\n"
                segment_text += f"问题1: {q1['question']}\n回答: {q1['answer']}\n\n"

                if q2:
                    segment_text += f"问题2: {q2['question']}\n回答: {q2['answer']}\n\n"

                segments.append(segment_text)

            print(f"📊 {len(unique_questions)} 个去重问题，分为 {len(segments)} 个分段")

            # 并发分析所有模型
            all_results = {}

            for model in self.models:
                print(f"🤖 模型 {model} 批量分析中...")

                # 批量分析
                model_results = await self._analyze_batch_segments(segments, model, batch_size=3)
                all_results[model] = model_results

                # 显示进度
                success_count = len([r for r in model_results if r.get('success', False)])
                print(f"  ✅ {model}: {success_count}/{len(segments)} 分段成功")

            # 计算最终评分
            final_scores = {}
            model_agreement = {}

            for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                trait_scores = []

                for model, results in all_results.items():
                    model_trait_scores = []
                    for result in results:
                        if result.get('success', False) and 'scores' in result:
                            score = result['scores'].get(trait, 3)
                            model_trait_scores.append(score)

                    if model_trait_scores:
                        avg_score = sum(model_trait_scores) / len(model_trait_scores)
                        trait_scores.append(avg_score)

                if trait_scores:
                    final_scores[trait] = round(sum(trait_scores) / len(trait_scores))
                    # 计算模型间一致性
                    consistency = 100 - (max(trait_scores) - min(trait_scores)) * 20
                    model_agreement[trait] = max(0, consistency)
                else:
                    final_scores[trait] = 3
                    model_agreement[trait] = 0

            # 计算MBTI
            mbti_type = self._calculate_mbti(final_scores)

            # 生成结果
            processing_time = time.time() - start_time
            self.stats['processing_time'] += processing_time
            self.stats['total_segments'] += len(segments) * len(self.models)

            result = {
                'success': True,
                'file': str(file_path),
                'processing_time': processing_time,
                'file_info': {
                    'filename': file_path.name,
                    'original_questions': len(questions),
                    'unique_questions': len(unique_questions),
                    'segments': len(segments),
                    'models': self.models
                },
                'final_scores': final_scores,
                'mbti_type': mbti_type,
                'model_agreement': model_agreement,
                'model_results': all_results,
                'performance_stats': {
                    'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['total_segments']) * 100,
                    'api_calls_saved': self.stats['cache_hits'],
                    'total_api_calls': self.stats['api_calls'],
                    'avg_time_per_segment': processing_time / (len(segments) * len(self.models))
                }
            }

            # 保存结果
            output_file = output_dir / f"{file_path.stem}_ultra_optimized.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ 超级优化完成: {output_file}")
            print(f"⏱️  处理时间: {processing_time:.1f} 秒")
            print(f"📊 缓存命中率: {result['performance_stats']['cache_hit_rate']:.1f}%")
            print(f"🎯 最终评分: {final_scores}")
            print(f"🧠 MBTI: {mbti_type}")

            return result

        except Exception as e:
            return {
                'success': False,
                'file': str(file_path),
                'error': str(e),
                'processing_time': time.time() - start_time
            }

    def _calculate_mbti(self, scores: Dict) -> str:
        """根据Big5评分计算MBTI"""
        try:
            e_i = "E" if scores.get('extraversion', 3) > 3 else "I"
            s_n = "S" if scores.get('openness_to_experience', 3) < 4 else "N"
            t_f = "T" if scores.get('agreeableness', 3) < 3 else "F"
            j_p = "J" if scores.get('conscientiousness', 3) > 3 else "P"

            return f"{e_i}{s_n}{t_f}{j_p}"
        except:
            return "UNKNOWN"

async def test_ultra_optimized():
    print("🚀 测试超级优化分析器...")

    try:
        analyzer = UltraOptimizedAnalyzer()

        # 查找测试文件
        results_dir = Path("results/results")
        json_files = list(results_dir.glob("*.json"))

        if not json_files:
            print("❌ 没有找到测试文件")
            return

        # 选择测试文件
        test_file = json_files[10] if len(json_files) > 10 else json_files[0]
        print(f"📁 测试文件: {test_file.name}")

        # 创建输出目录
        output_dir = Path("ultra_optimized_results")
        output_dir.mkdir(exist_ok=True)

        # 执行超级优化分析
        result = await analyzer.analyze_file_ultra_optimized(test_file, output_dir)

        if result['success']:
            print(f"✅ 超级优化测试成功!")
            stats = result['performance_stats']
            print(f"   处理时间: {result['processing_time']:.1f} 秒")
            print(f"   缓存命中率: {stats['cache_hit_rate']:.1f}%")
            print(f"   API调用节省: {stats['api_calls_saved']} 次")
            print(f"   平均每段: {stats['avg_time_per_segment']:.1f} 秒")
        else:
            print(f"❌ 测试失败: {result['error']}")

        # 显示总体统计
        print(f"\n📊 总体性能统计:")
        print(f"   总缓存命中: {analyzer.stats['cache_hits']}")
        print(f"   总API调用: {analyzer.stats['api_calls']}")
        print(f"   总分段数: {analyzer.stats['total_segments']}")

    except Exception as e:
        print(f"💥 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ultra_optimized())