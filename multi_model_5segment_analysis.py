#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三模型5题分段独立分析脚本
每个测评报告使用三个不同的云评估模型独立分析，并对照一致性
"""

import sys
import os
import json
import time
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import statistics

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['DASHSCOPE_API_KEY'] = 'sk-ded837735b3c44599a9bc138da561c27'

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class MultiModel5SegmentAnalyzer:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # 三个模型配置
        self.models = [
            {"name": "qwen-long", "description": "通义千问长文本模型"},
            {"name": "deepseek-v3.2-exp", "description": "DeepSeek高级模型"},
            {"name": "Moonshot-Kimi-K2-Instruct", "description": "月之暗面Kimi模型"}
        ]

    def _create_5segment_prompt(self, segment: List[Dict], segment_number: int, total_segments: int) -> str:
        """创建5题分段分析提示"""
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

**特别注意：只能使用1、3、5三个整数分数，禁止使用2、4等其他数值！**

**第{segment_number}段问卷内容（{len(segment)}题/共{total_segments}段）：**
"""

        for i, item in enumerate(segment, 1):
            prompt += f"""
**问题 {i}:**
{item['question']}

**回答 {i}:**
{item['answer']}

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

    def _analyze_segment_with_model(self, model_config: Dict, segment: List[Dict], segment_number: int, total_segments: int) -> Dict:
        """使用指定模型分析单个分段"""
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            prompt = self._create_5segment_prompt(segment, segment_number, total_segments)

            print(f"    📡 调用 {model_config['name']} 分析段{segment_number}...")
            response = client.chat.completions.create(
                model=model_config['name'],
                messages=[
                    {"role": "system", "content": "你是专业的心理评估分析师。必须严格使用1-3-5评分标准。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )

            content = response.choices[0].message.content

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
                import re
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

            # 验证评分标准
            if 'scores' in result:
                invalid_scores = []
                for trait, score in result['scores'].items():
                    if score not in [1, 3, 5]:
                        invalid_scores.append(f"{trait}:{score}")
                        # 修正无效评分
                        if score < 2:
                            result['scores'][trait] = 1
                        elif score > 4:
                            result['scores'][trait] = 5
                        else:
                            result['scores'][trait] = 3

                if invalid_scores:
                    print(f"      ⚠️ {model_config['name']} 修正无效评分: {invalid_scores}")

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

    def _calculate_mbti_type(self, scores: Dict) -> str:
        """根据Big5评分计算MBTI类型 - 修复版本"""
        try:
            # Big5到MBTI的映射
            openness = scores.get('openness_to_experience', 3)
            conscientiousness = scores.get('conscientiousness', 3)
            extraversion = scores.get('extraversion', 3)
            agreeableness = scores.get('agreeableness', 3)
            neuroticism = scores.get('neuroticism', 3)

            # I/E维度
            I_E = 'I' if extraversion <= 3 else 'E'

            # S/N维度 - 基于开放性
            S_N = 'N' if openness >= 4 else 'S'

            # T/F维度 - 基于宜人性
            T_F = 'F' if agreeableness >= 4 else 'T'

            # J/P维度 - 基于尽责性
            J_P = 'J' if conscientiousness >= 4 else 'P'

            return f"{I_E}{S_N}{T_F}{J_P}"

        except Exception as e:
            print(f"    ❌ MBTI转换失败: {e}")
            return "UNKNOWN"

    def _calculate_model_consistency(self, model_results: List[Dict]) -> Dict:
        """计算三个模型间的一致性"""
        if len(model_results) != 3:
            return {"error": "需要恰好3个模型的结果"}

        successful_models = [r for r in model_results if r.get('success', False)]
        if len(successful_models) < 2:
            return {"error": "成功模型数量不足"}

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
            "total_models": 3
        }

    def analyze_file_with_three_models(self, file_path: str, output_dir: str) -> Dict:
        """使用三个模型独立分析单个文件"""
        print(f"📈 开始三模型分析: {Path(file_path).name}")

        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取问题
            questions = []
            if 'assessment_results' in data and isinstance(data['assessment_results'], list):
                for item in data['assessment_results']:
                    if isinstance(item, dict) and 'question_data' in item:
                        question_data = item['question_data']
                        if isinstance(question_data, dict):
                            question_text = question_data.get('prompt_for_agent', question_data.get('mapped_ipip_concept', ''))

                            answer_text = ''
                            if 'extracted_response' in item and item['extracted_response']:
                                answer_text = item['extracted_response']
                            elif 'conversation_log' in item and isinstance(item['conversation_log'], list):
                                for msg in item['conversation_log']:
                                    if isinstance(msg, dict) and msg.get('role') == 'assistant':
                                        answer_text = msg.get('content', '')
                                        break

                            if question_text and answer_text:
                                questions.append({
                                    'question': question_text,
                                    'answer': answer_text
                                })

            if len(questions) < 5:
                raise Exception(f"问题数量不足：{len(questions)}")

            # 分段处理（每段5题）
            segment_size = 5
            segments = []
            for i in range(0, len(questions), segment_size):
                segment = questions[i:i+segment_size]
                if len(segment) == segment_size:
                    segments.append(segment)

            total_segments = len(segments)
            print(f"  📊 {len(questions)}题 -> {total_segments}个分段")

            # 三个模型的结果存储
            model_analysis_results = {}

            # 对每个模型进行独立分析
            for model_config in self.models:
                print(f"  🤖 使用模型: {model_config['name']} ({model_config['description']})")

                model_segments = []
                segment_results = []

                # 分析每个分段
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
                            if result['success'] and 'scores' in result:
                                all_scores.append(result['scores'][trait])

                        if all_scores:
                            final_scores[trait] = statistics.median(all_scores)
                            final_scores[trait] = int(final_scores[trait])  # 转换为整数

                    # 生成MBTI类型
                    mbti_type = self._calculate_mbti_type(final_scores)

                    model_analysis_results[model_config['name']] = {
                        "segment_results": segment_results,
                        "final_scores": final_scores,
                        "mbti_type": mbti_type,
                        "successful_segments": len([r for r in segment_results if r['success']]),
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
            output_filename = f"{Path(file_path).stem}_multi_model_5segment_analysis.json"
            output_path = os.path.join(output_dir, output_filename)

            analysis_result = {
                "file_info": {
                    "filename": Path(file_path).name,
                    "total_questions": len(questions),
                    "segments_count": total_segments,
                    "questions_per_segment": segment_size,
                    "analysis_date": datetime.now().isoformat()
                },
                "models_used": self.models,
                "model_results": model_analysis_results,
                "consistency_analysis": consistency_analysis,
                "summary": {
                    "overall_consistency": consistency_analysis.get('overall_consistency', 0),
                    "model_count": len(self.models),
                    "successful_models": consistency_analysis.get('successful_models', 0)
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)

            print(f"  💾 结果已保存: {output_filename}")

            # 显示简要结果
            print(f"  📋 分析结果摘要:")
            for model, results in model_analysis_results.items():
                print(f"    {model}: {results['final_scores']} -> {results['mbti_type']} ({results['successful_segments']}/{results['total_segments']}段成功)")

            print(f"  🎯 模型一致性: {consistency_analysis.get('overall_consistency', 0):.1f}%")

            return {
                'success': True,
                'file_path': file_path,
                'output_path': output_path,
                'model_results': model_analysis_results,
                'consistency_score': consistency_analysis.get('overall_consistency', 0)
            }

        except Exception as e:
            print(f"  ❌ 文件分析失败: {e}")
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def batch_analyze(self, input_dir: str, output_dir: str = "multi_model_5segment_results", max_files: int = None):
        """批量分析"""
        print(f"🚀 开始三模型5题分段批量分析")
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {[m['name'] for m in self.models]}")
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

            result = self.analyze_file_with_three_models(file_path, output_dir)
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
                "models": [{"name": m["name"], "description": m["description"]} for m in self.models],
                "segment_size": 5,
                "processing_date": datetime.now().isoformat(),
                "input_directory": input_dir,
                "output_directory": output_dir
            },
            "input_files": files,
            "results": batch_results,
            "statistics": {
                "total_files": len(files),
                "successful_files": len(successful_files),
                "failed_files": len(files) - len(successful_files),
                "average_consistency": statistics.mean(overall_consistency_scores) if overall_consistency_scores else 0,
                "consistency_scores": overall_consistency_scores
            }
        }

        with open(os.path.join(output_dir, "multi_model_5segment_batch_report.json"), 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, ensure_ascii=False, indent=2)

        print(f"📄 批量报告已保存: multi_model_5segment_batch_report.json")

        return batch_report

def main():
    """主函数"""
    analyzer = MultiModel5SegmentAnalyzer()

    # 输入输出目录
    input_dir = "results/results"
    output_dir = "multi_model_5segment_results"

    # 批量分析 (处理所有剩余文件)
    analyzer.batch_analyze(input_dir, output_dir, max_files=547)

if __name__ == "__main__":
    main()