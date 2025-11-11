#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Fallback 批量处理器 - 企业级高可用批量测评报告处理
集成三层fallback策略：Ollama Cloud → OpenRouter → Local模型
支持断点续跑、超时保护、性能监控、智能故障转移
"""

import sys
import os
import json
import re
import asyncio
from pathlib import Path
from datetime import datetime
import time
import argparse
import logging
import pickle
from typing import List, Dict, Any, Tuple, Optional
import traceback

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_report_pipeline import TransparentPipeline
from cloud_fallback_manager import CloudFallbackManager
from fallback_performance_monitor import PerformanceOptimizedFallbackManager


class CloudFallbackBatchProcessor:
    """Cloud Fallback批量处理器 - 企业级高可用批量测评报告处理"""

    def __init__(self, input_dir: str, output_dir: str,
                 max_evaluators: int = 3,
                 use_enhanced: bool = False,
                 use_cloud_fallback: bool = True,
                 performance_monitoring: bool = True):
        """
        初始化Cloud Fallback批处理器

        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
            max_evaluators: 最大评估器数量
            use_enhanced: 是否使用增强流水线
            use_cloud_fallback: 是否启用Cloud Fallback
            performance_monitoring: 是否启用性能监控
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_evaluators = max_evaluators
        self.use_enhanced = use_enhanced
        self.use_cloud_fallback = use_cloud_fallback
        self.performance_monitoring = performance_monitoring

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 检查点文件路径
        self.checkpoint_file = self.output_dir / "cloud_fallback_batch_checkpoint.pkl"
        self.results_file = self.output_dir / "cloud_fallback_batch_results.json"
        self.summary_file = self.output_dir / "cloud_fallback_batch_summary.md"
        self.log_file = self.output_dir / "cloud_fallback_batch_processing.log"
        self.performance_file = self.output_dir / "performance_dashboard.json"

        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 初始化Cloud Fallback管理器
        if use_cloud_fallback:
            if performance_monitoring:
                self.fallback_manager = PerformanceOptimizedFallbackManager()
                self.logger.info("🚀 启用Cloud Fallback + 性能监控")
            else:
                self.fallback_manager = CloudFallbackManager()
                self.logger.info("☁️ 启用Cloud Fallback")
        else:
            # 回退到本地流水线
            from single_report_pipeline.transparent_pipeline import TransparentPipeline
            self.fallback_manager = None
            self.pipeline = TransparentPipeline(use_cloud=False)
            self.logger.info("🏠 使用本地流水线")

        # 初始化状态
        self.processed_files = set()
        self.results = []
        self.start_time = datetime.now()
        self.total_files = 0
        self.current_file_index = 0

        # 性能优化参数
        self.timeout_per_question = 300  # 5分钟超时
        self.retry_count = 2  # 重试次数

        # 问题报告筛选参数
        self.problem_reports_dir = self.output_dir / "problem_reports"
        self.problem_reports_dir.mkdir(exist_ok=True)
        self.problem_reports_count = 0

        # 初始化问题报告识别模式
        self._init_problem_patterns()

        # Cloud Fallback统计
        self.cloud_fallback_stats = {
            'ollama_cloud_usage': 0,
            'openrouter_usage': 0,
            'local_usage': 0,
            'fallback_chain_usage': [],
            'total_questions_processed': 0,
            'failed_questions': 0
        }

    def _init_problem_patterns(self):
        """初始化问题报告识别模式"""
        self.problem_patterns = [
            # 英文问题模式
            r'please provide me with the prompt',
            r'please provide me with a prompt',
            r'please provide me with a prompt so I can assist you',
            r'as an ai language model',
            r'i don\'t have personal information',
            r'i cannot answer',
            r'i\'m not able to',
            r'i am not able to',
            r'i\'m not sure what',
            r'i cannot provide',
            r'i don\'t have access to',
            r'i don\'t have enough information',
            r'i don\'t have enough context',
            r'i don\'t understand the question',
            r'i don\'t know what',
            r'i\'m not sure what you mean',
            r'i\'m not sure i understand',
            r'as an ai assistant',
            r'as a language model',
            r'i am an ai',
            r'i\'m an ai',
            r'i\'m not human',
            r'i don\'t have personal experiences',
            r'i cannot answer from personal experience',
            r'i don\'t have access to real-time information',
            r'i don\'t have access to current information',
            r'i don\'t have access to external information',
            r'i cannot browse the internet',
            r'i don\'t have access to the internet',
            r'i don\'t have access to external data',
            r'i don\'t have access to external sources',
            r'i don\'t have access to external resources',
            r'i don\'t have access to any external information',
            r'i don\'t have access to any external data',
            r'i don\'t have access to any external sources',
            r'i don\'t have access to any external resources',

            # 中文问题模式
            r'请提供给我提示词',
            r'请提供给我提示',
            r'请提供提示词',
            r'作为一个人工智能语言模型',
            r'作为一个人工智能助手',
            r'我没有个人信息',
            r'我无法回答',
            r'我不能回答',
            r'我不能提供',
            r'我没有访问权限',
            r'我没有足够的信息',
            r'我没有足够的上下文',
            r'我不理解这个问题',
            r'我不知道什么',
            r'我不确定你的意思',
            r'我不确定我理解',
            r'我是一个人工智能',
            r'我不是人类',
            r'我没有个人经历',
            r'我无法从个人经历回答',
            r'我没有实时信息访问权限',
            r'我没有当前信息访问权限',
            r'我没有外部信息访问权限',
            r'我无法浏览互联网',
            r'我没有互联网访问权限',
            r'我没有外部数据访问权限',
            r'我没有外部来源访问权限',
            r'我没有外部资源访问权限',

            # 拒绝回答模式
            r'i cannot answer questions',
            r'i cannot provide information',
            r'i cannot provide details',
            r'i cannot provide specific information',
            r'i cannot provide personal information',
            r'i cannot provide medical advice',
            r'i cannot provide legal advice',
            r'i cannot provide financial advice',
            r'i cannot provide professional advice',
            r'我无法回答问题',
            r'我无法提供信息',
            r'我无法提供详细信息',
            r'我无法提供具体信息',
            r'我无法提供个人信息',
            r'我无法提供医疗建议',
            r'我无法提供法律建议',
            r'我无法提供金融建议',
            r'我无法提供专业建议',

            # 系统消息模式
            r'system message',
            r'system prompt',
            r'role: system',
            r'"role": "system"',
            r'\\[system\\]',
            r'\\[system prompt\\]',
            r'系统消息',
            r'系统提示',
            r'角色: 系统',
            r'"角色": "系统"',

            # 无效回答模式
            r'the question is incomplete',
            r'the question is unclear',
            r'the question is ambiguous',
            r'这个问题不完整',
            r'这个问题不清楚',
            r'这个问题模糊',
            r'answer the question',
            r'回答这个问题',
            r'please answer',
            r'请回答',

            # 错误消息模式
            r'an error occurred',
            r'something went wrong',
            r'there was an error',
            r'发生错误',
            r'出现了问题',
            r'发生了错误',
            r'处理失败',
            r'evaluation failed',
            r'评估失败'
        ]

    def _is_problem_report(self, file_path: Path) -> Tuple[bool, str]:
        """
        检查是否为问题报告

        Args:
            file_path: 文件路径

        Returns:
            (is_problem, reason): 是否问题报告及原因
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # 检查问题模式
            for pattern in self.problem_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True, f"匹配问题模式: {pattern[:50]}..."

            # 检查回答数量（50题文件必须有50个回答）
            answer_count = content.count('"answer":')
            question_count = content.count('"question_id"')

            if question_count == 50:  # 50题文件
                if answer_count < 45:  # 允许最多缺失5个答案
                    return True, f"回答数量不足: {answer_count}/50"
            elif question_count == 240:  # 240题文件
                if answer_count < 220:  # 允许最多缺失20个答案
                    return True, f"回答数量不足: {answer_count}/240"

            return False, ""

        except Exception as e:
            return True, f"文件读取错误: {str(e)}"

    def _find_valid_files(self) -> List[Path]:
        """
        查找有效的测评报告文件

        Returns:
            有效文件列表
        """
        json_files = list(self.input_dir.glob("*.json"))
        valid_files = []
        problem_files = []

        self.logger.info(f"📂 找到 {len(json_files)} 个测评报告文件")

        for file_path in json_files:
            is_problem, reason = self._is_problem_report(file_path)

            if is_problem:
                problem_files.append((file_path, reason))
                self.problem_reports_count += 1

                # 移动问题报告到问题报告目录
                problem_dest = self.problem_reports_dir / file_path.name
                try:
                    import shutil
                    shutil.move(str(file_path), str(problem_dest))
                    self.logger.warning(f"🚩 问题报告已移动: {file_path.name} - {reason}")
                except Exception as e:
                    self.logger.error(f"❌ 移动问题报告失败: {file_path.name} - {e}")
            else:
                valid_files.append(file_path)

        # 记录问题报告统计
        if problem_files:
            self.logger.info(f"🚩 识别出 {len(problem_files)} 个问题报告")
            for file_path, reason in problem_files[:10]:  # 只显示前10个
                self.logger.warning(f"    📄 {file_path.name}: {reason}")
            if len(problem_files) > 10:
                self.logger.warning(f"    ... 还有 {len(problem_files) - 10} 个问题报告")

        self.logger.info(f"✅ 找到 {len(valid_files)} 个有效报告文件")

        return valid_files

    async def _process_single_question_with_fallback(self, question: Dict, question_index: int) -> Dict[str, Any]:
        """
        使用Cloud Fallback处理单个问题

        Args:
            question: 问题数据
            question_index: 问题索引

        Returns:
            处理结果
        """
        try:
            if self.use_cloud_fallback and self.fallback_manager:
                # 使用Cloud Fallback处理
                model_family = self._determine_model_family(question)

                prompt = question.get('answer', '')
                context = {
                    'question_id': question.get('question_id', f'Q{question_index}'),
                    'concept': question.get('concept', ''),
                    'is_reversed': question.get('is_reversed', False)
                }

                # 记录fallback链使用情况
                fallback_chain_used = []

                result = await self.fallback_manager.evaluate_with_fallback(
                    model_family=model_family,
                    prompt=prompt,
                    context=context
                )

                # 更新统计信息
                self.cloud_fallback_stats['total_questions_processed'] += 1

                if result.success:
                    # 记录提供商使用情况
                    provider_key = f"{result.provider.value}:{result.model_name}"
                    fallback_chain_used.append(provider_key)

                    if result.provider.value == 'ollama_cloud':
                        self.cloud_fallback_stats['ollama_cloud_usage'] += 1
                    elif result.provider.value == 'openrouter':
                        self.cloud_fallback_stats['openrouter_usage'] += 1
                    elif result.provider.value == 'local':
                        self.cloud_fallback_stats['local_usage'] += 1

                    self.cloud_fallback_stats['fallback_chain_usage'].append(fallback_chain_used)

                    # 转换为统一格式
                    final_scores = result.scores
                    reliability = 0.8  # 基础可靠性

                    # 获取详细的可靠性信息（如果可用）
                    if hasattr(result, 'metadata') and result.metadata:
                        reliability = result.metadata.get('reliability', 0.8)

                    return {
                        'success': True,
                        'question_id': question.get('question_id', f'Q{question_index}'),
                        'question_index': question_index,
                        'final_scores': final_scores,
                        'reliability': reliability,
                        'provider': result.provider.value,
                        'model_name': result.model_name,
                        'response_time': result.response_time,
                        'fallback_chain': fallback_chain_used,
                        'error_message': None
                    }
                else:
                    # Fallback失败
                    self.cloud_fallback_stats['failed_questions'] += 1
                    return {
                        'success': False,
                        'question_id': question.get('question_id', f'Q{question_index}'),
                        'question_index': question_index,
                        'final_scores': {},
                        'reliability': 0.0,
                        'provider': 'none',
                        'model_name': 'none',
                        'response_time': 0.0,
                        'fallback_chain': [],
                        'error_message': result.error_message
                    }
            else:
                # 使用本地流水线
                result = self.pipeline.process_single_question(question, question_index)
                return result

        except Exception as e:
            self.logger.error(f"❌ 处理问题 {question_index} 失败: {e}")
            self.cloud_fallback_stats['failed_questions'] += 1

            return {
                'success': False,
                'question_id': question.get('question_id', f'Q{question_index}'),
                'question_index': question_index,
                'final_scores': {},
                'reliability': 0.0,
                'provider': 'error',
                'model_name': 'error',
                'response_time': 0.0,
                'fallback_chain': [],
                'error_message': str(e)
            }

    def _determine_model_family(self, question: Dict) -> str:
        """
        根据问题确定模型家族

        Args:
            question: 问题数据

        Returns:
            模型家族 ('qwen' 或 'deepseek')
        """
        # 基于问题ID或内容选择模型家族
        question_id = question.get('question_id', '')

        # 简单的轮询策略
        if question_id.startswith(('E', 'I')):  # Extraversion, Intellect
            return 'qwen'
        elif question_id.startswith(('A', 'C', 'N')):  # Agreeableness, Conscientiousness, Neuroticism
            return 'deepseek'
        else:
            # 默认轮询
            import random
            return random.choice(['qwen', 'deepseek'])

    async def _process_file_with_fallback(self, file_path: Path) -> Dict[str, Any]:
        """
        使用Cloud Fallback处理单个文件

        Args:
            file_path: 文件路径

        Returns:
            处理结果
        """
        try:
            self.logger.info(f"🔍 Cloud Fallback处理: {file_path.name}")

            # 解析输入文件
            from single_report_pipeline.input_parser import InputParser
            parser = InputParser()
            questions = parser.parse_assessment_json(str(file_path))

            self.logger.info(f"   题目总数: {len(questions)} (全部处理)")

            # 处理所有问题
            results = []
            successful_questions = 0
            total_reliability = 0.0

            for i, question in enumerate(questions):
                self.logger.info(f"   处理题目 {i+1}/{len(questions)}: {question.get('question_id', i)}")

                try:
                    # 处理单个问题
                    result = await self._process_single_question_with_fallback(question, i)

                    if result['success']:
                        successful_questions += 1
                        total_reliability += result['reliability']

                        # 记录处理信息
                        provider_info = f"{result['provider']}:{result['model_name']}"
                        fallback_info = " → ".join(result['fallback_chain']) if result['fallback_chain'] else provider_info

                        self.logger.info(f"      ✅ 完成 - 可靠性: {result['reliability']:.3f}, "
                                       f"模型: {fallback_info}, "
                                       f"响应时间: {result['response_time']:.2f}s")
                    else:
                        self.logger.warning(f"      ❌ 失败 - {result['error_message']}")

                    results.append(result)

                except Exception as e:
                    self.logger.error(f"      ❌ 异常 - {e}")
                    results.append({
                        'success': False,
                        'question_id': question.get('question_id', i),
                        'question_index': i,
                        'error_message': str(e)
                    })

            # 计算文件级别的统计
            avg_reliability = total_reliability / successful_questions if successful_questions > 0 else 0.0
            success_rate = successful_questions / len(questions) if questions else 0.0

            # 生成文件评估结果
            file_result = {
                'file_name': file_path.name,
                'total_questions': len(questions),
                'successful_questions': successful_questions,
                'failed_questions': len(questions) - successful_questions,
                'success_rate': success_rate,
                'average_reliability': avg_reliability,
                'processing_time': (datetime.now() - self.start_time).total_seconds(),
                'cloud_fallback_stats': {
                    'ollama_cloud_usage': self.cloud_fallback_stats['ollama_cloud_usage'],
                    'openrouter_usage': self.cloud_fallback_stats['openrouter_usage'],
                    'local_usage': self.cloud_fallback_stats['local_usage'],
                    'total_questions': self.cloud_fallback_stats['total_questions_processed'],
                    'failed_questions': self.cloud_fallback_stats['failed_questions']
                },
                'questions': results,
                'timestamp': datetime.now().isoformat()
            }

            # 保存文件结果
            output_file = self.output_dir / f"{file_path.stem}_cloud_fallback_evaluation.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"   📊 文件处理完成: {successful_questions}/{len(questions)} 成功, "
                           f"平均可靠性: {avg_reliability:.3f}")

            return file_result

        except Exception as e:
            self.logger.error(f"❌ 文件处理失败 {file_path.name}: {e}")
            return {
                'file_name': file_path.name,
                'success': False,
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def process_batch_async(self):
        """异步批量处理"""
        try:
            self.logger.info("🚀 Cloud Fallback批量测评报告处理器")
            self.logger.info("=" * 80)
            self.logger.info(f"输入目录: {self.input_dir}")
            self.logger.info(f"输出目录: {self.output_dir}")
            self.logger.info(f"处理参数: 全部题目处理, 最大{self.max_evaluators}个评估器")
            self.logger.info(f"算法选择: Cloud Fallback {'(增强模式)' if self.use_enhanced else ''}")

            # 加载检查点
            if self._load_checkpoint():
                self.logger.info(f"📂 从检查点恢复: 已处理 {len(self.processed_files)} 个文件")
            else:
                self.logger.info("ℹ️  未找到检查点文件")

            # 查找有效文件
            valid_files = self._find_valid_files()
            self.total_files = len(valid_files)

            self.logger.info(f"   已处理: {len(self.processed_files)} 个")
            self.logger.info(f"   剩余: {self.total_files} 个")

            if not valid_files:
                self.logger.warning("⚠️  没有找到有效文件")
                return

            # 过滤已处理文件
            remaining_files = [f for f in valid_files if f.name not in self.processed_files]

            if not remaining_files:
                self.logger.info("✅ 所有文件已处理完成")
                return

            self.logger.info("")
            self.logger.info(f"▶️  从第 {len(self.processed_files) + 1} 个文件开始处理")
            self.logger.info("")

            # 处理剩余文件
            for i, file_path in enumerate(remaining_files):
                self.current_file_index = len(self.processed_files) + i + 1

                self.logger.info(f"📁 进度: {self.current_file_index}/{self.total_files} 文件")

                try:
                    # 处理文件
                    result = await self._process_file_with_fallback(file_path)
                    self.results.append(result)

                    # 记录已处理文件
                    self.processed_files.add(file_path.name)

                    # 保存检查点
                    self._save_checkpoint()

                    # 清理临时变量
                    import gc
                    gc.collect()

                except Exception as e:
                    self.logger.error(f"❌ 文件处理异常 {file_path.name}: {e}")
                    traceback.print_exc()
                    continue

            # 生成最终报告
            self._generate_final_report()

            # 生成性能报告（如果启用性能监控）
            if self.performance_monitoring and hasattr(self.fallback_manager, 'get_performance_dashboard'):
                self._generate_performance_report()

            self.logger.info("")
            self.logger.info("🎉 Cloud Fallback批量处理完成！")

        except Exception as e:
            self.logger.error(f"❌ 批量处理失败: {e}")
            traceback.print_exc()

    def _load_checkpoint(self) -> bool:
        """加载检查点"""
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint = pickle.load(f)
                    self.processed_files = checkpoint.get('processed_files', set())
                    self.results = checkpoint.get('results', [])
                    self.start_time = checkpoint.get('start_time', self.start_time)
                    return True
        except Exception as e:
            self.logger.warning(f"⚠️  加载检查点失败: {e}")
        return False

    def _save_checkpoint(self):
        """保存检查点"""
        try:
            checkpoint = {
                'processed_files': self.processed_files,
                'results': self.results,
                'start_time': self.start_time,
                'cloud_fallback_stats': self.cloud_fallback_stats
            }
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint, f)
        except Exception as e:
            self.logger.error(f"❌ 保存检查点失败: {e}")

    def _generate_final_report(self):
        """生成最终报告"""
        try:
            # 统计信息
            successful_files = [r for r in self.results if r.get('success', True)]
            total_questions = sum(r.get('total_questions', 0) for r in successful_files)
            successful_questions = sum(r.get('successful_questions', 0) for r in successful_files)

            avg_reliability = sum(r.get('average_reliability', 0) for r in successful_files) / len(successful_files) if successful_files else 0

            processing_time = (datetime.now() - self.start_time).total_seconds()

            # Cloud Fallback统计
            cloud_usage = self.cloud_fallback_stats['ollama_cloud_usage']
            openrouter_usage = self.cloud_fallback_stats['openrouter_usage']
            local_usage = self.cloud_fallback_stats['local_usage']
            total_processed = self.cloud_fallback_stats['total_questions_processed']

            # 生成报告内容
            report_content = f"""# Cloud Fallback批量处理报告

