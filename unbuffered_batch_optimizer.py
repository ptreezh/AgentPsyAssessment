#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无缓冲批量优化器 - 解决输出冲突问题
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time

# 强制无缓冲输出
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 设置环境变量
os.environ['DASHSCOPE_API_KEY'] = 'sk-3f16ac9d87e34ca88bf3925c3651624f'
os.environ['PYTHONUNBUFFERED'] = '1'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class UnbufferedBatchOptimizer:
    def __init__(self, models: List[str] = None):
        self.models = models or ["qwen-max", "deepseek-v3.2-exp", "Moonshot-Kimi-K2-Instruct"]

        # 优化参数 - 5题分段，1秒延迟
        self.segment_size = 5
        self.delay_between_files = 1
        self.delay_between_segments = 1

        # 缓存设置
        self.cache_dir = Path("unbuffered_cache")
        self.cache_dir.mkdir(exist_ok=True)

        # 进度跟踪
        self.progress_file = Path("unbuffered_batch_progress.json")
        self.completed_files = set()
        self.failed_files = set()

        # 性能统计
        self.stats = {
            'start_time': time.time(),
            'files_processed': 0,
            'segments_processed': 0,
            'cache_hits': 0,
            'api_calls': 0,
            'total_processing_time': 0
        }

        print(f"🚀 无缓冲批量优化器已初始化")
        print(f"🤖 使用模型: {', '.join(self.models)}")
        print(f"📊 优化配置: {self.segment_size}题/段, {self.delay_between_files}s延迟")
        print(f"🔑 API密钥已设置")
        sys.stdout.flush()

    def load_progress(self) -> bool:
        """加载进度信息"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    self.completed_files = set(progress.get('completed_files', []))
                    self.failed_files = set(progress.get('failed_files', []))
                    self.stats.update(progress.get('stats', {}))
                    return True
            except Exception as e:
                print(f"❌ 进度加载失败: {e}")
                sys.stdout.flush()
        return False

    def save_progress(self):
        """保存进度信息"""
        try:
            progress = {
                'models': self.models,
                'completed_files': list(self.completed_files),
                'failed_files': list(self.failed_files),
                'stats': self.stats,
                'last_update': datetime.now().isoformat(),
                'total_processed': len(self.completed_files) + len(self.failed_files)
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 进度保存失败: {e}")
            sys.stdout.flush()

    def _create_cache_key(self, questions: List[Dict], model: str) -> str:
        """创建缓存键"""
        content = f"{model}_"
        for q in questions:
            content += f"{q['question'][:50]}_{q['answer'][:50]}_"
        return hashlib.md5(content.encode()).hexdigest()

    def _load_cache(self, cache_key: str) -> Optional[Dict]:
        """加载缓存"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    self.stats['cache_hits'] += 1
                    return result
            except:
                pass
        return None

    def _save_cache(self, cache_key: str, result: Dict):
        """保存缓存"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 缓存保存失败: {e}")
            sys.stdout.flush()

    def _create_segment_prompt(self, questions: List[Dict], segment_num: int) -> str:
        """创建分段分析提示"""
        prompt = f"""请分析以下{len(questions)}个问题和回答，评估Big5人格特质（1-5分）：

"""

        for i, q in enumerate(questions, 1):
            prompt += f"""
问题 {i}: {q['question']}
回答: {q['answer']}
"""

        prompt += f"""

请返回JSON格式：
{{
  "segment_number": {segment_num},
  "questions_count": {len(questions)},
  "scores": {{
    "openness_to_experience": 1-5,
    "conscientiousness": 1-5,
    "extraversion": 1-5,
    "agreeableness": 1-5,
    "neuroticism": 1-5
  }},
  "evidence": {{
    "openness_to_experience": ["具体证据"],
    "conscientiousness": ["具体证据"],
    "extraversion": ["具体证据"],
    "agreeableness": ["具体证据"],
    "neuroticism": ["具体证据"]
  }}
}}

