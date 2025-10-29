#!/usr/bin/env python3
"""
多模型一致性分析 - 使用不同 iFlow 模型评估相同数据并分析一致性
"""

import asyncio
import json
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from iflow_sdk_evaluator import IFlowSDKEvaluator, IFlowBatchProcessor


class MultiModelConsistencyAnalyzer:
    """多模型一致性分析器"""
    
    def __init__(self, models: List[str] = None):
        """
        初始化分析器
        
        Args:
            models: 模型列表，默认使用多个 iFlow 模型
        """
        if models is None:
            self.models = [
                "deepseek-v3.2-exp",
                "deepseek-r1:70b",
                "deepseek-r1:8b",
                "deepseek-chat"
            ]
        else:
            self.models = models
        
        self.evaluators = {model: IFlowSDKEvaluator(model=model) for model in self.models}
    
    def load_assessment_file(self, file_path: Path) -> List[Dict]:
        """加载测评文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = []
        if isinstance(data, dict) and 'assessment_results' in data:
            assessment_results = data['assessment_results']
            
            for item in assessment_results:
                if isinstance(item, dict) and 'question_data' in item and 'conversation_log' in item:
                    question_data = item['question_data']
                    conversation_log = item['conversation_log']
                    
                    question = None
                    answer = None
                    
                    for log_item in conversation_log:
                        if log_item.get('role') == 'user':
                            content = log_item.get('content', '')
                            if '[ASSESSMENT_QUESTION]' in content:
                                question = content.replace('[ASSESSMENT_QUESTION]', '').strip()
                        elif log_item.get('role') == 'assistant':
                            answer = log_item.get('content', '')
                            if '\n\n' in answer:
                                answer = answer.split('\n\n')[-1].strip()
                    
                    if question and answer:
                        questions.append({
                            'question': question,
                            'answer': answer,
                            'dimension': question_data.get('dimension', ''),
                            'question_id': question_data.get('question_id', '')
                        })
        
        return questions
    
    def create_segments(self, questions: List[Dict], segment_size: int = 5) -> List[List[Dict]]:
        """将问题列表分成5题分段"""
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i + segment_size]
            if segment:
                segments.append(segment)
        return segments
    
    async def evaluate_with_model(self, segments: List[List[Dict]], model: str) -> Dict[str, Any]:
        """使用指定模型评估分段"""
        print(f"🤖 使用模型 {model} 进行评估...")
        
        processor = IFlowBatchProcessor(model=model)
        segment_results = await processor.batch_evaluate(segments)
        final_scores = processor.calculate_final_scores(segment_results['results'])
        
        return {
            'model': model,
            'segment_results': segment_results,
            'final_scores': final_scores,
            'stats': processor.stats
        }
    
    def calculate_consistency(self, all_results: Dict[str, Dict]) -> Dict[str, Any]:
        """计算模型间的一致性分析"""
        
        traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        consistency_analysis = {}
        
        # 收集所有模型的分数
        model_scores = {}
        for model, result in all_results.items():
            if result['final_scores'].get('success', False):
                model_scores[model] = result['final_scores']['big5_scores']
        
        # 计算每个特质的一致性
        for trait in traits:
            scores = [model_scores[model][trait] for model in model_scores if trait in model_scores[model]]
            if scores:
                mean = statistics.mean(scores)
                stdev = statistics.stdev(scores) if len(scores) > 1 else 0
                min_score = min(scores)
                max_score = max(scores)
                
                consistency_analysis[trait] = {
                    'mean': round(mean, 2),
                    'stdev': round(stdev, 2),
                    'min': min_score,
                    'max': max_score,
                    'range': max_score - min_score,
                    'consistency_level': self._get_consistency_level(stdev)
                }
        
        # 计算总体一致性
        all_scores = []
        for model_scores_dict in model_scores.values():
            all_scores.extend(list(model_scores_dict.values()))
        
        overall_stdev = statistics.stdev(all_scores) if len(all_scores) > 1 else 0
        
        return {
            'traits_consistency': consistency_analysis,
            'overall_consistency': {
                'stdev': round(overall_stdev, 2),
                'consistency_level': self._get_consistency_level(overall_stdev)
            },
            'models_compared': list(model_scores.keys()),
            'total_models': len(model_scores)
        }
    
    def _get_consistency_level(self, stdev: float) -> str:
        """根据标准差判断一致性等级"""
        if stdev < 0.5:
            return "非常高"
        elif stdev < 1.0:
            return "高"
        elif stdev < 1.5:
            return "中等"
        else:
            return "低"
    
    def find_disagreements(self, all_results: Dict[str, Dict]) -> List[Dict]:
        """找出模型间的主要分歧点"""
        
        traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        disagreements = []
        
        # 收集所有模型的分数
        model_scores = {}
        for model, result in all_results.items():
            if result['final_scores'].get('success', False):
                model_scores[model] = result['final_scores']['big5_scores']
        
        # 找出分歧较大的特质
        for trait in traits:
            scores = [model_scores[model][trait] for model in model_scores if trait in model_scores[model]]
            if scores:
                score_range = max(scores) - min(scores)
                if score_range >= 2:  # 分数差异大于2分视为显著分歧
                    disagreement = {
                        'trait': trait,
                        'score_range': score_range,
                        'model_scores': {model: model_scores[model][trait] for model in model_scores}
                    }
                    disagreements.append(disagreement)
        
        return disagreements
    
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件的多模型一致性"""
        
        print(f"\n📊 分析文件: {file_path.name}")
        
        # 加载数据
        questions = self.load_assessment_file(file_path)
        if not questions:
            return {'success': False, 'error': f'无法加载或解析文件: {file_path.name}'}
        
        print(f"   找到 {len(questions)} 个问答对")
        
        # 创建分段
        segments = self.create_segments(questions, segment_size=5)
        print(f"   分成 {len(segments)} 个分段")
        
        # 使用不同模型进行评估
        all_results = {}
        for model in self.models:
            try:
                result = await self.evaluate_with_model(segments, model)
                all_results[model] = result
                
                if result['final_scores']['success']:
                    scores = result['final_scores']['big5_scores']
                    score_str = ", ".join([f"{trait[0].upper()}:{score}" for trait, score in scores.items()])
                    print(f"   ✅ {model}: {score_str}")
                else:
                    print(f"   ❌ {model}: 评估失败")
                    
            except Exception as e:
                print(f"   ❌ {model}: 评估出错 - {e}")
                all_results[model] = {'error': str(e)}
        
        # 计算一致性分析
        consistency = self.calculate_consistency(all_results)
        disagreements = self.find_disagreements(all_results)
        
        return {
            'success': True,
            'file': str(file_path),
            'total_questions': len(questions),
            'segments': len(segments),
            'model_results': all_results,
            'consistency_analysis': consistency,
            'disagreements': disagreements,
            'analysis_time': datetime.now().isoformat()
        }


