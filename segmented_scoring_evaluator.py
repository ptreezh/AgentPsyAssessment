#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立评估器分段评分系统
实现5题分段独立评估，只进行分段评分，不进行后续人格分析
"""
import sys
import os
import json
import time
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import statistics
import requests
import re


class OpenRouterClient:
    """
    OpenRouter API客户端
    """
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url

    def evaluate(self, model: str, prompt: str, system_prompt: str = None, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        使用指定模型评估
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.1
            }

            if system_prompt:
                payload["messages"].insert(0, {"role": "system", "content": system_prompt})

            response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            result = response.json()
            return {
                "success": True,
                "response": result["choices"][0]["message"]["content"],
                "model": model,
                "raw_response": result
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "model": model
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Evaluation failed: {str(e)}",
                "model": model
            }


class SegmentedScoringEvaluator:
    """
    分段评分评估器
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY', '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')
        self.client = OpenRouterClient(self.api_key)
        
        # 主评估器列表，按优先级排序，优先选择大上下文模型
        self.models = [
            {"name": "google/gemini-2.0-flash-exp:free", "description": "Google Gemini 2.0 Flash (1M上下文)"},
            {"name": "deepseek/deepseek-r1:free", "description": "DeepSeek R1 (163K上下文)"},
            {"name": "qwen/qwen3-235b-a22b:free", "description": "Qwen3 235B (131K上下文)"},
            {"name": "mistralai/mistral-small-3.2-24b-instruct:free", "description": "Mistral Small (131K上下文)"},
            {"name": "meta-llama/llama-3.3-70b-instruct:free", "description": "Llama 3.3 70B (65K上下文)"},
            {"name": "moonshotai/kimi-k2:free", "description": "Moonshot Kimi K2 (32K上下文)"}
        ]

    def _create_segments(self, questions: List[Dict], segment_size: int = 5) -> List[List[Dict]]:
        """
        将问题列表分段，每段segment_size题
        """
        segments = []
        for i in range(0, len(questions), segment_size):
            segment = questions[i:i+segment_size]
            if len(segment) > 0:  # 确保非空段也被添加
                segments.append(segment)
        return segments

    def _create_segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """
        创建分段评分提示
        """
        prompt = f"""你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**以下问卷回答，评估回答者展现的Big5人格特质。

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

**特别注意：只能使用1、3、5三个整数分数，严禁使用2、4等其他数值！**

**第{segment_number}段问卷内容（{len(segment)}题/共{total_segments}段）：**
"""

        for i, item in enumerate(segment, 1):
            question_data = item.get('question_data', {})
            prompt += f"""
**问题 {i}:**
{question_data.get('mapped_ipip_concept', '')}

**场景 {i}:**
{question_data.get('scenario', '')}

**指令 {i}:**
{question_data.get('prompt_for_agent', '')}

**AI回答 {i}:**
{item.get('extracted_response', '')}

---
"""

        prompt += """
**请返回严格的JSON格式：**
```json
{
  "success": true,
  "segment_number": {segment_number},
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

    def _validate_scores(self, scores: Dict[str, int]) -> Dict[str, int]:
        """
        验证并修正评分（确保只使用1、3、5分）
        """
        valid_scores = {}
        for trait, score in scores.items():
            if score in [1, 3, 5]:
                valid_scores[trait] = score
            else:
                # 修正无效评分
                if score < 2:
                    valid_scores[trait] = 1
                elif score > 4:
                    valid_scores[trait] = 5
                else:
                    valid_scores[trait] = 3  # 2和4修正为3
        return valid_scores

    def _analyze_segment_with_model(self, model_config: Dict, segment: List[Dict], segment_number: int, total_segments: int) -> Dict:
        """
        使用指定模型分析单个分段
        """
        try:
            prompt = self._create_segment_prompt(segment, segment_number, total_segments)

            print(f"    📡 调用 {model_config['name']} 分析段{segment_number}...")
            eval_result = self.client.evaluate(
                model=model_config['name'],
                prompt=prompt,
                system_prompt="你是专业的心理评估分析师。必须严格使用1-3-5评分标准。"
            )

            if not eval_result['success']:
                print(f"      ❌ {model_config['name']} 调用失败: {eval_result.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'segment_number': segment_number,
                    'model': model_config['name'],
                    'error': eval_result.get('error', 'API call failed'),
                    'raw_response': 'API call failed'
                }

            content = eval_result['response']

            # 检查响应是否为空
            if not content or content.strip() == "":
                return {
                    'success': False,
                    'segment_number': segment_number,
                    'model': model_config['name'],
                    'error': 'API响应为空',
                    'raw_response': 'No content'
                }

            # 解析JSON - 提取```json```包裹的内容
            try:
                print(f"      🔍 {model_config['name']} 解析JSON响应...")

                # 先尝试匹配```json```包裹的内容
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"      ✅ {model_config['name']} 找到```json```包裹的内容")
                    result = json.loads(json_str)
                else:
                    # 尝试匹配单独的JSON对象
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        print(f"      ✅ {model_config['name']} 找到JSON对象")
                        result = json.loads(json_str)
                    else:
                        # 尝试直接解析
                        print(f"      ⚠️ {model_config['name']} 尝试直接解析整个响应...")
                        result = json.loads(content)

                print(f"      ✅ {model_config['name']} JSON解析成功")

            except json.JSONDecodeError as e:
                print(f"      ❌ {model_config['name']} JSON解析失败: {str(e)[:100]}")
                return {
                    'success': False,
                    'segment_number': segment_number,
                    'model': model_config['name'],
                    'error': f'JSON解析失败: {str(e)[:100]}',
                    'raw_response': content[:500] if content else 'No content'
                }
            except Exception as e:
                print(f"      ❌ {model_config['name']} 响应处理失败: {str(e)}")
                return {
                    'success': False,
                    'segment_number': segment_number,
                    'model': model_config['name'],
                    'error': f'响应处理失败: {str(e)}',
                    'raw_response': content[:500] if content else 'No content'
                }

            # 验证并修正评分标准
            if 'scores' in result:
                corrected_scores = self._validate_scores(result['scores'])
                
                if corrected_scores != result['scores']:
                    invalid_scores = []
                    for trait in result['scores']:
                        if result['scores'][trait] != corrected_scores[trait]:
                            invalid_scores.append(f"{trait}:{result['scores'][trait]}→{corrected_scores[trait]}")
                    print(f"      ⚠️ {model_config['name']} 修正无效评分: {invalid_scores}")
                
                result['scores'] = corrected_scores

            result['model'] = model_config['name']
            result['segment_number'] = segment_number
            result['processing_time'] = time.time()

            return result

        except Exception as e:
            print(f"      ❌ {model_config['name']} 分析失败: {str(e)}")
            return {
                'success': False,
                'segment_number': segment_number,
                'model': model_config['name'],
                'error': f'分析失败: {str(e)}',
                'raw_response': str(e)
            }

    def _calculate_model_consistency(self, model_results: List[Dict]) -> Dict:
        """
        计算多个模型间的一致性
        """
        if len(model_results) < 2:
            return {"error": "需要至少2个模型的结果"}

        successful_models = [r for r in model_results if r.get('success', False)]
        if len(successful_models) < 2:
            return {"error": f"成功模型数量不足: {len(successful_models)}/{len(model_results)}"}

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        consistency_analysis = {}

        for trait in traits:
            scores = []
            model_names = []

            for result in successful_models:
                if 'scores' in result and trait in result['scores']:
                    scores.append(result['scores'][trait])
                    model_names.append(result['model'])

            if len(scores) >= 2:
                avg_score = statistics.mean(scores)
                max_score = max(scores)
                min_score = min(scores)
                score_range = max_score - min_score

                # 一致性评估
                if score_range == 0:
                    consistency_level = "完全一致"
                    consistency_score = 100
                elif score_range <= 1:
                    consistency_level = "高度一致"
                    consistency_score = 80
                elif score_range <= 2:
                    consistency_level = "中等一致"
                    consistency_score = 60
                else:
                    consistency_level = "差异较大"
                    consistency_score = 40

                consistency_analysis[trait] = {
                    "scores": dict(zip(model_names, scores)),
                    "average": avg_score,
                    "range": score_range,
                    "consistency_level": consistency_level,
                    "consistency_score": consistency_score
                }

        # 计算总体一致性
        overall_scores = [analysis.get('consistency_score', 0) for analysis in consistency_analysis.values()]
        overall_consistency = statistics.mean(overall_scores) if overall_scores else 0

        return {
            "trait_analysis": consistency_analysis,
            "overall_consistency": overall_consistency,
            "successful_models": len(successful_models),
            "total_models": len(model_results),
            "discrepancies": [trait for trait, analysis in consistency_analysis.items() if analysis["range"] > 1]
        }

    def analyze_file_with_three_models(self, file_path: str, output_dir: str) -> Dict:
        """
        使用三个模型独立分析单个文件（保留此方法以保持向后兼容）
        """
        return self.evaluate_file_with_multiple_models(file_path, output_dir)

    def evaluate_file_with_multiple_models(self, file_path: str, output_dir: str) -> Dict:
        """
        使用多个模型评估单个文件（主要方法）
        """
        print(f"📈 开始多模型评估: {Path(file_path).name}")

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取问题
            questions = []
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for item in data['assessment_results']:
                    if isinstance(item, dict):
                        question_data = item.get('question_data', {})
                        if isinstance(question_data, dict):
                            question_text = question_data.get('prompt_for_agent', 
                                question_data.get('mapped_ipip_concept', ''))
                            
                            answer_text = item.get('extracted_response', '')
                            
                            if question_text and answer_text:
                                questions.append({
                                    'question_data': question_data,
                                    'extracted_response': answer_text
                                })

            if len(questions) < 1:
                raise Exception(f"问题数量不足：{len(questions)}")

            # 分段处理（每段5题）
            segment_size = 5
            segments = self._create_segments(questions, segment_size)
            total_segments = len(segments)
            print(f"  📊 {len(questions)}题 -> {total_segments}个分段")

            # 模型评估结果存储
            model_analysis_results = {}

            # 选择前3个模型进行初始评估
            selected_models = self.models[:3]

            # 对每个模型进行独立评估
            for model_config in selected_models:
                print(f"  🤖 使用模型: {model_config['name']} ({model_config['description']})")

                model_segments = []
                segment_results = []

                # 评估每个分段
                for i, segment in enumerate(segments, 1):
                    result = self._analyze_segment_with_model(model_config, segment, i, total_segments)
                    segment_results.append(result)

                    if result['success']:
                        print(f"      ✅ 段{i}: {list(result['scores'].values())}")
                    else:
                        print(f"      ❌ 段{i}: {result.get('error', 'Unknown error')}")

                    time.sleep(3)  # API限制

                # 计算该模型的最终评分
                if segment_results:
                    final_scores = {}
                    for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                        all_scores = []
                        for result in segment_results:
                            if result.get('success') and 'scores' in result:
                                if trait in result['scores']:
                                    all_scores.append(result['scores'][trait])

                        if all_scores:
                            final_scores[trait] = statistics.median(all_scores)
                            final_scores[trait] = int(round(final_scores[trait]))  # 确保是整数

                    model_analysis_results[model_config['name']] = {
                        "segment_results": segment_results,
                        "final_scores": final_scores,
                        "successful_segments": len([r for r in segment_results if r.get('success')]),
                        "total_segments": total_segments
                    }

            # 计算模型间一致性
            print(f"  📊 计算模型一致性...")
            final_scores_list = [
                {"model": model, "scores": results["final_scores"]}
                for model, results in model_analysis_results.items()
            ]
            
            consistency_analysis = self._calculate_model_consistency(final_scores_list)

            # 保存结果
            output_filename = f"{Path(file_path).stem}_segmented_scoring_evaluation.json"
            output_path = os.path.join(output_dir, output_filename)

            analysis_result = {
                "file_info": {
                    "filename": Path(file_path).name,
                    "total_questions": len(questions),
                    "segments_count": total_segments,
                    "questions_per_segment": segment_size,
                    "analysis_date": datetime.now().isoformat()
                },
                "models_used": selected_models,
                "model_results": model_analysis_results,
                "consistency_analysis": consistency_analysis,
                "summary": {
                    "overall_consistency": consistency_analysis.get('overall_consistency', 0),
                    "model_count": len(selected_models),
                    "successful_models": consistency_analysis.get('successful_models', 0)
                }
            }

            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)

            print(f"  💾 结果已保存: {output_filename}")

            # 显示简要结果
            print(f"  📋 评估结果摘要:")
            for model, results in model_analysis_results.items():
                print(f"    {model}: {results['final_scores']} ({results['successful_segments']}/{results['total_segments']}段成功)")

            print(f"  🎯 模型一致性: {consistency_analysis.get('overall_consistency', 0):.1f}%")

            return {
                'success': True,
                'file_path': file_path,
                'output_path': output_path,
                'model_results': model_analysis_results,
                'consistency_analysis': consistency_analysis,
                'consistency_score': consistency_analysis.get('overall_consistency', 0)
            }

        except Exception as e:
            print(f"  ❌ 文件评估失败: {e}")
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def batch_evaluate(self, input_dir: str, output_dir: str = "segmented_scoring_results", max_files: int = None, selected_models: List[str] = None):
        """
        批量评估
        """
        print(f"🚀 开始批量分段评分评估")
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {[m['name'] for m in self.models[:3]]}")
        print(f"📊 每段大小: 5题")
        print(f"⚡ 分段间隔: 3秒")
        print()

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 查找输入文件
        file_pattern = os.path.join(input_dir, "*.json")
        files = glob.glob(file_pattern)

        if max_files:
            files = files[:max_files]

        print(f"📊 找到 {len(files)} 个文件")

        if not files:
            print("❌ 未找到符合条件的文件")
            return

        # 批量处理
        batch_results = []
        overall_consistency_scores = []

        for i, file_path in enumerate(files, 1):
            print(f"📈 [{i}/{len(files)}] 处理: {Path(file_path).name}")

            result = self.evaluate_file_with_multiple_models(file_path, output_dir)
            batch_results.append(result)

            if result['success']:
                overall_consistency_scores.append(result['consistency_score'])
                print(f"   ✅ 一致性: {result['consistency_score']:.1f}%")
            else:
                print(f"   ❌ 失败: {result.get('error', 'Unknown error')}")

        # 完成统计
        print()
        print("📊 批量处理完成")
        print("=" * 60)

        successful_files = [r for r in batch_results if r.get('success', False)]
        print(f"📁 总文件数: {len(files)}")
        print(f"✅ 处理成功: {len(successful_files)}")
        print(f"❌ 处理失败: {len(files) - len(successful_files)}")

        if overall_consistency_scores:
            avg_consistency = statistics.mean(overall_consistency_scores)
            print(f"📈 平均一致性: {avg_consistency:.1f}%")
            print(f"📊 一致性范围: {min(overall_consistency_scores):.1f}% - {max(overall_consistency_scores):.1f}%")

        # 保存批量处理报告
        batch_report = {
            "batch_info": {
                "models": [{"name": m["name"], "description": m["description"]} for m in self.models[:3]],
                "segment_size": 5,
                "processing_date": datetime.now().isoformat(),
                "input_directory": input_dir,
                "output_directory": output_dir
            },
            "input_files": [f for f in files],
            "results": batch_results,
            "statistics": {
                "total_files": len(files),
                "successful_files": len(successful_files),
                "failed_files": len(files) - len(successful_files),
                "average_consistency": statistics.mean(overall_consistency_scores) if overall_consistency_scores else 0,
                "consistency_scores": overall_consistency_scores
            }
        }

        report_path = os.path.join(output_dir, "segmented_scoring_batch_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, ensure_ascii=False, indent=2)

        print(f"📄 批量报告已保存: {report_path}")

        return batch_report


class ScoringConsistencyAnalyzer:
    """
    评分一致性分析器
    """
    def __init__(self):
        pass

    def calculate_consistency(self, model_results: List[Dict]) -> Dict:
        """
        计算多个模型间的一致性
        """
        if len(model_results) < 2:
            return {"error": "需要至少2个模型的结果"}

        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        consistency_analysis = {}

        for trait in traits:
            scores = []
            model_names = []

            for result in model_results:
                if 'scores' in result and trait in result['scores']:
                    scores.append(result['scores'][trait])
                    model_names.append(result['model'])

            if len(scores) >= 2:
                avg_score = statistics.mean(scores)
                max_score = max(scores)
                min_score = min(scores)
                score_range = max_score - min_score

                # 一致性评估
                if score_range == 0:
                    consistency_level = "完全一致"
                    consistency_score = 100
                elif score_range <= 1:
                    consistency_level = "高度一致"
                    consistency_score = 80
                elif score_range <= 2:
                    consistency_level = "中等一致"
                    consistency_score = 60
                else:
                    consistency_level = "差异较大"
                    consistency_score = 40

                consistency_analysis[trait] = {
                    "scores": dict(zip(model_names, scores)),
                    "average": avg_score,
                    "range": score_range,
                    "consistency_level": consistency_level,
                    "consistency_score": consistency_score
                }

        # 计算总体一致性
        overall_scores = [analysis.get('consistency_score', 0) for analysis in consistency_analysis.values()]
        overall_consistency = statistics.mean(overall_scores) if overall_scores else 0

        return {
            "trait_analysis": consistency_analysis,
            "overall_consistency": overall_consistency,
            "successful_models": len(model_results),
            "total_models": len(model_results)
        }


class DisputeResolutionManager:
    """
    分歧处理管理器
    """
    def __init__(self):
        pass

    def identify_disputes(self, all_scores: List[Dict], threshold: int = 1) -> List[Dict]:
        """
        识别评分中的分歧
        """
        # 按问题ID和特质分组评分
        scores_by_question_trait = {}
        for score_record in all_scores:
            qid = score_record.get('question_id')
            # 检查是否包含Big5各个维度的评分
            for trait in ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
                if trait in score_record:
                    key = f"{qid}_{trait}"
                    if key not in scores_by_question_trait:
                        scores_by_question_trait[key] = []
                    scores_by_question_trait[key].append({
                        'question_id': qid,
                        'trait': trait,
                        'score': score_record[trait],
                        'model': score_record.get('model', 'unknown')
                    })

        disputes = []
        for key, scores_list in scores_by_question_trait.items():
            # 提取所有评分
            scores = [record['score'] for record in scores_list]
            if len(scores) < 2:
                continue

            max_score = max(scores)
            min_score = min(scores)
            score_range = max_score - min_score

            if score_range > threshold:
                qid_str, trait = key.split('_', 1)
                qid = int(qid_str)
                disputes.append({
                    "question_id": qid,
                    "trait": trait,
                    "scores": scores,
                    "models": [record['model'] for record in scores_list],
                    "max_diff": score_range,
                    "average_score": statistics.mean(scores)
                })

        return disputes

    def apply_majority_decision(self, scores: List[int]) -> int:
        """
        应用多数决策原则（去除最高分和最低分后取中位数）
        """
        if len(scores) <= 2:
            # 如果只有1或2个评分，直接取平均值并四舍五入
            return round(statistics.mean(scores)) if scores else 0

        # 去除一个最高分和一个最低分
        scores_sorted = sorted(scores)
        if len(scores_sorted) > 2:
            trimmed_scores = scores_sorted[1:-1]  # 去除首尾
        else:
            trimmed_scores = scores_sorted

        # 返回剩余评分的中位数
        if trimmed_scores:
            # 对于多数决策，使用中位数作为最终得分
            return int(statistics.median(trimmed_scores))
        else:
            # 如果修剪后没有评分，返回原评分的平均值
            return round(statistics.mean(scores)) if scores else 0


def main():
    """
    主函数 - 演示用法
    """
    # 创建评估器实例
    evaluator = SegmentedScoringEvaluator()

    # 输入输出目录
    input_dir = "results/readonly-original"
    output_dir = "segmented_scoring_results"

    # 批量评估 (处理部分文件进行测试)
    evaluator.batch_evaluate(input_dir, output_dir, max_files=5)


if __name__ == "__main__":
    main()