确保每个评分都是1-5的整数，并提供具体的分析证据。"""

        return prompt

    def _analyze_segment(self, questions: List[Dict], segment_num: int, model: str) -> Dict:
        """分析单个分段"""
        self.stats['segments_processed'] += 1

        # 检查缓存
        cache_key = self._create_cache_key(questions, model)
        cached_result = self._load_cache(cache_key)
        if cached_result:
            print(f"  📦 缓存命中: {model} 段{segment_num}")
            sys.stdout.flush()
            return cached_result

        # 执行API调用
        self.stats['api_calls'] += 1
        print(f"  🔍 分析段{segment_num}: {model} ({len(questions)}题)")
        sys.stdout.flush()

        try:
            from enhanced_cloud_analyzer import EnhancedCloudAnalyzer
            analyzer = EnhancedCloudAnalyzer(model=model)

            # 准备segment数据格式
            segment_data = []
            for q in questions:
                segment_data.append({
                    'question': q['question'],
                    'answer': q['answer']
                })

            # 使用analyze_segment方法
            segment_result = analyzer.analyze_segment(segment_data, segment_num)

            # 转换结果格式
            if segment_result.get('success', False):
                result = {
                    'success': True,
                    'segment_number': segment_num,
                    'model': model,
                    'questions_count': len(questions),
                    'scores': segment_result.get('scores', {}),
                    'evidence': segment_result.get('evidence', {})
                }
            else:
                result = {
                    'success': False,
                    'segment_number': segment_num,
                    'model': model,
                    'questions_count': len(questions),
                    'error': segment_result.get('error', '分析失败')
                }

            # 保存缓存
            if result.get('success', False):
                self._save_cache(cache_key, result)

            return result

        except Exception as e:
            error_result = {
                'success': False,
                'segment_number': segment_num,
                'model': model,
                'error': str(e),
                'questions_count': len(questions)
            }
            print(f"  ❌ 分析失败: {model} 段{segment_num} - {e}")
            sys.stdout.flush()
            return error_result

    def _parse_response(self, response: str, segment_num: int, questions_count: int, model: str) -> Dict:
        """解析响应"""
        try:
            import re

            # 提取JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]

                # 清理JSON字符串
                json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                result = json.loads(json_str)

                if 'scores' in result:
                    result['segment_number'] = segment_num
                    result['questions_count'] = questions_count
                    result['model'] = model
                    result['success'] = True

                    # 确保评分在1-5范围内
                    for trait in result['scores']:
                        score = result['scores'][trait]
                        result['scores'][trait] = max(1, min(5, int(score)))

                    return result

        except Exception as e:
            print(f"  ⚠️ 响应解析失败: {e}")
            sys.stdout.flush()

        return {
            'success': False,
            'segment_number': segment_num,
            'model': model,
            'questions_count': questions_count,
            'error': '响应解析失败'
        }

    def analyze_file(self, file_path: Path, output_dir: Path) -> Dict:
        """分析单个文件"""
        start_time = time.time()
        print(f"\n🚀 开始分析: {file_path.name}")
        print(f"📊 配置: {self.segment_size}题/段, {len(self.models)}个模型")
        sys.stdout.flush()

        try:
            # 读取文件，尝试多种编码
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        data = json.load(f)
                except:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = json.load(f)

            # 提取问题 - 适应新的JSON结构
            questions = []

            # 检查是否是新的评估结果格式
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for item in data['assessment_results']:
                    if isinstance(item, dict) and 'question_data' in item:
                        question_data = item['question_data']

                        if isinstance(question_data, dict):
                            # 从question_data中提取问题
                            question_text = question_data.get('prompt_for_agent', question_data.get('mapped_ipip_concept', ''))

                            # 从extracted_response或conversation_log中提取回答
                            answer_text = ''
                            if 'extracted_response' in item and item['extracted_response']:
                                answer_text = item['extracted_response']
                            elif 'conversation_log' in item and isinstance(item['conversation_log'], list):
                                # 从对话日志中提取agent的回答
                                for msg in item['conversation_log']:
                                    if isinstance(msg, dict) and msg.get('role') == 'assistant':
                                        answer_text = msg.get('content', '')
                                        break

                            if question_text and answer_text:
                                questions.append({
                                    'question': question_text,
                                    'answer': answer_text
                                })
            else:
                # 原有的直接格式
                for item in data:
                    if 'question' in item and 'answer' in item:
                        questions.append({
                            'question': item['question'],
                            'answer': item['answer']
                        })

            if not questions:
                return {
                    'success': False,
                    'file': str(file_path),
                    'error': '没有找到有效问题'
                }

            # 创建分段
            segments = []
            for i in range(0, len(questions), self.segment_size):
                segment_questions = questions[i:i + self.segment_size]
                segments.append((i // self.segment_size + 1, segment_questions))

            print(f"📋 {len(questions)}题分为{len(segments)}段")
            sys.stdout.flush()

            # 分析所有模型
            all_results = {}

            for model in self.models:
                print(f"\n🤖 处理模型: {model}")
                sys.stdout.flush()

                model_results = []
                for segment_num, segment_questions in segments:
                    result = self._analyze_segment(segment_questions, segment_num, model)
                    model_results.append(result)

                    # 段间延迟
                    if segment_num < len(segments):
                        time.sleep(self.delay_between_segments)

                all_results[model] = model_results

                # 显示进度
                success_count = len([r for r in model_results if r.get('success', False)])
                print(f"  ✅ {model}: {success_count}/{len(segments)}段成功")
                sys.stdout.flush()

            # 计算最终评分
            final_scores = self._calculate_final_scores(all_results)
            mbti_type = self._calculate_mbti(final_scores)

            # 计算处理时间
            processing_time = time.time() - start_time
            self.stats['total_processing_time'] += processing_time
            self.stats['files_processed'] += 1

            result = {
                'success': True,
                'file': str(file_path),
                'processing_time': processing_time,
                'optimization_info': {
                    'segment_size': self.segment_size,
                    'segments_count': len(segments),
                    'models_count': len(self.models),
                    'original_segments': len(questions) // 2,
                    'optimization_ratio': (len(questions) // 2) / len(segments)
                },
                'final_scores': final_scores,
                'mbti_type': mbti_type,
                'model_results': all_results,
                'performance_stats': {
                    'cache_hit_rate': self.stats['cache_hits'] / max(1, self.stats['segments_processed']) * 100,
                    'avg_time_per_segment': processing_time / (len(segments) * len(self.models)),
                    'files_per_hour': 3600 / processing_time if processing_time > 0 else 0
                }
            }

            # 保存结果
            output_file = output_dir / f"{file_path.stem}_unbuffered_optimized.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 文件分析完成: {output_file}")
            print(f"⏱️  处理时间: {processing_time:.1f}秒")
            print(f"🎯 最终评分: {final_scores}")
            print(f"🧠 MBTI: {mbti_type}")
            print(f"🚀 处理速度: {result['performance_stats']['files_per_hour']:.1f}文件/小时")
            sys.stdout.flush()

            return result

        except Exception as e:
            error_result = {
                'success': False,
                'file': str(file_path),
                'error': str(e),
                'processing_time': time.time() - start_time
            }
            print(f"❌ 文件分析失败: {e}")
            sys.stdout.flush()
            return error_result

    def _calculate_final_scores(self, all_results: Dict) -> Dict:
        """计算最终评分"""
        trait_scores = {}

        for model, results in all_results.items():
            model_trait_scores = {}

            for result in results:
                if result.get('success', False) and 'scores' in result:
                    for trait, score in result['scores'].items():
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

    def run_batch_analysis(self, input_dir: Path, output_dir: Path):
        """运行批量分析"""
        print(f"\n🎯 开始无缓冲批量分析")
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        sys.stdout.flush()

        # 创建输出目录
        output_dir.mkdir(exist_ok=True)

        # 查找输入文件
        json_files = list(input_dir.glob("*.json"))
        if not json_files:
            print("❌ 没有找到JSON文件")
            return

        print(f"📁 找到 {len(json_files)} 个文件")
        sys.stdout.flush()

        # 加载进度
        if self.load_progress():
            print(f"📂 发现进度信息:")
            print(f"   已完成: {len(self.completed_files)} 个文件")
            print(f"   失败: {len(self.failed_files)} 个文件")
            sys.stdout.flush()

        # 过滤待处理文件
        remaining_files = [f for f in json_files if str(f) not in self.completed_files and str(f) not in self.failed_files]

        print(f"📊 剩余待处理: {len(remaining_files)} 个文件")
        sys.stdout.flush()

        if not remaining_files:
            print("✅ 所有文件已处理完成")
            return

        # 处理文件
        total_files = len(remaining_files)
        successful = 0

        for i, file_path in enumerate(remaining_files, 1):
            print(f"\n📈 进度: {i}/{total_files} ({i/total_files*100:.1f}%)")
            sys.stdout.flush()

            result = self.analyze_file(file_path, output_dir)

            if result['success']:
                self.completed_files.add(str(file_path))
                successful += 1
                print(f"✅ 成功处理: {file_path.name}")
            else:
                self.failed_files.add(str(file_path))
                print(f"❌ 处理失败: {file_path.name} - {result.get('error', 'Unknown error')}")

            sys.stdout.flush()

            # 保存进度
            self.save_progress()

            # 文件间延迟
            if i < total_files:
                print(f"⏳ 等待 {self.delay_between_files}s 后处理下一个文件...")
                time.sleep(self.delay_between_files)

        # 生成最终报告
        total_time = time.time() - self.stats['start_time']
        print(f"\n📊 批量分析完成!")
        print(f"✅ 成功: {successful}/{total_files}")
        print(f"⏱️  总耗时: {total_time/3600:.1f} 小时")
        print(f"🚀 平均速度: {successful/(total_time/3600):.1f} 文件/小时")
        print(f"📦 缓存命中率: {self.stats['cache_hits']/max(1, self.stats['segments_processed'])*100:.1f}%")
        print(f"📁 结果保存在: {output_dir}")
        sys.stdout.flush()

def main():
    """主函数"""
    print("🚀 启动无缓冲批量优化器")
    sys.stdout.flush()

    try:
        # 创建优化器
        optimizer = UnbufferedBatchOptimizer()

        # 设置目录
        input_dir = Path("results/results")
        output_dir = Path("unbuffered_optimized_results")

        # 运行分析
        optimizer.run_batch_analysis(input_dir, output_dir)

    except Exception as e:
        print(f"💥 程序失败: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

if __name__ == "__main__":
    main()