## 处理概览
- **处理时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **总耗时**: {processing_time:.2f} 秒
- **输入目录**: {self.input_dir}
- **输出目录**: {self.output_dir}

## 文件处理统计
- **总文件数**: {self.total_files}
- **成功处理**: {len(successful_files)}
- **处理失败**: {self.total_files - len(successful_files)}
- **成功率**: {len(successful_files)/self.total_files:.1%}

## 问题报告筛选
- **问题报告数**: {self.problem_reports_count}
- **有效报告数**: {self.total_files}
- **筛选通过率**: {self.total_files/(self.total_files + self.problem_reports_count):.1%}

## 题目处理统计
- **总题目数**: {total_questions}
- **成功处理**: {successful_questions}
- **处理失败**: {total_questions - successful_questions}
- **题目成功率**: {successful_questions/total_questions:.1%}
- **平均可靠性**: {avg_reliability:.3f}

## Cloud Fallback使用统计
- **Ollama Cloud使用**: {cloud_usage} 次 ({cloud_usage/total_processed:.1%})
- **OpenRouter使用**: {openrouter_usage} 次 ({openrouter_usage/total_processed:.1%})
- **本地模型使用**: {local_usage} 次 ({local_usage/total_processed:.1%})
- **总处理题目**: {total_processed}
- **失败题目**: {self.cloud_fallback_stats['failed_questions']}

