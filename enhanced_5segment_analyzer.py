#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版5题分段分析器 - 修复技术问题，加强可信度验证
"""

import sys
import os
import json
import hashlib
import time
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 强制无缓冲输出
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 设置环境变量
os.environ['PYTHONUNBUFFERED'] = '1'
# API密钥将通过环境变量传递

class Enhanced5SegmentAnalyzer:
    def __init__(self, models: List[str] = None):
        self.models = models or ["qwen-max"]
        self.segment_size = 5
        self.delay_between_segments = 1

        # 缓存设置
        self.cache_dir = Path("enhanced_5segment_cache")
        self.cache_dir.mkdir(exist_ok=True)

        # 可信度验证参数
        self.validation_stats = {
            'total_segments': 0,
            'successful_segments': 0,
            'score_variations': [],  # 记录每次评分的变异度
            'all_three_count': 0,     # 全3分的段数
            'diverse_score_count': 0, # 评分多样化的段数
            'evidence_quality_scores': [],  # 证据质量评分
            'processing_times': []
        }

        print(f"🚀 增强版5题分段分析器已初始化")
        print(f"🤖 使用模型: {', '.join(self.models)}")
        print(f"📊 配置: {self.segment_size}题/段, {self.delay_between_segments}s延迟")
        print(f"🔑 API密钥已配置")
        print(f"✅ 可信度验证已启用")
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
                    print(f"  📦 缓存命中: {cache_key[:8]}...")
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

    def _load_questions_from_file(self, file_path: Path) -> List[Dict]:
        """从文件加载问题数据"""
        print(f"📂 加载文件: {file_path.name}")

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

        questions = []

        # 处理评估结果格式
        if 'assessment_results' in data and isinstance(data['assessment_results'], list):
            for item in data['assessment_results']:
                if isinstance(item, dict) and 'question_data' in item:
                    question_data = item['question_data']

                    if isinstance(question_data, dict):
                        # 提取问题文本
                        question_text = question_data.get('prompt_for_agent',
                                           question_data.get('mapped_ipip_concept', ''))

                        # 提取回答文本
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
                                'question': question_text.strip(),
                                'answer': answer_text.strip()
                            })

        print(f"✅ 成功提取 {len(questions)} 个问题")
        return questions

    def _create_enhanced_prompt(self, segment: List[Dict], segment_number: int) -> str:
        """创建增强的评估提示"""
        prompt = f"""【重要：你是心理评估分析师，不是被测试者】

你是专业的心理评估分析师，专门分析AI代理的人格特征。你的任务是**分析**以下问卷回答，评估回答者展现的Big5人格特质。

**关键提醒：**
- ❌ 你不是被测试者，不要回答问卷问题
- ❌ 不要混淆角色，你是评估分析师
- ✅ 专注于分析回答中的人格特征
- ✅ 忽略角色扮演内容，专注实际行为倾向

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠、目标导向
3. **外向性(E)**：社交活跃度、能量来源、外向程度
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向（反向计分）

**评分标准（1-5分）：**
- 1分：极低表现（明显缺乏该特质）
- 2分：较低表现（倾向缺乏）
- 3分：中等表现（平衡或不确定）
- 4分：较高表现（倾向具备）
- 5分：极高表现（明显具备该特质）

**评估任务：**
分析以下第{segment_number}段（{len(segment)}题）的问卷回答：

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
**分析要求：**
1. 基于回答内容，评估每个Big5维度
2. 寻找具体的行为证据和语言特征
3. 给出差异化评分，避免默认3分
4. 提供具体的评估依据

