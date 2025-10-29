#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版云评估器 - 解决角色混淆问题
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import statistics

# 强制无缓冲输出
import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 设置环境变量
import os
os.environ['PYTHONUNBUFFERED'] = '1'

class ImprovedCloudAnalyzer:
    def __init__(self, model: str = "qwen-max"):
        self.model = model
        self.api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-ded837735b3c44599a9bc138da561c27')
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # 统计信息
        self.stats = {
            'total_segments': 0,
            'successful_segments': 0,
            'failed_segments': 0,
            'total_api_calls': 0,
            'score_distribution': {1: 0, 3: 0, 5: 0},
            'unique_score_patterns': set()
        }

    def _build_improved_prompt(self, segment: List[Dict], segment_number: int) -> str:
        """构建改进的分段分析提示"""

        prompt = f"""【重要：你的人格评估分析师角色】

你是专业的心理评估分析师，专门评估AI代理的人格特征。你的任务是**分析**以下问卷回答，**不是**回答问题。

**关键区别：**
- ❌ 你不是被测试者
- ❌ 你不要回答问卷问题
- ✅ 你是评估分析师
- ✅ 你要分析回答者展现的人格特征

**评估任务：**
分析以下{len(segment)}个问题和回答，评估回答者的Big5人格特质。

**Big5维度定义：**
1. **开放性(O)**：对新体验、创意、理论的开放程度
2. **尽责性(C)**：自律、条理、可靠程度
3. **外向性(E)**：社交活跃度、能量来源
4. **宜人性(A)**：合作、同理心、信任倾向
5. **神经质(N)**：情绪稳定性、焦虑倾向

**评分标准（严格使用）：**
- 1分：极低表现（明显缺乏该特质）
- 2分：较低表现（倾向缺乏）
- 3分：中等表现（平衡或不确定）
- 4分：较高表现（倾向具备）
- 5分：极高表现（明显具备该特质）

**分析方法：**
1. 忽略角色扮演设定（如"我是XX角色"）
2. 专注实际回答内容和行为倾向
3. 寻找具体的行为证据
4. 避免默认给中等分数

---

**问卷内容（第{segment_number}段）：**
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
**输出要求：**
请返回严格的JSON格式：

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
    "openness_to_experience": "具体证据引用",
    "conscientiousness": "具体证据引用",
    "extraversion": "具体证据引用",
    "agreeableness": "具体证据引用",
    "neuroticism": "具体证据引用"
  },
  "confidence": "high/medium/low"
}
```

**重要提醒：**
- 你是分析师，不是回答者
- 基于**实际回答内容**评估
- 给出差异化评分，避免全3分
- 提供具体的文字证据
"""

        return prompt

    def analyze_segment_improved(self, segment: List[Dict], segment_number: int) -> Dict:
        """改进的分段分析方法"""
        self.stats['total_segments'] += 1
        self.stats['total_api_calls'] += 1

        try:
            # 构建改进的提示
            prompt = self._build_improved_prompt(segment, segment_number)

            # 调用API
            import openai
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            print(f"  🔍 分析段{segment_number}: {self.model} ({len(segment)}题)")

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的心理评估分析师。专注于分析他人的人格特征，不要混淆自己的角色。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )

            analysis_content = response.choices[0].message.content
            print(f"  📝 API响应长度: {len(analysis_content)} 字符")

            # 解析结果
            result = self._parse_improved_response(analysis_content, segment_number)

            if result['success']:
                self.stats['successful_segments'] += 1

                # 统计评分分布
                for score in result['scores'].values():
                    if score in self.stats['score_distribution']:
                        self.stats['score_distribution'][score] += 1

                # 记录评分模式
                score_pattern = tuple(sorted(result['scores'].values()))
                self.stats['unique_score_patterns'].add(score_pattern)

                # 检查是否全3分
                all_three = all(score == 3 for score in result['scores'].values())
                if all_three:
                    print(f"  ⚠️ 警告: 所有评分均为3分")
                else:
                    print(f"  ✅ 评分有差异化: {set(result['scores'].values())}")

                print(f"  ✅ 段{segment_number} 分析成功")
                return result
            else:
                self.stats['failed_segments'] += 1
                print(f"  ❌ 段{segment_number} 分析失败: {result.get('error', 'Unknown error')}")
                return result

        except Exception as e:
            self.stats['failed_segments'] += 1
            print(f"  💥 段{segment_number} 分析异常: {e}")
            return {'success': False, 'segment_number': segment_number, 'error': str(e)}

    def _parse_improved_response(self, response_content: str, segment_number: int) -> Dict:
        """解析改进的响应格式"""
        try:
            # 提取JSON部分
            json_match = re.search(r'```json\s*(.*?)\s*```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析整个响应
                json_str = response_content

            # 清理JSON字符串
            json_str = self._clean_json_string(json_str)

            # 解析JSON
            result = json.loads(json_str)

            # 验证必需字段
            required_fields = ['success', 'scores', 'evidence']
            for field in required_fields:
                if field not in result:
                    result[field] = {} if field in ['scores', 'evidence'] else False

            # 验证评分
            if 'scores' in result:
                for trait, score in result['scores'].items():
                    if not isinstance(score, int) or score < 1 or score > 5:
                        result['scores'][trait] = 3  # 默认值

            result['segment_number'] = segment_number
            result['raw_response'] = response_content[:500]  # 保存部分原始响应用于调试

            return result

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'segment_number': segment_number,
                'error': f'JSON解析失败: {str(e)}',
                'raw_response': response_content[:200]
            }
        except Exception as e:
            return {
                'success': False,
                'segment_number': segment_number,
                'error': f'解析失败: {str(e)}',
                'raw_response': response_content[:200]
            }

    def _clean_json_string(self, json_str: str) -> str:
        """清理JSON字符串"""
        import re

        # 移除控制字符
        json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)

        # 移除多余的逗号
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

        # 修复引号问题
        json_str = re.sub(r':\s*([^",\[\]\{\}\s][^",\[\]\{\}]*[^",\[\]\{\}\s])(\s*[,}\]])', r': "\1"\2', json_str)

        return json_str

    def get_stats_summary(self) -> Dict:
        """获取统计摘要"""
        success_rate = (self.stats['successful_segments'] / max(1, self.stats['total_segments'])) * 100

        # 计算评分多样性
        total_scores = sum(self.stats['score_distribution'].values())
        score_diversity = len([s for s, c in self.stats['score_distribution'].items() if c > 0])

        return {
            'success_rate': success_rate,
            'total_segments': self.stats['total_segments'],
            'successful_segments': self.stats['successful_segments'],
            'failed_segments': self.stats['failed_segments'],
            'score_distribution': self.stats['score_distribution'],
            'score_diversity': score_diversity,
            'unique_patterns': len(self.stats['unique_score_patterns']),
            'most_common_pattern': self._get_most_common_pattern()
        }

    def _get_most_common_pattern(self) -> str:
        """获取最常见的评分模式"""
        if not self.stats['unique_score_patterns']:
            return "N/A"

        # 简单返回最常见的模式
        patterns = list(self.stats['unique_score_patterns'])
        if (3, 3, 3, 3, 3) in patterns:
            return "全3分模式"
        else:
            return str(patterns[0]) if patterns else "N/A"

