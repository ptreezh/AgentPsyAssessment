#!/usr/bin/env python3
"""
完整的批量分析流程
对295份原始测评报告进行完整的处理流程：
1. 格式转换 → 2. 报告精简 → 3. 分段式评分 → 4. 汇总分析
"""

import json
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import traceback

# 导入必要的模块
try:
    from segmented_analysis import SegmentedPersonalityAnalyzer
    from shared_analysis.analyze_results import create_simplified_assessment, analyze_single_file
    from shared_analysis.ollama_evaluator import get_ollama_evaluators, create_ollama_evaluator, get_ollama_model_config
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

# 导入Ollama评估器
try:
    evaluators = get_ollama_evaluators()
    if not evaluators:
        raise ValueError("没有找到配置的Ollama评估器")
    print(f"找到评估器: {list(evaluators.keys())}")
except Exception as e:
    print(f"初始化评估器失败: {e}")
    sys.exit(1)

class ComprehensiveBatchAnalyzer:
    """完整批量分析器"""

    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=2, max_segment_size=30000)
        self.evaluators = evaluators  # 使用全局评估器配置

        # 创建输出目录结构
        self.converted_dir = self.output_dir / "01_converted"
        self.simplified_dir = self.output_dir / "02_simplified"
        self.segmented_dir = self.output_dir / "03_segmented_analysis"
        self.final_results_dir = self.output_dir / "04_final_results"
        self.logs_dir = self.output_dir / "logs"

        for dir_path in [self.converted_dir, self.simplified_dir, self.segmented_dir,
                        self.final_results_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 设置日志
        self.setup_logging()

        # 统计信息
        self.stats = {
            'total_files': 0,
            'converted': 0,
            'simplified': 0,
            'analyzed': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }

    def setup_logging(self):
        """设置日志"""
        log_file = self.logs_dir / f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def find_raw_reports(self) -> List[Path]:
        """查找原始报告文件"""
        raw_files = []
        for file_path in self.input_dir.rglob("*.json"):
            if "_converted.json" not in file_path.name:
                raw_files.append(file_path)

        self.stats['total_files'] = len(raw_files)
        self.logger.info(f"找到 {len(raw_files)} 个原始报告文件")
        return raw_files

    def convert_format(self, input_file: Path) -> Dict:
        """步骤1：格式转换 - 将原始报告转换为标准格式"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 基本格式标准化
            converted_data = {
                'source_file': input_file.name,
                'conversion_time': datetime.now().isoformat(),
                'original_data': data
            }

            # 如果数据已经是标准格式，直接使用
            if 'assessment_results' in data or 'questions' in data:
                converted_data['assessment_data'] = data
            else:
                # 尝试从其他字段提取评估数据
                converted_data['assessment_data'] = self.extract_assessment_data(data)

            return converted_data

        except Exception as e:
            self.logger.error(f"格式转换失败 {input_file}: {e}")
            return None

    def extract_assessment_data(self, data: Dict) -> Dict:
        """从各种格式中提取评估数据"""
        # 查找可能包含评估数据的字段
        possible_keys = ['results', 'data', 'response', 'output', 'content']

        for key in possible_keys:
            if key in data:
                if isinstance(data[key], dict):
                    return data[key]
                elif isinstance(data[key], list) and len(data[key]) > 0:
                    return {'questions': data[key]}

        # 如果找不到，返回原始数据并标记
        return {
            'questions': [],
            'note': '无法识别数据格式，使用原始数据',
            'raw_data': data
        }

    def simplify_report(self, converted_data: Dict) -> Dict:
        """步骤2：报告精简 - 创建简化版本避免上下文限制"""
        try:
            assessment_data = converted_data.get('assessment_data', {})

            # 使用现有的精简函数
            simplified_summary = create_simplified_assessment(assessment_data)

            # 创建包含原始数据和简化版本的完整结构
            simplified = {
                'metadata': {
                    'source_file': converted_data['source_file'],
                    'conversion_time': converted_data['conversion_time'],
                    'simplification_time': datetime.now().isoformat()
                },
                'assessment_data': assessment_data,
                'assessment_summary': simplified_summary.get('assessment_summary', {})
            }

            return simplified

        except Exception as e:
            self.logger.error(f"报告精简失败 {converted_data['source_file']}: {e}")
            return None

    def analyze_with_segmented_approach(self, simplified_data: Dict) -> Dict:
        """步骤3：分段式评分 - 三个评估器独立分析并对比"""
        try:
            source_file = simplified_data['metadata']['source_file']
            assessment_data = simplified_data.get('assessment_data', {})

            # 提取问题
            questions = self.analyzer.extract_questions(assessment_data)

            if not questions:
                self.logger.warning(f"未找到问题: {source_file}")
                return None

            # 创建分段
            segments = self.analyzer.create_segments(questions)

            self.logger.info(f"文件 {source_file} 分成 {len(segments)} 个段")

            # 优先使用默认的三个评估器
            default_evaluators = self.evaluators.get("default_evaluators", ["glm_4_6_cloud", "deepseek_v3_1_cloud", "qwen3_vl_cloud"])
            backup_evaluators = [name for name in self.evaluators.keys() if name not in default_evaluators]
            
            evaluator_final_results = {}
            
            # 第一步：使用默认评估器
            for evaluator_name in default_evaluators:
                try:
                    self.logger.info(f"开始使用评估器 {evaluator_name} 分析文件 {source_file}")

                    # 为每个评估器创建新的分析器实例
                    evaluator_analyzer = SegmentedPersonalityAnalyzer(max_questions_per_segment=3, max_segment_size=30000)

                    evaluator = create_ollama_evaluator(evaluator_name)
                    if not evaluator:
                        self.logger.error(f"无法创建评估器: {evaluator_name}")
                        continue

                    # 逐段分析
                    segment_results = []
                    for i, segment in enumerate(segments):
                        self.logger.info(f"评估器 {evaluator_name} 处理段 {i+1}/{len(segments)}")

                        # 获取正确的模型名称
                        model_key = self.evaluators[evaluator_name]['model']
                        model_config = get_ollama_model_config(model_key)
                        actual_model_name = model_config.get('name', model_key)

                        # 调用真正的评估器，带重试机制
                        max_retries = 5  # 增加重试次数
                        retry_delay = 10  # 增加初始延迟时间

                        for retry in range(max_retries):
                            try:
                                self.logger.info(f"评估器 {evaluator_name} 分析段 {i+1} (尝试 {retry+1}/{max_retries})")

                                # 使用分析器的analyze_segment方法获取段分析结果
                                segment_analysis = evaluator_analyzer.analyze_segment(segment, i+1)
                                
                                # 根据不同模型设置不同的超时时间
                                original_timeout = evaluator.timeout
                                if 'qwen3_30b' in actual_model_name or 'deepseek' in actual_model_name:
                                    evaluator.timeout = 600  # 10分钟超时
                                elif 'mistral' in actual_model_name:
                                    evaluator.timeout = 300  # 5分钟超时
                                else:
                                    evaluator.timeout = 180  # 3分钟超时

                                eval_result = evaluator.evaluate_json_response(
                                    model_name=actual_model_name,
                                    system_prompt=segment_analysis['system_prompt'],
                                    user_prompt=segment_analysis['user_prompt']
                                )

                                # 恢复原始超时
                                evaluator.timeout = original_timeout

                                if eval_result.get('success'):
                                    segment_result = eval_result['response']
                                    segment_results.append(segment_result)

                                    # 累积分数到该评估器的分析器
                                    evaluator_analyzer.accumulate_scores(segment_result)

                                    self.logger.info(f"评估器 {evaluator_name} 分析段 {i+1} 成功")
                                    break
                                else:
                                    error_msg = eval_result.get('error', '未知错误')
                                    self.logger.warning(f"评估器 {evaluator_name} 分析段 {i+1} 尝试 {retry+1} 失败: {error_msg}")

                                    # 在重试前恢复原始超时
                                    evaluator.timeout = original_timeout

                                    if retry < max_retries - 1:
                                        self.logger.info(f"等待 {retry_delay} 秒后重试...")
                                        import time
                                        time.sleep(retry_delay)
                                        retry_delay *= 2  # 指数退避
                                    else:
                                        self.logger.error(f"评估器 {evaluator_name} 分析段 {i+1} 最终失败: {error_msg}")
                                        # 不再跳过段，而是抛出异常停止分析
                                        raise Exception(f"评估器 {evaluator_name} 无法分析段 {i+1}: {error_msg}")

                            except Exception as e:
                                error_msg = str(e)
                                self.logger.warning(f"评估器 {evaluator_name} 分析段 {i+1} 尝试 {retry+1} 异常: {error_msg}")

                                # 在重试前恢复原始超时
                                evaluator.timeout = original_timeout

                                if retry < max_retries - 1:
                                    self.logger.info(f"等待 {retry_delay} 秒后重试...")
                                    import time
                                    time.sleep(retry_delay)
                                    retry_delay *= 2  # 指数退避
                                else:
                                    self.logger.error(f"评估器 {evaluator_name} 分析段 {i+1} 最终异常失败: {error_msg}")
                                    # 不再跳过段，而是抛出异常停止分析
                                    raise Exception(f"评估器 {evaluator_name} 无法分析段 {i+1}: {error_msg}")

                    # 计算该评估器的最终分数
                    final_scores = evaluator_analyzer.calculate_final_scores()

                    evaluator_final_results[evaluator_name] = {
                        'segment_count': len(segments),
                        'question_count': len(questions),
                        'segment_results': segment_results,
                        'final_scores': final_scores,
                        'analysis_time': datetime.now().isoformat()
                    }

                    self.logger.info(f"评估器 {evaluator_name} 完成分析，MBTI类型: {final_scores['mbti']['type']}")

                except Exception as e:
                    self.logger.error(f"评估器 {evaluator_name} 完整分析失败: {e}")
                    self.logger.error(traceback.format_exc())

            # 如果所有评估器都失败，直接失败
            if not evaluator_final_results:
                error_msg = f"所有评估器都失败，无法分析文件 {source_file}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            # 生成评估器对比分析
            comparison_analysis = self.generate_evaluator_comparison(evaluator_final_results)

            return {
                'source_file': source_file,
                'analysis_time': datetime.now().isoformat(),
                'segment_count': len(segments),
                'question_count': len(questions),
                'evaluator_results': evaluator_final_results,
                'comparison_analysis': comparison_analysis
            }

        except Exception as e:
            self.logger.error(f"分段分析失败 {simplified_data['metadata']['source_file']}: {e}")
            self.logger.error(traceback.format_exc())
            return None

  
    def aggregate_evaluator_results(self, evaluator_results: Dict) -> Dict:
        """聚合多个评估器的结果"""
        try:
            # 收集所有评估器的question_scores
            all_question_scores = []

            # 找出第一个评估器的结果作为模板
            first_evaluator = list(evaluator_results.values())[0]
            if 'question_scores' not in first_evaluator:
                # 如果没有question_scores，返回第一个结果
                return first_evaluator

            # 为每个问题聚合不同评估器的分数
            template_questions = first_evaluator['question_scores']

            aggregated_questions = []
            for i, template_question in enumerate(template_questions):
                question_id = template_question['question_id']
                dimension = template_question['dimension']

                # 聚合Big Five分数
                aggregated_big_five = {}
                for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    scores = []
                    evidences = []

                    for evaluator_name, result in evaluator_results.items():
                        if 'question_scores' in result and len(result['question_scores']) > i:
                            question_result = result['question_scores'][i]
                            if 'big_five_scores' in question_result and trait in question_result['big_five_scores']:
                                trait_data = question_result['big_five_scores'][trait]
                                scores.append(trait_data.get('score', 5.0))
                                evidences.append(trait_data.get('evidence', ''))

                    if scores:
                        avg_score = sum(scores) / len(scores)
                        aggregated_big_five[trait] = {
                            'score': round(avg_score, 1),
                            'evidence': f"聚合{len(scores)}个评估器: {'; '.join(evidences[:2])}"  # 取前2个证据
                        }
                    else:
                        aggregated_big_five[trait] = {
                            'score': 5.0,
                            'evidence': '无法聚合分数'
                        }

                aggregated_questions.append({
                    'question_id': question_id,
                    'dimension': dimension,
                    'big_five_scores': aggregated_big_five
                })

            return {
                'question_scores': aggregated_questions
            }

        except Exception as e:
            self.logger.error(f"聚合评估器结果失败: {e}")
            # 返回第一个评估器的结果作为备用
            return first_evaluator

    def generate_evaluator_comparison(self, evaluator_results: Dict) -> Dict:
        """生成评估器对比分析"""
        try:
            if not evaluator_results:
                return {'error': 'No evaluator results provided'}

            comparison = {
                'evaluator_count': len(evaluator_results),
                'mbti_comparison': {},
                'big_five_comparison': {},
                'consensus_analysis': {},
                'disagreement_analysis': {}
            }

            # 收集所有评估器的MBTI类型
            mbti_types = []
            big_five_scores = {}

            for evaluator_name, result in evaluator_results.items():
                final_scores = result.get('final_scores', {})
                mbti = final_scores.get('mbti', {})
                big_five = final_scores.get('big_five', {})

                if mbti:
                    mbti_types.append(mbti.get('type', 'Unknown'))
                    comparison['mbti_comparison'][evaluator_name] = {
                        'type': mbti.get('type', 'Unknown'),
                        'confidence': mbti.get('confidence', 0)
                    }

                if big_five:
                    big_five_scores[evaluator_name] = big_five
                    comparison['big_five_comparison'][evaluator_name] = big_five

            # 计算MBTI一致性
            if mbti_types:
                mbti_consensus = max(set(mbti_types), key=mbti_types.count)
                mbti_agreement = mbti_types.count(mbti_consensus) / len(mbti_types)

                comparison['consensus_analysis']['mbti'] = {
                    'consensus_type': mbti_consensus,
                    'agreement_rate': round(mbti_agreement, 2),
                    'vote_counts': {mbti_type: mbti_types.count(mbti_type) for mbti_type in set(mbti_types)}
                }

            # 计算Big Five分数的相关性
            if len(big_five_scores) > 1:
                big_five_traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
                score_variations = {}

                for trait in big_five_traits:
                    scores = []
                    for evaluator_name, scores_dict in big_five_scores.items():
                        if trait in scores_dict:
                            scores.append(scores_dict[trait].get('score', 5.0))

                    if scores:
                        avg_score = sum(scores) / len(scores)
                        max_score = max(scores)
                        min_score = min(scores)
                        variation = max_score - min_score

                        score_variations[trait] = {
                            'average_score': round(avg_score, 2),
                            'max_score': max_score,
                            'min_score': min_score,
                            'variation': round(variation, 2),
                            'coefficient_of_variation': round(variation / avg_score if avg_score > 0 else 0, 2)
                        }

                comparison['consensus_analysis']['big_five'] = score_variations

                # 识别分歧最大的维度
                max_variation_trait = max(score_variations.items(), key=lambda x: x[1]['variation'])
                comparison['disagreement_analysis']['highest_variation'] = {
                    'trait': max_variation_trait[0],
                    'variation': max_variation_trait[1]['variation'],
                    'details': max_variation_trait[1]
                }

            return comparison

        except Exception as e:
            self.logger.error(f"生成评估器对比分析失败: {e}")
            return {'error': str(e)}

    def process_single_file(self, input_file: Path) -> Dict:
        """处理单个文件的完整流程"""
        file_result = {
            'source_file': input_file.name,
            'status': 'processing',
            'steps': {},
            'final_result': None
        }

        try:
            # 步骤1：格式转换
            self.logger.info(f"处理文件 {input_file.name} - 步骤1：格式转换")
            converted = self.convert_format(input_file)
            if not converted:
                file_result['status'] = 'failed'
                file_result['error'] = '格式转换失败'
                return file_result

            file_result['steps']['converted'] = True

            # 保存转换结果
            converted_file = self.converted_dir / f"{input_file.stem}_converted.json"
            with open(converted_file, 'w', encoding='utf-8') as f:
                json.dump(converted, f, ensure_ascii=False, indent=2)

            # 步骤2：报告精简
            self.logger.info(f"处理文件 {input_file.name} - 步骤2：报告精简")
            simplified = self.simplify_report(converted)
            if not simplified:
                file_result['status'] = 'failed'
                file_result['error'] = '报告精简失败'
                return file_result

            file_result['steps']['simplified'] = True

            # 保存精简结果
            simplified_file = self.simplified_dir / f"{input_file.stem}_simplified.json"
            with open(simplified_file, 'w', encoding='utf-8') as f:
                json.dump(simplified, f, ensure_ascii=False, indent=2)

            # 步骤3：分段式评分
            self.logger.info(f"处理文件 {input_file.name} - 步骤3：分段式评分")
            analyzed = self.analyze_with_segmented_approach(simplified)
            if not analyzed:
                file_result['status'] = 'failed'
                file_result['error'] = '分段分析失败'
                return file_result

            file_result['steps']['analyzed'] = True
            file_result['final_result'] = analyzed

            # 保存分析结果
            analyzed_file = self.segmented_dir / f"{input_file.stem}_analyzed.json"
            with open(analyzed_file, 'w', encoding='utf-8') as f:
                json.dump(analyzed, f, ensure_ascii=False, indent=2)

            file_result['status'] = 'completed'
            self.stats['analyzed'] += 1
            self.logger.info(f"文件 {input_file.name} 分析完成，包含 {len(analyzed.get('evaluator_results', {}))} 个评估器结果")

        except Exception as e:
            file_result['status'] = 'failed'
            file_result['error'] = str(e)
            self.logger.error(f"处理文件失败 {input_file}: {e}")
            self.stats['failed'] += 1

        return file_result

    def generate_summary_report(self, results: List[Dict]) -> Dict:
        """步骤4：汇总分析 - 生成综合分析报告（支持多评估器对比）"""
        summary = {
            'analysis_summary': {
                'total_files_processed': len(results),
                'successful_analyses': len([r for r in results if r['status'] == 'completed']),
                'failed_analyses': len([r for r in results if r['status'] == 'failed']),
                'analysis_time': datetime.now().isoformat()
            },
            'evaluator_performance': {},
            'big_five_aggregate': {},
            'mbti_distribution': {},
            'cross_evaluator_analysis': {},
            'detailed_results': results
        }

        # 收集所有评估器的结果
        evaluator_big_five_scores = {}
        evaluator_mbti_types = {}
        evaluator_comparisons = []

        for result in results:
            if result['status'] == 'completed' and 'evaluator_results' in result:
                # 对于每个评估器的结果
                for evaluator_name, evaluator_result in result['evaluator_results'].items():
                    final_scores = evaluator_result.get('final_scores', {})

                    # 初始化评估器数据结构
                    if evaluator_name not in evaluator_big_five_scores:
                        evaluator_big_five_scores[evaluator_name] = []
                        evaluator_mbti_types[evaluator_name] = []

                    # 收集Big Five分数
                    if 'big_five' in final_scores:
                        evaluator_big_five_scores[evaluator_name].append(final_scores['big_five'])

                    # 收集MBTI类型
                    if 'mbti' in final_scores:
                        evaluator_mbti_types[evaluator_name].append(final_scores['mbti']['type'])

                # 收集评估器对比数据
                if 'comparison_analysis' in result:
                    evaluator_comparisons.append(result['comparison_analysis'])

        # 计算每个评估器的Big Five平均分数
        for evaluator_name, big_five_list in evaluator_big_five_scores.items():
            if big_five_list:
                evaluator_avg = {}
                for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                    scores = [bf.get(trait, {}).get('score', 0) for bf in big_five_list]
                    avg_score = sum(scores) / len(scores) if scores else 0
                    evaluator_avg[trait] = {
                        'average_score': round(avg_score, 2),
                        'min_score': min(scores) if scores else 0,
                        'max_score': max(scores) if scores else 0,
                        'sample_count': len(scores)
                    }
                summary['big_five_aggregate'][evaluator_name] = evaluator_avg

        # 统计每个评估器的MBTI类型分布
        for evaluator_name, mbti_list in evaluator_mbti_types.items():
            mbti_counts = {}
            for mbti_type in mbti_list:
                mbti_counts[mbti_type] = mbti_counts.get(mbti_type, 0) + 1
            summary['mbti_distribution'][evaluator_name] = mbti_counts

        # 计算评估器间的一致性分析
        if evaluator_comparisons:
            # 计算平均MBTI一致性
            mbti_agreement_rates = [comp.get('consensus_analysis', {}).get('mbti', {}).get('agreement_rate', 0)
                                   for comp in evaluator_comparisons if 'consensus_analysis' in comp]

            if mbti_agreement_rates:
                summary['cross_evaluator_analysis']['mbti_consistency'] = {
                    'average_agreement_rate': round(sum(mbti_agreement_rates) / len(mbti_agreement_rates), 2),
                    'perfect_agreement_count': len([rate for rate in mbti_agreement_rates if rate == 1.0]),
                    'total_comparisons': len(mbti_agreement_rates)
                }

            # 计算Big Five分数变异性
            all_variations = []
            for comp in evaluator_comparisons:
                big_five_consensus = comp.get('consensus_analysis', {}).get('big_five', {})
                for trait, variation_data in big_five_consensus.items():
                    if 'variation' in variation_data:
                        all_variations.append({
                            'trait': trait,
                            'variation': variation_data['variation']
                        })

            if all_variations:
                avg_variation = sum(v['variation'] for v in all_variations) / len(all_variations)
                summary['cross_evaluator_analysis']['score_variability'] = {
                    'average_variation': round(avg_variation, 2),
                    'max_variation': max(v['variation'] for v in all_variations),
                    'most_variable_trait': max(all_variations, key=lambda x: x['variation'])['trait']
                }

        # 计算评估器性能统计
        for evaluator_name in evaluator_big_five_scores.keys():
            successful_analyses = len(evaluator_big_five_scores[evaluator_name])
            summary['evaluator_performance'][evaluator_name] = {
                'successful_analyses': successful_analyses,
                'success_rate': round(successful_analyses / len([r for r in results if r['status'] == 'completed']), 2)
            }

        return summary

    def run_batch_analysis(self):
        """运行批量分析"""
        self.logger.info("开始批量分析流程")
        self.stats['start_time'] = datetime.now()

        # 查找原始报告
        raw_files = self.find_raw_reports()

        # 处理每个文件
        results = []
        for i, input_file in enumerate(raw_files):
            self.logger.info(f"处理文件 {i+1}/{len(raw_files)}: {input_file.name}")

            result = self.process_single_file(input_file)
            results.append(result)

            # 定期保存进度
            if (i + 1) % 10 == 0:
                self.logger.info(f"已处理 {i+1}/{len(raw_files)} 个文件")

                # 保存中间结果
                progress_file = self.output_dir / f"progress_{i+1}.json"
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)

        # 生成汇总报告
        self.logger.info("生成汇总分析报告")
        summary_report = self.generate_summary_report(results)

        # 保存最终结果
        final_report_file = self.final_results_dir / "comprehensive_analysis_report.json"
        with open(final_report_file, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, ensure_ascii=False, indent=2)

        self.stats['end_time'] = datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']

        self.logger.info(f"批量分析完成！")
        self.logger.info(f"总文件数: {len(raw_files)}")
        self.logger.info(f"成功分析: {self.stats['analyzed']}")
        self.logger.info(f"失败: {self.stats['failed']}")
        self.logger.info(f"耗时: {duration}")

        return summary_report

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python comprehensive_batch_analysis.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    # 检查输入目录
    if not os.path.exists(input_dir):
        print(f"输入目录不存在: {input_dir}")
        sys.exit(1)

    # 创建分析器并运行
    analyzer = ComprehensiveBatchAnalyzer(input_dir, output_dir)
    result = analyzer.run_batch_analysis()

    print(f"\n分析完成！结果保存在: {output_dir}")
    print(f"汇总报告: {output_dir}/04_final_results/comprehensive_analysis_report.json")

if __name__ == "__main__":
    main()