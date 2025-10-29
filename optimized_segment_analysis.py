#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的分段分析 - 支持临时文件缓存
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class OptimizedSegmentAnalyzer:
    def __init__(self, model: str = "qwen-max", cache_dir: str = "segment_cache"):
        from enhanced_cloud_analyzer import EnhancedCloudAnalyzer
        self.analyzer = EnhancedCloudAnalyzer(model=model)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, questions_text: str, segment_num: int) -> str:
        """生成分段缓存键"""
        content = f"{questions_text}_{segment_num}_{self.analyzer.model}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cache_file(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"

    def analyze_segment_with_cache(self, questions_text: str, segment_num: int) -> Dict:
        """带缓存的分析分段"""
        cache_key = self._get_cache_key(questions_text, segment_num)
        cache_file = self._get_cache_file(cache_key)

        # 检查缓存
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_result = json.load(f)
                print(f"  📦 使用缓存: 段 {segment_num}")
                return cached_result
            except:
                pass  # 缓存损坏，重新分析

        # 执行分析
        print(f"  🔍 分析段 {segment_num} (2 题)")
        result = self.analyzer._analyze_segment(questions_text, segment_num)

        # 保存到缓存
        if result.get('success', False):
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"  💾 缓存已保存: 段 {segment_num}")
            except Exception as e:
                print(f"  ⚠️  缓存保存失败: {e}")

        return result

    def analyze_file_optimized(self, file_path: Path, output_dir: Path) -> Dict:
        """优化的文件分析"""
        print(f"🚀 优化分析: {file_path.name}")

        try:
            # 读取并预处理文件
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
                    'error': '没有找到有效的问题',
                    'file': str(file_path)
                }

            # 创建分段（每段2个问题）
            segments = []
            for i in range(0, len(questions), 2):
                segment_questions = questions[i:i+2]
                segment_text = f"分析以下问题和回答，评估Big5人格特质：\n\n"
                for j, q in enumerate(segment_questions, 1):
                    segment_text += f"问题{j}: {q['question']}\n回答: {q['answer']}\n\n"
                segments.append(segment_text)

            print(f"📊 总共 {len(questions)} 个问题，分为 {len(segments)} 个分段")

            # 分析分段（使用缓存）
            segment_results = []
            accumulated_scores = {}
            accumulated_evidence = {}

            for i, segment_text in enumerate(segments, 1):
                result = self.analyze_segment_with_cache(segment_text, i)
                segment_results.append(result)

                if result.get('success', False):
                    # 累积评分
                    if 'scores' in result:
                        for trait, score in result['scores'].items():
                            if trait not in accumulated_scores:
                                accumulated_scores[trait] = []
                            accumulated_scores[trait].append(score)

                    # 累积证据
                    if 'evidence' in result:
                        for trait, evidence_list in result['evidence'].items():
                            if trait not in accumulated_evidence:
                                accumulated_evidence[trait] = []
                            accumulated_evidence[trait].extend(evidence_list)

                    print(f"  ✅ 段 {i} 分析成功")
                else:
                    print(f"  ❌ 段 {i} 分析失败: {result.get('error', 'Unknown')}")

            # 计算最终评分
            final_scores = {}
            for trait, scores in accumulated_scores.items():
                if scores:
                    final_scores[trait] = round(sum(scores) / len(scores))
                else:
                    final_scores[trait] = 3

            # 生成摘要
            summary = {
                'file_info': {
                    'filename': file_path.name,
                    'total_questions': len(questions),
                    'total_segments': len(segments),
                    'successful_segments': len([r for r in segment_results if r.get('success', False)]),
                    'model': self.analyzer.model
                },
                'final_scores': final_scores,
                'accumulated_evidence': accumulated_evidence,
                'segment_results': segment_results,
                'cache_stats': {
                    'cache_dir': str(self.cache_dir),
                    'cached_files': len(list(self.cache_dir.glob("*.json")))
                }
            }

            # 保存结果
            output_file = output_dir / f"{file_path.stem}_optimized_summary.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            print(f"✅ 优化分析完成: {output_file}")
            print(f"📊 成功率: {summary['file_info']['successful_segments']}/{len(segments)} ({summary['file_info']['successful_segments']/len(segments)*100:.1f}%)")
            print(f"📦 缓存文件数: {summary['cache_stats']['cached_files']}")

            return {
                'success': True,
                'file': str(file_path),
                'summary': summary,
                'output_file': str(output_file)
            }

        except Exception as e:
            return {
                'success': False,
                'file': str(file_path),
                'error': str(e)
            }

def test_optimized_analysis():
    print("🚀 测试优化分段分析...")

    try:
        # 创建优化分析器
        analyzer = OptimizedSegmentAnalyzer(model="qwen-max")

        # 查找测试文件
        results_dir = Path("results/results")
        json_files = list(results_dir.glob("*.json"))

        if not json_files:
            print("❌ 没有找到测试文件")
            return

        # 选择一个未处理的文件测试
        test_file = json_files[5] if len(json_files) > 5 else json_files[0]
        print(f"📁 测试文件: {test_file.name}")

        # 创建输出目录
        output_dir = Path("optimized_test_results")
        output_dir.mkdir(exist_ok=True)

        # 记录时间
        import time
        start_time = time.time()

        # 执行优化分析
        result = analyzer.analyze_file_optimized(test_file, output_dir)

        elapsed_time = time.time() - start_time
        print(f"⏱️  优化分析耗时: {elapsed_time:.1f} 秒")

        if result['success']:
            print(f"✅ 优化分析成功!")
            success_rate = result['summary']['file_info']['successful_segments'] / result['summary']['file_info']['total_segments'] * 100
            print(f"   成功率: {success_rate:.1f}%")
            print(f"   缓存文件数: {result['summary']['cache_stats']['cached_files']}")
        else:
            print(f"❌ 优化分析失败: {result['error']}")

    except Exception as e:
        print(f"💥 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_optimized_analysis()