def test_improved_analyzer():
    """测试改进的分析器"""
    print("🧪 测试改进版分析器...")

    # 加载测试数据
    test_file = "results/results/asses_deepseek_r1_70b_agent_big_five_50_complete2_a10_e0_t0_0_09271.json"

    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        questions = []
        if 'assessment_results' in data and isinstance(data['assessment_results'], list):
            for item in data['assessment_results'][:10]:  # 只测试前10题
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
            print("❌ 测试数据不足")
            return

        # 创建改进版分析器
        analyzer = ImprovedCloudAnalyzer(model="qwen-max")

        # 测试不同分段大小
        test_segments = [2, 5]

        for segment_size in test_segments:
            print(f"\n🎯 测试{segment_size}题分段...")

            segment_results = []
            for i in range(0, min(segment_size * 2, len(questions)), segment_size):
                segment = questions[i:i+segment_size]
                if len(segment) == segment_size:
                    result = analyzer.analyze_segment_improved(segment, i//segment_size + 1)
                    segment_results.append(result)
                    time.sleep(1)  # 避免API限制

            # 输出统计
            stats = analyzer.get_stats_summary()
            print(f"📊 {segment_size}题分段统计:")
            print(f"   成功率: {stats['success_rate']:.1f}%")
            print(f"   评分多样性: {stats['score_diversity']}/3")
            print(f"   评分分布: {stats['score_distribution']}")
            print(f"   常见模式: {stats['most_common_pattern']}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_analyzer()