**输出格式（严格JSON）：**
```json
{
  "success": true,
  "segment_number": 分段编号,
  "analysis_summary": "简要分析总结",
  "scores": {
    "openness_to_experience": 1-5整数,
    "conscientiousness": 1-5整数,
    "extraversion": 1-5整数,
    "agreeableness": 1-5整数,
    "neuroticism": 1-5整数
  },
  "evidence": {
    "openness_to_experience": "具体的文字证据",
    "conscientiousness": "具体的文字证据",
    "extraversion": "具体的文字证据",
    "agreeableness": "具体的文字证据",
    "neuroticism": "具体的文字证据"
  },
  "confidence": "high/medium/low"
}
```
"""

        return prompt

    def _validate_analysis_result(self, result: Dict) -> Dict:
        """验证分析结果的可信度"""
        validation = {
            'valid': True,
            'issues': [],
            'score_diversity': 0,
            'evidence_quality': 0,
            'confidence_level': 'high'
        }

        # 检查必需字段
        required_fields = ['success', 'scores', 'evidence']
        for field in required_fields:
            if field not in result:
                validation['issues'].append(f"缺少必需字段: {field}")
                validation['valid'] = False

        if not validation['valid']:
            validation['confidence_level'] = 'low'
            return validation

        # 检查评分范围
        scores = result.get('scores', {})
        for trait, score in scores.items():
            if not isinstance(score, int) or score < 1 or score > 5:
                validation['issues'].append(f"无效评分: {trait} = {score}")
                validation['valid'] = False

        # 计算评分多样性
        unique_scores = set(scores.values())
        validation['score_diversity'] = len(unique_scores)

        # 检查是否全3分
        if len(unique_scores) == 1 and 3 in unique_scores:
            validation['issues'].append("所有评分均为3分，缺乏差异化")
            validation['confidence_level'] = 'low'
            self.validation_stats['all_three_count'] += 1
        else:
            self.validation_stats['diverse_score_count'] += 1

        # 检查证据质量
        evidence = result.get('evidence', {})
        evidence_length = 0
        for trait, ev in evidence.items():
            evidence_length += len(ev)

        validation['evidence_quality'] = min(evidence_length // 50, 10)  # 0-10分

        if evidence_length < 100:
            validation['issues'].append("证据质量不足")
            if validation['confidence_level'] == 'high':
                validation['confidence_level'] = 'medium'

        return validation

    def _analyze_segment(self, questions: List[Dict], segment_number: int, model: str) -> Dict:
        """分析单个分段"""
        start_time = time.time()
        self.validation_stats['total_segments'] += 1

        # 检查缓存
        cache_key = self._create_cache_key(questions, model)
        cached_result = self._load_cache(cache_key)
        if cached_result:
            return cached_result

        print(f"  🔍 分析段{segment_number}: {model} ({len(questions)}题)")

        try:
            import openai
            client = openai.OpenAI(
                api_key=os.getenv('DASHSCOPE_API_KEY'),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            prompt = self._create_enhanced_prompt(questions, segment_number)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是专业的心理评估分析师，专注于分析他人的人格特征。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )

            analysis_content = response.choices[0].message.content
            print(f"  📝 API响应长度: {len(analysis_content)} 字符")

            # 解析结果
            result = self._parse_response(analysis_content, segment_number)

            if result['success']:
                # 验证结果质量
                validation = self._validate_analysis_result(result)
                result['validation'] = validation

                if validation['valid']:
                    self.validation_stats['successful_segments'] += 1
                    self.validation_stats['score_variations'].append(validation['score_diversity'])
                    self.validation_stats['evidence_quality_scores'].append(validation['evidence_quality'])

                    processing_time = time.time() - start_time
                    self.validation_stats['processing_times'].append(processing_time)

                    print(f"  ✅ 段{segment_number} 分析成功")
                    print(f"    评分分布: {set(result['scores'].values())}")
                    print(f"    证据质量: {validation['evidence_quality']}/10")
                    print(f"    置信度: {validation['confidence_level']}")

                    # 保存缓存
                    self._save_cache(cache_key, result)

                else:
                    print(f"  ⚠️ 段{segment_number} 验证失败: {', '.join(validation['issues'])}")
                    result['success'] = False
                    result['error'] = '; '.join(validation['issues'])

            else:
                print(f"  ❌ 段{segment_number} 分析失败: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            print(f"  💥 段{segment_number} 异常: {e}")
            return {
                'success': False,
                'segment_number': segment_number,
                'model': model,
                'error': str(e)
            }

    def _parse_response(self, response_content: str, segment_number: int) -> Dict:
        """解析API响应"""
        try:
            # 提取JSON部分
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = response_content

            # 清理JSON
            json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

            result = json.loads(json_str)
            result['segment_number'] = segment_number
            result['raw_response_length'] = len(response_content)

            return result

        except Exception as e:
            return {
                'success': False,
                'segment_number': segment_number,
                'error': f'JSON解析失败: {str(e)}',
                'raw_response_length': len(response_content)
            }

    def analyze_file(self, file_path: Path, output_dir: Path) -> Dict:
        """分析单个文件"""
        start_time = time.time()
        print(f"\n🚀 开始5题分段分析: {file_path.name}")

        try:
            # 加载问题
            questions = self._load_questions_from_file(file_path)
            if not questions:
                return {
                    'success': False,
                    'file': str(file_path),
                    'error': '没有找到有效问题'
                }

            # 分段
            segments = []
            for i in range(0, len(questions), self.segment_size):
                segment = questions[i:i+self.segment_size]
                if len(segment) == self.segment_size:
                    segments.append(segment)

            if not segments:
                return {
                    'success': False,
                    'file': str(file_path),
                    'error': f'问题数量({len(questions)})不是{self.segment_size}的倍数'
                }

            print(f"📊 {len(questions)}题分为{len(segments)}段")

            # 分析各段
            all_results = {}
            for model in self.models:
                print(f"\n🤖 处理模型: {model}")
                model_results = []

                for segment in segments:
                    segment_num = len(model_results) + 1
                    result = self._analyze_segment(segment, segment_num, model)
                    model_results.append(result)

                    # 段间延迟
                    if segment_num < len(segments):
                        time.sleep(self.delay_between_segments)

                all_results[model] = model_results

            # 计算最终评分
            final_scores = self._calculate_final_scores(all_results)
            mbti_type = self._calculate_mbti(final_scores)

            # 计算模型一致性
            model_consistency = self._calculate_model_consistency(all_results)

            # 计算处理时间
            processing_time = time.time() - start_time

            result = {
                'success': True,
                'file': str(file_path),
                'processing_time': processing_time,
                'analysis_info': {
                    'segment_size': self.segment_size,
                    'total_segments': len(segments),
                    'models_count': len(self.models),
                    'total_questions': len(questions)
                },
                'final_scores': final_scores,
                'mbti_type': mbti_type,
                'model_consistency': model_consistency,
                'model_results': all_results,
                'validation_stats': self._get_validation_summary()
            }

            # 保存结果
            output_file = output_dir / f"{file_path.stem}_enhanced_5segment.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 5题分段分析完成: {output_file}")
            print(f"⏱️  处理时间: {processing_time:.1f} 秒")
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

    def _calculate_final_scores(self, all_results: Dict) -> Dict:
        """计算最终评分"""
        trait_scores = {}

        for model, results in all_results.items():
            for result in results:
                if result.get('success', False) and 'scores' in result:
                    for trait, score in result['scores'].items():
                        if trait not in trait_scores:
                            trait_scores[trait] = []
                        trait_scores[trait].append(score)

        # 计算平均分
        final_scores = {}
        for trait, scores in trait_scores.items():
            if scores:
                final_scores[trait] = round(statistics.mean(scores))
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

    def _calculate_model_consistency(self, all_results: Dict) -> Dict:
        """计算模型一致性"""
        consistency = {}
        traits = ['openness_to_experience', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

        for trait in traits:
            model_scores = []

            for model, results in all_results.items():
                trait_avg = []
                for result in results:
                    if result.get('success', False) and 'scores' in result:
                        score = result['scores'].get(trait, 3)
                        trait_avg.append(score)

                if trait_avg:
                    model_scores.append(statistics.mean(trait_avg))

            if len(model_scores) >= 2:
                max_score = max(model_scores)
                min_score = min(model_scores)
                consistency[trait] = max(0, 100 - (max_score - min_score) * 20)
            else:
                consistency[trait] = 100

        return consistency

    def _get_validation_summary(self) -> Dict:
        """获取验证统计摘要"""
        stats = self.validation_stats

        if stats['total_segments'] == 0:
            return {'status': 'no_data'}

        success_rate = (stats['successful_segments'] / stats['total_segments']) * 100
        diverse_rate = (stats['diverse_score_count'] / max(1, stats['successful_segments'])) * 100
        avg_processing_time = statistics.mean(stats['processing_times']) if stats['processing_times'] else 0
        avg_evidence_quality = statistics.mean(stats['evidence_quality_scores']) if stats['evidence_quality_scores'] else 0

        return {
            'total_segments': stats['total_segments'],
            'successful_segments': stats['successful_segments'],
            'success_rate': success_rate,
            'diverse_score_rate': diverse_rate,
            'all_three_count': stats['all_three_count'],
            'avg_processing_time': avg_processing_time,
            'avg_evidence_quality': avg_evidence_quality,
            'credibility_score': self._calculate_credibility_score()
        }

    def _calculate_credibility_score(self) -> int:
        """计算整体可信度分数（0-100）"""
        stats = self.validation_stats

        if stats['total_segments'] == 0:
            return 0

        success_rate = stats['successful_segments'] / stats['total_segments']
        diverse_rate = stats['diverse_score_count'] / max(1, stats['successful_segments'])
        avg_evidence = statistics.mean(stats['evidence_quality_scores']) if stats['evidence_quality_scores'] else 0

        # 综合评分
        credibility = (success_rate * 40 + diverse_rate * 40 + (avg_evidence / 10) * 20)
        return min(100, int(credibility))

def test_enhanced_5segment():
    """测试增强版5题分段分析器"""
    print("🧪 测试增强版5题分段分析器...")

    analyzer = Enhanced5SegmentAnalyzer(models=["qwen-max"])

    # 测试文件
    test_file = Path("results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json")
    output_dir = Path("enhanced_5segment_results")
    output_dir.mkdir(exist_ok=True)

    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return

    # 执行分析
    result = analyzer.analyze_file(test_file, output_dir)

    if result['success']:
        print(f"\n🎉 测试成功!")
        print(f"📊 可信度分数: {result['validation_stats']['credibility_score']}/100")
        print(f"📈 成功率: {result['validation_stats']['success_rate']:.1f}%")
        print(f"🎯 评分多样性: {result['validation_stats']['diverse_score_rate']:.1f}%")
        print(f"📝 平均证据质量: {result['validation_stats']['avg_evidence_quality']:.1f}/10")

        # 检查是否有全3分问题
        if result['validation_stats']['all_three_count'] > 0:
            print(f"⚠️ 警告: 发现 {result['validation_stats']['all_three_count']} 个全3分段")
        else:
            print(f"✅ 没有全3分段问题")

    else:
        print(f"❌ 测试失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_enhanced_5segment()