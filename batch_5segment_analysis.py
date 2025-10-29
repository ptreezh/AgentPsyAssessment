#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5题分段批量分析脚本 - 重新分析所有测评报告
使用已验证的1-3-5评分标准
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

class FiveSegmentAnalyzer:
    def __init__(self, model: str = "qwen-long"):
        self.model = model
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # 统计信息
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_segments': 0,
            'successful_segments': 0,
            'failed_segments': 0,
            'score_distribution': {1: 0, 3: 0, 5: 0},
            'processing_start': None,
            'processing_end': None
        }

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

**严格评分标准（必须使用）：**
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

    def _analyze_segment(self, segment: List[Dict], segment_number: int, total_segments: int) -> Dict:
        """分析单个分段"""
        try:
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            prompt = self._create_5segment_prompt(segment, segment_number, total_segments)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的心理评估分析师。必须严格使用1-3-5评分标准。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )

            content = response.choices[0].message.content
            print(f"  📝 API响应长度: {len(content) if content else 0} 字符")

            # 检查响应是否为空
            if not content or content.strip() == "":
                print(f"  ❌ API响应为空")
                return {
                    'success': False,
                    'segment_number': segment_number,
                    'error': 'API响应为空',
                    'raw_response': 'No content'
                }

            # 解析JSON - 提取```json```包裹的内容
            try:
                import re
                print(f"  🔍 尝试解析JSON响应...")

                # 先尝试匹配```json```包裹的内容
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"  ✅ 找到```json```包裹的内容")
                    result = json.loads(json_str)
                else:
                    # 尝试匹配单独的JSON对象
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        print(f"  ✅ 找到JSON对象")
                        result = json.loads(json_str)
                    else:
                        # 尝试直接解析
                        print(f"  ⚠️ 尝试直接解析整个响应...")
                        result = json.loads(content)

                print(f"  ✅ JSON解析成功")

            except json.JSONDecodeError as e:
                print(f"  ❌ JSON解析失败: {str(e)[:100]}")
                print(f"  📄 响应内容预览: {content[:200] if content else 'No content'}...")
                return {
                    'success': False,
                    'segment_number': segment_number,
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
                    print(f"  ⚠️ 发现并修正无效评分: {invalid_scores}")

            result['model'] = self.model
            result['segment_number'] = segment_number
            result['processing_time'] = time.time()

            return result

        except Exception as e:
            return {
                'success': False,
                'segment_number': segment_number,
                'error': f'分析失败: {str(e)}',
                'raw_response': str(e)
            }

    def analyze_file(self, file_path: str, output_dir: str) -> Dict:
        """分析单个文件"""
        self.stats['total_files'] += 1

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
            segment_results = []

            print(f"  📊 {Path(file_path).name}: {len(questions)}题 -> {total_segments}个分段")

            # 分析每个分段
            for i, segment in enumerate(segments, 1):
                self.stats['total_segments'] += 1

                result = self._analyze_segment(segment, i, total_segments)
                segment_results.append(result)

                if result['success']:
                    self.stats['successful_segments'] += 1
                    # 统计评分分布
                    for score in result['scores'].values():
                        self.stats['score_distribution'][score] += 1

                    print(f"    ✅ 段{i} ({len(segment)}题): {list(result['scores'].values())}")
                else:
                    self.stats['failed_segments'] += 1
                    print(f"    ❌ 段{i}: {result.get('error', 'Unknown error')}")

                time.sleep(3)  # API限制

            # 计算最终评分
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

                # 保存结果
                output_filename = f"{Path(file_path).stem}_5segment_analysis.json"
                output_path = os.path.join(output_dir, output_filename)

                analysis_result = {
                    "file_info": {
                        "filename": Path(file_path).name,
                        "total_questions": len(questions),
                        "segments_count": total_segments,
                        "questions_per_segment": segment_size,
                        "model_used": self.model,
                        "analysis_date": datetime.now().isoformat()
                    },
                    "segment_results": segment_results,
                    "final_scores": final_scores,
                    "mbti_type": mbti_type,
                    "validation_stats": self._calculate_validation_stats(segment_results),
                    "stats": self._get_stats_summary()
                }

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_result, f, ensure_ascii=False, indent=2)

                self.stats['processed_files'] += 1
                print(f"  💾 结果已保存: {output_filename}")

                return {
                    'success': True,
                    'file_path': file_path,
                    'output_path': output_path,
                    'total_segments': total_segments,
                    'successful_segments': len([r for r in segment_results if r['success']]),
                    'final_scores': final_scores,
                    'mbti_type': mbti_type
                }
            else:
                raise Exception("没有分段结果")

        except Exception as e:
            self.stats['failed_files'] += 1
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e)
            }

    def _calculate_mbti_type(self, scores: Dict) -> str:
        """根据Big5评分计算MBTI类型"""
        try:
            # Big5到MBTI的映射
            openness = scores.get('openness_to_experience', 3)
            conscientiousness = scores.get('conscientiousness', 3)
            extraversion = scores.get('extraversion', 3)
            agreeableness = scores.get('agreeableness', 3)
            neuroticism = scores.get('neuroticism', 3)

            # I/E维度
            I_E = 'I' if extraversion <= 3 else 'E'

            # S/N维度
            S_N = 'S' if neuroticism <= 3 else 'N'

            # T/F维度 - 基于思维与情感的平衡
            T_F = 'T' if conscientiousness >= openness_to_experience else 'F'

            # J/P维度 - 基于组织与适应性的平衡
            J_P = 'J' if conscientiousness >= 4 and openness_to_experience <= 3 else 'P'

            return f"{I_E}{S_N}{T_F}{J_P}"

        except Exception:
            return "UNKNOWN"

    def _calculate_validation_stats(self, segment_results: List[Dict]) -> Dict:
        """计算验证统计"""
        successful_results = [r for r in segment_results if r.get('success', False)]

        if not successful_results:
            return {
                'total_segments': len(segment_results),
                'successful_segments': 0,
                'success_rate': 0.0,
                'score_diversity': 0,
                'all_three_count': 0,
                'avg_score': 0,
                'valid_scores_ratio': 0
            }

        success_rate = len(successful_results) / len(segment_results) * 100

        # 评分多样性
        all_scores = []
        for result in successful_results:
            if 'scores' in result:
                all_scores.extend(result['scores'].values())

        score_diversity = len(set(all_scores))

        # 全3分分段数量
        all_three_count = 0
        for result in successful_results:
            if 'scores' in result:
                scores = result['scores'].values()
                if all(score == 3 for score in scores):
                    all_three_count += 1

        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

        # 1-3-5评分标准符合率
        valid_scores = sum(1 for score in all_scores if score in [1, 3, 5])
        valid_scores_ratio = (valid_scores / len(all_scores) * 100) if all_scores else 0

        return {
            'total_segments': len(segment_results),
            'successful_segments': len(successful_results),
            'success_rate': success_rate,
            'score_diversity': score_diversity,
            'unique_scores': sorted(list(set(all_scores))),
            'all_three_count': all_three_count,
            'avg_score': avg_score,
            'valid_scores_ratio': valid_scores_ratio,
            'credibility_score': self._calculate_credibility_score(success_rate, score_diversity, all_three_count, len(segment_results))
        }

    def _calculate_credibility_score(self, success_rate: float, score_diversity: int, all_three_count: int, total_segments: int) -> int:
        """计算可信度分数"""
        if total_segments == 0:
            return 0

        base_score = success_rate
        diversity_bonus = min(score_diversity * 10, 40)
        all_three_penalty = (all_three_count / total_segments) * 50

        final_score = min(100, int(base_score + diversity_bonus - all_three_penalty))
        return max(0, final_score)

    def _get_stats_summary(self) -> Dict:
        """获取统计摘要"""
        success_rate = (self.stats['successful_segments'] / max(1, self.stats['total_segments'])) * 100
        return {
            'total_files': self.stats['total_files'],
            'processed_files': self.stats['processed_files'],
            'failed_files': self.stats['failed_files'],
            'total_segments': self.stats['total_segments'],
            'successful_segments': self.stats['successful_segments'],
            'failed_segments': self.stats['failed_segments'],
            'success_rate': success_rate,
            'score_distribution': self.stats['score_distribution'],
            'processing_time': None
        }

    def batch_analyze(self, input_dir: str, output_dir: str = "5segment_results", file_pattern: str = "*.json", max_files: int = None):
        """批量分析"""
        print(f"🚀 开始5题分段批量分析")
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        print(f"🤖 使用模型: {self.model}")
        print(f"📊 每段大小: 5题")
        print(f"⚡ 分段间隔: 3秒")
        print()

        self.stats['processing_start'] = datetime.now()

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 查找输入文件
        file_pattern = os.path.join(input_dir, file_pattern)
        files = glob.glob(file_pattern)

        if max_files:
            files = files[:max_files]

        print(f"📊 找到 {len(files)} 个文件")

        if not files:
            print("❌ 未找到符合条件的文件")
            return

        # 批量处理
        batch_results = []

        for i, file_path in enumerate(files, 1):
            print(f"📈 [{i}/{len(files)}] 处理: {Path(file_path).name}")

            result = self.analyze_file(file_path, output_dir)
            batch_results.append(result)

            # 显示进度
            successful = len([r for r in batch_results if r.get('success', False)])
            print(f"   成功: {successful}/{len(batch_results)}")

        # 完成统计
        self.stats['processing_end'] = datetime.now()
        if self.stats['processing_start'] and self.stats['processing_end']:
            self.stats['processing_time'] = (self.stats['processing_end'] - self.stats['processing_start']).total_seconds()

        print()
        print("📊 批量处理完成")
        print("=" * 50)
        stats = self._get_stats_summary()
        print(f"📁 总文件数: {stats['total_files']}")
        print(f"✅ 处理成功: {stats['processed_files']}")
        print(f"❌ 处理失败: {stats['failed_files']}")
        print(f"📊 总分段数: {stats['total_segments']}")
        print(f"✅ 成功分段: {stats['successful_segments']}")
        print(f"❌ 失败分段: {stats['failed_segments']}")
        print(f"📈 成功率: {stats['success_rate']:.1f}%")

        if stats['score_distribution']:
            total_scores = sum(stats['score_distribution'].values())
            print(f"📊 评分分布: {stats['score_distribution']}")
            print(f"   1分: {stats['score_distribution'][1]/total_scores:.1f}%")
            print(f"   3分: {stats['score_distribution'][3]/total_scores:.1f}%")
            print(f"   5分: {stats['score_distribution'][5]/total_scores:.1f}%")

        # 保存批量处理报告
        batch_report = {
            "batch_info": {
                "model": self.model,
                "segment_size": 5,
                "processing_date": datetime.now().isoformat(),
                "processing_time": stats.get('processing_time')
            },
            "input_files": files,
            "results": batch_results,
            "stats": stats
        }

        with open(os.path.join(output_dir, "batch_5segment_report.json"), 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, ensure_ascii=False, indent=2)

        print(f"📄 批量报告已保存: batch_5segment_report.json")

        return batch_report

def main():
    """主函数"""
    analyzer = FiveSegmentAnalyzer(model="qwen-long")

    # 输入输出目录
    input_dir = "results/results"
    output_dir = "5segment_results"

    # 批量分析
    analyzer.batch_analyze(input_dir, output_dir, max_files=10)  # 先处理10个文件测试

if __name__ == "__main__":
    main()