## 性能指标
- **平均处理速度**: {total_questions/processing_time:.2f} 题目/秒
- **平均文件处理时间**: {processing_time/len(successful_files):.2f} 秒/文件

## 配置信息
- **Cloud Fallback**: {'启用' if self.use_cloud_fallback else '禁用'}
- **性能监控**: {'启用' if self.performance_monitoring else '禁用'}
- **增强算法**: {'启用' if self.use_enhanced else '禁用'}
- **最大评估器数**: {self.max_evaluators}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            # 保存Markdown报告
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

            # 保存JSON结果
            summary_data = {
                'processing_overview': {
                    'start_time': self.start_time.isoformat(),
                    'total_processing_time': processing_time,
                    'input_directory': str(self.input_dir),
                    'output_directory': str(self.output_dir)
                },
                'file_statistics': {
                    'total_files': self.total_files,
                    'successful_files': len(successful_files),
                    'failed_files': self.total_files - len(successful_files),
                    'success_rate': len(successful_files) / self.total_files
                },
                'problem_report_filtering': {
                    'problem_reports': self.problem_reports_count,
                    'valid_reports': self.total_files,
                    'filter_pass_rate': self.total_files / (self.total_files + self.problem_reports_count)
                },
                'question_statistics': {
                    'total_questions': total_questions,
                    'successful_questions': successful_questions,
                    'failed_questions': total_questions - successful_questions,
                    'question_success_rate': successful_questions / total_questions,
                    'average_reliability': avg_reliability
                },
                'cloud_fallback_statistics': self.cloud_fallback_stats,
                'performance_metrics': {
                    'average_processing_speed': total_questions / processing_time,
                    'average_file_processing_time': processing_time / len(successful_files)
                },
                'configuration': {
                    'cloud_fallback_enabled': self.use_cloud_fallback,
                    'performance_monitoring_enabled': self.performance_monitoring,
                    'enhanced_algorithm_enabled': self.use_enhanced,
                    'max_evaluators': self.max_evaluators
                },
                'results': self.results,
                'generation_time': datetime.now().isoformat()
            }

            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📊 报告已保存:")
            self.logger.info(f"   📄 Markdown: {self.summary_file}")
            self.logger.info(f"   📊 JSON: {self.results_file}")

        except Exception as e:
            self.logger.error(f"❌ 生成报告失败: {e}")

    def _generate_performance_report(self):
        """生成性能监控报告"""
        try:
            if hasattr(self.fallback_manager, 'get_performance_dashboard'):
                dashboard = self.fallback_manager.get_performance_dashboard()

                with open(self.performance_file, 'w', encoding='utf-8') as f:
                    json.dump(dashboard, f, indent=2, ensure_ascii=False)

                self.logger.info(f"📈 性能仪表板: {self.performance_file}")

                # 记录关键性能指标
                if 'overall_performance' in dashboard:
                    overall = dashboard['overall_performance']
                    self.logger.info(f"   📊 成功率: {overall['success_rate']:.1%}")
                    self.logger.info(f"   ⚡ 平均速度: {overall['requests_per_minute']:.1f} 请求/分钟")

                if 'health_scores' in dashboard:
                    self.logger.info(f"   💓 提供商健康评分已生成")

                if 'recommendations' in dashboard:
                    recommendations = dashboard['recommendations']
                    self.logger.info(f"   💡 优化建议: {len(recommendations)} 条")

        except Exception as e:
            self.logger.error(f"❌ 生成性能报告失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Cloud Fallback批量测评报告处理器')
    parser.add_argument('--input-dir', required=True, help='输入目录路径')
    parser.add_argument('--output-dir', required=True, help='输出目录路径')
    parser.add_argument('--max-evaluators', type=int, default=3, help='最大评估器数量')
    parser.add_argument('--enhanced', action='store_true', help='使用增强算法')
    parser.add_argument('--no-cloud-fallback', action='store_true', help='禁用Cloud Fallback')
    parser.add_argument('--no-performance-monitoring', action='store_true', help='禁用性能监控')

    args = parser.parse_args()

    # 创建处理器
    processor = CloudFallbackBatchProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        max_evaluators=args.max_evaluators,
        use_enhanced=args.enhanced,
        use_cloud_fallback=not args.no_cloud_fallback,
        performance_monitoring=not args.no_performance_monitoring
    )

    # 运行异步处理
    asyncio.run(processor.process_batch_async())


if __name__ == '__main__':
    main()