def print_consistency_report(analysis_result: Dict):
    """打印一致性分析报告"""
    
    print("\n" + "="*60)
    print("📈 多模型一致性分析报告")
    print("="*60)
    
    if not analysis_result.get('success', False):
        print(f"❌ 分析失败: {analysis_result.get('error', '未知错误')}")
        return
    
    print(f"📁 分析文件: {analysis_result['file']}")
    print(f"📊 总问题数: {analysis_result['total_questions']}")
    print(f"📋 分段数量: {analysis_result['segments']}")
    
    consistency = analysis_result['consistency_analysis']
    print(f"\n🤖 参与模型 ({consistency['total_models']}个): {', '.join(consistency['models_compared'])}")
    
    print("\n📊 特质一致性分析:")
    for trait, stats in consistency['traits_consistency'].items():
        print(f"   {trait:20}: 均值={stats['mean']}, 标准差={stats['stdev']}, 范围={stats['min']}-{stats['max']}, 一致性={stats['consistency_level']}")
    
    overall = consistency['overall_consistency']
    print(f"\n📊 总体一致性: 标准差={overall['stdev']}, 等级={overall['consistency_level']}")
    
    disagreements = analysis_result['disagreements']
    if disagreements:
        print(f"\n⚠️  发现 {len(disagreements)} 个显著分歧:")
        for d in disagreements:
            print(f"   {d['trait']}: 分数范围 {d['score_range']}")
            for model, score in d['model_scores'].items():
                print(f"     - {model}: {score}")
    else:
        print("\n✅ 模型间无显著分歧")


async def main():
    """主函数"""
    
    # 选择测试文件
    test_files = [
        "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a1_e0_t0_0_09271.json",
        "results/results/asses_gemma3_latest_agent_big_five_50_complete2_def_e0_t0_0_09201.json"
    ]
    
    analyzer = MultiModelConsistencyAnalyzer()
    
    all_results = {}
    for file_path_str in test_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            result = await analyzer.analyze_file(file_path)
            all_results[file_path.name] = result
            print_consistency_report(result)
        else:
            print(f"❌ 文件不存在: {file_path}")
    
    # 保存结果
    output_file = f"multi_model_consistency_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 一致性分析结果已保存到: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())