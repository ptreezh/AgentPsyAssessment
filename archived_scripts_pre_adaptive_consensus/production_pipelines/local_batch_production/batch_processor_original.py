#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理器 - 高效稳定的批量测评报告处理
支持50题文件、断点续跑、超时保护、增强算法
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime
import time
import argparse
import logging
import pickle
from typing import List, Dict, Any, Tuple

# 添加包目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_report_pipeline import TransparentPipeline


class BatchProcessor:
    """批量处理器 - 高效稳定的批量测评报告处理"""

    def __init__(self, input_dir: str, output_dir: str,
                 max_evaluators: int = 3,
                 use_enhanced: bool = False):
        """
        初始化批处理器

        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
            max_evaluators: 最大评估器数量
            use_enhanced: 是否使用增强流水线
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_evaluators = max_evaluators
        self.use_enhanced = use_enhanced

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 检查点文件路径
        self.checkpoint_file = self.output_dir / "batch_checkpoint.pkl"
        self.results_file = self.output_dir / "batch_results.json"
        self.summary_file = self.output_dir / "batch_summary.md"
        self.log_file = self.output_dir / "batch_processing.log"

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

        # 初始化流水线
        if use_enhanced:
            from single_report_pipeline.enhanced_transparent_pipeline import EnhancedTransparentPipeline
            self.pipeline = EnhancedTransparentPipeline(use_cloud=False)
            self.logger.info("✅ 使用增强流水线（新算法）")
        else:
            self.pipeline = TransparentPipeline(use_cloud=False)
            self.logger.info("✅ 使用原流水线")

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

    def _init_problem_patterns(self):
        """初始化问题报告识别模式"""
        self.problem_patterns = [
            # 英文问题模式
            r'please provide me with the prompt',
            r'please provide me with a prompt',
            r'please provide me with a prompt so I can assist you',
            r'please provide me with a prompt so I can help you',
            r'can you give me the prompt',
            r'what is the prompt',
            r'please provide the prompt',
            r'can i see the prompt',
            r'i need the prompt',
            r'what should i do',
            r'tell me what to do',
            r'please give me instructions',
            r'what task should i perform',
            r'i\'m ready for any task',
            r'ready for any task',
            r'please provide the question',
            r'what is the question',
            r'can you provide the question',
            r'so I can assist you',
            r'so I can help you',
            r'I\'m ready for any task, question or creative',
            r'I\'m ready for any task, question or creative writing',

            # 中文问题模式
            r'请提供提示词',
            r'请提供题目',
            r'请给出问题',
            r'请给出提示词',
            r'我没有看到题目',
            r'没有看到问题',
            r'请告诉我问题',
            r'可以告诉我问题是什么吗',
            r'能告诉我问题是什么吗',
            r'需要提示词',
            r'请提供具体问题',
            r'请说明任务',
            r'我应该做什么',
            r'请提供具体要求',

            # 模糊问题模式
            r'no prompt',
            r'no question',
            r'no instructions',
            r'missing prompt',
            r'missing question',
            r'没有提示词',
            r'没有问题',
            r'没有题目',
            r'缺少提示词',
            r'缺少问题',

            # 系统回应模式
            r'i am an ai',
            r'i\'m an ai',
            r'i am a language model',
            r'i\'m a language model',
            r'i cannot provide',
            r'i cannot answer',
            r'as an ai',
            r'as an assistant',

            # 角色扮演和不相关回答模式
            r'什么问题',
            r'请描述一下',
            r'请说明',
            r'能详细说明',
            r'可以详细描述',
            r'具体是什么',
            r'请提供具体',
            r'请更详细',
            r'需要更多信息',
            r'能详细解释',
            r'请详细解释',

            # 括号动作描述模式 (角色扮演)
            r'（.*?）',
            r'\(.*?\)',
            r'\【.*?\】',
            r'\[.*?\]',

            # 通用无意义回应
            r'好的，明白了',
            r'了解了',
            r'收到',
            r'知道了',
            r'嗯，好的',
            r'好的，请说',
            r'请继续',
            r'请讲',
        ]

        # 编译正则表达式模式
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL)
                                 for pattern in self.problem_patterns]

    def check_problem_response(self, response_text: str) -> bool:
        """检查单个回答是否为问题回答"""
        if not response_text or not isinstance(response_text, str):
            return False

        # 检查是否匹配任何问题模式
        for pattern in self.compiled_patterns:
            if pattern.search(response_text):
                return True

        # 检查过短回答
        if len(response_text.strip()) < 10:
            return True

        # 检查是否只是标点符号
        if re.match(r'^[?.!]+$', response_text.strip()):
            return True

        return False

    def is_problem_report(self, file_path: str) -> Tuple[bool, str]:
        """
        检查是否为问题测评报告

        Args:
            file_path: 文件路径

        Returns:
            (is_problem, reason): 是否为问题报告, 原因
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            assessment_results = report_data.get('assessment_results', [])
            if not assessment_results:
                return True, "empty_assessment_results"

            total_questions = len(assessment_results)
            problem_responses = 0

            for result in assessment_results:
                extracted_response = result.get('extracted_response', '')
                if self.check_problem_response(extracted_response):
                    problem_responses += 1

            # 如果超过30%的回答都是问题回答，则标记为问题报告
            problem_ratio = problem_responses / total_questions
            if problem_ratio >= 0.3:
                reason = f"问题回答比例: {problem_responses}/{total_questions} ({problem_ratio:.1%})"
                return True, reason

            return False, ""

        except Exception as e:
            return True, f"检查失败: {str(e)}"

    def handle_problem_report(self, file_path: Path, reason: str):
        """处理问题测评报告"""
        try:
            # 复制文件到问题报告目录
            problem_file = self.problem_reports_dir / file_path.name
            import shutil
            shutil.copy2(file_path, problem_file)

            # 保存问题详情
            detail_file = self.problem_reports_dir / f"{file_path.stem}_problem_details.txt"
            with open(detail_file, 'w', encoding='utf-8') as f:
                f.write(f"文件: {file_path.name}\n")
                f.write(f"问题原因: {reason}\n")
                f.write(f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            self.problem_reports_count += 1
            self.logger.warning(f"🚩 问题报告已标记: {file_path.name} - {reason}")

        except Exception as e:
            self.logger.error(f"❌ 处理问题报告失败 {file_path.name}: {e}")

    def load_checkpoint(self):
        """加载检查点"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)

                self.processed_files = set(checkpoint_data.get('processed_files', []))
                self.results = checkpoint_data.get('results', [])
                self.start_time = checkpoint_data.get('start_time', datetime.now())
                self.total_files = checkpoint_data.get('total_files', 0)
                self.current_file_index = checkpoint_data.get('current_file_index', 0)

                self.logger.info(f"✅ 已加载检查点: 处理了 {len(self.processed_files)} 个文件")
                return True
            except Exception as e:
                self.logger.warning(f"⚠️  加载检查点失败: {e}")
                return False
        else:
            self.logger.info("ℹ️  未找到检查点文件")
            return False

    def save_checkpoint(self):
        """保存检查点"""
        checkpoint_data = {
            'processed_files': list(self.processed_files),
            'results': self.results,
            'start_time': self.start_time,
            'total_files': self.total_files,
            'current_file_index': self.current_file_index
        }

        try:
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            self.logger.info(f"💾 检查点已保存: {len(self.processed_files)} 个文件")
        except Exception as e:
            self.logger.error(f"❌ 保存检查点失败: {e}")

    def process_single_file_optimized(self, file_path: str) -> Dict[str, Any]:
        """
        优化的单文件处理

        Args:
            file_path: 文件路径

        Returns:
            处理结果
        """
        self.logger.info(f"🔍 优化处理: {Path(file_path).name}")

        start_time = time.time()

        try:
            # 解析文件
            from single_report_pipeline.input_parser import InputParser
            parser = InputParser()
            questions = parser.parse_assessment_json(file_path)

            total_questions = len(questions)
            self.logger.info(f"   题目总数: {total_questions} (全部处理)")

            # 处理所有题目
            all_question_results = []

            for i, question in enumerate(questions):
                question_id = question.get('question_id', f'Q{i+1}')
                self.logger.info(f"   处理题目 {i+1}/{total_questions}: {question_id}")

                try:
                    # Windows兼容的超时处理
                    import threading

                    result_container = {}
                    exception_container = {}

                    def worker():
                        try:
                            result = self.pipeline.process_single_question(question, i)
                            result_container['result'] = result
                        except Exception as e:
                            exception_container['exception'] = e

                    # 启动工作线程
                    thread = threading.Thread(target=worker)
                    thread.daemon = True
                    thread.start()

                    # 等待完成或超时
                    thread.join(timeout=self.timeout_per_question)

                    if thread.is_alive():
                        # 超时处理
                        self.logger.warning(f"      ⚠️ 题目处理超时: {question_id}")
                        default_result = {
                            'question_id': question_id,
                            'final_adjusted_scores': {
                                'openness_to_experience': 3,
                                'conscientiousness': 3,
                                'extraversion': 3,
                                'agreeableness': 3,
                                'neuroticism': 3
                            },
                            'confidence_metrics': {
                                'overall_reliability': 0.5,
                                'trait_reliabilities': {
                                    'openness_to_experience': 0.5,
                                    'conscientiousness': 0.5,
                                    'extraversion': 0.5,
                                    'agreeableness': 0.5,
                                    'neuroticism': 0.5
                                }
                            },
                            'timeout': True
                        }
                        all_question_results.append(default_result)
                    elif 'exception' in exception_container:
                        # 异常处理
                        self.logger.error(f"      ❌ 处理失败: {exception_container['exception']}")
                        continue
                    else:
                        # 成功处理
                        result = result_container['result']
                        all_question_results.append(result)

                        # 显示关键信息
                        reliability = result['confidence_metrics']['overall_reliability']
                        models_used = len(result['models_used'])
                        self.logger.info(f"      ✅ 完成 - 可靠性: {reliability:.3f}, 模型数: {models_used}")

                except Exception as e:
                    self.logger.error(f"      ❌ 处理失败: {e}")
                    continue

            # 快速计算Big5得分（避免完整流水线计算）
            big5_scores = self.calculate_big5_scores_fast(all_question_results)
            mbti_type = self.calculate_mbti_fast(big5_scores)

            processing_time = time.time() - start_time

            result = {
                'file_path': file_path,
                'total_questions': total_questions,
                'processed_questions': len(all_question_results),
                'big5_scores': big5_scores,
                'mbti_type': mbti_type,
                'question_results': all_question_results,
                'processing_time': processing_time,
                'algorithm_info': {
                    'max_evaluators': self.max_evaluators,
                    'use_enhanced': self.use_enhanced
                },
                'summary': {
                    'openness': big5_scores.get('openness_to_experience', 3.0),
                    'conscientiousness': big5_scores.get('conscientiousness', 3.0),
                    'extraversion': big5_scores.get('extraversion', 3.0),
                    'agreeableness': big5_scores.get('agreeableness', 3.0),
                    'neuroticism': big5_scores.get('neuroticism', 3.0),
                    'processing_time': round(processing_time, 2)
                }
            }

            self.logger.info(f"✅ 文件处理完成: {Path(file_path).name} ({processing_time:.2f}秒)")
            return result

        except Exception as e:
            self.logger.error(f"❌ 文件处理失败: {file_path} - {e}")
            return None

    def calculate_big5_scores_fast(self, question_results: List[Dict]) -> Dict[str, float]:
        """快速计算Big5得分"""
        if not question_results:
            return {
                'openness_to_experience': 3.0,
                'conscientiousness': 3.0,
                'extraversion': 3.0,
                'agreeableness': 3.0,
                'neuroticism': 3.0
            }

        # 简化计算：直接取所有题目的平均值
        dimensions = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        big5_scores = {}

        for dimension in dimensions:
            scores = []
            for result in question_results:
                if 'final_adjusted_scores' in result:
                    score = result['final_adjusted_scores'].get(dimension, 3)
                    if score in [1, 3, 5]:
                        scores.append(score)

            if scores:
                big5_scores[dimension] = round(sum(scores) / len(scores), 2)
            else:
                big5_scores[dimension] = 3.0

        return big5_scores

    def calculate_mbti_fast(self, big5_scores: Dict[str, float]) -> str:
        """快速计算MBTI类型"""
        O = big5_scores.get('openness_to_experience', 3)
        C = big5_scores.get('conscientiousness', 3)
        E = big5_scores.get('extraversion', 3)
        A = big5_scores.get('agreeableness', 3)
        N = big5_scores.get('neuroticism', 3)

        # E/I: 外向性 vs 神经质
        e_score = E + (5 - N)
        i_score = (5 - E) + N
        E_preference = 'E' if e_score > i_score else 'I'

        # S/N: 感觉 vs 直觉 (基于开放性)
        S_preference = 'S' if O <= 3 else 'N'

        # T/F: 思考 vs 情感 (基于宜人性)
        T_preference = 'T' if A <= 3 else 'F'

        # J/P: 判断 vs 知觉 (基于尽责性)
        J_preference = 'J' if C > 3 else 'P'

        return f"{E_preference}{S_preference}{T_preference}{J_preference}"

    def run(self):
        """运行批量处理"""
        self.logger.info("🚀 批量测评报告分析器")
        self.logger.info("=" * 80)
        self.logger.info(f"输入目录: {self.input_dir}")
        self.logger.info(f"输出目录: {self.output_dir}")
        self.logger.info(f"处理参数: 全部题目处理, 最大{self.max_evaluators}个评估器")
        self.logger.info(f"算法选择: {'增强算法' if self.use_enhanced else '原算法'}")

        # 加载检查点
        checkpoint_loaded = self.load_checkpoint()

        # 查找文件
        files = list(self.input_dir.glob("*.json"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]

        if not files:
            self.logger.error("❌ 未找到测评报告文件")
            return

        self.total_files = len(files)
        self.logger.info(f"📂 找到 {self.total_files} 个测评报告文件")
        self.logger.info(f"   已处理: {len(self.processed_files)} 个")
        self.logger.info(f"   剩余: {self.total_files - len(self.processed_files)} 个")

        # 过滤已处理的文件
        remaining_files = [f for f in files if str(f) not in self.processed_files]
        remaining_files.sort(key=lambda x: x.name)

        self.logger.info("")
        self.logger.info(f"▶️  从第 {self.current_file_index + 1} 个文件开始处理")
        self.logger.info("")

        # 处理文件
        for i, file_path in enumerate(remaining_files):
            self.current_file_index = i + len(self.processed_files)

            self.logger.info(f"📁 进度: {self.current_file_index}/{self.total_files} 文件")

            # 检查是否为问题报告
            is_problem, reason = self.is_problem_report(str(file_path))
            if is_problem:
                self.handle_problem_report(file_path, reason)
                self.processed_files.add(str(file_path))  # 标记为已处理，避免重复
                continue  # 跳过正常处理流程

            # 正常处理文件
            result = self.process_single_file_optimized(str(file_path))

            if result:
                self.results.append(result)
                self.processed_files.add(str(file_path))

                # 每处理一个文件就保存检查点
                self.save_checkpoint()

                # 保存中间结果
                self.save_intermediate_results()
            else:
                self.logger.error(f"❌ 跳过文件: {file_path}")
                continue

        # 最终汇总
        self.generate_final_summary()
        self.logger.info("🎉 批量处理完成!")

        return self.results

    def save_intermediate_results(self):
        """保存中间结果"""
        try:
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"❌ 保存中间结果失败: {e}")

    def generate_final_summary(self):
        """生成最终汇总"""
        if not self.results:
            self.logger.warning("⚠️ 没有处理结果，跳过汇总生成")
            return

        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()

        # 生成Markdown摘要
        summary_content = f"""# 批量处理结果摘要

## 📊 处理统计
- **总文件数**: {self.total_files}
- **有效处理**: {len(self.results)}
- **问题报告**: {self.problem_reports_count}
- **处理失败**: {self.total_files - len(self.processed_files)}
- **处理成功率**: {len(self.results)/self.total_files:.1%}
- **总处理时间**: {total_time:.1f}秒

## 🚩 问题报告筛选
- **筛选标准**: 30%以上回答为问题回答（如"请提供提示词"等）
- **问题报告数量**: {self.problem_reports_count} 个
- **问题报告比例**: {self.problem_reports_count/self.total_files:.1%}
- **问题报告目录**: `{self.problem_reports_dir}`

## ⚙️ 处理参数
- **处理题目数**: 全部50题
- **最大评估器数量**: {self.max_evaluators}
- **使用增强算法**: {'是' if self.use_enhanced else '否'}
- **超时设置**: {self.timeout_per_question}秒/题目

## 📋 文件处理结果
"""

        for result in self.results:
            file_name = Path(result['file_path']).name
            big5 = result.get('big5_scores', {})
            mbti = result.get('mbti_type', 'Unknown')
            time_used = result.get('processing_time', 0)
            questions = result.get('processed_questions', 0)

            summary_content += f"""
### {file_name}
- **题目数**: {questions}/{result.get('total_questions', 0)}
- **Big5得分**: {big5}
- **MBTI类型**: {mbti}
- **处理时间**: {time_used:.2f}秒
"""

        summary_content += f"""

## 🎯 整体统计
"""

        # 计算平均Big5得分
        if self.results:
            avg_scores = {
                'openness_to_experience': 0,
                'conscientiousness': 0,
                'extraversion': 0,
                'agreeableness': 0,
                'neuroticism': 0
            }

            for result in self.results:
                big5 = result.get('big5_scores', {})
                for dim in avg_scores:
                    avg_scores[dim] += big5.get(dim, 0)

            for dim in avg_scores:
                avg_scores[dim] = round(avg_scores[dim] / len(self.results), 2)

            summary_content += f"""
- **平均Big5得分**: {avg_scores}
"""

        summary_content += f"""

## 💡 处理说明
- **完整50题处理**: 生产版本处理完整的50题目测评报告
- **问题报告筛选**: 自动识别并筛选被试未正确看到题目提示的报告
- **断点续跑**: 支持从中断处继续处理，避免重复工作
- **超时保护**: 每题5分钟超时，防止因个别问题卡住整体进度

## 🚩 问题报告说明
问题报告是指被试可能没有正确看到题目提示词的测评报告，表现为：
- 回答"请提供提示词"、"请给出问题"等
- 回答过短或仅为标点符号
- 问题回答比例超过30%的报告

这些报告已被单独分类保存，不影响正常报告的处理结果。
"""

        try:
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            self.logger.info(f"📄 汇总报告已保存: {self.summary_file}")
        except Exception as e:
            self.logger.error(f"❌ 保存汇总报告失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量处理器')
    parser.add_argument('--input-dir', required=True, help='输入目录')
    parser.add_argument('--output-dir', required=True, help='输出目录')
    parser.add_argument('--max-evaluators', type=int, default=3, help='最大评估器数量')
    parser.add_argument('--enhanced', action='store_true', help='使用增强算法')
    parser.add_argument('--resume', action='store_true', help='从检查点恢复')

    args = parser.parse_args()

    processor = BatchProcessor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        max_evaluators=args.max_evaluators,
        use_enhanced=args.enhanced
    )

    if args.resume:
        processor.load_checkpoint()

    results = processor.run()

    if results:
        print(f"\n🎉 处理完成! 共处理 {len(results)} 个文件")
        print(f"📄 结果文件: {processor.results_file}")
        print(f"📋 汇总报告: {processor.summary_file}")
    else:
        print("\n❌ 没有成功处理任何文件")
        sys.exit(1)


if __name__ == "__main__":
    main()